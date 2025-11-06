#!/usr/bin/env python3
"""
OpenAI and OpenAI-compatible provider implementation.

---agentspec
what: |
  Concrete implementation of BaseProvider for OpenAI and OpenAI-compatible APIs.

  **Supports:**
  - OpenAI cloud (GPT-4, GPT-5, etc.)
  - Ollama (local models like llama3.2, mistral, etc.)
  - Any OpenAI-compatible API (LMStudio, LocalAI, etc.)

  **Environment Variables:**
  - OPENAI_API_KEY: API key (optional for local services)
  - AGENTSPEC_OPENAI_API_KEY: Alternative API key env var
  - OPENAI_BASE_URL: Base URL for API (default: https://api.openai.com/v1)
  - AGENTSPEC_OPENAI_BASE_URL: Alternative base URL env var
  - OLLAMA_BASE_URL: Ollama-specific base URL

  **Priority Chain:**
  - API key: CLI arg > OPENAI_API_KEY > AGENTSPEC_OPENAI_API_KEY > "not-needed"
  - Base URL: CLI arg > OPENAI_BASE_URL > AGENTSPEC_OPENAI_BASE_URL > OLLAMA_BASE_URL > default

why: |
  OpenAI-compatible API standard enables local-first workflows (Ollama) and
  multi-provider support (OpenAI, Azure, custom deployments) without code changes.

  Fallback to "not-needed" API key supports local services (Ollama, LMStudio)
  that don't require authentication.

  Instructor provides unified interface for structured outputs across all
  OpenAI-compatible providers.

guardrails:
  - DO NOT remove "not-needed" API key fallback (breaks Ollama)
  - DO NOT change environment variable priority chain (breaks user configs)
  - DO NOT remove chat completions fallback (not all providers support responses API)
  - ALWAYS preserve message role structure (system/user/assistant)

deps:
  imports:
    - openai
    - instructor
    - os
  calls:
    - BaseProvider.__init__
    - instructor.from_openai
---/agentspec
"""

from __future__ import annotations

import os
from typing import Optional, List, Dict, Any

from agentspec.generators.providers.base import BaseProvider
from agentspec.models.agentspec import AgentSpec
from agentspec.models.config import GenerationConfig


