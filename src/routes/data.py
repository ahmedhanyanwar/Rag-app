from fastapi import (
    APIRouter,
    UploadFile,
    status,
    Request
)
from fastapi.responses import JSONResponse
import os
import shutil
import logging

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",       # Before any api request
    tags=["api_v1", "data"]     # organize the code
)
