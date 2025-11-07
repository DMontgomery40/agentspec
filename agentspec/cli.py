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
                """
        super().__init__(*args, **kwargs)
        self._all_valid_args = set()
    
    def _collect_valid_args(self, parser):
        """
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


def _check_python_version():
    """Check Python version meets minimum requirements."""
    import sys
    
    REQUIRED_MAJOR = 3
    REQUIRED_MINOR = 10
    
    current = sys.version_info[:2]
    if current[0] < REQUIRED_MAJOR or (current[0] == REQUIRED_MAJOR and current[1] < REQUIRED_MINOR):
        print(f"""
╔══════════════════════════════════════════════════════════════════════════╗
║                     ❌ PYTHON VERSION TOO OLD                            ║
╚══════════════════════════════════════════════════════════════════════════╝

Current Python: {current[0]}.{current[1]}
Required minimum: {REQUIRED_MAJOR}.{REQUIRED_MINOR}+

agentspec requires Python {REQUIRED_MAJOR}.{REQUIRED_MINOR}+ because it uses modern syntax (PEP 604 union types).

To upgrade, see: https://github.com/DMontgomery40/agentspec/blob/main/COMPATIBILITY.md
""", file=sys.stderr)
        sys.exit(1)


def main():
    """
        """
    # Check Python version before anything else
    _check_python_version()
    
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
    from rich_argparse import RawDescriptionRichHelpFormatter
    
    lint_parser = subparsers.add_parser(
        "lint",
        help="Validate agentspec blocks in Python files",
        description=(
            "Validate agentspec docstrings for presence, structure, and verbosity.\n\n"
            "Common flows:\n"
            "  • Enforce standards in CI: --strict (warnings cause non-zero exit)\n"
            "  • Raise minimum spec verbosity: --min-lines N\n"
            "  • Quick check of a single file before commit\n\n"
            "Behavior:\n"
            "  • Prints per-file errors and warnings\n"
            "  • Exits non-zero on errors (and on warnings when --strict)\n"
        ),
        epilog=(
            "Examples:\n"
            "  agentspec lint src/ --strict\n"
            "  agentspec lint src/payments.py --strict --min-lines 20\n"
            "  agentspec lint src/ --min-lines 15\n"
        ),
        formatter_class=RawDescriptionRichHelpFormatter,
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
            "  • Human-readable docs site or review bundle: (default) markdown\n"
            "  • Machine-readable output for pipelines: --format json\n"
            "  • Agent-executable context with print() prompts: --format agent-context\n\n"
            "Outputs:\n"
            "  • markdown → agent_specs.md\n"
            "  • json → agent_specs.json\n"
            "  • agent-context → AGENT_CONTEXT.md\n"
        ),
        epilog=(
            "Examples:\n"
            "  agentspec extract src/\n"
            "  agentspec extract src/ --format json > specs.json\n"
            "  agentspec extract src/auth.py --format agent-context\n"
        ),
        formatter_class=RawDescriptionRichHelpFormatter,
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
    from rich_argparse import RawDescriptionRichHelpFormatter
    
    generate_parser = subparsers.add_parser(
        "generate",
        help="Auto-generate verbose agentspec docstrings",
        description=(
            "Generate or refresh agentspec docstrings from code.\n\n"
            "Common flows:\n"
            "  • Keep docs in sync: --update-existing\n"
            "  • For ambiguous or uncommon code: avoid --terse for thoroughness\n"
            "  • Fit more into LLM context: --terse\n"
            "  • Add commit-intent summaries: --diff-summary\n\n"
            "Providers:\n"
            "  • Anthropic by model name (e.g., claude-haiku-4-5)\n"
            "  • OpenAI-compatible (incl. Ollama): --provider openai [--base-url URL]\n"
        ),
        epilog=(
            "Examples:\n"
            "  agentspec generate src/ --update-existing --terse\n"
            "  agentspec generate src/core/ --diff-summary\n"
            "  agentspec generate src/ --provider openai --model gpt-5\n"
            "  agentspec generate src/ --provider openai --model llama3.2 --base-url http://localhost:11434/v1\n"
        ),
        formatter_class=RawDescriptionRichHelpFormatter,
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
