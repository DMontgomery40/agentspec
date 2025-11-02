import os
from types import ModuleType, SimpleNamespace

import importlib


def test_generate_chat_uses_responses_only(monkeypatch):
    # Create a fake openai module with only Responses API
    class FakeResp:
        def __init__(self):
            self.output_text = "ok"

    class FakeClient:
        def __init__(self, *a, **k):
            self.responses = SimpleNamespace(create=self.create)

        def create(self, *a, **k):
            return FakeResp()

    fake_mod = ModuleType("openai")
    fake_mod.OpenAI = lambda *a, **k: SimpleNamespace(
        responses=SimpleNamespace(create=lambda **kwargs: FakeResp())
    )

    monkeypatch.setitem(importlib.import_module("sys").modules, "openai", fake_mod)

    from agentspec.llm import generate_chat

    out = generate_chat(
        model="gpt-5-mini",
        messages=[{"role": "system", "content": "x"}, {"role": "user", "content": "y"}],
        base_url="https://api.openai.com/v1",
        provider="openai",
        reasoning_effort="minimal",
        verbosity="low",
    )
    assert out == "ok"


def test_generate_passes_effort_and_verbosity(monkeypatch):
    # Capture kwargs passed to responses.create via generate.generate_docstring
    calls = {}

    def stub_generate_chat(**kwargs):
        calls.update(kwargs)
        # Minimal YAML to satisfy validators in generate.generate_docstring
        return (
            "---agentspec\n"
            "what: |\n  ok\n\n"
            "why: |\n  ok\n\n"
            "guardrails:\n  - NOTE: ok\n---/agentspec\n"
        )

    monkeypatch.setattr("agentspec.llm.generate_chat", lambda *a, **k: stub_generate_chat(**k))

    from agentspec.generate import generate_docstring

    code = "def f():\n    return 1\n"
    _ = generate_docstring(
        code=code,
        filepath="t.py",
        model="gpt-5-mini",
        as_agentspec_yaml=True,
        base_url="https://api.openai.com/v1",
        provider="openai",
        terse=True,
    )

    assert calls.get("reasoning_effort") == "minimal"
    assert calls.get("verbosity") == "low"
