from agentspec import lint, extract
from pathlib import Path

def test_lint_runs():
    result = lint.run("agentspec/")
    assert isinstance(result, int)

def test_extract_runs():
    result = extract.run("agentspec/", "markdown")
    assert isinstance(result, int)
