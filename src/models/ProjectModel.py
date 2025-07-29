from math import ceil
from motor.motor_asyncio import AsyncIOMotorDatabase

from .BaseDataModel import BaseDataModel
from .enums import DataBaseEnum
from .db_schemes import Project

from motor.motor_asyncio import AsyncIOMotorClient

class ProjectModel(BaseDataModel):
    def __init__(self, db_client: AsyncIOMotorDatabase):
        super().__init__(db_client)
        self.db_client = AsyncIOMotorClient(self.app_settings.MONGODB_URL)[self.app_settings.MONGODB_DATABASE]


        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: AsyncIOMotorDatabase):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        # Make sure that collection was not created yet
        # all_collection = value when one insertion happen 
        all_collection = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_PROJECT_NAME.value not in all_collection:
            indexes = Project.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"],
                )

    async def create_project(self, project: Project):
        result = await self.collection.insert_one(project.model_dump(by_alias=True, exclude_unset=True))
        project.id = result.inserted_id

        return project
    
    async def get_or_create_project(self, project_id: str):

        record = await self.collection.find_one({
            "project_id": project_id
        })

        if record is None:
            project = Project(project_id=project_id)
            project = await self.create_project(project)

            return project

        return Project(**record)
    
    # This called pagination to avoid the overload
    async def get_all_projects(self, page: int=1, page_size: int=10):
        total_documents = await self.collection.count_documents({})
        total_pages = ceil(total_documents / page_size)
        
        cursor = self.collection.find().skip((page - 1) * page_size).limit(page_size)
        projects = [
            Project(**document)
            async for document in cursor 
        ]

        return projects, total_pages

    async def delete_project(self, project_id: str) -> int:
        result = await self.collection.delete_one({"project_id": project_id})
        return result.deleted_count
    
    async def delete_all_projects(self):
        await self.collection.delete_many({})
    
    async def drop_projects_collection(self):
        await self.collection.drop()
        