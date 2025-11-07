#!/usr/bin/env python3
"""
Base provider abstraction for LLM interactions.

"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

from agentspec.models.agentspec import AgentSpec
from agentspec.models.config import GenerationConfig


class BaseProvider(ABC):
    """
    Abstract base class for LLM providers.

        """

    def __init__(self, config: GenerationConfig):
        """
        Initialize provider with configuration.

        Args:
            config: Generation configuration (model, temperature, etc.)

        Rationale:
            Store config for later use but don't initialize API clients yet.
            Lazy initialization avoids blocking imports and allows validation
            before making expensive API calls.

        Guardrails:
            - DO NOT make API calls in __init__
            - DO NOT validate API keys here (do it in validate_config)
            - ALWAYS store config for later use
        """
        self.config = config

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AgentSpec:
        """
        Generate structured AgentSpec from prompt.

        Args:
            prompt: User prompt describing the code to document
            system_prompt: Optional system prompt with instructions
            **kwargs: Provider-specific parameters

        Returns:
            Validated AgentSpec object

        Raises:
            RuntimeError: If provider is not configured correctly
            ValueError: If prompt is empty or invalid
            ConnectionError: If API is unreachable
            Exception: Provider-specific errors (rate limits, auth failures, etc.)

        Rationale:
            This is the primary interface for generating docstrings. Returns
            structured Pydantic models instead of raw text to ensure validation.

        Guardrails:
            - ALWAYS use Instructor for structured outputs
            - DO NOT parse JSON manually (Instructor handles it)
            - ALWAYS validate returned AgentSpec before returning
            - DO NOT retry on failures (let orchestrator handle retries)
        """
        pass

    @abstractmethod
    def generate_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        Lower-level chat interface for custom workflows.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            temperature: Sampling temperature (overrides config)
            max_tokens: Max tokens in response (overrides config)
            **kwargs: Provider-specific parameters

        Returns:
            Raw text response from LLM

        Raises:
            RuntimeError: If provider is not configured correctly
            ConnectionError: If API is unreachable
            Exception: Provider-specific errors

        Rationale:
            Some workflows need raw chat interface (e.g., multi-turn conversations,
            custom JSON parsing). This method provides escape hatch from structured
            outputs while maintaining consistent error handling.

        Guardrails:
            - DO NOT use this for standard generation (use generate() instead)
            - ALWAYS normalize message format before sending to API
            - DO NOT modify messages list in-place
        """
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate provider configuration.

        Returns:
            True if configuration is valid (API key present, model accessible, etc.)

        Raises:
            RuntimeError: If configuration is invalid (missing API key, etc.)

        Rationale:
            Explicit validation allows early failure with clear error messages
            instead of cryptic API errors on first generate() call.

        Guardrails:
            - DO NOT make expensive API calls (just check config)
            - ALWAYS raise descriptive exceptions (include what's wrong)
            - DO NOT return False (raise exception instead for clarity)
        """
        pass

    @property
    def name(self) -> str:
        """Provider name (for logging/debugging)."""
        return self.__class__.__name__

    @property
    def raw_client(self) -> Any:
        """
        Access to raw API client for custom operations.

                """
        # Subclasses should override and return their _client
        raise NotImplementedError(f"{self.__class__.__name__} does not expose raw_client")
