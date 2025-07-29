from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager

from routes import base, data
from helpers.config import get_settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager to initialize and clean up resources.

    This function is automatically triggered at startup and shutdown:
    - Initializes MongoDB connection.
    - Connects to the vector database (e.g., Qdrant).
    - Configures the LLM generation and embedding providers.
    - Closes resources on app shutdown.
    """
    # Load app settings
    settings = get_settings()

    # ------------------ Startup ------------------ #
    # MongoDB connection
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

    yield  # App runs here

    # ------------------ Shutdown ------------------ #
    app.mongo_conn.close()
    app.vectordb_client.disconnect()


# Initialize FastAPI app with lifespan handler
app = FastAPI(lifespan=lifespan)

# Register all route modules
app.include_router(base.base_router)
app.include_router(data.data_router)
