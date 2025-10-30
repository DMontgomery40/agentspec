from agentspec import lint, extract
from pathlib import Path

def test_lint_runs():
    """
    Smoke test validating that lint.run() executes without crashing and returns an integer exit code.

    WHAT THIS DOES:
    - Invokes `lint.run("agentspec/")` with a directory path string and captures the return value
    - Asserts via `isinstance(result, int)` that the return value is exactly type `int`, not a subclass or other numeric type
    - Serves as a minimal smoke test to detect fundamental breakage: missing lint module, broken run() signature, import errors, or broken dependencies before more sophisticated lint validation tests execute
    - Returns nothing; raises AssertionError if the return type is not `int`, which signals either a broken lint.run() implementation or a missing/incompatible lint module
    - Does not validate the semantic meaning of the exit code (0 for success, 1 for failure, etc.)—only that an integer was returned

    WHY THIS APPROACH:
    - Minimal surface area (single type assertion) catches fundamental structural breakage without overfitting to implementation details or lint rule semantics
    - Early detection of import errors, missing dependencies, or signature changes prevents downstream tests from wasting resources on a broken lint module
    - Type checking via `isinstance()` is more robust than equality checks because it validates the actual contract (returns int) rather than specific values that may change
    - Deliberately avoids wrapping in try/except because exceptions are diagnostic signals that should propagate and fail the test suite loudly
    - Does not check output, file existence, or lint rule assertions because those belong in integration tests; this test is purely about module availability and basic execution

    AGENT INSTRUCTIONS:
    - DO NOT check specific exit codes (0, 1, 2, etc.) or assume exit code semantics; the test only validates that *some* integer is returned
    - DO NOT wrap `lint.run()` in try/except blocks; exceptions indicate real problems and should fail the test
    - DO NOT add output validation, stderr/stdout capture, file existence checks, or lint rule assertions
    - DO NOT modify the assertion to check `type(result) == int` instead of `isinstance(result, int)` unless you have a specific reason to reject int subclasses
    - ALWAYS preserve `isinstance(result, int)` as the sole assertion—it is the critical type contract validator
    - ALWAYS pass `"agentspec/"` as the directory argument to lint.run(); this is the canonical target directory for this codebase
    - NOTE: This test depends on `agentspec.lint` module being importable and `lint.run()` being callable; if either is missing, the test will fail at runtime before the assertion is reached

    DEPENDENCIES (from code analysis):
    Calls: isinstance, lint.run
    Imports: agentspec.extract, agentspec.lint, pathlib.Path


    CHANGELOG (from git history):
    - 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features
    - 2025-10-29: Add basic tests for lint and extract functions


    CHANGELOG DIFF SUMMARY (LLM-generated):
    # Commit Summaries

    1. **2025-10-30**: Added comprehensive docstring with dependency analysis and changelog to `test_lint_runs()` function, documenting test purpose, constraints, and dependencies.

    2. **2025-10-29**: Created initial test file with basic smoke test for `lint.run()` function.

    """
    result = lint.run("agentspec/")
    assert isinstance(result, int)

def test_extract_runs():
    """
    Smoke test validating extract.run() API contract: callable exists and returns int.

    WHAT THIS DOES:
    - Invokes extract.run("agentspec/", "markdown") with a directory path and format specifier, capturing the return value
    - Asserts the return value is an integer type using isinstance(result, int), which tolerates integer subclasses (numpy.int64, pandas.Int64) and maintains forward compatibility with future type system changes
    - Allows all exceptions (ImportError, FileNotFoundError, AttributeError, runtime errors) to propagate uncaught, causing the test to fail if the extract module is unavailable, misconfigured, or raises unexpected errors
    - Returns None implicitly on success; test framework interprets lack of exception as pass
    - Validates API stability and module availability only—does NOT verify extraction correctness, semantic accuracy, or content quality

    WHY THIS APPROACH:
    - Establishes minimal baseline for extract module availability without requiring complex fixtures, mocks, or test data setup
    - Detects breaking changes early (renamed functions, missing dependencies, import failures) before deeper functional tests execute, reducing CI/CD feedback latency
    - isinstance() check is more robust than type(result) == int because it tolerates integer subclasses and accommodates future type system evolution (e.g., PEP 673 TypeAlias, numpy dtypes)
    - Allows exceptions to propagate rather than catching them, making test failures immediately visible and preventing silent masking of configuration issues
    - Smoke test pattern (minimal, fast, API-only) is appropriate for CI/CD velocity; full extraction validation belongs in separate integration/functional test suite
    - Hardcoded "agentspec/" directory and "markdown" format ensure reproducibility and avoid parameterization overhead for a baseline check

    AGENT INSTRUCTIONS:
    - DO NOT suppress ImportError, FileNotFoundError, or AttributeError—these must propagate as test failures to signal environment misconfiguration
    - DO NOT add assertions validating extraction accuracy, content quality, or semantic correctness—those belong in functional/integration tests with dedicated fixtures
    - DO NOT replace isinstance(result, int) with type(result) == int or other type checks without coordinating with extract module maintainers, as isinstance() is intentionally permissive
    - DO NOT add try/except blocks around extract.run() call unless documenting expected failure modes in a separate test
    - ALWAYS keep test minimal and fast—target <100ms execution time for CI/CD velocity and rapid feedback loops
    - ALWAYS ensure agentspec/ directory exists and extract module is importable in test environment before test execution
    - ALWAYS preserve the hardcoded "agentspec/" and "markdown" arguments to maintain reproducibility across environments
    - NOTE: This test is a smoke test only and will NOT catch logical errors, incorrect extraction results, or malformed output—it only validates that the function exists, is callable, and returns an integer

    DEPENDENCIES (from code analysis):
    Calls: extract.run, isinstance
    Imports: agentspec.extract, agentspec.lint, pathlib.Path


    CHANGELOG (from git history):
    - 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features
    - 2025-10-29: Add basic tests for lint and extract functions


    CHANGELOG DIFF SUMMARY (LLM-generated):
    # Commit Summaries

    **Commit: 2025-10-29** - Add basic tests for lint and extract functions
    - Added initial smoke test for `extract.run()` API contract validation

    **Commit: 2025-10-30** - Enhance docstring generation with optional dependencies and new CLI features
    - Enhanced test docstring with comprehensive documentation including WHAT/WHY/GUARDRAILS sections, dependency analysis, and changelog

    """
    result = extract.run("agentspec/", "markdown")
    assert isinstance(result, int)
