#!/usr/bin/env python3
"""
Orchestrator for coordinating the entire generation pipeline.

"""

from __future__ import annotations

import ast
import re
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

# Import modular injection function (NOT from monolithic generate.py)
from agentspec.insert_metadata import inject_deterministic_metadata


class Orchestrator:
    """
    Main orchestrator for docstring generation pipeline.

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

            # INJECT DETERMINISTIC METADATA (two-phase architecture)
            # This happens AFTER LLM generation and formatting
            # The LLM never saw this data
            if metadata:
                # Convert CollectedMetadata to dict format for injection
                injection_data = {}

                # Extract dependencies
                if "dependencies" in metadata.code_analysis:
                    deps = metadata.code_analysis["dependencies"]
                    injection_data['deps'] = {
                        'calls': deps.get('calls', []),
                        'imports': deps.get('imports', [])
                    }

                # Extract changelog from git history
                if "commit_history" in metadata.git_analysis:
                    commits = metadata.git_analysis["commit_history"].get('commits', [])
                    # Format as changelog entries
                    changelog_entries = []
                    for commit in commits[:10]:  # Limit to 10 most recent
                        date = commit.get('date', '')
                        msg = commit.get('message', '')
                        changelog_entries.append(f"{date}: {msg}")
                    injection_data['changelog'] = changelog_entries

                # Inject into docstring using existing generate.py function
                # as_agentspec_yaml=False because new architecture generates PEP 257 docstrings
                docstring = inject_deterministic_metadata(docstring, injection_data, as_agentspec_yaml=False)
                result.messages.append("Injected deterministic metadata (dependencies, changelog)")

            # If diff_summary requested, make separate LLM call to summarize function-scoped code diffs (excluding docstrings/comments)
            if self.config.diff_summary and function_name and isinstance(file_path, Path):
                try:
                    from agentspec.collect import collect_function_code_diffs
                    code_diffs = collect_function_code_diffs(Path(file_path), function_name)

                    if code_diffs:
                        # Build prompt for LLM: infer the WHY from the code changes and commit messages
                        diff_prompt = (
                            "CRITICAL: Output format is EXACTLY one line per commit in format:\n"
                            "- YYYY-MM-DD: summary (hash)\n\n"
                            "Summarize the intent (WHY) behind these changes to the specific function.\n"
                            "Only consider the added/removed lines shown (docstrings/comments removed).\n"
                            "Use the exact date and commit hash provided. Provide a concise WHY summary in <=15 words.\n\n"
                        )
                        for d in code_diffs:
                            commit_hash = d.get('hash', 'unknown')
                            diff_prompt += f"Commit: {d['date']} - {d['message']} ({commit_hash})\n"
                            diff_prompt += f"Function: {function_name}\n"
                            diff_prompt += f"Changed lines:\n{d['diff']}\n\n"

                        # Separate API call for diff summaries
                        summary_system_prompt = (
                            "CRITICAL: You are a precise code-change analyst. Output EXACTLY one line per commit in format:\n"
                            "- YYYY-MM-DD: concise summary (hash)\n\n"
                            "Infer WHY the function changed in <=10 words. Use exact date and hash provided."
                            if self.config.terse else
                            "CRITICAL: You are a precise code-change analyst. Output EXACTLY one line per commit in format:\n"
                            "- YYYY-MM-DD: concise summary (hash)\n\n"
                            "Explain WHY the function changed in <=15 words. Use exact date and hash provided."
                        )

                        # Create a custom AgentSpec model just for diff summary (plain text response)
                        from pydantic import BaseModel

                        class DiffSummaryResponse(BaseModel):
                            summary: str

                        # Make LLM call with lower temperature and fewer tokens
                        try:
                            # Use provider's raw client for plain text response (bypassing Instructor)
                            # We need plain text, not structured AgentSpec
                            raw_client = self.provider.raw_client

                            # Get raw completion without Instructor parsing
                            if self.provider.name == "AnthropicProvider":
                                raw_response = raw_client.messages.create(
                                    model=self.config.model,
                                    max_tokens=500 if self.config.terse else 1000,
                                    temperature=0.0,
                                    messages=[
                                        {"role": "user", "content": summary_system_prompt + "\n\n" + diff_prompt}
                                    ]
                                )
                                diff_summaries_text = raw_response.content[0].text
                            else:
                                # OpenAI or compatible
                                raw_response = raw_client.chat.completions.create(
                                    model=self.config.model,
                                    max_tokens=500 if self.config.terse else 1000,
                                    temperature=0.0,
                                    messages=[
                                        {"role": "system", "content": summary_system_prompt},
                                        {"role": "user", "content": diff_prompt}
                                    ]
                                )
                                diff_summaries_text = raw_response.choices[0].message.content

                            # Validate diff summary format
                            expected_pattern = re.compile(r'^\s*-\s+\d{4}-\d{2}-\d{2}:\s+.+\([a-f0-9]{4,}\)\s*$', re.MULTILINE)
                            lines = [line.strip() for line in diff_summaries_text.split('\n') if line.strip()]

                            # Check if response follows the required format
                            valid_lines = []
                            for line in lines:
                                if expected_pattern.match(line):
                                    valid_lines.append(line)
                                elif line and not line.startswith('#') and not line.startswith('```'):
                                    # If line has content but doesn't match format, LLM ignored instructions
                                    result.messages.append(f"Warning: Diff summary line doesn't match required format: {line[:50]}...")
                                    break
                            else:
                                # All lines are valid or empty
                                if not valid_lines:
                                    result.messages.append("Warning: Diff summary is empty")
                                else:
                                    result.messages.append(f"Diff summary format validated ({len(valid_lines)} entries)")

                            # Inject function-scoped diff summary section
                            diff_summary_section = f"\n\nFUNCTION CODE DIFF SUMMARY (LLM-generated):\n{diff_summaries_text}\n"
                            docstring += diff_summary_section
                            result.messages.append("Injected diff summary")

                        except Exception as e:
                            result.messages.append(f"Warning: Failed to generate diff summary: {str(e)}")

                except Exception as e:
                    result.messages.append(f"Warning: Failed to collect code diffs: {str(e)}")

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
