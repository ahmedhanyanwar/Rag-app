from abc import ABC, abstractmethod
from typing import List, Dict, Optional

from models.db_schemes.data_chunk import RetrievedDocument

class VectorDBInterface(ABC):
    """
    Abstract base class for defining vector database operations.
    This interface enforces a consistent structure for vector store providers 
    such as Qdrant, FAISS, Pinecone, etc.
    """

    @abstractmethod
    def connect(self) -> None:
        """
        Establish a connection to the vector database.
        Should be called before performing any operations.
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """
        Cleanly disconnect from the vector database and release any held resources.
        """
        pass

    @abstractmethod
    def is_collection_existed(self, collection_name: str) -> bool:
        """
        Check whether a specific collection exists in the database.
        """
        pass

    @abstractmethod
    def list_all_collection(self) -> List[str]:
        """
        Retrieve the names of all existing collections in the database.
        """
        pass

    @abstractmethod
    def get_collection_info(self, collection_name: str):
        """
        Retrieve metadata or configuration details for a specific collection.
        """
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a specific collection from the database.
        """
        pass

    @abstractmethod
    def create_collection(
        self,
        collection_name: str,
        embedding_size: int,
        do_reset: bool = False
    ) -> bool:
        """
        Create a new collection to store vectors.
        """
        pass

    @abstractmethod
    def insert_one(
        self,
        collection_name: str,
        text: str,
        vector: List[float],
        metadata: Optional[Dict] = None,
        record_id: Optional[str] = None
    ) -> bool:
        """
        Insert a single document into the collection.
        """
        pass

    @abstractmethod
    def insert_many(
        self,
        collection_name: str,
        texts: List[str],
        vectors: List[List[float]],
        metadatas: Optional[List[Dict]] = None,
        record_ids: Optional[List[str]] = None,
        batch_size: int = 50
    ) -> bool:
        """
        Insert multiple documents into the collection in batches.
        """
        pass

    @abstractmethod
    def search_by_vector(
        self,
        collection_name: str,
        vector: List[float],
        limit: int
    ) -> List[RetrievedDocument]:
        """
        Perform a similarity search to retrieve top-k documents closest to the given vector.
        """
        pass
