from pydantic import BaseModel, Field
from typing import Optional
from bson.objectid import ObjectId
from pymongo import ASCENDING

class DataChunk(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    chunk_project_id: ObjectId
    chunk_order: int = Field(..., gt=0)
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict = Field(default_factory=dict)
    chunk_asset_id: ObjectId

    chunk_size: int
    chunk_overlap_size: int

    model_config = {
        "arbitrary_types_allowed": True, # To allow the ObjectId type
        "populate_by_name": True  # important if you use alias `_id`
    }

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [
                    ("chunk_project_id", ASCENDING)
                ],
                "name": "chunk_project_id_index_1",
                "unique": False # more than one chunk belongs to same project
            },
            {
                "key": [
                    ("chunk_project_id", ASCENDING),
                    ("chunk_asset_id", ASCENDING),
                    ("chunk_size", ASCENDING),
                    ("chunk_overlap_size", ASCENDING),

                ],
                "name": "proj_asset_param_idx",
                "unique": False
            }
        ]

class RetrievedDocument(BaseModel):
    text: str
    score: float