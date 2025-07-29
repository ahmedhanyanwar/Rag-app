import os
import random
import string

from helpers.config import get_settings

class BaseController:
    def __init__(self):
        self.app_settings = get_settings()
        controller_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = os.path.dirname(controller_dir)
        self.files_dir = os.path.join(self.base_dir, "assets", "files")
        

    def generate_random_string(self, length: int=12):
        return ''.join(
            random.choices(
                string.ascii_lowercase + string.digits,
                k=length
            )
        )
    
    def get_project_path(self, project_id: str):
        project_dir = os.path.join(self.files_dir, str(project_id))
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
        return project_dir
    