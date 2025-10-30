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
    print(f"[AGENTSPEC_CONTEXT] main: Parses command-line arguments using argparse to determine which subcommand to execute (lint, extract, or generate) | For \"lint\": validates agentspec docstring blocks in Python files against format requirements, with configurable minimum line counts and strict mode for treating warnings as errors | For \"extract\": reads Python files and exports agentspec docstring blocks in multiple formats (markdown, JSON, or agent-context optimized)")
    parser = argparse.ArgumentParser(
        description="Agentspec: Structured, enforceable docstrings for AI agents"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Lint command
    lint_parser = subparsers.add_parser(
        "lint",
        help="Validate agentspec blocks in Python files"
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
        help="Extract agentspec blocks to markdown or JSON"
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
        help="Auto-generate verbose agentspec docstrings using Claude"
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
            as_agentspec_yaml=args.agentspec_yaml
        )
    else:
        parser.print_help()
        exit_code = 1
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
