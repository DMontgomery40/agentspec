from pathlib import Path

from agentspec import collect


def test_collect_metadata_for_javascript_function():
    """
    Smoke test validating that collect.collect_metadata returns calls/imports for JavaScript functions.

    ---agentspec
    what: |
      Ensures the JavaScript metadata pathway dispatches through LanguageRegistry and returns
      deterministic call/import lists for tree-sitter enabled adapters. Uses the
      fixtures/javascript/simple-function.js file and targets the `add` function to verify
      that `console.log` is detected as a call and that changelog fallbacks remain populated.

    deps:
      calls:
        - agentspec.collect.collect_metadata
      called_by: []

    why: |
      Regression coverage for the new JavaScript metadata branch prevents future changes from
      accidentally breaking LanguageRegistry dispatch or emptying the returned structure. The
      test asserts baseline expectations (calls include console.log, imports list exists, changelog
      populated) without over-constraining formatting.

    guardrails:
      - DO NOT hard-code exact changelog contents; git availability varies per environment
      - DO NOT mutate fixture files within this test; they are shared by other suites
      - DO NOT assume additional calls/imports beyond what the adapter currently returns

    changelog:
      - "2025-10-31: Add regression coverage for JavaScript metadata collection"
    ---/agentspec
    """

    fixture = Path(__file__).parent / "fixtures" / "javascript" / "simple-function.js"

    metadata = collect.collect_metadata(fixture, "add")

    assert metadata
    deps = metadata.get("deps", {})
    calls = deps.get("calls", [])
    imports = deps.get("imports", [])

    assert "console.log" in calls
    assert isinstance(imports, list)

    changelog = metadata.get("changelog", [])
    assert isinstance(changelog, list)
    assert changelog  # fallback should still supply at least one entry


