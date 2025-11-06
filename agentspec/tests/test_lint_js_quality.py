from pathlib import Path
from textwrap import dedent


def test_js_agentspec_lint_flags_nested_deps_and_code_imports(tmp_path: Path):
    js = dedent(
        """
        /**
         * ---agentspec
         * what: |
         *   Dashboard component.
         *   deps:
         *     calls:
         *       - x
         * deps:
         *   calls:
         *     - client.getConfig
         *   imports:
         *     - import { IconButton } from '@mui/material';
         *     - { useState, useEffect }
         * why: |
         *   test
         * guardrails:
         *   - NOTE: ok
         * ---/agentspec
         */
        export function Demo() { return null }
        """
    )
    p = tmp_path / "bad.js"
    p.write_text(js, encoding="utf-8")

    from agentspec.lint import check_js_file
    errors, warnings = check_js_file(p, min_lines=3)
    joined = "\n".join(m for _, m in errors)
    assert "deps" in joined and "nested" in joined or "mapping" in joined
    assert "imports" in joined and "code-like" in joined

