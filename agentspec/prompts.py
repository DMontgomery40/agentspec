#!/usr/bin/env python3
"""
Prompt loading and management for agentspec generation.

All system prompts are stored as .md files in agentspec/prompts/
for easy editing and iteration.
"""
from pathlib import Path
from typing import Dict, Any

# Directory containing all prompt templates
PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt(prompt_name: str) -> str:
    """
    Load a prompt template from the prompts directory.

    Args:
        prompt_name: Name of the prompt file (without .md extension)

    Returns:
        str: The loaded prompt template

    Raises:
        FileNotFoundError: If the prompt file doesn't exist
    """
    prompt_file = PROMPTS_DIR / f"{prompt_name}.md"
    if not prompt_file.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {prompt_file}\n"
            f"Available prompts in {PROMPTS_DIR}:\n"
            + "\n".join(f"  - {p.stem}" for p in PROMPTS_DIR.glob("*.md"))
        )
    return prompt_file.read_text(encoding="utf-8")


def get_verbose_docstring_prompt() -> str:
    """Get the verbose docstring generation prompt."""
    return load_prompt("verbose_docstring")


def get_terse_docstring_prompt() -> str:
    """Get the terse docstring generation prompt."""
    return load_prompt("terse_docstring")


def get_agentspec_yaml_prompt() -> str:
    """Get the agentspec YAML block generation prompt."""
    return load_prompt("agentspec_yaml")


# V2 Prompts (Clean - No Metadata Leakage)
# These prompts have:
# - NO metadata mentions (no {hard_data}, no deps.calls/imports instructions)
# - Extensive bug-catching examples (7 patterns each)
# - Anthropic best practices (XML tags, few-shot prompting)
# - Explicit anti-hallucination instructions

def get_verbose_docstring_prompt_v2() -> str:
    """Get the verbose docstring generation prompt (v2 - clean, no metadata leakage)."""
    return load_prompt("verbose_docstring_v2")


def get_terse_docstring_prompt_v2() -> str:
    """Get the terse docstring generation prompt (v2 - clean, no metadata leakage)."""
    return load_prompt("terse_docstring_v2")


def get_agentspec_yaml_prompt_v2() -> str:
    """Get the agentspec YAML block generation prompt (v2 - clean, no metadata leakage)."""
    return load_prompt("agentspec_yaml_v2")


def format_prompt(template: str, **kwargs: Any) -> str:
    """
    Format a prompt template with the provided variables.

    Args:
        template: Prompt template string with {placeholders}
        **kwargs: Variables to substitute into the template

    Returns:
        str: Formatted prompt ready to send to LLM

    Example:
        >>> template = get_verbose_docstring_prompt()
        >>> prompt = format_prompt(template, code="def foo(): pass", filepath="test.py", hard_data="...")
    """
    return template.format(**kwargs)
