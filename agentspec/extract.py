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
    '''
    ---agentspec
    what: |
      Extracts the agentspec metadata block from a Python docstring by locating content between "---agentspec" and "---/agentspec" delimiters.

      Inputs: docstring (str) - a docstring that may contain an embedded agentspec YAML block
      Outputs: Optional[str] - the extracted and whitespace-normalized YAML content, or None if delimiters are absent or malformed

      Behavior:
      - Returns None immediately if docstring is falsy (empty, None)
      - Returns None if opening delimiter "---agentspec" is not found
      - Locates the opening delimiter and advances past it to find content start
      - Searches for closing delimiter "---/agentspec" after the opening delimiter
      - Returns None if closing delimiter is not found (prevents partial/malformed extraction)
      - Strips leading and trailing whitespace from extracted content before returning
      - Performs sequential validation with early-exit pattern for O(n) performance

      Edge cases:
      - Malformed delimiters (missing closing tag) safely return None rather than partial content
      - Multiple delimiter pairs: extracts only the first occurrence
      - Whitespace normalization handles inconsistent indentation in docstrings
        deps:
          calls:
            - docstring.find
            - len
            - strip
          imports:
            - agentspec.utils.collect_python_files
            - ast
            - dataclasses.asdict
            - dataclasses.dataclass
            - dataclasses.field
            - json
            - pathlib.Path
            - typing.Any
            - typing.Dict
            - typing.List
            - typing.Optional
            - yaml


    why: |
      String search via find() is faster than regex for literal delimiter matching and avoids regex compilation overhead. The early-exit validation pattern (docstring exists → opening delimiter → closing delimiter) provides both O(n) performance and graceful degradation when delimiters are missing or incomplete. Explicit, unambiguous delimiters ("---agentspec" / "---/agentspec") are unlikely to appear accidentally in docstrings, reducing false positives. Returning None on any validation failure allows the extraction pipeline to degrade gracefully without raising exceptions, enabling robust batch processing of heterogeneous docstrings.

    guardrails:
      - DO NOT modify delimiter strings without updating all docstring generation code and documentation, as delimiters are the contract between generators and extractors
      - DO NOT remove closing delimiter validation, as it prevents extraction of incomplete or malformed blocks that could corrupt downstream YAML parsing
      - ALWAYS return None on any validation failure to support graceful pipeline degradation and allow callers to handle missing metadata
      - ALWAYS preserve .strip() to normalize whitespace in extracted blocks, ensuring consistent YAML parsing regardless of docstring indentation style
      - DO NOT use regex for delimiter matching without performance benchmarking, as string search is simpler and faster for literal patterns

        changelog:
          - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate"
          - "-    """Extract the agentspec block from a docstring.""""
          - "- 2025-10-29: Enhanced extract.py with full YAML parsing and agent-context format"
          - "-        return """
          - "-        return """
          - "-    return docstring[start:end].strip() if end != -1 else """
          - "- 2025-10-29: Add agent spec extraction and export functionality"
        ---/agentspec
    '''
    if not docstring:
        return None
    if "---agentspec" not in docstring:
        return None
    start = docstring.find("---agentspec") + len("---agentspec")
    end = docstring.find("---/agentspec")
    return docstring[start:end].strip() if end != -1 else None


def _parse_yaml_block(block: str) -> Optional[Dict[str, Any]]:
    '''
    ---agentspec
    what: |
      Safely parses a YAML block string into a Python dictionary or other valid YAML structure.

      Accepts any string input and attempts to parse it using yaml.safe_load(). Returns the parsed result (dict, list, scalar, or None) on success. Returns None silently if the input contains invalid YAML syntax or raises a yaml.YAMLError during parsing.

      Handles edge cases: empty strings, whitespace-only strings, and malformed YAML all return None without raising exceptions. Valid YAML that parses to non-dict types (lists, strings, integers, booleans, None) is returned as-is; callers are responsible for type validation before treating results as dictionaries.
        deps:
          calls:
            - yaml.safe_load
          imports:
            - agentspec.utils.collect_python_files
            - ast
            - dataclasses.asdict
            - dataclasses.dataclass
            - dataclasses.field
            - json
            - pathlib.Path
            - typing.Any
            - typing.Dict
            - typing.List
            - typing.Optional
            - yaml


    why: |
      Uses yaml.safe_load() instead of yaml.load() to prevent code injection attacks when parsing YAML from untrusted sources such as docstrings and code comments. The fail-silent pattern (returning None on parse errors) allows graceful degradation when optional metadata is missing or malformed, avoiding exception propagation and enabling callers to distinguish between "no YAML found" and "YAML found but invalid" through a single None return value.

    guardrails:
      - DO NOT use yaml.load() or yaml.unsafe_load()—these are security vulnerabilities that allow arbitrary code execution from untrusted YAML input
      - DO NOT remove the try/except block or convert to exception-raising behavior—silent failure is intentional for optional metadata handling
      - DO NOT return empty dict {} or False on parse failure—always return None for caller clarity and type consistency
      - ALWAYS use yaml.safe_load() specifically to maintain security posture
      - NOTE: Type hint declares Dict return but yaml.safe_load() can return list, string, int, bool, or None—callers must validate the actual type before accessing dict keys

        changelog:
          - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate"
          - "-    """Parse YAML from agentspec block.""""
          - "- 2025-10-29: Enhanced extract.py with full YAML parsing and agent-context format"
          - "-    return docstring[start:end].strip() if end != -1 else """
          - "- 2025-10-29: Add agent spec extraction and export functionality"
        ---/agentspec
    '''
    try:
        return yaml.safe_load(block)
    except yaml.YAMLError:
        return None


