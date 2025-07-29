from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager

from routes import base, data, nlp
from helpers.config import get_settings
from stores.vectordb import VectorDBFactory
from stores.llm import LLMProviderFactory

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

    # Vector database connection
    vectordb_factory = VectorDBFactory(config=settings)
    app.vectordb_client = vectordb_factory.create(provider=settings.VECTOR_DB_BACKEND)
    app.vectordb_client.connect()

    # Language  provider setup
    llm_factory = LLMProviderFactory(config=settings)

    # Generation model
    app.generation_client = llm_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id=settings.GENERATION_MODEL_ID)

    # Embedding model
    app.embedding_client = llm_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(
        model_id=settings.EMBEDDING_MODEL_ID,
        embedding_size=settings.EMBEDDING_MODEL_SIZE,
    )
    
    yield  # App runs here

    # ------------------ Shutdown ------------------ #
    app.mongo_conn.close()
    app.vectordb_client.disconnect()


# Initialize FastAPI app with lifespan handler
app = FastAPI(lifespan=lifespan)

# Register all route modules
app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)