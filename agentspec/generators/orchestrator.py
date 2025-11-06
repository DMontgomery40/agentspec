#!/usr/bin/env python3
"""
Orchestrator for coordinating the entire generation pipeline.

---agentspec
what: |
  Main coordinator class that ties together parsing, generation, and formatting.

  **Pipeline:**
  1. Parse source code (PythonParser)
  2. Select prompt builder (VerbosePrompt or TersePrompt)
  3. Build prompts for LLM
  4. Call LLM provider (Anthropic, OpenAI, Local)
  5. Get structured AgentSpec back (via Instructor)
  6. Format as docstring (GoogleFormatter, NumpyFormatter, etc.)
  7. Return formatted docstring

  **Responsibilities:**
  - Language detection (from file extension)
  - Parser selection (Python, JS, TS)
  - Provider selection (based on config)
  - Formatter selection (based on style config)
  - Prompt selection (verbose vs terse)
  - Error handling and retries
  - Result aggregation

why: |
  Orchestrator pattern separates coordination logic from implementation details.
  Each component (parser, provider, formatter) can be tested independently, then
  orchestrator wires them together.

  This enables:
  - Swappable components (try different formatters without changing generation)
  - Easy testing (mock individual components)
  - Clear separation of concerns
  - Configuration-driven behavior (swap providers via config, not code)

guardrails:
  - DO NOT put parsing/formatting logic in orchestrator (delegate to components)
  - ALWAYS validate config before starting generation
  - DO NOT swallow exceptions (propagate with context)
  - ALWAYS use dependency injection (pass components to constructor)

deps:
  imports:
    - pathlib
    - typing
  calls:
    - PythonParser
    - AnthropicProvider / OpenAIProvider / LocalProvider
    - GoogleFormatter / NumpyFormatter / SphinxFormatter
    - VerbosePrompt / TersePrompt
---/agentspec
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Optional, Dict, Any

from agentspec.models.config import GenerationConfig
from agentspec.models.agentspec import AgentSpec
from agentspec.models.results import GenerationResult

# Parsers
from agentspec.parsers import PythonParser, BaseParser, ParsedFunction

# Providers
from agentspec.generators.providers import (
    BaseProvider,
    AnthropicProvider,
    OpenAIProvider,
    LocalProvider,
)

# Formatters
from agentspec.generators.formatters import BaseFormatter
from agentspec.generators.formatters.python import (
    GoogleDocstringFormatter,
    NumpyDocstringFormatter,
    SphinxDocstringFormatter,
)

# Prompts
from agentspec.generators.prompts import BasePrompt, VerbosePrompt, TersePrompt

# Collectors
from agentspec.collectors import CollectorOrchestrator
from agentspec.collectors.code_analysis import (
    SignatureCollector,
    ExceptionCollector,
    DecoratorCollector,
    ComplexityCollector,
    TypeAnalysisCollector,
    DependencyCollector,
)
from agentspec.collectors.git_analysis import (
    CommitHistoryCollector,
    GitBlameCollector,
)


class Orchestrator:
    """
    Main orchestrator for docstring generation pipeline.

    ---agentspec
    what: |
      Coordinates the entire generation flow from source code to formatted docstring.

      **Initialization:**
      - Takes GenerationConfig
      - Initializes parser, provider, formatter, prompt builder based on config
      - Validates all components are configured correctly

      **Main Method:**
      - generate_docstring(code, function_name, context) → GenerationResult
      - Runs full pipeline and returns result object

      **Component Selection:**
      - Provider: auto-detect from model name, or use explicit config
      - Formatter: based on style config (google/numpy/sphinx)
      - Prompt: based on terse flag (verbose by default)
      - Parser: based on language (currently only Python)

    why: |
      Centralized orchestration makes it easy to:
      - Configure entire pipeline from one config object
      - Test end-to-end flow with real components
      - Swap implementations without changing calling code
      - Add new languages/styles/providers incrementally

    guardrails:
      - DO NOT initialize components in method calls (do it in __init__)
      - ALWAYS validate config in __init__ (fail fast)
      - DO NOT modify config during generation (read-only)
      - ALWAYS use dependency injection (testability)
    ---/agentspec
    """

    def __init__(self, config: GenerationConfig):
        """
        Initialize orchestrator with configuration.

        Args:
            config: Generation configuration

        Raises:
            RuntimeError: If configuration is invalid
            ValueError: If unsupported options specified

        Rationale:
            Initialize all components up front (fail fast if misconfigured).
            Lazy initialization would delay errors until first generate() call.

        Guardrails:
            - ALWAYS validate provider is configured correctly
            - DO NOT initialize parser until needed (language-specific)
            - ALWAYS validate style is supported
        """
        self.config = config

        # Initialize provider
        self.provider = self._create_provider()

        # Validate provider config
        self.provider.validate_config()

        # Initialize formatter
        self.formatter = self._create_formatter()

        # Initialize prompt builder
        self.prompt = self._create_prompt()

        # Parser initialized per-file (language-specific)
        self._parser: Optional[BaseParser] = None

    def _create_provider(self) -> BaseProvider:
        """
        Create LLM provider based on config.

        Returns:
            Initialized provider

        Rationale:
            Auto-detect provider from model name if provider="auto".
            Otherwise use explicit provider setting.

        Guardrails:
            - ALWAYS check model name for anthropic/claude prefix
            - DO NOT assume OpenAI if model unknown (could be Ollama)
            - ALWAYS pass full config to provider (don't filter)
        """
        provider_type = self.config.provider.lower()

        # Auto-detect from model name
        if provider_type == "auto":
            model_lower = self.config.model.lower()
            if "claude" in model_lower or "anthropic" in model_lower:
                provider_type = "anthropic"
            else:
                # Default to OpenAI-compatible for unknown models
                provider_type = "openai"

        # Create appropriate provider
        if provider_type == "anthropic":
            return AnthropicProvider(self.config)
        elif provider_type == "openai":
            return OpenAIProvider(self.config)
        elif provider_type == "local":
            return LocalProvider(self.config)
        else:
            raise ValueError(
                f"Unsupported provider: {provider_type}. "
                f"Use 'anthropic', 'openai', 'local', or 'auto'"
            )

    def _create_formatter(self) -> BaseFormatter:
        """
        Create formatter based on style config.

        Returns:
            Initialized formatter

        Rationale:
            Map style string to formatter class. Default to Google if invalid.

        Guardrails:
            - ALWAYS support google/numpy/sphinx for Python
            - DO NOT fail on unknown style (default to google)
            - ALWAYS log warning if defaulting
        """
        style = self.config.style.lower()

        formatters = {
            "google": GoogleDocstringFormatter,
            "numpy": NumpyDocstringFormatter,
            "sphinx": SphinxDocstringFormatter,
        }

        formatter_class = formatters.get(style, GoogleDocstringFormatter)

        if style not in formatters:
            print(f"Warning: Unknown style '{style}', defaulting to Google")

        return formatter_class()

    def _create_prompt(self) -> BasePrompt:
        """
        Create prompt builder based on config.

        Returns:
            Initialized prompt builder

        Rationale:
            Use TersePrompt if terse flag set, otherwise VerbosePrompt.

        Guardrails:
            - ALWAYS default to verbose (better quality)
            - DO NOT use terse for complex/critical code
        """
        if self.config.terse:
            return TersePrompt()
        else:
            return VerbosePrompt()

    def _detect_language(self, file_path: Path) -> str:
        """
        Detect programming language from file extension.

        Args:
            file_path: Path to source file

        Returns:
            Language identifier (python, javascript, typescript, etc.)

        ---agentspec
        what: |
          Maps file extensions to language identifiers for:
          - Parser selection
          - Prompt customization
          - Formatter selection

          Supported extensions:
          - .py, .pyw → python
          - .js, .jsx, .mjs, .cjs → javascript
          - .ts, .tsx → typescript

          Defaults to "python" for unknown extensions (backwards compatibility).

        why: |
          Language detection is required because:
          - Different languages have different parsers (PythonParser vs JSParser)
          - Prompts need language-specific instructions
          - Formatters produce different output (docstrings vs JSDoc)

          File extension is the most reliable signal (faster than parsing).

        guardrails:
          - ALWAYS use suffix (not full path) for detection
          - DO NOT fail on unknown extensions (default to python)
          - ALWAYS lowercase extension for comparison
          - DO NOT parse file content (too slow for detection)
        ---/agentspec
        """
        suffix = file_path.suffix.lower()

        language_map = {
            ".py": "python",
            ".pyw": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".mjs": "javascript",
            ".cjs": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
        }

        return language_map.get(suffix, "python")

    def generate_docstring(
        self,
        code: str,
        function_name: str,
        context: Optional[Dict[str, Any]] = None
    ) -> GenerationResult:
        """
        Generate docstring for a function.

        Args:
            code: Function source code
            function_name: Name of function
            context: Optional context (file_path, parent_class, etc.)

        Returns:
            GenerationResult with success status and generated docstring

        Raises:
            Exception: If generation fails (LLM error, validation failure, etc.)

        Rationale:
            Main entry point for generation. Runs full pipeline:
            1. Build prompts
            2. Call LLM provider
            3. Get structured AgentSpec
            4. Format as docstring
            5. Return result

        Guardrails:
            - ALWAYS wrap in try/except (capture all errors)
            - ALWAYS populate result.errors on failure
            - DO NOT modify input code
            - ALWAYS include original_code in result (for rollback)
        """
        context = context or {}
        file_path = context.get("file_path", Path("unknown"))

        result = GenerationResult(
            success=False,
            function_name=function_name,
            file_path=Path(file_path),
            original_code=code,
            dry_run=self.config.dry_run,
        )

        try:
            # Run collectors to extract deterministic metadata
            metadata = None
            try:
                # Parse code to get AST node
                tree = ast.parse(code)
                function_node = None

                # Find the function definition in the AST
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name == function_name:
                        function_node = node
                        break

                if function_node:
                    # Create and configure collector orchestrator
                    collector_orch = CollectorOrchestrator()

                    # Register all available collectors
                    collector_orch.register(SignatureCollector())
                    collector_orch.register(ExceptionCollector())
                    collector_orch.register(DecoratorCollector())
                    collector_orch.register(ComplexityCollector())
                    collector_orch.register(TypeAnalysisCollector())
                    collector_orch.register(DependencyCollector())

                    # Register git collectors (may fail if not in git repo)
                    try:
                        collector_orch.register(GitBlameCollector())
                        collector_orch.register(CommitHistoryCollector())
                    except Exception:
                        # Git collectors optional (file may not be in git)
                        pass

                    # Collect all metadata
                    collector_context = {
                        "function_name": function_name,
                        "file_path": file_path,
                    }
                    metadata = collector_orch.collect_all(function_node, collector_context)

                    result.messages.append(f"Collected metadata: {len(metadata.code_analysis)} code analysis items")

            except Exception as e:
                # Collectors are best-effort; continue without metadata if they fail
                result.messages.append(f"Warning: Collector error (continuing without metadata): {str(e)}")

            # Detect language from file extension
            language = self._detect_language(Path(file_path))

            # Build prompts
            system_prompt = self.prompt.build_system_prompt(
                language=language,
                style=self.config.style
            )

            user_prompt = self.prompt.build_user_prompt(
                code=code,
                function_name=function_name,
                context=context
                # NOTE: metadata is NOT passed to LLM (two-phase architecture)
                # It will be injected into the final docstring after LLM generation
            )

            result.messages.append(f"Built prompts for {function_name}")

            # Call LLM provider
            result.messages.append(f"Calling {self.provider.name}...")

            agent_spec: AgentSpec = self.provider.generate(
                prompt=user_prompt,
                system_prompt=system_prompt
            )

            result.messages.append(f"Received structured response from LLM")

            # Format as docstring
            docstring = self.formatter.format(agent_spec)

            result.messages.append(f"Formatted as {self.config.style} docstring")

            # TODO: INJECT DETERMINISTIC METADATA HERE (two-phase architecture)
            # This is where we should inject:
            # - dependencies (from metadata.code_analysis["dependencies"])
            # - changelog (from metadata.git_analysis["commit_history"])
            # - git blame data (from metadata.git_analysis["blame"])
            #
            # The injection should NEVER be visible to the LLM.
            # See existing code in agentspec/generate.py for injection logic.
            #
            # For now, collectors run but metadata is not injected (saved for later PR)

            # Validate output
            self.formatter.validate_output(docstring)

            # Update result
            result.generated_docstring = docstring
            result.success = True

            result.messages.append("Generation complete!")

        except Exception as e:
            result.errors.append(f"Generation failed: {str(e)}")
            result.success = False

        return result

    def generate_for_file(self, file_path: Path) -> Dict[str, GenerationResult]:
        """
        Generate docstrings for all functions in a file.

        Args:
            file_path: Path to source file

        Returns:
            Dict mapping function names to GenerationResult objects

        Rationale:
            Batch process entire file. Useful for CLI commands that operate
            on files/directories.

        Guardrails:
            - DO NOT fail entire file if one function fails
            - ALWAYS continue processing remaining functions
            - ALWAYS return results for all functions (even failures)
        """
        # Detect language and initialize appropriate parser
        language = self._detect_language(file_path)

        if language == "python":
            parser = PythonParser()
        else:
            # JS/TS parsers not yet implemented - skip silently
            # extract and lint work with JS/TS, but generate doesn't yet
            print(f"Warning: Skipping {file_path} - generate only supports Python (.py) files currently")
            print(f"  Note: extract and lint commands work with JS/TS files")
            return {}

        if not parser.can_parse(file_path):
            raise ValueError(f"Cannot parse file: {file_path}")

        # Parse file
        module = parser.parse_file(file_path)

        results: Dict[str, GenerationResult] = {}

        # Process each function
        for func in module.functions:
            # Skip if function already has docstring and update_existing=False
            if func.existing_docstring and not self.config.update_existing:
                continue

            # Generate docstring
            context = {
                "file_path": file_path,
                "parent_class": func.parent_class,
                "existing_docstring": func.existing_docstring,
            }

            result = self.generate_docstring(
                code=func.body,
                function_name=func.name,
                context=context
            )

            results[func.name] = result

        return results
