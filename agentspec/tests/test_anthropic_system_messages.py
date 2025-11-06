import types
import sys


def test_anthropic_uses_system_param(monkeypatch):
    calls = {}

    class FakeAnthropic:
        class _Msgs:
            def __init__(self):
                self.last = None

            def create(self, **kwargs):  # record kwargs
                calls.update(kwargs)
                class R:
                    content = [types.SimpleNamespace(text="ok")]  # minimal shim
                return R()

        def __init__(self):
            self.messages = self._Msgs()

    fake_mod = types.ModuleType("anthropic")
    fake_mod.Anthropic = FakeAnthropic
    monkeypatch.setitem(sys.modules, "anthropic", fake_mod)

    from agentspec.llm import generate_chat

    out = generate_chat(
        model="claude-haiku-4-5",
        messages=[
            {"role": "system", "content": "ROLE: precise doc"},
            {"role": "user", "content": "code here"},
        ],
        temperature=0.0,
        max_tokens=200,
        provider="claude",
    )

    assert out == "ok"
    # Ensures system is passed separately and messages exclude system
    assert calls.get("system") == "ROLE: precise doc"
    msg_roles = [m.get("role") for m in (calls.get("messages") or [])]
    assert "system" not in msg_roles
    assert msg_roles == ["user"]

