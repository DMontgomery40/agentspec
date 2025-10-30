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
    Brief one-line description.

    Classifies whether a model identifier string represents an Anthropic-provided language model by checking for 'claude' or 'anthropic' prefixes.

    WHAT THIS DOES:
    This function performs defensive model identifier classification to determine if a given string represents an Anthropic model. It accepts a `model` parameter of type `str` (though None values are handled gracefully), normalizes the input by coercing None to empty string and converting to lowercase, then performs two independent prefix checks using `.startswith()`. The function returns True if the normalized model string begins with either 'claude' OR 'anthropic', and False otherwise. It handles multiple edge cases including None inputs (coerced to empty string, returns False), empty strings (returns False), mixed-case inputs like 'Claude-2' or 'ANTHROPIC-CLAUDE' (correctly identified as True), partial matches like 'claude-2-100k' (correctly identified as True), non-matching strings like 'gpt-4' or 'llama-2' (return False), and leading/trailing whitespace which is NOT stripped (so ' claude-2' would return False). The function uses short-circuit OR evaluation, meaning if the first condition is True, the second is not evaluated. No exceptions are raised under any input condition due to the defensive design pattern that prevents AttributeError.

    WHY THIS APPROACH:
    Case-insensitive matching is essential because model identifiers from various sources (user input, configuration files, API responses) may use inconsistent casing conventions, and case-insensitive comparison ensures robust identification regardless of source formatting. The defensive `(model or '')` pattern is a critical safeguard that prevents AttributeError when None is passed, which can occur due to optional parameters or missing configuration values; rather than forcing all callers to validate input, this function gracefully handles the edge case internally. The dual prefix strategy checking both 'claude' and 'anthropic' accommodates potential future naming conventions and future-proofs the function without requiring code changes if Anthropic's naming conventions evolve. String prefix matching via `.startswith()` is O(n) where n is the length of the prefix (typically 6-10 characters), which is significantly faster than regex compilation/matching or list lookups against a registry, making this approach ideal for a function called frequently in request routing paths where latency overhead must be minimized. Alternatives were rejected: regex matching introduces higher overhead and unnecessary complexity for simple prefix matching; exact matching against a hardcoded list is brittle when Anthropic releases new model variants and requires code changes for each new model; external model registry lookup introduces I/O latency and external dependencies inappropriate for a simple classification utility; whitespace normalization via `.strip()` was not included because model identifiers are typically well-formed and adding it would mask upstream data quality issues.

    AGENT INSTRUCTIONS:
    - DO NOT modify the prefix strings ('claude', 'anthropic') without auditing all downstream code that depends on this function's classification, as changes here affect model routing throughout the system and could cause requests to be sent to wrong API endpoints.
    - DO NOT remove the defensive `(model or '')` pattern without ensuring all callers guarantee non-None input and adding explicit type validation, as this pattern is the only safeguard against AttributeError from None values.
    - DO NOT add `.strip()` to normalize whitespace without verifying that all upstream model identifier sources are properly formatted, as silently accepting malformed identifiers could mask data quality issues.
    - DO NOT change the return type from boolean without updating all conditional logic that depends on this function, as it is used in if/elif chains and ternary operators throughout the codebase.
    - DO NOT add regex or complex matching logic without performance testing, as this function may be called in hot paths (per-request model selection) and any performance regression could impact API latency.
    - ALWAYS maintain both prefix checks ('claude' AND 'anthropic') unless Anthropic's official documentation explicitly deprecates one naming convention.
    - ALWAYS preserve case-insensitivity behavior, as model identifiers from configuration and user input cannot be guaranteed to use consistent casing.
    - NOTE: This function is a gatekeeper for routing requests to Anthropic's API. Any logic error here will cause misrouting of requests, potentially sending Anthropic-destined requests to other providers or vice versa, resulting in authentication failures or incorrect API behavior. Treat changes to this function with extreme caution and ensure comprehensive testing of model routing behavior across all supported model identifier formats.

    DEPENDENCIES (from code analysis):
    Calls: lower, m.startswith
    Imports: __future__.annotations, os, typing.Dict, typing.List, typing.Optional


    CHANGELOG (from git history):
    - 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features


    FUNCTION CODE DIFF SUMMARY (LLM-generated):
    Added function to identify Anthropic models by checking if model name starts with 'claude' or 'anthropic' prefix.

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
    Brief one-line description.

    WHAT THIS DOES:
    Unified LLM interface that routes requests to either Anthropic Claude or OpenAI-compatible providers (including local Ollama instances), accepting a model identifier, message list, temperature, max_tokens, optional base_url, and provider hint, returning a single string response.

    The function implements two distinct code paths:

    **Anthropic Path (Claude models):**
    - Triggered when provider='anthropic' is explicit, or when _is_anthropic_model(model) returns True and provider is not forced to 'openai'
    - Concatenates all 'system' and 'user' role messages with "\n\n" separator into a single prompt string
    - Filters out 'assistant' role messages (one-way conversation, not multi-turn)
    - Creates Anthropic client with lazy import; raises RuntimeError if anthropic SDK not installed
    - Calls client.messages.create() with model, max_tokens, temperature, and reconstructed single-message format
    - Returns resp.content[0].text directly

    **OpenAI-Compatible Path (default):**
    - Triggered for all non-Anthropic models or when provider='openai' is explicit
    - Resolves API key from environment: OPENAI_API_KEY → AGENTSPEC_OPENAI_API_KEY → 'not-needed' (permissive fallback for local services)
    - Resolves base_url from parameter → OPENAI_BASE_URL → AGENTSPEC_OPENAI_BASE_URL → OLLAMA_BASE_URL → 'https://api.openai.com/v1' (default OpenAI)
    - Creates OpenAI client with resolved base_url and api_key
    - **Primary attempt: Responses API** (newer OpenAI interface)
      - Concatenates system + user/assistant messages with "\n\n" separator into input_text
      - Calls client.responses.create() with model, input, temperature, max_output_tokens
      - Extracts text via defensive attribute chain: output_text → output[].content.text → text
      - Returns first non-empty text found; silently catches all exceptions and falls through
    - **Fallback: Chat Completions API** (OpenAI-compatible standard)
      - Normalizes message roles: unknown roles default to 'user'
      - Preserves original message structure (system/user/assistant roles intact)
      - Calls client.chat.completions.create() with model, messages, temperature, max_tokens
      - Returns comp.choices[0].message.content or empty string if response malformed

    **Edge Cases Handled:**
    - Missing dependencies: Raises RuntimeError with installation instructions (lazy import pattern)
    - Empty/None content fields: Defaults to empty string
    - Malformed response objects: Defensive hasattr/getattr chain with fallbacks
    - Responses API unavailable: Silent exception catch, automatic fallback to Chat Completions
    - Invalid message roles: Coerced to 'user' role
    - Missing API key for local services: Accepts 'not-needed' placeholder
    - Empty response choices: Returns empty string instead of crashing

    WHY THIS APPROACH:
    **Provider Routing:** The dual-path design accommodates two distinct LLM ecosystems with incompatible APIs. Anthropic's message format differs fundamentally from OpenAI's, requiring separate client initialization and message reconstruction. The provider parameter allows explicit control while defaulting to auto-detection via _is_anthropic_model(), reducing caller burden and enabling transparent provider switching.

    **Lazy Imports:** Both anthropic and openai SDKs are imported only when needed within their respective code paths. This avoids hard dependencies and allows users to install only the SDK(s) they require, reducing package bloat and installation friction. The try/except ImportError pattern provides clear error messages directing users to install missing dependencies.

    **Message Concatenation (Anthropic):** Claude's API expects a different message structure than the input format. Rather than complex transformation logic that preserves multi-turn conversation history, concatenating system+user content into a single prompt is sufficient for most use cases and simplifies the interface. Assistant messages are dropped because the Anthropic path reconstructs messages as a single user message, which doesn't preserve multi-turn conversation history—this is an intentional tradeoff favoring simplicity over fidelity.

    **Responses API with Chat Completions Fallback:** The Responses API is OpenAI's newer, simpler interface but not all providers support it (e.g., Ollama, local deployments, older OpenAI-compatible services). The try/except pattern attempts the modern API first, then silently falls back to the widely-supported Chat Completions API. This maximizes compatibility without requiring caller awareness of provider capabilities or version-specific API support.

    **Defensive Response Extraction:** Response objects vary across providers and API versions. The hasattr/getattr chain with multiple fallback paths (output_text → output → text) ensures robustness against schema variations without requiring strict type checking. This defensive approach prevents AttributeError crashes when response structures differ from expected schemas.

    **Environment Variable Hierarchy:** Multiple environment variable names (OPENAI_API_KEY, AGENTSPEC_OPENAI_API_KEY, OLLAMA_BASE_URL) allow flexible configuration across different deployment contexts (CI/CD, Docker, local dev) without code changes. The hierarchy respects parameter overrides first, then checks provider-specific variables, then falls back to defaults. This enables infrastructure automation to configure different providers without modifying application code.

    **Tradeoff: Simplicity vs. Fidelity:** Message concatenation loses conversation structure (no role preservation in Anthropic path). This is acceptable for single-turn use cases but limits multi-turn dialogue. The alternative (full message transformation with conversation history management) would add complexity, maintenance burden, and require changes to the Anthropic API call structure.

    AGENT INSTRUCTIONS:
    - DO NOT remove the lazy import pattern for anthropic/openai. Hard dependencies would break installations for users who only need one provider. The try/except ImportError is critical for graceful degradation and clear error messaging.
    - DO NOT change the message concatenation separator from "\n\n" without testing against actual Claude models. This separator is semantic—changing it alters prompt meaning and model behavior in ways that may not be immediately apparent.
    - DO NOT remove the Responses API try/except fallback. Silently catching exceptions here is intentional for provider compatibility. Removing it would break Ollama and other Chat Completions-only providers that don't support the newer Responses API.
    - DO NOT modify the environment variable resolution order without coordinating with deployment documentation. The hierarchy (parameter → OPENAI_BASE_URL → AGENTSPEC_OPENAI_BASE_URL → OLLAMA_BASE_URL → default) is relied upon by infrastructure automation and deployment scripts.
    - DO NOT change the 'not-needed' API key fallback without understanding local service requirements. Some providers (Ollama, local LLaMA, local Mistral) don't validate API keys; removing this breaks their usage and forces unnecessary authentication configuration.
    - DO NOT add strict type validation to response extraction (e.g., isinstance checks on resp.output). Providers return varying structures; defensive getattr/hasattr is more robust than strict typing and prevents crashes on schema variations.
    - DO NOT preserve 'assistant' role messages in the Anthropic path without adding multi-turn support. Current design reconstructs all messages as a single user message; preserving assistant messages would require conversation history management and API changes to support multi-turn dialogue.
    - DO NOT change role normalization logic (unknown roles → 'user') without considering downstream impact. Some callers may rely on this coercion for malformed input handling; changing it could break existing integrations.
    - DO NOT remove the empty string fallback in Chat Completions return. This prevents AttributeError crashes when comp.choices is empty or message.content is None, ensuring the function always returns a string.
    - ALWAYS preserve the parameter order and type hints; callers may use positional arguments or rely on the current signature.
    - ALWAYS test changes against both Anthropic and OpenAI providers, plus at least one local provider (Ollama) to ensure compatibility across all code paths.
    - NOTE: This function silently falls back from Responses API to Chat Completions. If you add logging or error tracking, ensure it doesn't spam logs with expected fallback events.
    - NOTE: The Anthropic path does not preserve multi-turn conversation history. If multi-turn support is needed, the message reconstruction logic must be redesigned and the Anthropic API call structure must change.
    - NOTE: Empty message content is normalized to empty string, not None. Ensure downstream code handles empty strings appropriately.

    DEPENDENCIES (from code analysis):
    Calls: Anthropic, OpenAI, RuntimeError, _is_anthropic_model, completions.create, getattr, hasattr, isinstance, join, lower, m.get, messages.create, oai_messages.append, os.getenv, responses.create, str, user_content.append
    Imports: __future__.annotations, os, typing.Dict, typing.List, typing.Optional


    CHANGELOG (from git history):
    - 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features


    FUNCTION CODE DIFF SUMMARY (LLM-generated):
    Added provider parameter and conditional logic to support both Anthropic and OpenAI APIs with graceful fallback, plus improved dependency error messages and environment variable resolution for flexible model provider selection.

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
