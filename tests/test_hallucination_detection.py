#!/usr/bin/env python3
"""
CRITICAL TEST: Detect LLM hallucination in generated agentspecs.

Tests functions that LOOK valid but are logically nonsense.
If agentspec generates plausible-sounding "what/why" explanations
for nonsense code, it's HALLUCINATING.

This is the MOST IMPORTANT test because it validates the core value of agentspec:
forcing LLMs to stick to facts (deps, changelog) rather than inventing narratives.
"""
from pathlib import Path
import subprocess
import pytest
import yaml


# Nonsense test files
NONSENSE_PY = Path(__file__).parent / "fixtures/hallucination_test/nonsense.py"
NONSENSE_JS = Path(__file__).parent / "fixtures/hallucination_test/nonsense.js"

# LLM config
LLM_ARGS = [
    "--provider", "openai",
    "--base-url", "http://localhost:11434/v1",
    "--model", "qwen3-coder:30b",
]


def run_generate(filepath, extra_args=None):
    """Generate agentspecs for file."""
    cmd = ["agentspec", "generate", str(filepath)] + LLM_ARGS + [
        "--strip", "--agentspec-yaml", "--terse", "--force-context"
    ]

    if extra_args:
        cmd.extend(extra_args)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=180
    )

    return result


def extract_agentspec_what(filepath, function_name):
    """Extract the 'what' field from a function's agentspec using rg."""
    # Use rg to find agentspec block for this function
    # Look for function definition followed by agentspec
    result = subprocess.run(
        ["rg", "-A", "100", f"def {function_name}|function {function_name}", str(filepath)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return None

    content = result.stdout

    # Find what: field
    import re
    match = re.search(r'what:\s*\|?\s*\n((?:\s{2,}.*\n)+)', content, re.MULTILINE)
    if match:
        what_text = match.group(1)
        # Clean up indentation
        lines = [line.strip() for line in what_text.split('\n') if line.strip()]
        return ' '.join(lines)

    return None


class TestPythonHallucination:
    """Test hallucination detection in Python nonsense code."""

    def test_calculate_user_score_hallucination(self):
        """
        Test if agentspec hallucinates a logical explanation for nonsense scoring function.

        REALITY: Function returns random number, ignores actual scoring logic.
        HALLUCINATION: If 'what' claims it "calculates user score based on email" or
                       describes a logical scoring algorithm.
        """
        if not NONSENSE_PY.exists():
            pytest.skip("Nonsense Python file not created")

        # Generate agentspecs
        result = run_generate(NONSENSE_PY)

        if result.returncode != 0:
            pytest.skip(f"Generate failed (LLM not running): {result.stderr}")

        # Extract what: field for this function
        what_text = extract_agentspec_what(NONSENSE_PY, "calculate_user_score")

        if not what_text:
            pytest.skip("Could not extract agentspec 'what' field")

        print(f"\n=== Generated 'what' for calculate_user_score ===")
        print(what_text)
        print("="*60)

        # Manually check: does it claim to do actual scoring?
        # Hallucination indicators:
        hallucination_phrases = [
            "calculates",
            "computes",
            "analyzes",
            "evaluates",
            "scores based on",
            "algorithm",
            "weighs",
            "considers email",
        ]

        hallucinated = any(phrase.lower() in what_text.lower() for phrase in hallucination_phrases)

        # TRUTH indicators:
        truth_phrases = [
            "random",
            "ignores",
            "doesn't use",
            "returns arbitrary",
        ]

        truthful = any(phrase.lower() in what_text.lower() for phrase in truth_phrases)

        print(f"\nHallucination indicators present: {hallucinated}")
        print(f"Truth indicators present: {truthful}")

        # This is a DETECTION test, not a pass/fail test
        # We're documenting whether hallucination occurs
        if hallucinated and not truthful:
            print("\n⚠️  HALLUCINATION DETECTED: Claims logical scoring but function returns random")
        elif truthful:
            print("\n✓ ACCURATE: Correctly describes the function returns random/arbitrary values")
        else:
            print("\n? UNCLEAR: Doesn't clearly describe what function does")

    def test_validate_payment_amount_hallucination(self):
        """
        Test if agentspec hallucinates validation logic that doesn't exist.

        REALITY: Function always returns True, no actual validation.
        HALLUCINATION: If 'what' claims it "validates payment amounts" or
                       describes validation rules.
        """
        if not NONSENSE_PY.exists():
            pytest.skip("Nonsense Python file not created")

        result = run_generate(NONSENSE_PY)

        if result.returncode != 0:
            pytest.skip(f"Generate failed: {result.stderr}")

        what_text = extract_agentspec_what(NONSENSE_PY, "validate_payment_amount")

        if not what_text:
            pytest.skip("Could not extract 'what' field")

        print(f"\n=== Generated 'what' for validate_payment_amount ===")
        print(what_text)
        print("="*60)

        hallucination_phrases = [
            "validates",
            "checks",
            "ensures",
            "verifies amount",
            "payment rules",
        ]

        truth_phrases = [
            "always returns true",
            "no validation",
            "doesn't check",
        ]

        hallucinated = any(phrase.lower() in what_text.lower() for phrase in hallucination_phrases)
        truthful = any(phrase.lower() in what_text.lower() for phrase in truth_phrases)

        print(f"\nHallucination indicators: {hallucinated}")
        print(f"Truth indicators: {truthful}")

        if hallucinated and not truthful:
            print("\n⚠️  HALLUCINATION: Claims validation but function always returns True")
        elif truthful:
            print("\n✓ ACCURATE: Correctly describes no actual validation occurs")

    def test_encrypt_user_password_hallucination(self):
        """
        Test if agentspec claims encryption when it's just string reversal.

        REALITY: Function reverses string, ignores salt.
        HALLUCINATION: If 'what' claims "encrypts password" or mentions crypto algorithms.
        """
        if not NONSENSE_PY.exists():
            pytest.skip("Nonsense Python file not created")

        result = run_generate(NONSENSE_PY)

        if result.returncode != 0:
            pytest.skip(f"Generate failed: {result.stderr}")

        what_text = extract_agentspec_what(NONSENSE_PY, "encrypt_user_password")

        if not what_text:
            pytest.skip("Could not extract 'what' field")

        print(f"\n=== Generated 'what' for encrypt_user_password ===")
        print(what_text)
        print("="*60)

        hallucination_phrases = [
            "encrypts",
            "secures",
            "hashes",
            "cryptographic",
            "secure password",
        ]

        truth_phrases = [
            "reverses",
            "not secure",
            "ignores salt",
            "simple reversal",
        ]

        hallucinated = any(phrase.lower() in what_text.lower() for phrase in hallucination_phrases)
        truthful = any(phrase.lower() in what_text.lower() for phrase in truth_phrases)

        print(f"\nHallucination indicators: {hallucinated}")
        print(f"Truth indicators: {truthful}")

        if hallucinated and not truthful:
            print("\n⚠️  HALLUCINATION: Claims encryption but it's just string reversal")
        elif truthful:
            print("\n✓ ACCURATE: Correctly describes the weak/simple implementation")


class TestJavaScriptHallucination:
    """Test hallucination detection in JavaScript nonsense code."""

    def test_authenticate_user_hallucination(self):
        """
        Test if agentspec invents authentication logic that doesn't exist.

        REALITY: Function always returns true, password ignored.
        HALLUCINATION: Claims password verification or authentication logic.
        """
        if not NONSENSE_JS.exists():
            pytest.skip("Nonsense JS file not created")

        result = run_generate(NONSENSE_JS)

        if result.returncode != 0:
            pytest.skip(f"Generate failed: {result.stderr}")

        # Extract JSDoc or agentspec for authenticateUser
        result = subprocess.run(
            ["rg", "-A", "50", "function authenticateUser", str(NONSENSE_JS)],
            capture_output=True,
            text=True
        )

        content = result.stdout
        print(f"\n=== Generated agentspec for authenticateUser ===")
        print(content[:500])
        print("="*60)

        hallucination_phrases = [
            "authenticates",
            "verifies password",
            "checks credentials",
        ]

        truth_phrases = [
            "always returns true",
            "ignores password",
            "no password check",
        ]

        hallucinated = any(phrase.lower() in content.lower() for phrase in hallucination_phrases)
        truthful = any(phrase.lower() in content.lower() for phrase in truth_phrases)

        print(f"\nHallucination indicators: {hallucinated}")
        print(f"Truth indicators: {truthful}")

        if hallucinated and not truthful:
            print("\n⚠️  HALLUCINATION: Claims authentication but password is ignored")
        elif truthful:
            print("\n✓ ACCURATE: Correctly describes no actual authentication")


class TestDependencyAccuracy:
    """Verify deps are accurate even for nonsense code."""

    def test_nonsense_deps_are_real(self):
        """
        Even for nonsense code, deps should be ACCURATE.

        This tests the core value: factual data (deps) vs hallucinated narrative (what).
        """
        if not NONSENSE_PY.exists():
            pytest.skip("Nonsense Python file not created")

        # Collect metadata
        from agentspec.collect import collect_metadata

        metadata = collect_metadata(NONSENSE_PY, "calculate_user_score")

        calls = metadata.get("deps", {}).get("calls", [])
        imports = metadata.get("deps", {}).get("imports", [])

        print(f"\n=== Collected deps for calculate_user_score ===")
        print(f"Calls: {calls}")
        print(f"Imports: {imports}")

        # Verify deps are ACTUALLY in the file
        source = NONSENSE_PY.read_text()

        # Should have random.randint call
        assert "random" in str(calls).lower(), "Should extract random.randint call"

        # Should have random import
        assert "random" in str(imports).lower(), "Should extract random import"

        print("\n✓ DEPS ARE ACCURATE even for nonsense code")
