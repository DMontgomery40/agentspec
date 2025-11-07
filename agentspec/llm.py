#!/usr/bin/env python3
"""
Lightweight LLM router supporting Anthropic (Claude) and any
OpenAI-compatible API (OpenAI cloud, local Ollama, or third‑party services
that implement the OpenAI Chat Completions spec).

Usage:
- call generate_chat(model, messages, temperature, max_tokens, base_url=None)
  where messages is a list of {role: 'system'|'user'|'assistant', content: str}
"""
from __future__ import annotations

import os
from typing import List, Dict, Optional


def _is_anthropic_model(model: str) -> bool:
    """
    "
          - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features"
        ---/agentspec
    """
    m = (model or '').lower()
    return m.startswith('claude') or m.startswith('anthropic')


def generate_chat(
    model: str,
    messages: List[Dict[str, str]],
    temperature: float = 0.2,
    max_tokens: int = 2000,
    base_url: Optional[str] = None,
    provider: Optional[str] = 'auto',
) -> str:
    """
    "
          - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features"

    """
    force_anthropic = (provider or 'auto').lower() == 'anthropic'
    force_openai = (provider or 'auto').lower() == 'openai'

    if force_anthropic or (_is_anthropic_model(model) and not force_openai):
        # Lazy import to avoid hard dependency unless needed
        try:
            from anthropic import Anthropic
        except ImportError as e:
            raise RuntimeError(
                "Missing dependency: anthropic. Install with `pip install anthropic` to use Claude models."
            ) from e

        # Build a single user message by concatenating contents (Claude expects
        # a different structure, but concatenating is sufficient here)
        user_content = []
        for m in messages:
            if m.get('role') in ('system', 'user'):
                user_content.append(m.get('content', ''))
        prompt = "\n\n".join(user_content)

        client = Anthropic()
        resp = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.content[0].text

    # OpenAI-compatible path
    # Determine base_url and api key
    try:
        from openai import OpenAI
    except ImportError as e:
        raise RuntimeError(
            "Missing dependency: openai. Install with `pip install openai` to use OpenAI-compatible models (including local Ollama)."
        ) from e

    api_key = os.getenv('OPENAI_API_KEY') or os.getenv('AGENTSPEC_OPENAI_API_KEY') or 'not-needed'
    resolved_base = (
        base_url
        or os.getenv('OPENAI_BASE_URL')
        or os.getenv('AGENTSPEC_OPENAI_BASE_URL')
        or os.getenv('OLLAMA_BASE_URL')
        or 'https://api.openai.com/v1'
    )

    client = OpenAI(base_url=resolved_base, api_key=api_key)

    # Prefer Responses API. If provider doesn't support it, fall back to
    # Chat Completions for compatibility (e.g., Ollama).
    try:
        # Build a single string input that includes both system and user parts
        sys_parts = [m['content'] for m in messages if m.get('role') == 'system']
        usr_parts = [m['content'] for m in messages if m.get('role') in ('user', 'assistant')]
        input_text = "\n\n".join(sys_parts + usr_parts)

        resp = client.responses.create(
            model=model,
            input=input_text,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        # Extract text robustly
        if hasattr(resp, 'output_text') and resp.output_text:
            return str(resp.output_text)
        if hasattr(resp, 'output') and resp.output:
            # Attempt to find any text content blocks
            for item in resp.output:
                content = getattr(item, 'content', None)
                if isinstance(content, list):
                    for sub in content:
                        t = getattr(sub, 'text', None)
                        if t:
                            return str(t)
                t = getattr(content, 'text', None)
                if t:
                    return str(t)
        # Fallback
        t = getattr(resp, 'text', None)
        if t:
            return str(t)
    except Exception:
        # Fall back to Chat Completions for providers without Responses API
        pass

    # Chat Completions fallback (OpenAI-compatible providers like Ollama)
    oai_messages = []
    for m in messages:
        role = m.get('role', 'user')
        if role not in ('system', 'user', 'assistant'):
            role = 'user'
        oai_messages.append({"role": role, "content": m.get('content', '')})

    comp = client.chat.completions.create(
        model=model,
        messages=oai_messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return (comp.choices[0].message.content or "") if comp and comp.choices else ""
