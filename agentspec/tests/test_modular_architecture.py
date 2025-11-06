#!/usr/bin/env python3
"""
Smoke tests for modular architecture refactor.

Tests the core components work together without requiring actual LLM calls.
"""

from pathlib import Path

# Models
from agentspec.models.agentspec import AgentSpec, DependencyInfo
from agentspec.models.config import GenerationConfig

# Formatters
from agentspec.generators.formatters.python import (
    GoogleDocstringFormatter,
    NumpyDocstringFormatter,
)

# Prompts
from agentspec.generators.prompts import VerbosePrompt, TersePrompt


def test_agentspec_model_validation():
    """Test AgentSpec Pydantic model validates correctly."""
    # Valid spec
    spec = AgentSpec(
        summary="Process user input and return validated data",
        description="Takes raw input, validates, sanitizes",
        rationale="Using dict instead of Pydantic to preserve unknown fields for audit",
        guardrails=[
            "DO NOT remove sanitization (XSS vulnerability)",
            "DO NOT make strict=True default (breaks callers)",
        ],
    )

    assert spec.summary == "Process user input and return validated data"
    assert len(spec.guardrails) == 2

    # Invalid: too few guardrails
    try:
        AgentSpec(
            summary="Test",
            rationale="Test rationale that is long enough to meet minimum",
            guardrails=["Only one"],  # Need minimum 2
        )
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected

    # Invalid: rationale too short
    try:
        AgentSpec(
            summary="Test",
            rationale="Short",  # Need minimum 50 chars
            guardrails=["Guard 1", "Guard 2"],
        )
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected


def test_google_formatter():
    """Test Google-style formatter produces valid docstring."""
    spec = AgentSpec(
        summary="Process user input and return validated data",
        description="Takes raw user input, validates format, and sanitizes content.",
        rationale="Using dict instead of Pydantic model to preserve unknown fields for audit logging. Pydantic would silently drop them.",
        guardrails=[
            "DO NOT remove sanitization step (XSS vulnerability)",
            "DO NOT make strict=True the default (breaks existing callers)",
        ],
        dependencies=DependencyInfo(
            calls=["validate_input", "sanitize_content"],
            called_by=["api.process_request"],
        ),
    )

    formatter = GoogleDocstringFormatter()
    docstring = formatter.format(spec)

    # Check basic structure
    assert docstring.startswith('"""')
    assert docstring.endswith('"""')
    assert "Process user input" in docstring
    assert "Rationale:" in docstring
    assert "Guardrails:" in docstring
    assert "DO NOT remove sanitization" in docstring
    assert "Dependencies:" in docstring

    print("\nGoogle-style docstring:")
    print(docstring)


def test_numpy_formatter():
    """Test NumPy-style formatter produces valid docstring."""
    spec = AgentSpec(
        summary="Calculate the mean of an array",
        rationale="Using NumPy's native mean for performance. Pure Python would be 10x slower for large arrays.",
        guardrails=[
            "DO NOT replace with pure Python loop (performance regression)",
            "ALWAYS handle NaN values explicitly (different from zero)",
        ],
    )

    formatter = NumpyDocstringFormatter()
    docstring = formatter.format(spec)

    # Check NumPy-style headers
    assert "Rationale" in docstring
    assert "----------" in docstring  # NumPy uses dashed underlines

    print("\nNumPy-style docstring:")
    print(docstring)


def test_verbose_prompt_builder():
    """Test verbose prompt builder generates comprehensive prompts."""
    prompt_builder = VerbosePrompt()

    system_prompt = prompt_builder.build_system_prompt(language="python", style="google")

    # Check system prompt includes key instructions
    assert "rationale" in system_prompt.lower()
    assert "guardrails" in system_prompt.lower()
    assert "minimum" in system_prompt.lower()

    user_prompt = prompt_builder.build_user_prompt(
        code="def foo(x):\n    return x * 2",
        function_name="foo",
        context={"file_path": "test.py"}
    )

    assert "foo" in user_prompt
    assert "def foo(x)" in user_prompt

    print("\nVerbose system prompt length:", len(system_prompt))
    print("Verbose user prompt length:", len(user_prompt))


def test_terse_prompt_builder():
    """Test terse prompt builder generates concise prompts."""
    prompt_builder = TersePrompt()

    system_prompt = prompt_builder.build_system_prompt(language="python", style="google")

    # Terse should be shorter
    verbose_builder = VerbosePrompt()
    verbose_system = verbose_builder.build_system_prompt()

    assert len(system_prompt) < len(verbose_system)
    assert "concise" in system_prompt.lower() or "brief" in system_prompt.lower()

    print("\nTerse system prompt length:", len(system_prompt))
    print("Verbose system prompt length:", len(verbose_system))
    print(f"Reduction: {len(verbose_system) - len(system_prompt)} chars")


def test_generation_config_terse_mode():
    """Test GenerationConfig adjusts parameters for terse mode."""
    config = GenerationConfig(
        terse=True,
        max_tokens=2000,
        temperature=0.5,
    )

    # Terse mode should override these
    assert config.max_tokens == 500  # Capped at 500 in terse
    assert config.temperature == 0.0  # Force to 0.0 in terse


if __name__ == "__main__":
    # Run tests
    print("=" * 60)
    print("SMOKE TESTS: Modular Architecture")
    print("=" * 60)

    test_agentspec_model_validation()
    print("✅ AgentSpec model validation")

    test_google_formatter()
    print("✅ Google formatter")

    test_numpy_formatter()
    print("✅ NumPy formatter")

    test_verbose_prompt_builder()
    print("✅ Verbose prompt builder")

    test_terse_prompt_builder()
    print("✅ Terse prompt builder")

    test_generation_config_terse_mode()
    print("✅ Generation config terse mode")

    print("\n" + "=" * 60)
    print("ALL SMOKE TESTS PASSED ✅")
    print("=" * 60)
