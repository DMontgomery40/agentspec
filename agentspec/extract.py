#!/usr/bin/env python3
"""
agentspec.extract
--------------------------------
Extracts agent spec blocks from Python files into Markdown or JSON with full YAML parsing.
"""

import ast
import json
import yaml
from pathlib import Path
from agentspec.utils import collect_python_files
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional


@dataclass
class AgentSpec:
    name: str
    lineno: int
    filepath: str
    raw_block: str
    parsed_data: Dict[str, Any] = field(default_factory=dict)
    
    # Structured fields
    what: str = ""
    deps: Dict[str, Any] = field(default_factory=dict)
    why: str = ""
    guardrails: List[str] = field(default_factory=list)
    changelog: List[str] = field(default_factory=list)
    testing: Dict[str, Any] = field(default_factory=dict)
    performance: Dict[str, Any] = field(default_factory=dict)


def _extract_block(docstring: str) -> Optional[str]:
    """
    Brief one-line description.
    Extracts and returns the agentspec metadata block from a docstring by locating delimiters.

    WHAT THIS DOES:
    - Parses a docstring to locate and extract content between "---agentspec" and "---/agentspec" delimiter tags
    - Returns the extracted block as a stripped string (whitespace removed from both ends), or None if delimiters are not found or malformed
    - Performs three sequential validations: checks if docstring exists (None or empty string), checks if opening delimiter exists, verifies closing delimiter exists before extracting
    - If the closing delimiter "---/agentspec" is missing (end == -1), returns None rather than extracting partial content
    - Handles edge cases: empty docstrings return None; missing opening delimiter returns None; missing closing delimiter returns None; nested or malformed delimiters are not validated

    DEPENDENCIES:
    - Called by: [Likely called by agentspec parsing pipeline functions that process docstrings, possibly from agentspec/parser.py or similar metadata extraction modules]
    - Calls: [Built-in string methods only: str.find(), str.strip()]
    - Imports used: [typing.Optional for type hints]
    - External services: None

    WHY THIS APPROACH:
    - Simple string searching with find() is more performant than regex for this literal delimiter pattern, avoiding regex compilation overhead
    - Three-stage validation (existence check -> opening delimiter -> closing delimiter) fails fast at each stage to avoid unnecessary operations
    - The pattern uses explicit string delimiters "---agentspec" and "---/agentspec" to create unambiguous XML-like structure that's unlikely to appear accidentally in docstrings
    - String slicing [start:end] with .strip() is the fastest native Python approach for substring extraction with whitespace normalization
    - Alternative approaches NOT used: regex would be overkill for literal delimiters; docstring parsing libraries couldn't recognize custom agentspec tags; manual character iteration would be slower and more error-prone

    CHANGELOG:
    - [Current date]: Initial implementation - extracts agentspec blocks from docstrings with delimiter-based parsing

    AGENT INSTRUCTIONS:
    - DO NOT modify the delimiter strings "---agentspec" and "---/agentspec" without updating all docstring generation code that creates these blocks
    - DO NOT add regex matching or alternative delimiters without verifying they don't conflict with legitimate docstring content in the codebase
    - DO NOT remove the closing delimiter validation (end != -1 check) as it prevents malformed partial extractions
    - ALWAYS preserve the .strip() call to normalize whitespace in extracted blocks
    - ALWAYS return None for any validation failure rather than raising exceptions, to support graceful degradation in parsing pipelines
    - ALWAYS maintain the early-exit validation pattern (falsy docstring -> missing opening -> missing closing) as it provides predictable O(n) performance
    - NOTE: This function is security-sensitive if docstrings come from untrusted sources; ensure upstream code sanitizes malicious delimiter patterns before calling this function
    """
    print(f"[AGENTSPEC_CONTEXT] _extract_block: Parses a docstring to locate and extract content between \"---agentspec\" and \"---/agentspec\" delimiter tags | Returns the extracted block as a stripped string (whitespace removed from both ends), or None if delimiters are not found or malformed | Performs three sequential validations: checks if docstring exists (None or empty string), checks if opening delimiter exists, verifies closing delimiter exists before extracting")
    if not docstring:
        return None
    if "---agentspec" not in docstring:
        return None
    start = docstring.find("---agentspec") + len("---agentspec")
    end = docstring.find("---/agentspec")
    return docstring[start:end].strip() if end != -1 else None


