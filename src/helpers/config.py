from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Dict

class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str

    FILE_ALLOWED_TYPES: List[str]
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int

    MONGODB_URL: str
    MONGODB_DATABASE: str

    # This means that all variable on .env get loaded
    #   then turns to class 
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

# Skelton
def get_settings():
    return Settings()