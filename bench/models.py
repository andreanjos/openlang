"""Model adapters — Codex via CLI, Gemini via SDK."""

import asyncio
import tempfile
import os
from abc import ABC, abstractmethod


class ModelAdapter(ABC):
    name: str

    @abstractmethod
    async def complete(self, system: str, prompt: str) -> str: ...


async def _run_cli(cmd: list[str], timeout: int = 90) -> str:
    """Run a CLI command and return stdout."""
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await asyncio.wait_for(
        proc.communicate(),
        timeout=timeout,
    )
    out = stdout.decode().strip()
    if proc.returncode != 0 and not out:
        err = stderr.decode().strip()
        # Filter out Node deprecation warnings
        err_lines = [
            l
            for l in err.split("\n")
            if "DeprecationWarning" not in l and "trace-deprecation" not in l
        ]
        raise RuntimeError("\n".join(err_lines)[:200])
    return out


def _write_temp(content: str) -> str:
    """Write content to a temp file, return path."""
    fd, path = tempfile.mkstemp(suffix=".txt", prefix="openlang_")
    os.write(fd, content.encode())
    os.close(fd)
    return path


class CodexAdapter(ModelAdapter):
    def __init__(self):
        self.name = "codex"

    async def complete(self, system: str, prompt: str) -> str:
        full_prompt = f"{system}\n\n---\n\n{prompt}"
        path = _write_temp(full_prompt)
        try:
            return await _run_cli(
                [
                    "codex",
                    "exec",
                    f"Read the file {path} and follow the instructions inside. Output your response to stdout only.",
                ],
                timeout=90,
            )
        finally:
            os.unlink(path)


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
                max_output_tokens=4096,
            ),
        )
        return response.text


def get_adapters(models: list[str] | None = None) -> list[ModelAdapter]:
    """Return requested model adapters."""
    available = {
        "codex": CodexAdapter,
        "gemini": GeminiAdapter,
    }
    if models is None:
        models = list(available.keys())
    return [available[m]() for m in models if m in available]
