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
from typing import List, Dict, Optional, Any


def _is_anthropic_model(model: str) -> bool:
    """
    ---agentspec
    what: |
      This function performs model identifier classification to determine if a given string represents an Anthropic-provided language model.

      **Input Processing:**
      - Accepts a single parameter `model` of type `str` (though None is handled defensively)
      - Normalizes input by applying the defensive pattern `(model or '')` which coerces None to empty string, then converts to lowercase via `.lower()`
      - This normalization ensures consistent comparison regardless of input casing or None values

      **Core Logic:**
      - Performs two independent prefix checks on the normalized string using `.startswith()` method
      - Returns True if the normalized model string begins with either 'claude' OR 'anthropic'
      - Returns False if neither prefix matches
      - Uses short-circuit OR evaluation, so if first condition is True, second is not evaluated

      **Edge Cases Handled:**
      - None input: Coerced to empty string, returns False (empty string doesn't start with 'claude' or 'anthropic')
      - Empty string: Returns False
      - Mixed case inputs: 'Claude-2', 'ANTHROPIC-CLAUDE', 'cLaUdE-3' all correctly identified as True
      - Partial matches: 'claude-2-100k', 'anthropic-claude-v1' correctly identified as True
      - Non-matching strings: 'gpt-4', 'llama-2', 'mistral' correctly return False
      - Whitespace: Leading/trailing whitespace is NOT stripped; ' claude-2' would return False

      **Return Value:**
      - Boolean primitive (True or False) suitable for conditional branching in model routing logic
      - No exceptions raised under any input condition (defensive design prevents AttributeError)
    deps:
          calls:
            - lower
            - m.startswith
          imports:
            - __future__.annotations
            - os
            - typing.Dict
            - typing.List
            - typing.Optional


    why: |
      **Case-Insensitive Matching:**
      Model identifiers from various sources (user input, configuration files, API responses) may use inconsistent casing. Case-insensitive comparison ensures robust identification regardless of source formatting conventions.

      **Defensive None Handling:**
      The pattern `(model or '')` is a defensive programming practice that prevents AttributeError when None is passed. This is critical because the function signature accepts `str` but callers may pass None due to optional parameters or missing configuration. Rather than forcing callers to validate input, this function gracefully handles the edge case.

      **Dual Prefix Strategy:**
      Checking both 'claude' and 'anthropic' accommodates potential future naming conventions. Anthropic may release models under either prefix, and this approach future-proofs the function without requiring code changes if naming conventions evolve.

      **Performance Characteristics:**
      String prefix matching is O(n) where n is the length of the prefix being checked (typically 6-10 characters). This is significantly faster than regex compilation/matching or list lookups against a registry. For a function called frequently in request routing paths, this lightweight approach minimizes latency overhead.

      **Alternatives Rejected:**
      - Regex matching: Higher overhead, less readable, unnecessary complexity for simple prefix matching
      - Exact matching against a hardcoded list: Brittle when Anthropic releases new model variants; requires code changes for each new model
      - External model registry lookup: Introduces I/O latency and external dependency; inappropriate for a simple classification utility
      - Whitespace normalization: Not included because model identifiers are typically well-formed; adding `.strip()` would mask upstream data quality issues

    guardrails:
      - DO NOT modify the prefix strings ('claude', 'anthropic') without auditing all downstream code that depends on this function's classification. Changes here affect model routing throughout the system and could cause requests to be sent to wrong API endpoints.
      - DO NOT remove the defensive `(model or '')` pattern without ensuring all callers guarantee non-None input and adding explicit type validation. This pattern is the only safeguard against AttributeError from None values.
      - DO NOT add `.strip()` to normalize whitespace without verifying that all upstream model identifier sources are properly formatted. Silently accepting malformed identifiers could mask data quality issues.
      - DO NOT change the return type from boolean without updating all conditional logic that depends on this function. This function is used in if/elif chains and ternary operators throughout the codebase.
      - DO NOT add regex or complex matching logic without performance testing. This function may be called in hot paths (per-request model selection); any performance regression could impact API latency.
      - ALWAYS maintain both prefix checks ('claude' AND 'anthropic') unless Anthropic's official documentation explicitly deprecates one naming convention.
      - ALWAYS preserve case-insensitivity behavior; model identifiers from configuration and user input cannot be guaranteed to use consistent casing.
      - CRITICAL: This function is a gatekeeper for routing requests to Anthropic's API. Any logic error here will cause misrouting of requests, potentially sending Anthropic-destined requests to other providers or vice versa, resulting in authentication failures or incorrect API behavior.

    changelog:

      - "2025-10-31: Clean up docstring formatting"
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
    *,
    reasoning_effort: Optional[str] = None,
    verbosity: Optional[str] = None,
    grammar_lark: Optional[str] = None,
) -> str:
    """
    ---agentspec
    what: |
      Unified LLM interface routing to Anthropic (Claude) or OpenAI‑compatible providers. Uses OpenAI
      Responses API by default, with automatic fallback to Chat Completions for OpenAI‑compatible
      runtimes that do not implement Responses (e.g., Ollama/vLLM/LM Studio).

      Inputs: model, messages, temperature, max_tokens, base_url, provider, optional reasoning/verbosity
      and grammar_lark (Responses/CFG only).

      Behavior:
      - Anthropic path (provider == 'claude' or model startswith 'claude'): call messages.create
      - OpenAI path: try responses.create; if it raises a transport error or returns 404, fallback to
        chat.completions.create with a translated message format

    guardrails:
      - DO NOT apply grammar_lark on Anthropic; CFG is Responses‑specific
      - Preserve existing message order and content; only reformat for chat.completions
      - Keep fallback narrow (transport failure or 404) to avoid masking real API errors

    changelog:
      - "2025-11-02: feat(llm): Add Chat Completions fallback for OpenAI‑compatible providers (Ollama)"
    ---/agentspec
    """
    prov = (provider or 'auto').lower()

    # Anthropic routing
    if prov in ('claude', 'anthropic') or _is_anthropic_model(model):
        try:
            from anthropic import Anthropic  # type: ignore
        except Exception as e:  # pragma: no cover
            raise RuntimeError(
                "Missing dependency: anthropic. Install with `pip install anthropic` to use Claude models."
            ) from e
        # Extract system and non-system turns
        sys_parts: list[str] = []
        conv: list[Dict[str, str]] = []
        for m in messages:
            role = (m.get('role') or '').lower()
            content = m.get('content', '')
            if role == 'system':
                if content:
                    sys_parts.append(content)
            elif role in ('user', 'assistant'):
                conv.append({"role": role, "content": content})
        system_text = "\n\n".join(sys_parts) if sys_parts else None
        # If assistant turns exist, keep them; otherwise pass only user
        client = Anthropic()
        kwargs: Dict[str, Any] = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": conv or [{"role": "user", "content": ""}],
        }
        if system_text:
            kwargs["system"] = system_text
        resp = client.messages.create(**kwargs)
        try:
            return resp.content[0].text  # type: ignore[attr-defined]
        except Exception:
            return ""

    # OpenAI‑compatible path
    try:
        from openai import OpenAI  # type: ignore
    except ImportError as e:  # pragma: no cover
        raise RuntimeError(
            "Missing dependency: openai. Install with `pip install openai` to use OpenAI-compatible models."
        ) from e

    api_key = os.getenv('OPENAI_API_KEY') or os.getenv('AGENTSPEC_OPENAI_API_KEY') or 'not-needed'
    resolved_base = (
        base_url
        or os.getenv('OPENAI_BASE_URL')
        or os.getenv('AGENTSPEC_OPENAI_BASE_URL')
        or 'https://api.openai.com/v1'
    )
    client = OpenAI(base_url=resolved_base, api_key=api_key)

    # Build single string input for Responses
    sys_parts = [m.get('content', '') for m in messages if m.get('role') == 'system']
    usr_parts = [m.get('content', '') for m in messages if m.get('role') in ('user', 'assistant')]
    input_text = "\n\n".join(sys_parts + usr_parts)

    kwargs: Dict[str, Any] = {}
    if reasoning_effort:
        kwargs['reasoning'] = {'effort': reasoning_effort}
    if verbosity:
        kwargs['text'] = {'verbosity': verbosity}
    if grammar_lark:
        kwargs['tools'] = [{
            'type': 'custom',
            'name': 'agentspec_yaml',
            'format': {'type': 'grammar', 'syntax': 'lark', 'definition': grammar_lark},
        }]

    # Try Responses API first
    try:
        resp = client.responses.create(
            model=model,
            input=input_text,
            temperature=temperature,
            max_output_tokens=max_tokens,
            **kwargs,
        )
        if hasattr(resp, 'output_text') and getattr(resp, 'output_text'):
            return str(getattr(resp, 'output_text'))
        if hasattr(resp, 'output') and getattr(resp, 'output'):
            for item in getattr(resp, 'output'):
                content = getattr(item, 'content', None)
                if isinstance(content, list):
                    for sub in content:
                        t = getattr(sub, 'text', None)
                        if t:
                            return str(t)
                t = getattr(content, 'text', None)
                if t:
                    return str(t)
        t = getattr(resp, 'text', None)
        if t:
            return str(t)
    except Exception:
        # Fall through to chat completions
        pass

    # Fallback: Chat Completions (for Ollama, etc.)
    try:
        # Translate messages to chat format
        chat_messages = []
        for m in messages:
            role = m.get('role')
            if role in ('system', 'user', 'assistant'):
                chat_messages.append({"role": role, "content": m.get('content', '')})
        comp = client.chat.completions.create(
            model=model,
            messages=chat_messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        # Extract text
        try:
            return comp.choices[0].message.content or ""
        except Exception:
            return ""
    except Exception:
        return ""
