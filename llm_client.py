from __future__ import annotations

import json
from urllib import request
from urllib.error import URLError

from config import OPENAI_API_BASE, OPENAI_API_KEY, OPENAI_API_MODE, OPENAI_MODEL, OPENAI_REASONING_EFFORT

LLM_REQUEST_TIMEOUT_SECONDS = 120
from prompts import (
    ANALYSIS_PROMPT,
    BONUS_STACK_PROMPT,
    IDEA_PROMPT,
    LAUNCH_ASSETS_PROMPT,
    OUTLINE_PROMPT,
    SAAS_PLAN_PROMPT,
    SALES_PAGE_PROMPT,
    SYSTEM_PROMPT,
)


def has_api_key() -> bool:
    return bool(OPENAI_API_KEY)

def api_connection_status() -> tuple[bool, str]:
    if not OPENAI_API_KEY:
        return False, "Chưa có API key."
    if not OPENAI_API_BASE:
        return True, "Có API key."
    try:
        req = request.Request(
            OPENAI_API_BASE.rstrip("/") + "/models",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        )
        with request.urlopen(req, timeout=4) as response:
            if 200 <= response.status < 300:
                return True, f"Kết nối OK: {OPENAI_API_BASE}"
            return False, f"API trả status {response.status}: {OPENAI_API_BASE}"
    except URLError as error:
        return False, f"Không kết nối được API: {error.reason}"
    except Exception as error:
        return False, f"Không kết nối được API: {error}"


def analyze_with_llm(product_context: str) -> dict:
    content = _chat(ANALYSIS_PROMPT.format(product_context=product_context))
    return json.loads(_strip_json_fence(content))


def generate_ideas_with_llm(analysis_context: str, count: int = 10) -> str:
    return _chat(IDEA_PROMPT.format(analysis_context=analysis_context, count=count))


def write_sales_page_with_llm(idea_context: str) -> str:
    return _chat(SALES_PAGE_PROMPT.format(idea_context=idea_context))


def build_outline_with_llm(idea_context: str) -> str:
    return _chat(OUTLINE_PROMPT.format(idea_context=idea_context))


def create_bonus_stack_with_llm(idea_context: str) -> str:
    return _chat(BONUS_STACK_PROMPT.format(idea_context=idea_context))


def create_launch_assets_with_llm(idea_context: str) -> str:
    return _chat(LAUNCH_ASSETS_PROMPT.format(idea_context=idea_context))


def create_saas_plan_with_llm(idea_context: str) -> str:
    return _chat(SAAS_PLAN_PROMPT.format(idea_context=idea_context))


def chat_with_llm(
    prompt: str,
    *,
    reasoning_effort: str | None = None,
    max_output_tokens: int | None = None,
) -> str:
    return _chat(prompt, reasoning_effort=reasoning_effort, max_output_tokens=max_output_tokens)

def stream_chat_with_llm(
    prompt: str,
    *,
    reasoning_effort: str | None = None,
    max_output_tokens: int | None = None,
):
    yield from _chat_stream(prompt, reasoning_effort=reasoning_effort, max_output_tokens=max_output_tokens)

def _chat(
    user_prompt: str,
    *,
    reasoning_effort: str | None = None,
    max_output_tokens: int | None = None,
) -> str:
    try:
        from openai import OpenAI
    except ImportError as error:
        raise RuntimeError("OpenAI package is missing. Install with: pip install openai") from error

    client_kwargs = {"api_key": OPENAI_API_KEY, "timeout": LLM_REQUEST_TIMEOUT_SECONDS}
    if OPENAI_API_BASE:
        client_kwargs["base_url"] = OPENAI_API_BASE
    client = OpenAI(**client_kwargs)
    if OPENAI_API_MODE == "responses" or "codex" in OPENAI_MODEL.lower():
        request_kwargs = {
            "model": OPENAI_MODEL,
            "instructions": SYSTEM_PROMPT,
            "input": user_prompt,
        }
        effort = (reasoning_effort if reasoning_effort is not None else OPENAI_REASONING_EFFORT).strip().lower()
        if effort and effort not in {"default", "auto", "none", "off"}:
            request_kwargs["reasoning"] = {"effort": effort}
        if max_output_tokens:
            request_kwargs["max_output_tokens"] = max_output_tokens
        response = client.responses.create(**request_kwargs)
        return getattr(response, "output_text", "") or ""

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
    )
    return response.choices[0].message.content or ""

def _chat_stream(
    user_prompt: str,
    *,
    reasoning_effort: str | None = None,
    max_output_tokens: int | None = None,
):
    try:
        from openai import OpenAI
    except ImportError as error:
        raise RuntimeError("OpenAI package is missing. Install with: pip install openai") from error

    client_kwargs = {"api_key": OPENAI_API_KEY, "timeout": LLM_REQUEST_TIMEOUT_SECONDS}
    if OPENAI_API_BASE:
        client_kwargs["base_url"] = OPENAI_API_BASE
    client = OpenAI(**client_kwargs)

    if OPENAI_API_MODE == "responses" or "codex" in OPENAI_MODEL.lower():
        request_kwargs = {
            "model": OPENAI_MODEL,
            "instructions": SYSTEM_PROMPT,
            "input": user_prompt,
            "stream": True,
        }
        effort = (reasoning_effort if reasoning_effort is not None else OPENAI_REASONING_EFFORT).strip().lower()
        if effort and effort not in {"default", "auto", "none", "off"}:
            request_kwargs["reasoning"] = {"effort": effort}
        if max_output_tokens:
            request_kwargs["max_output_tokens"] = max_output_tokens
        stream = client.responses.create(**request_kwargs)
        for event in stream:
            if getattr(event, "type", "") == "response.output_text.delta":
                delta = getattr(event, "delta", "")
                if delta:
                    yield delta
        return

    stream = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
        stream=True,
    )
    for event in stream:
        delta = event.choices[0].delta.content if event.choices else ""
        if delta:
            yield delta


def _strip_json_fence(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned.removeprefix("```json").strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```").strip()
    if cleaned.endswith("```"):
        cleaned = cleaned.removesuffix("```").strip()
    return cleaned
