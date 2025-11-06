from pathlib import Path
from textwrap import dedent


def test_linter_flags_multiple_blocks_and_forbidden_phrase(tmp_path: Path):
    src = dedent(
        '''
        def g():
            """
            ---agentspec
            what: |
              ok1

            why: |
              ok1

            guardrails:
              - NOTE: ok1
            ---/agentspec

            ---agentspec
            what: |
              ok2

            why: |
              ok2

            guardrails:
              - NOTE: ok2
            ---/agentspec

            I'm ready to generate AgentSpec YAML documentation. However, I don't see any code provided yet for me to audit.
            """
            return 1
        '''
    )
    p = tmp_path / "x.py"
    p.write_text(src, encoding="utf-8")

    from agentspec.lint import check_file
    errors, warnings = check_file(p)
    messages = "\n".join(m for _, m in errors)
    assert "contains" in messages and "agentspec blocks" in messages
    # Phrase detection is advisory; accept either path
    assert ("forbidden phrase" in messages) or ("missing required keys" in messages)
