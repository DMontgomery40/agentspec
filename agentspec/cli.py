#!/usr/bin/env python3
"""
agentspec CLI
-------------
Command-line interface for linting and extracting agent specifications.
"""

import argparse
import difflib
import sys
from pathlib import Path

# Import only what's needed at runtime per command to avoid importing optional deps unnecessarily
from agentspec import lint, extract
from agentspec.utils import load_env_from_dotenv


class FuzzyArgumentParser(argparse.ArgumentParser):
    """Custom ArgumentParser with fuzzy matching for unknown arguments."""
    
    def __init__(self, *args, **kwargs):
        """
        ---agentspec
        what: |
          Initializes a CLI handler instance by invoking the parent class constructor with all provided positional and keyword arguments, then establishes an empty set `_all_valid_args` to track valid argument names. This set serves as a container for accumulating and validating command-line argument specifications throughout the CLI handler's lifecycle. The initialization ensures the parent class is properly set up before introducing CLI-specific state management.
            deps:
              calls:
                - __init__
                - set
                - super
              imports:
                - agentspec.extract
                - agentspec.lint
                - agentspec.utils.load_env_from_dotenv
                - argparse
                - difflib
                - pathlib.Path
                - sys


        why: |
          The parent class initialization must occur first to establish base functionality and state. The `_all_valid_args` set is initialized as empty to support lazy accumulation of valid arguments as they are registered or discovered during CLI parsing and validation phases. Using a set provides O(1) lookup performance for argument validation checks and prevents duplicate argument names from being tracked.

        guardrails:
          - DO NOT assume `_all_valid_args` is pre-populated; it must be explicitly populated by other methods before being used for validation, as initialization leaves it empty.
          - DO NOT modify the parent class initialization signature or order; the `super().__init__()` call must precede any instance-specific state setup to maintain proper inheritance semantics.
          - DO NOT use `_all_valid_args` for filtering or restricting arguments before it has been populated by the CLI handler's argument registration logic.

            changelog:
              - "- no git history available"
            ---/agentspec
        """
        super().__init__(*args, **kwargs)
        self._all_valid_args = set()
    
    def _collect_valid_args(self, parser):
        """
        ---agentspec
        what: |
          Recursively collects all valid argument strings from an argparse parser and its subparsers.

          Behavior:
          - Iterates through all actions in the provided parser's `_actions` list
          - Extracts option strings (e.g., '-h', '--help', '-v', '--verbose') from each action that has them
          - Identifies subparser actions (instances of `argparse._SubParsersAction`) and recursively collects valid arguments from each subparser's choices
          - Returns a set of all collected argument strings, eliminating duplicates

          Inputs:
          - `parser`: An argparse.ArgumentParser instance (or subparser) to inspect

          Outputs:
          - A set of strings representing all valid argument flags and option names available in the parser hierarchy

          Edge cases:
          - Handles parsers with no actions gracefully (returns empty set)
          - Handles parsers with no subparsers (returns only top-level option strings)
          - Recursion terminates when leaf subparsers are reached (those without further subparsers)
          - Duplicate argument strings across parser levels are automatically deduplicated by set semantics
            deps:
              calls:
                - args_set.update
                - choices.values
                - isinstance
                - self._collect_valid_args
                - set
              imports:
                - agentspec.extract
                - agentspec.lint
                - agentspec.utils.load_env_from_dotenv
                - argparse
                - difflib
                - pathlib.Path
                - sys


        why: |
          This method enables comprehensive validation and discovery of all CLI arguments across a potentially nested parser hierarchy. By recursively traversing subparsers, it builds a complete inventory of valid arguments without requiring manual enumeration. This is useful for argument validation, help generation, or CLI introspection. The set-based approach ensures O(1) lookup performance for membership testing and automatic deduplication of shared argument names across parser levels.

        guardrails:
          - DO NOT assume all actions have option_strings; some actions (like positional arguments) may lack them, which is why the conditional check `if action.option_strings` is necessary
          - DO NOT modify the parser structure during traversal; this method is read-only and should not alter `_actions` or subparser choices
          - DO NOT rely on this for runtime argument parsing; it is a metadata collection utility and does not validate or process actual CLI input
          - DO NOT assume subparser choices are always populated; empty subparsers will contribute nothing to the result set

            changelog:
              - "- no git history available"
            ---/agentspec
        """
        args_set = set()
        
        # Get all option strings from actions
        for action in parser._actions:
            if action.option_strings:
                args_set.update(action.option_strings)
        
        # Also check subparsers
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                for subparser in action.choices.values():
                    args_set.update(self._collect_valid_args(subparser))
        
        return args_set
    
    def error(self, message):
        """
        ---agentspec
        what: |
          Overrides ArgumentParser.error() to provide intelligent fuzzy-matching suggestions for unrecognized command-line arguments. When an "unrecognized arguments" error occurs, the method:

          1. Extracts unknown argument(s) from the error message
          2. Collects all valid arguments from the parser and its subparsers (cached in `_all_valid_args`)
          3. Attempts multi-stage matching for each unknown argument:
             - **Partial word matches** (highest priority): Checks if the unknown argument appears as a complete word component in valid arguments (e.g., `--yaml` matches `--agentspec-yaml`)
             - **Direct similarity matching** (60% threshold): Uses difflib.SequenceMatcher for typo detection
             - **Combined flag+word matching** (70% threshold): For non-flag words following a flag, attempts hyphenation (e.g., `--update existing` → `--update-existing`)
             - **Partial flag matching** (50% threshold): For unmatched flags, finds arguments containing the unknown word as a substring or component
          4. Returns up to 3 suggestions per unknown argument, prioritized by match type and similarity score
          5. Falls back to parent class error handling for non-argument errors

          Outputs formatted error message with usage information and suggestions to stderr, then exits with code 2.
            deps:
              calls:
                - arg.startswith
                - arg_base.split
                - difflib.SequenceMatcher
                - difflib.get_close_matches
                - enumerate
                - error
                - join
                - len
                - message.split
                - partial_matches.append
                - partial_word_matches.append
                - prev_arg.startswith
                - ratio
                - self._collect_valid_args
                - self.exit
                - self.print_usage
                - sorted
                - split
                - strip
                - suggestions.append
                - super
                - unknown_arg.startswith
              imports:
                - agentspec.extract
                - agentspec.lint
                - agentspec.utils.load_env_from_dotenv
                - argparse
                - difflib
                - pathlib.Path
                - sys


        why: |
          Improves user experience by guiding users toward correct argument names instead of cryptic "unrecognized arguments" rejections. Handles common typos, hyphenation variations, and partial flag names that users might naturally attempt. The multi-stage matching strategy balances precision (word-component matches are most reliable) with recall (similarity matching catches typos). Caching valid arguments avoids repeated traversal of the parser tree. The approach prioritizes exact word matches over pure similarity to avoid suggesting semantically unrelated arguments.

        guardrails:
          - DO NOT modify error messages for non-argument errors; always delegate to parent class via super().error() to preserve standard ArgumentParser behavior
          - ALWAYS cache valid arguments in `_all_valid_args` to avoid repeated collection overhead during multiple error conditions
          - DO NOT suggest matches below established similarity thresholds (0.6 for direct matches, 0.7 for combined flag+word, 0.5 for partial flag matches) to prevent misleading suggestions
          - DO NOT suggest more than 3 alternatives per unknown argument to avoid overwhelming the user with options
          - DO NOT apply word-component matching logic to non-flag arguments (those not starting with `--`) to avoid false positives

            changelog:
              - "- no git history available"
            ---/agentspec
        """
        # Check if this is an "unrecognized arguments" error
        if "unrecognized arguments:" in message:
            # Extract the unknown argument(s)
            unknown_args = message.split("unrecognized arguments:")[-1].strip().split()
            
            # Collect all valid arguments from this parser and its subparsers
            if not self._all_valid_args:
                self._all_valid_args = self._collect_valid_args(self)
            
            # Try to find suggestions for each unknown argument
            suggestions = []
            for i, unknown_arg in enumerate(unknown_args):
                # Check for partial word matches first (these are most reliable)
                # e.g., --yaml should match --agentspec-yaml before --model
                partial_word_matches = []
                if unknown_arg.startswith('--'):
                    unknown_base = unknown_arg[2:]  # Strip '--'
                    for arg in self._all_valid_args:
                        if not arg.startswith('--'):
                            continue
                        arg_base = arg[2:]  # Strip '--'
                        # Check if unknown word appears in valid arg (most reliable match)
                        if unknown_base in arg_base.split('-') or arg_base.split('-')[-1] == unknown_base:
                            partial_word_matches.append(arg)
                
                # If we found word matches, use those (prioritize over similarity)
                if partial_word_matches:
                    # Sort by similarity within word matches
                    sorted_word_matches = sorted(
                        partial_word_matches,
                        key=lambda x: difflib.SequenceMatcher(None, unknown_arg, x).ratio(),
                        reverse=True
                    )[:3]
                    suggestions.append(f"  '{unknown_arg}' → did you mean '{sorted_word_matches[0]}'?")
                    if len(sorted_word_matches) > 1:
                        suggestions[-1] += f" (or {', '.join(sorted_word_matches[1:])})"
                    continue
                
                # Try direct similarity match
                matches = difflib.get_close_matches(
                    unknown_arg,
                    self._all_valid_args,
                    n=3,
                    cutoff=0.6  # Require at least 60% similarity
                )
                
                # If no good match and it's a non-flag word, try combining with previous arg
                if not matches and not unknown_arg.startswith('-') and i > 0:
                    prev_arg = unknown_args[i - 1]
                    if prev_arg.startswith('--'):
                        # Try combining: --update + existing → --update-existing
                        combined = prev_arg + '-' + unknown_arg
                        combined_matches = difflib.get_close_matches(
                            combined,
                            self._all_valid_args,
                            n=3,
                            cutoff=0.7
                        )
                        if combined_matches:
                            suggestions.append(
                                f"  '{prev_arg} {unknown_arg}' → did you mean '{combined_matches[0]}'?"
                            )
                            continue
                
                if matches:
                    suggestions.append(f"  '{unknown_arg}' → did you mean '{matches[0]}'?")
                    if len(matches) > 1:
                        suggestions[-1] += f" (or {', '.join(matches[1:])})"
                elif unknown_arg.startswith('--'):
                    # For flags starting with --, try partial matches
                    # e.g., --update might match --update-existing, or --yaml might match --agentspec-yaml
                    unknown_base = unknown_arg[2:]  # Strip '--'
                    partial_matches = []
                    
                    for arg in self._all_valid_args:
                        if not arg.startswith('--'):
                            continue
                        arg_base = arg[2:]  # Strip '--'
                        
                        # Check if unknown is contained in valid arg or vice versa
                        if unknown_base in arg_base or arg_base in unknown_base:
                            partial_matches.append(arg)
                        # Also check if they share a significant word (e.g., "yaml" in both)
                        elif unknown_base in arg_base.split('-') or arg_base.split('-')[-1] == unknown_base:
                            partial_matches.append(arg)
                    
                    if partial_matches:
                        # Sort by priority: exact word matches first, then similarity
                        # This ensures --yaml matches --agentspec-yaml before --model
                        def match_priority(arg):
                            """
                            ---agentspec
                            what: |
                              Ranks command-line argument candidates for fuzzy matching against an unknown argument.

                              Takes a candidate argument string (expected to start with '--') and compares it against
                              an unknown_arg from the enclosing scope. Returns a tuple of (word_match_score, similarity_ratio)
                              used for sorting candidates by relevance.

                              The function strips the '--' prefix from the candidate, then:
                              1. Computes sequence similarity ratio between unknown_arg and the full candidate
                              2. Checks if the unknown argument's base form appears as a complete word within the candidate
                                 (split by hyphens, or as the final hyphen-separated component)
                              3. Returns (1.0, similarity) if a word match is found (highest priority)
                              4. Returns (0.0, similarity) if only sequence similarity applies (lower priority)

                              Edge cases: Handles hyphenated argument names correctly by splitting on '-' and checking
                              both exact word membership and suffix matching. Unknown arguments without hyphens are
                              treated as single words.
                                deps:
                                  calls:
                                    - arg_base.split
                                    - difflib.SequenceMatcher
                                    - ratio
                                  imports:
                                    - agentspec.extract
                                    - agentspec.lint
                                    - agentspec.utils.load_env_from_dotenv
                                    - argparse
                                    - difflib
                                    - pathlib.Path
                                    - sys


                            why: |
                              This prioritization scheme balances exact semantic matching with fuzzy similarity.
                              Word-level matches (e.g., 'help' in '--show-help') are more reliable than character-level
                              similarity alone, reducing false positives when multiple arguments have similar character
                              sequences. The two-tier tuple return enables stable sorting: word matches always rank
                              above non-matches, and ties are broken by similarity ratio. This approach is appropriate
                              for CLI help/suggestion systems where semantic correctness outweighs minor typo tolerance.

                            guardrails:
                              - DO NOT rely solely on sequence similarity without word matching, as it may suggest
                                semantically unrelated arguments that happen to share character patterns
                              - DO NOT modify unknown_arg or the candidate argument in-place; this function must be
                                side-effect-free to work correctly in sorting contexts
                              - DO NOT assume the candidate always starts with '--'; validation should occur in the
                                caller before invoking this function
                              - DO NOT use this function outside a context where unknown_arg and unknown_base are
                                defined in the enclosing scope; refactor to pass them as parameters if reusing elsewhere

                                changelog:
                                  - "- no git history available"
                                ---/agentspec
                            """
                            arg_base = arg[2:]  # Strip '--'
                            similarity = difflib.SequenceMatcher(None, unknown_arg, arg).ratio()
                            # Boost score if unknown word is actually in the arg (not just similar)
                            if unknown_base in arg_base.split('-') or arg_base.split('-')[-1] == unknown_base:
                                return (1.0, similarity)  # Word match gets priority
                            return (0.0, similarity)  # Similarity only
                        
                        sorted_matches = sorted(
                            partial_matches,
                            key=match_priority,
                            reverse=True
                        )
                        # Filter to matches with at least 50% similarity (lower threshold for partial)
                        filtered_matches = [m for m in sorted_matches if difflib.SequenceMatcher(None, unknown_arg, m).ratio() >= 0.5][:3]
                        if filtered_matches:
                            suggestions.append(
                                f"  '{unknown_arg}' → did you mean '{filtered_matches[0]}'?"
                            )
                            if len(filtered_matches) > 1:
                                suggestions[-1] += f" (or {', '.join(filtered_matches[1:])})"
            
            if suggestions:
                error_msg = f"agentspec: error: {message}\n"
                error_msg += "\nDid you mean:\n" + "\n".join(suggestions)
                self.print_usage(sys.stderr)
                self.exit(2, error_msg)
        
        # Fall back to default error handling
        super().error(message)


