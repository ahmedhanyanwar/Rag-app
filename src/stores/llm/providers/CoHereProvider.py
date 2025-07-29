import cohere
import logging
from typing import Union, List, Tuple

from ..LLMInterface import LLMInterface
from ..LLMEnum import CoHereEnums, DocumentTypeEnum

class CoHereProvider(LLMInterface):

    def __init__(
        self,
        api_key: str,
        default_input_max_characters: int=1000,
        default_generation_max_output_tokens: int=1000,
        default_generation_temperature: float=0.1
    ):
        self.api_key = api_key
        
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        # Need in the future
        self.generate_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = cohere.Client(
            api_key= self.api_key,
        )

        self.enums = CoHereEnums
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str) -> None:
        self.generate_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int) -> None:
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
    
    def generate_text(
        self,
        prompt: str,
        chat_history: List[dict] = None,
        max_output_tokens: int = None,
        temperature: float = None
    ) -> Tuple[str, List[dict]]:
        """
        Returns (response_text, updated_chat_history)
        """
        if not self.client or not self.generate_model_id:
            self.logger.error("Cohere client or model ID not set.")
            return None, chat_history or []

        chat_history = chat_history or []

        max_output_tokens = max_output_tokens or self.default_generation_max_output_tokens
        temperature = temperature or self.default_generation_temperature
        
        try:
            # send only prior history + the new message
            response = self.client.chat(
                model=self.generate_model_id,
                chat_history=chat_history,
                message=prompt,
                max_tokens=max_output_tokens,
                temperature=temperature
            )
        except Exception as e:
            self.logger.exception(f"Error in Cohere chat: {e}")
            return None, chat_history

        if not response or not response.text:
            self.logger.error("Empty response from Cohere.")
            return None, chat_history
        
        # now append the turn to history for next time
        chat_history.append(self.construct_prompt(prompt, self.enums.USER.value))
        chat_history.append(self.construct_prompt(response.text, self.enums.ASSISTANT.value))

        return response.text, chat_history


    def embed_text(self, text: Union[str, List[str]], document_type: str=None):
        if not self.client:
            self.logger.error("CoHere client was not set.")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model for CoHere was not set.")
            return None
        
        if isinstance(text, str):
            text = [text]

        input_type= self.enums.DOCUMENT.value
        if document_type == DocumentTypeEnum.QUERY.value:
            input_type = self.enums.QUERY.value

        response = self.client.embed(
            texts= text,
            model=self.embedding_model_id,
            input_type=input_type,
            embedding_types=['float']
        )

        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error("Error while embedding text with CoHere")
            return None

        return [f for f in response.embeddings.float]

    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "message": prompt
        }
    
    def process_text(self, text: str):
        # Cut if to large and remove start and end /n and space
        return text[:self.default_input_max_characters].strip()