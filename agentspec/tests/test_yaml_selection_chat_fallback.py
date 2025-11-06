import types
import sys


def test_yaml_selection_prefers_valid_block_on_chat_fallback(monkeypatch):
    # Force Responses path to raise so we hit chat.completions fallback
    class FakeClient:
        def __init__(self):
            class Resp:
                def create(self, **kwargs):
                    raise RuntimeError("force fallback")
            self.responses = Resp()

            class CC:
                class _Inner:
                    def create(self, **kwargs):
                        class Item:
                            class Msg:
                                content = (
                                    # First invalid block (missing guardrails)
                                    "---agentspec\nwhat: |\n  bad\n\nwhy: |\n  bad\n---/agentspec\n"
                                    # Second valid block
                                    "---agentspec\nwhat: |\n  good\n\nwhy: |\n  ok\n\nguardrails:\n  - NOTE: ok\n---/agentspec\n"
                                )
                            message = Msg()
                        class R:
                            choices = [types.SimpleNamespace(message=Item.Msg())]
                        return R()
                create = _Inner().create
            self.chat = types.SimpleNamespace(completions=CC())

    fake_mod = types.ModuleType("openai")
    fake_mod.OpenAI = lambda *a, **k: FakeClient()
    monkeypatch.setitem(sys.modules, "openai", fake_mod)

    from agentspec.generate import generate_docstring

    code = "def f():\n    return 1\n"
    out = generate_docstring(
        code=code,
        filepath="t.py",
        model="qwen3-coder:30b",
        as_agentspec_yaml=True,
        base_url="http://localhost:11434/v1",
        provider="openai",
        terse=True,
    )

    # Only the valid block should remain
    assert out.count("---agentspec") == 1
    assert "good" in out and "bad" not in out