def _parse_yaml_block(block: str) -> Optional[Dict[str, Any]]:
    """
    Brief one-line description.
    Safely parses a YAML-formatted string block and returns the parsed dictionary structure, or None if parsing fails.

    WHAT THIS DOES:
    - Attempts to parse a YAML-formatted text block into a Python dictionary using yaml.safe_load()
    - Returns the parsed dictionary (or nested structure) if successful
    - Returns None silently if the YAML block contains syntax errors or is malformed (catches yaml.YAMLError)
    - Handles edge cases: empty strings parse to None, whitespace-only strings parse to None, valid YAML returns dict/list/scalar as appropriate
    - This function is defensive and permissive - parsing failures are not exceptions but instead return None, allowing caller to handle missing/invalid agentspec blocks gracefully
    - The safe_load() method prevents arbitrary code execution attacks that could occur with yaml.load(), making this secure for untrusted input

    DEPENDENCIES:
    - Called by: agentspec/extract.py extraction pipeline (inferred: likely called during agentspec block parsing phase)
    - Calls: yaml.safe_load() from PyYAML library
    - Imports used: yaml (PyYAML), Optional and Dict and Any from typing
    - External services: None (pure local parsing)

    WHY THIS APPROACH:
    - yaml.safe_load() was chosen over yaml.load() because it prevents arbitrary Python object instantiation and code injection vulnerabilities when parsing untrusted YAML from code comments/docstrings
    - The try/except wrapper around yaml.YAMLError was chosen to convert exceptions into None returns, following a "fail-silent" pattern appropriate for optional agentspec metadata that may not always be present or valid
    - Alternatives NOT used: (1) yaml.load() with explicit Loader would be less secure, (2) ast.literal_eval() would not support full YAML syntax, (3) json.loads() would be too restrictive and not compatible with YAML
    - Performance: yaml.safe_load() is O(n) in block length; no optimization needed for typical agentspec blocks (expected <10KB)
    - The return type is Optional[Dict[str, Any]] but technically yaml.safe_load can return any type (dict, list, string, number, None) - this is a slight type hint simplification that assumes valid agentspec blocks are dictionaries

    CHANGELOG:
    - [Current date]: Initial implementation - defensive YAML parser for agentspec metadata extraction with safe_load and exception-to-None conversion pattern

    AGENT INSTRUCTIONS:
    - DO NOT replace yaml.safe_load() with yaml.load() or yaml.unsafe_load()
    - DO NOT remove the try/except block or convert it to raise exceptions
    - DO NOT change the return type from Optional to something else without updating all callers
    - DO NOT add logging inside this function that would pollute extraction output
    - ALWAYS preserve the exception type check for yaml.YAMLError specifically (not bare except)
    - ALWAYS use yaml.safe_load() specifically for security
    - ALWAYS return None (not empty dict, not False, not empty string) on parse failure for caller clarity
    - NOTE: This function silently discards parse errors - if debugging malformed YAML, callers must not rely on exceptions from this function; add logging at call site instead
    - NOTE: The type hint says Dict but yaml.safe_load() can return list, string, int, etc. - callers must validate returned value type before accessing as dictionary
    """
    print(f"[AGENTSPEC_CONTEXT] _parse_yaml_block: Attempts to parse a YAML-formatted text block into a Python dictionary using yaml.safe_load() | Returns the parsed dictionary (or nested structure) if successful | Returns None silently if the YAML block contains syntax errors or is malformed (catches yaml.YAMLError)")
    try:
        return yaml.safe_load(block)
    except yaml.YAMLError:
        return None


