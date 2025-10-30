#!/usr/bin/env python3
"""
agentspec CLI
-------------
Command-line interface for linting and extracting agent specifications.
"""

import argparse
import sys
from pathlib import Path

from agentspec import lint, extract, generate


def main():
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
        exit_code = generate.run(
            args.target,
            dry_run=args.dry_run,
            force_context=args.force_context
        )
    else:
        parser.print_help()
        exit_code = 1
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
