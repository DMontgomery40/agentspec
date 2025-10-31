"""
agentspec.langs
------------------
Language adapter registry and protocol for multi-language agentspec support.

Provides a pluggable architecture for adding support for new languages (Python, JavaScript, etc.)
without modifying core processing logic.

---agentspec
what: |
  Registry-based language adapter system enabling agentspec to support multiple languages.
  
  The module maintains a global registry of LanguageAdapter implementations, keyed by
  file extension. It provides two main APIs:
  - LanguageRegistry.get_by_extension(ext): Get adapter for a file extension
  - LanguageRegistry.get_by_path(path): Get adapter for a file path
  
  All adapters implement the LanguageAdapter protocol, which defines how to:
  - Discover source files of a language
  - Parse source files into AST-like structures
  - Extract and insert docstrings
  - Gather metadata (function calls, imports, etc.)
  - Validate syntax

deps:
  calls:
    - inspect, importlib
  called_by:
    - agentspec.collect
    - agentspec.extract
    - agentspec.lint
    - agentspec.generate
    - agentspec.insert_metadata
    - agentspec.cli

why: |
  A registry pattern allows core modules to dispatch language-specific behavior without
  hard-coding language logic. This enables:
  1. Adding new languages without modifying existing code
  2. Testing language adapters independently
  3. Graceful fallback if a language adapter is not installed
  4. Clear separation of concerns between language-agnostic and language-specific code
  
  Using file extensions as the registry key provides fast O(1) lookups and aligns with
  how developers naturally identify source files.

guardrails:
  - DO NOT register the same extension twice without unregistering the old adapter first
  - DO NOT modify the registry after adapters are in use; thread safety is not guaranteed
  - ALWAYS implement the LanguageAdapter protocol completely for any new language

changelog:
  - "2025-10-31: Initial implementation of language adapter architecture"
---/agentspec
"""

from __future__ import annotations
from typing import Dict, Optional, Set, Protocol
from pathlib import Path


class LanguageAdapter(Protocol):
    """
    Protocol defining the interface for language-specific adapters.
    
    Any language adapter must implement all methods and properties defined here.
    """

    @property
    def file_extensions(self) -> Set[str]:
        """
        Return set of file extensions this adapter handles (e.g., {'.py', '.pyi'}).
        """
        ...

    def discover_files(self, target: Path) -> list[Path]:
        """
        Discover all source files in target directory or return single file if target is a file.
        
        Should respect language-specific ignore patterns and common exclusion directories.
        """
        ...

    def extract_docstring(self, filepath: Path, lineno: int) -> Optional[str]:
        """
        Extract docstring from the function/class at lineno in filepath.
        
        Returns the raw docstring content including any agentspec blocks, or None.
        """
        ...

    def insert_docstring(self, filepath: Path, lineno: int, docstring: str) -> None:
        """
        Insert or replace the docstring for the function/class at lineno in filepath.
        
        Should handle proper indentation and formatting for the language.
        """
        ...

    def gather_metadata(self, filepath: Path, function_name: str) -> Dict:
        """
        Extract function calls, imports, and other metadata for analysis.
        
        Returns a dict with keys like 'calls', 'imports', 'called_by', etc.
        """
        ...

    def validate_syntax(self, filepath: Path) -> bool:
        """
        Check if the file has valid syntax after modifications.
        
        Should return True if syntax is valid, False or raise if invalid.
        """
        ...

    def get_comment_delimiters(self) -> tuple[str, str]:
        """
        Return the (start, end) delimiters for multi-line comments in this language.
        
        E.g., ('/*', '*/') for JavaScript, ('"""', '"""') for Python docstrings.
        """
        ...

    def parse(self, source_code: str) -> object:
        """
        Parse source code into a language-specific AST or tree structure.
        
        Returns the parsed tree which can be traversed by other adapter methods.
        """
        ...


class LanguageRegistry:
    """
    Global registry mapping file extensions to language adapters.
    """

    _adapters: Dict[str, LanguageAdapter] = {}

    @classmethod
    def register(cls, adapter: LanguageAdapter) -> None:
        """Register an adapter for all its supported extensions."""
        for ext in adapter.file_extensions:
            cls._adapters[ext.lower()] = adapter

    @classmethod
    def unregister(cls, extension: str) -> None:
        """Unregister an adapter by extension."""
        cls._adapters.pop(extension.lower(), None)

    @classmethod
    def get_by_extension(cls, extension: str) -> Optional[LanguageAdapter]:
        """Get adapter for a file extension (e.g., '.py', '.js')."""
        return cls._adapters.get(extension.lower())

    @classmethod
    def get_by_path(cls, filepath: Path | str) -> Optional[LanguageAdapter]:
        """Get adapter for a file by its path."""
        if isinstance(filepath, str):
            filepath = Path(filepath)
        ext = filepath.suffix.lower()
        return cls.get_by_extension(ext)

    @classmethod
    def supported_extensions(cls) -> Set[str]:
        """Return all currently registered file extensions."""
        return set(cls._adapters.keys())

    @classmethod
    def list_adapters(cls) -> Dict[str, LanguageAdapter]:
        """Return all registered adapters."""
        return dict(cls._adapters)


# Import and register the Python adapter
from agentspec.langs.python_adapter import PythonAdapter

_python_adapter = PythonAdapter()
LanguageRegistry.register(_python_adapter)

__all__ = [
    'LanguageAdapter',
    'LanguageRegistry',
    'PythonAdapter',
]
