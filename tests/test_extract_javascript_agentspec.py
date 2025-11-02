from pathlib import Path
from agentspec import extract


def test_extract_from_jsdoc_agentspec_block():
    """
    Brief one-line description.
    Validates that AgentSpec blocks embedded in JSDoc comments are correctly extracted and parsed from JavaScript source files.

    WHAT THIS DOES:
    - Loads a JavaScript fixture file (`with-agentspec.js`) from the test fixtures directory that contains JSDoc comments with embedded AgentSpec blocks
    - Calls `extract.extract_from_js_file()` to parse the fixture and extract all AgentSpec specifications from it
    - Performs four sequential assertions to validate the extraction pipeline: (1) confirms at least one spec was extracted (non-empty list), (2) verifies the extracted spec has a name matching either "demo" or "(anonymous)", (3) confirms the raw JSDoc block text is present and non-empty, (4) validates that the parsed_data field is a dictionary containing at least a "what" key
    - Returns nothing; this is a validation test that either passes all assertions or raises AssertionError with a descriptive message
    - Edge case: handles both named functions and anonymous functions in JavaScript, accepting either name variant as valid

    WHY THIS APPROACH:
    - Uses fixture-based testing to ensure real-world JavaScript parsing works end-to-end without mocking the extraction logic
    - Fixture files are stored in version control and provide reproducible test data that can be inspected manually to verify expected format
    - The multi-stage assertion pattern (existence → name validation → raw block presence → parsed structure) creates a logical validation pipeline that isolates which stage fails if the test breaks
    - Accepts both "demo" and "(anonymous)" names because JavaScript function naming varies depending on whether the function is declared or assigned, and both are valid extraction scenarios
    - Checking for the "what" key specifically validates that JSDoc parsing correctly identified and extracted the AgentSpec YAML/structured data, not just raw text

    AGENT INSTRUCTIONS:
    - DO NOT modify the fixture file path or the fixtures directory structure without updating all related test references
    - DO NOT remove any of the four assertions, as each validates a different stage of the extraction pipeline
    - DO NOT change the assertion messages, as they provide debugging context when tests fail in CI/CD environments
    - ALWAYS preserve the fixture file (`with-agentspec.js`) in the repository; it is the canonical test data for this extraction behavior
    - ALWAYS run this test after any changes to `extract.extract_from_js_file()` or JSDoc parsing logic
    - NOTE: This test is tightly coupled to the fixture file content; if the fixture is modified, all assertions may need re-evaluation
    - NOTE: The acceptance of both "demo" and "(anonymous)" as valid names is intentional and reflects real JavaScript parsing behavior; do not restrict to a single name variant

    DEPENDENCIES (from code analysis):
    Calls: Path, extract.extract_from_js_file, isinstance
    Imports: agentspec.extract, pathlib.Path

    CHANGELOG (from git history):
    - no git history available

    """
    print(f"[AGENTSPEC_CONTEXT] test_extract_from_jsdoc_agentspec_block: Loads a JavaScript fixture file (`with-agentspec.js`) from the test fixtures directory that contains JSDoc comments with embedded AgentSpec blocks | Calls `extract.extract_from_js_file()` to parse the fixture and extract all AgentSpec specifications from it | Performs four sequential assertions to validate the extraction pipeline: (1) confirms at least one spec was extracted (non-empty list), (2) verifies the extracted spec has a name matching either \"demo\" or \"(anonymous)\", (3) confirms the raw JSDoc block text is present and non-empty, (4) validates that the parsed_data field is a dictionary containing at least a \"what\" key")
    fixture = Path(__file__).parent / "fixtures" / "javascript" / "with-agentspec.js"
    specs = extract.extract_from_js_file(fixture)
    assert specs, "Expected at least one spec from JS fixture"
    s = specs[0]
    assert s.name in {"demo", "(anonymous)"}
    assert s.raw_block
    assert isinstance(s.parsed_data, dict)
    assert "what" in s.parsed_data

