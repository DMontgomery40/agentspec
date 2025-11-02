from pathlib import Path
from agentspec import lint


def test_lint_js_file_with_agentspec_block_passes_minimum():
    fixture = Path(__file__).parent / "fixtures" / "javascript" / "with-agentspec.js"
    errors, warnings = lint.check_js_file(fixture, min_lines=3)
    assert not errors
    assert isinstance(warnings, list)

