#!/usr/bin/env python3
"""
agentspec CLI
-------------
Command-line interface for linting and extracting agent specifications.
"""

import argparse
import difflib
import sys

# Import only what's needed at runtime per command to avoid importing optional deps unnecessarily
from agentspec import lint, extract, strip
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
                if unknown_arg.startswith("--"):
                    unknown_base = unknown_arg[2:]  # Strip '--'
                    for arg in self._all_valid_args:
                        if not arg.startswith("--"):
                            continue
                        arg_base = arg[2:]  # Strip '--'
                        # Check if unknown word appears in valid arg (most reliable match)
                        if unknown_base in arg_base.split("-") or arg_base.split("-")[-1] == unknown_base:
                            partial_word_matches.append(arg)

                # If we found word matches, use those (prioritize over similarity)
                if partial_word_matches:
                    # Sort by similarity within word matches
                    sorted_word_matches = sorted(
                        partial_word_matches,
                        key=lambda x: difflib.SequenceMatcher(None, unknown_arg, x).ratio(),
                        reverse=True,
                    )[:3]
                    suggestions.append(f"  '{unknown_arg}' → did you mean '{sorted_word_matches[0]}'?")
                    if len(sorted_word_matches) > 1:
                        suggestions[-1] += f" (or {', '.join(sorted_word_matches[1:])})"
                    continue

                # Try direct similarity match
                matches = difflib.get_close_matches(
                    unknown_arg, self._all_valid_args, n=3, cutoff=0.6  # Require at least 60% similarity
                )

                # If no good match and it's a non-flag word, try combining with previous arg
                if not matches and not unknown_arg.startswith("-") and i > 0:
                    prev_arg = unknown_args[i - 1]
                    if prev_arg.startswith("--"):
                        # Try combining: --update + existing → --update-existing
                        combined = prev_arg + "-" + unknown_arg
                        combined_matches = difflib.get_close_matches(combined, self._all_valid_args, n=3, cutoff=0.7)
                        if combined_matches:
                            suggestions.append(f"  '{prev_arg} {unknown_arg}' → did you mean '{combined_matches[0]}'?")
                            continue

                if matches:
                    suggestions.append(f"  '{unknown_arg}' → did you mean '{matches[0]}'?")
                    if len(matches) > 1:
                        suggestions[-1] += f" (or {', '.join(matches[1:])})"
                elif unknown_arg.startswith("--"):
                    # For flags starting with --, try partial matches
                    # e.g., --update might match --update-existing, or --yaml might match --agentspec-yaml
                    unknown_base = unknown_arg[2:]  # Strip '--'
                    partial_matches = []

                    for arg in self._all_valid_args:
                        if not arg.startswith("--"):
                            continue
                        arg_base = arg[2:]  # Strip '--'

                        # Check if unknown is contained in valid arg or vice versa
                        if unknown_base in arg_base or arg_base in unknown_base:
                            partial_matches.append(arg)
                        # Also check if they share a significant word (e.g., "yaml" in both)
                        elif unknown_base in arg_base.split("-") or arg_base.split("-")[-1] == unknown_base:
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
                            if unknown_base in arg_base.split("-") or arg_base.split("-")[-1] == unknown_base:
                                return (1.0, similarity)  # Word match gets priority
                            return (0.0, similarity)  # Similarity only

                        sorted_matches = sorted(partial_matches, key=match_priority, reverse=True)
                        # Filter to matches with at least 50% similarity (lower threshold for partial)
                        filtered_matches = [
                            m for m in sorted_matches if difflib.SequenceMatcher(None, unknown_arg, m).ratio() >= 0.5
                        ][:3]
                        if filtered_matches:
                            suggestions.append(f"  '{unknown_arg}' → did you mean '{filtered_matches[0]}'?")
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
      Renders a formatted help screen to stdout using Rich library with four main sections:
      1. Title panel introducing Agentspec as "Structured, enforceable docstrings for AI agents"
      2. Commands table listing primary commands (lint, extract, generate, strip) with descriptions
      3. Quick-start examples panel showing common usage patterns for each command
      4. Key flags reference table documenting important CLI flags grouped by command (--strict for lint, --format for extract, --terse/--update-existing/--diff-summary for generate, --mode for strip)

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

      - "2025-10-31: Clean up docstring formatting"
        ---/agentspec
    """
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich import box

    console = Console()

    # Title
    console.print(
        Panel.fit(
            "[bold magenta]Agentspec[/bold magenta]\n" "[dim]Structured, enforceable docstrings for AI agents[/dim]",
            border_style="cyan",
            padding=(1, 2),
        )
    )
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

    commands_table.add_row("lint", "Validate agentspec blocks in Python files")
    commands_table.add_row("extract", "Extract agentspec blocks to markdown or JSON")
    commands_table.add_row("generate", "Auto-generate verbose agentspec docstrings using Claude")
    commands_table.add_row("strip", "Remove agentspec-generated docstrings from Python files")
    commands_table.add_row("prompts", "Prompts and examples toolkit")

    console.print(commands_table)
    console.print()

    # Quick examples
    console.print("[bold]Quick Start:[/bold]")
    console.print(
        Panel(
            "[green]agentspec lint src/ --strict[/green]\n"
            "[green]agentspec extract src/ --format json > specs.json[/green]\n"
            "[green]agentspec generate src/ --update-existing --terse[/green]\n"
            "[green]agentspec generate src/core/ --diff-summary[/green]\n"
            "[green]agentspec strip src/ --mode yaml --dry-run[/green]",
            title="[bold]Examples[/bold]",
            border_style="dim",
            padding=(0, 1),
        )
    )
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
    flags_table.add_row("--mode", "Strip mode: all (default), yaml, or docstrings (strip)")

    console.print(flags_table)
    console.print()

    console.print(
        "[dim]For detailed help on a specific command:[/dim] " "[bold cyan]agentspec <command> --help[/bold cyan]"
    )


def _show_generate_rich_help():
    """
    ---agentspec
    what: |
      Render a dyslexia-friendly Rich help for `agentspec generate`, including a Quick Provider Guide with
      copy/paste examples for OpenAI (CFG default), Anthropic, and Ollama. Uses big panels and short lines.
    ---/agentspec
    """
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich import box

    c = Console()

    c.print(Panel.fit("[bold magenta]agentspec generate[/bold magenta]\n[dim]Generate agentspec documentation[/dim]",
                      border_style="cyan", padding=(1,2)))

    guide = (
        "[bold]Quick Provider Guide[/bold]\n\n"
        "[bold green]OpenAI (default, CFG)[/bold green]\n"
        "OPENAI_API_KEY must be set.\n"
        "[white]agentspec generate src/ --model gpt-5 --agentspec-yaml --update-existing[/white]\n\n"
        "[bold yellow]Anthropic[/bold yellow]\n"
        "ANTHROPIC_API_KEY must be set.\n"
        "[white]agentspec generate src/ --provider claude --model claude-3-haiku-20240307 --agentspec-yaml --update-existing[/white]\n\n"
        "[bold cyan]Ollama (local)[/bold cyan]\n"
        "Run: [white]ollama run qwen3-coder:30b[/white]\n"
        "[white]agentspec generate src/ --provider openai --base-url http://localhost:11434/v1 --model qwen3-coder:30b --agentspec-yaml --update-existing[/white]"
    )
    c.print(Panel(guide, title="Provider Guide", border_style="dim", padding=(0,1)))

    eg = (
        "[bold]Examples[/bold]\n"
        "[white]agentspec generate src/ --update-existing --terse[/white]\n"
        "[white]agentspec generate src/core/ --agentspec-yaml --update-existing[/white]\n"
        "[white]agentspec generate src/ --diff-summary --dry-run[/white]\n"
        "[white]agentspec generate src/ --force-context --agentspec-yaml[/white]"
    )
    c.print(Panel(eg, title="Examples", border_style="dim", padding=(0,1)))

    t = Table(title="Key Flags", box=box.SIMPLE_HEAVY, show_header=False)
    t.add_column("Flag", style="yellow")
    t.add_column("Description")
    t.add_row("--model", "Model id (e.g., gpt-5, claude-3-haiku-20240307, qwen3-coder:30b)")
    t.add_row("--provider", "openai | claude | auto (Ollama uses openai w/ base-url)")
    t.add_row("--base-url", "Custom endpoint (e.g., http://localhost:11434/v1)")
    t.add_row("--agentspec-yaml", "Generate structured YAML blocks")
    t.add_row("--update-existing", "Regenerate existing docstrings")
    t.add_row("--terse", "Shorter output (max_tokens=500)")
    t.add_row("--diff-summary", "Add per-function code diff summaries")
    t.add_row("--force-context", "Force print AGENTSPEC_CONTEXT to console")
    t.add_row("--dry-run", "Show what would be generated without writing files")
    c.print(t)


def _show_prompts_rich_help():
    """
    ---agentspec
    what: |
      Render a Rich-formatted help screen for the `prompts` subcommand with full TUI parity to generate -h.
      Includes usage guide, workflow explanation, examples, and complete flags table. Critical accessibility
      requirement for dyslexia accommodation.
    ---/agentspec
    """
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich import box

    c = Console()

    c.print(Panel.fit(
        "[bold magenta]agentspec prompts[/bold magenta]\n[dim]Prompts and examples dataset toolkit[/dim]",
        border_style="cyan", 
        padding=(1,2)
    ))

    # Workflow guide (like Provider Guide for generate)
    guide = (
        "[bold]What This Does[/bold]\n\n"
        "Builds a curated dataset of good/bad documentation examples to improve LLM output quality.\n\n"
        "[bold green]Dataset Location[/bold green]\n"
        "[white]agentspec/prompts/examples.json[/white]\n\n"
        "[bold yellow]Quality Controls[/bold yellow]\n"
        "• Maintains good:bad ratio (prevents dataset degradation)\n"
        "• Validates ASK USER guardrails when required\n"
        "• Dry-run mode for review before committing\n\n"
        "[bold cyan]Typical Workflow[/bold cyan]\n"
        "1. Find code with good/bad documentation examples\n"
        "2. Run with --dry-run to preview the dataset entry\n"
        "3. Review ratio impact and entry quality\n"
        "4. Remove --dry-run to save to dataset"
    )
    c.print(Panel(guide, title="Workflow Guide", border_style="dim", padding=(0,1)))

    # Examples with better context
    examples = (
        "[bold]Examples[/bold]\n\n"
        "[dim]# Add a good example from a test file[/dim]\n"
        "[green]agentspec prompts tests/test_extract.py --add-example \\\n"
        "  --function test_extract_agentspec_block \\\n"
        "  --good-output 'Clear and complete' --dry-run[/green]\n\n"
        "[dim]# Add a bad example with correction[/dim]\n"
        "[green]agentspec prompts src/utils.py --add-example \\\n"
        "  --function parse_config \\\n"
        "  --bad-output 'parses stuff' \\\n"
        "  --correction 'Parses YAML config and validates required fields' \\\n"
        "  --dry-run[/green]\n\n"
        "[dim]# Require ASK USER guardrail (for dangerous operations)[/dim]\n"
        "[green]agentspec prompts src/admin.py --add-example \\\n"
        "  --function delete_user \\\n"
        "  --require-ask-user --dry-run[/green]\n\n"
        "[dim]# Short form (positional path)[/dim]\n"
        "[green]agentspec prompts tests/test_lint.py --add-example --dry-run[/green]"
    )
    c.print(Panel(examples, title="Examples", border_style="dim", padding=(0,1)))

    # Complete flags table
    t = Table(title="All Flags", box=box.SIMPLE_HEAVY, show_header=False)
    t.add_column("Flag", style="yellow")
    t.add_column("Description")
    t.add_row("--add-example", "[bold]REQUIRED[/bold] - Create a dataset entry")
    t.add_row("--file <path>", "Path to source file ([bold]REQUIRED[/bold], or use positional <path>)")
    t.add_row("--function <name>", "Scope to specific function/test in file")
    t.add_row("--subject-function <fqfn>", "Fully qualified name of code being documented")
    t.add_row("--good-output TEXT", "Example of good documentation to validate")
    t.add_row("--bad-output TEXT", "Example of bad documentation to analyze")
    t.add_row("--correction TEXT", "What the bad documentation should have said")
    t.add_row("--require-ask-user", "Ensure ASK USER guardrail is present in entry")
    t.add_row("--dry-run", "Preview entry without writing to dataset")
    t.add_row("--strict-ratio", "Fail if adding would reduce good:bad ratio below minimum")
    c.print(t)
    
    c.print()
    c.print("[dim]Dataset location:[/dim] [white]agentspec/prompts/examples.json[/white]")


def _show_lint_rich_help():
    """Rich TUI help for agentspec lint command."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich import box
    
    c = Console()
    
    c.print(Panel.fit(
        "[bold magenta]agentspec lint[/bold magenta]\n[dim]Validate agentspec blocks[/dim]",
        border_style="cyan",
        padding=(1,2)
    ))
    
    guide = (
        "[bold]What This Does[/bold]\n\n"
        "Validates agentspec YAML blocks for:\n"
        "• Required fields (what, deps, why, guardrails)\n"
        "• YAML syntax errors\n"
        "• Field completeness and structure\n"
        "• Minimum documentation length\n\n"
        "[bold green]Success Criteria[/bold green]\n"
        "✅ All required fields present\n"
        "✅ Valid YAML syntax\n"
        "✅ Guardrails defined (minimum 2-3)\n"
        "✅ Meets minimum line requirements\n\n"
        "[bold yellow]Exit Codes[/bold yellow]\n"
        "0 = All checks passed\n"
        "1 = Errors found (or warnings with --strict)"
    )
    c.print(Panel(guide, title="Validation Guide", border_style="dim", padding=(0,1)))
    
    examples = (
        "[bold]Examples[/bold]\n\n"
        "[dim]# Lint entire project[/dim]\n"
        "[green]agentspec lint src/[/green]\n\n"
        "[dim]# Lint single file[/dim]\n"
        "[green]agentspec lint src/utils.py[/green]\n\n"
        "[dim]# Strict mode (warnings = errors)[/dim]\n"
        "[green]agentspec lint src/ --strict[/green]\n\n"
        "[dim]# Require longer documentation[/dim]\n"
        "[green]agentspec lint src/ --min-lines 15[/green]"
    )
    c.print(Panel(examples, title="Examples", border_style="dim", padding=(0,1)))
    
    t = Table(title="Flags", box=box.SIMPLE_HEAVY, show_header=False)
    t.add_column("Flag", style="yellow")
    t.add_column("Description")
    t.add_row("--strict", "Treat warnings as errors (fail on any issue)")
    t.add_row("--min-lines", "Minimum lines required per agentspec (default: 10)")
    c.print(t)


