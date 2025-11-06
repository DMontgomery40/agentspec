#!/usr/bin/env python3
"""
Local LLM provider (Ollama, LMStudio, etc.) implementation.

---agentspec
what: |
  Convenience wrapper around OpenAIProvider specifically for local LLM services.

  **Supported Services:**
  - Ollama (http://localhost:11434/v1)
  - LM Studio (http://localhost:1234/v1)
  - LocalAI
  - Any local OpenAI-compatible server

  **Configuration:**
  - Automatically uses OLLAMA_BASE_URL if set
  - Falls back to http://localhost:11434/v1 (Ollama default)
  - Uses "not-needed" as API key (local services don't need auth)

  **Common Models (Ollama):**
  - llama3.2 (Meta's Llama 3.2)
  - mistral (Mistral AI)
  - codellama (Code-specialized Llama)
  - qwen2.5-coder (Alibaba's code model)
  - deepseek-coder (DeepSeek's code model)

why: |
  Local-first LLM support enables:
  - Privacy (no data sent to external APIs)
  - Cost savings (no API fees)
  - Offline usage (no internet required)
  - Experimentation (try different open models)

  This is a thin wrapper around OpenAIProvider because Ollama implements the
  OpenAI API standard. No need to duplicate code - just set sensible defaults.

guardrails:
  - DO NOT add Ollama-specific logic here (keep it in OpenAIProvider)
  - ALWAYS use OpenAI-compatible standard (don't create custom API)
  - DO NOT require API key (local services are unauthenticated)
  - ALWAYS default to localhost:11434 (standard Ollama port)

deps:
  imports:
    - typing
  calls:
    - OpenAIProvider.__init__
---/agentspec
"""

from __future__ import annotations

import os
from typing import Optional

from agentspec.generators.providers.openai import OpenAIProvider
from agentspec.models.config import GenerationConfig


class LocalProvider(OpenAIProvider):
    """
    Local LLM provider (wraps OpenAIProvider with local defaults).

    ---agentspec
    what: |
      Extends OpenAIProvider with defaults optimized for local LLM services:
      - Base URL defaults to http://localhost:11434/v1 (Ollama)
      - API key defaults to "not-needed" (no auth)
      - Otherwise identical to OpenAIProvider

      This is purely a convenience class - users can achieve the same result
      by using OpenAIProvider with --base-url http://localhost:11434/v1.

    why: |
      Explicit LocalProvider class improves UX:
      - Clearer intent (--provider local vs --provider openai --base-url ...)
      - Better error messages (can detect Ollama not running)
      - Easier documentation (one section for local, one for cloud)

    guardrails:
      - DO NOT override generate() or generate_chat() (use parent implementations)
      - DO NOT add custom logic (keep it generic for all local services)
      - ALWAYS inherit from OpenAIProvider (don't duplicate code)
    ---/agentspec
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
