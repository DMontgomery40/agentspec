#!/usr/bin/env python3
"""
Base prompt abstraction for LLM generation.

---agentspec
what: |
  Abstract base class for prompt templates and builders.

  **Core Interface:**
  - build_system_prompt() → str: System-level instructions
  - build_user_prompt(code, context) → str: User prompt with code
  - get_examples() → List[str]: Few-shot examples (optional)

  Prompt builders are stateless and reusable.

why: |
  Separating prompts from generation logic enables:
  - A/B testing different prompt strategies
  - Easy updates to prompts without code changes
  - Language-specific prompt variations
  - Terse vs verbose modes

guardrails:
  - DO NOT hardcode prompts in providers (use prompt builders)
  - ALWAYS include instruction about PEP 257/JSDoc compliance
  - ALWAYS emphasize Rationale and Guardrails sections (core value)

deps:
  imports:
    - abc
    - typing
---/agentspec
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BasePrompt(ABC):
    """
    Abstract base class for prompt builders.

    ---agentspec
    what: |
      Defines the interface for building LLM prompts.

      Prompts are split into:
      - System prompt: Overall instructions and guidelines
      - User prompt: Specific code to document

      This separation enables better prompt engineering and clearer
      separation of concerns.

    why: |
      ABC ensures consistent prompt interface across all modes.
      Enables polymorphic usage (verbose/terse/custom prompts).

    guardrails:
      - DO NOT put code in system prompt (only instructions)
      - ALWAYS include format specification (Google/NumPy/etc.)
      - DO NOT make prompts language-specific in base class
    ---/agentspec
    """

    @abstractmethod
    def build_system_prompt(self, language: str = "python", style: str = "google") -> str:
        """
        Build system-level prompt with instructions.

        Args:
            language: Programming language (python, javascript, typescript)
            style: Docstring style (google, numpy, sphinx, jsdoc, tsdoc)

        Returns:
            System prompt text

        Rationale:
            System prompt contains general instructions that apply to all
            code in the session. Separating it from user prompt enables
            multi-turn conversations if needed.

        Guardrails:
            - ALWAYS include PEP 257/JSDoc compliance requirement
            - ALWAYS emphasize Rationale and Guardrails importance
            - DO NOT include specific code examples (use user prompt)
        """
        pass

    @abstractmethod
    def build_user_prompt(
        self,
        code: str,
        function_name: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build user prompt with specific code to document.

        Args:
            code: Function/class source code
            function_name: Name of function to document
            context: Optional context (file path, existing docstring, etc.)

        Returns:
            User prompt text

        Rationale:
            User prompt contains the specific code and any context needed
            for documentation generation.

        Guardrails:
            - ALWAYS include the full code (don't truncate)
            - ALWAYS include function name (helps LLM focus)
            - DO NOT include existing docstring in code (provide separately)
        """
        pass

    def get_examples(self) -> List[str]:
        """
        Get few-shot examples (optional).

        Returns:
            List of example prompts/responses

        Rationale:
            Few-shot examples can improve LLM output quality for
            specific formatting or edge cases. Optional because
            they increase token usage.

        Guardrails:
            - DO NOT include more than 2-3 examples (token cost)
            - ALWAYS use realistic, high-quality examples
        """
        return []
