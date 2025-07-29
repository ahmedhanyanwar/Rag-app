from qdrant_client import models, QdrantClient
import logging
from typing import List, Optional, Dict

from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import VectorDBEnums, DistanceMethodEnums
from models.db_schemes.data_chunk import RetrievedDocument

class QdrantDBProvider(VectorDBInterface):
    def __init__(self, db_path: str, distance_method: str):
        self.client = None
        self.db_path = db_path

        self.logger = logging.getLogger(__name__)

        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT
        else:
            self.logger.warning(f"Unknown distance method '{distance_method}', using Cosine as default.")
            self.distance_method = models.Distance.COSINE

    def connect(self) -> None:
        self.client = QdrantClient(path=self.db_path)

    def disconnect(self) -> None:
        self.client = None

    def is_collection_existed(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)

    def list_all_collection(self) -> List[str]:
        collections_response = self.client.get_collections()
        return [col.name for col in collections_response.collections]

    def get_collection_info(self, collection_name: str):
        return self.client.get_collection(collection_name=collection_name)

    def delete_collection(self, collection_name: str) -> bool:
        if self.is_collection_existed(collection_name):
            self.logger.info(f"Deleting collection: {collection_name}")
            self.client.delete_collection(collection_name=collection_name)
            return True
        self.logger.warning(f"Collection {collection_name} does not exist.")
        return False

    def create_collection(
        self, collection_name: str,
        embedding_size: int,
        do_reset: bool = False
    ) -> bool:
        if do_reset:
            self.delete_collection(collection_name)

        if not self.is_collection_existed(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_method
                )
            )
            self.logger.info(f"Collection '{collection_name}' created.")
            return True
        self.logger.info(f"Collection '{collection_name}' already exists.")
        return False

    def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: List[float],
        metadata: Optional[Dict] = None,
        record_id: Optional[str] = None
    ) -> bool:
        if not self.is_collection_existed(collection_name):
            self.logger.error(f"Cannot insert into non-existent collection '{collection_name}'.")
            return False

        try:
            self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        id=record_id,
                        vector=vector,
                        payload={
                            "text": text,
                            "metadata": metadata
                        }
                    )
                ]
            )
            self.logger.info(f"Inserted record into collection '{collection_name}'.")
            return True
        except Exception as e:
            self.logger.exception(f"Error inserting single record: {e}")
            return False

    def insert_many(
        self,
        collection_name: str,
        texts: List[str],
        vectors: List[List[float]],
        metadatas: Optional[List[Dict]] = None,
        record_ids: Optional[List[str]] = None,
        batch_size: int = 50
    ) -> bool:
        if not self.is_collection_existed(collection_name):
            self.logger.error(f"Cannot insert into non-existent collection '{collection_name}'.")
            return False

        if metadatas is None:
            metadatas = [{}] * len(texts)
        if record_ids is None:
            record_ids = list(range(len(texts)))

        try:
            for i in range(0, len(texts), batch_size):
                batch_records = [
                    models.Record(
                        id=record_ids[j],
                        vector=vectors[j],
                        payload={
                            "text": texts[j],
                            "metadata": metadatas[j]
                        }
                    )
                    for j in range(i, min(i + batch_size, len(texts)))
                ]
                
                self.client.upload_records(
                    collection_name=collection_name,
                    records=batch_records
                )
            self.logger.info(f"All records inserted into '{collection_name}'.")
            return True
        except Exception as e:
            self.logger.exception(f"Error inserting records batch: {e}")
            return False

    def search_by_vector(
        self,
        collection_name: str,
        vector: List[float],
        limit: int
    ) -> List[RetrievedDocument]:
        try:
            results = self.client.search(
                collection_name=collection_name,
                query_vector=vector,
                limit=limit
            )
            return [
                RetrievedDocument(
                    score=record.score,
                    text=record.payload.get("text", "")
                )
                for record in results
            ]
        except Exception as e:
            self.logger.exception(f"Error during search in collection '{collection_name}': {e}")
            return []
