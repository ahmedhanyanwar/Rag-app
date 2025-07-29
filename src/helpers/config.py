from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str

    # This means that all variable on .env get loaded
    #   then turns to class 
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

# Skelton
def get_settings():
    return Settings()