def _show_rich_help():
    """
    ---agentspec
    what: |
      Renders a formatted help screen to stdout using Rich library with three main sections:
      1. Title panel introducing Agentspec as "Structured, enforceable docstrings for AI agents"
      2. Commands table listing three primary commands (lint, extract, generate) with descriptions
      3. Quick-start examples panel showing common usage patterns for each command
      4. Key flags reference table documenting important CLI flags grouped by command (--strict for lint, --format for extract, --terse/--update-existing/--diff-summary for generate)

      The function constructs Rich Table and Panel objects with styled headers, colored text, and box drawing, then prints each section sequentially to console. No return value; output is side-effect only (stdout).

      Edge cases: Function assumes Rich library is available at runtime; will raise ImportError if Rich is not installed. Function produces no output if console.print() fails silently (e.g., in non-TTY environments, Rich may suppress formatting).
        deps:
          calls:
            - Console
            - Panel
            - Panel.fit
            - Table
            - commands_table.add_column
            - commands_table.add_row
            - console.print
            - flags_table.add_column
            - flags_table.add_row
          imports:
            - agentspec.extract
            - agentspec.lint
            - agentspec.utils.load_env_from_dotenv
            - argparse
            - difflib
            - pathlib.Path
            - sys


    why: |
      Provides an interactive, discoverable CLI help interface without requiring external help text files or manual markdown documentation. Rich formatting (colors, tables, panels, styled text) significantly improves terminal UX and makes command discovery more intuitive than plain text help. Embedding help generation in code ensures help text stays synchronized with actual CLI implementation. Organizing help into logical sections (commands, examples, flags) reduces cognitive load for new users exploring the tool.

    guardrails:
      - DO NOT call this function in non-interactive environments expecting plain text output; Rich may strip formatting or fail silently in non-TTY contexts.
      - DO NOT assume Rich library is pre-installed; imports occur inside function body, so missing Rich will raise ImportError at runtime rather than at module load time.
      - ALWAYS output directly to stdout via Rich Console; do not attempt to capture or redirect return value (function returns None).
      - DO NOT modify console output after printing; Rich Console.print() is not idempotent and subsequent calls will append rather than replace.

        changelog:
          - "- 2025-10-30: chore(lint): ignore E501 to allow long AGENTSPEC context prints"
          - "-    # Emphasize the three most useful generation flags first"
          - "-    Prefer thorough output for ambiguous or uncommon code (avoid --terse)"
          - "-    flags_table.add_row("--terse", "Concise sections for LLM context windows (generate)")"
          - "-    flags_table.add_row("--diff-summary", "Add per-function code diff summaries (generate)")"
          - "-    # Still documented, less emphasized"
          - "-    flags_table.add_row("--update-existing", "Regenerate existing docstrings (generate)")"
          - "-    flags_table.add_row("--agentspec-yaml", "Embed YAML agentspec blocks (generate)")"
          - "-    flags_table.add_row("--force-context", "Add print() statements to force context (generate)")"
          - "-    # Lint/Extract"
          - "-    flags_table.add_row("--min-lines", "Minimum spec size (lint)")"
          - "- 2025-10-30: feat: update CLI help with new generation flags and improved descriptions"
          - "-        "[green]agentspec generate src/ --dry-run[/green]\n""
          - "-        "[green]agentspec generate src/auth.py --diff-summary[/green]","
          - "-    Critical mode removed; see README guidance for important code"
          - "-    flags_table.add_row("--update-existing", "Regenerate existing docstrings (generate)")"
          - "-    flags_table.add_row("--dry-run", "Preview without modifying files (generate)")"
          - "-    flags_table.add_row("--diff-summary", "Add per-function code diff summaries (generate)")"
          - "- 2025-10-30: feat: enhance CLI help and add rich formatting support"
        ---/agentspec
    """
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich import box
    
    console = Console()
    
    # Title
    console.print(Panel.fit(
        "[bold magenta]Agentspec[/bold magenta]\n"
        "[dim]Structured, enforceable docstrings for AI agents[/dim]",
        border_style="cyan",
        padding=(1, 2),
    ))
    console.print()
    
    # Commands table
    commands_table = Table(
        title="[bold]Commands[/bold]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        title_style="bold",
    )
    commands_table.add_column("Command", style="green", no_wrap=True)
    commands_table.add_column("Description")
    
    commands_table.add_row(
        "lint",
        "Validate agentspec blocks in Python files"
    )
    commands_table.add_row(
        "extract", 
        "Extract agentspec blocks to markdown or JSON"
    )
    commands_table.add_row(
        "generate",
        "Auto-generate verbose agentspec docstrings using Claude"
    )
    
    console.print(commands_table)
    console.print()
    
    # Quick examples
    console.print("[bold]Quick Start:[/bold]")
    console.print(Panel(
        "[green]agentspec lint src/ --strict[/green]\n"
        "[green]agentspec extract src/ --format json > specs.json[/green]\n"
        "[green]agentspec generate src/ --update-existing --terse[/green]\n"
        "[green]agentspec generate src/core/ --diff-summary[/green]",
        title="[bold]Examples[/bold]",
        border_style="dim",
        padding=(0, 1),
    ))
    console.print()
    
    # Key flags table
    flags_table = Table(
        title="[bold]Key Flags[/bold]",
        box=box.SIMPLE,
        show_header=False,
        title_style="bold",
    )
    flags_table.add_column("Flag", style="yellow")
    flags_table.add_column("Description")
    
    flags_table.add_row("--strict", "Treat warnings as errors (lint)")
    flags_table.add_row("--format", "Output format: markdown/json/agent-context (extract)")
    flags_table.add_row("--terse", "Shorter output with max_tokens=500 (generate)")
    flags_table.add_row("--update-existing", "Regenerate existing docstrings (generate)")
    flags_table.add_row("--diff-summary", "Add per-function code diff summaries (generate)")
    
    console.print(flags_table)
    console.print()
    
    console.print(
        "[dim]For detailed help on a specific command:[/dim] "
        "[bold cyan]agentspec <command> --help[/bold cyan]"
    )


