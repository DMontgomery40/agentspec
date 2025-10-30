#!/usr/bin/env python3
import argparse
import sys
from agentspec import lint, extract

def main():
    parser = argparse.ArgumentParser(
        prog="agentspec",
        description="Lint, extract, and manage structured docstrings for AI agents."
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Lint
    lint_parser = subparsers.add_parser("lint", help="Lint files for required agent spec blocks.")
    lint_parser.add_argument("path", help="File or directory to check.")

    # Extract
    extract_parser = subparsers.add_parser("extract", help="Extract agent specs to markdown/json.")
    extract_parser.add_argument("path", help="File or directory to extract from.")
    extract_parser.add_argument("--json", action="store_true", help="Export as JSON instead of Markdown.")

    args = parser.parse_args()

    if args.command == "lint":
        sys.exit(lint.run(args.path))
    elif args.command == "extract":
        fmt = "json" if args.json else "markdown"
        sys.exit(extract.run(args.path, fmt))

if __name__ == "__main__":
    main()
