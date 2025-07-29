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

from controllers import DataController
from models.enums import ResponseSignal, AssetTypeEnum
from models.db_schemes import DataChunk, Asset
from models import ProjectModel, ChunkModel, AssetModel

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",       # Before any api request
    tags=["api_v1", "data"]     # organize the code
)

@data_router.post("/upload/{project_id}")
async def upload_data(
    request: Request,
    project_id: str,
    file: UploadFile
):
    # Create or get the project
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_or_create_project(project_id=project_id)

    data_controller = DataController()
    is_valid, result_signal = data_controller.validate_uploaded_file(file=file)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"signal": result_signal}
        )

    # Compute the file hash before saving
    file_hash = await data_controller.compute_file_hash(file)

    # Check if file with same content already exists
    asset_model = await AssetModel.create_instance(request.app.db_client)
    existing = await asset_model.is_existed(
        asset_project_id=project.id,
        file_hash=file_hash
    )

    if existing:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"signal": ResponseSignal.FILE_DUPLICATE_CONTENT.value}
        )

    # Save file only if it's not a duplicate
    success, file_path, file_id_name = await data_controller.save_file_to_disk(
        file=file,
        project_id=project_id
    )

    if not success:
        logger.error(f"Error while saving file: {file_id_name}")
        return JSONResponse(
            content={"signal": ResponseSignal.FILE_UPLOADED_FAILED.value},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # Insert asset metadata into database
    asset_resource = Asset(
        asset_project_id=project.id,
        asset_type=AssetTypeEnum.FILE.value,
        asset_file_extension=os.path.splitext(file_path)[-1],
        asset_name=file_id_name,
        asset_size=os.path.getsize(file_path),
        asset_file_hash=file_hash
    )

    asset_record = await asset_model.create_asset(asset=asset_resource)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.FILE_UPLOADED_SUCCESS.value,
            "file_id": str(asset_record.asset_name)
        }
    )
