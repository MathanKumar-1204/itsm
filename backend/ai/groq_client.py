import os
import json
import logging
import time
from typing import Optional, Dict, Any, List
from config import Config

logger = logging.getLogger(__name__)


class GroqClient:
    """
    Official Groq API client supporting GPT-OSS model family (e.g., openai/gpt-oss-120b, openai/gpt-oss-20b).
    Enforces strict model verification, timeouts, and structured error handling.
    """

    def __init__(self):
        self.api_key = Config.GROQ_API_KEY
        self.primary_model = Config.GROQ_MODEL
        self.fallback_model = Config.GROQ_FALLBACK_MODEL
        self._client = None

    def _get_client(self):
        if self._client is not None:
            return self._client
        if not self.api_key:
            return None

        try:
            from groq import Groq
            self._client = Groq(api_key=self.api_key, timeout=30.0)
            return self._client
        except Exception as e:
            logger.error(f"Error creating Groq client: {e}")
            return None

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1500,
        response_format: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Executes chat completion with configured GPT-OSS model, falling back to verified fallback if needed.
        """
        client = self._get_client()
        if not client:
            raise ValueError("Groq API key is not configured. Please set GROQ_API_KEY in environment.")

        models_to_try = [self.primary_model]
        if self.fallback_model and self.fallback_model != self.primary_model:
            models_to_try.append(self.fallback_model)

        last_error = None

        for model in models_to_try:
            try:
                kwargs = {
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                }
                if response_format:
                    kwargs["response_format"] = response_format

                start_time = time.time()
                response = client.chat.completions.create(**kwargs)
                elapsed = time.time() - start_time

                content = response.choices[0].message.content
                logger.info(f"Groq completion successful with {model} in {elapsed:.2f}s")
                return {
                    "content": content,
                    "model": model,
                    "usage": {
                        "prompt_tokens": getattr(response.usage, "prompt_tokens", 0),
                        "completion_tokens": getattr(response.usage, "completion_tokens", 0),
                    },
                }
            except Exception as e:
                logger.warning(f"Groq completion failed with model {model}: {e}")
                last_error = e

        raise RuntimeError(f"All configured Groq models failed. Last error: {last_error}")

    def chat_json(self, messages: List[Dict[str, str]], temperature: float = 0.1) -> Dict[str, Any]:
        """
        Executes completion requesting JSON response format and parses the resulting string into a dict.
        """
        # Ensure system message instructs JSON
        system_json_hint = "You must respond ONLY with valid JSON conforming to the requested schema. Do not enclose in markdown ticks if possible, or return raw JSON."
        if messages and messages[0].get("role") == "system":
            messages[0]["content"] += f"\n\n{system_json_hint}"
        else:
            messages.insert(0, {"role": "system", "content": system_json_hint})

        response = self.chat_completion(
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        content = response["content"].strip()
        # Clean any backticks if model wrapped in ```json
        if content.startswith("```"):
            lines = content.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            content = "\n".join(lines).strip()

        try:
            parsed = json.loads(content)
            return parsed
        except json.JSONDecodeError as jde:
            logger.error(f"Failed to parse JSON from Groq response: {content}")
            raise ValueError(f"Model returned invalid JSON: {jde}")


groq_client = GroqClient()
