from pydantic import BaseModel, Field, field_validator
from typing import Optional
from bson.objectid import ObjectId
from pymongo import ASCENDING

class Project(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")

    project_id: str = Field(..., min_length=1)

    @field_validator("project_id")
    @classmethod
    def validate_project_id(cls, value):
        if not value.isalnum():
            raise ValueError("Project_id must be alphanumeric")
        return value

    model_config = {
        "arbitrary_types_allowed": True, # To allow the ObjectId type
        "populate_by_name": True  # important if you use alias `_id`
    }

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [
                    ("project_id", ASCENDING)
                ],
                "name": "project_id_index_1",
                "unique": True
            }
        ]
