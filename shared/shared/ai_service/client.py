import os
import json
import logging
from openai import OpenAI

logger = logging.getLogger(__name__)


class AIClient:
    """Unified AI client supporting multiple LLM providers via OpenAI-compatible API."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.api_key = os.getenv('AI_API_KEY', '')
        self.api_base = os.getenv('AI_API_BASE', 'https://api.openai.com/v1')
        self.model = os.getenv('AI_MODEL', 'gpt-4o')
        self.embedding_model = os.getenv('AI_EMBEDDING_MODEL', 'text-embedding-3-small')
        self.client = OpenAI(api_key=self.api_key, base_url=self.api_base)

    def chat(self, messages, model=None, temperature=0.7, max_tokens=2000) -> str:
        """Send chat completion request."""
        try:
            response = self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"AI chat error: {e}")
            return ""

    def structured_output(self, messages, schema, model=None, temperature=0.3) -> dict:
        """Get structured JSON output from LLM."""
        system_msg = {
            'role': 'system',
            'content': f'You must respond with valid JSON matching this schema: {json.dumps(schema, ensure_ascii=False)}. Only output the JSON, no other text.'
        }
        all_messages = [system_msg] + messages
        result = self.chat(all_messages, model=model, temperature=temperature)
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse AI structured output: {result[:200]}")
            return {}

    def embedding(self, text, model=None) -> list:
        """Get text embedding vector."""
        try:
            response = self.client.embeddings.create(
                model=model or self.embedding_model,
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"AI embedding error: {e}")
            return []

    def chat_stream(self, messages, model=None, temperature=0.7):
        """Stream chat completion."""
        try:
            stream = self.client.chat.completions.create(
                model=model or self.model,
                messages=messages,
                temperature=temperature,
                stream=True,
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"AI chat stream error: {e}")
            yield ""
