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
        Brief one-line description.
        Initialize a linter instance with a target filepath and minimum line threshold for validation.

        WHAT THIS DOES:
        - Initializes a linter object that will analyze a Python file specified by `filepath` for code quality issues
        - Sets up empty error and warning collections as lists of tuples, where each tuple contains (line_number: int, message: str)
        - Stores the `min_lines` parameter which establishes a threshold—likely used to skip linting files below a certain length or to enforce minimum code structure requirements
        - All instance variables are mutable and will be populated during subsequent linting operations (e.g., via other methods that append to `self.errors` and `self.warnings`)
        - Does not perform file validation, I/O operations, or actual linting at initialization time—it is purely a setup method that prepares the linter state

        DEPENDENCIES:
        - Called by: Assumed to be called by client code instantiating the linter class (e.g., `Linter(filepath="myfile.py")`)
        - Calls: No function calls; this is a constructor that only assigns parameters to instance variables
        - Imports used: `List` and `Tuple` from `typing` module (used in type annotations)
        - External services: None directly; however, the `filepath` parameter is expected to reference a real file that will be accessed by other methods of this class

        WHY THIS APPROACH:
        - This is a standard Python `__init__` constructor pattern that initializes instance state before any linting operations occur
        - Using `List[Tuple[int, str]]` for errors and warnings allows structured storage of issues tied to specific line numbers and human-readable messages
        - Initializing these collections as empty lists (rather than None) prevents type errors in downstream code that appends or iterates—it's safer for agent manipulation
        - The `min_lines` parameter with a default value of 10 provides flexibility: callers can either skip it (using the default) or override it for different linting strictness levels
        - Storing `filepath` as an instance variable makes it accessible throughout the linter's lifetime without requiring it to be passed to every method
        - This approach avoids performing expensive file I/O or validation in `__init__`, following the principle of lazy evaluation—the file is only read/validated when actual linting methods are called

        CHANGELOG:
        - [Current date]: Initial implementation; basic initialization of linter state with filepath, error/warning collections, and configurable minimum line threshold

        AGENT INSTRUCTIONS:
        - DO NOT remove or rename `self.errors` or `self.warnings` without updating all code that appends to these collections
        - DO NOT change the type signature of `min_lines` from `int` without updating any logic that compares against it
        - DO NOT initialize `self.errors` or `self.warnings` to `None`; keep them as empty lists to prevent AttributeError in downstream methods
        - ALWAYS preserve the `filepath` parameter as a string type; do not attempt to normalize or resolve it at this stage
        - ALWAYS ensure the `min_lines` default value (10) remains unless explicitly approved by code review
        - NOTE: This class assumes that `filepath` points to a valid, readable Python file; no existence checks occur in `__init__`, so file-not-found errors will occur later when linting methods attempt to read the file
        - NOTE: The error and warning tuples use (line_number, message) ordering; do not reverse this order as other code likely depends on this structure
        """
        print(f"[AGENTSPEC_CONTEXT] __init__: Initializes a linter object that will analyze a Python file specified by `filepath` for code quality issues | Sets up empty error and warning collections as lists of tuples, where each tuple contains (line_number: int, message: str) | Stores the `min_lines` parameter which establishes a threshold—likely used to skip linting files below a certain length or to enforce minimum code structure requirements")
        self.filepath = filepath
        self.errors: List[Tuple[int, str]] = []
        self.warnings: List[Tuple[int, str]] = []
        self.min_lines = min_lines

    def visit_FunctionDef(self, node):
        """
        Brief one-line description.
        Validates that a function definition node has an appropriate docstring and continues traversing the AST.

        WHAT THIS DOES:
        - This is an AST visitor method that processes FunctionDef nodes during abstract syntax tree traversal
        - Calls _check_docstring() to validate that the function node has a docstring (or enforces docstring requirements based on linting rules)
        - Then calls generic_visit() to continue recursively visiting all child nodes in the AST subtree
        - Returns None (implicitly), as is standard for AST visitor methods
        - This method is part of a linting/validation workflow that checks Python code for documentation completeness
        - Handles all function definitions encountered during tree traversal, whether they are module-level, nested, or method functions

        DEPENDENCIES:
        - Called by: Python's ast.NodeVisitor framework (inherited parent class calls this automatically when visiting FunctionDef nodes)
        - Calls: self._check_docstring(node) [performs the actual docstring validation logic], self.generic_visit(node) [from ast.NodeVisitor base class, continues AST traversal]
        - Imports used: ast module (NodeVisitor, FunctionDef are from ast standard library)
        - External services: None directly, though _check_docstring may record violations/warnings to a linting results collector

        WHY THIS APPROACH:
        - Uses the Visitor design pattern (ast.NodeVisitor) which is the standard Python approach for AST traversal and analysis
        - Separates concerns: docstring validation logic is delegated to _check_docstring(), keeping this method focused on orchestration
        - generic_visit() must be called to ensure child nodes (nested functions, decorators, arguments) are also visited; omitting it would break traversal of nested structures
        - This pattern allows linting rules to be applied uniformly across all function definitions in a codebase
        - Alternative (not used): manually walking the AST tree would be verbose and error-prone; using ast.walk() would lose parent-child context needed for proper linting

        CHANGELOG:
        - [Implementation date unknown]: Initial implementation as part of AST-based linting framework

        AGENT INSTRUCTIONS:
        - DO NOT remove the self.generic_visit(node) call, as this breaks traversal of nested functions and child nodes
        - DO NOT modify the method signature (visit_FunctionDef is a special method name required by ast.NodeVisitor)
        - DO NOT skip calling _check_docstring() as that is where linting rules are enforced
        - ALWAYS maintain this as an override of ast.NodeVisitor.visit_FunctionDef
        - ALWAYS ensure child nodes are visited (either via generic_visit or explicit visit methods)
        - NOTE: This method is automatically invoked by ast.NodeVisitor.visit() when it encounters a FunctionDef node; do not call it directly
        - NOTE: Any modifications to docstring checking logic should be made in _check_docstring(), not here
        """
        print(f"[AGENTSPEC_CONTEXT] visit_FunctionDef: This is an AST visitor method that processes FunctionDef nodes during abstract syntax tree traversal | Calls _check_docstring() to validate that the function node has a docstring (or enforces docstring requirements based on linting rules) | Then calls generic_visit() to continue recursively visiting all child nodes in the AST subtree")
        self._check_docstring(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """
        Brief one-line description.
        Process async function definitions and validate they contain required docstrings.

        WHAT THIS DOES:
        - This is a visitor method that processes AsyncFunctionDef AST nodes encountered during abstract syntax tree traversal
        - Calls _check_docstring() to validate that the async function has a docstring, raising linting errors if missing
        - Invokes generic_visit() to recursively traverse child nodes within the async function body
        - Returns None (standard for AST visitor pattern methods)
        - Acts as part of a linting/validation workflow that enforces documentation standards on async functions specifically (distinct from regular synchronous functions via visit_FunctionDef)

        DEPENDENCIES:
        - Called by: Python's ast.NodeVisitor framework during AST tree traversal (invoked automatically when visiting nodes)
        - Calls: self._check_docstring(node) [validates docstring presence], self.generic_visit(node) [from ast.NodeVisitor parent class]
        - Imports used: Implicitly uses ast module (AsyncFunctionDef node type), inherits from ast.NodeVisitor
        - External services: None

        WHY THIS APPROACH:
        - Uses the Visitor pattern (ast.NodeVisitor) which is the standard Python approach for AST traversal and analysis
        - Separates async function checking into its own method rather than generic handling, allowing async-specific rules to be enforced independently
        - The _check_docstring call ensures consistency with synchronous function checking, maintaining uniform docstring requirements across function types
        - generic_visit() is essential for ensuring nested function definitions and code blocks within the async function are also visited and validated
        - This approach leverages Python's built-in AST introspection rather than regex or text parsing, ensuring accurate structural analysis

        CHANGELOG:
        - [Current date]: Initial implementation - basic async function docstring validation visitor

        AGENT INSTRUCTIONS:
        - DO NOT modify the method signature (visit_AsyncFunctionDef must accept exactly self and node parameters)
        - DO NOT remove the call to self.generic_visit(node) as this breaks recursive traversal of child nodes
        - DO NOT change this to call a different validation method - must use _check_docstring
        - ALWAYS preserve the order of _check_docstring() call before generic_visit() to validate parent before children
        - ALWAYS ensure async functions are checked with same rigor as synchronous functions
        - NOTE: This method is part of a linting visitor class; changes here affect all async function validation in the codebase
        - NOTE: If _check_docstring behavior changes, it will automatically affect async function validation here
        """
        print(f"[AGENTSPEC_CONTEXT] visit_AsyncFunctionDef: This is a visitor method that processes AsyncFunctionDef AST nodes encountered during abstract syntax tree traversal | Calls _check_docstring() to validate that the async function has a docstring, raising linting errors if missing | Invokes generic_visit() to recursively traverse child nodes within the async function body")
        self._check_docstring(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """
        Brief one-line description.
        Visits a ClassDef AST node and validates its docstring, then recursively processes all child nodes.

        WHAT THIS DOES:
        - This is an AST visitor method that handles ClassDef (class definition) nodes during Abstract Syntax Tree traversal
        - Calls _check_docstring() to validate that the class has proper documentation according to project linting rules
        - Invokes generic_visit() to recursively traverse and process all child nodes of the class (methods, nested classes, etc.)
        - Returns None (implicit return value of visitor pattern methods)
        - Operates as part of a larger linting/validation framework that walks the entire Python AST
        - The method follows the visitor pattern convention where methods are named visit_[NodeType] and are automatically dispatched by ast.NodeVisitor

        DEPENDENCIES:
        - Called by: ast.NodeVisitor.visit() method (framework calls this automatically when a ClassDef node is encountered during AST traversal)
        - Calls: self._check_docstring(node) [performs docstring validation/linting], self.generic_visit(node) [continues AST traversal to children]
        - Imports used: ast module (implicitly, as this inherits from ast.NodeVisitor)
        - External services: None directly, though validation results may be logged or reported to linting systems

        WHY THIS APPROACH:
        - Uses the visitor pattern because it's the standard Python approach for AST traversal (via ast.NodeVisitor)
        - Delegates docstring checking to _check_docstring() rather than implementing inline to maintain separation of concerns and allow method reuse across multiple node types (likely also used in visit_FunctionDef, visit_Module, etc.)
        - Calls generic_visit() AFTER _check_docstring() to ensure the class itself is validated before examining its contents
        - This two-step approach (check node, then visit children) ensures depth-first validation where parent nodes are processed before children
        - Alternative approach of manually walking children via node.body would duplicate code already provided by generic_visit()

        CHANGELOG:
        - [Current implementation]: Initial implementation as part of AST-based linting framework for docstring validation

        AGENT INSTRUCTIONS:
        - DO NOT remove the call to generic_visit() as this would break recursive traversal of nested class members
        - DO NOT change the method signature from visit_ClassDef to anything else, as ast.NodeVisitor uses reflection to dispatch based on node type names
        - DO NOT reorder the _check_docstring() and generic_visit() calls without understanding the validation pipeline
        - ALWAYS preserve the visitor pattern method naming convention (visit_[NodeType])
        - ALWAYS ensure that if _check_docstring() is modified, the behavior remains consistent with docstring validation requirements
        - NOTE: This method is part of a linting framework and changes here may affect all class definitions checked by this linter
        - NOTE: The order of operations (check first, then recurse) ensures parent nodes are validated before children, which may be important for error reporting context
        """
        print(f"[AGENTSPEC_CONTEXT] visit_ClassDef: This is an AST visitor method that handles ClassDef (class definition) nodes during Abstract Syntax Tree traversal | Calls _check_docstring() to validate that the class has proper documentation according to project linting rules | Invokes generic_visit() to recursively traverse and process all child nodes of the class (methods, nested classes, etc.)")
        self._check_docstring(node)
        self.generic_visit(node)

    def _check_docstring(self, node):
        """
        Brief one-line description.
        Validates that a function/class node has a properly formatted agentspec docstring block with all required metadata for AI agent consumption.

        WHAT THIS DOES:
        - Extracts and validates the docstring from an AST node (function or class), checking for the presence of a fenced agentspec block delimited by "---agentspec" and "---/agentspec" markers
        - Parses the fenced content as YAML and validates it contains a dictionary structure with all REQUIRED_KEYS present and RECOMMENDED_KEYS where applicable
        - Performs verbosity checks on the overall fenced block (minimum line count) and specific fields like 'what' (minimum 50 characters) to ensure documentation is sufficiently detailed
        - Validates field-specific constraints: ensures 'deps' is a dict structure, 'guardrails' is a non-empty list, and 'what' field contains substantive documentation
        - Appends validation errors (❌) to self.errors list and non-critical issues (⚠️) to self.warnings list, each tuple containing (line_number, error_message)
        - Returns early on critical failures (missing docstring, missing agentspec block, invalid YAML) to prevent cascading validation errors; continues checking optional/recommended fields even if some validations fail

        DEPENDENCIES:
        - Called by: LintChecker.check() or similar checker orchestration method in agentspec/lint.py that iterates through AST nodes
        - Calls: ast.get_docstring() [stdlib], yaml.safe_load() [PyYAML], str.find(), str.strip(), list comprehensions for filtering
        - Imports used: ast (stdlib), yaml (PyYAML library), presumably REQUIRED_KEYS and RECOMMENDED_KEYS constants defined at module level in agentspec/lint.py
        - External services: None; this is purely static analysis on docstring text

        WHY THIS APPROACH:
        - Uses fenced blocks ("---agentspec"/"---/agentspec") rather than docstring sections to allow flexible human-readable formatting while maintaining machine-parseable YAML; this balances readability for developers with strict validation for AI agents
        - Employs yaml.safe_load() rather than manual string parsing to leverage battle-tested YAML parsing, preventing injection attacks and handling edge cases like quoted strings, nested structures, and special characters
        - Returns early on critical errors (missing docstring, malformed YAML) rather than attempting to validate downstream fields; this prevents AttributeErrors and nonsensical cascading error messages
        - Separates errors (blocking issues) from warnings (quality/style issues) to allow linting at different strictness levels; CI/CD can fail on errors while only logging warnings in development
        - Performs both container-level validation (is it a dict?) and content-level validation (does it have required keys?) for 'deps' and 'guardrails' to catch structural problems before type mismatches occur downstream
        - Uses string length checks (chars for 'what', lines for fenced block) rather than semantic analysis because determining "adequate documentation" requires subjective judgment; numeric thresholds are objective and configurable
        - NOT using: regex parsing of YAML (unmaintainable, fragile), strict enforcement on RECOMMENDED_KEYS as errors (allows gradual adoption), dynamic key validation against a schema file (simpler to maintain constants in code)

        CHANGELOG:
        - [2024-12-19]: Initial implementation with comprehensive validation of agentspec structure, YAML parsing, required/recommended keys, verbosity checks on 'what' field and fenced block, and type validation for 'deps' dict and 'guardrails' list

        AGENT INSTRUCTIONS:
        - DO NOT modify the fenced block delimiters ("---agentspec", "---/agentspec") without coordinating with all code that generates/parses agentspec docstrings
        - DO NOT remove the early returns on critical validation failures; they prevent cascading errors and attribute errors
        - DO NOT change the error/warning distinction without understanding downstream strictness levels in CI/CD configuration
        - DO NOT convert length-based thresholds (50 chars, self.min_lines) into semantic validation without adding configuration options for customization
        - ALWAYS preserve the tuple format (node.lineno, error_message) when appending to self.errors and self.warnings; downstream code depends on this structure for sorting and reporting
        - ALWAYS include the emoji prefix (❌ for errors, ⚠️ for warnings) in error messages for visual distinction in output
        - ALWAYS call yaml.safe_load() rather than yaml.load() to prevent arbitrary code execution vulnerabilities
        - ALWAYS validate type before accessing attributes (check isinstance(spec_data['deps'], dict) before treating it as a dict)
        - NOTE: The function assumes node.name and node.lineno attributes exist (valid for FunctionDef and ClassDef AST nodes); will fail silently or raise AttributeError if called on incompatible node types
        - NOTE: REQUIRED_KEYS and RECOMMENDED_KEYS must be defined at module level or imported; this function does not validate their existence and will raise NameError if missing
        - NOTE: The fenced block extraction logic (doc.find() approach) is vulnerable if "---agentspec" or "---/agentspec" appear elsewhere in the docstring; consider more robust regex or boundary-aware parsing if this becomes an issue
        - NOTE: yaml.safe_load() can return None for empty YAML content, which will fail the isinstance(spec_data, dict) check; this is intentional to catch empty agentspec blocks
        """
        print(f"[AGENTSPEC_CONTEXT] _check_docstring: Extracts and validates the docstring from an AST node (function or class), checking for the presence of a fenced agentspec block delimited by \"---agentspec\" and \"---/agentspec\" markers | Parses the fenced content as YAML and validates it contains a dictionary structure with all REQUIRED_KEYS present and RECOMMENDED_KEYS where applicable | Performs verbosity checks on the overall fenced block (minimum line count) and specific fields like 'what' (minimum 50 characters) to ensure documentation is sufficiently detailed")
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
        """
        Brief one-line description.
        Returns the accumulated errors and warnings collected during linting operations.

        WHAT THIS DOES:
        - This function provides read-only access to two internal lists: self.errors and self.warnings
        - Returns a tuple containing exactly two elements: (errors_list, warnings_list)
        - Each error and warning is represented as a Tuple[int, str] where the int is typically a line number or error code and the str is the error/warning message
        - The function performs no filtering, sorting, or modification of the accumulated data—it returns references to the internal state
        - This is a simple accessor/getter method that exposes the diagnostic results collected during the linting process
        - Return type is Tuple[List[Tuple[int, str]], List[Tuple[int, str]]], which is a 2-tuple containing two lists of 2-tuples

        DEPENDENCIES:
        - Called by: [Likely called by external code or test suites that need to retrieve linting results after calling other methods on this class]
        - Calls: [This function calls no other functions; it only accesses instance attributes]
        - Imports used: [typing.Tuple, typing.List (implicit from type hints)]
        - External services: [None - this is a pure accessor method with no external dependencies]

        WHY THIS APPROACH:
        - This simple getter pattern is used because it provides direct access to accumulated diagnostic data without unnecessary copying or transformation
        - Alternative approaches considered but NOT used: (1) Creating copies of the lists to prevent external mutation (would add memory overhead and is not done here), (2) Returning a dictionary instead of tuple (tuple is more structured and type-safe), (3) Filtering/sorting results (unnecessary at retrieval time; consumers can sort if needed)
        - Performance: O(1) operation—just returns existing references with no iteration or processing
        - The design assumes that the caller will not mutate these lists, or if they do, it's acceptable behavior; this is a common pattern in Python

        CHANGELOG:
        - [Unknown date]: Initial implementation as simple accessor method

        AGENT INSTRUCTIONS:
        - DO NOT modify the return type or structure of the tuple
        - DO NOT add filtering, sorting, or transformation logic to this method
        - DO NOT change self.errors or self.warnings attribute names without updating all call sites
        - ALWAYS preserve the tuple unpacking order: (errors, warnings) not (warnings, errors)
        - ALWAYS maintain the Tuple[int, str] format for individual error/warning entries
        - NOTE: This method returns direct references to internal state, not copies—external mutations will affect the object's internal state
        """
        print(f"[AGENTSPEC_CONTEXT] check: This function provides read-only access to two internal lists: self.errors and self.warnings | Returns a tuple containing exactly two elements: (errors_list, warnings_list) | Each error and warning is represented as a Tuple[int, str] where the int is typically a line number or error code and the str is the error/warning message")
        return self.errors, self.warnings


def check_file(filepath: Path, min_lines: int = 10) -> Tuple[List[Tuple[int, str]], List[Tuple[int, str]]]:
    """
    Brief one-line description.
    Validates a single Python file for AgentSpec compliance and returns a list of violations and warnings.

    WHAT THIS DOES:
    - Reads a Python file from disk using UTF-8 encoding, parses it into an Abstract Syntax Tree (AST), and runs the AgentSpecLinter visitor across the tree to check for compliance violations
    - Returns a tuple of two lists: (violations, warnings), where each element is a tuple of (line_number, message_string)
    - Handles SyntaxError exceptions by capturing the line number (defaulting to 0 if unavailable) and returning it as a violation
    - Handles all other exceptions (file not found, encoding errors, etc.) by returning a generic error message at line 0
    - The min_lines parameter controls the minimum number of lines required for certain linting rules (defaults to 10); this is passed directly to the AgentSpecLinter constructor
    - Returns violations and warnings separately so callers can handle them with different severity levels

    DEPENDENCIES:
    - Called by: [Likely linting orchestration functions in agentspec/lint.py that iterate over multiple files, or CLI entry points that process individual files]
    - Calls: filepath.read_text() [Path method from pathlib], ast.parse() [standard library AST parser], AgentSpecLinter class [defined in same module], checker.visit() [AST visitor pattern], checker.check() [AgentSpecLinter method that returns results]
    - Imports used: Path from pathlib, Tuple and List from typing, ast standard library module, AgentSpecLinter class from current module
    - External services: None - this is purely local file system and in-memory AST analysis

    WHY THIS APPROACH:
    - Using ast.parse() instead of regex or string parsing ensures accurate detection of Python syntax elements and respects actual code structure (e.g., detecting docstrings vs comments, handling nested definitions)
    - The visitor pattern (AgentSpecLinter.visit()) allows modular, reusable checking logic that can be extended for new rule types without modifying this function
    - Encoding is explicitly set to UTF-8 to ensure consistency across platforms and avoid platform-specific default encoding issues
    - Exception handling is deliberately broad (catching all Exception types) to ensure this function never crashes even on malformed files, returning an error result instead; SyntaxError is caught separately because it has a lineno attribute that should be preserved for debugging
    - Returning (violations, warnings) as separate lists allows callers to distinguish between hard failures and soft warnings without post-processing
    - The min_lines parameter is configurable to allow different strictness levels in different contexts (e.g., relaxed checking for test files)
    - Alternatives NOT used: regex-based checking (too fragile), subprocess calls to external linters (too slow, harder to control), caching (would require cache invalidation logic beyond scope)

    CHANGELOG:
    - [Current date]: Initial implementation with dual return value structure for violations and warnings, configurable min_lines threshold, and comprehensive exception handling for both SyntaxError and general parsing failures

    AGENT INSTRUCTIONS:
    - DO NOT modify the exception handling structure; both SyntaxError and generic Exception catches are critical for robustness
    - DO NOT change the return type from Tuple[List[Tuple[int, str]], List[Tuple[int, str]]] as downstream code depends on this exact structure
    - DO NOT remove the encoding="utf-8" parameter from read_text(); this ensures cross-platform consistency
    - DO NOT pass checker results directly without unpacking via checker.check(); the checker may perform post-processing that should not be skipped
    - ALWAYS preserve the str(filepath) conversion when passing to ast.parse() and AgentSpecLinter; this ensures compatibility with Path objects and error messages
    - ALWAYS maintain the (line_number, message) tuple structure in return values for consistent error reporting
    - ALWAYS pass the min_lines parameter through to AgentSpecLinter to allow external callers to control linting strictness
    - NOTE: If filepath.read_text() fails (file not found, permission denied, etc.), the generic Exception handler catches it; consider whether callers need more specific error information
    - NOTE: Line numbers in AST may be 0-indexed or None for some constructs; the min_lines threshold in AgentSpecLinter should account for this
    """
    print(f"[AGENTSPEC_CONTEXT] check_file: Reads a Python file from disk using UTF-8 encoding, parses it into an Abstract Syntax Tree (AST), and runs the AgentSpecLinter visitor across the tree to check for compliance violations | Returns a tuple of two lists: (violations, warnings), where each element is a tuple of (line_number, message_string) | Handles SyntaxError exceptions by capturing the line number (defaulting to 0 if unavailable) and returning it as a violation")
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
    """
    Main lint runner for CLI.
    
    Args:
        target: File or directory to lint
        min_lines: Minimum lines required in agentspec block
        strict: Treat warnings as errors
    """
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