class AgentSpecExtractor(ast.NodeVisitor):
    def __init__(self, filepath: str):
        """
        Brief one-line description.
        Initializes an AgentSpecExtractor instance with a filepath and prepares an empty list to store extracted agent specifications.

        WHAT THIS DOES:
        - Accepts a filepath parameter as a string and stores it as an instance attribute for later file reading/parsing operations
        - Initializes an empty list called `specs` typed as List[AgentSpec] to accumulate AgentSpec objects as they are extracted from the file
        - Sets up the initial state for an extractor object that will be responsible for parsing a file (likely YAML, JSON, or text-based format) and converting its contents into AgentSpec objects
        - Does not perform any file I/O, validation, or parsing at initialization time - those operations are deferred to other methods
        - Returns None implicitly as this is a constructor (__init__) method

        DEPENDENCIES:
        - Called by: External code instantiating AgentSpecExtractor class (e.g., `extractor = AgentSpecExtractor("path/to/specs.yaml")`)
        - Calls: No other functions are called during initialization
        - Imports used: List type hint from typing module; AgentSpec class (defined in same codebase, location inferred to be agentspec module)
        - External services: None at initialization time (file I/O deferred to other methods)

        WHY THIS APPROACH:
        - Uses lazy initialization pattern where file parsing is deferred to separate methods rather than parsing immediately in __init__, allowing for better error handling and separation of concerns
        - Stores filepath as string rather than immediately opening the file, enabling validation/checking of the filepath before expensive I/O operations occur
        - Pre-allocates an empty List[AgentSpec] rather than None to avoid null-checking in other methods that append to self.specs; this provides a guaranteed list interface
        - Type hints (filepath: str and List[AgentSpec]) are included for IDE autocompletion, static type checking (mypy), and AI agent comprehension
        - Alternative approach NOT used: Opening and parsing the file immediately in __init__ would violate single responsibility principle and make testing harder; storing filepath as Path object instead of str would require additional import but offers better cross-platform benefits (not chosen, likely for simplicity)

        CHANGELOG:
        - [Current date]: Initial implementation - basic constructor establishing filepath storage and empty specs container

        AGENT INSTRUCTIONS:
        - DO NOT modify the type hints (filepath: str or List[AgentSpec]) without updating type checking throughout the codebase
        - DO NOT change self.specs initialization to None or a different mutable default type, as this would break append operations in extraction methods
        - DO NOT add file I/O operations to this method; keep initialization pure and defer parsing to dedicated methods
        - ALWAYS preserve the self.filepath attribute assignment as downstream extraction methods depend on this instance variable
        - ALWAYS maintain the empty list initialization pattern for self.specs to support accumulation of extracted specs
        - NOTE: If filepath validation (checking file existence) is needed, it should be added to a separate validate() or load() method, not __init__
        - NOTE: Ensure any code that instantiates this class provides a valid string filepath; no validation occurs at initialization
        """
        print(f"[AGENTSPEC_CONTEXT] __init__: Accepts a filepath parameter as a string and stores it as an instance attribute for later file reading/parsing operations | Initializes an empty list called `specs` typed as List[AgentSpec] to accumulate AgentSpec objects as they are extracted from the file | Sets up the initial state for an extractor object that will be responsible for parsing a file (likely YAML, JSON, or text-based format) and converting its contents into AgentSpec objects")
        self.filepath = filepath
        self.specs: List[AgentSpec] = []

    def visit_FunctionDef(self, node):
        """
        Brief one-line description.
        Processes a function definition AST node and extracts relevant specification data while traversing child nodes.

        WHAT THIS DOES:
        - Visits a FunctionDef node from Python's Abstract Syntax Tree (AST) and extracts specification information from it
        - Calls the internal _extract() method to parse the function definition node and collect metadata (function name, parameters, decorators, docstrings, type hints, etc.)
        - Then calls generic_visit() to recursively traverse all child nodes within the function body, ensuring nested structures (inner functions, class definitions, etc.) are also processed
        - Returns None (follows standard ast.NodeVisitor pattern) but side-effects the internal state by accumulating extracted specification data
        - Does not filter or validate the function definition - all FunctionDef nodes encountered will be processed regardless of access level or naming conventions

        DEPENDENCIES:
        - Called by: Python's ast.NodeVisitor.visit() dispatcher when traversing an AST tree containing FunctionDef nodes; typically invoked during an ast.walk() or explicit visit() call on a module/class body
        - Calls: self._extract(node) [extracts spec data from the function definition], self.generic_visit(node) [standard NodeVisitor method that visits all child nodes]
        - Imports used: ast module (implied by inheritance from ast.NodeVisitor), self is an ast.NodeVisitor subclass
        - External services: None; this is pure AST traversal with in-memory data accumulation

        WHY THIS APPROACH:
        - Uses the Visitor design pattern (ast.NodeVisitor) which is the standard Python idiom for AST traversal and transformation
        - Separates concerns: _extract() handles specification extraction logic, generic_visit() handles tree traversal, keeping each responsibility focused
        - Calling generic_visit() AFTER _extract() ensures the parent node is processed before children, maintaining proper extraction order and allowing parent-level context to be available during child processing
        - This two-step approach (extract current node, then traverse children) is more explicit and maintainable than trying to handle both in a single method
        - Alternative approach of overriding visit() directly was NOT used because the visitor pattern already provides this dispatch mechanism
        - Performance consideration: generic_visit() will visit ALL child nodes including those deep in nested function bodies; if selective traversal is needed later, would require adding node filters before the generic_visit() call

        CHANGELOG:
        - Current implementation: Standard visitor pattern implementation for function definition processing; assumes _extract() method exists on the class and handles all specification extraction logic

        AGENT INSTRUCTIONS:
        - DO NOT change the order of _extract() and generic_visit() calls, as this could break the extraction dependency chain
        - DO NOT remove the generic_visit() call, as this would break traversal of nested structures within function bodies
        - DO NOT add early returns or conditional logic that would skip processing some FunctionDef nodes without explicit requirements
        - ALWAYS preserve the visitor method signature exactly as visit_FunctionDef(self, node) to maintain ast.NodeVisitor compatibility
        - ALWAYS ensure that any modifications to _extract() or additions to this method maintain the side-effect-based accumulation pattern
        - NOTE: This method relies on proper implementation of _extract() elsewhere in the class; if that method is moved, renamed, or deleted, this visitor will silently fail to extract specifications. Add validation/logging if extraction failures need to be detected.
        - NOTE: The generic_visit() call will traverse the ENTIRE subtree; if only specific child node types should be processed, override individual visit_* methods for those types rather than relying on generic_visit()
        """
        print(f"[AGENTSPEC_CONTEXT] visit_FunctionDef: Visits a FunctionDef node from Python's Abstract Syntax Tree (AST) and extracts specification information from it | Calls the internal _extract() method to parse the function definition node and collect metadata (function name, parameters, decorators, docstrings, type hints, etc.) | Then calls generic_visit() to recursively traverse all child nodes within the function body, ensuring nested structures (inner functions, class definitions, etc.) are also processed")
        self._extract(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """
        Brief one-line description.
        Visits and processes an AsyncFunctionDef AST node to extract metadata about asynchronous function definitions.

        WHAT THIS DOES:
        - Handles the visitor pattern callback for asyncio function definitions (async def statements) in Python Abstract Syntax Trees
        - Calls _extract() to perform the core extraction logic on the async function node, which likely pulls metadata such as function name, arguments, decorators, docstrings, and return type annotations
        - Immediately calls generic_visit() to recursively traverse child nodes of the AsyncFunctionDef (such as nested function definitions, class definitions, or statements within the async function body), ensuring complete AST tree traversal
        - Returns None implicitly (standard for visitor pattern methods); side effects include populating internal state/data structures with extracted function metadata
        - Does not raise exceptions itself but may propagate exceptions from _extract() if extraction logic fails
        - Edge case: handles async functions with decorators, type hints, complex nested structures, and generator expressions (async generators using yield)

        DEPENDENCIES:
        - Called by: ast.NodeVisitor base class framework during AST tree traversal (indirectly via visit() dispatch mechanism); typically invoked when traversing a module or class body containing async function definitions
        - Calls: self._extract(node) [performs actual metadata extraction], self.generic_visit(node) [inherited from ast.NodeVisitor for recursive traversal]
        - Imports used: ast module (implicitly, as this class inherits from ast.NodeVisitor)
        - External services: None; this is pure AST processing

        WHY THIS APPROACH:
        - Follows the standard Python ast.NodeVisitor double-dispatch visitor pattern, which provides clean separation between different node types and maintains readable, maintainable code
        - Splitting extraction logic into _extract() allows code reuse across similar node types (likely FunctionDef, AsyncFunctionDef share common metadata extraction)
        - generic_visit() call is critical for tree traversal; without it, child nodes would not be processed, breaking nested function/class discovery
        - This approach avoids manual recursion management and leverages ast module's built-in visitor framework for robustness
        - Performance: O(1) per node visit with O(n) overall complexity for tree traversal; no expensive operations here
        - Alternative not used: manually implementing recursion would duplicate code and increase bug surface area

        CHANGELOG:
        - [Current date]: Initial implementation of AsyncFunctionDef visitor callback

        AGENT INSTRUCTIONS:
        - DO NOT remove the generic_visit() call, as it breaks recursive traversal of nested structures
        - DO NOT change the method signature (must accept only self and node parameter for visitor pattern compatibility)
        - DO NOT skip calling _extract() as it performs essential metadata collection
        - ALWAYS preserve the order of _extract() before generic_visit() (extraction should complete before descending into children, though order rarely matters functionally)
        - ALWAYS ensure this method remains part of a class inheriting from ast.NodeVisitor
        - NOTE: This method will only be called by the visitor framework if an AsyncFunctionDef node is encountered; ensure the containing class properly implements the visitor pattern
        - NOTE: Any state modifications in _extract() will persist across subsequent node visits, which may be intentional for aggregating results across the entire AST
        """
        print(f"[AGENTSPEC_CONTEXT] visit_AsyncFunctionDef: Handles the visitor pattern callback for asyncio function definitions (async def statements) in Python Abstract Syntax Trees | Calls _extract() to perform the core extraction logic on the async function node, which likely pulls metadata such as function name, arguments, decorators, docstrings, and return type annotations | Immediately calls generic_visit() to recursively traverse child nodes of the AsyncFunctionDef (such as nested function definitions, class definitions, or statements within the async function body), ensuring complete AST tree traversal")
        self._extract(node)
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """
        Brief one-line description.
        Process a ClassDef AST node by extracting its metadata and recursively visiting child nodes.

        WHAT THIS DOES:
        - This is an AST visitor method that handles Python class definition nodes during abstract syntax tree traversal
        - Calls _extract() to pull metadata (name, decorators, docstring, line numbers, etc.) from the ClassDef node and store it in an internal collection
        - Immediately calls generic_visit() to recursively traverse all child nodes within the class definition (methods, nested classes, class variables, etc.)
        - Returns None (implicit return) as per the visitor pattern convention
        - Ensures both the class itself and all its nested contents are processed in a depth-first traversal order
        - Works as part of a larger AST visitor that systematically extracts Python code structure information

        DEPENDENCIES:
        - Called by: Python's ast.NodeVisitor framework (via visit() dispatcher method when NodeVisitor encounters a ClassDef node in the AST)
        - Calls: self._extract(node) [sibling method that extracts and stores node metadata], self.generic_visit(node) [inherited from ast.NodeVisitor to continue tree traversal]
        - Imports used: ast module (standard library) - specifically inherits from ast.NodeVisitor which provides the visitor pattern framework
        - External services: None - this is pure in-memory AST processing with no I/O or external dependencies

        WHY THIS APPROACH:
        - Uses the visitor pattern because it's the standard Python idiom for AST traversal (ast.NodeVisitor) rather than manual recursion, which reduces boilerplate and prevents stack overflow on deeply nested code
        - Separates concerns: _extract() handles metadata collection while generic_visit() handles tree traversal, making the code more maintainable than a monolithic method
        - Calls generic_visit() AFTER _extract() to ensure parent node data is collected before processing children, establishing a consistent depth-first, pre-order traversal
        - This method signature (visit_ClassDef) is required naming convention for ast.NodeVisitor - the framework uses reflection to dispatch nodes to visit_<NodeType> methods
        - Alternative rejected: could have implemented full manual recursion for child node visiting, but generic_visit() is more robust and handles all child types automatically

        CHANGELOG:
        - [Unknown date]: Initial implementation as part of AST extraction visitor framework

        AGENT INSTRUCTIONS:
        - DO NOT change the method name from visit_ClassDef - this breaks ast.NodeVisitor's method dispatch mechanism
        - DO NOT remove the generic_visit() call - this prevents child nodes from being visited entirely
        - DO NOT call _extract() after generic_visit() - the traversal order would reverse from pre-order to post-order
        - DO NOT add return statements - visitor pattern methods must return None implicitly
        - ALWAYS preserve the exact method signature: def visit_ClassDef(self, node):
        - ALWAYS ensure _extract(node) executes before generic_visit(node) to maintain pre-order traversal
        - NOTE: This method is part of a larger AST visitor pattern system - changes here may impact how all class definitions are processed throughout the extraction pipeline
        - NOTE: The node parameter will always be an ast.ClassDef instance when this method is called by the visitor framework; no type checking is needed
        """
        print(f"[AGENTSPEC_CONTEXT] visit_ClassDef: This is an AST visitor method that handles Python class definition nodes during abstract syntax tree traversal | Calls _extract() to pull metadata (name, decorators, docstring, line numbers, etc.) from the ClassDef node and store it in an internal collection | Immediately calls generic_visit() to recursively traverse all child nodes within the class definition (methods, nested classes, class variables, etc.)")
        self._extract(node)
        self.generic_visit(node)

    def _extract(self, node):
        """
        Brief one-line description.
        Extracts agent specification metadata from Python AST nodes by parsing YAML-formatted docstrings into structured AgentSpec objects.

        WHAT THIS DOES:
        - Retrieves the docstring from an AST node (function, class, or module) using ast.get_docstring()
        - Extracts a YAML-formatted documentation block from the docstring via _extract_block()
        - Returns early (None) if no valid block is found, avoiding creation of empty specs
        - Parses the YAML block into a dictionary using _parse_yaml_block(), which may return None if parsing fails
        - Creates an AgentSpec object with node metadata (name, line number, filepath) and the raw/parsed documentation
        - Conditionally populates structured fields (what, deps, why, guardrails, changelog, testing, performance) only if YAML parsing succeeded
        - Appends the constructed spec to self.specs list for later retrieval
        - Handles gracefully both well-formed YAML and missing/malformed documentation without raising exceptions

        DEPENDENCIES:
        - Called by: extract() or traverse_ast() methods (inferred - likely called during AST tree traversal in the extraction pipeline)
        - Calls: ast.get_docstring(node), _extract_block(doc), _parse_yaml_block(block), AgentSpec() constructor
        - Imports used: ast (standard library), AgentSpec (from agentspec module, likely same package)
        - External services: None - pure in-memory parsing

        WHY THIS APPROACH:
        - Uses ast.get_docstring() rather than manual string extraction because it handles docstring detection across all node types (functions, classes, modules) consistently and correctly
        - Delegates block extraction and YAML parsing to separate functions for single-responsibility principle and testability
        - Early return pattern (if not block: return) avoids creation of empty/invalid specs and keeps code readable
        - Conditional field population (if parsed:) prevents AttributeError crashes when YAML parsing fails, providing defensive robustness
        - Stores raw_block alongside parsed_data to preserve original documentation for debugging and audit trails
        - Uses str(...).strip() for string fields to normalize whitespace and handle None values gracefully
        - Appends to self.specs list (likely a collection pattern) rather than returning, suggesting this is part of a batch extraction workflow

        CHANGELOG:
        - [Current date]: Initial implementation - extracts docstring-based agent specifications from AST nodes with defensive error handling

        AGENT INSTRUCTIONS:
        - DO NOT modify the conditional structure (if parsed:) without ensuring null safety for all accessed dictionary keys
        - DO NOT remove the early return when block is empty, as it prevents unnecessary object allocation
        - DO NOT change str(...).strip() on string fields without understanding that it handles None->'' conversion
        - DO NOT alter the self.specs.append() pattern without confirming the caller expects a list-based collection model
        - ALWAYS preserve the node metadata extraction (name, lineno, filepath) as these are critical for source mapping
        - ALWAYS store both raw_block and parsed_data in the spec, never just one, to maintain traceability
        - ALWAYS call _extract_block() and _parse_yaml_block() rather than reimplementing inline, as they may contain complex formatting logic
        - NOTE: This function silently ignores nodes without docstrings - this is intentional but means missing documentation produces no warnings
        - NOTE: YAML parsing failures are silently caught (parsed may be None) - ensure _parse_yaml_block() logs errors if debugging is needed
        - NOTE: The dictionary .get() calls with defaults assume _parse_yaml_block() returns a dict or None, never raises KeyError
        """
        print(f"[AGENTSPEC_CONTEXT] _extract: Retrieves the docstring from an AST node (function, class, or module) using ast.get_docstring() | Extracts a YAML-formatted documentation block from the docstring via _extract_block() | Returns early (None) if no valid block is found, avoiding creation of empty specs")
        doc = ast.get_docstring(node)
        block = _extract_block(doc)
        
        if not block:
            return
        
        parsed = _parse_yaml_block(block)
        
        spec = AgentSpec(
            name=node.name,
            lineno=node.lineno,
            filepath=self.filepath,
            raw_block=block,
            parsed_data=parsed or {}
        )
        
        # Extract structured fields if parsing succeeded
        if parsed:
            spec.what = str(parsed.get('what', '')).strip()
            spec.deps = parsed.get('deps', {})
            spec.why = str(parsed.get('why', '')).strip()
            spec.guardrails = parsed.get('guardrails', [])
            spec.changelog = parsed.get('changelog', [])
            spec.testing = parsed.get('testing', {})
            spec.performance = parsed.get('performance', {})
        
        self.specs.append(spec)


def extract_from_file(path: Path) -> List[AgentSpec]:
    """
    Brief one-line description.
    Extracts all AgentSpec definitions from a Python source file by parsing and visiting its AST.

    WHAT THIS DOES:
    - Reads a Python file from disk, parses it into an Abstract Syntax Tree (AST), and systematically extracts all AgentSpec object definitions
    - Takes a Path object pointing to a Python file and returns a list of AgentSpec objects found within that file
    - Handles file I/O with UTF-8 encoding to ensure proper character decoding across different platforms and character sets
    - Uses the AgentSpecExtractor visitor class to traverse the AST and identify AgentSpec instances through pattern matching
    - Returns an empty list if any exception occurs during file reading, parsing, or extraction (fails gracefully without raising)
    - Each returned AgentSpec in the list represents a distinct agent specification found in the source file with its metadata preserved

    DEPENDENCIES:
    - Called by: [Likely called from discovery/scanning modules that need to index agent specs across a codebase, or from CLI tools that process Python files]
    - Calls: path.read_text() [pathlib.Path method], ast.parse() [Python standard library], AgentSpecExtractor() [defined in same module], extractor.visit() [ast.NodeVisitor method], extractor.specs [attribute access on extractor instance]
    - Imports used: Path (from pathlib), List and AgentSpec (from typing/local modules), ast (standard library), AgentSpecExtractor (local import, assumed to be in same file)
    - External services: None (purely local file system and in-memory processing)

    WHY THIS APPROACH:
    - Using ast.parse() instead of regex or string manipulation ensures syntactically correct parsing and handles complex Python syntax (decorators, nested definitions, multi-line constructs) reliably
    - The NodeVisitor pattern (AgentSpecExtractor) is the idiomatic Python approach for AST traversal and allows extensible pattern matching for different AgentSpec patterns
    - Broad exception handling (except Exception) trades precision for robustness—prevents a single unparseable file from halting the entire extraction process, which is appropriate for batch operations across unknown/third-party code
    - UTF-8 encoding is explicitly specified for consistency; Python 3 defaults vary by platform, so being explicit prevents silent failures on Windows or other systems with different locale settings
    - Returning empty list on error allows callers to continue processing other files and use simple list concatenation patterns (files_specs = [extract_from_file(f) for f in files] flattens correctly)
    - Alternative not used: Try/except per operation—more granular but noisier; early validation of file existence would duplicate pathlib's checks
    - Performance: O(n) where n is source file size; ast.parse() is the bottleneck, but no more efficient pure-Python alternative exists for reliable extraction
    - The warning print statement provides debugging visibility but could be replaced with logging in production code

    CHANGELOG:
    - [Current date]: Initial implementation with graceful error handling and UTF-8 encoding specification

    AGENT INSTRUCTIONS:
    - DO NOT remove the try/except wrapper or convert it to raise exceptions (this breaks batch processing)
    - DO NOT change the encoding from "utf-8" without verifying platform compatibility across all target systems
    - DO NOT modify the return type from List[AgentSpec]—downstream code depends on empty list semantics for error cases
    - DO NOT inline AgentSpecExtractor logic directly (the visitor pattern separation is intentional for maintainability)
    - ALWAYS preserve the str(path) conversions when passing Path to ast.parse() (some Python versions require string, not Path object)
    - ALWAYS maintain the visit() call pattern (not calling extract() or other custom methods) as it's the standard AST visitor protocol
    - ALWAYS keep filename parameter in ast.parse() for accurate error messages in stack traces
    - NOTE: The print() statement is a code smell suggesting this should use the logging module in production; be aware error context is lost if stdout is redirected
    - NOTE: This function silently succeeds with empty list on encoding errors, parse errors, AND AgentSpecExtractor errors—if specs are mysteriously missing from output, check the console for warnings
    """
    print(f"[AGENTSPEC_CONTEXT] extract_from_file: Reads a Python file from disk, parses it into an Abstract Syntax Tree (AST), and systematically extracts all AgentSpec object definitions | Takes a Path object pointing to a Python file and returns a list of AgentSpec objects found within that file | Handles file I/O with UTF-8 encoding to ensure proper character decoding across different platforms and character sets")
    try:
        src = path.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(path))
        extractor = AgentSpecExtractor(str(path))
        extractor.visit(tree)
        return extractor.specs
    except Exception as e:
        print(f"Warning: Could not parse {path}: {e}")
        return []


