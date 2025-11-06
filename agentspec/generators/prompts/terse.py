#!/usr/bin/env python3
"""
Terse prompt template for concise docstring generation.

---agentspec
what: |
  Prompt template for generating concise, focused docstrings.

  **Characteristics:**
  - Shorter descriptions (focus on essentials)
  - Minimum 2 guardrails (vs 3+ in verbose)
  - Shorter rationale (100+ chars vs 200+)
  - No unnecessary examples
  - max_tokens=500 (vs 2000 in verbose)

  Used when --terse flag is provided or context window is limited.

why: |
  Terse mode serves specific use cases:
  - Limited context windows (fitting more functions)
  - Simple/obvious functions (don't need lengthy explanations)
  - Quick iteration (faster LLM responses)
  - Cost optimization (fewer tokens)

  Still includes core safety features (Rationale, Guardrails) but more concise.

guardrails:
  - DO NOT eliminate Rationale or Guardrails (required even in terse mode)
  - DO NOT reduce to placeholder text (defeats purpose)
  - ALWAYS maintain minimum quality bar (2 guardrails, 100 char rationale)

deps:
  imports:
    - typing
  calls:
    - BasePrompt.build_system_prompt
---/agentspec
"""

from __future__ import annotations

from typing import Dict, Any, Optional, TYPE_CHECKING

from agentspec.generators.prompts.base import BasePrompt

if TYPE_CHECKING:
    from agentspec.collectors.base import CollectedMetadata


class TersePrompt(BasePrompt):
    """
    Terse prompt builder for concise documentation.

    ---agentspec
    what: |
      Generates prompts that instruct LLMs to create focused, concise docstrings.

      Key instructions:
      - Be concise but complete
      - Focus on critical information
      - Minimum 2 guardrails (not 3+)
      - Shorter rationale (but still present)
      - Skip verbose examples

    why: |
      Some situations benefit from concise docs (simple functions,
      context window limits, cost optimization). Terse mode provides
      core safety while reducing verbosity.

    guardrails:
      - DO NOT skip required sections (Rationale, Guardrails still mandatory)
      - ALWAYS maintain minimum quality (no placeholders)
    ---/agentspec
    """

    def build_system_prompt(self, language: str = "python", style: str = "google") -> str:
        """Build concise system prompt for terse mode."""

        style_instructions = {
            "google": "Google-style docstrings",
            "numpy": "NumPy-style docstrings",
            "sphinx": "Sphinx-style docstrings",
            "jsdoc": "JSDoc comments",
            "tsdoc": "TSDoc comments",
        }

        format_instruction = style_instructions.get(style, style_instructions["google"])

        system_prompt = f"""You are a code documentation expert. Generate CONCISE but complete {language} docstrings.

OUTPUT FORMAT:
JSON object with these fields:

{{
  "summary": "One-line description",
  "description": "Brief explanation (optional, only if non-obvious)",
  "sections": [
    {{"title": "Args", "items": [{{"name": "x", "type": "int", "description": "brief desc"}}]}},
    {{"title": "Returns", "content": "return value description"}}
  ],
  "rationale": "WHY this approach (minimum 100 chars, focus on key decision)",
  "guardrails": [
    "DO NOT change X because Y",
    "ALWAYS preserve Z"
  ]
}}

REQUIREMENTS:

1. **Rationale**: Minimum 100 characters. Focus on the ONE key decision/tradeoff.

2. **Guardrails**: Minimum 2. Must be specific and actionable.

3. **Description**: Only include if behavior is non-obvious. Skip for simple functions.

BE CONCISE:
- Skip verbose explanations
- Focus on critical information
- Omit obvious details
- Keep it focused and actionable

COMPLIANCE:
- Must be valid {format_instruction}
- Must include Rationale and Guardrails (core safety features)

Generate focused, concise documentation that captures critical safety information."""

        return system_prompt

    def build_user_prompt(
        self,
        code: str,
        function_name: str,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional["CollectedMetadata"] = None
    ) -> str:
        """
        Build concise user prompt.

        ---agentspec
        what: |
          Constructs terse user prompt with essential information only:
          - Function identification
          - Source code
          - Key metadata (if available, formatted concisely)
          - Generation instructions

        why: |
          Terse mode optimizes for token efficiency while maintaining quality.
          Metadata still included but more concisely formatted than verbose mode.

        guardrails:
          - ALWAYS handle metadata=None case (backwards compatibility)
          - DO NOT include verbose metadata formatting (defeats terse purpose)
          - ALWAYS include essential facts (params, exceptions, complexity)
        ---/agentspec
        """

        context = context or {}
        file_path = context.get("file_path", "unknown")

        prompt_parts = [
            f"Function: {function_name}",
            f"File: {file_path}",
        ]

        # Include metadata concisely if available
        if metadata and metadata.code_analysis:
            facts = []

            if "signature" in metadata.code_analysis:
                sig = metadata.code_analysis["signature"]
                params = sig.get("parameters", [])
                facts.append(f"{len(params)} params")
                if sig.get("return_type"):
                    facts.append(f"returns {sig['return_type']}")

            if "exceptions" in metadata.code_analysis:
                exceptions = metadata.code_analysis["exceptions"]
                if exceptions:
                    exc_types = [e.get("type") for e in exceptions]
                    facts.append(f"raises {', '.join(exc_types)}")

            if "complexity" in metadata.code_analysis:
                comp = metadata.code_analysis["complexity"]
                facts.append(f"complexity {comp.get('cyclomatic_complexity')}")

            if facts:
                prompt_parts.append(f"Facts: {' | '.join(facts)}")

        prompt_parts.append(f"\nCode:\n```\n{code}\n```")

        prompt_parts.append("\nGenerate concise docstring with:")
        prompt_parts.append("- Brief description")
        prompt_parts.append("- Key rationale (WHY this approach)")
        prompt_parts.append("- 2+ specific guardrails")
        prompt_parts.append("- Args/Returns documentation")

        return "\n".join(prompt_parts)
