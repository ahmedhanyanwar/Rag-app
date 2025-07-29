import os

from .providers import QdrantDBProvider
from .VectorDBEnums import VectorDBEnums
from helpers.config import Settings

class VectorDBFactory:
    def __init__(self, config: Settings):
        self.config = config
        
    def get_database_dir(self, db_name: str):
        base_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        database_path = os.path.join(base_dir, "assets", "database", db_name)
        if not os.path.exists(database_path):
            os.makedirs(database_path)
        return database_path
    
    def create(self, provider: str):
        if provider == VectorDBEnums.QDRANT.value:
            db_path = self.get_database_dir(db_name= self.config.VECTOR_DB_PATH_NAME)
            return QdrantDBProvider(
                db_path=db_path,
                distance_method=self.config.VECTOR_DB_DIATANCE_METHOD
            )

        return None
