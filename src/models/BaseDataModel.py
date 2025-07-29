from helpers.config import get_settings

class BaseDataModel:
    def __init__(self, db_client: object):
        self.app_settings = get_settings()
        # AsyncIOMotorClient(MONGODB_URL)[MONGODB_DATABASE_NAME]
        # This is the open connection
        self.db_client = db_client 
