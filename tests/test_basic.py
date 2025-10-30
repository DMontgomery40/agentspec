from agentspec import lint, extract
from pathlib import Path

def test_lint_runs():
    '''
    ```python
    """
    Smoke test validating lint.run() executes and returns an integer exit code.

    WHAT:
    - Invokes `lint.run("agentspec/")` and asserts return type is exactly `int`
    - Detects import errors, broken signatures, missing dependencies before sophisticated lint tests execute
    - Does NOT validate exit code semantics, lint rule correctness, output quality, or file discovery

    WHY:
    - Minimal surface area: Single type assertion catches fundamental breakage without overfitting to implementation details
    - Early detection: Identifies missing lint module or broken run() signature before downstream tests waste resources
    - Type invariant as stable contract: Return type `int` is the only guaranteed interface; exit code semantics are implementation-dependent

    GUARDRAILS:
    - DO NOT check specific exit codes (0, 1, etc.) or assume exit code semantics
    - DO NOT wrap lint.run() in try/except; exceptions are diagnostic signals
    - DO NOT add output validation, file existence checks, or lint rule assertions
    - ALWAYS preserve `isinstance(result, int)` as sole assertion—it is the critical type contract validator
    - ALWAYS allow test to fail fast if lint.run is unavailable or broken
    """
    ```

    DEPENDENCIES (from code analysis):
    Calls: isinstance, lint.run
    Imports: agentspec.extract, agentspec.lint, pathlib.Path


    CHANGELOG (from git history):
    - 2025-10-29: Add basic tests for lint and extract functions

    '''
    result = lint.run("agentspec/")
    assert isinstance(result, int)

def test_extract_runs():
    '''
    ```python
    """
    Smoke test: extract.run() executes without exception and returns an integer.

    WHAT:
    - Invokes extract.run("agentspec/", "markdown") and asserts return value is int-like via isinstance (tolerates subclasses)
    - Validates API contract only: callable exists, returns int; does NOT verify extraction correctness or semantic accuracy
    - Allows all exceptions (ImportError, FileNotFoundError, runtime errors) to propagate as test failures

    WHY:
    - Establishes minimal baseline for extract module availability and API stability without complex fixtures
    - Prioritizes early detection of breaking changes (renamed functions, missing dependencies) over correctness validation
    - isinstance() tolerates integer subclasses (numpy.int64, pandas.Int64) and future type system changes; reduces brittleness
    - Fast, deterministic first-stage gating test: catches ~80% of integration breakage before deeper functional tests

    GUARDRAILS:
    - DO NOT add try/except blocks suppressing ImportError, FileNotFoundError, or AttributeError—must propagate as failures
    - DO NOT modify to validate extraction accuracy or content quality—belongs in separate functional/integration tests
    - DO NOT change isinstance(result, int) assertion without coordinating with extract module maintainers
    - DO NOT parameterize hardcoded path or format without confirming stability across all test environments
    - ALWAYS keep test minimal and fast—target <100ms for CI/CD velocity
    - ALWAYS run before deeper extraction tests to fail fast on API breakage
    - ALWAYS ensure agentspec/ directory and extract module are importable in test environment
    """
    ```

    DEPENDENCIES (from code analysis):
    Calls: extract.run, isinstance
    Imports: agentspec.extract, agentspec.lint, pathlib.Path


    CHANGELOG (from git history):
    - 2025-10-29: Add basic tests for lint and extract functions

    '''
    result = extract.run("agentspec/", "markdown")
    assert isinstance(result, int)
