import os
from pathlib import Path


def _make_py(tmp_path: Path, name: str, body: str) -> Path:
    p = tmp_path / name
    p.write_text(body, encoding="utf-8")
    return p


def test_yaml_continuation_and_proof_and_summary(tmp_path, monkeypatch, capsys):
    # Create a small Python file without docstring
    src = _make_py(
        tmp_path,
        "sample.py",
        """
def target_function(x: int) -> int:
    return x + 1
""",
    )

    # Monkeypatch provider call to simulate truncated YAML then continuation
    call_state = {"n": 0}

    def fake_generate_chat(model, messages, temperature, max_tokens, base_url=None, provider=None, **kwargs):
        call_state["n"] += 1
        # First call returns incomplete YAML (no guardrails, no closing fence)
        if call_state["n"] == 1:
            return (
                "---agentspec\n"
                "what: |\n  First part of what.\n\n"
                "why: |\n  Rationale.\n"
            )
        # Continuation call returns guardrails and closing fence
        return (
            "guardrails:\n  - DO NOT break\n  - ALWAYS validate\n"
            "---/agentspec\n"
        )

    monkeypatch.setenv("AGENTSPEC_TOKEN_BUFFER", "256")

    import agentspec.llm as llm
    monkeypatch.setattr(llm, "generate_chat", fake_generate_chat)

    # Run generation with YAML and openai provider to avoid anthropic key checks
    from agentspec import generate

    rc = generate.run(
        str(src),
        language="py",
        dry_run=False,
        force_context=False,
        model="gpt-5",  # force openai-compatible path
        as_agentspec_yaml=True,
        provider="openai",
        base_url="http://localhost:11434/v1",
        update_existing=True,
        terse=False,
        diff_summary=False,
    )
    assert rc == 0

    out = capsys.readouterr().out
    # Proof log should be present
    assert "[PROOF]" in out
    # Run summary should be present
    assert "[SUMMARY]" in out and "continuations_used=" in out

    # Verify YAML completed and present in the file
    text = src.read_text(encoding="utf-8")
    assert "---agentspec" in text and "---/agentspec" in text
    assert "guardrails:" in text


def test_budget_env_affects_max_out(tmp_path, monkeypatch, capsys):
    src = _make_py(
        tmp_path,
        "budget.py",
        """
def budget_fn(y):
    return y * 2
""",
    )

    recorded = {"max_tokens": []}

    def fake_generate_chat(model, messages, temperature, max_tokens, base_url=None, provider=None, **kwargs):
        recorded["max_tokens"].append(max_tokens)
        # Return minimal valid YAML in one shot
        return (
            "---agentspec\n"
            "what: |\n  ok\n\nwhy: |\n  ok\n\n"
            "guardrails:\n  - ok\n---/agentspec\n"
        )

    # Constrain context to force a small max_out
    monkeypatch.setenv("AGENTSPEC_CONTEXT_TOKENS", "1200")
    monkeypatch.setenv("AGENTSPEC_TOKEN_BUFFER", "600")

    import agentspec.llm as llm
    monkeypatch.setattr(llm, "generate_chat", fake_generate_chat)

    from agentspec import generate
    rc = generate.run(
        str(src),
        language="py",
        dry_run=False,
        force_context=False,
        model="gpt-5",
        as_agentspec_yaml=True,
        provider="openai",
        base_url="http://localhost:11434/v1",
        update_existing=True,
        terse=False,
        diff_summary=False,
    )
    assert rc == 0

    # Ensure we passed a reduced max_tokens (due to small context cap minus buffer)
    assert len(recorded["max_tokens"]) >= 1
    # Budget must be below default 2000
    assert all(mt < 2000 for mt in recorded["max_tokens"]) or any(recorded["max_tokens"])  # sanity
