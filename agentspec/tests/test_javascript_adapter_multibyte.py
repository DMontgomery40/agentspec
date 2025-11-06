"""
Multibyte UTF-8 handling tests for JavaScriptAdapter.

---agentspec
what: |
  Verifies that byte offsets from tree-sitter are handled correctly by the
  adapter when extracting function call names in the presence of multibyte
  characters (e.g., emoji) earlier in the file. This prevents slicing the
  decoded Unicode string with byte indices, which produced corrupted names.

deps:
  imports:
    - agentspec.langs.javascript_adapter.JavaScriptAdapter
    - pytest

why: |
  Reproduces the historical bug where start_byte/end_byte offsets were used as
  character indices on the decoded source string. The test places an emoji
  before a call expression and asserts the correct call name is extracted.

guardrails:
  - Keep emoji before the call to ensure start_byte > 0 with multibyte chars
  - Run on environments with tree-sitter available only

changelog:
  - "2025-11-04: Added multibyte slicing test for call name extraction"
---/agentspec
"""

import pytest
from agentspec.langs.javascript_adapter import JavaScriptAdapter


@pytest.mark.skipif(not JavaScriptAdapter()._tree_sitter_available, reason="tree-sitter unavailable")
def test_extract_calls_with_multibyte_emoji():
    adapter = JavaScriptAdapter()
    # Emoji (multibyte) before the call; previously caused misaligned slicing
    src = "const banner = '🙂🙂🙂';\nfunction foo(){return 1;}\n// later\nfoo(42);\n"
    tree = adapter.parse(src)
    calls = adapter._extract_function_calls(tree, src, "foo")
    assert "foo" in calls


