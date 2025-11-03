import os
from pathlib import Path

from agentspec.tools.add_example import ExampleParser


def test_analyze_documentation_stub_injects_ask_user():
    os.environ["AGENTSPEC_EXAMPLES_STUB"] = "1"
    parser = ExampleParser()
    # Anchor to real test function code
    file_path = str(Path("tests/test_extract_javascript_agentspec.py").resolve())
    ctx = parser.extract_code_context(file_path, "test_extract_from_jsdoc_agentspec_block")

    # Provide a good snippet and require ASK USER
    analysis = parser.analyze_documentation(
        code=ctx.code,
        bad_output=None,
        good_output="Checks presence of the 'what' key in parsed_data; does not validate content quality.",
        correction=None,
    )
    assert isinstance(analysis, dict)
    guards = analysis.get("good_guardrails") or []
    assert any("ASK USER" in g for g in guards), "Expected an ASK USER guardrail from stub analysis"


def test_make_example_enforces_ask_user_when_required():
    os.environ["AGENTSPEC_EXAMPLES_STUB"] = "1"
    parser = ExampleParser()
    file_path = str(Path("tests/test_extract_javascript_agentspec.py").resolve())
    ctx = parser.extract_code_context(file_path, "test_extract_from_jsdoc_agentspec_block")

    record = parser.make_example(
        code_context=ctx,
        subject_function="agentspec.extract.extract_from_js_file",
        bad_output="Asserts that JSDoc was parsed and content validated",
        good_output="Checks presence of 'what' key only; does not validate quality.",
        correction="Only checks existence of 'what' key",
        require_ask_user=True,
    )
    good = (record.get("good_documentation") or {})
    guards = good.get("guardrails") or []
    assert any("ASK USER" in g for g in guards), "ASK USER guardrail must be present when required"


def test_compute_ratio_counts_good_and_bad():
    os.environ["AGENTSPEC_EXAMPLES_STUB"] = "1"
    parser = ExampleParser()

    # Synthetic dataset mirroring structure
    data = {
        "examples": [
            {"good_documentation": {"what": "ok"}},
            {"good_documentation": {"what": "ok"}, "bad_documentation": {"text": "bad"}},
            {"bad_documentation": {"text": "bad"}},
        ]
    }
    g, b, r = parser.compute_ratio(data)
    assert g == 2 and b == 2 and abs(r - (2 / 4)) < 1e-6


def test_make_example_includes_code_snippet(monkeypatch):
    os.environ["AGENTSPEC_EXAMPLES_STUB"] = "1"
    parser = ExampleParser()
    file_path = str(Path("tests/test_extract_javascript_agentspec.py").resolve())
    ctx = parser.extract_code_context(file_path, "test_extract_from_jsdoc_agentspec_block")

    record = parser.make_example(
        code_context=ctx,
        subject_function="agentspec.extract.extract_from_js_file",
        bad_output=None,
        good_output="Checks presence only",
        correction=None,
        require_ask_user=False,
    )
    assert "code_snippet" in record and isinstance(record["code_snippet"], str) and record["code_snippet"].strip()

