I need you to help create examples to be appended to your system prompt. I will give you an example of exactly what these "examples" need to be formatted as:

```json
{
  "version": "1.0",
  "last_updated": "2025-11-02",
  "examples": [
    {
      "id": "weak_test_assertion_jsdoc_extract",
      "type": "negative_then_positive",
      "language": "python",
      "code": "assert \"what\" in s.parsed_data",
      "code_context": {
        "file": "tests/test_extract_javascript_agentspec.py",
        "function": "test_extract_from_jsdoc_agentspec_block",
        "subject_function": "agentspec.extract.extract_from_js_file"
      },
      "bad_documentation": {
        "what": "Assertion confirms that JSDoc parsing correctly identified and extracted the AgentSpec YAML/structured data (not just raw text)",
        "why_bad": "Claims validation that doesn't happen - assertion only checks for the presence of the 'what' key; it does not evaluate content quality"
      },
      "good_documentation": {
        "what": "Checks presence of the 'what' key in parsed_data dict. WARNING: This does not validate agentspec content quality; any YAML with a 'what' key will pass.",
        "why": "This integration test ensures the extraction pipeline returns a dict with expected keys from JSDoc agentspec blocks. It is not intended to validate semantic quality of the YAML, only that extraction produced a minimally structured result.",
        "guardrails": [
          "ASK USER: Before editing extract_from_js_file or this test, confirm whether the intent is to validate content quality or only the existence of a 'what' key",
          "DO NOT conflate key-existence checks with content validation; keep separate tests for semantics vs structure",
          "NOTE: Strengthen tests elsewhere to validate YAML quality if required"
        ]
      },
      "lesson": "Do not infer semantic validation from key-existence assertions; document the actual check and add an ASK USER guardrail for ambiguous intent."
    }
  ]
}
```

NOW, I'm going to give you CODE and a CRITIQUE. You will return the dataset formatted JSON, exactly in the same format shown above.

## CRITICAL: Understanding the Format

**"bad_documentation"** = What a LAZY/WRONG agent would write (vague, overclaims, misleading)
- Example from above: "Assertion confirms JSDoc parsing correctly identified and extracted the AgentSpec YAML/structured data"
- This SOUNDS good but actually overclaims what the code does

**"good_documentation"** = What the documentation SHOULD actually say (accurate, warnings, guardrails)
- Example from above: "Checks presence of the 'what' key in parsed_data dict. WARNING: This does not validate agentspec content quality..."
- This is ACCURATE about what the code actually does

**Your job:** Show what BAD documentation would claim vs what GOOD documentation should accurately say about the code.

