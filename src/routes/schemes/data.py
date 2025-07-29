from pydantic import BaseModel
from typing import Optional

class ProcessRequest(BaseModel):
    file_id: str = None # Optional
    chunk_size: Optional[int] = 100
    overlap_size: Optional[int] = 20
    do_reset: Optional[int] = 0
    force_reproduce_chunks: Optional[int] = 0