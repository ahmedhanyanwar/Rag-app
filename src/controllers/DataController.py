from fastapi import UploadFile
import re
import os
import aiofiles
import hashlib

from .BaseController import BaseController
from models.enums import ResponseSignal

class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.size_scale = 1024 * 1024  # convert from MB to Bytes

    def validate_uploaded_file(self, file: UploadFile):
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value

        if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value

        return True, ResponseSignal.FILE_UPLOADED_SUCCESS.value

    def generate_unique_filepath(self, org_file_name: str, project_id: str):
        random_key = self.generate_random_string()
        project_path = self.get_project_path(project_id=project_id)
        cleaned_filename = self.get_clean_filename(org_file_name)
        file_name, ext = cleaned_filename.split('.')
        new_file_name = f"{file_name}_{random_key}.{ext}"
        new_file_path = os.path.join(project_path, new_file_name)

        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_name = f"{file_name}_{random_key}.{ext}"
            new_file_path = os.path.join(project_path, new_file_name)

        return new_file_path, new_file_name

    def get_clean_filename(self, org_file_name: str):
        # Remove any special character except letters, digits, space, and dot
        cleaned_filename = re.sub(r'[^\w\s.]', '', org_file_name.strip())
        cleaned_filename = cleaned_filename.replace(" ", "_")
        return cleaned_filename

    async def compute_file_hash(self, file: UploadFile) -> str:
        sha256 = hashlib.sha256()
        await file.seek(0)  # Ensure pointer is at start
        while chunk := await file.read(self.app_settings.FILE_DEFAULT_CHUNK_SIZE):
            sha256.update(chunk)
        await file.seek(0)  # Reset for future use
        return sha256.hexdigest()

    async def save_file_to_disk(self, file: UploadFile, project_id: str):
        file_path, file_id_name = self.generate_unique_filepath(
            org_file_name=file.filename,
            project_id=project_id
        )

        try:
            async with aiofiles.open(file_path, "wb") as out:
                while chunk := await file.read(self.app_settings.FILE_DEFAULT_CHUNK_SIZE):
                    await out.write(chunk)
            return True, file_path, file_id_name
        except Exception as e:
            return False, "", str(e)