def _show_extract_rich_help():
    """Rich TUI help for agentspec extract command."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich import box
    
    c = Console()
    
    c.print(Panel.fit(
        "[bold magenta]agentspec extract[/bold magenta]\n[dim]Extract agentspec blocks to various formats[/dim]",
        border_style="cyan",
        padding=(1,2)
    ))
    
    guide = (
        "[bold]Output Formats[/bold]\n\n"
        "[bold green]markdown[/bold green] (default)\n"
        "Human-readable format with headers, code blocks, and organization by file.\n"
        "Best for documentation and review.\n\n"
        "[bold yellow]json[/bold yellow]\n"
        "Structured data format for programmatic access.\n"
        "Includes all metadata, function signatures, and specs.\n"
        "Best for tooling and automation.\n\n"
        "[bold cyan]agent-context[/bold cyan]\n"
        "Optimized format for AI assistants.\n"
        "Includes function signatures, relationships, and dependencies.\n"
        "Best for feeding into LLMs."
    )
    c.print(Panel(guide, title="Format Guide", border_style="dim", padding=(0,1)))
    
    examples = (
        "[bold]Examples[/bold]\n\n"
        "[dim]# Extract to markdown (human-readable)[/dim]\n"
        "[green]agentspec extract src/[/green]\n\n"
        "[dim]# Extract to JSON file[/dim]\n"
        "[green]agentspec extract src/ --format json > specs.json[/green]\n\n"
        "[dim]# Agent-context format for LLM[/dim]\n"
        "[green]agentspec extract src/ --format agent-context > context.md[/green]\n\n"
        "[dim]# Single file extraction[/dim]\n"
        "[green]agentspec extract src/core.py --format json[/green]"
    )
    c.print(Panel(examples, title="Examples", border_style="dim", padding=(0,1)))
    
    t = Table(title="Flags", box=box.SIMPLE_HEAVY, show_header=False)
    t.add_column("Flag", style="yellow")
    t.add_column("Description")
    t.add_row("--format", "Output format: markdown (default) | json | agent-context")
    c.print(t)


def _show_strip_rich_help():
    """Rich TUI help for agentspec strip command."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich import box
    
    c = Console()
    
    c.print(Panel.fit(
        "[bold magenta]agentspec strip[/bold magenta]\n[dim]Remove agentspec-generated content[/dim]",
        border_style="cyan",
        padding=(1,2)
    ))
    
    guide = (
        "[bold]Strip Modes[/bold]\n\n"
        "[bold green]all[/bold green] (default)\n"
        "Removes both YAML blocks and narrative docstrings.\n"
        "Complete cleanup for regeneration.\n\n"
        "[bold yellow]yaml[/bold yellow]\n"
        "Removes only fenced agentspec YAML blocks (---agentspec...---/agentspec).\n"
        "Keeps narrative docstrings intact.\n\n"
        "[bold cyan]docstrings[/bold cyan]\n"
        "Removes only narrative docstrings generated by agentspec.\n"
        "Keeps YAML blocks intact.\n\n"
        "[bold red]⚠️ Safety Features[/bold red]\n"
        "• AST-based parsing (only removes marked content)\n"
        "• Compile check per edit (skips if compilation fails)\n"
        "• Deletes adjacent AGENTSPEC_CONTEXT print statements\n"
        "• Dry-run mode to preview changes"
    )
    c.print(Panel(guide, title="Mode Guide", border_style="dim", padding=(0,1)))
    
    examples = (
        "[bold]Examples[/bold]\n\n"
        "[dim]# Preview what would be removed (DRY RUN - ALWAYS START HERE!)[/dim]\n"
        "[green]agentspec strip src/ --dry-run[/green]\n\n"
        "[dim]# Remove everything (for full regeneration)[/dim]\n"
        "[green]agentspec strip src/ --mode all[/green]\n\n"
        "[dim]# Remove only YAML blocks[/dim]\n"
        "[green]agentspec strip src/ --mode yaml[/green]\n\n"
        "[dim]# Remove only narrative docstrings[/dim]\n"
        "[green]agentspec strip src/ --mode docstrings[/green]\n\n"
        "[dim]# Single file strip with preview[/dim]\n"
        "[green]agentspec strip src/core.py --mode all --dry-run[/green]"
    )
    c.print(Panel(examples, title="Examples", border_style="dim", padding=(0,1)))
    
    t = Table(title="Flags", box=box.SIMPLE_HEAVY, show_header=False)
    t.add_column("Flag", style="yellow")
    t.add_column("Description")
    t.add_row("--mode", "Strip mode: all (default) | yaml | docstrings")
    t.add_row("--dry-run", "Preview changes without modifying files [bold]RECOMMENDED FIRST[/bold]")
    c.print(t)
    
    c.print()
    c.print("[bold yellow]⚠️  RECOMMENDATION:[/bold yellow] [white]Always run with --dry-run first to preview changes![/white]")


