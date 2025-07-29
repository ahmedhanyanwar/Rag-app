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

from controllers import DataController, ProcessController
from models.enums import ResponseSignal, AssetTypeEnum
from .schemes.data import ProcessRequest
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

@data_router.post("/process/{project_id}")
async def process_endpoint(request: Request, project_id: str, process_request: ProcessRequest):
    chunk_size = process_request.chunk_size
    overlap_size=process_request.overlap_size
    do_reset = process_request.do_reset
    force_reproduce_chunks = process_request.force_reproduce_chunks

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_or_create_project(project_id)

    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)
    # asset_model = AssetModel(db_client=request.app.db_client)

    if process_request.file_id:  # Given asset_name
        asset_record = await asset_model.get_asset_record(
            asset_project_id=project.id,
            asset_name=process_request.file_id
        )

        if asset_record is None:
            return JSONResponse(
                content={
                    "signal": ResponseSignal.FILE_ID_ERROR.value
                },
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        
        project_file_ids = {
            asset_record.id: asset_record.asset_name
        }
    else: # Brings all assets that have this project_id
        project_files =  await asset_model.get_all_project_assets(
            asset_project_id=project.id,
            asset_type=AssetTypeEnum.FILE.value,
            fetch_all=True
        )
    
        # Now build the mapping
        project_file_ids = {
            record.id: record.asset_name
            for record in project_files
        }

    if len(project_file_ids) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.NO_FILES_ERROR.value
            }
        )
    
    process_controller = ProcessController(project_id=project_id)

    chunk_model = await ChunkModel.create_instance(request.app.db_client)
    
    # Delete all chunks
    if do_reset == 1: 
        await chunk_model.delete_chunks_by_project_id(chunk_project_id=project.id)
        logger.info(f"Delete all chunks of project_id({project_id})")
    
    no_records = 0
    no_files = 0

    for asset_id, asset_name in project_file_ids.items():
        if force_reproduce_chunks:
            await chunk_model.delete_chunks_for_asset(
                chunk_project_id=project.id,
                chunk_asset_id=asset_id
            )
            logger.info(f"[Force] cleared chunks for {asset_name}")
        else:
            # 1) identical‑param check
            same_params = await chunk_model.is_chunks_exist(
                chunk_project_id=project.id,
                chunk_asset_id=asset_id,
                chunk_size=chunk_size,
                overlap_size=overlap_size,
            )
            if same_params:
                logger.info(f"[Skip] identical chunks already exist → {asset_name}")
                continue  # nothing to do

            # 2) different‑param chunks: remove them
            removed = await chunk_model.delete_chunks_for_asset(
                chunk_project_id=project.id,
                chunk_asset_id=asset_id
            )
            if removed:
                logger.info(f"[Update] removed {removed} outdated chunks for {asset_name}")

        # -------- read, chunk, insert --------
        file_content = process_controller.get_file_content(file_id=asset_name)
        if file_content is None:
            logger.error(f"[Error] cannot read file {asset_name}")
            continue

        chunks = process_controller.process_file_content(
            file_content=file_content,
            file_id=asset_name,
            chunk_size=chunk_size,
            overlap_size=overlap_size,
        )
        if not chunks:
            logger.warning(f"[Skip] no chunks from {asset_name}")
            continue

        docs = [
            DataChunk(
                chunk_project_id=project.id,
                chunk_text=c.page_content,
                chunk_metadata=c.metadata,
                chunk_order=i + 1,
                chunk_asset_id=asset_id,
                chunk_size=chunk_size,
                chunk_overlap_size=overlap_size,
            )
            for i, c in enumerate(chunks)
        ]

        try:
            inserted = await chunk_model.insert_many_chunks(docs)
            no_records += inserted
            no_files  += 1
            logger.info(f"[Insert] {inserted} chunks stored for {asset_name}")
        except Exception as exc:
            logger.error(f"[Error] failed insert for {asset_name}: {exc}")


    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_records,
            "processed_file": no_files
        }
    )

@data_router.get("/delete/{project_id}")
async def delete_project(request: Request,project_id: str):
    project_model = ProjectModel(request.app.db_client)
    project = await project_model.get_or_create_project(project_id)
    await project_model.delete_project(project_id)
    
    chunk_model = ChunkModel(request.app.db_client)
    await chunk_model.delete_chunks_by_project_id(chunk_project_id=project.id)
    
    asset_model = AssetModel(request.app.db_client)
    await asset_model.delete_assets_by_project_id(asset_project_id=project.id)

    project_path = DataController().get_project_path(project_id)
    for item in os.listdir(project_path):
        item_path = os.path.join(project_path, item)
        os.remove(item_path)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "single": f"Delete project id: {project_id}"
        }
    )

@data_router.get("/reset_all")
async def delete_project(request: Request):
    project_model = ProjectModel(request.app.db_client)
    await project_model.drop_projects_collection()
    chunk_model = ChunkModel(request.app.db_client)
    await chunk_model.drop_chunks_collection()
    asset_model = AssetModel(request.app.db_client)
    await asset_model.drop_assets_collection()

    file_path = DataController().files_dir
    for item in os.listdir(file_path):
        item_path = os.path.join(file_path, item)
        shutil.rmtree(item_path)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "single": "Restart the app."
        }
    )