def main():
    """
    ---agentspec
    what: |
      CLI entry point that parses command-line arguments and dispatches to three subcommands: lint, extract, and generate.

      **Lint subcommand**: Validates agentspec docstring blocks in Python files against format and verbosity requirements. Accepts target (file or directory), --min-lines (minimum lines in agentspec blocks, default 10), and --strict flag (treats warnings as errors). Calls lint.run() with parsed arguments.

      **Extract subcommand**: Exports agentspec blocks from Python files to portable formats. Accepts target (file or directory) and --format flag (choices: markdown, json, agent-context; default markdown). Calls extract.run() with parsed arguments.

      **Generate subcommand**: Auto-generates or refreshes agentspec docstrings using Claude or OpenAI-compatible APIs. Accepts target (file or directory), --dry-run (preview without modifying), --force-context (add print() statements for LLM context), --model (model identifier), --agentspec-yaml (embed YAML block), --provider (auto/anthropic/openai, default auto), --base-url (for OpenAI-compatible endpoints), --update-existing (regenerate existing docstrings), --terse (shorter output), and --diff-summary (add git diff summaries). Lazy-imports generate module to avoid requiring anthropic dependency unless command is used. Calls generate.run() with all parsed arguments.

      **Behavior**: Loads .env file automatically via load_env_from_dotenv(). Displays rich-formatted help if no arguments or --help flag provided. Uses argparse with RichHelpFormatter for improved CLI UX. Routes parsed args to appropriate submodule handler (lint.run(), extract.run(), or generate.run()). Exits with status code 0 on success or 1 on error/missing command. Prints help and exits if no subcommand provided.

      **Edge cases**: Missing ANTHROPIC_API_KEY environment variable causes generate.run() to fail with auth error. Invalid Claude model names fail at API call time, not argument parsing time. --strict flag converts linting warnings to hard errors; use with caution in CI/CD pipelines.
        deps:
          calls:
            - FuzzyArgumentParser
            - _show_rich_help
            - extract.run
            - extract_parser.add_argument
            - generate.run
            - generate_parser.add_argument
            - len
            - lint.run
            - lint_parser.add_argument
            - load_env_from_dotenv
            - parser.add_subparsers
            - parser.parse_args
            - parser.print_help
            - subparsers.add_parser
            - sys.exit
          imports:
            - agentspec.extract
            - agentspec.lint
            - agentspec.utils.load_env_from_dotenv
            - argparse
            - difflib
            - pathlib.Path
            - sys


    why: |
      Subcommand pattern isolates lint, extract, and generate logic for independent testing, maintenance, and feature development without tight coupling. Rich-based help formatter improves CLI UX for both end users and agent consumption. Lazy import of generate module avoids requiring anthropic dependency unless generate command is explicitly invoked, reducing installation friction for users who only need lint/extract. Early exit on missing command prevents ambiguous behavior and ensures explicit user feedback via help text. Explicit if/elif dispatch chain is more readable and debuggable than dict-based dispatch at this scale; easier for agents to trace execution flow. Default values (--min-lines=10, --format=markdown, --model=claude-haiku-4-5) provide sensible out-of-the-box behavior for common workflows. sys.exit() calls ensure process terminates cleanly; Python does not auto-exit from main(). Three distinct operations (validate, export, generate) are grouped as CLI commands rather than separate scripts for better UX and unified distribution.

    guardrails:
      - DO NOT modify the if/elif dispatch logic without updating corresponding submodule signatures in lint.py, extract.py, and generate.py
      - DO NOT remove sys.exit() calls; they are required for proper CLI exit behavior and process termination
      - DO NOT add new subcommands without documenting them in this docstring's WHAT section and updating help text
      - DO NOT change argument parameter names (e.g., target, format, model, provider, base_url) as they are consumed by downstream modules via args object attributes
      - DO NOT remove or rename --dry-run and --force-context flags for generate; these are critical safety mechanisms
      - ALWAYS preserve help text on all CLI flags for end-user clarity and discoverability
      - ALWAYS validate that new CLI flags have sensible defaults to avoid breaking existing automation scripts and CI/CD pipelines
      - ALWAYS ensure subcommand descriptions include common workflows and examples in epilog for agent/user guidance
      - ALWAYS lazy-import optional dependencies (like generate module) to avoid requiring them unless explicitly needed
      - ALWAYS call load_env_from_dotenv() at entry point to allow users to configure via .env without manual export

        changelog:
          - "- 2025-10-30: feat: enhance CLI help and add rich formatting support"
          - "- Parses command-line arguments using argparse to determine which subcommand to execute (lint, extract, or generate)"
          - "- For "lint": validates agentspec docstring blocks in Python files against format requirements, with configurable minimum line counts and strict mode for treating warnings as errors"
          - "- For "extract": reads Python files and exports agentspec docstring blocks in multiple formats (markdown, JSON, or agent-context optimized)"
          - "- For "generate": uses Claude API to auto-generate verbose agentspec docstrings for functions lacking them, with optional dry-run preview and context-forcing via print statements"
          - "- Routes the parsed arguments to the appropriate submodule handler (lint.run(), extract.run(), generate.run())"
          - "- Exits with status code 0 on success or 1 on error/missing command"
          - "- Prints help text and exits if no subcommand is provided"
          - "- Called by: Entry point script (typically invoked as `python -m agentspec` or via setuptools console_scripts entry point)"
          - "- Calls: lint.run(), extract.run(), generate.run() [defined in agentspec/lint.py, agentspec/extract.py, agentspec/generate.py respectively]"
          - "- Imports used: argparse (stdlib), sys (stdlib)"
          - "- External services: Claude API (only when generate command is used)"
          - "- argparse is the standard Python CLI library and handles complex subcommand hierarchies with minimal boilerplate"
          - "- Subcommand pattern allows independent command modules (lint, extract, generate) to be developed and tested separately without tight coupling"
          - "- Three distinct operations (validate, export, generate) are logically grouped as CLI commands rather than separate scripts for better UX and distribution"
          - "- Default values for --min-lines (10), --format ("markdown"), and --model ("claude-haiku-4-5") provide sensible out-of-the-box behavior"
          - "- Explicit command dispatcher (if/elif chain) is more readable and debuggable than dict-based dispatch at this scale; easier for agents to trace execution flow"
          - "- sys.exit() is called twice (for missing command and final status) to ensure process terminates cleanly; Python doesn't auto-exit from main()"
          - "- Early exit on missing command prevents ambiguous behavior and ensures explicit user feedback via help text"
          - "- Current: Initial implementation with three core subcommands (lint, extract, generate) and full CLI argument specification"
          - "- DO NOT modify the if/elif dispatch logic without updating corresponding submodule signatures in lint.py, extract.py, generate.py"
          - "- DO NOT remove sys.exit() calls; they are required for proper CLI exit behavior"
          - "- DO NOT add new subcommands without documenting them in this docstring's WHAT THIS DOES section"
          - "- DO NOT change argument parameter names (e.g., "target", "format", "model") as they are consumed by downstream modules via args object attributes"
          - "- ALWAYS preserve the --dry-run and --force-context flags for generate command; these are critical safety mechanisms"
          - "- ALWAYS ensure all subcommand argument definitions include help text for end-user clarity"
          - "- ALWAYS validate that new CLI flags have sensible defaults to avoid breaking existing automation scripts"
          - "- NOTE: The generate command requires ANTHROPIC_API_KEY environment variable; missing this will cause generate.run() to fail with auth error"
          - "- NOTE: model parameter accepts specific Claude model identifiers; using an invalid model name will fail at API call time, not argument parsing time"
          - "- NOTE: The --strict flag converts linting warnings to hard errors; use with caution in CI/CD pipelines"
          - "-    print(f"[AGENTSPEC_CONTEXT] main: Parses command-line arguments using argparse to determine which subcommand to execute (lint, extract, or generate) | For \"lint\": validates agentspec docstring blocks in Python files against format requirements, with configurable minimum line counts and strict mode for treating warnings as errors | For \"extract\": reads Python files and exports agentspec docstring blocks in multiple formats (markdown, JSON, or agent-context optimized)")"
          - "-        description="Agentspec: Structured, enforceable docstrings for AI agents""
          - "-        help="Validate agentspec blocks in Python files""
          - "-        help="Extract agentspec blocks to markdown or JSON""
          - "-        help="Auto-generate verbose agentspec docstrings using Claude""
          - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features"
          - "- Parses command-line arguments using argparse to determine which subcommand to execute (lint, extract, or generate)"
          - "- For "lint": validates agentspec docstring blocks in Python files against format requirements, with configurable minimum line counts and strict mode for treating warnings as errors"
          - "- For "extract": reads Python files and exports agentspec docstring blocks in multiple formats (markdown, JSON, or agent-context optimized)"
          - "- For "generate": uses Claude API to auto-generate verbose agentspec docstrings for functions lacking them, with optional dry-run preview and context-forcing via print statements"
          - "- Routes the parsed arguments to the appropriate submodule handler (lint.run(), extract.run(), generate.run())"
          - "- Exits with status code 0 on success or 1 on error/missing command"
          - "- Prints help text and exits if no subcommand is provided"
          - "- Called by: Entry point script (typically invoked as `python -m agentspec` or via setuptools console_scripts entry point)"
          - "- Calls: lint.run(), extract.run(), generate.run() [defined in agentspec/lint.py, agentspec/extract.py, agentspec/generate.py respectively]"
          - "- Imports used: argparse (stdlib), sys (stdlib)"
          - "- External services: Claude API (only when generate command is used)"
          - "- argparse is the standard Python CLI library and handles complex subcommand hierarchies with minimal boilerplate"
          - "- Subcommand pattern allows independent command modules (lint, extract, generate) to be developed and tested separately without tight coupling"
          - "- Three distinct operations (validate, export, generate) are logically grouped as CLI commands rather than separate scripts for better UX and distribution"
          - "- Default values for --min-lines (10), --format ("markdown"), and --model ("claude-haiku-4-5") provide sensible out-of-the-box behavior"
          - "- Explicit command dispatcher (if/elif chain) is more readable and debuggable than dict-based dispatch at this scale; easier for agents to trace execution flow"
          - "- sys.exit() is called twice (for missing command and final status) to ensure process terminates cleanly; Python doesn't auto-exit from main()"
          - "- Early exit on missing command prevents ambiguous behavior and ensures explicit user feedback via help text"
          - "- Current: Initial implementation with three core subcommands (lint, extract, generate) and full CLI argument specification"
          - "- DO NOT modify the if/elif dispatch logic without updating corresponding submodule signatures in lint.py, extract.py, generate.py"
          - "- DO NOT remove sys.exit() calls; they are required for proper CLI exit behavior"
          - "- DO NOT add new subcommands without documenting them in this docstring's WHAT THIS DOES section"
          - "- DO NOT change argument parameter names (e.g., "target", "format", "model") as they are consumed by downstream modules via args object attributes"
          - "- ALWAYS preserve the --dry-run and --force-context flags for generate command; these are critical safety mechanisms"
          - "- ALWAYS ensure all subcommand argument definitions include help text for end-user clarity"
          - "- ALWAYS validate that new CLI flags have sensible defaults to avoid breaking existing automation scripts"
          - "- NOTE: The generate command requires ANTHROPIC_API_KEY environment variable; missing this will cause generate.run() to fail with auth error"
          - "- NOTE: model parameter accepts specific Claude model identifiers; using an invalid model name will fail at API call time, not argument parsing time"
          - "- NOTE: The --strict flag converts linting warnings to hard errors; use with caution in CI/CD pipelines"
          - "-            as_agentspec_yaml=args.agentspec_yaml"
          - "- 2025-10-30: feat: robust docstring generation and Haiku defaults"
          - "- Parses command-line arguments using argparse to determine which subcommand to execute (lint, extract, or generate)"
          - "- For "lint": validates agentspec docstring blocks in Python files against format requirements, with configurable minimum line counts and strict mode for treating warnings as errors"
          - "- For "extract": reads Python files and exports agentspec docstring blocks in multiple formats (markdown, JSON, or agent-context optimized)"
          - "- For "generate": uses Claude API to auto-generate verbose agentspec docstrings for functions lacking them, with optional dry-run preview and context-forcing via print statements"
          - "- Routes the parsed arguments to the appropriate submodule handler (lint.run(), extract.run(), generate.run())"
          - "- Exits with status code 0 on success or 1 on error/missing command"
          - "- Prints help text and exits if no subcommand is provided"
          - "- Called by: Entry point script (typically invoked as `python -m agentspec` or via setuptools console_scripts entry point)"
          - "- Calls: lint.run(), extract.run(), generate.run() [defined in agentspec/lint.py, agentspec/extract.py, agentspec/generate.py respectively]"
          - "- Imports used: argparse (stdlib), sys (stdlib)"
          - "- External services: Claude API (only when generate command is used)"
          - "- argparse is the standard Python CLI library and handles complex subcommand hierarchies with minimal boilerplate"
          - "- Subcommand pattern allows independent command modules (lint, extract, generate) to be developed and tested separately without tight coupling"
          - "- Three distinct operations (validate, export, generate) are logically grouped as CLI commands rather than separate scripts for better UX and distribution"
          - "-    - Default values for --min-lines (10), --format ("markdown"), and --model ("claude-sonnet-4-20250514") provide sensible out-of-the-box behavior"
          - "- Explicit command dispatcher (if/elif chain) is more readable and debuggable than dict-based dispatch at this scale; easier for agents to trace execution flow"
          - "- sys.exit() is called twice (for missing command and final status) to ensure process terminates cleanly; Python doesn't auto-exit from main()"
          - "- Early exit on missing command prevents ambiguous behavior and ensures explicit user feedback via help text"
          - "- Current: Initial implementation with three core subcommands (lint, extract, generate) and full CLI argument specification"
          - "- DO NOT modify the if/elif dispatch logic without updating corresponding submodule signatures in lint.py, extract.py, generate.py"
          - "- DO NOT remove sys.exit() calls; they are required for proper CLI exit behavior"
          - "- DO NOT add new subcommands without documenting them in this docstring's WHAT THIS DOES section"
          - "- DO NOT change argument parameter names (e.g., "target", "format", "model") as they are consumed by downstream modules via args object attributes"
          - "- ALWAYS preserve the --dry-run and --force-context flags for generate command; these are critical safety mechanisms"
          - "- ALWAYS ensure all subcommand argument definitions include help text for end-user clarity"
          - "- ALWAYS validate that new CLI flags have sensible defaults to avoid breaking existing automation scripts"
          - "- NOTE: The generate command requires ANTHROPIC_API_KEY environment variable; missing this will cause generate.run() to fail with auth error"
          - "- NOTE: model parameter accepts specific Claude model identifiers; using an invalid model name will fail at API call time, not argument parsing time"
          - "- NOTE: The --strict flag converts linting warnings to hard errors; use with caution in CI/CD pipelines"
          - "-        default="claude-sonnet-4-20250514","
          - "-        help="Claude model to use. Options: claude-sonnet-4-20250514 (default), ""
          - "-             "claude-haiku-4-5, claude-3-5-sonnet-20241022, claude-3-5-haiku-20241022""
          - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate"
          - "-            model=args.model"
          - "- 2025-10-29: Fix model name AGAIN - claude-haiku-4-5 is the correct name (not claude-haiku-4-5-20250929)"
          - "-        choices=["
          - "-            "claude-sonnet-4-20250514","
          - "-            "claude-3-5-sonnet-20241022","
          - "-            "claude-3-5-haiku-20241022""
          - "-        ],"
          - "-        help="Claude model to use (default: claude-sonnet-4-20250514)""
        ---/agentspec
    """
    # Load .env automatically (nearest) so users don't have to export manually
    load_env_from_dotenv()
    
    # Override help completely for main command
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ('--help', '-h')):
        _show_rich_help()
        sys.exit(0)
    
    # Use Rich-based help formatter (required dependency)
    from rich_argparse import RichHelpFormatter as _HelpFmt  # type: ignore

    parser = FuzzyArgumentParser(
        description="Agentspec: Structured, enforceable docstrings for AI agents",
        formatter_class=_HelpFmt,
        epilog=(
            "Quick start:\n"
            "  agentspec lint src/ --strict\n"
            "  agentspec extract src/ --format json > specs.json\n"
            "  agentspec generate src/ --dry-run\n"
            "  agentspec generate src/auth.py --diff-summary\n\n"
            "Tip: run 'agentspec <command> --help' for detailed flags."
        ),
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Lint command
    lint_parser = subparsers.add_parser(
        "lint",
        help="Validate agentspec blocks in Python files",
        description=(
            "Validate agentspec docstrings for presence, structure, and verbosity.\n\n"
            "Common flows:\n"
            "- Enforce standards in CI: --strict (warnings cause non-zero exit)\n"
            "- Raise minimum spec verbosity: --min-lines N\n"
            "- Quick check of a single file before commit\n\n"
            "Behavior:\n"
            "- Prints per-file errors and warnings\n"
            "- Exits non-zero on errors (and on warnings when --strict)\n"
        ),
        epilog=(
            "Examples:\n"
            "  agentspec lint src/ --strict\n"
            "  agentspec lint src/payments.py --strict --min-lines 20\n"
            "  agentspec lint src/ --min-lines 15\n"
        ),
        formatter_class=_HelpFmt,
    )
    lint_parser.add_argument(
        "target",
        help="File or directory to lint"
    )
    lint_parser.add_argument(
        "--min-lines",
        type=int,
        default=10,
        help="Minimum lines required in agentspec blocks (default: 10)"
    )
    lint_parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors"
    )
    
    # Extract command
    extract_parser = subparsers.add_parser(
        "extract",
        help="Extract agentspec blocks to markdown or JSON",
        description=(
            "Extract agentspecs from code into portable docs for humans/CI/LLMs.\n\n"
            "Common flows:\n"
            "- Human-readable docs site or review bundle: (default) markdown\n"
            "- Machine-readable output for pipelines: --format json\n"
            "- Agent-executable context with print() prompts: --format agent-context\n\n"
            "Outputs:\n"
            "- markdown → agent_specs.md\n"
            "- json → agent_specs.json\n"
            "- agent-context → AGENT_CONTEXT.md\n"
        ),
        epilog=(
            "Examples:\n"
            "  agentspec extract src/\n"
            "  agentspec extract src/ --format json > specs.json\n"
            "  agentspec extract src/auth.py --format agent-context\n"
        ),
        formatter_class=_HelpFmt,
    )
    extract_parser.add_argument(
        "target",
        help="File or directory to extract from"
    )
    extract_parser.add_argument(
        "--format",
        choices=["markdown", "json", "agent-context"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    
    # Generate command
    generate_parser = subparsers.add_parser(
        "generate",
        help="Auto-generate verbose agentspec docstrings",
        description=(
            "Generate or refresh agentspec docstrings from code.\n\n"
            "Common flows:\n"
            "- Keep docs in sync: --update-existing\n"
            "- Higher accuracy for ambiguous or uncommon code: --critical\n"
            "- Fit more into LLM context: --terse\n"
            "- Add commit-intent summaries: --diff-summary\n\n"
            "Providers:\n"
            "- Anthropic by model name (e.g., claude-haiku-4-5)\n"
            "- OpenAI-compatible (incl. Ollama): --provider openai [--base-url URL]\n"
        ),
        epilog=(
            "Examples:\n"
            "  agentspec generate src/ --update-existing --terse\n"
            "  agentspec generate src/core/ --critical --diff-summary\n"
            "  agentspec generate src/ --provider openai --model gpt-4o-mini\n"
            "  agentspec generate src/ --provider openai --model llama3.2 --base-url http://localhost:11434/v1\n"
        ),
        formatter_class=_HelpFmt,
    )
    generate_parser.add_argument(
        "target",
        help="File or directory to generate docstrings for"
    )
    generate_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be generated without modifying files"
    )
    generate_parser.add_argument(
        "--force-context",
        action="store_true",
        help="Add print() statements to force LLMs to load docstrings into context"
    )
    generate_parser.add_argument(
        "--model",
        type=str,
        default="claude-haiku-4-5",
        help=(
            "Claude model to use. Options: claude-haiku-4-5 (default), "
            "claude-3-5-sonnet-20241022, claude-3-5-haiku-20241022"
        ),
    )
    generate_parser.add_argument(
        "--agentspec-yaml",
        action="store_true",
        help="Generate docstrings that contain an embedded ---agentspec YAML block"
    )
    generate_parser.add_argument(
        "--provider",
        choices=["auto", "anthropic", "openai"],
        default="auto",
        help="LLM provider to use: 'anthropic' (Claude), 'openai' (OpenAI-compatible, including Ollama), or 'auto' (infer from model)"
    )
    generate_parser.add_argument(
        "--base-url",
        type=str,
        default=None,
        help="Base URL for OpenAI-compatible providers (e.g., http://localhost:11434/v1 for Ollama). Overrides env if set."
    )
    generate_parser.add_argument(
        "--update-existing",
        action="store_true",
        help="Regenerate docstrings even for functions that already have them (useful when code changes)"
    )
    generate_parser.add_argument(
        "--terse",
        action="store_true",
        help="TERSE MODE: Shorter output with max_tokens=500 and temperature=0.0 (more concise, deterministic)"
    )
    generate_parser.add_argument(
        "--diff-summary",
        action="store_true",
        help="DIFF SUMMARY: Add LLM-generated summaries of git diffs for each commit (separate API call)"
    )

    # Keep top-level help concise. Detailed flags remain in each subcommand's --help.

    # Parse args
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    if args.command == "lint":
        exit_code = lint.run(
            args.target,
            min_lines=args.min_lines,
            strict=args.strict
        )
    elif args.command == "extract":
        exit_code = extract.run(
            args.target,
            fmt=args.format
        )
    elif args.command == "generate":
        # Lazy import to avoid requiring anthropic unless generate is used
        from agentspec import generate
        exit_code = generate.run(
            args.target,
            dry_run=args.dry_run,
            force_context=args.force_context,
            model=args.model,
            as_agentspec_yaml=args.agentspec_yaml,
            provider=args.provider,
            base_url=args.base_url,
            update_existing=args.update_existing,
            terse=args.terse,
            diff_summary=args.diff_summary,
        )
    else:
        parser.print_help()
        exit_code = 1
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
