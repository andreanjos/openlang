"""Model adapters for OpenLang benchmark."""

import asyncio
import os
from abc import ABC, abstractmethod


class ModelAdapter(ABC):
    name: str

    @abstractmethod
    async def complete(self, system: str, prompt: str) -> str: ...


class ClaudeAdapter(ModelAdapter):
    def __init__(self, model: str = "claude-sonnet-4-6"):
        self.name = f"claude-{model}"
        self.model = model
        import anthropic
        self.client = anthropic.AsyncAnthropic()

    async def complete(self, system: str, prompt: str) -> str:
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text


class OpenAIAdapter(ModelAdapter):
    def __init__(self, model: str = "gpt-4.1-mini"):
        self.name = model
        self.model = model
        import openai
        self.client = openai.AsyncOpenAI()

    async def complete(self, system: str, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content


class GeminiAdapter(ModelAdapter):
    def __init__(self, model: str = "gemini-2.5-flash"):
        self.name = model
        self.model = model
        from google import genai
        self.client = genai.Client()

    async def complete(self, system: str, prompt: str) -> str:
        from google.genai import types
        response = await asyncio.to_thread(
            self.client.models.generate_content,
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system,
                max_output_tokens=1024,
            ),
        )
        return response.text


def get_adapters(models: list[str] | None = None) -> list[ModelAdapter]:
    """Return requested model adapters. Defaults to all available."""
    available = {
        "claude": lambda: ClaudeAdapter(),
        "gpt": lambda: OpenAIAdapter(),
        "gemini": lambda: GeminiAdapter(),
    }
    if models is None:
        models = list(available.keys())
    return [available[m]() for m in models if m in available]
