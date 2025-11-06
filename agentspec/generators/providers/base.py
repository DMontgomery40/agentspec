#!/usr/bin/env python3
"""
Base provider abstraction for LLM interactions.

---agentspec
what: |
  Abstract base class defining the interface all LLM providers must implement.

  **Core Interface:**
  - generate(): Send prompt to LLM, get structured AgentSpec back
  - generate_chat(): Lower-level chat interface for custom workflows
  - validate_config(): Check provider is configured correctly

  **Design Principles:**
  - Provider-agnostic: Works with Anthropic, OpenAI, Ollama, etc.
  - Structured outputs: Returns validated Pydantic models (via Instructor)
  - Error handling: Raises descriptive exceptions on failures
  - Async-ready: Interface designed to support async in future

  Providers are responsible for:
  - API client initialization (lazy where possible)
  - Request formatting (provider-specific message structures)
  - Response parsing (extract text from provider-specific formats)
  - Error handling (API errors, rate limits, auth failures)

why: |
  ABC ensures all providers implement the same interface, enabling:
  - Swappable providers without code changes (dependency injection)
  - Consistent error handling across all LLM integrations
  - Easy testing (mock providers for unit tests)
  - Future extensibility (new providers just implement this interface)

  Using Instructor for structured outputs eliminates manual JSON parsing
  and provides automatic validation via Pydantic schemas.

guardrails:
  - DO NOT add provider-specific logic to this base class
  - ALWAYS use Instructor for structured outputs (don't parse JSON manually)
  - DO NOT make blocking I/O calls in __init__ (lazy initialization)
  - ALWAYS raise descriptive exceptions (include provider name in message)

deps:
  imports:
    - abc
    - typing
    - pydantic
---/agentspec
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

from agentspec.models.agentspec import AgentSpec
from agentspec.models.config import GenerationConfig


class BaseProvider(ABC):
    """
    Abstract base class for LLM providers.

    ---agentspec
    what: |
      Defines the contract all LLM providers must implement. Subclasses handle
      provider-specific details (API clients, message formatting, etc.) while
      presenting a uniform interface to the orchestrator.

      **Required Methods:**
      - generate(prompt, config) → AgentSpec: Generate structured docstring spec
      - generate_chat(messages, config) → str: Lower-level chat interface
      - validate_config() → bool: Check provider configuration is valid

      **Lifecycle:**
      1. Instantiate provider (lazy initialization, no I/O)
      2. Call validate_config() to check auth/connectivity
      3. Call generate() with prompt and config
      4. Provider returns validated AgentSpec or raises exception

      Subclasses should implement lazy initialization (defer API client creation
      until first generate() call) to avoid blocking during import.

    why: |
      ABC pattern enables polymorphism - the orchestrator can work with any
      provider without knowing implementation details. This is critical for:
      - Testing (use mock provider without real API calls)
      - Multi-provider support (fallback from Claude to Ollama)
      - User choice (users pick their preferred provider)

    guardrails:
      - DO NOT perform I/O in __init__ (lazy initialization only)
      - ALWAYS validate API keys before first API call
      - DO NOT swallow exceptions (let them propagate with context)
      - ALWAYS return AgentSpec from generate() (not dict or JSON string)
    ---/agentspec
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

        ---agentspec
        what: |
          Exposes the underlying API client (e.g., anthropic.Anthropic, openai.OpenAI)
          for operations that need direct access without Instructor wrapping.

          Use cases:
          - Generating plain text responses (diff summaries, commit messages)
          - Custom streaming responses
          - Operations not supported by structured generation

        why: |
          Some operations (like diff_summary) need plain text responses without
          Pydantic validation. Rather than duplicating client initialization logic,
          expose the raw client through a property.

        guardrails:
          - DO NOT use this for normal docstring generation (use generate() instead)
          - ALWAYS call _ensure_client() first in subclass implementations
          - DO NOT modify client state (read-only access)
        ---/agentspec
        """
        # Subclasses should override and return their _client
        raise NotImplementedError(f"{self.__class__.__name__} does not expose raw_client")
