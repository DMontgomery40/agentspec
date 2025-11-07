#!/usr/bin/env python3
"""
OpenAI and OpenAI-compatible provider implementation.

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

        """

    def __init__(self, config: GenerationConfig):
        """Initialize OpenAI provider with config."""
        super().__init__(config)
        self._client = None
        self._instructor_client = None

    @property
    def raw_client(self):
        """Access raw OpenAI client for custom operations."""
        self._ensure_client()
        return self._client

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