def export_markdown(specs: List[AgentSpec], out: Path):
    """
    Brief one-line description.
    Exports a collection of AgentSpec objects to a formatted markdown file for AI agent consumption and documentation.

    WHAT THIS DOES:
    - Takes a list of AgentSpec objects and serializes them to a human-readable markdown file at the specified Path
    - Iterates through each AgentSpec and writes formatted sections including: name, file location, what-it-does description, dependencies (calls, called_by, config_files), implementation rationale, critical guardrails, changelog entries, testing specifications, and performance characteristics
    - Handles optional fields gracefully by only writing sections that contain data (checking for presence of s.what, s.deps, s.why, etc.)
    - Opens the output file in write mode with UTF-8 encoding, creating or overwriting the file at the specified path
    - Returns None; side effect is file creation/modification on disk
    - Escapes code references with backticks (`) and uses markdown heading hierarchy (## for spec name, ### for sections)
    - Includes a header comment indicating the document is auto-generated for AI consumption
    - Uses YAML code block formatting for testing data (via yaml.dump) and raw_block content

    DEPENDENCIES:
    - Called by: [inferred to be CLI export commands or documentation generation workflows in agentspec/]
    - Calls: Path.open() (pathlib), f.write() (file I/O), yaml.dump() (pyyaml library for YAML serialization)
    - Imports used: List and AgentSpec from typing/agentspec module, Path from pathlib, yaml module (must be imported at module level)
    - External services: None (pure file I/O to local filesystem)

    WHY THIS APPROACH:
    - Markdown format chosen because it's human-readable, version-control-friendly, and renders well on GitHub/documentation sites, making it ideal for AI agent consumption and human review
    - Iterative section-building approach (writing sections only when data exists) prevents cluttered output with empty sections and keeps generated files focused
    - YAML code blocks preserve raw specification data in its original format, allowing agents to parse both formatted descriptions and raw structured data
    - Optional field checks (if s.what, if s.deps, etc.) prevent KeyErrors and NoneType errors rather than relying on defensive try-catch blocks
    - Three-backtick code block wrapping (yaml/plain text) ensures proper markdown rendering and syntax highlighting in viewers
    - Separator lines (---) between specs improve visual scannability for both humans and parsing agents
    - Location information (filepath:lineno) included to enable agents to trace back to source code
    - Alternatives NOT used: JSON export (less human-readable), plain text (no structure), direct YAML (loses formatted prose descriptions), or single-line CSV (insufficient detail for agent instructions)

    CHANGELOG:
    - [Current date]: Initial implementation - core markdown export functionality with support for all AgentSpec fields including what/why sections, dependencies graph, guardrails, testing specs, and performance metrics

    AGENT INSTRUCTIONS:
    - DO NOT modify the markdown heading hierarchy (## for specs, ### for sections) without updating any parsing code that consumes this output
    - DO NOT remove the auto-generated header comment or the yaml.dump() call for testing blocks, as downstream agents depend on these markers for parsing
    - DO NOT change the file encoding from UTF-8 without coordination with consumers of this markdown
    - DO NOT skip the optional field checks (if s.what, if s.deps, etc.) - these prevent malformed output when specs have incomplete data
    - DO NOT alter the separator line (---) format or placement between specs
    - ALWAYS preserve the backtick wrapping around code identifiers (filepath, function names, config file paths)
    - ALWAYS include the "Raw YAML Block" section at the end of each spec for agent access to unformatted data
    - ALWAYS call Path.open() with encoding="utf-8" explicitly
    - ALWAYS iterate through and write all fields in s.deps (calls, called_by, config_files) if present
    - NOTE: This function assumes all AgentSpec objects have a raw_block attribute containing the original YAML text - if this is missing, the output will have incomplete specs
    - NOTE: The yaml.dump() call requires pyyaml to be installed and imported at module level; this will raise ImportError if yaml is not available
    - NOTE: File is opened in write mode ("w"), which truncates existing files - use append mode or backup logic if incremental updates are needed
    - NOTE: No validation is performed on AgentSpec field contents; malformed data (e.g., lists with None values) will produce malformed markdown
    """
    print(f"[AGENTSPEC_CONTEXT] export_markdown: Takes a list of AgentSpec objects and serializes them to a human-readable markdown file at the specified Path | Iterates through each AgentSpec and writes formatted sections including: name, file location, what-it-does description, dependencies (calls, called_by, config_files), implementation rationale, critical guardrails, changelog entries, testing specifications, and performance characteristics | Handles optional fields gracefully by only writing sections that contain data (checking for presence of s.what, s.deps, s.why, etc.)")
    with out.open("w", encoding="utf-8") as f:
        f.write("# 🤖 Extracted Agent Specifications\n\n")
        f.write("**This document is auto-generated for AI agent consumption.**\n\n")
        f.write("---\n\n")
        
        for s in specs:
            f.write(f"## {s.name}\n\n")
            f.write(f"**Location:** `{s.filepath}:{s.lineno}`\n\n")
            
            if s.what:
                f.write(f"### What This Does\n\n{s.what}\n\n")
            
            if s.deps:
                f.write(f"### Dependencies\n\n")
                if 'calls' in s.deps:
                    f.write(f"**Calls:**\n")
                    for call in s.deps['calls']:
                        f.write(f"- `{call}`\n")
                    f.write("\n")
                
                if 'called_by' in s.deps:
                    f.write(f"**Called By:**\n")
                    for caller in s.deps['called_by']:
                        f.write(f"- `{caller}`\n")
                    f.write("\n")
                
                if 'config_files' in s.deps:
                    f.write(f"**Config Files:**\n")
                    for cfg in s.deps['config_files']:
                        f.write(f"- `{cfg}`\n")
                    f.write("\n")
            
            if s.why:
                f.write(f"### Why This Approach\n\n{s.why}\n\n")
            
            if s.guardrails:
                f.write(f"### ⚠️ Guardrails (CRITICAL)\n\n")
                for guard in s.guardrails:
                    f.write(f"- **{guard}**\n")
                f.write("\n")
            
            if s.changelog:
                f.write(f"### Changelog\n\n")
                for entry in s.changelog:
                    f.write(f"- {entry}\n")
                f.write("\n")
            
            if s.testing:
                f.write(f"### Testing\n\n")
                f.write(f"```yaml\n{yaml.dump(s.testing, default_flow_style=False)}```\n\n")
            
            if s.performance:
                f.write(f"### Performance Characteristics\n\n")
                for key, value in s.performance.items():
                    f.write(f"- **{key}:** {value}\n")
                f.write("\n")
            
            f.write(f"### Raw YAML Block\n\n")
            f.write(f"```yaml\n{s.raw_block}\n```\n\n")
            f.write("---\n\n")