class AgentSpecExtractor(ast.NodeVisitor):
    def __init__(self, filepath: str):
        """
        ---agentspec
        what: |
          Initializes an AgentSpecExtractor instance with a file path and prepares an empty container for accumulated specifications.

          - Accepts a filepath string parameter and stores it as self.filepath for deferred file parsing
          - Initializes self.specs as an empty List[AgentSpec] to accumulate extracted agent specifications during processing
          - Performs no file I/O, validation, or parsing at initialization time; all such operations are deferred to dedicated extraction methods
          - Enables downstream methods to append AgentSpec objects to self.specs without null-checking or type conversion

          Inputs:
          - filepath (str): Path to a Python file or directory containing agentspec YAML blocks to extract

          Outputs:
          - None; side effects are instance attribute assignment (self.filepath, self.specs)

          Edge cases:
          - No validation of filepath existence or format occurs during __init__; invalid paths are caught later during file I/O operations
          - Empty specs list is intentional and expected; extraction methods populate it incrementally
            deps:
              imports:
                - agentspec.utils.collect_python_files
                - ast
                - dataclasses.asdict
                - dataclasses.dataclass
                - dataclasses.field
                - json
                - pathlib.Path
                - typing.Any
                - typing.Dict
                - typing.List
                - typing.Optional
                - yaml


        why: |
          Lazy initialization separates concerns and improves error handling by deferring expensive or failure-prone operations (file I/O, parsing, validation) to dedicated methods rather than the constructor.

          Pre-allocating self.specs as an empty list avoids null-checking and type-narrowing logic in downstream append operations, reducing cognitive load and potential runtime errors.

          Type hints (List[AgentSpec]) enable IDE autocompletion, static type checking, and self-documenting code that clarifies the expected structure of accumulated data.

          Storing filepath as an instance attribute allows extraction methods to reference it without requiring it as a parameter, simplifying method signatures and enabling stateful processing across multiple method calls.

        guardrails:
          - DO NOT add file I/O operations (open, read, Path.read_text) in __init__; keep initialization pure and defer I/O to dedicated methods to enable better error handling and testability
          - DO NOT change self.specs to None or a non-list type; downstream extraction methods assume it is a mutable List and call append() on it
          - DO NOT omit self.filepath assignment; extraction methods depend on this attribute to locate and parse the target file
          - DO NOT initialize self.specs to None or skip initialization; this breaks extraction methods that expect a pre-allocated list and would require null-checking elsewhere
          - DO NOT validate filepath format or existence in __init__; validation belongs in dedicated methods that can provide context-specific error messages

            changelog:
              - "- no git history available"
            ---/agentspec
        """
        self.filepath = filepath
        self.specs: List[AgentSpec] = []

    def visit_FunctionDef(self, node):
        """
        ---agentspec
        what: |
          Implements the ast.NodeVisitor pattern to extract function metadata from AST FunctionDef nodes.

          Behavior:
          - Calls self._extract(node) to parse and accumulate function metadata including name, parameters, decorators, docstrings, and type hints from the current FunctionDef node
          - Calls self.generic_visit(node) to recursively traverse and process all child nodes (nested functions, classes, and other AST children)
          - Returns None per ast.NodeVisitor protocol; accumulates extracted data via side effects on the visitor instance

          Inputs:
          - node: an ast.FunctionDef node representing a function definition in the AST

          Outputs:
          - None (side-effect based; extracted metadata stored in visitor instance state)

          Edge cases:
          - Nested functions are processed recursively; extraction order is parent-first
          - Decorated functions have decorators extracted alongside function signature
          - Functions with type hints and docstrings are fully captured
          - Empty or malformed function definitions are handled by _extract() error handling
            deps:
              calls:
                - self._extract
                - self.generic_visit
              imports:
                - agentspec.utils.collect_python_files
                - ast
                - dataclasses.asdict
                - dataclasses.dataclass
                - dataclasses.field
                - json
                - pathlib.Path
                - typing.Any
                - typing.Dict
                - typing.List
                - typing.Optional
                - yaml


        why: |
          The visitor pattern is the standard Python idiom for AST traversal, providing clean separation between extraction logic and tree traversal mechanics.
          Processing the parent node via _extract() before recursing via generic_visit() ensures proper extraction order and maintains context availability for nested structures.
          This approach is maintainable, extensible, and follows ast.NodeVisitor conventions for compatibility with Python's AST infrastructure.

        guardrails:
          - DO NOT remove the generic_visit(node) call; it breaks traversal of nested functions, classes, and other child nodes, resulting in incomplete metadata extraction
          - DO NOT reorder _extract() and generic_visit() calls; reversing them breaks the extraction dependency chain and may cause context loss for nested structures
          - ALWAYS preserve the method signature as visit_FunctionDef(self, node) for ast.NodeVisitor compatibility; renaming or changing parameters breaks the visitor dispatch mechanism
          - DO NOT modify node in-place before calling generic_visit(); preserve AST integrity for recursive processing

            changelog:
              - "- no git history available"
            ---/agentspec
        """
        self._extract(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """
        ---agentspec
        what: |
          Visitor callback for async function definitions that extracts metadata and traverses child nodes.

          Behavior:
          - Calls self._extract(node) to collect async function metadata including name, arguments, decorators, docstrings, and type hints
          - Calls self.generic_visit(node) to recursively process nested structures within the async function body
          - Handles async generators and decorated async functions uniformly

          Inputs:
          - node: an ast.AsyncFunctionDef node representing an async function definition

          Outputs:
          - Side effect: populates internal state via _extract() with async function metadata
          - Side effect: recursively visits all child nodes in the AST subtree

          Edge cases:
          - Async generators (async def with yield) are processed identically to regular async functions
          - Decorated async functions have decorators extracted as part of node metadata
          - Nested async functions within async functions are discovered via recursive generic_visit()
            deps:
              calls:
                - self._extract
                - self.generic_visit
              imports:
                - agentspec.utils.collect_python_files
                - ast
                - dataclasses.asdict
                - dataclasses.dataclass
                - dataclasses.field
                - json
                - pathlib.Path
                - typing.Any
                - typing.Dict
                - typing.List
                - typing.Optional
                - yaml


        why: |
          Follows the ast.NodeVisitor double-dispatch pattern for clean separation of node-type-specific logic.
          Reuses _extract() logic across both FunctionDef and AsyncFunctionDef node types to avoid duplication.
          The generic_visit() call is critical for discovering nested functions, classes, and other definitions within the async function body; omitting it breaks recursive traversal and causes nested definitions to be missed.
          Calling _extract() before generic_visit() ensures metadata extraction completes before descending into child nodes, maintaining proper traversal order.

        guardrails:
          - DO NOT remove the generic_visit() call; it breaks recursive traversal and prevents discovery of nested functions, classes, and other definitions within the async function body
          - DO NOT alter the method signature; it must accept (self, node) to comply with ast.NodeVisitor double-dispatch pattern
          - ALWAYS call _extract() before generic_visit() to ensure metadata extraction completes before descending into child nodes
          - DO NOT assume the node has specific attributes without checking; rely on _extract() to handle attribute validation

            changelog:
              - "- no git history available"
            ---/agentspec
        """
        self._extract(node)
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """
        ---agentspec
        what: |
          Extracts class metadata (name, decorators, docstring, line numbers) from an AST ClassDef node and recursively visits all child nodes in depth-first pre-order traversal.

          Inputs:
          - node: An ast.ClassDef node representing a class definition

          Outputs:
          - Side effect: Populates internal state via _extract() with class metadata
          - Side effect: Recursively processes all child nodes (methods, nested classes, attributes) via generic_visit()

          Behavior:
          - Calls _extract(node) to capture class-level metadata before recursion
          - Calls generic_visit(node) to traverse all child nodes in the AST
          - Maintains depth-first, pre-order traversal order (parent processed before children)
          - Integrates with ast.NodeVisitor dispatch mechanism via method naming convention
            deps:
              calls:
                - self._extract
                - self.generic_visit
              imports:
                - agentspec.utils.collect_python_files
                - ast
                - dataclasses.asdict
                - dataclasses.dataclass
                - dataclasses.field
                - json
                - pathlib.Path
                - typing.Any
                - typing.Dict
                - typing.List
                - typing.Optional
                - yaml


        why: |
          The visitor pattern is the standard Python idiom for AST traversal, eliminating manual recursion boilerplate and leveraging ast.NodeVisitor's built-in dispatch. Pre-order traversal (extract before recursing) ensures parent metadata is collected before child metadata, enabling proper hierarchical organization. Separation of concerns between _extract() (metadata collection) and generic_visit() (tree traversal) improves maintainability and clarity of intent.

        guardrails:
          - DO NOT rename this method—the name visit_ClassDef is required by ast.NodeVisitor's visit_<NodeType> dispatch mechanism and renaming breaks automatic node routing
          - DO NOT remove the generic_visit() call—omitting it prevents child nodes from being visited, resulting in incomplete AST traversal and missing nested classes/methods
          - DO NOT call _extract() after generic_visit()—this reverses traversal order to post-order, causing children to be processed before parents and breaking hierarchical metadata collection
          - DO NOT modify the method signature—ast.NodeVisitor expects exactly def visit_ClassDef(self, node):
          - ALWAYS call _extract() before generic_visit() to maintain pre-order traversal semantics

            changelog:
              - "- no git history available"
            ---/agentspec
        """
        self._extract(node)
        self.generic_visit(node)

    def _extract(self, node):
        '''
        ---agentspec
        what: |
          Extracts agent specification metadata from AST nodes by parsing YAML-formatted docstrings into AgentSpec objects.

          - Retrieves docstring via ast.get_docstring() and extracts YAML block; returns early if none found
          - Creates fallback spec from raw docstring if YAML block absent; parses YAML into structured AgentSpec fields
          - Appends spec to self.specs with node metadata (name, lineno, filepath) and both raw_block and parsed_data preserved
          - Handles edge cases: missing docstrings, malformed YAML, empty blocks, and multi-paragraph fallback text
          - Extracts structured fields (what, deps, why, guardrails, changelog, testing, performance) from parsed YAML when available
          - Converts string fields to stripped strings; preserves dictionaries and lists as-is from YAML parse result
            deps:
              calls:
                - AgentSpec
                - _extract_block
                - _parse_yaml_block
                - ast.get_docstring
                - doc.split
                - doc.splitlines
                - p.strip
                - parsed.get
                - specs.append
                - str
                - strip
              imports:
                - agentspec.utils.collect_python_files
                - ast
                - dataclasses.asdict
                - dataclasses.dataclass
                - dataclasses.field
                - json
                - pathlib.Path
                - typing.Any
                - typing.Dict
                - typing.List
                - typing.Optional
                - yaml


        why: |
          ast.get_docstring() handles docstring detection consistently across all AST node types (FunctionDef, ClassDef, etc.).
          Early return and conditional field population prevent empty specs and crashes on malformed YAML, improving robustness.
          Dual storage of raw_block and parsed_data preserves original documentation for debugging, audit trails, and recovery from parse failures.
          Fallback mechanism ensures extraction succeeds even when YAML formatting is absent, allowing graceful degradation to basic docstring capture.
          Explicit field extraction with .strip() and .get() provides null safety and prevents None values from propagating into spec fields.

        guardrails:
          - DO NOT modify conditional structure without ensuring null safety for all dictionary key accesses; use .get() with defaults
          - DO NOT remove early return when block is empty; prevents unnecessary allocation and maintains performance
          - DO NOT change str(...).strip() on string fields without understanding None→'' conversion semantics
          - DO NOT skip node metadata extraction (name, lineno, filepath); source mapping is critical for traceability
          - DO NOT store only parsed_data without raw_block; dual storage maintains audit trail and enables recovery
          - DO NOT reimplement YAML extraction inline; always call _extract_block() and _parse_yaml_block() to maintain separation of concerns
          - DO NOT assume parsed dictionary keys exist; always use .get() with appropriate defaults ('' for strings, {} for dicts, [] for lists)

            changelog:
              - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate"
              - "-    """Extract the agentspec block from a docstring.""""
              - "- 2025-10-29: Enhanced extract.py with full YAML parsing and agent-context format"
              - "-        return """
              - "-        return """
              - "-    return docstring[start:end].strip() if end != -1 else """
              - "- 2025-10-29: Add agent spec extraction and export functionality"
            ---/agentspec
        '''
        doc = ast.get_docstring(node)
        block = _extract_block(doc)

        if not block:
            # Fallback: treat raw docstring as a basic spec so extraction works
            if not doc:
                return
            spec = AgentSpec(
                name=node.name,
                lineno=node.lineno,
                filepath=self.filepath,
                raw_block=doc,
                parsed_data={},
            )
            # Use the first non-empty paragraph or line as 'what'
            parts = [p.strip() for p in doc.split("\n\n") if p.strip()] or [p.strip() for p in doc.splitlines() if p.strip()]
            spec.what = parts[0] if parts else ""
            self.specs.append(spec)
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
    '''
    ---agentspec
    what: |
      Extracts all AgentSpec definitions from a Python source file by parsing its Abstract Syntax Tree (AST).

      Reads the file at the given Path with UTF-8 encoding, parses it into an AST representation, and visits all nodes using an AgentSpecExtractor visitor to collect AgentSpec objects. Returns a list of all AgentSpec instances found in the file.

      On any exception—including file I/O errors, syntax errors, or extraction failures—prints a warning message to stderr and returns an empty list instead of raising. This allows graceful degradation when processing unknown or third-party code.

      Input: path (Path object pointing to a Python source file)
      Output: List[AgentSpec] containing zero or more extracted specifications

      Edge cases:
      - Non-existent files: caught by path.read_text(), returns empty list with warning
      - Syntax errors in Python source: caught by ast.parse(), returns empty list with warning
      - Files with no AgentSpec definitions: returns empty list (no warning, normal case)
      - Encoding issues: UTF-8 decode errors caught, returns empty list with warning
        deps:
          calls:
            - AgentSpecExtractor
            - ast.parse
            - extractor.visit
            - path.read_text
            - print
            - str
          imports:
            - agentspec.utils.collect_python_files
            - ast
            - dataclasses.asdict
            - dataclasses.dataclass
            - dataclasses.field
            - json
            - pathlib.Path
            - typing.Any
            - typing.Dict
            - typing.List
            - typing.Optional
            - yaml


    why: |
      AST parsing is the most reliable approach for extracting AgentSpec definitions because it handles complex Python syntax robustly—decorators, nested class/function definitions, multi-line constructs, and string literals are all properly represented in the AST without fragile regex or text-based heuristics.

      Graceful error handling (try/except returning empty list) enables batch processing across multiple files without halting on problematic input. This is essential for tools that scan entire codebases where some files may be malformed, incomplete, or in non-standard formats.

      Empty list return semantics allow simple list concatenation patterns (e.g., `all_specs = [] ; for file in files: all_specs.extend(extract_from_file(file))`) without special-casing None or exception handling at the call site.

      The visitor pattern via AgentSpecExtractor.visit() provides clean separation of concerns: parsing logic is isolated in the extractor class, making the extraction logic testable and reusable.

    guardrails:
      - DO NOT remove the try/except wrapper or convert to raising exceptions—this breaks batch processing and causes the entire extraction pipeline to fail on a single malformed file
      - DO NOT change encoding from "utf-8" without verifying platform compatibility across Windows, macOS, and Linux; UTF-8 is the safe default for modern Python codebases
      - DO NOT modify the return type from List[AgentSpec]—downstream code depends on the empty list semantics to distinguish "no specs found" from "error occurred"
      - ALWAYS preserve str(path) conversions when passing Path objects to ast.parse() and in warning messages, as ast.parse() expects a string filename for error reporting
      - ALWAYS maintain the visitor pattern via AgentSpecExtractor.visit() call—do not inline extraction logic to preserve modularity and testability
      - DO NOT suppress the warning print statement—it provides essential debugging visibility when files fail to parse in batch operations

        changelog:
          - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate"
          - "-    """Extract all agentspecs from a Python file.""""
          - "- 2025-10-29: Enhanced extract.py with full YAML parsing and agent-context format"
          - "-    except Exception:"
          - "- 2025-10-29: Add agent spec extraction and export functionality"
        ---/agentspec
    '''
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
    '''
    ---agentspec
    what: |
      Serializes a list of AgentSpec objects to a formatted markdown file for AI agent consumption.

      For each spec, writes a markdown section containing:
      - Spec name and source location (filepath:lineno)
      - What/Why/Guardrails narrative sections (if present)
      - Dependencies breakdown (calls, called_by, config_files as separate lists)  - Testing configuration as YAML block (if present)
      - Performance characteristics as key-value pairs (if present)
      - Raw YAML block preserving the original spec data
      - Separator line between specs

      Includes auto-generated header ("🤖 Extracted Agent Specifications") and metadata note at document start.
      Conditionally renders only non-empty optional fields to prevent malformed output.
      Uses UTF-8 encoding explicitly via Path.open().
        deps:
          calls:
            - f.write
            - out.open
            - performance.items
            - yaml.dump
          imports:
            - agentspec.utils.collect_python_files
            - ast
            - dataclasses.asdict
            - dataclasses.dataclass
            - dataclasses.field
            - json
            - pathlib.Path
            - typing.Any
            - typing.Dict
            - typing.List
            - typing.Optional
            - yaml


    why: |
      Markdown is version-control-friendly, GitHub-renderable, and directly parseable by AI agents without custom deserialization.
      Raw YAML blocks preserve spec data alongside formatted prose, enabling dual consumption (human-readable narrative + machine-parseable structure).
      Conditional field rendering prevents empty sections that would clutter output or confuse downstream parsers.
      Explicit UTF-8 encoding ensures consistent handling across platforms and CI/CD environments.
      Hierarchical heading structure (##, ###) enables outline-based navigation and programmatic section extraction.

    guardrails:
      - DO NOT modify heading hierarchy (##, ###) without updating downstream parsers that depend on these markers for section extraction
      - DO NOT remove the auto-generated header or raw YAML blocks; AI agents depend on these markers for document structure validation
      - DO NOT change UTF-8 encoding without coordinating with all consumers; assume UTF-8 is mandatory
      - DO NOT omit the raw YAML block for any spec; it is the canonical representation for machine consumption
      - DO NOT render empty dependency, changelog, testing, or performance sections; always check field presence first
      - DO NOT alter the separator line format (---) between specs; parsers may depend on this delimiter

        changelog:
          - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate"
          - "-    """Export to verbose markdown format for agent consumption.""""
          - "- 2025-10-29: Enhanced extract.py with full YAML parsing and agent-context format"
          - "-        f.write("# Extracted Agent Specs\n\n")"
          - "-            f.write(f"## {s.name} ({s.filepath}:{s.lineno})\n\n")"
          - "-            f.write("```yaml\n" + s.block + "\n```\n\n---\n\n")"
          - "- 2025-10-29: Add agent spec extraction and export functionality"
        ---/agentspec
    '''
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
    '''
    ---agentspec
    what: |
      Serializes a list of AgentSpec objects to a JSON file for downstream consumption.

      For each AgentSpec in the input list, extracts all metadata fields (name, lineno, filepath, what, deps, why, guardrails, changelog, testing, performance, raw_block) into a dictionary. Collects all dictionaries into a single list and writes to the specified Path as formatted JSON with 2-space indentation and UTF-8 encoding.

      Inputs: specs (List[AgentSpec]) – collection of agent specifications; out (Path) – target file path for JSON output.

      Outputs: None (side effect: writes JSON file to disk).

      Edge cases: Empty specs list produces valid empty JSON array; raw_block field may contain multi-line strings that are properly escaped by json.dump.
        deps:
          calls:
            - data.append
            - json.dump
            - out.open
          imports:
            - agentspec.utils.collect_python_files
            - ast
            - dataclasses.asdict
            - dataclasses.dataclass
            - dataclasses.field
            - json
            - pathlib.Path
            - typing.Any
            - typing.Dict
            - typing.List
            - typing.Optional
            - yaml


    why: |
      JSON format ensures broad compatibility with downstream tools, CI/CD pipelines, and non-Python consumers without requiring YAML or custom parsing. Explicit field-by-field mapping provides API stability if AgentSpec gains internal-only attributes in the future, decoupling the export format from the dataclass structure. UTF-8 encoding and 2-space indentation balance readability with cross-platform portability.

    guardrails:
      - DO NOT remove fields from spec_dict without updating all downstream JSON consumers, as this breaks contract with tools that depend on the schema.
      - DO NOT change encoding without cross-platform testing, as UTF-8 is assumed by downstream processors.
      - ALWAYS preserve raw_block field for round-trip docstring reconstruction and audit trails.
      - ALWAYS ensure parent directory of out exists before calling; this function does not create intermediate directories (caller responsibility).

        changelog:
          - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate"
          - "-    """Export to JSON for programmatic consumption.""""
          - "- 2025-10-29: Enhanced extract.py with full YAML parsing and agent-context format"
          - "-        json.dump([asdict(s) for s in specs], f, indent=2)"
          - "- 2025-10-29: Add agent spec extraction and export functionality"
        ---/agentspec
    '''
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
    ---agentspec
    what: |
      Exports a list of AgentSpec objects to a markdown file optimized for agent consumption. For each spec, writes a formatted section containing: a markdown header with spec name and file location, executable Python print() statements that agents can run to display metadata, guardrail items with one-based enumeration, and the raw YAML or docstring block. The "what" field is truncated to 100 characters; None/empty values for "what" and "guardrails" are handled gracefully with conditional checks. Output is UTF-8 encoded with triple-dash separators between specs. Returns None (side effect: writes file to disk).
        deps:
          calls:
            - enumerate
            - f.write
            - len
            - out.open
          imports:
            - agentspec.utils.collect_python_files
            - ast
            - dataclasses.asdict
            - dataclasses.dataclass
            - dataclasses.field
            - json
            - pathlib.Path
            - typing.Any
            - typing.Dict
            - typing.List
            - typing.Optional
            - yaml


    why: |
      Embedded print() statements allow agents to parse both markdown structure (human-readable) and executable Python code (programmatic understanding) from a single file. Markdown format preserves readability for humans while maintaining machine-readable YAML blocks. One-based guardrail indexing matches human counting conventions rather than zero-based programming conventions, improving agent interpretation. Truncating "what" to 100 characters balances verbosity with output file size. Conditional checks prevent AttributeError when specs have None values. Triple-dash separators enable independent section parsing by agents. Preserving raw_block exactly as-is maintains original formatting and comments from source rather than re-serializing.

    guardrails:
      - DO NOT modify print() statement format or "[AGENTSPEC]" prefix; agents pattern-match on these strings for reliable parsing
      - DO NOT remove conditional checks for s.what and s.guardrails; some specs may have None or empty values that would cause write failures
      - DO NOT change the 100-character truncation length without considering downstream agent parsing logic that may depend on consistent output size
      - DO NOT reorder sections (header, prints, full spec, separator); agent parsing depends on this exact structure
      - DO NOT re-serialize raw_block through YAML/JSON; preserve it exactly as-is to maintain original formatting and comments
      - ALWAYS preserve markdown header hierarchy (## for spec sections) and raw_block exactly as written
      - ALWAYS encode output as UTF-8 and enumerate guardrails starting from 1, not 0
      - ALWAYS include the triple-dash separator ("---\n\n") between specs for section demarcation
      - NOTE: Function assumes all AgentSpec objects have valid name, filepath, and lineno attributes; missing attributes will cause AttributeError
      - NOTE: File write operations are not atomic; process crash mid-write will corrupt output file
      - NOTE: Output file can grow large with many specs; consider pagination or splitting for >5000 specs
      - NOTE: Agents should treat print() statements as metadata instructions, not as code to execute in all contexts

        changelog:
          - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features"
          - "- Iterates through a list of AgentSpec objects and writes each specification to a markdown file at the provided Path"
          - "- For each spec, writes a formatted section containing: the spec name and file location as a markdown header, executable Python print() statements that agents can run to display spec metadata, guardrail items with enumerated numbering, and the raw YAML block of the complete specification"
          - "- The output file is UTF-8 encoded and is designed to be human-readable markdown while also containing executable Python code blocks that agents can parse and execute to understand function specifications"
          - "- Returns None (writes side effect only)"
          - "- Handles edge cases where s.what or s.guardrails may be None/empty by using conditional checks before writing their sections"
          - "- Truncates the "what" field to 100 characters to keep output concise"
          - "- Called by: [Likely called from CLI commands or documentation generation scripts in agentspec module, inferred from function name and public API pattern]"
          - "- Calls: Path.open() (pathlib), str.write() (file I/O), len() (builtin), enumerate() (builtin)"
          - "- Imports used: List (typing), AgentSpec (assumed from same module), Path (pathlib)"
          - "- External services: Local filesystem only (writes to disk)"
          - "- This function uses embedded print() statements within markdown code blocks because agents process both the markdown structure (for readability) and executable Python statements (for programmatic understanding of specifications)"
          - "- The approach prioritizes agent readability by forcing explicit print calls that must be "read" by agents, rather than relying on implicit spec parsing"
          - "- Markdown format was chosen for human reviewability while maintaining machine-readable YAML blocks at the end of each section"
          - "- Truncation of s.what to 100 characters balances verbosity with output file size; alternatives like full text or 50-char limit were rejected"
          - "- The conditional checks (if s.what, if s.guardrails) handle None/empty values gracefully rather than raising AttributeError or writing empty sections"
          - "- Enumeration starting at 1 (not 0) for guardrails provides agent-friendly one-based indexing that matches human counting conventions"
          - "- Performance is O(n*m) where n=number of specs and m=average guardrail count per spec; acceptable for typical use cases with <1000 specs"
          - "- The triple-dash separator ("---\n\n") between specs allows agents to parse sections independently if needed"
          - "- Using raw_block preserves the original YAML exactly as written rather than re-serializing, maintaining formatting and comments from source"
          - "- [2024-12-19]: Initial implementation - exports AgentSpec list to markdown with embedded print statements for agent consumption"
          - "- DO NOT modify the print() statement format or the "[AGENTSPEC]" prefix, as agents may be pattern-matching on these strings"
          - "- DO NOT remove the conditional checks for s.what and s.guardrails, as some specs may have None values"
          - "- DO NOT change the 100-character truncation length without considering downstream agent parsing"
          - "- DO NOT reorder the sections (header, prints, full spec, separator) as this structure is relied upon for agent parsing"
          - "- ALWAYS preserve the markdown header hierarchy (## for spec sections)"
          - "- ALWAYS include the raw_block exactly as-is without modification"
          - "- ALWAYS encode output as UTF-8"
          - "- ALWAYS enumerate guardrails starting from 1, not 0"
          - "- NOTE: This function assumes all AgentSpec objects have valid name, filepath, and lineno attributes; missing attributes will cause AttributeError"
          - "- NOTE: File write operations are not atomic; if the process crashes mid-write, the output file will be corrupted"
          - "- NOTE: The output file can grow quite large with many specs; consider pagination or splitting for >5000 specs"
          - "- NOTE: Agents reading this output should treat print() statements as metadata instructions, not as code to execute in all contexts"
          - "-            f.write(f"**Full Specification:**\n\n")"
          - "-            f.write(f"```yaml\n{s.raw_block}\n```\n\n")"
          - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate"
          - "-    Export in a format optimized for injecting into agent context."
          - "-    Extremely verbose, includes print() statements."
          - "- 2025-10-29: Enhanced extract.py with full YAML parsing and agent-context format"
          - "-        json.dump([asdict(s) for s in specs], f, indent=2)"
          - "- 2025-10-29: Add agent spec extraction and export functionality"
        ---/agentspec
    """
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
            
            if s.parsed_data:
                f.write(f"**Full Specification (YAML):**\n\n")
                f.write(f"```yaml\n{s.raw_block}\n```\n\n")
            else:
                f.write(f"**Full Specification (Raw Docstring):**\n\n")
                f.write(f"```\n{s.raw_block}\n```\n\n")
            f.write("---\n\n")


def run(target: str, fmt: str = "markdown") -> int:
    """
    ---agentspec
    what: |
      Extracts agent specification blocks from Python files in a target directory and exports them in the specified format.

      Behavior:
      - Accepts a target path (file or directory) and optional format string (markdown, json, or agent-context)
      - Collects all Python files from the target using collect_python_files, which handles path validation and .gitignore/.venv filtering
      - Iterates through collected files and extracts AgentSpec objects from embedded YAML blocks and docstrings using extract_from_file
      - Aggregates all extracted specs into a single list
      - Exports aggregated specs to a format-specific output file: agent_specs.json, AGENT_CONTEXT.md, or agent_specs.md (default)
      - Returns 0 on successful export, 1 if no specs are found

      Inputs:
      - target: string path to file or directory containing Python source code
      - fmt: output format string; one of "markdown" (default), "json", or "agent-context"

      Outputs:
      - Exit code: 0 for success, 1 if no specs found
      - Side effect: writes formatted specs to filesystem (agent_specs.json, AGENT_CONTEXT.md, or agent_specs.md)
      - Console output: status message with spec count and output file path

      Edge cases:
      - Empty target directory or no Python files: returns 1 with warning message
      - Invalid format string: defaults to markdown export
      - Non-existent target path: handled by collect_python_files validation
        deps:
          calls:
            - Path
            - all_specs.extend
            - collect_python_files
            - export_agent_context
            - export_json
            - export_markdown
            - extract_from_file
            - len
            - print
          imports:
            - agentspec.utils.collect_python_files
            - ast
            - dataclasses.asdict
            - dataclasses.dataclass
            - dataclasses.field
            - json
            - pathlib.Path
            - typing.Any
            - typing.Dict
            - typing.List
            - typing.Optional
            - yaml


    why: |
      Centralizes spec extraction and export logic into a single CLI entry point, enabling users to batch-process Python codebases and generate machine-readable spec documentation.
      Format abstraction (markdown/json/agent-context) allows flexible output without modifying core extraction logic.
      Exit code convention (0/1) ensures proper shell integration and scripting compatibility.
      Aggregation pattern (extend all_specs) scales efficiently across large codebases.

    guardrails:
      - DO NOT assume target path exists; collect_python_files handles validation and raises appropriate errors
      - DO NOT export if specs list is empty; always return 1 and print warning to prevent silent failures
      - ALWAYS return an exit code (0 or 1) for proper CLI integration and shell scripting
      - DO NOT modify or filter specs during aggregation; preserve all extracted specs as-is
      - DO NOT assume format string is valid; default to markdown for unrecognized formats to prevent crashes

        changelog:
          - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features"
          - "-        print("⚠️  No agent spec blocks found.")"
          - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate"
          - "-    files = [path] if path.is_file() else list(path.rglob("*.py"))"
          - "- 2025-10-29: Enhanced extract.py with full YAML parsing and agent-context format"
          - "-        print("⚠️ No agent spec blocks found.")"
          - "-    out = Path(f"agent_specs.{ 'json' if fmt == 'json' else 'md'}")"
          - "-    print(f"✅ Exported {len(all_specs)} specs → {out}")"
          - "- 2025-10-29: Add agent spec extraction and export functionality"
        ---/agentspec
    """
    path = Path(target)
    files = collect_python_files(path)
    all_specs: List[AgentSpec] = []

    for file in files:
        all_specs.extend(extract_from_file(file))

    if not all_specs:
        print("⚠️  No agent spec blocks or docstrings found.")
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
