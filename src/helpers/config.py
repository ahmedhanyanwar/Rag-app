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

    GENERATION_AND_EMBEDDING_BACKEND: List[str]

    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str

    OPENAI_API_KEY: str = None
    OPENAI_API_URL: str = None
    COHERE_API_KEY: str = None

    GENERATION_MODEL_ID_LITERAL: List[str] = None

    GENERATION_MODEL_ID: str = None
    EMBEDDING_MODEL_ID: str = None
    EMBEDDING_MODEL_SIZE: int = None

    INPUT_DEFAULT_MAX_CHARACTERS: int = None
    GENERATION_DEFAULT_MAX_TOKENS: int = None
    GENERATION_DEFAULT_TEMPERATURE: float = None

    VECTOR_DB_BACKEND: str
    VECTOR_DB_PATH_NAME: str
    VECTOR_DB_DIATANCE_METHOD: str = None

    PRIMARY_LANG: str
    DEFAULT_LANG: str

    # This means that all variable on .env get loaded
    #   then turns to class 
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

# Skelton
def get_settings():
    return Settings()