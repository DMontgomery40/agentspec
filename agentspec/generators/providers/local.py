#!/usr/bin/env python3
"""
Local LLM provider (Ollama, LMStudio, etc.) implementation.

"""

from __future__ import annotations

import os
from typing import Optional

from agentspec.generators.providers.openai import OpenAIProvider
from agentspec.models.config import GenerationConfig


class LocalProvider(OpenAIProvider):
    """
    Local LLM provider (wraps OpenAIProvider with local defaults).

        """

    def __init__(self, config: GenerationConfig):
        """
        Initialize local provider with Ollama defaults.

        Args:
            config: Generation configuration

        Rationale:
            Override base_url if not set, defaulting to Ollama. Otherwise
            delegate everything to OpenAIProvider.

        Guardrails:
            - DO NOT require API key (local services are unauthenticated)
            - ALWAYS check OLLAMA_BASE_URL before using default
        """
        # Set base_url to Ollama default if not already set
        if not config.base_url:
            config.base_url = (
                os.getenv("OLLAMA_BASE_URL")
                or "http://localhost:11434/v1"
            )

        # Delegate to parent
        super().__init__(config)

    @property
    def name(self) -> str:
        """Override name for clearer logging."""
        return "LocalProvider (Ollama/LMStudio)"
