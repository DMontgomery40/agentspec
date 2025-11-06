import os
from pathlib import Path


def test_diff_summary_flow(monkeypatch, tmp_path: Path):
    # Make a temp python file with a minimal function
    """
    ```yaml
    ---agentspec
    what: |
      Tests that `process_file()` generates both AgentSpec YAML docstrings AND a separate diff summary.
      Flow: (1) fake LLM returns YAML for docstring, (2) fake LLM returns "Diff Summary:\n- changed things" when system prompt mentions "Diff Summary", (3) `collect_function_code_diffs()` returns git history, (4) `apply_docstring_with_metadata()` is called with `diff_summary_lines` populated, (5) test asserts diff_summary_lines contains "refactor".

      AI SLOP DETECTED:
      - Monkeypatch stubs LLM to return different outputs based on system prompt string matching ("Diff Summary" in sys). This is fragile; if prompt wording changes, test silently fails.
      - Test does not verify that diff_summary_lines are actually *used* downstream (only that they're passed).
      - No assertion that YAML docstring was also applied; only checks diff_summary_lines.
        deps:
          calls:
            - any
            - append
            - captured.get
            - fake_generate_chat
            - get
            - kwargs.get
            - monkeypatch.setattr
            - monkeypatch.setenv
            - p.write_text
            - process_file
          imports:
            - os
            - pathlib.Path


    why: |
      Tests the integration between docstring generation (YAML) and diff summary generation (separate LLM call). The dual-output design allows agents to see both structured metadata AND human-readable change history.

      Fragility: String-matching on system prompt is brittle. Should mock at function boundary instead (e.g., mock `generate_chat` to return different outputs based on call count or explicit parameter).

    guardrails:
      - DO NOT change system prompt wording without updating string match in fake_generate_chat; test will silently pass with wrong output
      - ALWAYS verify both YAML and diff_summary are applied; current test only checks diff_summary_lines presence
      - NOTE: This test relies on monkeypatch order; if LLM is called >2x, string matching may return wrong output
      - ASK USER: Should diff_summary_lines be validated for content (not just presence)? Currently only checks "refactor" substring exists.

    security:
      no_validation_of_llm_output:
        - Test accepts any LLM output matching string pattern; no schema validation
    I'm ready to generate AgentSpec YAML documentation. However, I don't see any code provided yet for me to audit.

    Please share the code you'd like me to document, and I'll produce a concise, accurate YAML block following the format and guidelines you've outlined.

    **What I need:**
    - The code to audit (function, class, module, or file)
    - Context (language, purpose, production vs. test)
    - Any known issues or concerns (optional)

    Once you provide the code, I'll deliver:
    1. **what**: Concise description + AI slop detection
    2. **why**: Reasoning behind the approach
    3. **guardrails**: Specific, actionable constraints for AI agents
    4. **security**: Vulnerabilities (if 2+ issues exist)

    Ready when you are.
    I'm ready to generate AgentSpec YAML documentation. However, I don't see any code provided yet for me to audit.

    Please share the code you'd like me to document, and I'll produce a concise, accurate YAML block following the format and guidelines you've outlined.

    **What I need:**
    - The code to audit (function, class, module, or file)
    - Context (language, purpose, production vs. test)
    - Any known issues or concerns (optional)

    Once you provide the code, I'll deliver:
    1. **what**: Concise description + AI slop detection
    2. **why**: Reasoning behind the approach
    3. **guardrails**: Specific, actionable constraints for AI agents
    4. **security**: Vulnerabilities (if 2+ issues exist)

    Ready when you are.

        changelog:
          - "- none yet"

    """
    p = tmp_path / "t.py"
    p.write_text("""
def target():
    return 1
""", encoding="utf-8")

    # Stub: LLM generate_chat returns YAML for docstring gen, and distinct text for diff summary
    calls = {"messages": []}

    def fake_generate_chat(**kwargs):
        """
        ```yaml
        ---agentspec
        what: |
          Mock function for testing LLM chat completions. Returns hardcoded AgentSpec YAML.
          Logs all `messages` kwargs to `calls["messages"]` list for assertion.
          If system prompt contains "Diff Summary" or "Summarize Function Diffs", returns marker string.
          Otherwise returns minimal valid YAML block with placeholder content.

          AI SLOP DETECTED:
          - Hardcoded return values mask real LLM behavior; tests pass but won't catch actual failures
          - Placeholder YAML ("ok" values) doesn't validate AgentSpec quality or structure
          - No validation of message format; accepts malformed input silently
            deps:
              calls:
                - append
                - get
                - kwargs.get
              imports:
                - os
                - pathlib.Path


        why: |
          Mock prevents external API calls during unit tests (cost, latency, rate limits).
          However, this implementation is too permissive: it accepts any input and returns valid-looking
          but semantically empty YAML. Tests using this mock will not catch real AgentSpec generation bugs.
          Better approach: validate message structure, return realistic YAML variants, or use snapshot testing.

        guardrails:
          - DO NOT use this mock for integration tests; it hides real LLM failures
          - DO NOT assume "ok" placeholder values are valid AgentSpec; add schema validation
          - ALWAYS inspect `calls["messages"]` in assertions; verify message structure, not just presence
          - NOTE: This mock is too lenient; strengthen it to reject malformed inputs or return error variants


            changelog:
              - "- none yet"
            ---/agentspec
        ```
        """
        calls["messages"].append(kwargs.get("messages"))
        # If system prompt mentions Diff Summary, return a marker
        sys = (kwargs.get("messages") or [{}])[0].get("content", "")
        if "Diff Summary" in sys or "Summarize Function Diffs" in sys:
            return "Diff Summary:\n- changed things"
        # Otherwise return minimal YAML block
        return (
            "---agentspec\n"
            "what: |\n  ok\n\n"
            "why: |\n  ok\n\n"
            "guardrails:\n  - NOTE: ok\n---/agentspec\n"
        )

    monkeypatch.setenv("AGENTSPEC_GENERATE_STUB", "1")
    monkeypatch.setattr("agentspec.llm.generate_chat", lambda *a, **k: fake_generate_chat(**k))

    # Provide fake diffs for the function
    def fake_collect_function_code_diffs(fp, fn, limit=5):
        """
        ```yaml
        ---agentspec
        what: |
          Returns hardcoded list of 5 fake git diffs for testing/demo purposes.
          Ignores all parameters (fp, fn, limit); always returns same mock data.

          AI SLOP DETECTED:
          - Function name suggests real git history collection; actually returns fake data
          - No actual repository access; will mislead agents into thinking git integration works
          - Stub masquerading as feature; blocks real implementation
            deps:
              imports:
                - os
                - pathlib.Path


        why: |
          Likely placeholder for incomplete git integration. Real implementation would:
          - Parse actual git log from repository at path `fp`
          - Filter commits affecting function `fn`
          - Return `limit` most recent diffs

          Current stub prevents agents from understanding actual code history patterns.

        guardrails:
          - DO NOT call this in production; returns fake data, not real git history
          - DO NOT assume return format matches actual git.log output; this is mock-only
          - ALWAYS replace with real git integration before merging to main
          - NOTE: This blocks accurate code auditing; real diffs needed for security review


            changelog:
              - "- none yet"
            ---/agentspec
        ```
        """
        return [{"date": "2025-11-01", "message": "refactor", "hash": "abcd123", "diff": "+ x\n- y"}]

    monkeypatch.setattr("agentspec.collect.collect_function_code_diffs", fake_collect_function_code_diffs)

    captured = {}

    def fake_apply(filepath, lineno, func_name, narrative, metadata, *, as_agentspec_yaml=False, force_context=False, diff_summary_lines=None):
        """
        ```yaml
        ---agentspec
        what: |
          Mock function that captures `diff_summary_lines` parameter and returns True.
          Simulates successful application of a code change without actually modifying files.
          Parameters: filepath, lineno, func_name, narrative, metadata (positional); as_agentspec_yaml, force_context, diff_summary_lines (keyword-only).

          AI SLOP DETECTED:
          - Function is a test stub; does not apply changes to actual files
          - No validation of inputs; accepts any values without checking validity
          - Captured state (`captured["diff_summary_lines"]`) is side effect; tests relying on this are fragile
            deps:
              imports:
                - os
                - pathlib.Path


        why: |
          Used in unit tests to avoid filesystem mutations during test runs.
          Keyword-only parameters (`*,`) enforce explicit argument passing, preventing accidental positional misuse.
          However, this stub provides no feedback on whether the "application" would actually succeed in production.

        guardrails:
          - DO NOT use in production code; this is test-only
          - DO NOT rely on `captured` dict for assertions without resetting between tests; state persists
          - ALWAYS validate that real `apply()` function has same signature before replacing this mock
          - NOTE: This stub always returns True; real implementation may fail; tests may have false positives


            changelog:
              - "- none yet"
            ---/agentspec
        ```
        """
        captured["diff_summary_lines"] = diff_summary_lines
        return True

    monkeypatch.setattr("agentspec.insert_metadata.apply_docstring_with_metadata", fake_apply)

    from agentspec.generate import process_file

    rc = process_file(
        filepath=p,
        dry_run=False,
        force_context=False,
        model="gpt-5-mini",
        as_agentspec_yaml=True,
        base_url="http://localhost:11434/v1",
        provider="openai",
        update_existing=True,
        terse=True,
        diff_summary=True,
    )

    assert captured.get("diff_summary_lines") is not None
    assert any("refactor" in ln for ln in captured["diff_summary_lines"])


