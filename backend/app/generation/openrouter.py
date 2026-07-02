"""Thin OpenRouter client. Model choice is a config decision per task type."""

import json
import logging

import httpx

from ..config import settings

logger = logging.getLogger("upvex.openrouter")


class OpenRouterError(Exception):
    pass


def is_configured() -> bool:
    return bool(settings.openrouter_api_key)


async def chat_json(
    model: str,
    system_prompt: str,
    user_prompt: str,
    *,
    temperature: float = 0.7,
    max_tokens: int = 8000,
    timeout: float = 120.0,
) -> dict:
    """Call OpenRouter chat completions expecting a JSON object response."""
    if not is_configured():
        raise OpenRouterError("OPENROUTER_API_KEY is not set")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "response_format": {"type": "json_object"},
    }
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "HTTP-Referer": "https://upvex.app",
        "X-Title": "Upvex",
    }

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(
            f"{settings.openrouter_base_url}/chat/completions",
            json=payload,
            headers=headers,
        )
    if resp.status_code != 200:
        raise OpenRouterError(f"OpenRouter HTTP {resp.status_code}: {resp.text[:500]}")

    data = resp.json()
    try:
        content = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise OpenRouterError(f"Unexpected OpenRouter response shape: {exc}")

    content = content.strip()
    if content.startswith("```"):
        # strip accidental markdown fences despite instructions
        content = content.strip("`")
        if content.startswith("json"):
            content = content[4:]
    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise OpenRouterError(f"Model returned invalid JSON: {exc}; head: {content[:300]}")