class OpenAIProvider(BaseProvider):
    """
    OpenAI and OpenAI-compatible provider.

    ---agentspec
    what: |
      Implements BaseProvider for OpenAI and any OpenAI-compatible API.

      **Initialization:**
      - Lazy-loads openai and instructor libraries
      - Resolves API key and base URL from environment or config
      - Creates Instructor-wrapped client on first use

      **Message Handling:**
      - Preserves system/user/assistant role structure (OpenAI format)
      - Normalizes unknown roles to 'user'
      - No message concatenation (unlike Anthropic provider)

      **Structured Outputs:**
      - Uses Instructor's `client.chat.completions.create()` with response_model
      - Automatic JSON schema generation from Pydantic models
      - Built-in retry logic with exponential backoff

      **Fallback Logic:**
      - API key: Try multiple env vars, fallback to "not-needed" for local services
      - Base URL: Try multiple env vars, fallback to OpenAI default

    why: |
      Preserving OpenAI message format (vs Anthropic's concatenation) enables
      proper multi-turn conversations if needed in future. More flexibility.

      Environment variable fallback chain supports diverse deployment scenarios:
      - Cloud: OPENAI_API_KEY + default base URL
      - Ollama: OLLAMA_BASE_URL + "not-needed" API key
      - Custom: AGENTSPEC_OPENAI_BASE_URL + AGENTSPEC_OPENAI_API_KEY

    guardrails:
      - DO NOT remove environment variable fallbacks (breaks deployments)
      - DO NOT change message format (breaks OpenAI API compliance)
      - ALWAYS validate roles are system/user/assistant
      - DO NOT remove lazy import (breaks optional dependency)
    ---/agentspec
    """

    def __init__(self, config: GenerationConfig):
        """Initialize OpenAI provider with config."""
        super().__init__(config)
        self._client = None
        self._instructor_client = None

    def _ensure_client(self):
        """Lazy initialize OpenAI client."""
        if self._client is not None:
            return

        try:
            from openai import OpenAI
        except ImportError as e:
            raise RuntimeError(
                "Missing dependency: openai. "
                "Install with: pip install openai"
            ) from e

        try:
            import instructor
        except ImportError as e:
            raise RuntimeError(
                "Missing dependency: instructor. "
                "Install with: pip install instructor"
            ) from e

        # Resolve API key (fallback chain)
        api_key = (
            os.getenv("OPENAI_API_KEY")
            or os.getenv("AGENTSPEC_OPENAI_API_KEY")
            or "not-needed"  # For local services like Ollama
        )

        # Resolve base URL (fallback chain)
        base_url = (
            self.config.base_url  # CLI argument takes precedence
            or os.getenv("OPENAI_BASE_URL")
            or os.getenv("AGENTSPEC_OPENAI_BASE_URL")
            or os.getenv("OLLAMA_BASE_URL")
            or "https://api.openai.com/v1"  # Default OpenAI
        )

        # Create base client
        self._client = OpenAI(base_url=base_url, api_key=api_key)

        # Wrap with Instructor for structured outputs
        self._instructor_client = instructor.from_openai(self._client)

    def validate_config(self) -> bool:
        """
        Validate OpenAI configuration.

        Checks:
        - openai library is installed
        - instructor library is installed
        - API key is set (or "not-needed" for local)
        - Base URL is set

        Returns:
            True if valid

        Raises:
            RuntimeError: If configuration is invalid
        """
        self._ensure_client()  # Will raise if invalid
        return True

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AgentSpec:
        """
        Generate structured AgentSpec using OpenAI-compatible API.

        Args:
            prompt: User prompt describing the code
            system_prompt: System instructions (generation guidelines)
            **kwargs: Additional parameters (ignored for now)

        Returns:
            Validated AgentSpec object

        Raises:
            RuntimeError: If provider not configured
            ValueError: If prompt is empty
            Exception: API errors, rate limits, etc.

        Rationale:
            Uses Instructor's response_model parameter to get structured output.
            Preserves OpenAI message format (system/user roles) for compatibility.

        Guardrails:
            - ALWAYS validate prompt is non-empty
            - DO NOT modify temperature/max_tokens from config without reason
            - ALWAYS preserve message role structure
        """
        self._ensure_client()

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        # Build messages list (OpenAI format)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Call OpenAI with structured output via Instructor
        try:
            response = self._instructor_client.chat.completions.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=messages,
                response_model=AgentSpec,  # Instructor magic!
            )
            return response
        except Exception as e:
            raise RuntimeError(
                f"OpenAI API error: {str(e)}"
            ) from e

    def generate_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Lower-level chat interface (returns raw text).

        Args:
            messages: List of {role, content} dicts
            temperature: Override config temperature
            max_tokens: Override config max_tokens
            **kwargs: Additional parameters

        Returns:
            Raw text response from OpenAI

        Rationale:
            For workflows that need raw text instead of structured AgentSpec.
            Preserves full message structure (system/user/assistant roles).

        Guardrails:
            - DO NOT modify message structure
            - ALWAYS normalize unknown roles to 'user'
            - DO NOT concatenate messages (unlike Anthropic)
        """
        self._ensure_client()

        # Normalize messages (ensure valid roles)
        normalized_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            if role not in ("system", "user", "assistant"):
                role = "user"  # Fallback for unknown roles
            normalized_messages.append({
                "role": role,
                "content": msg.get("content", "")
            })

        # Call OpenAI
        response = self._client.chat.completions.create(
            model=self.config.model,
            max_tokens=max_tokens or self.config.max_tokens,
            temperature=temperature if temperature is not None else self.config.temperature,
            messages=normalized_messages,
        )

        return response.choices[0].message.content or ""
