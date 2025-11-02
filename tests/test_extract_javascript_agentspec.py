from pathlib import Path
from agentspec import extract


def test_extract_from_jsdoc_agentspec_block():
    """
    ```yaml
    ---agentspec
    what: |
      Integration test that validates end-to-end extraction of AgentSpec blocks embedded in JSDoc comments from JavaScript source files.

      Path construction: `fixture = Path(__file__).parent / "fixtures" / "javascript" / "with-agentspec.js"` builds absolute path to test fixture file containing JavaScript code with embedded AgentSpec YAML blocks in JSDoc comments

      Extraction call: `specs = extract.extract_from_js_file(fixture)` invokes the extraction function to parse the fixture file and return a list of AgentSpec specification objects

      Assertion 1 (non-empty result): `assert specs, "Expected at least one spec from JS fixture"` validates that extraction returned a non-empty list, confirming the fixture file was successfully parsed and at least one AgentSpec block was found and extracted

      Assertion 2 (name validation): `assert s.name in {"demo", "(anonymous)"}` validates that the first extracted spec's name matches either "demo" or "(anonymous)". This accepts both variants because JavaScript function naming differs between declared functions (`function demo() {}`) and assigned functions (`const demo = () => {}`), and the extraction logic must handle both patterns correctly

      Assertion 3 (raw block capture): `assert s.raw_block` validates that the raw JSDoc comment text was captured and stored in the spec object, confirming the extraction preserved the original comment source

      Assertion 4 (parsed structure): `assert isinstance(s.parsed_data, dict)` validates that parsed_data is a dictionary (not string or None), and `assert "what" in s.parsed_data` validates that the dictionary contains at least a "what" key, confirming that JSDoc YAML parsing correctly identified and extracted the AgentSpec structured data (not just raw text)

      Test execution flow:
      1. Construct fixture file path
      2. Call extract_from_js_file() to parse fixture
      3. Validate specs list is non-empty
      4. Validate first spec name is "demo" or "(anonymous)"
      5. Validate raw_block field is populated
      6. Validate parsed_data is dict with "what" key

      No AI slop detected. This is a well-structured fixture-based integration test with clear validation stages and appropriate error messages.
        deps:
          calls:
            - Path
            - extract.extract_from_js_file
            - isinstance
          imports:
            - agentspec.extract
            - pathlib.Path


    why: |
      Uses fixture-based testing to validate real-world JavaScript parsing end-to-end without mocking the extraction logic. Fixture files stored in version control provide reproducible test data that can be inspected manually to verify expected format and catch regressions. The multi-stage assertion pattern (existence → name validation → raw block presence → parsed structure) creates a logical validation pipeline that isolates which stage fails if the test breaks, enabling faster debugging. Accepts both "demo" and "(anonymous)" names because JavaScript function naming varies depending on whether the function is declared (`function demo()`) or assigned (`const demo = () => {}`), and production code must handle both patterns. Checking for the "what" key specifically validates that JSDoc YAML parsing correctly identified and extracted structured data, not just raw comment text. This approach catches regressions in the extraction pipeline that unit tests might miss.

    guardrails:
      - DO NOT modify the fixture file path `fixtures/javascript/with-agentspec.js` without updating all test references; the test depends on the exact path to locate test data
      - DO NOT remove any of the four assertions; each validates a different stage of the extraction pipeline (existence, name, raw block, parsed structure) and removing any stage reduces test coverage and makes failures harder to diagnose
      - DO NOT change the assertion error messages; they provide debugging context when tests fail in CI/CD and help developers understand which extraction stage failed
      - DO NOT restrict name validation to a single variant; accepting both "demo" and "(anonymous)" is intentional and reflects real JavaScript parsing behavior where function names depend on declaration style
      - DO NOT modify the fixture file `with-agentspec.js` without re-evaluating all assertions; the test is tightly coupled to fixture content and changes may invalidate expectations
      - ALWAYS run this test after modifying `extract.extract_from_js_file()` to ensure JavaScript JSDoc parsing still works correctly
      - ALWAYS verify the fixture file exists before running tests; missing fixture files cause test failures that are harder to debug than assertion failures
      - ALWAYS ensure the fixture file contains valid AgentSpec YAML blocks in JSDoc comments; malformed YAML will cause parsed_data to be None or incomplete
      - NOTE: This is an integration test, not a unit test; it validates the entire extraction pipeline from file I/O through JSDoc parsing to data structure validation
      - NOTE: The test depends on fixture file stability; if fixture is modified, all assertions must be re-evaluated
      - NOTE: If test fails on name assertion, check if JavaScript function is declared vs assigned in fixture
      - NOTE: If test fails on parsed_data assertion, check if JSDoc YAML is valid and contains "what" key

        changelog:
          - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
        ---/agentspec
    ```
    """
    fixture = Path(__file__).parent / "fixtures" / "javascript" / "with-agentspec.js"
    specs = extract.extract_from_js_file(fixture)
    assert specs, "Expected at least one spec from JS fixture"
    s = specs[0]
    assert s.name in {"demo", "(anonymous)"}
    assert s.raw_block
    assert isinstance(s.parsed_data, dict)
    assert "what" in s.parsed_data

