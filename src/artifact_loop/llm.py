from __future__ import annotations

import os
from typing import TypeVar, Type

from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

T = TypeVar("T", bound=BaseModel)

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return _client


def complete_structured(
    messages: list[dict],
    response_model: Type[T],
    model: str = "gpt-4o-2024-08-06",
) -> T:
    client = _get_client()
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=messages,
        response_format=response_model,
    )
    return completion.choices[0].message.parsed
