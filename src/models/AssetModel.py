from math import ceil
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Union

from .BaseDataModel import BaseDataModel
from .enums import DataBaseEnum
from .db_schemes import Asset

class AssetModel(BaseDataModel):
    def __init__(self, db_client: AsyncIOMotorDatabase):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: AsyncIOMotorDatabase):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        # Make sure that collection was not created yet
        # all_collection = value when one insertion happen 
        all_collection = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_ASSET_NAME.value not in all_collection:
            indexes = Asset.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"],
                )

    async def create_asset(self, asset: Asset):
        result = await self.collection.insert_one(asset.model_dump(by_alias=True, exclude_unset=True))
        asset.id = result.inserted_id
        return asset
    
    async def get_asset_record(self, asset_project_id: Union[str, ObjectId], asset_name: str):
        asset_project_id = ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id
        record = await self.collection.find_one({
            "asset_project_id": asset_project_id,
            "asset_name": asset_name,
        })

        if record is None:
            return None
        
        return Asset(**record)

    async def get_all_project_assets(
            self,
            asset_project_id: Union[str, ObjectId],
            asset_type: str,
            page: int = 1,
            page_size: int = 10,
            fetch_all: bool = False
        ):
        asset_project_id = ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id
        search_dict = {
            "asset_project_id": asset_project_id,
            "asset_type": asset_type,
        }

        if fetch_all:
            cursor = self.collection.find(search_dict)
        else:
            cursor = self.collection.find(search_dict).skip((page - 1) * page_size).limit(page_size)

        records = [Asset(**record) async for record in cursor]
        return records

    async def get_total_pages(self, asset_project_id: Union[str, ObjectId], asset_type: str, page_size: int =10) -> int:
        asset_project_id = ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id
        search_dict = {
            "asset_project_id": asset_project_id,
            "asset_type": asset_type,
        }

        total_documents = await self.collection.count_documents(search_dict)
        total_pages = ceil(total_documents / page_size)
        return total_pages
    
    async def is_existed(
        self,
        asset_project_id: Union[str, ObjectId],
        file_hash: str
    ) -> bool:
        project_oid: ObjectId = (
            ObjectId(asset_project_id)
            if isinstance(asset_project_id, str)
            else asset_project_id
        )
        doc = await self.collection.find_one(
            {
                "asset_project_id": project_oid,
                "asset_file_hash": file_hash,
            },
            projection={"_id": 1},  # small projection for speed
        )
        return doc is not None

    async def delete_assets_by_project_id(self, asset_project_id: Union[str, ObjectId]) -> int:
        asset_project_id = ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id
        result = await self.collection.delete_many(
            {"asset_project_id": asset_project_id}
        )
        return result.deleted_count

    async def delete_all_assets(self):
        await self.collection.delete_many({})
    
    async def drop_assets_collection(self):
        await self.collection.drop()
        