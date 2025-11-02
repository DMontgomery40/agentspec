import os
from pathlib import Path

from agentspec import generate


FIXTURES = Path("tests/fixtures/javascript")


def _copy_fixture(tmp_path: Path, name: str) -> Path:
    src = FIXTURES / name
    dst = tmp_path / name
    dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    return dst


def test_js_two_phase_insert_and_metadata(tmp_path, monkeypatch):
    monkeypatch.setenv("AGENTSPEC_GENERATE_STUB", "1")
    # work on a temp copy
    target = _copy_fixture(tmp_path, "simple-function.js")
    # run generate (JS path), update existing to force write
    rc = generate.run(str(target), language="js", dry_run=False, update_existing=True)
    assert rc == 0
    text = target.read_text(encoding="utf-8")
    # JSDoc present and deterministic metadata injected
    assert "/**" in text and "*/" in text
    assert "DEPENDENCIES (from code analysis):" in text
    assert "CHANGELOG (from git history):" in text

    # Run again to ensure replace (not append)
    rc = generate.run(str(target), language="js", dry_run=False, update_existing=True)
    assert rc == 0
    text2 = target.read_text(encoding="utf-8")
    # Should have metadata for both functions (add and multiply), no duplicates
    assert text2.count("DEPENDENCIES (from code analysis):") == 2


def test_js_strip_then_generate_idempotent(tmp_path, monkeypatch):
    monkeypatch.setenv("AGENTSPEC_GENERATE_STUB", "1")
    target = _copy_fixture(tmp_path, "imports-exports.js")
    # Pre-clean old blocks if any, then generate
    rc = generate.run(str(target), language="js", dry_run=False, update_existing=True)
    assert rc == 0
    text = target.read_text(encoding="utf-8")
    # Metadata injected only once
    assert text.count("DEPENDENCIES (from code analysis):") == 1

