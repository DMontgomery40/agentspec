#!/usr/bin/env python3
"""
agentspec CLI
-------------
Command-line interface for linting and extracting agent specifications.
"""

import argparse
import sys
from pathlib import Path

# Import only what's needed at runtime per command to avoid importing optional deps unnecessarily
from agentspec import lint, extract
from agentspec.utils import load_env_from_dotenv


def _show_rich_help():
    """Display a beautiful Rich-formatted help screen."""
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
        "[green]agentspec generate src/core/ --critical --diff-summary[/green]",
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
    flags_table.add_row("--critical", "Ultra-accurate generation with verification (generate)")
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
    Brief entry point for the agentspec CLI application that dispatches to subcommands for linting, extracting, and generating AI-agent-focused docstrings.

    WHAT THIS DOES:
    - Parses command-line arguments using argparse to determine which subcommand to execute (lint, extract, or generate)
    - For "lint": validates agentspec docstring blocks in Python files against format requirements, with configurable minimum line counts and strict mode for treating warnings as errors
    - For "extract": reads Python files and exports agentspec docstring blocks in multiple formats (markdown, JSON, or agent-context optimized)
    - For "generate": uses Claude API to auto-generate verbose agentspec docstrings for functions lacking them, with optional dry-run preview and context-forcing via print statements
    - Routes the parsed arguments to the appropriate submodule handler (lint.run(), extract.run(), generate.run())
    - Exits with status code 0 on success or 1 on error/missing command
    - Prints help text and exits if no subcommand is provided

    DEPENDENCIES:
    - Called by: Entry point script (typically invoked as `python -m agentspec` or via setuptools console_scripts entry point)
    - Calls: lint.run(), extract.run(), generate.run() [defined in agentspec/lint.py, agentspec/extract.py, agentspec/generate.py respectively]
    - Imports used: argparse (stdlib), sys (stdlib)
    - External services: Claude API (only when generate command is used)

    WHY THIS APPROACH:
    - argparse is the standard Python CLI library and handles complex subcommand hierarchies with minimal boilerplate
    - Subcommand pattern allows independent command modules (lint, extract, generate) to be developed and tested separately without tight coupling
    - Three distinct operations (validate, export, generate) are logically grouped as CLI commands rather than separate scripts for better UX and distribution
    - Default values for --min-lines (10), --format ("markdown"), and --model ("claude-haiku-4-5") provide sensible out-of-the-box behavior
    - Explicit command dispatcher (if/elif chain) is more readable and debuggable than dict-based dispatch at this scale; easier for agents to trace execution flow
    - sys.exit() is called twice (for missing command and final status) to ensure process terminates cleanly; Python doesn't auto-exit from main()
    - Early exit on missing command prevents ambiguous behavior and ensures explicit user feedback via help text

    CHANGELOG:
    - Current: Initial implementation with three core subcommands (lint, extract, generate) and full CLI argument specification

    AGENT INSTRUCTIONS:
    - DO NOT modify the if/elif dispatch logic without updating corresponding submodule signatures in lint.py, extract.py, generate.py
    - DO NOT remove sys.exit() calls; they are required for proper CLI exit behavior
    - DO NOT add new subcommands without documenting them in this docstring's WHAT THIS DOES section
    - DO NOT change argument parameter names (e.g., "target", "format", "model") as they are consumed by downstream modules via args object attributes
    - ALWAYS preserve the --dry-run and --force-context flags for generate command; these are critical safety mechanisms
    - ALWAYS ensure all subcommand argument definitions include help text for end-user clarity
    - ALWAYS validate that new CLI flags have sensible defaults to avoid breaking existing automation scripts
    - NOTE: The generate command requires ANTHROPIC_API_KEY environment variable; missing this will cause generate.run() to fail with auth error
    - NOTE: model parameter accepts specific Claude model identifiers; using an invalid model name will fail at API call time, not argument parsing time
    - NOTE: The --strict flag converts linting warnings to hard errors; use with caution in CI/CD pipelines
    """
    # Load .env automatically (nearest) so users don't have to export manually
    load_env_from_dotenv()
    
    # Override help completely for main command
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ('--help', '-h')):
        _show_rich_help()
        sys.exit(0)
    
    # Use Rich-based help formatter (required dependency)
    from rich_argparse import RichHelpFormatter as _HelpFmt  # type: ignore

    parser = argparse.ArgumentParser(
        description="Agentspec: Structured, enforceable docstrings for AI agents",
        formatter_class=_HelpFmt,
        epilog=(
            "Quick start:\n"
            "  agentspec lint src/ --strict\n"
            "  agentspec extract src/ --format json > specs.json\n"
            "  agentspec generate src/ --dry-run\n"
            "  agentspec generate src/auth.py --critical --diff-summary\n\n"
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
        "--critical",
        action="store_true",
        help="CRITICAL MODE: Ultra-accurate generation with verification for important code (slower but more accurate)"
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
            critical=args.critical,
            terse=args.terse,
            diff_summary=args.diff_summary,
        )
    else:
        parser.print_help()
        exit_code = 1
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
