from openai import OpenAI
import logging
from typing import Union, List, Optional, Tuple, Dict

from ..LLMInterface import LLMInterface
from ..LLMEnum import OpenAIEnums


class OpenAIProvider(LLMInterface):

    def __init__(
        self,
        api_key: str,
        api_url: str = None,
        default_input_max_characters: int = 1000,
        default_generation_max_output_tokens: int = 1000,
        default_generation_temperature: float = 0.1
    ):
        self.api_key = api_key
        self.api_url = api_url

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generate_model_id: Optional[str] = None
        self.embedding_model_id: Optional[str] = None
        self.embedding_size: Optional[int] = None

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_url if self.api_url and len(self.api_key) else None
        )

        self.enums = OpenAIEnums
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str) -> None:
        self.generate_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int) -> None:
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def generate_text(
        self,
        prompt: str,
        chat_history: Optional[List[Dict[str, str]]] = None,
        max_output_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Tuple[Optional[str], List[Dict[str, str]]]:
        if not self.client or not self.generate_model_id:
            self.logger.error("OpenAI client or model ID not set.")
            return None, chat_history or []

        chat_history = chat_history or []
        max_output_tokens = max_output_tokens or self.default_generation_max_output_tokens
        temperature = temperature or self.default_generation_temperature

        # Append user message
        chat_history.append(self.construct_prompt(prompt, self.enums.USER.value))

        try:
            response = self.client.chat.completions.create(
                model=self.generate_model_id,
                messages=chat_history,
                max_tokens=max_output_tokens,
                temperature=temperature
            )
        except Exception as e:
            self.logger.exception(f"OpenAI chat call failed: {e}")
            return None, chat_history

        if not response or not response.choices or not response.choices[0].message:
            self.logger.error("Empty or invalid response from OpenAI.")
            return None, chat_history

        assistant_reply = response.choices[0].message.content.strip()
        chat_history.append(self.construct_prompt(assistant_reply, self.enums.ASSISTANT.value))

        return assistant_reply, chat_history

    def embed_text(
        self,
        text: Union[str, List[str]],
        document_type: str = None
    ) -> List[List[float]]:
        if not self.client or not self.embedding_model_id:
            self.logger.error("OpenAI embedding setup incomplete.")
            return []

        texts = [text] if isinstance(text, str) else text

        try:
            response = self.client.embeddings.create(
                input=texts,
                model=self.embedding_model_id
            )
        except Exception as e:
            self.logger.exception(f"OpenAI embedding call failed: {e}")
            return []

        if not response or not response.data:
            self.logger.error("Empty embedding response from OpenAI.")
            return []

        return [record.embedding for record in response.data]

    def construct_prompt(self, prompt: str, role: str) -> Dict[str, str]:
        return {
            "role": role,
            "content": prompt
        }

    def process_text(self, text: str) -> str:
        return text[:self.default_input_max_characters].strip()