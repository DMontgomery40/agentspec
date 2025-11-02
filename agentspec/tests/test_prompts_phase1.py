from pathlib import Path

from agentspec.prompts import (
    load_base_prompt,
    load_examples_json,
    load_agentspec_yaml_grammar,
)


def test_load_base_prompt_contains_title():
    text = load_base_prompt()
    assert isinstance(text, str) and text, "base_prompt.md should load non-empty text"
    assert "AgentSpec YAML Generator" in text


def test_load_agentspec_yaml_grammar_has_core_markers():
    grammar = load_agentspec_yaml_grammar()
    assert "---agentspec" in grammar
    assert "---/agentspec" in grammar
    assert "guardrails" in grammar


def test_examples_json_schema_and_anchored_example():
    data = load_examples_json()
    assert isinstance(data, dict)
    assert "examples" in data and isinstance(data["examples"], list)
    assert data["examples"], "examples.json must include at least one example"

    # Find the anchored example
    anchored = None
    for ex in data["examples"]:
        if ex.get("id") == "weak_test_assertion_jsdoc_extract":
            anchored = ex
            break

    assert anchored is not None, "Anchored example weak_test_assertion_jsdoc_extract must exist"

    # Check code context anchors to the real test file and function
    ctx = anchored.get("code_context") or {}
    assert ctx.get("file") == "tests/test_extract_javascript_agentspec.py"
    assert ctx.get("function") == "test_extract_from_jsdoc_agentspec_block"
    assert ctx.get("subject_function") == "agentspec.extract.extract_from_js_file"

    # Guardrails must include ASK USER instruction
    guards = (anchored.get("good_documentation") or {}).get("guardrails") or []
    joined = "\n".join(guards)
    assert "ASK USER" in joined, "Guardrails must include an ASK USER instruction for ambiguous intent"