def _check_python_version():
    """
    ---agentspec
    what: |
      Validates that the Python runtime meets minimum version requirements (3.10+) before allowing agentspec to execute.

      Behavior:
      - Extracts major and minor version numbers from sys.version_info
      - Compares against hardcoded constants: REQUIRED_MAJOR=3, REQUIRED_MINOR=10
      - If current version is less than 3.10, prints a formatted error message to stderr with:
        * Visual box formatting for prominence
        * Current Python version detected
        * Required minimum version
        * Rationale (PEP 604 union type syntax dependency)
        * Link to compatibility documentation
      - Calls sys.exit(1) on version mismatch, terminating the process with error code
      - Returns silently (None) if version check passes

      Inputs: None (reads from sys.version_info)
      Outputs: None on success; prints to stderr and exits with code 1 on failure

      Edge cases:
      - Handles pre-release versions (e.g., 3.10.0a1) correctly via tuple comparison
      - Works across all platforms where Python runs
      - Executes early in CLI initialization before any feature-dependent imports
        deps:
          calls:
            - print
            - sys.exit
          imports:
            - agentspec.extract
            - agentspec.lint
            - agentspec.strip
            - agentspec.utils.load_env_from_dotenv
            - argparse
            - difflib
            - sys


    why: |
      Python 3.10+ is required because agentspec uses PEP 604 union type syntax (e.g., `str | int`) which is not available in earlier versions. This check prevents cryptic SyntaxError failures later in the import chain by failing fast with a user-friendly message.

      Placing this check in cli.py ensures it runs before any module imports that depend on modern syntax. The formatted stderr output with documentation link helps users quickly understand and resolve the issue without needing to debug Python syntax errors.

    guardrails:
      - DO NOT rely on f-string formatting or other Python 3.10+ syntax within this function itself, as it must execute on older Python versions to deliver the error message
      - DO NOT use sys.exit(0) on success; only exit(1) on failure to preserve standard Unix exit code semantics
      - DO NOT import agentspec modules before this check completes, as they may contain PEP 604 syntax
      - DO NOT make the version requirement configurable at runtime; it must be a hard constraint to ensure codebase assumptions hold

        changelog:
          - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
          - "- 2025-10-31: feat: Python 3.10+ compatibility & CLI formatting improvements (be845fa)"
        ---/agentspec
    """
    import sys

    REQUIRED_MAJOR = 3
    REQUIRED_MINOR = 10

    current = sys.version_info[:2]
    if current[0] < REQUIRED_MAJOR or (current[0] == REQUIRED_MAJOR and current[1] < REQUIRED_MINOR):
        print(
            f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                     ❌ PYTHON VERSION TOO OLD                            ║
╚══════════════════════════════════════════════════════════════════════════╝

Current Python: {current[0]}.{current[1]}
Required minimum: {REQUIRED_MAJOR}.{REQUIRED_MINOR}+

agentspec requires Python {REQUIRED_MAJOR}.{REQUIRED_MINOR}+ because it uses modern syntax (PEP 604 union types).

To upgrade, see: https://github.com/DMontgomery40/agentspec/blob/main/COMPATIBILITY.md
""",
            file=sys.stderr,
        )
        sys.exit(1)


def main():
    """
    ---agentspec
    what: |
      CLI entry point that parses command-line arguments and dispatches to subcommands: lint, extract, generate, strip, and prompts.

      Behavior: Loads .env via load_env_from_dotenv(). Uses argparse with Rich help when available. Intercepts
      -h/--help and missing provider value for generate to render dyslexia-friendly Rich help panels instead of
      raw argparse errors.
    ---/agentspec
    """
    import sys
    import argparse

    from agentspec.utils import load_env_from_dotenv

    load_env_from_dotenv()

    # Intercept global help
    if len(sys.argv) == 2 and sys.argv[1] in ("-h", "--help"):
        try:
            _show_rich_help(); sys.exit(0)
        except Exception:
            pass

    # Intercept generate help and provider mistakes early
    if len(sys.argv) >= 2 and sys.argv[1] == "generate":
        # `agentspec generate -h` or `--help`
        if any(h in sys.argv[2:] for h in ("-h", "--help")):
            try:
                _show_generate_rich_help(); sys.exit(0)
            except Exception:
                pass
        # `--provider` without a value -> show rich panel, not raw argparse error
        if "--provider" in sys.argv[2:]:
            idx = sys.argv.index("--provider")
            if idx == len(sys.argv) - 1 or (idx+1 < len(sys.argv) and sys.argv[idx+1].startswith("-")):
                try:
                    _show_generate_rich_help(); sys.exit(0)
                except Exception:
                    pass
    
    # Intercept lint help
    if len(sys.argv) >= 2 and sys.argv[1] == "lint":
        if any(h in sys.argv[2:] for h in ("-h", "--help")):
            try:
                _show_lint_rich_help(); sys.exit(0)
            except Exception:
                pass
    
    # Intercept extract help
    if len(sys.argv) >= 2 and sys.argv[1] == "extract":
        if any(h in sys.argv[2:] for h in ("-h", "--help")):
            try:
                _show_extract_rich_help(); sys.exit(0)
            except Exception:
                pass
    
    # Intercept strip help
    if len(sys.argv) >= 2 and sys.argv[1] == "strip":
        if any(h in sys.argv[2:] for h in ("-h", "--help")):
            try:
                _show_strip_rich_help(); sys.exit(0)
            except Exception:
                pass

    try:
        from rich_argparse import RichHelpFormatter as _HelpFmt  # type: ignore
    except Exception:
        _HelpFmt = argparse.HelpFormatter

    parser = argparse.ArgumentParser(
        prog="agentspec",
        description="Agentspec CLI",
        formatter_class=_HelpFmt,
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # lint
    lint_parser = subparsers.add_parser("lint", help="Validate agentspec blocks")
    lint_parser.add_argument("target", help="File or directory to lint")
    lint_parser.add_argument("--min-lines", dest="min_lines", type=int, default=10)
    lint_parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")

    # extract
    extract_parser = subparsers.add_parser("extract", help="Extract agentspec blocks")
    extract_parser.add_argument("target", help="File or directory to extract from")
    extract_parser.add_argument(
        "--format",
        choices=["markdown", "json", "agent-context"],
        default="markdown",
    )

    # generate
    generate_parser = subparsers.add_parser("generate", help="Generate agentspec documentation")
    generate_parser.add_argument("target", help="File or directory to process")
    generate_parser.add_argument("--dry-run", action="store_true")
    generate_parser.add_argument("--force-context", action="store_true")
    generate_parser.add_argument("--model", default="claude-haiku-4-5")
    generate_parser.add_argument("--agentspec-yaml", dest="agentspec_yaml", action="store_true")
    generate_parser.add_argument("--provider", default="auto")
    generate_parser.add_argument("--base-url", dest="base_url", default=None)
    generate_parser.add_argument("--update-existing", action="store_true")
    generate_parser.add_argument("--terse", action="store_true")
    generate_parser.add_argument("--diff-summary", dest="diff_summary", action="store_true")

    # strip
    strip_parser = subparsers.add_parser("strip", help="Remove agentspec blocks")
    strip_parser.add_argument("target", help="File or directory")
    strip_parser.add_argument(
        "--mode",
        choices=["all", "yaml", "docstrings"],
        default="all",
    )
    strip_parser.add_argument("--dry-run", action="store_true")

    # prompts (new)
    prompts_parser = subparsers.add_parser("prompts", help="Prompts and examples toolkit")
    prompts_parser.add_argument("path", nargs="?", help="Optional file path (same as --file)")
    prompts_parser.add_argument("--add-example", dest="add_example", action="store_true", help="Create a dataset entry from the given file")
    prompts_parser.add_argument("--file", dest="file", required=False, help="Path to the file to read code from (REQUIRED with --add-example; or positional <path>)")
    prompts_parser.add_argument("--function", dest="function", required=False, help="Optional: name of a test or function inside that file")
    prompts_parser.add_argument("--subject-function", dest="subject_function", required=False, help="Optional: the code you’re documenting (e.g., agentspec.extract.extract_from_js_file)")
    prompts_parser.add_argument("--bad-output", dest="bad_output", required=False, help="Optional: a bad documentation example to analyze")
    prompts_parser.add_argument("--good-output", dest="good_output", required=False, help="Optional: a good documentation example to validate")
    prompts_parser.add_argument("--correction", dest="correction", required=False, help="Optional: what the bad doc should have said")
    prompts_parser.add_argument("--require-ask-user", dest="require_ask_user", action="store_true", help="Add an ASK USER guardrail to the record")
    prompts_parser.add_argument("--dry-run", action="store_true", help="Print the record and ratio; do not write to the dataset")
    prompts_parser.add_argument("--strict-ratio", dest="strict_ratio", action="store_true", help="Fail if adding would reduce the good:bad ratio below minimum")

    # Show Rich top-level help when no args
    if len(sys.argv) == 1:
        try:
            _show_rich_help(); sys.exit(0)
        except Exception:
            parser.print_help(); sys.exit(0)

    args = parser.parse_args()

    if not getattr(args, "command", None):
        try:
            _show_rich_help(); sys.exit(0)
        except Exception:
            parser.print_help(); sys.exit(0)

    if args.command == "lint":
        from agentspec import lint as _lint
        rc = _lint.run(args.target, min_lines=args.min_lines, strict=args.strict)
        sys.exit(0 if rc == 0 else 1)

    elif args.command == "extract":
        from agentspec import extract as _extract
        rc = _extract.run(args.target, fmt=args.format)
        sys.exit(0 if rc == 0 else 1)

    elif args.command == "generate":
        # If user asked for help implicitly, show Rich
        if args.provider in ("-h", "--help"):
            try:
                _show_generate_rich_help(); sys.exit(0)
            except Exception:
                pass
        from agentspec import generate as _gen
        rc = _gen.run(
            target=args.target,
            language="auto",
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
        sys.exit(0 if rc == 0 else 1)

    elif args.command == "strip":
        from agentspec import strip as _strip
        rc = _strip.run(target=args.target, mode=args.mode, dry_run=args.dry_run)
        sys.exit(0 if rc == 0 else 1)

    elif args.command == "prompts":
        if getattr(args, "add_example", False):
            # Allow positional path shorthand
            target_file = args.file or args.path
            if not target_file:
                print("❌ --file (or positional <path>) is required when using --add-example", file=sys.stderr)
                sys.exit(1)
            from agentspec.tools.add_example import _main_impl as _add_example
            _add_example(
                file_path=target_file,
                function_name=args.function,
                subject_function=args.subject_function,
                bad_output=args.bad_output,
                good_output=args.good_output,
                correction=args.correction,
                require_ask_user=args.require_ask_user,
                dry_run=args.dry_run,
                strict_ratio=args.strict_ratio,
            )
            sys.exit(0)
        try:
            _show_prompts_rich_help(); sys.exit(0)
        except Exception:
            parser.print_help(); sys.exit(0)

    else:
        try:
            _show_rich_help(); sys.exit(0)
        except Exception:
            parser.print_help(); sys.exit(0)


if __name__ == "__main__":
    main()
