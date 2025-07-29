from abc import ABC, abstractmethod
from typing import List, Union, Tuple, Optional, Dict

class LLMInterface(ABC):
    """Base interface for any LLM provider (sync or async)."""

    @abstractmethod
    def set_generation_model(self, model_id: str) -> None:
        """Select which model to use for text generation."""
        pass

    @abstractmethod
    def set_embedding_model(self, model_id: str, embedding_size: int) -> None:
        """Select which model to use for embeddings."""
        pass

    @abstractmethod
    def generate_text(
        self,
        prompt: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Tuple[str, List[Dict[str, str]]]:
        """
        Generate text from a prompt.
        Returns: (generated_text, updated_chat_history)
        """
        pass

    @abstractmethod
    def embed_text(
        self,
        text: Union[str, List[str]],
        document_type: Optional[str] = None
    ) -> List[List[float]]:
        """Return embedding vector(s) for the given text."""
        pass

    @abstractmethod
    def construct_prompt(self, prompt: str, role: str) -> Dict[str, str]:
        """Wrap a single message into the LLM’s expected prompt format."""
        pass
