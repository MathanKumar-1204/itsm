import os
import json
import logging
import time
from typing import Optional, Dict, Any, List
from config import Config

logger = logging.getLogger(__name__)


class GroqClient:
    """
    Enterprise Groq API client supporting GPT-OSS model family (e.g., openai/gpt-oss-120b, openai/gpt-oss-20b)
    with multi-key failover rotation across primary and fallback API keys.
    """

    def __init__(self):
        self.primary_model = Config.GROQ_MODEL
        self.fallback_model = Config.GROQ_FALLBACK_MODEL
        self._clients: Dict[str, Any] = {}

    def get_api_keys(self) -> List[str]:
        """Retrieves all configured Groq keys from configuration."""
        return Config.get_groq_api_keys()

    def _get_client_for_key(self, api_key: str):
        if not api_key:
            return None
        if api_key in self._clients:
            return self._clients[api_key]

        try:
            from groq import Groq
            client = Groq(api_key=api_key, timeout=30.0)
            self._clients[api_key] = client
            return client
        except Exception as e:
            masked = f"...{api_key[-6:]}" if len(api_key) > 6 else "key"
            logger.error(f"Error creating Groq client for key {masked}: {e}")
            return None

    def is_configured(self) -> bool:
        return len(self.get_api_keys()) > 0

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 1500,
        response_format: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Executes chat completion with failover rotation across configured Groq API keys and models.
        """
        keys = self.get_api_keys()
        if not keys:
            raise ValueError("No Groq API keys configured. Please set GROQ_API_KEY in environment.")

        models_to_try = [self.primary_model]
        if self.fallback_model and self.fallback_model != self.primary_model:
            models_to_try.append(self.fallback_model)

        last_error = None
        attempt_details = []

        # Iterate over keys pool (primary + fallback 1 + fallback 2)
        for key_idx, key in enumerate(keys, 1):
            masked = f"...{key[-6:]}" if len(key) > 6 else f"Key #{key_idx}"
            client = self._get_client_for_key(key)
            if not client:
                continue

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
                    logger.info(
                        f"Groq completion successful using Key #{key_idx} ({masked}) with {model} in {elapsed:.2f}s"
                    )
                    return {
                        "content": content,
                        "model": model,
                        "key_index": key_idx,
                        "usage": {
                            "prompt_tokens": getattr(response.usage, "prompt_tokens", 0),
                            "completion_tokens": getattr(response.usage, "completion_tokens", 0),
                        },
                    }
                except Exception as e:
                    err_msg = str(e)
                    logger.warning(
                        f"Groq completion failed on Key #{key_idx} ({masked}) with model {model}: {err_msg}"
                    )
                    last_error = e
                    attempt_details.append(f"Key #{key_idx} ({model}): {err_msg[:120]}")
                    # If rate limited (429) or auth error, jump to next fallback key immediately
                    if "429" in err_msg or "rate limit" in err_msg.lower() or "auth" in err_msg.lower() or "quota" in err_msg.lower():
                        logger.warning(f"Rate limit / quota error on Key #{key_idx}. Failing over to next Groq key...")
                        break

        raise RuntimeError(f"All configured Groq API keys and models failed. Attempts: {'; '.join(attempt_details)}. Last error: {last_error}")

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
