#!/usr/bin/env python3
"""
agentspec.lint
--------------------------------
Lints Python files for presence and completeness of structured agent spec blocks.
Now with YAML validation and verbose comment requirements.
"""

import ast
import sys
import yaml
from pathlib import Path
from agentspec.utils import collect_python_files
from typing import List, Tuple, Dict, Any


REQUIRED_KEYS = ["what", "deps", "why", "guardrails"]
RECOMMENDED_KEYS = ["changelog", "testing", "performance"]


class AgentSpecLinter(ast.NodeVisitor):
    def __init__(self, filepath: str, min_lines: int = 10):
        """
        ---agentspec
        what: |
          Initializes a linter instance by storing the target filepath and establishing validation thresholds.

          Inputs:
          - filepath (str): Path to the file to be linted; stored as-is without normalization or validation
          - min_lines (int, default=10): Minimum line count threshold used by downstream validation logic

          Outputs:
          - Initializes instance state with four attributes:
            - self.filepath: The provided filepath string
            - self.errors: Empty list of (line_number, message) tuples for storing linting errors
            - self.warnings: Empty list of (line_number, message) tuples for storing linting warnings
            - self.min_lines: The minimum line threshold value

          Behavior:
          - Performs no file I/O or filesystem operations; purely prepares linter state for lazy evaluation
          - Error and warning lists are initialized as empty to prevent AttributeError during append operations in downstream methods
          - Tuple structure (line_number, message) is established at initialization and must be preserved throughout the linter's lifetime

          Edge cases:
          - No validation of filepath existence or readability occurs; invalid paths are accepted and will fail only when actual linting methods attempt file access
          - min_lines can be set to zero or negative values; validation of this parameter is deferred to downstream comparison logic
            deps:
              imports:
                - agentspec.utils.collect_python_files
                - ast
                - pathlib.Path
                - sys
                - typing.Any
                - typing.Dict
                - typing.List
                - typing.Tuple
                - yaml


        why: |
          Deferred file I/O enables efficient initialization without blocking on filesystem access, allowing linter instances to be created and configured before actual linting begins.

          Empty list initialization for errors and warnings prevents AttributeError exceptions when downstream methods append tuples, eliminating the need for existence checks before each append operation.

          Storing filepath and min_lines as instance variables eliminates the need to pass these parameters repeatedly through method calls, reducing function signatures and improving code maintainability.

          Preserving filepath as a raw string without normalization keeps initialization lightweight and defers path resolution logic to methods that actually need it, following the principle of lazy evaluation.

        guardrails:
          - DO NOT initialize self.errors or self.warnings to None; keep as empty lists to prevent AttributeError when downstream code appends tuples
          - DO NOT change min_lines type from int without updating all downstream comparison operations that depend on numeric ordering
          - ALWAYS preserve filepath as string type without normalization or Path object conversion at this stage; normalization belongs in methods that consume the path
          - ALWAYS maintain (line_number, message) tuple ordering in errors and warnings lists; downstream code and external consumers depend on this consistent structure
          - DO NOT perform file existence checks or I/O operations in __init__; keep initialization pure and defer validation to linting methods

            changelog:
              - "- no git history available"
            ---/agentspec
        """
        self.filepath = filepath
        self.errors: List[Tuple[int, str]] = []
        self.warnings: List[Tuple[int, str]] = []
        self.min_lines = min_lines

    def visit_FunctionDef(self, node):
        """
        ---agentspec
        what: |
          Validates function definition docstrings and traverses child AST nodes.

          This visitor method is invoked by the ast.NodeVisitor framework when encountering a FunctionDef node during AST traversal. It performs two sequential operations:

          1. Docstring Validation: Calls _check_docstring(node) to inspect the function node and verify that required documentation is present and conforms to linting rules.
          2. Child Node Traversal: Calls generic_visit(node) to recursively visit all child nodes within the function definition, ensuring nested functions, class definitions, and other child structures are also validated.

          Inputs: node (ast.FunctionDef) - an AST node representing a function definition
          Outputs: None (side effects include validation checks and recursive traversal)

          Edge cases:
          - Nested function definitions are validated with the same rules as top-level functions
          - Functions with no docstring will trigger validation failure via _check_docstring()
          - Decorated functions are processed identically to undecorated ones
          - Lambda functions are not visited by this method (they use visit_Lambda if implemented)
            deps:
              calls:
                - self._check_docstring
                - self.generic_visit
              imports:
                - agentspec.utils.collect_python_files
                - ast
                - pathlib.Path
                - sys
                - typing.Any
                - typing.Dict
                - typing.List
                - typing.Tuple
                - yaml


        why: |
          The visitor pattern (ast.NodeVisitor) provides a clean, extensible mechanism for applying uniform linting rules across an entire AST. By implementing visit_FunctionDef, the linter automatically processes every function definition encountered during tree traversal without manual iteration.

          Separating docstring validation (_check_docstring) from traversal (generic_visit) maintains single responsibility: validation logic is isolated in _check_docstring, while this method orchestrates the visitation strategy.

          Recursive traversal via generic_visit ensures that nested functions and all descendant nodes are validated, preventing gaps in documentation coverage. This is critical for enforcing consistent standards across codebases with complex nesting.

        guardrails:
          - DO NOT omit the generic_visit(node) call; without it, child nodes will not be visited and nested function definitions will bypass validation entirely
          - DO NOT modify the method signature; ast.NodeVisitor requires the exact name visit_FunctionDef and the single node parameter for the framework to dispatch correctly
          - DO NOT skip _check_docstring(node); this is the enforcement point for documentation requirements and omitting it defeats the linting purpose
          - DO NOT assume all child nodes are functions; generic_visit handles all node types, including nested classes and other definitions
          - DO NOT catch or suppress exceptions from _check_docstring() unless explicitly designed to collect multiple errors; premature exception handling may hide validation failures

            changelog:
              - "- no git history available"
            ---/agentspec
        """
        self._check_docstring(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """
        ---agentspec
        what: |
          Validates async function definitions for required docstrings during AST traversal.

          Behavior:
          - Receives an AsyncFunctionDef node from the AST visitor pattern
          - Invokes _check_docstring(node) to validate docstring presence on the async function
          - Calls generic_visit(node) to recursively traverse and validate all child nodes
          - Ensures both the async function itself and any nested definitions are checked

          Inputs:
          - node: ast.AsyncFunctionDef object representing an async function definition

          Outputs:
          - None (side effect: records linting errors via _check_docstring if docstring missing)

          Edge cases:
          - Async functions without docstrings trigger validation errors
          - Nested async functions or inner definitions are validated recursively
          - Decorated async functions are still subject to docstring requirements
            deps:
              calls:
                - self._check_docstring
                - self.generic_visit
              imports:
                - agentspec.utils.collect_python_files
                - ast
                - pathlib.Path
                - sys
                - typing.Any
                - typing.Dict
                - typing.List
                - typing.Tuple
                - yaml


        why: |
          Enforces consistent documentation standards across both synchronous and asynchronous function definitions.
          The visitor pattern enables automatic AST traversal during the linting workflow without manual recursion.
          Checking the parent node before traversing children ensures validation occurs in logical order (parent before descendants).
          Async functions require the same documentation rigor as sync functions to maintain codebase consistency.

        guardrails:
          - DO NOT omit the generic_visit() call; it breaks recursive traversal of child nodes and leaves nested definitions unvalidated
          - DO NOT call generic_visit() before _check_docstring(); parent validation must occur before child traversal to maintain logical ordering
          - DO NOT assume async functions are exempt from docstring requirements; they must meet the same standards as sync functions

            changelog:
              - "- no git history available"
            ---/agentspec
        """
        self._check_docstring(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """
        ---agentspec
        what: |
          Validates class docstring compliance and recursively processes all child nodes within a class definition.

          Inputs:
          - node: An ast.ClassDef node representing a class definition in the AST

          Behavior:
          - Calls _check_docstring(node) to validate that the class has a compliant docstring according to project standards
          - Calls self.generic_visit(node) to recursively traverse and visit all child nodes (methods, nested classes, attributes)
          - Processes parent node validation before children to establish proper error context and reporting order

          Outputs:
          - No direct return value; side effects include docstring validation errors recorded in internal state and recursive visitation of child nodes

          Edge cases:
          - Classes with no docstring will be flagged by _check_docstring()
          - Nested classes are recursively validated with the same rules
          - Child methods within the class are visited and validated by their own visit_FunctionDef handler
        what_else: |
          This method is part of an AST visitor pattern implementation that enforces documentation standards across a Python codebase. It integrates into a larger linting workflow that traverses entire module ASTs to validate docstring presence and format compliance.
            deps:
              calls:
                - self._check_docstring
                - self.generic_visit
              imports:
                - agentspec.utils.collect_python_files
                - ast
                - pathlib.Path
                - sys
                - typing.Any
                - typing.Dict
                - typing.List
                - typing.Tuple
                - yaml


        why: |
          The visitor pattern (ast.NodeVisitor) provides a standard, maintainable mechanism for AST traversal with automatic node-type dispatch via method naming convention (visit_[NodeType]). By validating the parent class docstring before recursing into children, the validator establishes clear error context and ensures that documentation requirements are checked top-down through the class hierarchy. This ordering also allows parent-level validation errors to be reported before child-level errors, improving readability of lint output.

        guardrails:
          - DO NOT remove the generic_visit() call; it is essential for recursive traversal of all child nodes (methods, nested classes, attributes) and omitting it will cause child nodes to be silently skipped during validation
          - DO NOT rename this method; ast.NodeVisitor uses reflection to dispatch to visit_[NodeType] methods by name, and renaming breaks the automatic dispatch mechanism
          - DO NOT call _check_docstring() after generic_visit(); always validate the parent node before recursing into children to maintain proper error reporting order and context
          - DO NOT modify the method signature; it must accept exactly one parameter (node) to conform to the ast.NodeVisitor interface contract

            changelog:
              - "- no git history available"
            ---/agentspec
        """
        self._check_docstring(node)
        self.generic_visit(node)

    def _check_docstring(self, node):
        """
        ---agentspec
        what: |
          Validates that function and class nodes contain properly formatted agentspec YAML docstring blocks with required and recommended metadata fields. The method extracts the docstring, locates the "---agentspec"/"---/agentspec" fenced block, parses its YAML content, and enforces structural constraints: REQUIRED_KEYS presence, RECOMMENDED_KEYS presence (warnings), 'what' field minimum character length (50+), 'deps' as dict structure, and 'guardrails' as non-empty list. Returns early on critical failures (missing docstring, missing fenced block, invalid YAML, non-dict YAML root) to prevent cascading validation errors. Appends validation results as (lineno, message) tuples to self.errors (critical issues prefixed with ❌) or self.warnings (advisory issues prefixed with ⚠️).
            deps:
              calls:
                - ast.get_docstring
                - doc.find
                - errors.append
                - fenced.split
                - isinstance
                - join
                - l.strip
                - len
                - str
                - strip
                - warnings.append
                - yaml.safe_load
              imports:
                - agentspec.utils.collect_python_files
                - ast
                - pathlib.Path
                - sys
                - typing.Any
                - typing.Dict
                - typing.List
                - typing.Tuple
                - yaml


        why: |
          Fenced YAML blocks balance human-readable docstring formatting with machine-parseable structured metadata for AI agent consumption. Using yaml.safe_load() prevents code injection vulnerabilities and handles YAML edge cases more robustly than manual string parsing. Early returns on critical failures prevent AttributeErrors when accessing dict keys and eliminate nonsensical cascading error messages that confuse developers. Separating errors from warnings enables configurable strictness policies across different CI/CD environments (e.g., fail on errors, warn on missing recommendations). Numeric thresholds (character counts, line counts) provide objective, configurable validation criteria rather than subjective heuristics.

        guardrails:
          - DO NOT modify the "---agentspec" and "---/agentspec" fenced block delimiters without coordinating updates across all code that generates or parses agentspec docstrings, as this will break round-trip consistency.
          - DO NOT remove early returns on critical failures (missing docstring, missing block, invalid YAML, non-dict root); they prevent AttributeErrors and cascading error messages that obscure root causes.
          - DO NOT use yaml.load() instead of yaml.safe_load(); arbitrary code execution vulnerability when parsing untrusted docstrings.
          - DO NOT access spec_data dict attributes without isinstance() type checks first; YAML parsing may produce unexpected types (None, list, scalar) if input is malformed.
          - ALWAYS preserve the (lineno, message) tuple format when appending to self.errors and self.warnings; downstream code depends on this structure for sorting and reporting.
          - ALWAYS include the emoji prefix (❌ for errors, ⚠️ for warnings) in error/warning messages for visual distinction in linter output.
          - DO NOT treat missing recommended keys as errors; they should only generate warnings to allow gradual adoption of new metadata fields.

            changelog:
              - "- no git history available"
            ---/agentspec
        """
        doc = ast.get_docstring(node)
        if not doc:
            self.errors.append((node.lineno, f"❌ {node.name} missing docstring"))
            return

        # Check for agentspec block
        if "---agentspec" not in doc or "---/agentspec" not in doc:
            self.errors.append((node.lineno, f"❌ {node.name} missing agentspec fenced block"))
            return

        # Extract fenced section
        start = doc.find("---agentspec") + len("---agentspec")
        end = doc.find("---/agentspec")
        fenced = doc[start:end].strip()

        # Check minimum verbosity (line count)
        fenced_lines = [l for l in fenced.split('\n') if l.strip()]
        if len(fenced_lines) < self.min_lines:
            self.warnings.append(
                (node.lineno, f"⚠️  {node.name} agentspec too short "
                 f"({len(fenced_lines)} lines, recommend {self.min_lines}+)")
            )

        # Try to parse as YAML
        try:
            spec_data = yaml.safe_load(fenced)
            if not isinstance(spec_data, dict):
                self.errors.append(
                    (node.lineno, f"❌ {node.name} agentspec is not valid YAML dict")
                )
                return
        except yaml.YAMLError as e:
            self.errors.append(
                (node.lineno, f"❌ {node.name} agentspec has invalid YAML: {e}")
            )
            return

        # Check required keys
        missing = [k for k in REQUIRED_KEYS if k not in spec_data]
        if missing:
            self.errors.append(
                (node.lineno, f"❌ {node.name} missing required keys: {', '.join(missing)}")
            )

        # Check recommended keys (warnings only)
        missing_recommended = [k for k in RECOMMENDED_KEYS if k not in spec_data]
        if missing_recommended:
            self.warnings.append(
                (node.lineno, f"⚠️  {node.name} missing recommended keys: "
                 f"{', '.join(missing_recommended)}")
            )

        # Validate 'what' field verbosity
        if 'what' in spec_data:
            what_text = str(spec_data['what']).strip()
            if len(what_text) < 50:
                self.warnings.append(
                    (node.lineno, f"⚠️  {node.name} 'what' field too brief "
                     f"({len(what_text)} chars, recommend 50+)")
                )

        # Validate deps structure
        if 'deps' in spec_data:
            if not isinstance(spec_data['deps'], dict):
                self.warnings.append(
                    (node.lineno, f"⚠️  {node.name} 'deps' should be a dict with "
                     "'calls', 'called_by', etc.")
                )

        # Validate guardrails is a list
        if 'guardrails' in spec_data:
            if not isinstance(spec_data['guardrails'], list):
                self.errors.append(
                    (node.lineno, f"❌ {node.name} 'guardrails' must be a list")
                )
            elif len(spec_data['guardrails']) == 0:
                self.warnings.append(
                    (node.lineno, f"⚠️  {node.name} has empty 'guardrails' list")
                )

    def check(self) -> Tuple[List[Tuple[int, str]], List[Tuple[int, str]]]:
        '''
        ---agentspec
        what: |
          Returns a tuple containing two lists of accumulated linting results from the checker instance.
          The first list contains errors as Tuple[int, str] pairs (line number and error message).
          The second list contains warnings as Tuple[int, str] pairs (line number and warning message).
          This method provides direct access to internal state without filtering, sorting, or transformation.
          Line numbers are integers (0 if unavailable), and messages are string descriptions of the linting issue.
          The method returns references to the internal lists, not copies, making it a lightweight accessor.
            deps:
              imports:
                - agentspec.utils.collect_python_files
                - ast
                - pathlib.Path
                - sys
                - typing.Any
                - typing.Dict
                - typing.List
                - typing.Tuple
                - yaml


        why: |
          The simple getter pattern avoids unnecessary copying overhead when callers need to inspect accumulated linting results.
          Returning a tuple with fixed (errors, warnings) order provides type safety and semantic clarity about which list contains which category of issues.
          Direct reference returns are appropriate here since the caller receives the authoritative state of the linter at the moment of the call.
          This design supports efficient batch retrieval of all linting diagnostics without intermediate transformations.

        guardrails:
          - DO NOT add filtering, sorting, or transformation logic to the returned lists
          - DO NOT change the return type from Tuple[List[Tuple[int, str]], List[Tuple[int, str]]]
          - ALWAYS preserve the (errors, warnings) order in the returned tuple
          - ALWAYS return direct references to self.errors and self.warnings without copying
          - DO NOT modify the structure or content of error/warning tuples before returning

            changelog:
              - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate"
              - "-    """Check a single Python file for compliance.""""
              - "- 2025-10-29: Enhanced lint.py with YAML validation and verbose checks"
              - "-        checker = AgentSpecLinter(str(filepath))"
              - "-        return [(e.lineno or 0, f"Syntax error: {e}")]"
              - "-        return [(0, f"Error parsing {filepath}: {e}")]"
              - "-    """Main lint runner for CLI.""""
              - "- 2025-10-29: Add agent spec linter for Python files"
            ---/agentspec
        '''
        return self.errors, self.warnings


def check_file(filepath: Path, min_lines: int = 10) -> Tuple[List[Tuple[int, str]], List[Tuple[int, str]]]:
    '''
    ---agentspec
    what: |
      Validates a single Python file for AgentSpec compliance by parsing its AST and running a linter visitor.

      Inputs:
      - filepath: Path object pointing to a Python file to validate
      - min_lines: integer threshold (default 10) for minimum acceptable docstring/block length; passed to AgentSpecLinter for strictness control

      Outputs:
      - Returns Tuple[List[Tuple[int, str]], List[Tuple[int, str]]] where:
        - First list contains violations (line_number, error_message pairs)
        - Second list contains warnings (line_number, warning_message pairs)

      Behavior:
      - Reads file with UTF-8 encoding to ensure cross-platform consistency
      - Parses source to AST using ast.parse with filename context
      - Instantiates AgentSpecLinter visitor with filepath and min_lines parameter
      - Visits AST tree to collect compliance issues
      - Calls checker.check() to finalize and unpack violations/warnings lists

      Error handling:
      - SyntaxError: caught separately, preserves line number (or 0 if unavailable), returns as violation with "Syntax error:" prefix
      - All other exceptions: caught broadly, reported as line 0 error with "Error parsing {filepath}:" prefix, returns empty warnings list
      - Ensures function never raises; always returns valid tuple structure
        deps:
          calls:
            - AgentSpecLinter
            - ast.parse
            - checker.check
            - checker.visit
            - filepath.read_text
            - str
          imports:
            - agentspec.utils.collect_python_files
            - ast
            - pathlib.Path
            - sys
            - typing.Any
            - typing.Dict
            - typing.List
            - typing.Tuple
            - yaml


    why: |
      AST parsing provides accurate Python structure detection compared to fragile regex-based approaches, enabling reliable identification of docstrings, function signatures, and code blocks.

      Visitor pattern (AgentSpecLinter) allows modular, extensible rule checking without modifying this function's core logic; new compliance rules can be added to the visitor without touching check_file.

      Separate violations/warnings lists enable downstream callers to apply different severity handling—violations may fail CI/CD while warnings only log.

      Broad exception handling ensures robustness on malformed or edge-case files instead of crashing the entire linting process; line 0 errors signal parse-time failures distinct from content violations.

      min_lines parameter exposed as function argument allows external control over strictness without hardcoding thresholds.

    guardrails:
      - DO NOT remove encoding="utf-8" from read_text(); ensures consistent behavior across Windows, macOS, and Linux
      - DO NOT change return type signature; downstream code (CLI, CI integrations) depends on Tuple[List[Tuple[int, str]], List[Tuple[int, str]]]
      - DO NOT skip checker.check() unpacking; may perform critical post-processing, aggregation, or filtering of collected violations/warnings
      - ALWAYS pass min_lines through to AgentSpecLinter constructor; omitting it removes external strictness control
      - ALWAYS preserve str(filepath) conversion for Path object compatibility with AgentSpecLinter and error messages
      - DO NOT catch SyntaxError in the broad Exception handler; must preserve line number context from SyntaxError.lineno

        changelog:
          - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate"
          - "-    """Check a single Python file for compliance.""""
          - "- 2025-10-29: Enhanced lint.py with YAML validation and verbose checks"
          - "-        checker = AgentSpecLinter(str(filepath))"
          - "-        return [(e.lineno or 0, f"Syntax error: {e}")]"
          - "-        return [(0, f"Error parsing {filepath}: {e}")]"
          - "-    """Main lint runner for CLI.""""
          - "- 2025-10-29: Add agent spec linter for Python files"
        ---/agentspec
    '''
    try:
        src = filepath.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(filepath))
        checker = AgentSpecLinter(str(filepath), min_lines=min_lines)
        checker.visit(tree)
        return checker.check()
    except SyntaxError as e:
        return [(e.lineno or 0, f"Syntax error: {e}")], []
    except Exception as e:
        return [(0, f"Error parsing {filepath}: {e}")], []


def run(target: str, min_lines: int = 10, strict: bool = False) -> int:
    '''
    ---agentspec
    what: |
      Executes batch linting validation on Python files within a target directory to verify agentspec block compliance. Collects all Python files from the target path (file or directory), invokes check_file on each to validate agentspec requirements, and aggregates error and warning counts. Returns exit code 0 on success (no errors, and either no warnings or strict mode disabled), or exit code 1 on failure (errors present, or warnings present in strict mode). Prints per-file diagnostics with line numbers and messages, followed by a summary line showing total files checked and issue counts. Edge case: empty directory returns 0 with zero files checked and no output per file.
        deps:
          calls:
            - Path
            - check_file
            - collect_python_files
            - len
            - print
          imports:
            - agentspec.utils.collect_python_files
            - ast
            - pathlib.Path
            - sys
            - typing.Any
            - typing.Dict
            - typing.List
            - typing.Tuple
            - yaml


    why: |
      Provides a CLI-friendly batch validation entry point for enforcing agentspec compliance across entire codebases. Separates errors (blocking issues) from warnings (advisory issues) to allow flexible enforcement policies. Strict mode enables CI/CD pipelines to enforce zero-warning policies by treating warnings as failures, while permissive mode allows warnings to pass. Summary statistics printed before exit code ensure visibility into validation scope and results.

    guardrails:
      - DO NOT return 0 when strict=True and total_warnings > 0; strict mode must treat warnings as blocking failures to enforce zero-warning policies in CI/CD
      - DO NOT skip summary statistics output; always print the separator line and final status message to ensure visibility of validation results
      - DO NOT modify or filter files during linting; only validate and report, preserving immutability of the target codebase
      - DO NOT assume target path exists; rely on Path and collect_python_files to handle missing paths gracefully

        changelog:
          - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate"
          - "-    files = [path] if path.is_file() else list(path.rglob("*.py"))"
          - "- 2025-10-29: Enhanced lint.py with YAML validation and verbose checks"
          - "-        return [(0, f"Error parsing {filepath}: {e}")]"
          - "-    """Main lint runner for CLI.""""
          - "-        results = check_file(file)"
          - "-        if results:"
          - "-            for line, msg in results:"
          - "-            total_errors += len(results)"
          - "-    if total_errors == 0:"
          - "-        print(f"\n❌ Found {total_errors} lint issues.")"
          - "-        return 1"
          - "- 2025-10-29: Add agent spec linter for Python files"
        ---/agentspec
    '''
    path = Path(target)
    files = collect_python_files(path)

    total_errors = 0
    total_warnings = 0
    
    for file in files:
        errors, warnings = check_file(file, min_lines=min_lines)
        
        if errors or warnings:
            print(f"\n{file}:")
            for line, msg in errors:
                print(f"  Line {line}: {msg}")
                total_errors += 1
            for line, msg in warnings:
                print(f"  Line {line}: {msg}")
                total_warnings += 1

    print(f"\n{'='*60}")
    if total_errors == 0 and (total_warnings == 0 or not strict):
        print("✅ All files have valid agent specs.")
        print(f"   {len(files)} files checked, {total_warnings} warnings")
        return 0
    else:
        if strict and total_warnings > 0:
            print(f"❌ Found {total_errors} errors and {total_warnings} warnings (strict mode)")
            return 1
        elif total_errors > 0:
            print(f"❌ Found {total_errors} errors and {total_warnings} warnings")
            return 1
        else:
            print(f"⚠️  Found {total_warnings} warnings")
            return 0