def export_json(specs: List[AgentSpec], out: Path):
    """
    Brief one-line description.
    Serializes a list of AgentSpec objects to a JSON file for programmatic consumption and downstream processing.

    WHAT THIS DOES:
    - Iterates through each AgentSpec object in the provided list and converts it into a dictionary representation containing all documented metadata fields (name, line number, filepath, what/why/deps sections, guardrails, changelog, testing notes, performance notes, and raw docstring block).
    - Opens a file at the specified Path object in write mode with UTF-8 encoding and writes the list of dictionaries as formatted JSON with 2-space indentation for readability.
    - Returns None; side effect is file creation/overwrite at the target path.
    - No error handling: will raise FileNotFoundError if parent directories don't exist, PermissionError if insufficient write permissions, or TypeError if specs list contains non-AgentSpec objects or AgentSpec lacks expected attributes.
    - Assumes all AgentSpec attributes are JSON-serializable (strings, lists, dicts, None); will raise TypeError if any attribute contains non-serializable objects like custom classes or file handles.

    DEPENDENCIES:
    - Called by: [Inferred: CLI export command handlers, batch processing pipelines that need machine-readable spec output]
    - Calls: json.dump() (standard library), Path.open() (pathlib standard library)
    - Imports used: json (standard library), Path from pathlib (standard library), AgentSpec and List from typing/local modules
    - External services: Local filesystem only; no network or database dependencies

    WHY THIS APPROACH:
    - JSON format chosen for maximum compatibility with downstream tools, scripts, CI/CD pipelines, and other programming languages (vs. pickle which is Python-only, or CSV which doesn't handle nested structures well).
    - Dictionary construction loop is explicit and readable rather than using __dict__ or dataclass.asdict() to provide precise control over which fields are exported and their ordering, ensuring API stability if AgentSpec adds internal-only attributes in the future.
    - UTF-8 encoding explicitly specified for cross-platform compatibility and to handle any unicode characters in docstrings or filepaths.
    - 2-space indentation chosen as middle ground between file size and human readability (vs. compact single-line or verbose 4-space).
    - Raw file I/O with context manager used instead of json.dump(f=) for better error handling control if needed in future iterations.
    - No validation of specs list length, data types, or attribute existence - this is delegated to the caller to allow use in permissive/exploratory contexts, with failures fast and loud.

    CHANGELOG:
    - [Current date]: Initial implementation with full spec-to-dictionary mapping and UTF-8 JSON export.

    AGENT INSTRUCTIONS:
    - DO NOT remove fields from spec_dict without updating documentation and downstream consumers of this JSON format.
    - DO NOT change encoding from UTF-8 without explicit cross-platform testing.
    - DO NOT add try/except error handling without considering whether errors should bubble up or be logged at call site.
    - DO NOT change indentation parameter without documenting reasoning for file size vs. readability tradeoff.
    - ALWAYS ensure the output Path parent directory exists before calling this function (caller responsibility, not this function's).
    - ALWAYS preserve the raw_block field even if it seems redundant with other fields, as it is needed for round-trip reconstruction of original docstrings.
    - ALWAYS use Path.open() instead of open() string paths to maintain type safety and platform compatibility.
    - NOTE: This function will silently overwrite existing files at the target path with no backup - caller must handle preservation of previous versions if needed.
    - NOTE: All AgentSpec attributes must be JSON-serializable; if custom objects are added to AgentSpec in the future, this function will fail with cryptic TypeErrors unless those attributes are excluded or converted to primitives.
    """
    print(f"[AGENTSPEC_CONTEXT] export_json: Iterates through each AgentSpec object in the provided list and converts it into a dictionary representation containing all documented metadata fields (name, line number, filepath, what/why/deps sections, guardrails, changelog, testing notes, performance notes, and raw docstring block). | Opens a file at the specified Path object in write mode with UTF-8 encoding and writes the list of dictionaries as formatted JSON with 2-space indentation for readability. | Returns None; side effect is file creation/overwrite at the target path.")
    data = []
    for s in specs:
        spec_dict = {
            'name': s.name,
            'lineno': s.lineno,
            'filepath': s.filepath,
            'what': s.what,
            'deps': s.deps,
            'why': s.why,
            'guardrails': s.guardrails,
            'changelog': s.changelog,
            'testing': s.testing,
            'performance': s.performance,
            'raw_block': s.raw_block
        }
        data.append(spec_dict)
    
    with out.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def export_agent_context(specs: List[AgentSpec], out: Path):
    """
    Brief one-line description.
    Exports a collection of AgentSpec objects to a markdown file formatted as executable agent context with embedded print statements.

    WHAT THIS DOES:
    - Iterates through a list of AgentSpec objects and writes each specification to a markdown file at the provided Path
    - For each spec, writes a formatted section containing: the spec name and file location as a markdown header, executable Python print() statements that agents can run to display spec metadata, guardrail items with enumerated numbering, and the raw YAML block of the complete specification
    - The output file is UTF-8 encoded and is designed to be human-readable markdown while also containing executable Python code blocks that agents can parse and execute to understand function specifications
    - Returns None (writes side effect only)
    - Handles edge cases where s.what or s.guardrails may be None/empty by using conditional checks before writing their sections
    - Truncates the "what" field to 100 characters to keep output concise

    DEPENDENCIES:
    - Called by: [Likely called from CLI commands or documentation generation scripts in agentspec module, inferred from function name and public API pattern]
    - Calls: Path.open() (pathlib), str.write() (file I/O), len() (builtin), enumerate() (builtin)
    - Imports used: List (typing), AgentSpec (assumed from same module), Path (pathlib)
    - External services: Local filesystem only (writes to disk)

    WHY THIS APPROACH:
    - This function uses embedded print() statements within markdown code blocks because agents process both the markdown structure (for readability) and executable Python statements (for programmatic understanding of specifications)
    - The approach prioritizes agent readability by forcing explicit print calls that must be "read" by agents, rather than relying on implicit spec parsing
    - Markdown format was chosen for human reviewability while maintaining machine-readable YAML blocks at the end of each section
    - Truncation of s.what to 100 characters balances verbosity with output file size; alternatives like full text or 50-char limit were rejected
    - The conditional checks (if s.what, if s.guardrails) handle None/empty values gracefully rather than raising AttributeError or writing empty sections
    - Enumeration starting at 1 (not 0) for guardrails provides agent-friendly one-based indexing that matches human counting conventions
    - Performance is O(n*m) where n=number of specs and m=average guardrail count per spec; acceptable for typical use cases with <1000 specs

    WHY THIS APPROACH (continued):
    - The triple-dash separator ("---\n\n") between specs allows agents to parse sections independently if needed
    - Using raw_block preserves the original YAML exactly as written rather than re-serializing, maintaining formatting and comments from source

    CHANGELOG:
    - [2024-12-19]: Initial implementation - exports AgentSpec list to markdown with embedded print statements for agent consumption

    AGENT INSTRUCTIONS:
    - DO NOT modify the print() statement format or the "[AGENTSPEC]" prefix, as agents may be pattern-matching on these strings
    - DO NOT remove the conditional checks for s.what and s.guardrails, as some specs may have None values
    - DO NOT change the 100-character truncation length without considering downstream agent parsing
    - DO NOT reorder the sections (header, prints, full spec, separator) as this structure is relied upon for agent parsing
    - ALWAYS preserve the markdown header hierarchy (## for spec sections)
    - ALWAYS include the raw_block exactly as-is without modification
    - ALWAYS encode output as UTF-8
    - ALWAYS enumerate guardrails starting from 1, not 0
    - NOTE: This function assumes all AgentSpec objects have valid name, filepath, and lineno attributes; missing attributes will cause AttributeError
    - NOTE: File write operations are not atomic; if the process crashes mid-write, the output file will be corrupted
    - NOTE: The output file can grow quite large with many specs; consider pagination or splitting for >5000 specs
    - NOTE: Agents reading this output should treat print() statements as metadata instructions, not as code to execute in all contexts
    """
    print(f"[AGENTSPEC_CONTEXT] export_agent_context: Iterates through a list of AgentSpec objects and writes each specification to a markdown file at the provided Path | For each spec, writes a formatted section containing: the spec name and file location as a markdown header, executable Python print() statements that agents can run to display spec metadata, guardrail items with enumerated numbering, and the raw YAML block of the complete specification | The output file is UTF-8 encoded and is designed to be human-readable markdown while also containing executable Python code blocks that agents can parse and execute to understand function specifications")
    with out.open("w", encoding="utf-8") as f:
        f.write("# 🤖 AGENT CONTEXT: Function Specifications\n\n")
        f.write("**AGENTS: You MUST print() and read these specifications before modifying code.**\n\n")
        
        for s in specs:
            f.write(f"## SPEC: {s.name} ({s.filepath}:{s.lineno})\n\n")
            f.write(f"```python\n")
            f.write(f'print("[AGENTSPEC] Reading spec for {s.name}")\n')
            f.write(f'print("[AGENTSPEC] Location: {s.filepath}:{s.lineno}")\n')
            
            if s.what:
                f.write(f'print("[AGENTSPEC] What: {s.what[:100]}...")\n')
            
            if s.guardrails:
                f.write(f'print("[AGENTSPEC] GUARDRAILS ({len(s.guardrails)} items):")\n')
                for i, guard in enumerate(s.guardrails, 1):
                    f.write(f'print("[AGENTSPEC]   {i}. {guard}")\n')
            
            f.write(f"```\n\n")
            
            f.write(f"**Full Specification:**\n\n")
            f.write(f"```yaml\n{s.raw_block}\n```\n\n")
            f.write("---\n\n")


def run(target: str, fmt: str = "markdown") -> int:
    """
    Main extraction runner for CLI.
    
    Args:
        target: File or directory to extract from
        fmt: Output format ('markdown', 'json', 'agent-context')
    """
    path = Path(target)
    files = collect_python_files(path)
    all_specs: List[AgentSpec] = []

    for file in files:
        all_specs.extend(extract_from_file(file))

    if not all_specs:
        print("⚠️  No agent spec blocks found.")
        return 1

    # Determine output file
    if fmt == "json":
        out = Path("agent_specs.json")
        export_json(all_specs, out)
    elif fmt == "agent-context":
        out = Path("AGENT_CONTEXT.md")
        export_agent_context(all_specs, out)
    else:
        out = Path("agent_specs.md")
        export_markdown(all_specs, out)

    print(f"✅ Extracted {len(all_specs)} specs → {out}")
    return 0
