#!/usr/bin/env python3
"""
Verbose prompt template for detailed docstring generation.

---agentspec
what: |
  Default prompt template that generates comprehensive, detailed docstrings.

  **Characteristics:**
  - Detailed explanations in all sections
  - Multiple guardrails (minimum 3)
  - Complete dependency tracking
  - Full examples where appropriate
  - Longer rationale sections (200+ chars)

  Used by default for all generation unless --terse flag is provided.

why: |
  Verbose mode produces high-quality, comprehensive documentation that:
  - Helps agents understand code deeply
  - Prevents breaking changes (detailed guardrails)
  - Provides context for future modifications
  - Documents edge cases and design decisions

  The extra token cost is justified by improved code safety and
  reduced agent errors.

guardrails:
  - DO NOT reduce minimum requirements without team discussion
  - ALWAYS emphasize guardrails importance (core value prop)
  - DO NOT make prompts shorter to save tokens (defeats purpose)

deps:
  imports:
    - typing
  calls:
    - BasePrompt.build_system_prompt
---/agentspec
"""

from __future__ import annotations

from typing import Dict, Any, Optional

from agentspec.generators.prompts.base import BasePrompt


class VerbosePrompt(BasePrompt):
    """
    Verbose prompt builder for detailed documentation.

    ---agentspec
    what: |
      Generates prompts that instruct LLMs to create comprehensive docstrings.

      Key instructions:
      - Be thorough and detailed
      - Explain WHY not just WHAT
      - Include multiple specific guardrails
      - Document all edge cases
      - Provide complete examples

    why: |
      Default mode should produce highest quality output. Verbose prompts
      result in better agent understanding and safer code modifications.

    guardrails:
      - DO NOT reduce verbosity to save tokens
      - ALWAYS include minimum requirements (3+ guardrails, 200+ char rationale)
    ---/agentspec
    """

    def build_system_prompt(self, language: str = "python", style: str = "google") -> str:
        """Build comprehensive system prompt for verbose mode."""

        style_instructions = {
            "google": "Google-style docstrings with clear section labels (Args:, Returns:, etc.)",
            "numpy": "NumPy-style docstrings with underlined section headers (Parameters\\n----------)",
            "sphinx": "Sphinx-style docstrings with reStructuredText directives (:param:, :returns:, etc.)",
            "jsdoc": "JSDoc comments with @param, @returns, and @throws tags",
            "tsdoc": "TSDoc comments following Microsoft's TSDoc standard",
        }

        format_instruction = style_instructions.get(style, style_instructions["google"])

        system_prompt = f"""You are a code documentation expert specializing in {language} development.

Your task is to generate comprehensive, high-quality docstrings that help AI agents understand code safely.

OUTPUT FORMAT:
Generate a structured JSON object with these fields (this will be converted to a {style} docstring):

{{
  "summary": "One-line description (10-150 chars, no period at end)",
  "description": "Extended multi-paragraph explanation of what this does",
  "sections": [
    {{"title": "Args", "items": [{{"name": "param_name", "type": "param_type", "description": "what it does"}}]}},
    {{"title": "Returns", "content": "description of return value"}},
    {{"title": "Raises", "items": [{{"name": "ExceptionType", "description": "when this is raised"}}]}}
  ],
  "rationale": "WHY this implementation approach instead of alternatives (minimum 200 characters)",
  "guardrails": [
    "DO NOT change X because Y (be specific)",
    "ALWAYS preserve Z (explain why)",
    "DO NOT remove W without checking V (explain consequences)"
  ],
  "dependencies": {{
    "calls": ["function.name", "module.function"],
    "called_by": ["where.this.is.used"],
    "imports": ["module.name"]
  }}
}}

CRITICAL REQUIREMENTS:

1. **Rationale** (WHY section):
   - Explain WHY this approach was chosen
   - What alternatives were considered and rejected
   - What tradeoffs were made
   - Why specific libraries/patterns are used
   - Minimum 200 characters (be thorough!)

2. **Guardrails** (SAFETY section):
   - Minimum 3 specific guardrails
   - Each must start with "DO NOT" or "ALWAYS"
   - Explain WHAT not to change and WHY
   - Include consequences of violations
   - Be specific (not generic advice)

3. **Description**:
   - Multi-paragraph when appropriate
   - Explain edge cases and error handling
   - Document input validation and assumptions
   - Describe output format in detail

4. **Dependencies**:
   - List all functions this code calls
   - List what calls this code (if known)
   - List all imports used

EXAMPLES OF GOOD GUARDRAILS:
✅ "DO NOT change the retry limit from 3 to higher without load testing - this prevents cascade failures during outages"
✅ "ALWAYS validate input before processing - skipping validation allowed SQL injection in commit abc123"
✅ "DO NOT remove the mutex lock - concurrent access causes race condition in Redis cache updates"

EXAMPLES OF BAD GUARDRAILS (too generic):
❌ "DO NOT change this code"
❌ "Be careful when modifying"
❌ "This is important"

COMPLIANCE:
- Output MUST be valid {format_instruction}
- Python docstrings MUST be PEP 257 compliant
- JavaScript comments MUST be JSDoc compliant
- Be thorough - agents need complete information to avoid breaking changes

Generate detailed, specific, actionable documentation that prevents AI agents from making dangerous changes."""

        return system_prompt

    def build_user_prompt(
        self,
        code: str,
        function_name: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build user prompt with code to document."""

        context = context or {}
        file_path = context.get("file_path", "unknown")
        parent_class = context.get("parent_class")
        existing_docstring = context.get("existing_docstring")

        prompt_parts = [
            f"Function to document: {function_name}",
            f"File: {file_path}",
        ]

        if parent_class:
            prompt_parts.append(f"Parent class: {parent_class}")

        if existing_docstring:
            prompt_parts.append(f"\nExisting docstring (update this):\n{existing_docstring}")

        prompt_parts.append(f"\nSource code:\n```\n{code}\n```")

        prompt_parts.append("\nGenerate a comprehensive docstring with:")
        prompt_parts.append("- Thorough description of what this does")
        prompt_parts.append("- Detailed rationale (WHY this approach)")
        prompt_parts.append("- At least 3 specific, actionable guardrails")
        prompt_parts.append("- Complete argument and return documentation")
        prompt_parts.append("- Dependency tracking (what this calls, what calls this)")

        return "\n".join(prompt_parts)
