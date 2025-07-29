from math import ceil
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from pymongo import InsertOne
from typing import List, Union

from .BaseDataModel import BaseDataModel
from .enums import DataBaseEnum
from .db_schemes import DataChunk

class ChunkModel(BaseDataModel):
    def __init__(self, db_client: AsyncIOMotorDatabase):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: AsyncIOMotorDatabase):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        # Make sure that collection was not created yet
        # all_collection = value when one insertion happen 
        all_collection = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_CHUNK_NAME.value not in all_collection:
            indexes = DataChunk.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"],
                )

    async def create_chunk(self, chunk: DataChunk):
        result = await self.collection.insert_one(chunk.model_dump(by_alias=True, exclude_unset=True))
        chunk.id = result.inserted_id
        return chunk
    
    async def get_chunk(self, chunk_id: str):

        record = await self.collection.find_one({
            "_id": ObjectId(chunk_id)
        })
        if record is None:
            return None
        return DataChunk(**record)
    
    async def insert_many_chunks(self, chunks: List[DataChunk], batch_size: int=100) -> int:
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i: i + batch_size]
            # InsertOne() : it creates an insert operation object that can be passed to bulk_write()
            # Prepare the process
            operations = [
                InsertOne(chunk.model_dump(by_alias=True, exclude_unset=True))
                for chunk in batch
            ]
            
            result = await self.collection.bulk_write(operations)
            if not result.acknowledged:
                raise Exception("Bulk insert not acknowledged by MongoDB")
        return len(chunks)
            
    # This called pagination to avoid the overload
    async def get_all_chunks_in_project(
        self,
        project_id: Union[str, ObjectId],
        page: int = 1,
        page_size: int = 50
    ) -> List[DataChunk]:
        chunk_project_id = ObjectId(project_id) if isinstance(project_id, str) else project_id
        cursor = (
            self.collection
            .find({"chunk_project_id": chunk_project_id})
            .skip((page - 1) * page_size)
            .limit(page_size)
        )
        return [DataChunk(**doc) async for doc in cursor]

    async def get_total_pages(
        self,
        project_id: Union[str, ObjectId],
        page_size: int = 50
    ) -> int:
        chunk_project_id = ObjectId(project_id) if isinstance(project_id, str) else project_id
        total_documents = await self.collection.count_documents(
            {"chunk_project_id": chunk_project_id}
        )
        return ceil(total_documents / page_size)
    
    async def is_chunks_exist(
        self,
        chunk_project_id: Union[str, ObjectId],
        chunk_asset_id: Union[str, ObjectId],
        chunk_size: int,
        overlap_size: int
    ) -> bool:
        proj_id  = ObjectId(chunk_project_id) if isinstance(chunk_project_id, str) else chunk_project_id
        asset_id = ObjectId(chunk_asset_id)    if isinstance(chunk_asset_id, str)   else chunk_asset_id
        doc = await self.collection.find_one(
            {
                "chunk_project_id": proj_id,
                "chunk_asset_id": asset_id,
                "chunk_size":     chunk_size,
                "chunk_overlap_size":   overlap_size,
            },
            projection={"_id": 1},
        )
        return doc is not None
    
    async def delete_chunks_for_asset(
        self,
        chunk_project_id: Union[str, ObjectId],
        chunk_asset_id: Union[str, ObjectId],
    ) -> int:
        """Delete all chunks for (project, asset) irrespective of the params."""
        proj_id  = ObjectId(chunk_project_id) if isinstance(chunk_project_id, str) else chunk_project_id
        asset_id = ObjectId(chunk_asset_id)    if isinstance(chunk_asset_id, str)   else chunk_asset_id

        result = await self.collection.delete_many(
            {"chunk_project_id": proj_id, "chunk_asset_id": asset_id}
        )
        return result.deleted_count
    
    async def delete_chunks_by_project_id(self, chunk_project_id: Union[str, ObjectId]) -> int:
        chunk_project_id = ObjectId(chunk_project_id) if isinstance(chunk_project_id, str) else chunk_project_id
        result = await self.collection.delete_many(
            {"chunk_project_id": chunk_project_id}
        )
        return result.deleted_count

    async def delete_all_chunks(self):
            await self.collection.delete_many({})
        
    async def drop_chunks_collection(self):
        await self.collection.drop()
        