#!/usr/bin/env python3
"""
agentspec CLI
-------------
Command-line interface for linting and extracting agent specifications.
"""

import argparse
import sys
from pathlib import Path

from agentspec import lint, extract


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
    else:
        parser.print_help()
        exit_code = 1
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
