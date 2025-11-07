#!/usr/bin/env python3
"""
Terse prompt template for concise docstring generation.

"""

from __future__ import annotations

from typing import Dict, Any, Optional

from agentspec.generators.prompts.base import BasePrompt


class TersePrompt(BasePrompt):
    """
    Terse prompt builder for concise documentation.

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
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build concise user prompt.

                """

        context = context or {}
        file_path = context.get("file_path", "unknown")

        prompt_parts = [
            f"Function: {function_name}",
            f"File: {file_path}",
        ]

        prompt_parts.append(f"\nCode:\n```\n{code}\n```")

        prompt_parts.append("\nGenerate concise docstring with:")
        prompt_parts.append("- Brief description")
        prompt_parts.append("- Key rationale (WHY this approach)")
        prompt_parts.append("- 2+ specific guardrails")
        prompt_parts.append("- Args/Returns documentation")

        return "\n".join(prompt_parts)
