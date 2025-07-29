from pydantic import BaseModel, Field
from typing import Optional
from bson.objectid import ObjectId
from pymongo import ASCENDING
from datetime import datetime, timezone

class Asset(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")

    # Core fields
    asset_project_id: ObjectId
    asset_type: str = Field(..., min_length=1)

    # 64‑char SHA‑256 hex digest
    #  ^ means start of string.
    #  [a-fA-F0-9] means the valid is charecter from a-f or A-F or 0-9 and it is 64 character 
    #  $ means end of string.
    asset_file_hash: Optional[str] = Field(
        default=None,
        min_length=64,
        max_length=64,
        pattern=r"^[a-fA-F0-9]{64}$"
    )
    
    asset_file_extension: str = Field(default=None, min_length=1)
    asset_name: str = Field(..., min_length=1)
    asset_size: int = Field(ge=0, default=None)          # bytes
    asset_config: dict = Field(default=None)
    asset_pushed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    model_config = {
        "arbitrary_types_allowed": True,
        "populate_by_name": True
    }

    # ---------- indexes --------------------------------------------------
    @classmethod
    def get_indexes(cls):
        """
        Returns a list of PyMongo index specs for this collection.
        """
        return [
            {
                "key": [("asset_project_id", ASCENDING)],
                "name": "asset_project_id_idx",
                "unique": False,
            },
            {
                "key": [("asset_project_id", ASCENDING), ("asset_name", ASCENDING)],
                "name": "project_filename_idx",
                "unique": False,
            },
            {
                "key": [("asset_project_id", ASCENDING), ("asset_file_hash", ASCENDING)],
                "name": "file_hash_unique_idx",
                "unique": True,
            },
        ]
