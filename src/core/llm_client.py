from typing import List, Dict, Any, Optional

import requests

from src.core.config import settings
from src.core.logging import get_logger


logger = get_logger(__name__)


class LLMClient:
    """
    Simple OpenAI-compatible chat client.

    Assumes an endpoint compatible with:
    POST {LLM_API_BASE}/v1/chat/completions
    """

    def __init__(
        self,
        api_base: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        self.api_base = api_base or settings.LLM_API_BASE
        self.api_key = api_key or settings.LLM_API_KEY
        self.model = model or settings.LLM_MODEL

        if not self.api_key:
            logger.warning("LLM API key is not set. Calls will fail until configured.")

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 512,
    ) -> str:
        """
        Send a chat completion request and return the message content.
        """
        url = f"{self.api_base}/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        logger.info(
            "LLM chat request",
            extra={
                "model": self.model,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )

        resp = requests.post(url, json=payload, headers=headers, timeout=60)
        try:
            resp.raise_for_status()
        except Exception as e:
            logger.error(
                "LLM request failed",
                extra={
                    "status_code": resp.status_code,
                    "text": resp.text[:500],
                    "error": str(e),
                },
            )
            raise

        data = resp.json()
        try:
            content = data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(
                "Unexpected LLM response format",
                extra={
                    "response_sample": str(data)[:500],
                    "error": str(e),
                },
            )
            raise

        logger.info("LLM chat response received")
        return content
