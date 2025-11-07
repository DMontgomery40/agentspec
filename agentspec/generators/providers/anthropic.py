#!/usr/bin/env python3
"""
Anthropic (Claude) provider implementation.

"""

from __future__ import annotations

import os
from typing import Optional, List, Dict, Any

from agentspec.generators.providers.base import BaseProvider
from agentspec.models.agentspec import AgentSpec
from agentspec.models.config import GenerationConfig


class AnthropicProvider(BaseProvider):
    """
    Anthropic Claude provider.

        """

    def __init__(self, config: GenerationConfig):
        """Initialize Anthropic provider with config."""
        super().__init__(config)
        self._client = None
        self._instructor_client = None

    @property
    def raw_client(self):
        """Access raw Anthropic client for custom operations."""
        self._ensure_client()
        return self._client

    def _ensure_client(self):
        """Lazy initialize Anthropic client."""
        if self._client is not None:
            return

        try:
            from anthropic import Anthropic
        except ImportError as e:
            raise RuntimeError(
                "Missing dependency: anthropic. "
                "Install with: pip install anthropic"
            ) from e

        try:
            import instructor
        except ImportError as e:
            raise RuntimeError(
                "Missing dependency: instructor. "
                "Install with: pip install instructor"
            ) from e

        # Check for API key
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY environment variable not set. "
                "Get your API key from: https://console.anthropic.com/"
            )

        # Create base client
        self._client = Anthropic(api_key=api_key)

        # Wrap with Instructor for structured outputs
        self._instructor_client = instructor.from_anthropic(self._client)

    def validate_config(self) -> bool:
        """
        Validate Anthropic configuration.

        Checks:
        - ANTHROPIC_API_KEY is set
        - anthropic library is installed
        - instructor library is installed

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
        Generate structured AgentSpec using Claude.

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
            Instructor handles JSON parsing, validation, and retries automatically.

        Guardrails:
            - ALWAYS validate prompt is non-empty
            - DO NOT modify temperature/max_tokens from config without reason
            - ALWAYS use response_model for structured outputs
        """
        self._ensure_client()

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        # Build messages list
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # Concatenate all content for Claude
        all_content = "\n\n".join(
            msg["content"] for msg in messages
            if msg.get("role") in ("system", "user")
        )

        # Call Claude with structured output via Instructor
        try:
            response = self._instructor_client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=[{"role": "user", "content": all_content}],
                response_model=AgentSpec,  # Instructor magic!
            )
            return response
        except Exception as e:
            raise RuntimeError(
                f"Anthropic API error: {str(e)}"
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
            Raw text response from Claude

        Rationale:
            For workflows that need raw text instead of structured AgentSpec.
            Uses the same concatenation logic as generate().

        Guardrails:
            - DO NOT modify message concatenation logic
            - ALWAYS filter to system/user roles only
        """
        self._ensure_client()

        # Concatenate all content
        user_content = "\n\n".join(
            msg.get("content", "")
            for msg in messages
            if msg.get("role") in ("system", "user")
        )

        # Call Claude
        response = self._client.messages.create(
            model=self.config.model,
            max_tokens=max_tokens or self.config.max_tokens,
            temperature=temperature if temperature is not None else self.config.temperature,
            messages=[{"role": "user", "content": user_content}],
        )

        return response.content[0].text
