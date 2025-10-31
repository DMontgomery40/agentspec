# 🤖 Extracted Agent Specifications

**This document is auto-generated for AI agent consumption.**

---

## FuzzyArgumentParser

**Location:** `agentspec/cli.py:17`

### What This Does

Custom ArgumentParser with fuzzy matching for unknown arguments.

### Raw YAML Block

```yaml
Custom ArgumentParser with fuzzy matching for unknown arguments.
```

---

## __init__

**Location:** `agentspec/cli.py:20`

### What This Does

Initializes a CLI handler instance by invoking the parent class constructor with all provided positional and keyword arguments, then establishes an empty set `_all_valid_args` to track valid argument names. This set serves as a container for accumulating and validating command-line argument specifications throughout the CLI handler's lifecycle. The initialization ensures the parent class is properly set up before introducing CLI-specific state management.

### Dependencies

**Calls:**
- `__init__`
- `set`
- `super`

### Why This Approach

The parent class initialization must occur first to establish base functionality and state. The `_all_valid_args` set is initialized as empty to support lazy accumulation of valid arguments as they are registered or discovered during CLI parsing and validation phases. Using a set provides O(1) lookup performance for argument validation checks and prevents duplicate argument names from being tracked.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT assume `_all_valid_args` is pre-populated; it must be explicitly populated by other methods before being used for validation, as initialization leaves it empty.**
- **DO NOT modify the parent class initialization signature or order; the `super().__init__()` call must precede any instance-specific state setup to maintain proper inheritance semantics.**
- **DO NOT use `_all_valid_args` for filtering or restricting arguments before it has been populated by the CLI handler's argument registration logic.**

### Changelog

- - no git history available

### Raw YAML Block

```yaml
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
```

---

## _collect_valid_args

**Location:** `agentspec/cli.py:55`

### What This Does

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

### Dependencies

**Calls:**
- `args_set.update`
- `choices.values`
- `isinstance`
- `self._collect_valid_args`
- `set`

### Why This Approach

This method enables comprehensive validation and discovery of all CLI arguments across a potentially nested parser hierarchy. By recursively traversing subparsers, it builds a complete inventory of valid arguments without requiring manual enumeration. This is useful for argument validation, help generation, or CLI introspection. The set-based approach ensures O(1) lookup performance for membership testing and automatic deduplication of shared argument names across parser levels.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT assume all actions have option_strings; some actions (like positional arguments) may lack them, which is why the conditional check `if action.option_strings` is necessary**
- **DO NOT modify the parser structure during traversal; this method is read-only and should not alter `_actions` or subparser choices**
- **DO NOT rely on this for runtime argument parsing; it is a metadata collection utility and does not validate or process actual CLI input**
- **DO NOT assume subparser choices are always populated; empty subparsers will contribute nothing to the result set**

### Changelog

- - no git history available

### Raw YAML Block

```yaml
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
```

---

## error

**Location:** `agentspec/cli.py:123`

### What This Does

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

### Dependencies

**Calls:**
- `arg.startswith`
- `arg_base.split`
- `difflib.SequenceMatcher`
- `difflib.get_close_matches`
- `enumerate`
- `error`
- `join`
- `len`
- `message.split`
- `partial_matches.append`
- `partial_word_matches.append`
- `prev_arg.startswith`
- `ratio`
- `self._collect_valid_args`
- `self.exit`
- `self.print_usage`
- `sorted`
- `split`
- `strip`
- `suggestions.append`
- `super`
- `unknown_arg.startswith`

### Why This Approach

Improves user experience by guiding users toward correct argument names instead of cryptic "unrecognized arguments" rejections. Handles common typos, hyphenation variations, and partial flag names that users might naturally attempt. The multi-stage matching strategy balances precision (word-component matches are most reliable) with recall (similarity matching catches typos). Caching valid arguments avoids repeated traversal of the parser tree. The approach prioritizes exact word matches over pure similarity to avoid suggesting semantically unrelated arguments.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT modify error messages for non-argument errors; always delegate to parent class via super().error() to preserve standard ArgumentParser behavior**
- **ALWAYS cache valid arguments in `_all_valid_args` to avoid repeated collection overhead during multiple error conditions**
- **DO NOT suggest matches below established similarity thresholds (0.6 for direct matches, 0.7 for combined flag+word, 0.5 for partial flag matches) to prevent misleading suggestions**
- **DO NOT suggest more than 3 alternatives per unknown argument to avoid overwhelming the user with options**
- **DO NOT apply word-component matching logic to non-flag arguments (those not starting with `--`) to avoid false positives**

### Changelog

- - no git history available

### Raw YAML Block

```yaml
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
```

---

## match_priority

**Location:** `agentspec/cli.py:267`

### What This Does

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

### Dependencies

**Calls:**
- `arg_base.split`
- `difflib.SequenceMatcher`
- `ratio`

### Why This Approach

This prioritization scheme balances exact semantic matching with fuzzy similarity.
Word-level matches (e.g., 'help' in '--show-help') are more reliable than character-level
similarity alone, reducing false positives when multiple arguments have similar character
sequences. The two-tier tuple return enables stable sorting: word matches always rank
above non-matches, and ties are broken by similarity ratio. This approach is appropriate
for CLI help/suggestion systems where semantic correctness outweighs minor typo tolerance.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT rely solely on sequence similarity without word matching, as it may suggest semantically unrelated arguments that happen to share character patterns**
- **DO NOT modify unknown_arg or the candidate argument in-place; this function must be side-effect-free to work correctly in sorting contexts**
- **DO NOT assume the candidate always starts with '--'; validation should occur in the caller before invoking this function**
- **DO NOT use this function outside a context where unknown_arg and unknown_base are defined in the enclosing scope; refactor to pass them as parameters if reusing elsewhere**

### Changelog

- - no git history available

### Raw YAML Block

```yaml
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
```

---

## _show_rich_help

**Location:** `agentspec/cli.py:351`

### What This Does

Renders a formatted help screen to stdout using Rich library with three main sections:
1. Title panel introducing Agentspec as "Structured, enforceable docstrings for AI agents"
2. Commands table listing three primary commands (lint, extract, generate) with descriptions
3. Quick-start examples panel showing common usage patterns for each command
4. Key flags reference table documenting important CLI flags grouped by command (--strict for lint, --format for extract, --terse/--update-existing/--diff-summary for generate)

The function constructs Rich Table and Panel objects with styled headers, colored text, and box drawing, then prints each section sequentially to console. No return value; output is side-effect only (stdout).

Edge cases: Function assumes Rich library is available at runtime; will raise ImportError if Rich is not installed. Function produces no output if console.print() fails silently (e.g., in non-TTY environments, Rich may suppress formatting).

### Dependencies

**Calls:**
- `Console`
- `Panel`
- `Panel.fit`
- `Table`
- `commands_table.add_column`
- `commands_table.add_row`
- `console.print`
- `flags_table.add_column`
- `flags_table.add_row`

### Why This Approach

Provides an interactive, discoverable CLI help interface without requiring external help text files or manual markdown documentation. Rich formatting (colors, tables, panels, styled text) significantly improves terminal UX and makes command discovery more intuitive than plain text help. Embedding help generation in code ensures help text stays synchronized with actual CLI implementation. Organizing help into logical sections (commands, examples, flags) reduces cognitive load for new users exploring the tool.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT call this function in non-interactive environments expecting plain text output; Rich may strip formatting or fail silently in non-TTY contexts.**
- **DO NOT assume Rich library is pre-installed; imports occur inside function body, so missing Rich will raise ImportError at runtime rather than at module load time.**
- **ALWAYS output directly to stdout via Rich Console; do not attempt to capture or redirect return value (function returns None).**
- **DO NOT modify console output after printing; Rich Console.print() is not idempotent and subsequent calls will append rather than replace.**

### Changelog

- 2025-10-31: Clean up docstring formatting

### Raw YAML Block

```yaml
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

  - "2025-10-31: Clean up docstring formatting"
```

---

## _check_python_version

**Location:** `agentspec/cli.py:473`

### What This Does

Check Python version meets minimum requirements.

### Raw YAML Block

```yaml
Check Python version meets minimum requirements.
```

---

## main

**Location:** `agentspec/cli.py:500`

### What This Does

CLI entry point that parses command-line arguments and dispatches to three subcommands: lint, extract, and generate.

**Lint subcommand**: Validates agentspec docstring blocks in Python files against format and verbosity requirements. Accepts target (file or directory), --min-lines (minimum lines in agentspec blocks, default 10), and --strict flag (treats warnings as errors). Calls lint.run() with parsed arguments.

**Extract subcommand**: Exports agentspec blocks from Python files to portable formats. Accepts target (file or directory) and --format flag (choices: markdown, json, agent-context; default markdown). Calls extract.run() with parsed arguments.

**Generate subcommand**: Auto-generates or refreshes agentspec docstrings using Claude or OpenAI-compatible APIs. Accepts target (file or directory), --dry-run (preview without modifying), --force-context (add print() statements for LLM context), --model (model identifier), --agentspec-yaml (embed YAML block), --provider (auto/anthropic/openai, default auto), --base-url (for OpenAI-compatible endpoints), --update-existing (regenerate existing docstrings), --terse (shorter output), and --diff-summary (add git diff summaries). Lazy-imports generate module to avoid requiring anthropic dependency unless command is used. Calls generate.run() with all parsed arguments.

**Behavior**: Loads .env file automatically via load_env_from_dotenv(). Displays rich-formatted help if no arguments or --help flag provided. Uses argparse with RichHelpFormatter for improved CLI UX. Routes parsed args to appropriate submodule handler (lint.run(), extract.run(), or generate.run()). Exits with status code 0 on success or 1 on error/missing command. Prints help and exits if no subcommand provided.

**Edge cases**: Missing ANTHROPIC_API_KEY environment variable causes generate.run() to fail with auth error. Invalid Claude model names fail at API call time, not argument parsing time. --strict flag converts linting warnings to hard errors; use with caution in CI/CD pipelines.

### Dependencies

**Calls:**
- `FuzzyArgumentParser`
- `_show_rich_help`
- `extract.run`
- `extract_parser.add_argument`
- `generate.run`
- `generate_parser.add_argument`
- `len`
- `lint.run`
- `lint_parser.add_argument`
- `load_env_from_dotenv`
- `parser.add_subparsers`
- `parser.parse_args`
- `parser.print_help`
- `subparsers.add_parser`
- `sys.exit`

### Why This Approach

Subcommand pattern isolates lint, extract, and generate logic for independent testing, maintenance, and feature development without tight coupling. Rich-based help formatter improves CLI UX for both end users and agent consumption. Lazy import of generate module avoids requiring anthropic dependency unless generate command is explicitly invoked, reducing installation friction for users who only need lint/extract. Early exit on missing command prevents ambiguous behavior and ensures explicit user feedback via help text. Explicit if/elif dispatch chain is more readable and debuggable than dict-based dispatch at this scale; easier for agents to trace execution flow. Default values (--min-lines=10, --format=markdown, --model=claude-haiku-4-5) provide sensible out-of-the-box behavior for common workflows. sys.exit() calls ensure process terminates cleanly; Python does not auto-exit from main(). Three distinct operations (validate, export, generate) are grouped as CLI commands rather than separate scripts for better UX and unified distribution.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT modify the if/elif dispatch logic without updating corresponding submodule signatures in lint.py, extract.py, and generate.py**
- **DO NOT remove sys.exit() calls; they are required for proper CLI exit behavior and process termination**
- **DO NOT add new subcommands without documenting them in this docstring's WHAT section and updating help text**
- **DO NOT change argument parameter names (e.g., target, format, model, provider, base_url) as they are consumed by downstream modules via args object attributes**
- **DO NOT remove or rename --dry-run and --force-context flags for generate; these are critical safety mechanisms**
- **ALWAYS preserve help text on all CLI flags for end-user clarity and discoverability**
- **ALWAYS validate that new CLI flags have sensible defaults to avoid breaking existing automation scripts and CI/CD pipelines**
- **ALWAYS ensure subcommand descriptions include common workflows and examples in epilog for agent/user guidance**
- **ALWAYS lazy-import optional dependencies (like generate module) to avoid requiring them unless explicitly needed**
- **ALWAYS call load_env_from_dotenv() at entry point to allow users to configure via .env without manual export**

### Changelog

- 2025-10-31: Clean up docstring formatting

### Raw YAML Block

```yaml
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

  - "2025-10-31: Clean up docstring formatting"
```

---

## _get_function_calls

**Location:** `agentspec/collect.py:26`

### What This Does

```python
"""
Extract all function call names from an AST node as a sorted, deduplicated list.

### Raw YAML Block

```yaml
```python
"""
Extract all function call names from an AST node as a sorted, deduplicated list.

WHAT:
- Walks AST to find all ast.Call nodes and extracts callable names
- Handles simple calls (func), method calls (obj.method), and chained attributes (attr.method)
- Returns sorted, deduplicated list with empty strings filtered out

WHY:
- Enables static dependency analysis without code execution
- Qualified names preserve semantic context (local vs method calls)
- Sorting ensures deterministic output for reproducible analysis

GUARDRAILS:
- DO NOT remove isinstance() checks; they distinguish ast.Name from ast.Attribute node types
- DO NOT modify ast.walk() traversal without understanding it visits all nested nodes
- DO NOT alter sorting behavior; output must remain deterministic
- ALWAYS preserve both ast.Name and ast.Attribute handling for complete call pattern coverage
- ALWAYS filter empty strings to prevent malformed entries in results
"""
```

DEPENDENCIES (from code analysis):
Calls: ast.walk, calls.append, isinstance, sorted
Imports: __future__.annotations, ast, difflib, pathlib.Path, re, subprocess, typing.Any, typing.Dict, typing.List


CHANGELOG (from git history):
- 2025-10-30: feat: enhance CLI help and add rich formatting support
- Called by: agentspec/collect.py module-level analysis functions (inferred from file context)
- Calls: ast.walk (standard library AST traversal), calls.append (list mutation), isinstance (type checking), sorted (list ordering)
- Imports used: ast (Abstract Syntax Tree parsing and node types), typing.List (type hints)
- External services: None; this is pure static analysis using Python's built-in ast module
- Current implementation: Extracts all function call names from an AST node by walking the tree, handling simple calls, method calls, and chained attributes, then returns a sorted deduplicated list.
- DO NOT modify the ast.walk() traversal logic without understanding that it visits all nodes in the tree
- DO NOT remove the isinstance() type checks, as they are essential for correctly distinguishing between different call patterns
- DO NOT change the set deduplication without considering that it removes duplicate function names across the entire AST
- DO NOT alter the sorting behavior without ensuring output remains deterministic
- ALWAYS preserve the handling of both ast.Name and ast.Attribute node types
- ALWAYS maintain the qualified name construction for method calls (the "base.method" format)
- ALWAYS filter out empty strings from the final result
- NOTE: This function performs static analysis only and does not execute code; it cannot detect dynamically-called functions or functions called via eval/exec
- NOTE: The base detection for chained attributes (ast.Attribute.value being another ast.Attribute) only captures the immediate parent attribute name, not the full chain; calls like `a.b.c()` will be recorded as "b.c", not "a.b.c"
- NOTE: Edge case—if an ast.Attribute node has a base that is neither ast.Name nor ast.Attribute (e.g., a function call result), the base will be None and only the method name will be recorded
-    print(f"[AGENTSPEC_CONTEXT] _get_function_calls: Called by: agentspec/collect.py module-level analysis functions (inferred from file context) | Calls: ast.walk (standard library AST traversal), calls.append (list mutation), isinstance (type checking), sorted (list ordering) | Imports used: ast (Abstract Syntax Tree parsing and node types), typing.List (type hints)")
- 2025-10-30: feat: robust docstring generation and Haiku defaults


FUNCTION CODE DIFF SUMMARY (LLM-generated):
**Commit 1 (2025-10-30):** Removed debug context print statement from function.

**Commit 2 (2025-10-30):** Implement function call extraction with AST traversal.
```

---

## _get_module_imports

**Location:** `agentspec/collect.py:100`

### What This Does

```python
"""
Extracts and returns a sorted, deduplicated list of top-level module imports from an AST tree.

### Raw YAML Block

```yaml
```python
"""
Extracts and returns a sorted, deduplicated list of top-level module imports from an AST tree.

WHAT:
- Traverses AST body collecting `import X` and `from X import Y` statements
- For `import`: extracts module name; for `from...import`: joins module and alias with dots
- Handles relative imports (module=None), deduplicates via set, filters empty strings, returns sorted list

WHY:
- Provides coarse-grained dependency analysis sufficient for module-level context without recursive overhead
- Sorted output ensures deterministic, reproducible results for consistent agent analysis

GUARDRAILS:
- DO NOT remove sorted() call; deterministic ordering required for reproducible dependency tracking
- DO NOT change isinstance checks to single condition; Import and ImportFrom have different structures
- DO NOT modify dot-joining logic without considering relative imports where module is None
- ALWAYS preserve getattr fallback to [] when tree.body is missing
- ALWAYS return List[str] as specified in type hint
"""
```

DEPENDENCIES (from code analysis):
Calls: getattr, imports.append, isinstance, join, sorted
Imports: __future__.annotations, ast, difflib, pathlib.Path, re, subprocess, typing.Any, typing.Dict, typing.List


CHANGELOG (from git history):
- 2025-10-30: feat: enhance CLI help and add rich formatting support
- Traverses the abstract syntax tree (AST) of a Python module to identify all top-level import statements
- Handles both `import X` statements (ast.Import nodes) and `from X import Y` statements (ast.ImportFrom nodes)
- For `import` statements, extracts the module name directly from the alias
- For `from...import` statements, constructs the full import path by joining the source module with the imported name using dot notation, handling cases where the module is None (bare `from ... import`)
- Deduplicates the collected imports by converting to a set, filters out empty strings, and returns a sorted list for consistent ordering
- Returns an empty list if the AST has no body or contains no import statements
- Called by: agentspec/collect.py module-level analysis functions (inferred from context of coarse dependency collection)
- Calls: getattr (built-in), isinstance (built-in), sorted (built-in), str.join (built-in)
- Imports used: ast (standard library for AST node types), typing.List (type hints)
- External services: None
- Uses getattr with a default empty list to safely access the body attribute, preventing AttributeError if the AST node lacks a body (defensive programming)
- Checks isinstance for both ast.Import and ast.ImportFrom separately because they have different structures: Import has a flat names list, while ImportFrom has both a module and a names list
- Constructs full import paths for ImportFrom by joining module and alias name with dots, which provides more granular dependency information than just the module name
- Handles the edge case where ImportFrom.module is None (occurs with relative imports like `from . import foo`) by using `or ""` and filtering empty parts
- Deduplicates using set comprehension before sorting to ensure O(n log n) performance and eliminate redundant entries that might arise from multiple import statements importing the same module
- Returns sorted output for deterministic, reproducible results across runs, which is critical for consistent dependency tracking and agent analysis
- Alternative approach (not used): Could have used ast.walk() to find all imports recursively, but this function intentionally restricts to top-level imports only for "coarse" dependency context as documented in the docstring
- Current implementation: Extracts top-level imports from AST module body, deduplicates, and returns sorted list for dependency analysis.
- DO NOT modify the deduplication logic (set conversion) without understanding its impact on downstream dependency analysis
- DO NOT remove the sorted() call, as deterministic ordering is required for consistent agent analysis
- DO NOT change the isinstance checks to use a single condition without testing both Import and ImportFrom node types separately
- DO NOT modify the dot-joining logic for ImportFrom without considering relative imports (where module is None)
- ALWAYS preserve the filtering of empty strings in the set comprehension
- ALWAYS maintain the getattr fallback to [] for safety when tree.body is missing
- ALWAYS return a List[str] type as specified in the type hint
- NOTE: This function assumes the input is a valid ast.AST object; passing invalid AST structures may cause unexpected behavior
- NOTE: The function only captures top-level imports; nested imports inside functions or classes are intentionally excluded per the "coarse dependency context" design
- NOTE: Relative imports (from . import X) will have their module set to None, which is handled by the `or ""` pattern but results in just the alias name being returned
-    print(f"[AGENTSPEC_CONTEXT] _get_module_imports: Traverses the abstract syntax tree (AST) of a Python module to identify all top-level import statements | Handles both `import X` statements (ast.Import nodes) and `from X import Y` statements (ast.ImportFrom nodes) | For `import` statements, extracts the module name directly from the alias")
- 2025-10-30: feat: robust docstring generation and Haiku defaults


FUNCTION CODE DIFF SUMMARY (LLM-generated):
# Commit Analysis

**Commit 1 (2025-10-30):** Removed debug print statement from function.

**Commit 2 (2025-10-30):** Implement AST traversal to extract module imports.
```

---

## collect_changelog_diffs

**Location:** `agentspec/collect.py:183`

### What This Does

```python
"""
Extract function-level git history for the last 5 commits using git log -L.

### Raw YAML Block

```yaml
```python
"""
Extract function-level git history for the last 5 commits using git log -L.

WHAT:
- Retrieves function-specific changes across last 5 commits via `git log -L` with metadata (hash, date, message, diff)
- Parses git output by splitting on `COMMIT_START|||` delimiter to isolate commit metadata from diffs
- Returns list of dicts with keys: `hash`, `date` (YYYY-MM-DD), `message`, `diff`

WHY:
- Function-level tracking isolates relevant changes from file-wide noise for precise historical context
- Enables LLM-based summarization of function evolution without embedding raw diffs in docstrings
- Silent failure on git errors allows graceful degradation in non-git or offline environments

GUARDRAILS:
- DO NOT include returned diffs directly in docstrings; pass to LLM for summarization only
- DO NOT raise exceptions on git failures or parsing errors; always return empty list
- DO NOT assume function exists in git history; missing functions return empty list silently
- ALWAYS use `errors="ignore"` when decoding subprocess output to handle non-UTF8 characters
- ALWAYS validate delimiter split produces at least 4 parts before accessing metadata fields
"""
```

DEPENDENCIES (from code analysis):
Calls: commits.append, decode, diff_lines.append, join, len, line.split, line.startswith, out.splitlines, subprocess.check_output
Imports: __future__.annotations, ast, difflib, pathlib.Path, re, subprocess, typing.Any, typing.Dict, typing.List


CHANGELOG (from git history):
- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features


FUNCTION CODE DIFF SUMMARY (LLM-generated):
Extract function-level git history with dates and commit messages.
```

---

## _extract_function_source_without_docstring

**Location:** `agentspec/collect.py:268`

### What This Does

```python
"""
Extract function source code with docstring and comment-only lines removed.

### Raw YAML Block

```yaml
```python
"""
Extract function source code with docstring and comment-only lines removed.

WHAT:
- Parses source via AST to locate function definition (sync/async), returns cleaned body
- Removes leading docstring (handles ast.Constant and legacy ast.Str for version compatibility) and all comment-only lines
- Returns empty string if function not found or parsing fails

WHY:
- Enables clean function body extraction for downstream analysis without documentation noise
- AST-based approach ensures accurate docstring detection across Python versions
- Defensive exception handling prevents crashes on invalid input

GUARDRAILS:
- DO NOT assume docstring exists; always check body presence and first statement type before removal
- DO NOT fail on malformed source; catch all exceptions and return empty string
- DO NOT use absolute line indices directly for slicing; always map to relative indices by subtracting start offset
- ALWAYS call lstrip() when checking for comment-only lines to correctly identify pure comments
"""
```

DEPENDENCIES (from code analysis):
Calls: ast.parse, ast.walk, cleaned.append, getattr, hasattr, isinstance, join, ln.lstrip, max, src.split, stripped.startswith
Imports: __future__.annotations, ast, difflib, pathlib.Path, re, subprocess, typing.Any, typing.Dict, typing.List


CHANGELOG (from git history):
- 2025-10-30: feat: enhance CLI help and add rich formatting support


FUNCTION CODE DIFF SUMMARY (LLM-generated):
Extract function source code while removing docstrings and comments.
```

---

## collect_function_code_diffs

**Location:** `agentspec/collect.py:346`

### What This Does

```python
"""
Collect per-commit code diffs for a function from git history, filtering meaningful changes only.

### Raw YAML Block

```yaml
```python
"""
Collect per-commit code diffs for a function from git history, filtering meaningful changes only.

WHAT:
- Retrieves up to `limit` recent commits touching the file, extracts function body at each commit and parent, generates unified diff, filters to +/- lines only
- Excludes file headers (+++/---), hunk markers (@@), context lines, and comment-only changes
- Returns empty list on git failure or if function absent in both versions

WHY:
- Isolates functional evolution by removing noise (docstrings, comments, diff metadata) that obscures logic changes
- Gracefully handles git failures and missing commits rather than raising exceptions, enabling partial results in varied environments

GUARDRAILS:
- DO NOT include file headers, hunk markers, context lines, or comment-only changes in output
- DO NOT return results if git operations fail; return empty list instead
- ALWAYS skip commits where function body absent in both parent and current versions
- ALWAYS filter out malformed log entries lacking three fields (hash, date, message)
"""
```

DEPENDENCIES (from code analysis):
Calls: _extract_function_source_without_docstring, changes.append, content.lstrip, curr_func.splitlines, decode, difflib.unified_diff, dl.startswith, int, join, len, line.split, ln.strip, log_out.splitlines, prev_func.splitlines, results.append, startswith, str, subprocess.check_output
Imports: __future__.annotations, ast, difflib, pathlib.Path, re, subprocess, typing.Any, typing.Dict, typing.List


CHANGELOG (from git history):
- 2025-10-30: feat: enhance CLI help and add rich formatting support


FUNCTION CODE DIFF SUMMARY (LLM-generated):
Extract function-level code diffs across git history with limit support.
```

---

## collect_metadata

**Location:** `agentspec/collect.py:461`

### What This Does

```python
"""
Extracts deterministic metadata (function calls, imports, git history) from a Python function via AST parsing and git log.

### Raw YAML Block

```yaml
```python
"""
Extracts deterministic metadata (function calls, imports, git history) from a Python function via AST parsing and git log.

WHAT:
- Parses Python file AST to locate target function (sync or async) and extracts internal calls and module imports
- Retrieves function-specific git history using `git log -L :func_name:filepath` (up to 5 most recent commits), filtering to commit message lines only
- Returns `{"deps": {"calls": [...], "imports": [...]}, "changelog": [...]}` on success; empty dict `{}` on any failure (function not found, parse error, exception)
- Edge cases: First AST match used if function name collides; git unavailable defaults changelog to `["- no git history available"]`; no commits found defaults to `["- none yet"]`

WHY:
- AST-based parsing provides syntactically-aware function identification, avoiding false positives from strings/comments
- Git `-L` option provides function-specific history without manual line tracking; automatically handles boundary changes across commits
- Fail-closed exception handling (return `{}`) ensures agent pipelines never crash; metadata collection is non-critical and degrades gracefully
- Separate try-except for git allows partial metadata return (deps without changelog) if git fails

GUARDRAILS:
- DO NOT raise exceptions instead of returning `{}`; breaks fail-closed contract required by agent pipelines
- DO NOT remove `errors="ignore"` from `.decode()` without handling git output encoding edge cases
- DO NOT modify git command structure; `-L :func_name:filepath` syntax is required for accurate line-range filtering
- DO NOT recursively analyze imported modules or follow call chains; keep analysis local and deterministic
- ALWAYS preserve distinction between `ast.FunctionDef` and `ast.AsyncFunctionDef` to support both sync and async functions
- ALWAYS strip whitespace from changelog lines to avoid formatting artifacts
- ALWAYS filter git output to only lines matching commit format (starts with `"- YYYY-MM-DD:"` and contains hash in parentheses)
"""
```

DEPENDENCIES (from code analysis):
Calls: _get_function_calls, _get_module_imports, ast.parse, ast.walk, commit_pattern.match, decode, filepath.read_text, isinstance, join, len, lines.append, ln.strip, out.splitlines, print, re.compile, str, subprocess.check_output
Imports: __future__.annotations, ast, difflib, pathlib.Path, re, subprocess, typing.Any, typing.Dict, typing.List


CHANGELOG (from git history):
- 2025-10-30: feat: enhance CLI help and add rich formatting support
- Parses a Python file using the `ast` module to locate a target function by name (supporting both sync and async function definitions)
- Extracts two categories of deterministic metadata: (1) `deps.calls` containing all function calls made within the target function via `_get_function_calls()`, and (2) `deps.imports` containing all module-level imports in the file via `_get_module_imports()`
- Attempts to retrieve git changelog history specific to the target function using `git log -L` with line-range filtering, capturing up to 5 most recent commits with short dates and commit messages
- Returns a dictionary with structure `{"deps": {"calls": [...], "imports": [...]}, "changelog": [...]}` on success, or an empty dict `{}` if the function cannot be found, parsing fails, or any exception occurs during metadata collection
- Gracefully degrades: if git history is unavailable, changelog defaults to `["- no git history available"]`; if no commits are found, defaults to `["- none yet"]`
- Called by: [Inferred to be called by documentation generation or agent analysis pipelines that need to understand function dependencies]
- Calls: `_get_function_calls()` [extracts function call names from AST node], `_get_module_imports()` [extracts top-level import statements], `ast.parse()` [parses Python source into AST], `ast.walk()` [traverses AST nodes], `filepath.read_text()` [reads file content], `subprocess.check_output()` [executes git log command], `isinstance()` [type checking for FunctionDef/AsyncFunctionDef], `str.strip()` [whitespace cleanup], `str.splitlines()` [line splitting], `str.decode()` [bytes to string conversion]
- Imports used: `__future__.annotations` [enables postponed evaluation of type hints], `ast` [abstract syntax tree parsing], `pathlib.Path` [filesystem path handling], `subprocess` [external process execution], `typing.Any` [generic type annotation], `typing.Dict` [dictionary type annotation], `typing.List` [list type annotation]
- External services: Git command-line tool (required for changelog generation; gracefully fails if unavailable)
- AST-based parsing was chosen over regex or string matching because it provides accurate, syntactically-aware identification of function definitions and their internal calls, avoiding false positives from comments, strings, or nested scopes
- The `ast.walk()` approach iterates through all nodes rather than using a visitor pattern because it is simpler for one-off lookups and the performance cost is negligible for typical file sizes
- Git's `-L` option (line-range filtering) was selected over parsing all commits because it provides function-specific history without requiring manual line number tracking or heuristic-based filtering
- Fail-closed exception handling (returning `{}` on any error) was chosen to ensure the function never crashes the calling agent; metadata collection is non-critical and should degrade gracefully
- The `errors="ignore"` parameter in `.decode()` prevents UnicodeDecodeError from malformed git output, prioritizing robustness over strict validation
- Separate try-except blocks for git operations allow the function to return partial metadata (deps without changelog) if git fails, rather than losing all data
- The function does NOT recursively analyze imported modules or follow call chains, keeping analysis local and deterministic
- Current implementation: Parses Python AST to extract function metadata (calls and imports) and augments with git commit history using line-range filtering, with graceful degradation on parsing or git failures.
- DO NOT modify the exception handling to raise errors instead of returning `{}`; this breaks the fail-closed contract
- DO NOT remove the `errors="ignore"` parameter from `.decode()` without understanding git output encoding edge cases
- DO NOT change the git command structure without verifying that `-L :func_name:filepath` syntax is preserved for accurate line-range filtering
- DO NOT assume `_get_function_calls()` or `_get_module_imports()` are available; verify they exist in the same module
- ALWAYS preserve the distinction between `ast.FunctionDef` and `ast.AsyncFunctionDef` to support both sync and async functions
- ALWAYS return an empty dict on failure rather than raising exceptions, to maintain compatibility with agent pipelines
- ALWAYS strip whitespace from changelog lines to avoid formatting artifacts
- NOTE: This function depends on external git availability; it will silently degrade if git is not installed or the filepath is not in a git repository
- NOTE: The `-n5` limit on git log means only the 5 most recent commits are captured; older history is discarded
- NOTE: If a function name appears multiple times in a file (e.g., in different scopes), only the first match via `ast.walk()` is used; this may not be the intended function if there are name collisions
-    print(f"[AGENTSPEC_CONTEXT] collect_metadata: Parses a Python file using the `ast` module to locate a target function by name (supporting both sync and async function definitions) | Extracts two categories of deterministic metadata: (1) `deps.calls` containing all function calls made within the target function via `_get_function_calls()`, and (2) `deps.imports` containing all module-level imports in the file via `_get_module_imports()` | Attempts to retrieve git changelog history specific to the target function using `git log -L` with line-range filtering, capturing up to 5 most recent commits with short dates and commit messages")
- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features
- Parses a Python file using the `ast` module to locate a target function by name (supporting both sync and async function definitions)
- Extracts two categories of deterministic metadata: (1) `deps.calls` containing all function calls made within the target function via `_get_function_calls()`, and (2) `deps.imports` containing all module-level imports in the file via `_get_module_imports()`
- Attempts to retrieve git changelog history specific to the target function using `git log -L` with line-range filtering, capturing up to 5 most recent commits with short dates and commit messages
- Returns a dictionary with structure `{"deps": {"calls": [...], "imports": [...]}, "changelog": [...]}` on success, or an empty dict `{}` if the function cannot be found, parsing fails, or any exception occurs during metadata collection
- Gracefully degrades: if git history is unavailable, changelog defaults to `["- no git history available"]`; if no commits are found, defaults to `["- none yet"]`
- Called by: [Inferred to be called by documentation generation or agent analysis pipelines that need to understand function dependencies]
- Calls: `_get_function_calls()` [extracts function call names from AST node], `_get_module_imports()` [extracts top-level import statements], `ast.parse()` [parses Python source into AST], `ast.walk()` [traverses AST nodes], `filepath.read_text()` [reads file content], `subprocess.check_output()` [executes git log command], `isinstance()` [type checking for FunctionDef/AsyncFunctionDef], `str.strip()` [whitespace cleanup], `str.splitlines()` [line splitting], `str.decode()` [bytes to string conversion]
- Imports used: `__future__.annotations` [enables postponed evaluation of type hints], `ast` [abstract syntax tree parsing], `pathlib.Path` [filesystem path handling], `subprocess` [external process execution], `typing.Any` [generic type annotation], `typing.Dict` [dictionary type annotation], `typing.List` [list type annotation]
- External services: Git command-line tool (required for changelog generation; gracefully fails if unavailable)
- AST-based parsing was chosen over regex or string matching because it provides accurate, syntactically-aware identification of function definitions and their internal calls, avoiding false positives from comments, strings, or nested scopes
- The `ast.walk()` approach iterates through all nodes rather than using a visitor pattern because it is simpler for one-off lookups and the performance cost is negligible for typical file sizes
- Git's `-L` option (line-range filtering) was selected over parsing all commits because it provides function-specific history without requiring manual line number tracking or heuristic-based filtering
- Fail-closed exception handling (returning `{}` on any error) was chosen to ensure the function never crashes the calling agent; metadata collection is non-critical and should degrade gracefully
- The `errors="ignore"` parameter in `.decode()` prevents UnicodeDecodeError from malformed git output, prioritizing robustness over strict validation
- Separate try-except blocks for git operations allow the function to return partial metadata (deps without changelog) if git fails, rather than losing all data
- The function does NOT recursively analyze imported modules or follow call chains, keeping analysis local and deterministic
- Current implementation: Parses Python AST to extract function metadata (calls and imports) and augments with git commit history using line-range filtering, with graceful degradation on parsing or git failures.
- DO NOT modify the exception handling to raise errors instead of returning `{}`; this breaks the fail-closed contract
- DO NOT remove the `errors="ignore"` parameter from `.decode()` without understanding git output encoding edge cases
- DO NOT change the git command structure without verifying that `-L :func_name:filepath` syntax is preserved for accurate line-range filtering
- DO NOT assume `_get_function_calls()` or `_get_module_imports()` are available; verify they exist in the same module
- ALWAYS preserve the distinction between `ast.FunctionDef` and `ast.AsyncFunctionDef` to support both sync and async functions
- ALWAYS return an empty dict on failure rather than raising exceptions, to maintain compatibility with agent pipelines
- ALWAYS strip whitespace from changelog lines to avoid formatting artifacts
- NOTE: This function depends on external git availability; it will silently degrade if git is not installed or the filepath is not in a git repository
- NOTE: The `-n5` limit on git log means only the 5 most recent commits are captured; older history is discarded
- NOTE: If a function name appears multiple times in a file (e.g., in different scopes), only the first match via `ast.walk()` is used; this may not be the intended function if there are name collisions
-            lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
- 2025-10-30: feat: robust docstring generation and Haiku defaults


FUNCTION CODE DIFF SUMMARY (LLM-generated):
1. Remove verbose debug print statement from function.
2. Filter git log output to only include formatted changelog lines.
3. Initial implementation of metadata collection with AST parsing and git history.
```

---

## _extract_block

**Location:** `agentspec/extract.py:35`

### What This Does

Extracts the agentspec metadata block from a Python docstring by locating content between "---agentspec" and "

### Raw YAML Block

```yaml
what: |
  Extracts the agentspec metadata block from a Python docstring by locating content between "---agentspec" and "
```

---

## _parse_yaml_block

**Location:** `agentspec/extract.py:101`

### What This Does

Safely parses a YAML block string into a Python dictionary or other valid YAML structure.

Accepts any string input and attempts to parse it using yaml.safe_load(). Returns the parsed result (dict, list, scalar, or None) on success. Returns None silently if the input contains invalid YAML syntax or raises a yaml.YAMLError during parsing.

Handles edge cases: empty strings, whitespace-only strings, and malformed YAML all return None without raising exceptions. Valid YAML that parses to non-dict types (lists, strings, integers, booleans, None) is returned as-is; callers are responsible for type validation before treating results as dictionaries.

### Dependencies

**Calls:**
- `yaml.safe_load`

### Why This Approach

Uses yaml.safe_load() instead of yaml.load() to prevent code injection attacks when parsing YAML from untrusted sources such as docstrings and code comments. The fail-silent pattern (returning None on parse errors) allows graceful degradation when optional metadata is missing or malformed, avoiding exception propagation and enabling callers to distinguish between "no YAML found" and "YAML found but invalid" through a single None return value.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT use yaml.load() or yaml.unsafe_load()—these are security vulnerabilities that allow arbitrary code execution from untrusted YAML input**
- **DO NOT remove the try/except block or convert to exception-raising behavior—silent failure is intentional for optional metadata handling**
- **DO NOT return empty dict {} or False on parse failure—always return None for caller clarity and type consistency**
- **ALWAYS use yaml.safe_load() specifically to maintain security posture**
- **{'NOTE': 'Type hint declares Dict return but yaml.safe_load() can return list, string, int, bool, or None—callers must validate the actual type before accessing dict keys'}**

### Changelog

- 2025-10-31: Clean up docstring formatting

### Raw YAML Block

```yaml
what: |
  Safely parses a YAML block string into a Python dictionary or other valid YAML structure.

  Accepts any string input and attempts to parse it using yaml.safe_load(). Returns the parsed result (dict, list, scalar, or None) on success. Returns None silently if the input contains invalid YAML syntax or raises a yaml.YAMLError during parsing.

  Handles edge cases: empty strings, whitespace-only strings, and malformed YAML all return None without raising exceptions. Valid YAML that parses to non-dict types (lists, strings, integers, booleans, None) is returned as-is; callers are responsible for type validation before treating results as dictionaries.
deps:
      calls:
        - yaml.safe_load
      imports:
        - agentspec.utils.collect_python_files
        - ast
        - dataclasses.asdict
        - dataclasses.dataclass
        - dataclasses.field
        - json
        - pathlib.Path
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - yaml


why: |
  Uses yaml.safe_load() instead of yaml.load() to prevent code injection attacks when parsing YAML from untrusted sources such as docstrings and code comments. The fail-silent pattern (returning None on parse errors) allows graceful degradation when optional metadata is missing or malformed, avoiding exception propagation and enabling callers to distinguish between "no YAML found" and "YAML found but invalid" through a single None return value.

guardrails:
  - DO NOT use yaml.load() or yaml.unsafe_load()—these are security vulnerabilities that allow arbitrary code execution from untrusted YAML input
  - DO NOT remove the try/except block or convert to exception-raising behavior—silent failure is intentional for optional metadata handling
  - DO NOT return empty dict {} or False on parse failure—always return None for caller clarity and type consistency
  - ALWAYS use yaml.safe_load() specifically to maintain security posture
  - NOTE: Type hint declares Dict return but yaml.safe_load() can return list, string, int, bool, or None—callers must validate the actual type before accessing dict keys

changelog:

  - "2025-10-31: Clean up docstring formatting"
```

---

## __init__

**Location:** `agentspec/extract.py:150`

### What This Does

Initializes an AgentSpecExtractor instance with a file path and prepares an empty container for accumulated specifications.

- Accepts a filepath string parameter and stores it as self.filepath for deferred file parsing
- Initializes self.specs as an empty List[AgentSpec] to accumulate extracted agent specifications during processing
- Performs no file I/O, validation, or parsing at initialization time; all such operations are deferred to dedicated extraction methods
- Enables downstream methods to append AgentSpec objects to self.specs without null-checking or type conversion

Inputs:
- filepath (str): Path to a Python file or directory containing agentspec YAML blocks to extract

Outputs:
- None; side effects are instance attribute assignment (self.filepath, self.specs)

Edge cases:
- No validation of filepath existence or format occurs during __init__; invalid paths are caught later during file I/O operations
- Empty specs list is intentional and expected; extraction methods populate it incrementally

### Dependencies

### Why This Approach

Lazy initialization separates concerns and improves error handling by deferring expensive or failure-prone operations (file I/O, parsing, validation) to dedicated methods rather than the constructor.

Pre-allocating self.specs as an empty list avoids null-checking and type-narrowing logic in downstream append operations, reducing cognitive load and potential runtime errors.

Type hints (List[AgentSpec]) enable IDE autocompletion, static type checking, and self-documenting code that clarifies the expected structure of accumulated data.

Storing filepath as an instance attribute allows extraction methods to reference it without requiring it as a parameter, simplifying method signatures and enabling stateful processing across multiple method calls.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT add file I/O operations (open, read, Path.read_text) in __init__; keep initialization pure and defer I/O to dedicated methods to enable better error handling and testability**
- **DO NOT change self.specs to None or a non-list type; downstream extraction methods assume it is a mutable List and call append() on it**
- **DO NOT omit self.filepath assignment; extraction methods depend on this attribute to locate and parse the target file**
- **DO NOT initialize self.specs to None or skip initialization; this breaks extraction methods that expect a pre-allocated list and would require null-checking elsewhere**
- **DO NOT validate filepath format or existence in __init__; validation belongs in dedicated methods that can provide context-specific error messages**

### Changelog

- - no git history available

### Raw YAML Block

```yaml
what: |
  Initializes an AgentSpecExtractor instance with a file path and prepares an empty container for accumulated specifications.

  - Accepts a filepath string parameter and stores it as self.filepath for deferred file parsing
  - Initializes self.specs as an empty List[AgentSpec] to accumulate extracted agent specifications during processing
  - Performs no file I/O, validation, or parsing at initialization time; all such operations are deferred to dedicated extraction methods
  - Enables downstream methods to append AgentSpec objects to self.specs without null-checking or type conversion

  Inputs:
  - filepath (str): Path to a Python file or directory containing agentspec YAML blocks to extract

  Outputs:
  - None; side effects are instance attribute assignment (self.filepath, self.specs)

  Edge cases:
  - No validation of filepath existence or format occurs during __init__; invalid paths are caught later during file I/O operations
  - Empty specs list is intentional and expected; extraction methods populate it incrementally
deps:
      imports:
        - agentspec.utils.collect_python_files
        - ast
        - dataclasses.asdict
        - dataclasses.dataclass
        - dataclasses.field
        - json
        - pathlib.Path
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - yaml


why: |
  Lazy initialization separates concerns and improves error handling by deferring expensive or failure-prone operations (file I/O, parsing, validation) to dedicated methods rather than the constructor.

  Pre-allocating self.specs as an empty list avoids null-checking and type-narrowing logic in downstream append operations, reducing cognitive load and potential runtime errors.

  Type hints (List[AgentSpec]) enable IDE autocompletion, static type checking, and self-documenting code that clarifies the expected structure of accumulated data.

  Storing filepath as an instance attribute allows extraction methods to reference it without requiring it as a parameter, simplifying method signatures and enabling stateful processing across multiple method calls.

guardrails:
  - DO NOT add file I/O operations (open, read, Path.read_text) in __init__; keep initialization pure and defer I/O to dedicated methods to enable better error handling and testability
  - DO NOT change self.specs to None or a non-list type; downstream extraction methods assume it is a mutable List and call append() on it
  - DO NOT omit self.filepath assignment; extraction methods depend on this attribute to locate and parse the target file
  - DO NOT initialize self.specs to None or skip initialization; this breaks extraction methods that expect a pre-allocated list and would require null-checking elsewhere
  - DO NOT validate filepath format or existence in __init__; validation belongs in dedicated methods that can provide context-specific error messages

changelog:
      - "- no git history available"
```

---

## visit_FunctionDef

**Location:** `agentspec/extract.py:209`

### What This Does

Implements the ast.NodeVisitor pattern to extract function metadata from AST FunctionDef nodes.

Behavior:
- Calls self._extract(node) to parse and accumulate function metadata including name, parameters, decorators, docstrings, and type hints from the current FunctionDef node
- Calls self.generic_visit(node) to recursively traverse and process all child nodes (nested functions, classes, and other AST children)
- Returns None per ast.NodeVisitor protocol; accumulates extracted data via side effects on the visitor instance

Inputs:
- node: an ast.FunctionDef node representing a function definition in the AST

Outputs:
- None (side-effect based; extracted metadata stored in visitor instance state)

Edge cases:
- Nested functions are processed recursively; extraction order is parent-first
- Decorated functions have decorators extracted alongside function signature
- Functions with type hints and docstrings are fully captured
- Empty or malformed function definitions are handled by _extract() error handling

### Dependencies

**Calls:**
- `self._extract`
- `self.generic_visit`

### Why This Approach

The visitor pattern is the standard Python idiom for AST traversal, providing clean separation between extraction logic and tree traversal mechanics.
Processing the parent node via _extract() before recursing via generic_visit() ensures proper extraction order and maintains context availability for nested structures.
This approach is maintainable, extensible, and follows ast.NodeVisitor conventions for compatibility with Python's AST infrastructure.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT remove the generic_visit(node) call; it breaks traversal of nested functions, classes, and other child nodes, resulting in incomplete metadata extraction**
- **DO NOT reorder _extract() and generic_visit() calls; reversing them breaks the extraction dependency chain and may cause context loss for nested structures**
- **ALWAYS preserve the method signature as visit_FunctionDef(self, node) for ast.NodeVisitor compatibility; renaming or changing parameters breaks the visitor dispatch mechanism**
- **DO NOT modify node in-place before calling generic_visit(); preserve AST integrity for recursive processing**

### Changelog

- - no git history available

### Raw YAML Block

```yaml
what: |
  Implements the ast.NodeVisitor pattern to extract function metadata from AST FunctionDef nodes.

  Behavior:
  - Calls self._extract(node) to parse and accumulate function metadata including name, parameters, decorators, docstrings, and type hints from the current FunctionDef node
  - Calls self.generic_visit(node) to recursively traverse and process all child nodes (nested functions, classes, and other AST children)
  - Returns None per ast.NodeVisitor protocol; accumulates extracted data via side effects on the visitor instance

  Inputs:
  - node: an ast.FunctionDef node representing a function definition in the AST

  Outputs:
  - None (side-effect based; extracted metadata stored in visitor instance state)

  Edge cases:
  - Nested functions are processed recursively; extraction order is parent-first
  - Decorated functions have decorators extracted alongside function signature
  - Functions with type hints and docstrings are fully captured
  - Empty or malformed function definitions are handled by _extract() error handling
deps:
      calls:
        - self._extract
        - self.generic_visit
      imports:
        - agentspec.utils.collect_python_files
        - ast
        - dataclasses.asdict
        - dataclasses.dataclass
        - dataclasses.field
        - json
        - pathlib.Path
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - yaml


why: |
  The visitor pattern is the standard Python idiom for AST traversal, providing clean separation between extraction logic and tree traversal mechanics.
  Processing the parent node via _extract() before recursing via generic_visit() ensures proper extraction order and maintains context availability for nested structures.
  This approach is maintainable, extensible, and follows ast.NodeVisitor conventions for compatibility with Python's AST infrastructure.

guardrails:
  - DO NOT remove the generic_visit(node) call; it breaks traversal of nested functions, classes, and other child nodes, resulting in incomplete metadata extraction
  - DO NOT reorder _extract() and generic_visit() calls; reversing them breaks the extraction dependency chain and may cause context loss for nested structures
  - ALWAYS preserve the method signature as visit_FunctionDef(self, node) for ast.NodeVisitor compatibility; renaming or changing parameters breaks the visitor dispatch mechanism
  - DO NOT modify node in-place before calling generic_visit(); preserve AST integrity for recursive processing

changelog:
      - "- no git history available"
```

---

## visit_AsyncFunctionDef

**Location:** `agentspec/extract.py:268`

### What This Does

Visitor callback for async function definitions that extracts metadata and traverses child nodes.

Behavior:
- Calls self._extract(node) to collect async function metadata including name, arguments, decorators, docstrings, and type hints
- Calls self.generic_visit(node) to recursively process nested structures within the async function body
- Handles async generators and decorated async functions uniformly

Inputs:
- node: an ast.AsyncFunctionDef node representing an async function definition

Outputs:
- Side effect: populates internal state via _extract() with async function metadata
- Side effect: recursively visits all child nodes in the AST subtree

Edge cases:
- Async generators (async def with yield) are processed identically to regular async functions
- Decorated async functions have decorators extracted as part of node metadata
- Nested async functions within async functions are discovered via recursive generic_visit()

### Dependencies

**Calls:**
- `self._extract`
- `self.generic_visit`

### Why This Approach

Follows the ast.NodeVisitor double-dispatch pattern for clean separation of node-type-specific logic.
Reuses _extract() logic across both FunctionDef and AsyncFunctionDef node types to avoid duplication.
The generic_visit() call is critical for discovering nested functions, classes, and other definitions within the async function body; omitting it breaks recursive traversal and causes nested definitions to be missed.
Calling _extract() before generic_visit() ensures metadata extraction completes before descending into child nodes, maintaining proper traversal order.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT remove the generic_visit() call; it breaks recursive traversal and prevents discovery of nested functions, classes, and other definitions within the async function body**
- **DO NOT alter the method signature; it must accept (self, node) to comply with ast.NodeVisitor double-dispatch pattern**
- **ALWAYS call _extract() before generic_visit() to ensure metadata extraction completes before descending into child nodes**
- **DO NOT assume the node has specific attributes without checking; rely on _extract() to handle attribute validation**

### Changelog

- - no git history available

### Raw YAML Block

```yaml
what: |
  Visitor callback for async function definitions that extracts metadata and traverses child nodes.

  Behavior:
  - Calls self._extract(node) to collect async function metadata including name, arguments, decorators, docstrings, and type hints
  - Calls self.generic_visit(node) to recursively process nested structures within the async function body
  - Handles async generators and decorated async functions uniformly

  Inputs:
  - node: an ast.AsyncFunctionDef node representing an async function definition

  Outputs:
  - Side effect: populates internal state via _extract() with async function metadata
  - Side effect: recursively visits all child nodes in the AST subtree

  Edge cases:
  - Async generators (async def with yield) are processed identically to regular async functions
  - Decorated async functions have decorators extracted as part of node metadata
  - Nested async functions within async functions are discovered via recursive generic_visit()
deps:
      calls:
        - self._extract
        - self.generic_visit
      imports:
        - agentspec.utils.collect_python_files
        - ast
        - dataclasses.asdict
        - dataclasses.dataclass
        - dataclasses.field
        - json
        - pathlib.Path
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - yaml


why: |
  Follows the ast.NodeVisitor double-dispatch pattern for clean separation of node-type-specific logic.
  Reuses _extract() logic across both FunctionDef and AsyncFunctionDef node types to avoid duplication.
  The generic_visit() call is critical for discovering nested functions, classes, and other definitions within the async function body; omitting it breaks recursive traversal and causes nested definitions to be missed.
  Calling _extract() before generic_visit() ensures metadata extraction completes before descending into child nodes, maintaining proper traversal order.

guardrails:
  - DO NOT remove the generic_visit() call; it breaks recursive traversal and prevents discovery of nested functions, classes, and other definitions within the async function body
  - DO NOT alter the method signature; it must accept (self, node) to comply with ast.NodeVisitor double-dispatch pattern
  - ALWAYS call _extract() before generic_visit() to ensure metadata extraction completes before descending into child nodes
  - DO NOT assume the node has specific attributes without checking; rely on _extract() to handle attribute validation

changelog:
      - "- no git history available"
```

---

## visit_ClassDef

**Location:** `agentspec/extract.py:328`

### What This Does

Extracts class metadata (name, decorators, docstring, line numbers) from an AST ClassDef node and recursively visits all child nodes in depth-first pre-order traversal.

Inputs:
- node: An ast.ClassDef node representing a class definition

Outputs:
- Side effect: Populates internal state via _extract() with class metadata
- Side effect: Recursively processes all child nodes (methods, nested classes, attributes) via generic_visit()

Behavior:
- Calls _extract(node) to capture class-level metadata before recursion
- Calls generic_visit(node) to traverse all child nodes in the AST
- Maintains depth-first, pre-order traversal order (parent processed before children)
- Integrates with ast.NodeVisitor dispatch mechanism via method naming convention

### Dependencies

**Calls:**
- `self._extract`
- `self.generic_visit`

### Why This Approach

The visitor pattern is the standard Python idiom for AST traversal, eliminating manual recursion boilerplate and leveraging ast.NodeVisitor's built-in dispatch. Pre-order traversal (extract before recursing) ensures parent metadata is collected before child metadata, enabling proper hierarchical organization. Separation of concerns between _extract() (metadata collection) and generic_visit() (tree traversal) improves maintainability and clarity of intent.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT rename this method—the name visit_ClassDef is required by ast.NodeVisitor's visit_<NodeType> dispatch mechanism and renaming breaks automatic node routing**
- **DO NOT remove the generic_visit() call—omitting it prevents child nodes from being visited, resulting in incomplete AST traversal and missing nested classes/methods**
- **DO NOT call _extract() after generic_visit()—this reverses traversal order to post-order, causing children to be processed before parents and breaking hierarchical metadata collection**
- **{'DO NOT modify the method signature—ast.NodeVisitor expects exactly def visit_ClassDef(self, node)': None}**
- **ALWAYS call _extract() before generic_visit() to maintain pre-order traversal semantics**

### Changelog

- - no git history available

### Raw YAML Block

```yaml
what: |
  Extracts class metadata (name, decorators, docstring, line numbers) from an AST ClassDef node and recursively visits all child nodes in depth-first pre-order traversal.

  Inputs:
  - node: An ast.ClassDef node representing a class definition

  Outputs:
  - Side effect: Populates internal state via _extract() with class metadata
  - Side effect: Recursively processes all child nodes (methods, nested classes, attributes) via generic_visit()

  Behavior:
  - Calls _extract(node) to capture class-level metadata before recursion
  - Calls generic_visit(node) to traverse all child nodes in the AST
  - Maintains depth-first, pre-order traversal order (parent processed before children)
  - Integrates with ast.NodeVisitor dispatch mechanism via method naming convention
deps:
      calls:
        - self._extract
        - self.generic_visit
      imports:
        - agentspec.utils.collect_python_files
        - ast
        - dataclasses.asdict
        - dataclasses.dataclass
        - dataclasses.field
        - json
        - pathlib.Path
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - yaml


why: |
  The visitor pattern is the standard Python idiom for AST traversal, eliminating manual recursion boilerplate and leveraging ast.NodeVisitor's built-in dispatch. Pre-order traversal (extract before recursing) ensures parent metadata is collected before child metadata, enabling proper hierarchical organization. Separation of concerns between _extract() (metadata collection) and generic_visit() (tree traversal) improves maintainability and clarity of intent.

guardrails:
  - DO NOT rename this method—the name visit_ClassDef is required by ast.NodeVisitor's visit_<NodeType> dispatch mechanism and renaming breaks automatic node routing
  - DO NOT remove the generic_visit() call—omitting it prevents child nodes from being visited, resulting in incomplete AST traversal and missing nested classes/methods
  - DO NOT call _extract() after generic_visit()—this reverses traversal order to post-order, causing children to be processed before parents and breaking hierarchical metadata collection
  - DO NOT modify the method signature—ast.NodeVisitor expects exactly def visit_ClassDef(self, node):
  - ALWAYS call _extract() before generic_visit() to maintain pre-order traversal semantics

changelog:
      - "- no git history available"
```

---

## _extract

**Location:** `agentspec/extract.py:382`

### What This Does

Extracts agent specification metadata from AST nodes by parsing YAML-formatted docstrings into AgentSpec objects.

- Retrieves docstring via ast.get_docstring() and extracts YAML block; returns early if none found
- Creates fallback spec from raw docstring if YAML block absent; parses YAML into structured AgentSpec fields
- Appends spec to self.specs with node metadata (name, lineno, filepath) and both raw_block and parsed_data preserved
- Handles edge cases: missing docstrings, malformed YAML, empty blocks, and multi-paragraph fallback text
- Extracts structured fields (what, deps, why, guardrails, changelog, testing, performance) from parsed YAML when available
- Converts string fields to stripped strings; preserves dictionaries and lists as-is from YAML parse result

### Dependencies

**Calls:**
- `AgentSpec`
- `_extract_block`
- `_parse_yaml_block`
- `ast.get_docstring`
- `doc.split`
- `doc.splitlines`
- `p.strip`
- `parsed.get`
- `specs.append`
- `str`
- `strip`

### Why This Approach

ast.get_docstring() handles docstring detection consistently across all AST node types (FunctionDef, ClassDef, etc.).
Early return and conditional field population prevent empty specs and crashes on malformed YAML, improving robustness.
Dual storage of raw_block and parsed_data preserves original documentation for debugging, audit trails, and recovery from parse failures.
Fallback mechanism ensures extraction succeeds even when YAML formatting is absent, allowing graceful degradation to basic docstring capture.
Explicit field extraction with .strip() and .get() provides null safety and prevents None values from propagating into spec fields.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT modify conditional structure without ensuring null safety for all dictionary key accesses; use .get() with defaults**
- **DO NOT remove early return when block is empty; prevents unnecessary allocation and maintains performance**
- **DO NOT change str(...).strip() on string fields without understanding None→'' conversion semantics**
- **DO NOT skip node metadata extraction (name, lineno, filepath); source mapping is critical for traceability**
- **DO NOT store only parsed_data without raw_block; dual storage maintains audit trail and enables recovery**
- **DO NOT reimplement YAML extraction inline; always call _extract_block() and _parse_yaml_block() to maintain separation of concerns**
- **DO NOT assume parsed dictionary keys exist; always use .get() with appropriate defaults ('' for strings, {} for dicts, [] for lists)**

### Changelog

- 2025-10-31: Clean up docstring formatting

### Raw YAML Block

```yaml
what: |
  Extracts agent specification metadata from AST nodes by parsing YAML-formatted docstrings into AgentSpec objects.

  - Retrieves docstring via ast.get_docstring() and extracts YAML block; returns early if none found
  - Creates fallback spec from raw docstring if YAML block absent; parses YAML into structured AgentSpec fields
  - Appends spec to self.specs with node metadata (name, lineno, filepath) and both raw_block and parsed_data preserved
  - Handles edge cases: missing docstrings, malformed YAML, empty blocks, and multi-paragraph fallback text
  - Extracts structured fields (what, deps, why, guardrails, changelog, testing, performance) from parsed YAML when available
  - Converts string fields to stripped strings; preserves dictionaries and lists as-is from YAML parse result
deps:
      calls:
        - AgentSpec
        - _extract_block
        - _parse_yaml_block
        - ast.get_docstring
        - doc.split
        - doc.splitlines
        - p.strip
        - parsed.get
        - specs.append
        - str
        - strip
      imports:
        - agentspec.utils.collect_python_files
        - ast
        - dataclasses.asdict
        - dataclasses.dataclass
        - dataclasses.field
        - json
        - pathlib.Path
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - yaml


why: |
  ast.get_docstring() handles docstring detection consistently across all AST node types (FunctionDef, ClassDef, etc.).
  Early return and conditional field population prevent empty specs and crashes on malformed YAML, improving robustness.
  Dual storage of raw_block and parsed_data preserves original documentation for debugging, audit trails, and recovery from parse failures.
  Fallback mechanism ensures extraction succeeds even when YAML formatting is absent, allowing graceful degradation to basic docstring capture.
  Explicit field extraction with .strip() and .get() provides null safety and prevents None values from propagating into spec fields.

guardrails:
  - DO NOT modify conditional structure without ensuring null safety for all dictionary key accesses; use .get() with defaults
  - DO NOT remove early return when block is empty; prevents unnecessary allocation and maintains performance
  - DO NOT change str(...).strip() on string fields without understanding None→'' conversion semantics
  - DO NOT skip node metadata extraction (name, lineno, filepath); source mapping is critical for traceability
  - DO NOT store only parsed_data without raw_block; dual storage maintains audit trail and enables recovery
  - DO NOT reimplement YAML extraction inline; always call _extract_block() and _parse_yaml_block() to maintain separation of concerns
  - DO NOT assume parsed dictionary keys exist; always use .get() with appropriate defaults ('' for strings, {} for dicts, [] for lists)

changelog:

  - "2025-10-31: Clean up docstring formatting"
```

---

## extract_from_file

**Location:** `agentspec/extract.py:486`

### What This Does

Extracts all AgentSpec definitions from a Python source file by parsing its Abstract Syntax Tree (AST).

Reads the file at the given Path with UTF-8 encoding, parses it into an AST representation, and visits all nodes using an AgentSpecExtractor visitor to collect AgentSpec objects. Returns a list of all AgentSpec instances found in the file.

On any exception—including file I/O errors, syntax errors, or extraction failures—prints a warning message to stderr and returns an empty list instead of raising. This allows graceful degradation when processing unknown or third-party code.

Input: path (Path object pointing to a Python source file)
Output: List[AgentSpec] containing zero or more extracted specifications

Edge cases:
- Non-existent files: caught by path.read_text(), returns empty list with warning
- Syntax errors in Python source: caught by ast.parse(), returns empty list with warning
- Files with no AgentSpec definitions: returns empty list (no warning, normal case)
- Encoding issues: UTF-8 decode errors caught, returns empty list with warning

### Dependencies

**Calls:**
- `AgentSpecExtractor`
- `ast.parse`
- `extractor.visit`
- `path.read_text`
- `print`
- `str`

### Why This Approach

AST parsing is the most reliable approach for extracting AgentSpec definitions because it handles complex Python syntax robustly—decorators, nested class/function definitions, multi-line constructs, and string literals are all properly represented in the AST without fragile regex or text-based heuristics.

Graceful error handling (try/except returning empty list) enables batch processing across multiple files without halting on problematic input. This is essential for tools that scan entire codebases where some files may be malformed, incomplete, or in non-standard formats.

Empty list return semantics allow simple list concatenation patterns (e.g., `all_specs = [] ; for file in files: all_specs.extend(extract_from_file(file))`) without special-casing None or exception handling at the call site.

The visitor pattern via AgentSpecExtractor.visit() provides clean separation of concerns: parsing logic is isolated in the extractor class, making the extraction logic testable and reusable.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT remove the try/except wrapper or convert to raising exceptions—this breaks batch processing and causes the entire extraction pipeline to fail on a single malformed file**
- **DO NOT change encoding from "utf-8" without verifying platform compatibility across Windows, macOS, and Linux; UTF-8 is the safe default for modern Python codebases**
- **DO NOT modify the return type from List[AgentSpec]—downstream code depends on the empty list semantics to distinguish "no specs found" from "error occurred"**
- **ALWAYS preserve str(path) conversions when passing Path objects to ast.parse() and in warning messages, as ast.parse() expects a string filename for error reporting**
- **ALWAYS maintain the visitor pattern via AgentSpecExtractor.visit() call—do not inline extraction logic to preserve modularity and testability**
- **DO NOT suppress the warning print statement—it provides essential debugging visibility when files fail to parse in batch operations**

### Changelog

- 2025-10-31: Clean up docstring formatting

### Raw YAML Block

```yaml
what: |
  Extracts all AgentSpec definitions from a Python source file by parsing its Abstract Syntax Tree (AST).

  Reads the file at the given Path with UTF-8 encoding, parses it into an AST representation, and visits all nodes using an AgentSpecExtractor visitor to collect AgentSpec objects. Returns a list of all AgentSpec instances found in the file.

  On any exception—including file I/O errors, syntax errors, or extraction failures—prints a warning message to stderr and returns an empty list instead of raising. This allows graceful degradation when processing unknown or third-party code.

  Input: path (Path object pointing to a Python source file)
  Output: List[AgentSpec] containing zero or more extracted specifications

  Edge cases:
  - Non-existent files: caught by path.read_text(), returns empty list with warning
  - Syntax errors in Python source: caught by ast.parse(), returns empty list with warning
  - Files with no AgentSpec definitions: returns empty list (no warning, normal case)
  - Encoding issues: UTF-8 decode errors caught, returns empty list with warning
deps:
      calls:
        - AgentSpecExtractor
        - ast.parse
        - extractor.visit
        - path.read_text
        - print
        - str
      imports:
        - agentspec.utils.collect_python_files
        - ast
        - dataclasses.asdict
        - dataclasses.dataclass
        - dataclasses.field
        - json
        - pathlib.Path
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - yaml


why: |
  AST parsing is the most reliable approach for extracting AgentSpec definitions because it handles complex Python syntax robustly—decorators, nested class/function definitions, multi-line constructs, and string literals are all properly represented in the AST without fragile regex or text-based heuristics.

  Graceful error handling (try/except returning empty list) enables batch processing across multiple files without halting on problematic input. This is essential for tools that scan entire codebases where some files may be malformed, incomplete, or in non-standard formats.

  Empty list return semantics allow simple list concatenation patterns (e.g., `all_specs = [] ; for file in files: all_specs.extend(extract_from_file(file))`) without special-casing None or exception handling at the call site.

  The visitor pattern via AgentSpecExtractor.visit() provides clean separation of concerns: parsing logic is isolated in the extractor class, making the extraction logic testable and reusable.

guardrails:
  - DO NOT remove the try/except wrapper or convert to raising exceptions—this breaks batch processing and causes the entire extraction pipeline to fail on a single malformed file
  - DO NOT change encoding from "utf-8" without verifying platform compatibility across Windows, macOS, and Linux; UTF-8 is the safe default for modern Python codebases
  - DO NOT modify the return type from List[AgentSpec]—downstream code depends on the empty list semantics to distinguish "no specs found" from "error occurred"
  - ALWAYS preserve str(path) conversions when passing Path objects to ast.parse() and in warning messages, as ast.parse() expects a string filename for error reporting
  - ALWAYS maintain the visitor pattern via AgentSpecExtractor.visit() call—do not inline extraction logic to preserve modularity and testability
  - DO NOT suppress the warning print statement—it provides essential debugging visibility when files fail to parse in batch operations

changelog:

  - "2025-10-31: Clean up docstring formatting"
```

---

## export_markdown

**Location:** `agentspec/extract.py:560`

### What This Does

Serializes a list of AgentSpec objects to a formatted markdown file for AI agent consumption.

For each spec, writes a markdown section containing:
- Spec name and source location (filepath:lineno)
- What/Why/Guardrails narrative sections (if present)
- Dependencies breakdown (calls, called_by, config_files as separate lists)  - Testing configuration as YAML block (if present)
- Performance characteristics as key-value pairs (if present)
- Raw YAML block preserving the original spec data
- Separator line between specs

Includes auto-generated header ("🤖 Extracted Agent Specifications") and metadata note at document start.
Conditionally renders only non-empty optional fields to prevent malformed output.
Uses UTF-8 encoding explicitly via Path.open().

### Dependencies

**Calls:**
- `f.write`
- `out.open`
- `performance.items`
- `yaml.dump`

### Why This Approach

Markdown is version-control-friendly, GitHub-renderable, and directly parseable by AI agents without custom deserialization.
Raw YAML blocks preserve spec data alongside formatted prose, enabling dual consumption (human-readable narrative + machine-parseable structure).
Conditional field rendering prevents empty sections that would clutter output or confuse downstream parsers.
Explicit UTF-8 encoding ensures consistent handling across platforms and CI/CD environments.
Hierarchical heading structure (##, ###) enables outline-based navigation and programmatic section extraction.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT modify heading hierarchy (##,**
- **DO NOT remove the auto-generated header or raw YAML blocks; AI agents depend on these markers for document structure validation**
- **DO NOT change UTF-8 encoding without coordinating with all consumers; assume UTF-8 is mandatory**
- **DO NOT omit the raw YAML block for any spec; it is the canonical representation for machine consumption**
- **DO NOT render empty dependency, changelog, testing, or performance sections; always check field presence first**
- **DO NOT alter the separator line format (---) between specs; parsers may depend on this delimiter**

### Changelog

- 2025-10-31: Clean up docstring formatting

### Raw YAML Block

```yaml
what: |
  Serializes a list of AgentSpec objects to a formatted markdown file for AI agent consumption.

  For each spec, writes a markdown section containing:
  - Spec name and source location (filepath:lineno)
  - What/Why/Guardrails narrative sections (if present)
  - Dependencies breakdown (calls, called_by, config_files as separate lists)  - Testing configuration as YAML block (if present)
  - Performance characteristics as key-value pairs (if present)
  - Raw YAML block preserving the original spec data
  - Separator line between specs

  Includes auto-generated header ("🤖 Extracted Agent Specifications") and metadata note at document start.
  Conditionally renders only non-empty optional fields to prevent malformed output.
  Uses UTF-8 encoding explicitly via Path.open().
deps:
      calls:
        - f.write
        - out.open
        - performance.items
        - yaml.dump
      imports:
        - agentspec.utils.collect_python_files
        - ast
        - dataclasses.asdict
        - dataclasses.dataclass
        - dataclasses.field
        - json
        - pathlib.Path
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - yaml


why: |
  Markdown is version-control-friendly, GitHub-renderable, and directly parseable by AI agents without custom deserialization.
  Raw YAML blocks preserve spec data alongside formatted prose, enabling dual consumption (human-readable narrative + machine-parseable structure).
  Conditional field rendering prevents empty sections that would clutter output or confuse downstream parsers.
  Explicit UTF-8 encoding ensures consistent handling across platforms and CI/CD environments.
  Hierarchical heading structure (##, ###) enables outline-based navigation and programmatic section extraction.

guardrails:
  - DO NOT modify heading hierarchy (##, ###) without updating downstream parsers that depend on these markers for section extraction
  - DO NOT remove the auto-generated header or raw YAML blocks; AI agents depend on these markers for document structure validation
  - DO NOT change UTF-8 encoding without coordinating with all consumers; assume UTF-8 is mandatory
  - DO NOT omit the raw YAML block for any spec; it is the canonical representation for machine consumption
  - DO NOT render empty dependency, changelog, testing, or performance sections; always check field presence first
  - DO NOT alter the separator line format (---) between specs; parsers may depend on this delimiter

changelog:

  - "2025-10-31: Clean up docstring formatting"
```

---

## export_json

**Location:** `agentspec/extract.py:680`

### What This Does

Serializes a list of AgentSpec objects to a JSON file for downstream consumption.

For each AgentSpec in the input list, extracts all metadata fields (name, lineno, filepath, what, deps, why, guardrails, changelog, testing, performance, raw_block) into a dictionary. Collects all dictionaries into a single list and writes to the specified Path as formatted JSON with 2-space indentation and UTF-8 encoding.

Inputs: specs (List[AgentSpec]) – collection of agent specifications; out (Path) – target file path for JSON output.

Outputs: None (side effect: writes JSON file to disk).

Edge cases: Empty specs list produces valid empty JSON array; raw_block field may contain multi-line strings that are properly escaped by json.dump.

### Dependencies

**Calls:**
- `data.append`
- `json.dump`
- `out.open`

### Why This Approach

JSON format ensures broad compatibility with downstream tools, CI/CD pipelines, and non-Python consumers without requiring YAML or custom parsing. Explicit field-by-field mapping provides API stability if AgentSpec gains internal-only attributes in the future, decoupling the export format from the dataclass structure. UTF-8 encoding and 2-space indentation balance readability with cross-platform portability.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT remove fields from spec_dict without updating all downstream JSON consumers, as this breaks contract with tools that depend on the schema.**
- **DO NOT change encoding without cross-platform testing, as UTF-8 is assumed by downstream processors.**
- **ALWAYS preserve raw_block field for round-trip docstring reconstruction and audit trails.**
- **ALWAYS ensure parent directory of out exists before calling; this function does not create intermediate directories (caller responsibility).**

### Changelog

- 2025-10-31: Clean up docstring formatting

### Raw YAML Block

```yaml
what: |
  Serializes a list of AgentSpec objects to a JSON file for downstream consumption.

  For each AgentSpec in the input list, extracts all metadata fields (name, lineno, filepath, what, deps, why, guardrails, changelog, testing, performance, raw_block) into a dictionary. Collects all dictionaries into a single list and writes to the specified Path as formatted JSON with 2-space indentation and UTF-8 encoding.

  Inputs: specs (List[AgentSpec]) – collection of agent specifications; out (Path) – target file path for JSON output.

  Outputs: None (side effect: writes JSON file to disk).

  Edge cases: Empty specs list produces valid empty JSON array; raw_block field may contain multi-line strings that are properly escaped by json.dump.
deps:
      calls:
        - data.append
        - json.dump
        - out.open
      imports:
        - agentspec.utils.collect_python_files
        - ast
        - dataclasses.asdict
        - dataclasses.dataclass
        - dataclasses.field
        - json
        - pathlib.Path
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - yaml


why: |
  JSON format ensures broad compatibility with downstream tools, CI/CD pipelines, and non-Python consumers without requiring YAML or custom parsing. Explicit field-by-field mapping provides API stability if AgentSpec gains internal-only attributes in the future, decoupling the export format from the dataclass structure. UTF-8 encoding and 2-space indentation balance readability with cross-platform portability.

guardrails:
  - DO NOT remove fields from spec_dict without updating all downstream JSON consumers, as this breaks contract with tools that depend on the schema.
  - DO NOT change encoding without cross-platform testing, as UTF-8 is assumed by downstream processors.
  - ALWAYS preserve raw_block field for round-trip docstring reconstruction and audit trails.
  - ALWAYS ensure parent directory of out exists before calling; this function does not create intermediate directories (caller responsibility).

changelog:

  - "2025-10-31: Clean up docstring formatting"
```

---

## export_agent_context

**Location:** `agentspec/extract.py:748`

### Raw YAML Block

```yaml
what: |
      Exports a list of AgentSpec objects to a markdown file optimized for agent consumption. For each spec, writes a formatted section containing: a markdown header with spec name and file location, executable Python print() statements that agents can run to display metadata, guardrail items with one-based enumeration, and the raw YAML or docstring block. The "what" field is truncated to 100 characters; None/empty values for "what" and "guardrails" are handled gracefully with conditional checks. Output is UTF-8 encoded with triple-dash separators between specs. Returns None (side effect: writes file to disk).
    deps:
          calls:
            - enumerate
            - f.write
            - len
            - out.open
          imports:
            - agentspec.utils.collect_python_files
            - ast
            - dataclasses.asdict
            - dataclasses.dataclass
            - dataclasses.field
            - json
            - pathlib.Path
            - typing.Any
            - typing.Dict
            - typing.List
            - typing.Optional
            - yaml


    why: |
      Embedded print() statements allow agents to parse both markdown structure (human-readable) and executable Python code (programmatic understanding) from a single file. Markdown format preserves readability for humans while maintaining machine-readable YAML blocks. One-based guardrail indexing matches human counting conventions rather than zero-based programming conventions, improving agent interpretation. Truncating "what" to 100 characters balances verbosity with output file size. Conditional checks prevent AttributeError when specs have None values. Triple-dash separators enable independent section parsing by agents. Preserving raw_block exactly as-is maintains original formatting and comments from source rather than re-serializing.

    guardrails:
      - DO NOT modify print() statement format or "[AGENTSPEC]" prefix; agents pattern-match on these strings for reliable parsing
      - DO NOT remove conditional checks for s.what and s.guardrails; some specs may have None or empty values that would cause write failures
      - DO NOT change the 100-character truncation length without considering downstream agent parsing logic that may depend on consistent output size
      - DO NOT reorder sections (header, prints, full spec, separator); agent parsing depends on this exact structure
      - DO NOT re-serialize raw_block through YAML/JSON; preserve it exactly as-is to maintain original formatting and comments
      - ALWAYS preserve markdown header hierarchy (## for spec sections) and raw_block exactly as written
      - ALWAYS encode output as UTF-8 and enumerate guardrails starting from 1, not 0
      - ALWAYS include the triple-dash separator ("---

") between specs for section demarcation
      - NOTE: Function assumes all AgentSpec objects have valid name, filepath, and lineno attributes; missing attributes will cause AttributeError
      - NOTE: File write operations are not atomic; process crash mid-write will corrupt output file
      - NOTE: Output file can grow large with many specs; consider pagination or splitting for >5000 specs
      - NOTE: Agents should treat print() statements as metadata instructions, not as code to execute in all contexts

    changelog:

      - "2025-10-31: Clean up docstring formatting"
```

---

## run

**Location:** `agentspec/extract.py:825`

### What This Does

Extracts agent specification blocks from Python files in a target directory and exports them in the specified format.

Behavior:
- Accepts a target path (file or directory) and optional format string (markdown, json, or agent-context)
- Collects all Python files from the target using collect_python_files, which handles path validation and .gitignore/.venv filtering
- Iterates through collected files and extracts AgentSpec objects from embedded YAML blocks and docstrings using extract_from_file
- Aggregates all extracted specs into a single list
- Exports aggregated specs to a format-specific output file: agent_specs.json, AGENT_CONTEXT.md, or agent_specs.md (default)
- Returns 0 on successful export, 1 if no specs are found

Inputs:
- target: string path to file or directory containing Python source code
- fmt: output format string; one of "markdown" (default), "json", or "agent-context"

Outputs:
- Exit code: 0 for success, 1 if no specs found
- Side effect: writes formatted specs to filesystem (agent_specs.json, AGENT_CONTEXT.md, or agent_specs.md)
- Console output: status message with spec count and output file path

Edge cases:
- Empty target directory or no Python files: returns 1 with warning message
- Invalid format string: defaults to markdown export
- Non-existent target path: handled by collect_python_files validation

### Dependencies

**Calls:**
- `Path`
- `all_specs.extend`
- `collect_python_files`
- `export_agent_context`
- `export_json`
- `export_markdown`
- `extract_from_file`
- `len`
- `print`

### Why This Approach

Centralizes spec extraction and export logic into a single CLI entry point, enabling users to batch-process Python codebases and generate machine-readable spec documentation.
Format abstraction (markdown/json/agent-context) allows flexible output without modifying core extraction logic.
Exit code convention (0/1) ensures proper shell integration and scripting compatibility.
Aggregation pattern (extend all_specs) scales efficiently across large codebases.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT assume target path exists; collect_python_files handles validation and raises appropriate errors**
- **DO NOT export if specs list is empty; always return 1 and print warning to prevent silent failures**
- **ALWAYS return an exit code (0 or 1) for proper CLI integration and shell scripting**
- **DO NOT modify or filter specs during aggregation; preserve all extracted specs as-is**
- **DO NOT assume format string is valid; default to markdown for unrecognized formats to prevent crashes**

### Changelog

- 2025-10-31: Clean up docstring formatting

### Raw YAML Block

```yaml
what: |
  Extracts agent specification blocks from Python files in a target directory and exports them in the specified format.

  Behavior:
  - Accepts a target path (file or directory) and optional format string (markdown, json, or agent-context)
  - Collects all Python files from the target using collect_python_files, which handles path validation and .gitignore/.venv filtering
  - Iterates through collected files and extracts AgentSpec objects from embedded YAML blocks and docstrings using extract_from_file
  - Aggregates all extracted specs into a single list
  - Exports aggregated specs to a format-specific output file: agent_specs.json, AGENT_CONTEXT.md, or agent_specs.md (default)
  - Returns 0 on successful export, 1 if no specs are found

  Inputs:
  - target: string path to file or directory containing Python source code
  - fmt: output format string; one of "markdown" (default), "json", or "agent-context"

  Outputs:
  - Exit code: 0 for success, 1 if no specs found
  - Side effect: writes formatted specs to filesystem (agent_specs.json, AGENT_CONTEXT.md, or agent_specs.md)
  - Console output: status message with spec count and output file path

  Edge cases:
  - Empty target directory or no Python files: returns 1 with warning message
  - Invalid format string: defaults to markdown export
  - Non-existent target path: handled by collect_python_files validation
deps:
      calls:
        - Path
        - all_specs.extend
        - collect_python_files
        - export_agent_context
        - export_json
        - export_markdown
        - extract_from_file
        - len
        - print
      imports:
        - agentspec.utils.collect_python_files
        - ast
        - dataclasses.asdict
        - dataclasses.dataclass
        - dataclasses.field
        - json
        - pathlib.Path
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - yaml


why: |
  Centralizes spec extraction and export logic into a single CLI entry point, enabling users to batch-process Python codebases and generate machine-readable spec documentation.
  Format abstraction (markdown/json/agent-context) allows flexible output without modifying core extraction logic.
  Exit code convention (0/1) ensures proper shell integration and scripting compatibility.
  Aggregation pattern (extend all_specs) scales efficiently across large codebases.

guardrails:
  - DO NOT assume target path exists; collect_python_files handles validation and raises appropriate errors
  - DO NOT export if specs list is empty; always return 1 and print warning to prevent silent failures
  - ALWAYS return an exit code (0 or 1) for proper CLI integration and shell scripting
  - DO NOT modify or filter specs during aggregation; preserve all extracted specs as-is
  - DO NOT assume format string is valid; default to markdown for unrecognized formats to prevent crashes

changelog:

  - "2025-10-31: Clean up docstring formatting"
```

---

## _get_client

**Location:** `agentspec/generate.py:14`

### What This Does

Lazily instantiates and returns an Anthropic API client, deferring the import of the Anthropic class until the function is first called rather than at module load time.

Inputs: None

Outputs: An Anthropic() instance configured to automatically read the ANTHROPIC_API_KEY environment variable.

Behavior:
- Calls load_env_from_dotenv() to ensure environment variables from .env files are loaded
- Performs a deferred import of the Anthropic class from the anthropic package only at call time
- Instantiates and returns a new Anthropic() client, which internally reads ANTHROPIC_API_KEY from the environment
- Each invocation creates a fresh client instance; no caching or singleton pattern is implemented

Edge cases:
- If ANTHROPIC_API_KEY is missing or invalid, the Anthropic() constructor will raise anthropic.APIError or related authentication exceptions; callers must handle these gracefully
- If the anthropic package is not installed, ImportError is raised only when _get_client() is called, not during module import
- Enables agentspec/generate.py to be imported successfully in environments where the Anthropic API is not needed (e.g., dry-run paths, metadata collection, file discovery)

### Dependencies

**Calls:**
- `Anthropic`
- `load_env_from_dotenv`

### Why This Approach

Lazy loading defers the hard dependency on the anthropic package until it is actually needed, allowing the module to load successfully in non-generation workflows. This approach prevents ImportError exceptions during dry-run scenarios, testing, or when users invoke only non-generation commands such as metadata collection or file discovery.

The Anthropic() constructor automatically reads ANTHROPIC_API_KEY from the environment, following standard SDK conventions and avoiding the need for explicit credential passing.

Lightweight client instantiation means performance impact is negligible; the client is typically created only once per generate command invocation.

Alternative approaches (module-level import with try/except, singleton caching) were rejected because: (1) module-level import would fail immediately if anthropic is unavailable, defeating the purpose of supporting non-generation workflows, and (2) singleton caching adds unnecessary complexity and state management overhead without clear benefit for stateless, lightweight client instantiation.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT move the import statement to module level or wrap it in a try/except that silently fails; this defeats the lazy-loading purpose and reintroduces hard dependencies during module import**
- **DO NOT implement caching or singleton behavior without explicit requirements; it adds complexity and state management overhead without clear benefit**
- **DO NOT remove the inline comment explaining the lazy import pattern; it documents the intentional design choice for future maintainers**
- **ALWAYS ensure the ANTHROPIC_API_KEY environment variable is documented in user-facing setup instructions so users understand the credential requirement**
- **ALWAYS preserve the deferred import structure to maintain compatibility with non-generation workflows and partial command invocations**
- **ALWAYS handle anthropic.APIError and related authentication exceptions in calling code, as missing or invalid credentials will raise exceptions at runtime**

### Changelog

- - 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features
- - Performs lazy initialization of the Anthropic client by importing the Anthropic class only at call time, not at module load time
- - Returns a new Anthropic() instance configured to read the ANTHROPIC_API_KEY environment variable automatically
- - Enables the agentspec/generate.py module to be imported and used for non-generation commands (e.g., metadata collection, file discovery) without requiring a valid Anthropic API key or the anthropic package to be available
- - Avoids ImportError exceptions during dry-run paths, testing scenarios, or when users only invoke non-generation functionality
- - Each call creates a fresh client instance; no caching or singleton pattern is implemented at this level
- - Called by: agentspec.generate module functions that need to invoke Anthropic API calls (inferred from file context agentspec/generate.py)
- - Calls: anthropic.Anthropic() constructor
- - Imports used: anthropic.Anthropic (deferred/lazy import)
- - External services: Anthropic API (requires valid ANTHROPIC_API_KEY environment variable at runtime)
- - Lazy importing prevents hard dependency failures when the anthropic package is not installed or when users run agentspec commands that do not require API calls (e.g., metadata collection via agentspec.collect.collect_metadata or file discovery via agentspec.utils.collect_python_files)
- - Deferring the import until _get_client() is called allows the module to load successfully in environments where the Anthropic API is not needed, improving user experience for partial workflows
- - Relying on environment variable ANTHROPIC_API_KEY (handled by Anthropic() constructor) avoids explicit credential passing and follows standard SDK conventions
- - Alternative approaches (e.g., module-level import with try/except, singleton pattern with caching) were not used because: (1) module-level import would fail immediately if anthropic is unavailable, (2) singleton caching adds complexity without clear benefit since client instantiation is lightweight and stateless for typical use cases
- - Performance impact is negligible; client instantiation is fast and typically called only once per generate command invocation
- - Current implementation: Lazy-loads Anthropic client on first call to defer import and avoid hard dependency during non-generation commands or dry-run paths.
- - DO NOT move the import statement to module level or wrap it in a try/except that silently fails, as this defeats the purpose of lazy loading
- - DO NOT implement caching/singleton behavior without explicit requirements, as it adds complexity and state management overhead
- - DO NOT remove the inline comment explaining the lazy import pattern, as it documents the intentional design choice
- - ALWAYS ensure the ANTHROPIC_API_KEY environment variable is documented in user-facing setup instructions
- - ALWAYS preserve the deferred import structure to maintain compatibility with non-generation workflows
- - NOTE: This function will raise anthropic.APIError or related exceptions if ANTHROPIC_API_KEY is missing or invalid; callers must handle authentication failures gracefully
- - 2025-10-30: feat: robust docstring generation and Haiku defaults
- - 2025-10-29: Add auto-generator for verbose agentspec docstrings using Claude API

### Raw YAML Block

```yaml
what: |
  Lazily instantiates and returns an Anthropic API client, deferring the import of the Anthropic class until the function is first called rather than at module load time.

  Inputs: None

  Outputs: An Anthropic() instance configured to automatically read the ANTHROPIC_API_KEY environment variable.

  Behavior:
  - Calls load_env_from_dotenv() to ensure environment variables from .env files are loaded
  - Performs a deferred import of the Anthropic class from the anthropic package only at call time
  - Instantiates and returns a new Anthropic() client, which internally reads ANTHROPIC_API_KEY from the environment
  - Each invocation creates a fresh client instance; no caching or singleton pattern is implemented

  Edge cases:
  - If ANTHROPIC_API_KEY is missing or invalid, the Anthropic() constructor will raise anthropic.APIError or related authentication exceptions; callers must handle these gracefully
  - If the anthropic package is not installed, ImportError is raised only when _get_client() is called, not during module import
  - Enables agentspec/generate.py to be imported successfully in environments where the Anthropic API is not needed (e.g., dry-run paths, metadata collection, file discovery)
deps:
      calls:
        - Anthropic
        - load_env_from_dotenv
      imports:
        - agentspec.collect.collect_metadata
        - agentspec.utils.collect_python_files
        - agentspec.utils.load_env_from_dotenv
        - ast
        - json
        - os
        - pathlib.Path
        - re
        - sys
        - typing.Any
        - typing.Dict


why: |
  Lazy loading defers the hard dependency on the anthropic package until it is actually needed, allowing the module to load successfully in non-generation workflows. This approach prevents ImportError exceptions during dry-run scenarios, testing, or when users invoke only non-generation commands such as metadata collection or file discovery.

  The Anthropic() constructor automatically reads ANTHROPIC_API_KEY from the environment, following standard SDK conventions and avoiding the need for explicit credential passing.

  Lightweight client instantiation means performance impact is negligible; the client is typically created only once per generate command invocation.

  Alternative approaches (module-level import with try/except, singleton caching) were rejected because: (1) module-level import would fail immediately if anthropic is unavailable, defeating the purpose of supporting non-generation workflows, and (2) singleton caching adds unnecessary complexity and state management overhead without clear benefit for stateless, lightweight client instantiation.

guardrails:
  - DO NOT move the import statement to module level or wrap it in a try/except that silently fails; this defeats the lazy-loading purpose and reintroduces hard dependencies during module import
  - DO NOT implement caching or singleton behavior without explicit requirements; it adds complexity and state management overhead without clear benefit
  - DO NOT remove the inline comment explaining the lazy import pattern; it documents the intentional design choice for future maintainers
  - ALWAYS ensure the ANTHROPIC_API_KEY environment variable is documented in user-facing setup instructions so users understand the credential requirement
  - ALWAYS preserve the deferred import structure to maintain compatibility with non-generation workflows and partial command invocations
  - ALWAYS handle anthropic.APIError and related authentication exceptions in calling code, as missing or invalid credentials will raise exceptions at runtime

changelog:
      - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features"
      - "- Performs lazy initialization of the Anthropic client by importing the Anthropic class only at call time, not at module load time"
      - "- Returns a new Anthropic() instance configured to read the ANTHROPIC_API_KEY environment variable automatically"
      - "- Enables the agentspec/generate.py module to be imported and used for non-generation commands (e.g., metadata collection, file discovery) without requiring a valid Anthropic API key or the anthropic package to be available"
      - "- Avoids ImportError exceptions during dry-run paths, testing scenarios, or when users only invoke non-generation functionality"
      - "- Each call creates a fresh client instance; no caching or singleton pattern is implemented at this level"
      - "- Called by: agentspec.generate module functions that need to invoke Anthropic API calls (inferred from file context agentspec/generate.py)"
      - "- Calls: anthropic.Anthropic() constructor"
      - "- Imports used: anthropic.Anthropic (deferred/lazy import)"
      - "- External services: Anthropic API (requires valid ANTHROPIC_API_KEY environment variable at runtime)"
      - "- Lazy importing prevents hard dependency failures when the anthropic package is not installed or when users run agentspec commands that do not require API calls (e.g., metadata collection via agentspec.collect.collect_metadata or file discovery via agentspec.utils.collect_python_files)"
      - "- Deferring the import until _get_client() is called allows the module to load successfully in environments where the Anthropic API is not needed, improving user experience for partial workflows"
      - "- Relying on environment variable ANTHROPIC_API_KEY (handled by Anthropic() constructor) avoids explicit credential passing and follows standard SDK conventions"
      - "- Alternative approaches (e.g., module-level import with try/except, singleton pattern with caching) were not used because: (1) module-level import would fail immediately if anthropic is unavailable, (2) singleton caching adds complexity without clear benefit since client instantiation is lightweight and stateless for typical use cases"
      - "- Performance impact is negligible; client instantiation is fast and typically called only once per generate command invocation"
      - "- Current implementation: Lazy-loads Anthropic client on first call to defer import and avoid hard dependency during non-generation commands or dry-run paths."
      - "- DO NOT move the import statement to module level or wrap it in a try/except that silently fails, as this defeats the purpose of lazy loading"
      - "- DO NOT implement caching/singleton behavior without explicit requirements, as it adds complexity and state management overhead"
      - "- DO NOT remove the inline comment explaining the lazy import pattern, as it documents the intentional design choice"
      - "- ALWAYS ensure the ANTHROPIC_API_KEY environment variable is documented in user-facing setup instructions"
      - "- ALWAYS preserve the deferred import structure to maintain compatibility with non-generation workflows"
      - "- NOTE: This function will raise anthropic.APIError or related exceptions if ANTHROPIC_API_KEY is missing or invalid; callers must handle authentication failures gracefully"
      - "- 2025-10-30: feat: robust docstring generation and Haiku defaults"
      - "- 2025-10-29: Add auto-generator for verbose agentspec docstrings using Claude API"
```

---

## extract_function_info

**Location:** `agentspec/generate.py:218`

### What This Does

Parses a Python source file into an abstract syntax tree (AST) and identifies all function definitions requiring documentation. Filters functions based on docstring presence, length, and agentspec marker requirements. Returns a list of (line_number, function_name, source_code) tuples sorted in descending line number order to enable safe sequential docstring insertion without line number invalidation.

Inputs:
- filepath: Path object pointing to a valid Python source file
- require_agentspec: Boolean flag; when True, only functions lacking docstrings or missing the "---agentspec" marker are included
- update_existing: Boolean flag; when True, forces inclusion of ALL functions regardless of docstring status, bypassing normal filtering logic

Outputs:
- List of tuples: (line_number: int, function_name: str, source_code: str)
- Sorted descending by line_number (bottom-to-top processing order)
- Empty list if no functions match filtering criteria

Behavior:
- Handles both synchronous (ast.FunctionDef) and asynchronous (ast.AsyncFunctionDef) function definitions
- Traverses entire AST tree to capture module-level, class methods, and nested functions
- Docstring filtering: includes functions with no docstring OR docstrings shorter than 5 lines (unless require_agentspec=True, which checks for "---agentspec" marker instead)
- Extracts complete function source including decorators and multi-line signatures using node.lineno and node.end_lineno
- Descending sort order is critical: prevents line number shifts when inserting docstrings sequentially from bottom to top

Edge cases:
- Malformed Python syntax raises ast.SyntaxError (caller responsibility to handle)
- Functions with stub docstrings (< 5 lines) are treated as underdocumented
- Nested functions are included in results
- Async functions receive equal treatment to sync functions

### Dependencies

**Calls:**
- `ast.get_docstring`
- `ast.parse`
- `ast.walk`
- `existing.split`
- `f.read`
- `functions.append`
- `functions.sort`
- `isinstance`
- `join`
- `len`
- `open`
- `source.split`

### Why This Approach

AST parsing provides accurate syntactic understanding of function boundaries, correctly handling nested functions, decorators, and multi-line signatures where regex or text-based approaches would fail. The descending sort order is essential for correctness: when docstrings are inserted sequentially at specific line numbers, processing bottom-to-top ensures earlier insertions do not shift line numbers for functions processed later, preventing cascading index invalidation. Tuple-based return structure enables efficient positional unpacking and sorting in downstream code. Supporting both FunctionDef and AsyncFunctionDef ensures compatibility with modern Python async patterns. The 5-line threshold balances between detecting stub docstrings and respecting intentionally brief documentation. The update_existing flag provides programmatic control for regeneration workflows without requiring external filtering logic.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT reverse the sort order without updating all downstream insertion logic, as this will cause line number misalignment and syntax errors during docstring insertion**
- **DO NOT change the 5-line docstring threshold without updating related configuration and documentation, as this affects which functions are considered underdocumented**
- **DO NOT replace ast.walk() with ast.iter_child_nodes() without explicit handling for nested functions, as iter_child_nodes() only traverses immediate children**
- **DO NOT remove ast.AsyncFunctionDef handling, as this breaks support for Python 3.5+ async function documentation**
- **DO NOT use ast.get_source_segment() instead of manual line slicing without verifying Python 3.8+ availability across target environments**
- **ALWAYS preserve the (lineno, name, source_code) tuple structure, as downstream code depends on positional unpacking**
- **ALWAYS use node.end_lineno to capture complete function source including decorators and multi-line signatures**
- **ALWAYS validate that the input file contains syntactically valid Python before calling this function**
- **{'NOTE': 'Line number sorting is CRITICAL for correctness; reversing sort order without updating insertion logic will cause line number misalignment and potential syntax corruption'}**

### Changelog

- 2025-10-31: Clean up docstring formatting

### Raw YAML Block

```yaml
what: |
  Parses a Python source file into an abstract syntax tree (AST) and identifies all function definitions requiring documentation. Filters functions based on docstring presence, length, and agentspec marker requirements. Returns a list of (line_number, function_name, source_code) tuples sorted in descending line number order to enable safe sequential docstring insertion without line number invalidation.

  Inputs:
  - filepath: Path object pointing to a valid Python source file
  - require_agentspec: Boolean flag; when True, only functions lacking docstrings or missing the "---agentspec" marker are included
  - update_existing: Boolean flag; when True, forces inclusion of ALL functions regardless of docstring status, bypassing normal filtering logic

  Outputs:
  - List of tuples: (line_number: int, function_name: str, source_code: str)
  - Sorted descending by line_number (bottom-to-top processing order)
  - Empty list if no functions match filtering criteria

  Behavior:
  - Handles both synchronous (ast.FunctionDef) and asynchronous (ast.AsyncFunctionDef) function definitions
  - Traverses entire AST tree to capture module-level, class methods, and nested functions
  - Docstring filtering: includes functions with no docstring OR docstrings shorter than 5 lines (unless require_agentspec=True, which checks for "---agentspec" marker instead)
  - Extracts complete function source including decorators and multi-line signatures using node.lineno and node.end_lineno
  - Descending sort order is critical: prevents line number shifts when inserting docstrings sequentially from bottom to top

  Edge cases:
  - Malformed Python syntax raises ast.SyntaxError (caller responsibility to handle)
  - Functions with stub docstrings (< 5 lines) are treated as underdocumented
  - Nested functions are included in results
  - Async functions receive equal treatment to sync functions
deps:
      calls:
        - ast.get_docstring
        - ast.parse
        - ast.walk
        - existing.split
        - f.read
        - functions.append
        - functions.sort
        - isinstance
        - join
        - len
        - open
        - source.split
      imports:
        - agentspec.collect.collect_metadata
        - agentspec.utils.collect_python_files
        - agentspec.utils.load_env_from_dotenv
        - ast
        - json
        - os
        - pathlib.Path
        - re
        - sys
        - typing.Any
        - typing.Dict


why: |
  AST parsing provides accurate syntactic understanding of function boundaries, correctly handling nested functions, decorators, and multi-line signatures where regex or text-based approaches would fail. The descending sort order is essential for correctness: when docstrings are inserted sequentially at specific line numbers, processing bottom-to-top ensures earlier insertions do not shift line numbers for functions processed later, preventing cascading index invalidation. Tuple-based return structure enables efficient positional unpacking and sorting in downstream code. Supporting both FunctionDef and AsyncFunctionDef ensures compatibility with modern Python async patterns. The 5-line threshold balances between detecting stub docstrings and respecting intentionally brief documentation. The update_existing flag provides programmatic control for regeneration workflows without requiring external filtering logic.

guardrails:
  - DO NOT reverse the sort order without updating all downstream insertion logic, as this will cause line number misalignment and syntax errors during docstring insertion
  - DO NOT change the 5-line docstring threshold without updating related configuration and documentation, as this affects which functions are considered underdocumented
  - DO NOT replace ast.walk() with ast.iter_child_nodes() without explicit handling for nested functions, as iter_child_nodes() only traverses immediate children
  - DO NOT remove ast.AsyncFunctionDef handling, as this breaks support for Python 3.5+ async function documentation
  - DO NOT use ast.get_source_segment() instead of manual line slicing without verifying Python 3.8+ availability across target environments
  - ALWAYS preserve the (lineno, name, source_code) tuple structure, as downstream code depends on positional unpacking
  - ALWAYS use node.end_lineno to capture complete function source including decorators and multi-line signatures
  - ALWAYS validate that the input file contains syntactically valid Python before calling this function
  - NOTE: Line number sorting is CRITICAL for correctness; reversing sort order without updating insertion logic will cause line number misalignment and potential syntax corruption

changelog:

  - "2025-10-31: Clean up docstring formatting"
```

---

## inject_deterministic_metadata

**Location:** `agentspec/generate.py:324`

### What This Does

Injects deterministic metadata (dependencies and changelog) into LLM-generated docstrings in either YAML or plain text format.

For YAML format (as_agentspec_yaml=True):
- Parses deps_data (calls, imports) and changelog_data from metadata dictionary
- Locates injection point by searching for "why:" or "why |" markers; injects deps section before the first occurrence
- Falls back to injecting after "what:" section if no "why:" marker found
- Strips any LLM-generated changelog sections using regex to prevent duplication
- Injects changelog section before the closing "

### Raw YAML Block

```yaml
what: |
  Injects deterministic metadata (dependencies and changelog) into LLM-generated docstrings in either YAML or plain text format.

  For YAML format (as_agentspec_yaml=True):
  - Parses deps_data (calls, imports) and changelog_data from metadata dictionary
  - Locates injection point by searching for "why:" or "why |" markers; injects deps section before the first occurrence
  - Falls back to injecting after "what:" section if no "why:" marker found
  - Strips any LLM-generated changelog sections using regex to prevent duplication
  - Injects changelog section before the closing "
```

---

## generate_docstring

**Location:** `agentspec/generate.py:502`

### What This Does

---agentspec
what: |
  Generates AI-agent-friendly docstrings or embedded agentspec YAML blocks by invoking Claude API with code context and deterministic metadata injection.

### Raw YAML Block

```yaml
---agentspec
what: |
  Generates AI-agent-friendly docstrings or embedded agentspec YAML blocks by invoking Claude API with code context and deterministic metadata injection.

  **Inputs:**
  - `code` (str): Source code snippet to document
  - `filepath` (str): Path to the file containing the code (used for context and metadata collection)
  - `model` (str): Claude model identifier; defaults to "claude-haiku-4-5"
  - `as_agentspec_yaml` (bool): If True, generates fenced YAML block; if False, generates verbose narrative docstring
  - `base_url` (str | None): Optional custom LLM endpoint URL for provider routing
  - `provider` (str | None): LLM provider identifier ('auto', 'anthropic', 'openai', etc.); defaults to 'auto'
  - `terse` (bool): If True, uses compact prompt template and lower token limits (1500 vs 2000)
  - `diff_summary` (bool): If True, makes secondary LLM call to infer WHY from function-scoped git diffs

  **Processing flow:**
  1. Extracts function name from code using regex pattern matching
  2. Selects prompt template based on `as_agentspec_yaml` and `terse` flags
  3. Routes through unified LLM layer (`generate_chat()`) with configurable provider and base_url
  4. Returns narrative-only output (what/why/guardrails). Deterministic metadata (deps/changelog) is applied later via a safe two‑phase write.
  5. If `diff_summary=True` and function name found, collects function-scoped code diffs and makes secondary LLM call to summarize WHY changes were made, returning the narrative with an appended DIFF SUMMARY section (still narrative-only).

  **Outputs:**
  - Returns complete docstring string (narrative sections only; metadata injected deterministically)
  - Raises `anthropic.APIError`, `anthropic.RateLimitError`, `anthropic.AuthenticationError`, or provider-specific exceptions on API failures
  - Raises `ValueError` or `KeyError` if required module-scope prompts (GENERATION_PROMPT, AGENTSPEC_YAML_PROMPT, GENERATION_PROMPT_TERSE) are undefined

  **Edge cases:**
  - If function name cannot be extracted from code, metadata collection is skipped (meta remains empty dict)
  - If metadata collection fails, exception is caught and meta defaults to empty dict
  - If diff_summary requested but no code diffs found, diff summary section is omitted
  - If provider is 'auto', LLM layer auto-detects based on model name or environment configuration
  - Empty or None metadata sections are replaced with explicit placeholder messages to prevent downstream docstring generation failures
deps:
      calls:
        - Path
        - collect_function_code_diffs
        - collect_metadata
        - deps.get
        - dict
        - generate_chat
        - inject_deterministic_metadata
        - m.get
        - m.group
        - prompt.format
        - re.search
      imports:
        - agentspec.collect.collect_metadata
        - agentspec.utils.collect_python_files
        - agentspec.utils.load_env_from_dotenv
        - ast
        - json
        - os
        - pathlib.Path
        - re
        - sys
        - typing.Any
        - typing.Dict


why: |
  **Rationale for approach:**
  - Claude provides superior code understanding for nuanced, AI-consumable docstrings compared to local LLMs or rule-based approaches
  - Separates LLM generation (narrative only) from deterministic metadata injection to avoid hallucination and ensure accuracy of deps/changelog
  - Unified LLM layer (`generate_chat()`) abstracts provider differences, enabling flexible routing to Anthropic, OpenAI, or other compatible endpoints without code changes
  - Optional `diff_summary` flag enables WHY inference from git history without bloating main generation call or requiring git parsing in primary prompt
  - Terse mode reduces token usage and latency for resource-constrained scenarios while maintaining quality via lower temperature (0.0)
  - Function-scoped diff collection (via `collect_function_code_diffs()`) excludes docstrings/comments to focus on actual logic changes

  **Tradeoffs:**
  - Max tokens set to 2000 (1500 for terse) balances comprehensiveness with API cost and latency; lower values truncate valuable content, higher values add unnecessary expense
  - Temperature set to 0.2 (0.0 for terse) prioritizes consistency over creativity; higher values increase variance in docstring style
  - Metadata normalization uses defensive placeholder messages rather than raising exceptions, ensuring downstream code never encounters empty sections but potentially obscuring collection failures
  - Secondary diff_summary call adds latency and cost but provides richer WHY context without requiring complex multi-turn prompting
  - Regex-based function name extraction is simple but fragile for complex signatures; more robust parsing would require AST analysis

guardrails:
  - DO NOT pass metadata to LLM during generation; inject only after generation to prevent hallucination of false deps or changelog entries
  - DO NOT remove max_tokens limits without cost/latency analysis; unbounded tokens significantly increase API costs and response time
  - DO NOT modify hardcoded model defaults without updating documentation of breaking changes; users may depend on specific model behavior
  - DO NOT add validation that assumes specific prompt format unless GENERATION_PROMPT contract is formalized; prompt templates are module-scoped and may be overridden
  - DO NOT call this function without error handling for anthropic.APIError, anthropic.RateLimitError, anthropic.AuthenticationError, or provider-specific exceptions at call site
  - DO NOT remove or modify placeholder message strings ("No metadata found; Agentspec only allows non-deterministic data for...") as they communicate important context to downstream agents
  - DO NOT change the changelog template structure (two-item list with "- Current implementation: " stub) without updating all docstring generation code that depends on it
  - DO NOT add logic that silently drops empty metadata sections; the function's purpose is to guarantee non-empty sections for AI consumption
  - ALWAYS ensure GENERATION_PROMPT, AGENTSPEC_YAML_PROMPT, and GENERATION_PROMPT_TERSE are defined in module scope before calling
  - ALWAYS pass filepath context even if not immediately obvious why; it improves Claude's understanding of code purpose and generates more contextually appropriate docstrings
  - ALWAYS preserve the message.content[0].text extraction pattern unless Anthropic SDK changes response structure
  - ALWAYS preserve defensive None-handling in `_ensure_nonempty_metadata()` (m or {}) to accept None input gracefully
  - ALWAYS return a dictionary (never None) from metadata normalization to maintain contract with callers
changelog:
  - "No changelog available"
```

---

## insert_docstring_at_line

**Location:** `agentspec/generate.py:724`

### What This Does

```python
    """
    Insert or replace a docstring at a specific function, with optional debug context printing.

### Raw YAML Block

```yaml
    ```python
    """
    Insert or replace a docstring at a specific function, with optional debug context printing.

    WHAT:
    - Locates function by name/line using AST (with regex fallback), detects and removes existing docstring, inserts new docstring with correct indentation
    - Optionally adds print statement with first 3 docstring bullets for agent debugging
    - Validates syntax via compile before writing; returns False if compilation fails

    WHY:
    - AST-first approach handles multi-line signatures and decorators robustly; textual fallback preserves formatting better than full rewrite
    - Compile validation prevents leaving broken Python files on insertion errors
    - Bottom-to-top processing (via reversed insertion) prevents line number invalidation on repeated runs

    GUARDRAILS:
    - DO NOT modify indentation calculation (base_indent + 4) without verifying 4-space function body assumption
    - DO NOT remove quote-type detection (""" vs '''); both are valid and files may use either
    - DO NOT skip existing docstring/context-print removal; prevents duplicate accumulation on repeated runs
    - ALWAYS use reversed() when inserting new_lines to maintain correct line order
    - ALWAYS escape backslashes before quotes in print_content to prevent syntax errors in generated code
    """
    ```

    DEPENDENCIES (from code analysis):
    Calls: abs, ast.parse, ast.walk, candidate.insert, candidates.append, docstring.split, enumerate, f.readlines, f.writelines, func_line.lstrip, hasattr, isinstance, join, len, line.count, line.startswith, line.strip, list, max, min, new_lines.append, open, os.close, os.remove, path.exists, pattern.match, print, print_content.replace, py_compile.compile, re.compile, re.escape, replace, reversed, safe_doc.replace, safe_doc.split, sections.append, strip, tempfile.mkstemp, tf.writelines
    Imports: agentspec.collect.collect_metadata, agentspec.utils.collect_python_files, agentspec.utils.load_env_from_dotenv, ast, json, os, pathlib.Path, re, sys, typing.Any, typing.Dict


    CHANGELOG (from git history):
    - 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features
    - Reads a Python source file and locates the function definition at the specified line number
    - Detects and removes any existing docstring (both single-line and multi-line formats using """ or ''')
    - Removes any existing [AGENTSPEC_CONTEXT] debug print statement if present
    - Calculates proper indentation based on the function definition line to maintain code style
    - Formats the new docstring with correct triple-quote wrapping and indentation
    - Optionally adds a print statement containing the first 3 bullet points from the docstring for agent debugging
    - Writes the modified file back to disk, preserving all other code
    - Returns nothing; operates entirely through file I/O side effects
    - Called by: agentspec/generate.py (likely called from a main documentation generation pipeline)
    - Calls: open() (built-in), str.split(), str.strip(), str.lstrip(), str.replace(), reversed() (built-in), list.insert() (built-in)
    - Imports used: Path (from pathlib)
    - External services: File system access (reads and writes to filepath)
    - Uses line-by-line string manipulation rather than AST parsing to preserve exact file formatting, comments, and non-docstring content
    - Reads entire file into memory (readlines()) for simplicity; viable for typical Python source files but could be memory-intensive for very large files (>100MB)
    - Detects both """ and ''' delimiters because Python supports both, requiring careful quote type tracking
    - Handles both single-line docstrings (opening and closing quotes on same line) and multi-line docstrings with separate logic paths
    - Removes existing docstrings before insertion to prevent duplicate docstrings and ensure old content does not interfere
    - The force_context parameter allows injecting debug information into the function body itself as a print statement, enabling runtime inspection by agents
    - Indentation is calculated by measuring the function definition line's leading whitespace, then adding 4 spaces for function body content (standard Python convention)
    - Uses reversed() when inserting new lines to maintain correct order when inserting at the same index repeatedly
    - Escapes backslashes and quotes in the context print statement to prevent syntax errors when the print statement is written to file
    - [Current date]: Initial implementation with support for single/multi-line docstring detection, existing docstring removal, intelligent indentation preservation, and optional agent context printing
    - DO NOT modify the indentation calculation logic (base_indent + 4) without understanding that it assumes standard 4-space function body indentation
    - DO NOT remove the quote type detection logic (""" vs ''') as both are valid Python and files may use either convention
    - DO NOT skip the "skip existing context print" block as it prevents accumulation of duplicate print statements on repeated runs
    - DO NOT change the file I/O to use different methods (e.g., pathlib.write_text) without verifying that readlines()/writelines() behavior is preserved, as this maintains line endings
    - ALWAYS preserve the reversed() iteration when inserting new_lines to maintain correct line order
    - ALWAYS escape backslashes before quotes in print_content to prevent syntax errors in the generated print statement
    - ALWAYS verify that the insert_idx is correctly positioned after skipping existing docstrings before inserting new content
    - NOTE: This function DESTROYS any existing docstring without backup; if the docstring contains critical information not captured in the new docstring, it will be lost permanently
    - NOTE: The force_context feature truncates docstring content to first 3 bullet points; longer docstrings will lose information in the debug output
    - NOTE: This function assumes well-formed Python files; syntax errors or unusual formatting (e.g., decorators directly touching function def) may cause incorrect line detection
    - NOTE: File encoding is assumed to be UTF-8 (default for open()); files with other encodings may fail silently or produce corrupted output
    -        target = None
    -            # Insert before the first statement in the body
    -            insert_idx = (target.body[0].lineno or (func_line_idx + 1)) - 1
    -    except Exception:
    -    # Skip any existing docstring if present
    -    if insert_idx < len(lines):
    -        line = lines[insert_idx].strip()
    -        if line.startswith('"""') or line.startswith("'''"):
    -            quote_type = '"""' if '"""' in line else "'''"
    -            # Skip existing docstring
    -            if line.count(quote_type) >= 2:
    -                # Single-line docstring
    -                insert_idx += 1
    -            else:
    -                # Multi-line docstring - find end
    -                insert_idx += 1
    -                while insert_idx < len(lines):
    -                    if quote_type in lines[insert_idx]:
    -                        break
    -            # Also skip any existing context print
    -            if insert_idx < len(lines) and '[AGENTSPEC_CONTEXT]' in lines[insert_idx]:
    -                insert_idx += 1
    -            # Delete the old docstring and print
    -            del lines[func_line_idx + 1:insert_idx]
    -            insert_idx = func_line_idx + 1
    - 2025-10-30: feat: robust docstring generation and Haiku defaults
    - Reads a Python source file and locates the function definition at the specified line number
    - Detects and removes any existing docstring (both single-line and multi-line formats using """ or ''')
    - Removes any existing [AGENTSPEC_CONTEXT] debug print statement if present
    - Calculates proper indentation based on the function definition line to maintain code style
    - Formats the new docstring with correct triple-quote wrapping and indentation
    - Optionally adds a print statement containing the first 3 bullet points from the docstring for agent debugging
    - Writes the modified file back to disk, preserving all other code
    - Returns nothing; operates entirely through file I/O side effects
    - Called by: agentspec/generate.py (likely called from a main documentation generation pipeline)
    - Calls: open() (built-in), str.split(), str.strip(), str.lstrip(), str.replace(), reversed() (built-in), list.insert() (built-in)
    - Imports used: Path (from pathlib)
    - External services: File system access (reads and writes to filepath)
    - Uses line-by-line string manipulation rather than AST parsing to preserve exact file formatting, comments, and non-docstring content
    - Reads entire file into memory (readlines()) for simplicity; viable for typical Python source files but could be memory-intensive for very large files (>100MB)
    - Detects both """ and ''' delimiters because Python supports both, requiring careful quote type tracking
    - Handles both single-line docstrings (opening and closing quotes on same line) and multi-line docstrings with separate logic paths
    - Removes existing docstrings before insertion to prevent duplicate docstrings and ensure old content does not interfere
    - The force_context parameter allows injecting debug information into the function body itself as a print statement, enabling runtime inspection by agents
    - Indentation is calculated by measuring the function definition line's leading whitespace, then adding 4 spaces for function body content (standard Python convention)
    - Uses reversed() when inserting new lines to maintain correct order when inserting at the same index repeatedly
    - Escapes backslashes and quotes in the context print statement to prevent syntax errors when the print statement is written to file
    - [Current date]: Initial implementation with support for single/multi-line docstring detection, existing docstring removal, intelligent indentation preservation, and optional agent context printing
    - DO NOT modify the indentation calculation logic (base_indent + 4) without understanding that it assumes standard 4-space function body indentation
    - DO NOT remove the quote type detection logic (""" vs ''') as both are valid Python and files may use either convention
    - DO NOT skip the "skip existing context print" block as it prevents accumulation of duplicate print statements on repeated runs
    - DO NOT change the file I/O to use different methods (e.g., pathlib.write_text) without verifying that readlines()/writelines() behavior is preserved, as this maintains line endings
    - ALWAYS preserve the reversed() iteration when inserting new_lines to maintain correct line order
    - ALWAYS escape backslashes before quotes in print_content to prevent syntax errors in the generated print statement
    - ALWAYS verify that the insert_idx is correctly positioned after skipping existing docstrings before inserting new content
    - NOTE: This function DESTROYS any existing docstring without backup; if the docstring contains critical information not captured in the new docstring, it will be lost permanently
    - NOTE: The force_context feature truncates docstring content to first 3 bullet points; longer docstrings will lose information in the debug output
    - NOTE: This function assumes well-formed Python files; syntax errors or unusual formatting (e.g., decorators directly touching function def) may cause incorrect line detection
    - NOTE: File encoding is assumed to be UTF-8 (default for open()); files with other encodings may fail silently or produce corrupted output
    -    # Find the function definition line
    -    func_line_idx = lineno - 1
    -    # Find the first line after the function signature (where docstring goes)
    -    new_lines.append(f'{indent}"""
')
    -    for line in docstring.split('
'):
    -    new_lines.append(f'{indent}"""
')
    -    # Insert the new docstring
    -        lines.insert(insert_idx, line)
    -    # Write back
    -    with open(filepath, 'w') as f:
    -        f.writelines(lines)
    - 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate
    -    Insert docstring at a specific line number in a file.
    -    This handles the actual file modification.
    -    """Process a single file and generate docstrings."""
    - 2025-10-29: CRITICAL FIX: Escape quotes in context print statements to prevent syntax errors
    - 2025-10-29: CRITICAL FIX: Process functions bottom-to-top to prevent line number invalidation and syntax errors
    -    """Insert or replace docstring in function, optionally adding context print."""
    -    # Find where to insert docstring (right after function definition)
    -    func_line = node.lineno - 1
    -    # Check if there's already a docstring
    -    existing_docstring = ast.get_docstring(node)
    -    if existing_docstring:
    -        # Find and replace existing docstring
    -        start_line = func_line + 1
    -        # Skip decorators and find the actual def line
    -        for i in range(func_line, len(lines)):
    -            if 'def ' in lines[i]:
    -                start_line = i + 1
    -                break
    -        # Find end of existing docstring
    -        in_docstring = False
    -        quote_type = None
    -        end_line = start_line
    -        for i in range(start_line, len(lines)):
    -            line = lines[i].strip()
    -            if not in_docstring:
    -                if line.startswith('"""') or line.startswith("'''"):
    -                    in_docstring = True
    -                    quote_type = '"""' if '"""' in line else "'''"
    -                    if line.count(quote_type) >= 2:
    -                        # Single line docstring
    -                        end_line = i + 1
    -                        break
    -                if quote_type in line:
    -                    end_line = i + 1
    -                    break
    -        # Check if there's already a context print statement after docstring
    -        has_context_print = False
    -        if end_line < len(lines):
    -            next_line = lines[end_line].strip()
    -            if 'print(f"[AGENTSPEC_CONTEXT]' in next_line or 'print("[AGENTSPEC_CONTEXT]' in next_line:
    -                has_context_print = True
    -                end_line += 1  # Include the print line in deletion
    -        # Remove old docstring (and old print if exists)
    -        del lines[start_line:end_line]
    -        insert_line = start_line
    -    else:
    -        # Find insertion point (after function definition line)
    -        for i in range(func_line, len(lines)):
    -            if 'def ' in lines[i] or 'async def' in lines[i]:
    -                insert_line = i + 1
    -                break
    -    indent = '    '  # Assuming 4-space indent
    -    formatted = f'{indent}"""
'
    -        formatted += f'{indent}{line}
'
    -    formatted += f'{indent}"""
'
    -    # Add context-forcing print if requested
    -        # Extract key sections for print
    -        sections_to_print = []
    -        current_section = None
    -            if line.startswith('WHAT THIS DOES:'):
    -                current_section = 'WHAT_THIS_DOES'
    -            elif line.startswith('DEPENDENCIES:'):
    -                current_section = 'DEPENDENCIES'
    -            elif line.startswith('WHY THIS APPROACH:'):
    -                current_section = 'WHY_APPROACH'
    -            elif line.startswith('AGENT INSTRUCTIONS:'):
    -                current_section = 'AGENT_INSTRUCTIONS'
    -            elif line.startswith('CHANGELOG:'):
    -                current_section = None  # Skip changelog in prints
    -            elif current_section and line.startswith('-'):
    -                sections_to_print.append(line)
    -        # Add print statement that forces context
    -        func_name = node.name
    -        print_content = ' | '.join(sections_to_print[:3])  # First 3 bullet points
    -        formatted += f'{indent}print(f"[AGENTSPEC_CONTEXT] {func_name}: {print_content}")
'
    -    # Insert new docstring (and print if applicable)
    -    lines.insert(insert_line, formatted)
    -    """Find all functions that need docstrings."""
    -    def __init__(self):
    -        self.functions = []
    -    def visit_FunctionDef(self, node):
    -        if not ast.get_docstring(node) or len(ast.get_docstring(node).split('
')) < 5:
    -            self.functions.append((node.lineno, node.name))
    -        self.generic_visit(node)
    -    def visit_AsyncFunctionDef(self, node):
    -        if not ast.get_docstring(node) or len(ast.get_docstring(node).split('
')) < 5:
    -            self.functions.append((node.lineno, node.name))
    -        self.generic_visit(node)

    
```

---

## process_file

**Location:** `agentspec/generate.py:1156`

### What This Does

Processes a single Python file to identify functions lacking verbose docstrings and generates AI-consumable documentation for them using the Claude API.

Behavior:
- Extracts all function definitions from the target file using AST parsing via extract_function_info()
- Filters to functions without existing verbose docstrings (or all functions if update_existing=True)
- Displays a summary of findings to the user with function names and line numbers
- For each function needing documentation, calls generate_docstring() to create AI-generated docstrings via Claude API
- Inserts generated docstrings into the source file at correct line numbers using insert_docstring_at_line()
- Processes functions in descending line order (bottom-to-top) to prevent line number shifting during multi-insertion
- Supports dry-run mode to preview changes without file modification
- Supports force-context mode to inject print() statements alongside docstrings for debugging
- Optionally generates agentspec YAML blocks instead of traditional docstrings when as_agentspec_yaml=True
- Handles SyntaxError gracefully with early return and batch-safe failure isolation

Inputs:
- filepath: Path object pointing to Python file to process
- dry_run: bool (default False) - preview mode without file modifications
- force_context: bool (default False) - inject debug print() statements
- model: str (default "claude-haiku-4-5") - Claude model identifier
- as_agentspec_yaml: bool (default False) - generate YAML agentspec blocks instead of docstrings
- base_url: str | None (default None) - custom API endpoint URL
- provider: str | None (default 'auto') - API provider selection
- update_existing: bool (default False) - regenerate docstrings for all functions
- terse: bool (default False) - generate concise documentation
- diff_summary: bool (default False) - include diff summary in output

Outputs:
- Returns None in all cases (completion, early exit on syntax error, or dry-run)
- Side effects: modifies source file in-place (unless dry_run=True) by inserting docstrings
- Console output: progress messages, function list, success/error feedback

Edge cases:
- File with no functions: exits early with informational message
- File with all functions already documented: exits early (unless update_existing=True)
- SyntaxError in target file: caught and reported, allows batch processing to continue
- Individual function generation failure: caught and isolated, remaining functions still processed
- Dry-run mode: returns before any file modifications occur
- insert_docstring_at_line returns False: skips insertion with warning (syntax safety check)

### Dependencies

**Calls:**
- `extract_function_info`
- `functions.sort`
- `generate_docstring`
- `insert_docstring_at_line`
- `len`
- `print`
- `str`

### Why This Approach

Bottom-to-top processing prevents cascading line offset errors: insertions from end of file backward ensure previously-calculated line numbers remain valid as the file grows.

Nested exception handling (outer for SyntaxError, inner for per-function failures) allows graceful degradation: one malformed function or API error does not block remaining functions in the same file or other files in batch operations.

Dry-run mode implemented as early return before any file modifications enables safe preview and user confidence before committing changes.

Force-context flag is propagated to insert_docstring_at_line rather than handled here, maintaining separation of concerns: this function orchestrates the workflow while insert_docstring_at_line handles file mutation details.

Model parameter exposed as configurable argument (not hardcoded) allows runtime selection of Claude models, supporting experimentation with different versions and cost/quality tradeoffs.

Print statements used for user feedback rather than logging module ensures immediate console output during long-running batch operations without buffering delays.

Sequential processing chosen over parallel/concurrent to avoid Claude API rate-limit issues and maintain simplicity; docstring generation is I/O-bound but rate-limited, not CPU-bound.

Complete API response collection (not streaming) is acceptable for docstring length and simplifies error handling and insertion logic.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT modify the exception handling structure without understanding the bottom-to-top processing dependency; removing the nested try-except risks one malformed function blocking the entire file**
- **DO NOT change the order of operations (extract → check → generate → insert) without reviewing how line numbers are affected by insertions**
- **DO NOT hardcode the model name or remove the model parameter; this parameter must remain configurable for testing different Claude models**
- **DO NOT remove the dry-run early return; users depend on this to preview changes without file modification**
- **DO NOT skip the bottom-to-top sort; processing top-to-bottom will invalidate line numbers as insertions shift subsequent lines**
- **ALWAYS preserve the print statements that provide user feedback; they are critical for monitoring long-running batch operations**
- **ALWAYS pass filepath as a string (str(filepath)) when calling generate_docstring, even though filepath is a Path object, if the API expects strings**
- **ALWAYS maintain the force_context flag propagation to insert_docstring_at_line; this controls a critical feature for debugging**
- **ALWAYS process functions in bottom-to-top order (verify extract_function_info returns them sorted by line number descending) to prevent line number invalidation**
- **ALWAYS check the return value of insert_docstring_at_line; False indicates syntax safety rejection and should be reported to user**
- **{'NOTE': 'This function modifies the source file in-place; ensure files are version-controlled or backed up before running in non-dry-run mode'}**
- **{'NOTE': 'The Claude API call via generate_docstring may fail due to rate limits, authentication errors, or network issues; these are caught but users should monitor printed error messages'}**
- **{'NOTE': 'If a file has no functions or all functions already have docstrings, the function exits early without modifying anything; this is correct behavior and means repeated runs on the same file are safe'}**

### Changelog

- 2025-10-31: Clean up docstring formatting

### Raw YAML Block

```yaml
what: |
  Processes a single Python file to identify functions lacking verbose docstrings and generates AI-consumable documentation for them using the Claude API.

  Behavior:
  - Extracts all function definitions from the target file using AST parsing via extract_function_info()
  - Filters to functions without existing verbose docstrings (or all functions if update_existing=True)
  - Displays a summary of findings to the user with function names and line numbers
  - For each function needing documentation, calls generate_docstring() to create AI-generated docstrings via Claude API
  - Inserts generated docstrings into the source file at correct line numbers using insert_docstring_at_line()
  - Processes functions in descending line order (bottom-to-top) to prevent line number shifting during multi-insertion
  - Supports dry-run mode to preview changes without file modification
  - Supports force-context mode to inject print() statements alongside docstrings for debugging
  - Optionally generates agentspec YAML blocks instead of traditional docstrings when as_agentspec_yaml=True
  - Handles SyntaxError gracefully with early return and batch-safe failure isolation

  Inputs:
  - filepath: Path object pointing to Python file to process
  - dry_run: bool (default False) - preview mode without file modifications
  - force_context: bool (default False) - inject debug print() statements
  - model: str (default "claude-haiku-4-5") - Claude model identifier
  - as_agentspec_yaml: bool (default False) - generate YAML agentspec blocks instead of docstrings
  - base_url: str | None (default None) - custom API endpoint URL
  - provider: str | None (default 'auto') - API provider selection
  - update_existing: bool (default False) - regenerate docstrings for all functions
  - terse: bool (default False) - generate concise documentation
  - diff_summary: bool (default False) - include diff summary in output

  Outputs:
  - Returns None in all cases (completion, early exit on syntax error, or dry-run)
  - Side effects: modifies source file in-place (unless dry_run=True) by inserting docstrings
  - Console output: progress messages, function list, success/error feedback

  Edge cases:
  - File with no functions: exits early with informational message
  - File with all functions already documented: exits early (unless update_existing=True)
  - SyntaxError in target file: caught and reported, allows batch processing to continue
  - Individual function generation failure: caught and isolated, remaining functions still processed
  - Dry-run mode: returns before any file modifications occur
  - insert_docstring_at_line returns False: skips insertion with warning (syntax safety check)
deps:
      calls:
        - extract_function_info
        - functions.sort
        - generate_docstring
        - insert_docstring_at_line
        - len
        - print
        - str
      imports:
        - agentspec.collect.collect_metadata
        - agentspec.utils.collect_python_files
        - agentspec.utils.load_env_from_dotenv
        - ast
        - json
        - os
        - pathlib.Path
        - re
        - sys
        - typing.Any
        - typing.Dict


why: |
  Bottom-to-top processing prevents cascading line offset errors: insertions from end of file backward ensure previously-calculated line numbers remain valid as the file grows.

  Nested exception handling (outer for SyntaxError, inner for per-function failures) allows graceful degradation: one malformed function or API error does not block remaining functions in the same file or other files in batch operations.

  Dry-run mode implemented as early return before any file modifications enables safe preview and user confidence before committing changes.

  Force-context flag is propagated to insert_docstring_at_line rather than handled here, maintaining separation of concerns: this function orchestrates the workflow while insert_docstring_at_line handles file mutation details.

  Model parameter exposed as configurable argument (not hardcoded) allows runtime selection of Claude models, supporting experimentation with different versions and cost/quality tradeoffs.

  Print statements used for user feedback rather than logging module ensures immediate console output during long-running batch operations without buffering delays.

  Sequential processing chosen over parallel/concurrent to avoid Claude API rate-limit issues and maintain simplicity; docstring generation is I/O-bound but rate-limited, not CPU-bound.

  Complete API response collection (not streaming) is acceptable for docstring length and simplifies error handling and insertion logic.

guardrails:
  - DO NOT modify the exception handling structure without understanding the bottom-to-top processing dependency; removing the nested try-except risks one malformed function blocking the entire file
  - DO NOT change the order of operations (extract → check → generate → insert) without reviewing how line numbers are affected by insertions
  - DO NOT hardcode the model name or remove the model parameter; this parameter must remain configurable for testing different Claude models
  - DO NOT remove the dry-run early return; users depend on this to preview changes without file modification
  - DO NOT skip the bottom-to-top sort; processing top-to-bottom will invalidate line numbers as insertions shift subsequent lines
  - ALWAYS preserve the print statements that provide user feedback; they are critical for monitoring long-running batch operations
  - ALWAYS pass filepath as a string (str(filepath)) when calling generate_docstring, even though filepath is a Path object, if the API expects strings
  - ALWAYS maintain the force_context flag propagation to insert_docstring_at_line; this controls a critical feature for debugging
  - ALWAYS process functions in bottom-to-top order (verify extract_function_info returns them sorted by line number descending) to prevent line number invalidation
  - ALWAYS check the return value of insert_docstring_at_line; False indicates syntax safety rejection and should be reported to user
  - NOTE: This function modifies the source file in-place; ensure files are version-controlled or backed up before running in non-dry-run mode
  - NOTE: The Claude API call via generate_docstring may fail due to rate limits, authentication errors, or network issues; these are caught but users should monitor printed error messages
  - NOTE: If a file has no functions or all functions already have docstrings, the function exits early without modifying anything; this is correct behavior and means repeated runs on the same file are safe

changelog:

  - "2025-10-31: Clean up docstring formatting"
```

---

## run

**Location:** `agentspec/generate.py:1315`

### What This Does

CLI entry point for batch docstring generation across Python files with multi-provider LLM support.

Accepts a target path (file or directory). Performs provider auto-detection (Anthropic/OpenAI-compatible), validates API credentials before processing, and defaults to local Ollama (http://localhost:11434/v1) if OpenAI provider is selected without credentials.

Collects all Python files from target path using collect_python_files(), then iterates through each file, catching per-file exceptions to allow batch processing to continue despite individual failures. Dry-run mode prevents all file modifications and displays what would be processed. Returns 0 on success, 1 on credential validation failure or fatal errors.

Inputs: target (str path), dry_run (bool), force_context (bool), model (str, defaults to "claude-haiku-4-5"), as_agentspec_yaml (bool), provider (str or None, defaults to 'auto'), base_url (str or None), update_existing (bool), terse (bool), diff_summary (bool).

Outputs: int exit code (0 for success, 1 for failure).

Edge cases: target path does not exist (returns 1 after validation), missing API credentials in non-dry-run mode (returns 1 with error message), per-file processing exceptions (caught and logged, batch continues), provider auto-detection when model name contains "claude" (forces Anthropic provider).

### Dependencies

**Calls:**
- `Path`
- `collect_python_files`
- `load_env_from_dotenv`
- `lower`
- `os.getenv`
- `path.exists`
- `print`
- `process_file`
- `startswith`

### Why This Approach

Centralizes provider detection and credential validation at batch entry point to prevent runtime failures across multiple files. Auto-detection logic (checking model name for "claude" prefix, falling back to Ollama for OpenAI provider) enables offline-first workflows without credential setup while maintaining explicit control via provider parameter.

Dry-run mode provides safe preview capability before committing changes.

Per-file exception handling allows batch operations to be resilient—one malformed file or API failure does not block processing of remaining files. Early path validation prevents wasted API calls on non-existent targets.

Lazy import patterns keep optional dependencies out of non-generate code paths and reduce module load overhead for standard operations.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT proceed without valid API credentials (ANTHROPIC_API_KEY for Anthropic, OPENAI_API_KEY or base_url for OpenAI-compatible) unless dry_run=True, as this prevents silent failures mid-batch**
- **DO NOT hardcode model names or remove the model parameter; model selection must remain configurable for testing different versions**
- **DO NOT remove the dry-run early return; users depend on this to preview changes without file modification**
- **ALWAYS validate target path exists before file collection to fail fast with clear error message**
- **ALWAYS default to http://localhost:11434/v1 (local Ollama) if OpenAI provider is selected with no credentials, enabling offline-first workflows**
- **ALWAYS preserve per-file exception handling to allow batch processing to continue despite individual file failures**
- **ALWAYS load .env via load_env_from_dotenv() before credential checks to respect environment configuration**
- **ALWAYS pass base_url through to process_file to maintain provider configuration across batch operations**
- **{'NOTE': 'This function modifies source files in-place during non-dry-run execution; ensure files are version-controlled or backed up'}**
- **{'NOTE': 'Provider auto-detection checks model name for "claude" prefix (case-insensitive) to route to Anthropic; explicit provider parameter overrides this logic'}**
- **{'NOTE': 'Batch processing catches exceptions per-file but does not retry; users should monitor printed error messages for failures'}**

### Changelog

- 2025-10-31: Clean up docstring formatting

### Raw YAML Block

```yaml
what: |
  CLI entry point for batch docstring generation across Python files with multi-provider LLM support.

  Accepts a target path (file or directory). Performs provider auto-detection (Anthropic/OpenAI-compatible), validates API credentials before processing, and defaults to local Ollama (http://localhost:11434/v1) if OpenAI provider is selected without credentials.

  Collects all Python files from target path using collect_python_files(), then iterates through each file, catching per-file exceptions to allow batch processing to continue despite individual failures. Dry-run mode prevents all file modifications and displays what would be processed. Returns 0 on success, 1 on credential validation failure or fatal errors.

  Inputs: target (str path), dry_run (bool), force_context (bool), model (str, defaults to "claude-haiku-4-5"), as_agentspec_yaml (bool), provider (str or None, defaults to 'auto'), base_url (str or None), update_existing (bool), terse (bool), diff_summary (bool).

  Outputs: int exit code (0 for success, 1 for failure).

  Edge cases: target path does not exist (returns 1 after validation), missing API credentials in non-dry-run mode (returns 1 with error message), per-file processing exceptions (caught and logged, batch continues), provider auto-detection when model name contains "claude" (forces Anthropic provider).
deps:
      calls:
        - Path
        - collect_python_files
        - load_env_from_dotenv
        - lower
        - os.getenv
        - path.exists
        - print
        - process_file
        - startswith
      imports:
        - agentspec.collect.collect_metadata
        - agentspec.utils.collect_python_files
        - agentspec.utils.load_env_from_dotenv
        - ast
        - json
        - os
        - pathlib.Path
        - re
        - sys
        - typing.Any
        - typing.Dict


why: |
  Centralizes provider detection and credential validation at batch entry point to prevent runtime failures across multiple files. Auto-detection logic (checking model name for "claude" prefix, falling back to Ollama for OpenAI provider) enables offline-first workflows without credential setup while maintaining explicit control via provider parameter.

  Dry-run mode provides safe preview capability before committing changes.

  Per-file exception handling allows batch operations to be resilient—one malformed file or API failure does not block processing of remaining files. Early path validation prevents wasted API calls on non-existent targets.

  Lazy import patterns keep optional dependencies out of non-generate code paths and reduce module load overhead for standard operations.

guardrails:
  - DO NOT proceed without valid API credentials (ANTHROPIC_API_KEY for Anthropic, OPENAI_API_KEY or base_url for OpenAI-compatible) unless dry_run=True, as this prevents silent failures mid-batch
  - DO NOT hardcode model names or remove the model parameter; model selection must remain configurable for testing different versions
  - DO NOT remove the dry-run early return; users depend on this to preview changes without file modification
  - ALWAYS validate target path exists before file collection to fail fast with clear error message
  - ALWAYS default to http://localhost:11434/v1 (local Ollama) if OpenAI provider is selected with no credentials, enabling offline-first workflows
  - ALWAYS preserve per-file exception handling to allow batch processing to continue despite individual file failures
  - ALWAYS load .env via load_env_from_dotenv() before credential checks to respect environment configuration
  - ALWAYS pass base_url through to process_file to maintain provider configuration across batch operations
  - NOTE: This function modifies source files in-place during non-dry-run execution; ensure files are version-controlled or backed up
  - NOTE: Provider auto-detection checks model name for "claude" prefix (case-insensitive) to route to Anthropic; explicit provider parameter overrides this logic
  - NOTE: Batch processing catches exceptions per-file but does not retry; users should monitor printed error messages for failures

changelog:

  - "2025-10-31: Clean up docstring formatting"
```

---

## main

**Location:** `agentspec/generate.py:1429`

### What This Does

CLI entry point that parses command-line arguments and delegates to docstring generation.

Accepts a positional path argument (file or directory) and optional flags:
- `--dry-run`: Preview changes without modifying files
- `--force-context`: Insert print() statements to force LLMs to load docstrings into context
- `--model MODEL`: Specify Claude model variant (defaults to claude-haiku-4-5)

Validates that at least one argument is provided; exits with code 1 and displays usage if missing.
Extracts model name from `--model` flag if present, otherwise uses default.
Passes all parsed arguments (path, dry_run, force_context, model) to run() function.
Exits process with the exit code returned by run(), indicating success (0) or failure (non-zero).

Supported models: claude-haiku-4-5, claude-3-5-sonnet-20241022, claude-3-5-haiku-20241022.
Requires ANTHROPIC_API_KEY environment variable to be set before execution.

### Dependencies

**Calls:**
- `argv.index`
- `len`
- `print`
- `run`
- `sys.exit`

### Why This Approach

Manual argv parsing without argparse dependency keeps the single-file script minimal and self-contained.
Early validation of required path argument prevents silent failures and follows Unix convention (exit 1 on invalid input).
Model flag enables runtime switching between Claude variants without code modifications, allowing users to trade off speed/cost (Haiku) versus quality (Sonnet).
Default to claude-haiku-4-5 optimizes for speed and cost efficiency while maintaining reasonable output quality.
Boolean flags use simple string membership checks for clarity and minimal overhead in a lightweight CLI.
Usage message printed to stdout ensures visibility without requiring log configuration.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT parse arguments without updating the usage message to match all supported flags**
- **DO NOT remove ANTHROPIC_API_KEY environment variable mention from usage text**
- **DO NOT add required positional arguments without updating the len(sys.argv) < 2 validation check**
- **DO NOT alter the default model without updating all documentation and usage text that references it**
- **ALWAYS validate model_index + 1 < len(sys.argv) before accessing sys.argv[model_index + 1] to prevent IndexError**
- **{'ALWAYS pass all parsed arguments to run() in correct order': 'path, dry_run, force_context, model'}**
- **ALWAYS preserve sys.exit(1) behavior when arguments are invalid to follow Unix conventions**
- **ALWAYS ensure usage message stays in sync with actual supported flags and model options**
- **DO NOT validate model names here; invalid models will fail at API call time inside run()**
- **DO NOT perform environment variable validation here; that occurs inside run()**

### Changelog

- 2025-10-31: Clean up docstring formatting

### Raw YAML Block

```yaml
what: |
  CLI entry point that parses command-line arguments and delegates to docstring generation.

  Accepts a positional path argument (file or directory) and optional flags:
  - `--dry-run`: Preview changes without modifying files
  - `--force-context`: Insert print() statements to force LLMs to load docstrings into context
  - `--model MODEL`: Specify Claude model variant (defaults to claude-haiku-4-5)

  Validates that at least one argument is provided; exits with code 1 and displays usage if missing.
  Extracts model name from `--model` flag if present, otherwise uses default.
  Passes all parsed arguments (path, dry_run, force_context, model) to run() function.
  Exits process with the exit code returned by run(), indicating success (0) or failure (non-zero).

  Supported models: claude-haiku-4-5, claude-3-5-sonnet-20241022, claude-3-5-haiku-20241022.
  Requires ANTHROPIC_API_KEY environment variable to be set before execution.
deps:
      calls:
        - argv.index
        - len
        - print
        - run
        - sys.exit
      imports:
        - agentspec.collect.collect_metadata
        - agentspec.utils.collect_python_files
        - agentspec.utils.load_env_from_dotenv
        - ast
        - json
        - os
        - pathlib.Path
        - re
        - sys
        - typing.Any
        - typing.Dict


why: |
  Manual argv parsing without argparse dependency keeps the single-file script minimal and self-contained.
  Early validation of required path argument prevents silent failures and follows Unix convention (exit 1 on invalid input).
  Model flag enables runtime switching between Claude variants without code modifications, allowing users to trade off speed/cost (Haiku) versus quality (Sonnet).
  Default to claude-haiku-4-5 optimizes for speed and cost efficiency while maintaining reasonable output quality.
  Boolean flags use simple string membership checks for clarity and minimal overhead in a lightweight CLI.
  Usage message printed to stdout ensures visibility without requiring log configuration.

guardrails:
  - DO NOT parse arguments without updating the usage message to match all supported flags
  - DO NOT remove ANTHROPIC_API_KEY environment variable mention from usage text
  - DO NOT add required positional arguments without updating the len(sys.argv) < 2 validation check
  - DO NOT alter the default model without updating all documentation and usage text that references it
  - ALWAYS validate model_index + 1 < len(sys.argv) before accessing sys.argv[model_index + 1] to prevent IndexError
  - ALWAYS pass all parsed arguments to run() in correct order: path, dry_run, force_context, model
  - ALWAYS preserve sys.exit(1) behavior when arguments are invalid to follow Unix conventions
  - ALWAYS ensure usage message stays in sync with actual supported flags and model options
  - DO NOT validate model names here; invalid models will fail at API call time inside run()
  - DO NOT perform environment variable validation here; that occurs inside run()

changelog:

  - "2025-10-31: Clean up docstring formatting"
```

---

## apply_docstring_with_metadata

**Location:** `agentspec/insert_metadata.py:26`

### What This Does

Insert narrative-only docstring first, verify syntax, then inject deterministic
metadata (deps/changelog) and verify syntax again. If both passes succeed,
replace the target file atomically.

### Raw YAML Block

```yaml
Insert narrative-only docstring first, verify syntax, then inject deterministic
metadata (deps/changelog) and verify syntax again. If both passes succeed,
replace the target file atomically.

Notes
- This function deliberately avoids exposing metadata to any LLM.
- Works by writing to a temporary copy, then replacing the original file.
```

---

## LanguageAdapter

**Location:** `agentspec/langs/__init__.py:62`

### What This Does

Protocol defining the interface for language-specific adapters.

### Raw YAML Block

```yaml
Protocol defining the interface for language-specific adapters.

Any language adapter must implement all methods and properties defined here.
```

---

## file_extensions

**Location:** `agentspec/langs/__init__.py:70`

### What This Does

Return set of file extensions this adapter handles (e.g., {'.py', '.pyi'}).

### Raw YAML Block

```yaml
Return set of file extensions this adapter handles (e.g., {'.py', '.pyi'}).
```

---

## discover_files

**Location:** `agentspec/langs/__init__.py:76`

### What This Does

Discover all source files in target directory or return single file if target is a file.

### Raw YAML Block

```yaml
Discover all source files in target directory or return single file if target is a file.

Should respect language-specific ignore patterns and common exclusion directories.
```

---

## extract_docstring

**Location:** `agentspec/langs/__init__.py:84`

### What This Does

Extract docstring from the function/class at lineno in filepath.

### Raw YAML Block

```yaml
Extract docstring from the function/class at lineno in filepath.

Returns the raw docstring content including any agentspec blocks, or None.
```

---

## insert_docstring

**Location:** `agentspec/langs/__init__.py:92`

### What This Does

Insert or replace the docstring for the function/class at lineno in filepath.

### Raw YAML Block

```yaml
Insert or replace the docstring for the function/class at lineno in filepath.

Should handle proper indentation and formatting for the language.
```

---

## gather_metadata

**Location:** `agentspec/langs/__init__.py:100`

### What This Does

Extract function calls, imports, and other metadata for analysis.

### Raw YAML Block

```yaml
Extract function calls, imports, and other metadata for analysis.

Returns a dict with keys like 'calls', 'imports', 'called_by', etc.
```

---

## validate_syntax

**Location:** `agentspec/langs/__init__.py:108`

### What This Does

Check if the file has valid syntax after modifications.

### Raw YAML Block

```yaml
Check if the file has valid syntax after modifications.

Should return True if syntax is valid, False or raise if invalid.
```

---

## get_comment_delimiters

**Location:** `agentspec/langs/__init__.py:116`

### What This Does

Return the (start, end) delimiters for multi-line comments in this language.

### Raw YAML Block

```yaml
Return the (start, end) delimiters for multi-line comments in this language.

E.g., ('/*', '*/') for JavaScript, (', ') for Python docstrings.
```

---

## parse

**Location:** `agentspec/langs/__init__.py:124`

### What This Does

Parse source code into a language-specific AST or tree structure.

### Raw YAML Block

```yaml
Parse source code into a language-specific AST or tree structure.

Returns the parsed tree which can be traversed by other adapter methods.
```

---

## LanguageRegistry

**Location:** `agentspec/langs/__init__.py:133`

### What This Does

Global registry mapping file extensions to language adapters.

### Raw YAML Block

```yaml
Global registry mapping file extensions to language adapters.
```

---

## register

**Location:** `agentspec/langs/__init__.py:141`

### What This Does

Register an adapter for all its supported extensions.

### Raw YAML Block

```yaml
Register an adapter for all its supported extensions.
```

---

## unregister

**Location:** `agentspec/langs/__init__.py:147`

### What This Does

Unregister an adapter by extension.

### Raw YAML Block

```yaml
Unregister an adapter by extension.
```

---

## get_by_extension

**Location:** `agentspec/langs/__init__.py:152`

### What This Does

Get adapter for a file extension (e.g., '.py', '.js').

### Raw YAML Block

```yaml
Get adapter for a file extension (e.g., '.py', '.js').
```

---

## get_by_path

**Location:** `agentspec/langs/__init__.py:157`

### What This Does

Get adapter for a file by its path.

### Raw YAML Block

```yaml
Get adapter for a file by its path.
```

---

## supported_extensions

**Location:** `agentspec/langs/__init__.py:165`

### What This Does

Return all currently registered file extensions.

### Raw YAML Block

```yaml
Return all currently registered file extensions.
```

---

## list_adapters

**Location:** `agentspec/langs/__init__.py:170`

### What This Does

Return all registered adapters.

### Raw YAML Block

```yaml
Return all registered adapters.
```

---

## JavaScriptAdapter

**Location:** `agentspec/langs/javascript_adapter.py:78`

### What This Does

Language adapter for JavaScript (.js, .mjs, .jsx, .ts, .tsx) files.

### Raw YAML Block

```yaml
Language adapter for JavaScript (.js, .mjs, .jsx, .ts, .tsx) files.

Uses tree-sitter parser for reliable syntax analysis and comment extraction.
Supports ES6+ syntax including async/await, arrow functions, classes, etc.
```

---

## __init__

**Location:** `agentspec/langs/javascript_adapter.py:86`

### What This Does

Initialize the JavaScript adapter with tree-sitter parser.

### Raw YAML Block

```yaml
Initialize the JavaScript adapter with tree-sitter parser.
```

---

## file_extensions

**Location:** `agentspec/langs/javascript_adapter.py:97`

### What This Does

Return JavaScript/TypeScript file extensions this adapter handles.

### Raw YAML Block

```yaml
Return JavaScript/TypeScript file extensions this adapter handles.

Initially supports .js and .mjs; .jsx, .ts, .tsx support deferred.
```

---

## discover_files

**Location:** `agentspec/langs/javascript_adapter.py:105`

### What This Does

Discover all JavaScript files in target directory or return single file.

### Raw YAML Block

```yaml
Discover all JavaScript files in target directory or return single file.

Respects .gitignore and common exclusion directories (node_modules, etc).
```

---

## extract_docstring

**Location:** `agentspec/langs/javascript_adapter.py:145`

### What This Does

Extract JSDoc comment from function/class at lineno in filepath.

### Raw YAML Block

```yaml
Extract JSDoc comment from function/class at lineno in filepath.

Returns the docstring content (without /** */ delimiters), or None.
```

---

## insert_docstring

**Location:** `agentspec/langs/javascript_adapter.py:169`

### What This Does

Insert or replace JSDoc block for function/class at lineno.

### Raw YAML Block

```yaml
Insert or replace JSDoc block for function/class at lineno.

Formats docstring with proper JSDoc indentation and * prefix.
```

---

## gather_metadata

**Location:** `agentspec/langs/javascript_adapter.py:229`

### What This Does

Extract function calls, imports, and other metadata for a function.

### Raw YAML Block

```yaml
Extract function calls, imports, and other metadata for a function.

Returns dict with 'calls', 'imports', and 'called_by' keys.
```

---

## validate_syntax

**Location:** `agentspec/langs/javascript_adapter.py:257`

### What This Does

Check if file has valid JavaScript syntax by re-parsing.

### Raw YAML Block

```yaml
Check if file has valid JavaScript syntax by re-parsing.

Returns True if valid, raises ValueError if invalid.
```

---

## validate_syntax_string

**Location:** `agentspec/langs/javascript_adapter.py:271`

### What This Does

Validate JavaScript syntax string using tree-sitter.

### Raw YAML Block

```yaml
Validate JavaScript syntax string using tree-sitter.

Returns True if valid (no ERROR nodes), raises ValueError if invalid.
```

---

## get_comment_delimiters

**Location:** `agentspec/langs/javascript_adapter.py:289`

### What This Does

Return JavaScript multi-line comment delimiters for JSDoc.

### Raw YAML Block

```yaml
Return JavaScript multi-line comment delimiters for JSDoc.
```

---

## parse

**Location:** `agentspec/langs/javascript_adapter.py:295`

### What This Does

Parse JavaScript source code using tree-sitter.

### Raw YAML Block

```yaml
Parse JavaScript source code using tree-sitter.

Returns a tree-sitter Tree object.
```

---

## _find_preceding_jsdoc

**Location:** `agentspec/langs/javascript_adapter.py:308`

### What This Does

Find JSDoc comment immediately preceding a function/class at lineno.

### Raw YAML Block

```yaml
Find JSDoc comment immediately preceding a function/class at lineno.
```

---

## _extract_jsdoc_content

**Location:** `agentspec/langs/javascript_adapter.py:326`

### What This Does

Extract docstring content from JSDoc lines.

### Raw YAML Block

```yaml
Extract docstring content from JSDoc lines.
```

---

## _find_node_at_line

**Location:** `agentspec/langs/javascript_adapter.py:342`

### What This Does

Find function or class declaration node at specific line.

### Raw YAML Block

```yaml
Find function or class declaration node at specific line.
```

---

## _extract_function_calls

**Location:** `agentspec/langs/javascript_adapter.py:348`

### What This Does

Extract function call names from a specific function.

### Raw YAML Block

```yaml
Extract function call names from a specific function.
```

---

## _extract_imports

**Location:** `agentspec/langs/javascript_adapter.py:353`

### What This Does

Extract import statements from the module.

### Raw YAML Block

```yaml
Extract import statements from the module.
```

---

## _has_error_nodes

**Location:** `agentspec/langs/javascript_adapter.py:364`

### What This Does

Check if parse tree contains ERROR nodes.

### Raw YAML Block

```yaml
Check if parse tree contains ERROR nodes.
```

---

## PythonAdapter

**Location:** `agentspec/langs/python_adapter.py:62`

### What This Does

Language adapter for Python (.py, .pyi) files.

### Raw YAML Block

```yaml
Language adapter for Python (.py, .pyi) files.

Implements the LanguageAdapter protocol using ast module for parsing
and analysis.
```

---

## file_extensions

**Location:** `agentspec/langs/python_adapter.py:71`

### What This Does

Return Python file extensions this adapter handles.

### Raw YAML Block

```yaml
Return Python file extensions this adapter handles.
```

---

## discover_files

**Location:** `agentspec/langs/python_adapter.py:77`

### What This Does

Discover all Python files in target directory or return single file.

### Raw YAML Block

```yaml
Discover all Python files in target directory or return single file.

Delegates to agentspec.utils.collect_python_files() which respects
.gitignore and excludes common directories (.venv, __pycache__, etc).
```

---

## extract_docstring

**Location:** `agentspec/langs/python_adapter.py:88`

### What This Does

Extract docstring from function/class at lineno in filepath.

### Raw YAML Block

```yaml
Extract docstring from function/class at lineno in filepath.

Returns the raw docstring including any agentspec blocks, or None.
```

---

## insert_docstring

**Location:** `agentspec/langs/python_adapter.py:108`

### What This Does

Insert or replace docstring for function/class at lineno in filepath.

### Raw YAML Block

```yaml
Insert or replace docstring for function/class at lineno in filepath.

Handles proper indentation and preservation of function body.
```

---

## gather_metadata

**Location:** `agentspec/langs/python_adapter.py:163`

### What This Does

Extract function calls, imports, and other metadata for a function.

### Raw YAML Block

```yaml
Extract function calls, imports, and other metadata for a function.

Returns dict with 'calls', 'imports', and 'called_by' keys.
```

---

## validate_syntax

**Location:** `agentspec/langs/python_adapter.py:196`

### What This Does

Check if file has valid Python syntax.

### Raw YAML Block

```yaml
Check if file has valid Python syntax.

Returns True if valid, raises SyntaxError if invalid.
```

---

## get_comment_delimiters

**Location:** `agentspec/langs/python_adapter.py:209`

### What This Does

Return Python multi-line string delimiters.

### Raw YAML Block

```yaml
Return Python multi-line string delimiters.
```

---

## parse

**Location:** `agentspec/langs/python_adapter.py:216`

### What This Does

Parse Python source code into an AST.

### Raw YAML Block

```yaml
Parse Python source code into an AST.
```

---

## _get_indent

**Location:** `agentspec/langs/python_adapter.py:223`

### What This Does

Get indentation string for an AST node.

### Raw YAML Block

```yaml
Get indentation string for an AST node.

Returns the indentation level as a string of spaces.
```

---

## __init__

**Location:** `agentspec/lint.py:22`

### What This Does

Initializes a linter instance by storing the target filepath and establishing validation thresholds.

Inputs:
- filepath (str): Path to the file to be linted; stored as-is without normalization or validation
- min_lines (int, default=10): Minimum line count threshold used by downstream validation logic

Outputs:
- Initializes instance state with four attributes:
  - self.filepath: The provided filepath string
  - self.errors: Empty list of (line_number, message) tuples for storing linting errors
  - self.warnings: Empty list of (line_number, message) tuples for storing linting warnings
  - self.min_lines: The minimum line threshold value

Behavior:
- Performs no file I/O or filesystem operations; purely prepares linter state for lazy evaluation
- Error and warning lists are initialized as empty to prevent AttributeError during append operations in downstream methods
- Tuple structure (line_number, message) is established at initialization and must be preserved throughout the linter's lifetime

Edge cases:
- No validation of filepath existence or readability occurs; invalid paths are accepted and will fail only when actual linting methods attempt file access
- min_lines can be set to zero or negative values; validation of this parameter is deferred to downstream comparison logic

### Dependencies

### Why This Approach

Deferred file I/O enables efficient initialization without blocking on filesystem access, allowing linter instances to be created and configured before actual linting begins.

Empty list initialization for errors and warnings prevents AttributeError exceptions when downstream methods append tuples, eliminating the need for existence checks before each append operation.

Storing filepath and min_lines as instance variables eliminates the need to pass these parameters repeatedly through method calls, reducing function signatures and improving code maintainability.

Preserving filepath as a raw string without normalization keeps initialization lightweight and defers path resolution logic to methods that actually need it, following the principle of lazy evaluation.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT initialize self.errors or self.warnings to None; keep as empty lists to prevent AttributeError when downstream code appends tuples**
- **DO NOT change min_lines type from int without updating all downstream comparison operations that depend on numeric ordering**
- **ALWAYS preserve filepath as string type without normalization or Path object conversion at this stage; normalization belongs in methods that consume the path**
- **ALWAYS maintain (line_number, message) tuple ordering in errors and warnings lists; downstream code and external consumers depend on this consistent structure**
- **DO NOT perform file existence checks or I/O operations in __init__; keep initialization pure and defer validation to linting methods**

### Changelog

- - no git history available

### Raw YAML Block

```yaml
what: |
  Initializes a linter instance by storing the target filepath and establishing validation thresholds.

  Inputs:
  - filepath (str): Path to the file to be linted; stored as-is without normalization or validation
  - min_lines (int, default=10): Minimum line count threshold used by downstream validation logic

  Outputs:
  - Initializes instance state with four attributes:
    - self.filepath: The provided filepath string
    - self.errors: Empty list of (line_number, message) tuples for storing linting errors
    - self.warnings: Empty list of (line_number, message) tuples for storing linting warnings
    - self.min_lines: The minimum line threshold value

  Behavior:
  - Performs no file I/O or filesystem operations; purely prepares linter state for lazy evaluation
  - Error and warning lists are initialized as empty to prevent AttributeError during append operations in downstream methods
  - Tuple structure (line_number, message) is established at initialization and must be preserved throughout the linter's lifetime

  Edge cases:
  - No validation of filepath existence or readability occurs; invalid paths are accepted and will fail only when actual linting methods attempt file access
  - min_lines can be set to zero or negative values; validation of this parameter is deferred to downstream comparison logic
deps:
      imports:
        - agentspec.utils.collect_python_files
        - ast
        - pathlib.Path
        - sys
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Tuple
        - yaml


why: |
  Deferred file I/O enables efficient initialization without blocking on filesystem access, allowing linter instances to be created and configured before actual linting begins.

  Empty list initialization for errors and warnings prevents AttributeError exceptions when downstream methods append tuples, eliminating the need for existence checks before each append operation.

  Storing filepath and min_lines as instance variables eliminates the need to pass these parameters repeatedly through method calls, reducing function signatures and improving code maintainability.

  Preserving filepath as a raw string without normalization keeps initialization lightweight and defers path resolution logic to methods that actually need it, following the principle of lazy evaluation.

guardrails:
  - DO NOT initialize self.errors or self.warnings to None; keep as empty lists to prevent AttributeError when downstream code appends tuples
  - DO NOT change min_lines type from int without updating all downstream comparison operations that depend on numeric ordering
  - ALWAYS preserve filepath as string type without normalization or Path object conversion at this stage; normalization belongs in methods that consume the path
  - ALWAYS maintain (line_number, message) tuple ordering in errors and warnings lists; downstream code and external consumers depend on this consistent structure
  - DO NOT perform file existence checks or I/O operations in __init__; keep initialization pure and defer validation to linting methods

changelog:
      - "- no git history available"
```

---

## visit_FunctionDef

**Location:** `agentspec/lint.py:85`

### What This Does

Validates function definition docstrings and traverses child AST nodes.

This visitor method is invoked by the ast.NodeVisitor framework when encountering a FunctionDef node during AST traversal. It performs two sequential operations:

1. Docstring Validation: Calls _check_docstring(node) to inspect the function node and verify that required documentation is present and conforms to linting rules.
2. Child Node Traversal: Calls generic_visit(node) to recursively visit all child nodes within the function definition, ensuring nested functions, class definitions, and other child structures are also validated.

Inputs: node (ast.FunctionDef) - an AST node representing a function definition
Outputs: None (side effects include validation checks and recursive traversal)

Edge cases:
- Nested function definitions are validated with the same rules as top-level functions
- Functions with no docstring will trigger validation failure via _check_docstring()
- Decorated functions are processed identically to undecorated ones
- Lambda functions are not visited by this method (they use visit_Lambda if implemented)

### Dependencies

**Calls:**
- `self._check_docstring`
- `self.generic_visit`

### Why This Approach

The visitor pattern (ast.NodeVisitor) provides a clean, extensible mechanism for applying uniform linting rules across an entire AST. By implementing visit_FunctionDef, the linter automatically processes every function definition encountered during tree traversal without manual iteration.

Separating docstring validation (_check_docstring) from traversal (generic_visit) maintains single responsibility: validation logic is isolated in _check_docstring, while this method orchestrates the visitation strategy.

Recursive traversal via generic_visit ensures that nested functions and all descendant nodes are validated, preventing gaps in documentation coverage. This is critical for enforcing consistent standards across codebases with complex nesting.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT omit the generic_visit(node) call; without it, child nodes will not be visited and nested function definitions will bypass validation entirely**
- **DO NOT modify the method signature; ast.NodeVisitor requires the exact name visit_FunctionDef and the single node parameter for the framework to dispatch correctly**
- **DO NOT skip _check_docstring(node); this is the enforcement point for documentation requirements and omitting it defeats the linting purpose**
- **DO NOT assume all child nodes are functions; generic_visit handles all node types, including nested classes and other definitions**
- **DO NOT catch or suppress exceptions from _check_docstring() unless explicitly designed to collect multiple errors; premature exception handling may hide validation failures**

### Changelog

- - no git history available

### Raw YAML Block

```yaml
what: |
  Validates function definition docstrings and traverses child AST nodes.

  This visitor method is invoked by the ast.NodeVisitor framework when encountering a FunctionDef node during AST traversal. It performs two sequential operations:

  1. Docstring Validation: Calls _check_docstring(node) to inspect the function node and verify that required documentation is present and conforms to linting rules.
  2. Child Node Traversal: Calls generic_visit(node) to recursively visit all child nodes within the function definition, ensuring nested functions, class definitions, and other child structures are also validated.

  Inputs: node (ast.FunctionDef) - an AST node representing a function definition
  Outputs: None (side effects include validation checks and recursive traversal)

  Edge cases:
  - Nested function definitions are validated with the same rules as top-level functions
  - Functions with no docstring will trigger validation failure via _check_docstring()
  - Decorated functions are processed identically to undecorated ones
  - Lambda functions are not visited by this method (they use visit_Lambda if implemented)
deps:
      calls:
        - self._check_docstring
        - self.generic_visit
      imports:
        - agentspec.utils.collect_python_files
        - ast
        - pathlib.Path
        - sys
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Tuple
        - yaml


why: |
  The visitor pattern (ast.NodeVisitor) provides a clean, extensible mechanism for applying uniform linting rules across an entire AST. By implementing visit_FunctionDef, the linter automatically processes every function definition encountered during tree traversal without manual iteration.

  Separating docstring validation (_check_docstring) from traversal (generic_visit) maintains single responsibility: validation logic is isolated in _check_docstring, while this method orchestrates the visitation strategy.

  Recursive traversal via generic_visit ensures that nested functions and all descendant nodes are validated, preventing gaps in documentation coverage. This is critical for enforcing consistent standards across codebases with complex nesting.

guardrails:
  - DO NOT omit the generic_visit(node) call; without it, child nodes will not be visited and nested function definitions will bypass validation entirely
  - DO NOT modify the method signature; ast.NodeVisitor requires the exact name visit_FunctionDef and the single node parameter for the framework to dispatch correctly
  - DO NOT skip _check_docstring(node); this is the enforcement point for documentation requirements and omitting it defeats the linting purpose
  - DO NOT assume all child nodes are functions; generic_visit handles all node types, including nested classes and other definitions
  - DO NOT catch or suppress exceptions from _check_docstring() unless explicitly designed to collect multiple errors; premature exception handling may hide validation failures

changelog:
      - "- no git history available"
```

---

## visit_AsyncFunctionDef

**Location:** `agentspec/lint.py:141`

### What This Does

Validates async function definitions for required docstrings during AST traversal.

Behavior:
- Receives an AsyncFunctionDef node from the AST visitor pattern
- Invokes _check_docstring(node) to validate docstring presence on the async function
- Calls generic_visit(node) to recursively traverse and validate all child nodes
- Ensures both the async function itself and any nested definitions are checked

Inputs:
- node: ast.AsyncFunctionDef object representing an async function definition

Outputs:
- None (side effect: records linting errors via _check_docstring if docstring missing)

Edge cases:
- Async functions without docstrings trigger validation errors
- Nested async functions or inner definitions are validated recursively
- Decorated async functions are still subject to docstring requirements

### Dependencies

**Calls:**
- `self._check_docstring`
- `self.generic_visit`

### Why This Approach

Enforces consistent documentation standards across both synchronous and asynchronous function definitions.
The visitor pattern enables automatic AST traversal during the linting workflow without manual recursion.
Checking the parent node before traversing children ensures validation occurs in logical order (parent before descendants).
Async functions require the same documentation rigor as sync functions to maintain codebase consistency.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT omit the generic_visit() call; it breaks recursive traversal of child nodes and leaves nested definitions unvalidated**
- **DO NOT call generic_visit() before _check_docstring(); parent validation must occur before child traversal to maintain logical ordering**
- **DO NOT assume async functions are exempt from docstring requirements; they must meet the same standards as sync functions**

### Changelog

- - no git history available

### Raw YAML Block

```yaml
what: |
  Validates async function definitions for required docstrings during AST traversal.

  Behavior:
  - Receives an AsyncFunctionDef node from the AST visitor pattern
  - Invokes _check_docstring(node) to validate docstring presence on the async function
  - Calls generic_visit(node) to recursively traverse and validate all child nodes
  - Ensures both the async function itself and any nested definitions are checked

  Inputs:
  - node: ast.AsyncFunctionDef object representing an async function definition

  Outputs:
  - None (side effect: records linting errors via _check_docstring if docstring missing)

  Edge cases:
  - Async functions without docstrings trigger validation errors
  - Nested async functions or inner definitions are validated recursively
  - Decorated async functions are still subject to docstring requirements
deps:
      calls:
        - self._check_docstring
        - self.generic_visit
      imports:
        - agentspec.utils.collect_python_files
        - ast
        - pathlib.Path
        - sys
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Tuple
        - yaml


why: |
  Enforces consistent documentation standards across both synchronous and asynchronous function definitions.
  The visitor pattern enables automatic AST traversal during the linting workflow without manual recursion.
  Checking the parent node before traversing children ensures validation occurs in logical order (parent before descendants).
  Async functions require the same documentation rigor as sync functions to maintain codebase consistency.

guardrails:
  - DO NOT omit the generic_visit() call; it breaks recursive traversal of child nodes and leaves nested definitions unvalidated
  - DO NOT call generic_visit() before _check_docstring(); parent validation must occur before child traversal to maintain logical ordering
  - DO NOT assume async functions are exempt from docstring requirements; they must meet the same standards as sync functions

changelog:
      - "- no git history available"
```

---

## visit_ClassDef

**Location:** `agentspec/lint.py:197`

### What This Does

Validates class docstring compliance and recursively processes all child nodes within a class definition.

Inputs:
- node: An ast.ClassDef node representing a class definition in the AST

Behavior:
- Calls _check_docstring(node) to validate that the class has a compliant docstring according to project standards
- Calls self.generic_visit(node) to recursively traverse and visit all child nodes (methods, nested classes, attributes)
- Processes parent node validation before children to establish proper error context and reporting order

Outputs:
- No direct return value; side effects include docstring validation errors recorded in internal state and recursive visitation of child nodes

Edge cases:
- Classes with no docstring will be flagged by _check_docstring()
- Nested classes are recursively validated with the same rules
- Child methods within the class are visited and validated by their own visit_FunctionDef handler

### Dependencies

**Calls:**
- `self._check_docstring`
- `self.generic_visit`

### Why This Approach

The visitor pattern (ast.NodeVisitor) provides a standard, maintainable mechanism for AST traversal with automatic node-type dispatch via method naming convention (visit_[NodeType]). By validating the parent class docstring before recursing into children, the validator establishes clear error context and ensures that documentation requirements are checked top-down through the class hierarchy. This ordering also allows parent-level validation errors to be reported before child-level errors, improving readability of lint output.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT remove the generic_visit() call; it is essential for recursive traversal of all child nodes (methods, nested classes, attributes) and omitting it will cause child nodes to be silently skipped during validation**
- **DO NOT rename this method; ast.NodeVisitor uses reflection to dispatch to visit_[NodeType] methods by name, and renaming breaks the automatic dispatch mechanism**
- **DO NOT call _check_docstring() after generic_visit(); always validate the parent node before recursing into children to maintain proper error reporting order and context**
- **DO NOT modify the method signature; it must accept exactly one parameter (node) to conform to the ast.NodeVisitor interface contract**

### Changelog

- - no git history available

### Raw YAML Block

```yaml
what: |
  Validates class docstring compliance and recursively processes all child nodes within a class definition.

  Inputs:
  - node: An ast.ClassDef node representing a class definition in the AST

  Behavior:
  - Calls _check_docstring(node) to validate that the class has a compliant docstring according to project standards
  - Calls self.generic_visit(node) to recursively traverse and visit all child nodes (methods, nested classes, attributes)
  - Processes parent node validation before children to establish proper error context and reporting order

  Outputs:
  - No direct return value; side effects include docstring validation errors recorded in internal state and recursive visitation of child nodes

  Edge cases:
  - Classes with no docstring will be flagged by _check_docstring()
  - Nested classes are recursively validated with the same rules
  - Child methods within the class are visited and validated by their own visit_FunctionDef handler
what_else: |
  This method is part of an AST visitor pattern implementation that enforces documentation standards across a Python codebase. It integrates into a larger linting workflow that traverses entire module ASTs to validate docstring presence and format compliance.
deps:
      calls:
        - self._check_docstring
        - self.generic_visit
      imports:
        - agentspec.utils.collect_python_files
        - ast
        - pathlib.Path
        - sys
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Tuple
        - yaml


why: |
  The visitor pattern (ast.NodeVisitor) provides a standard, maintainable mechanism for AST traversal with automatic node-type dispatch via method naming convention (visit_[NodeType]). By validating the parent class docstring before recursing into children, the validator establishes clear error context and ensures that documentation requirements are checked top-down through the class hierarchy. This ordering also allows parent-level validation errors to be reported before child-level errors, improving readability of lint output.

guardrails:
  - DO NOT remove the generic_visit() call; it is essential for recursive traversal of all child nodes (methods, nested classes, attributes) and omitting it will cause child nodes to be silently skipped during validation
  - DO NOT rename this method; ast.NodeVisitor uses reflection to dispatch to visit_[NodeType] methods by name, and renaming breaks the automatic dispatch mechanism
  - DO NOT call _check_docstring() after generic_visit(); always validate the parent node before recursing into children to maintain proper error reporting order and context
  - DO NOT modify the method signature; it must accept exactly one parameter (node) to conform to the ast.NodeVisitor interface contract

changelog:
      - "- no git history available"
```

---

## _check_docstring

**Location:** `agentspec/lint.py:252`

### What This Does

Validates that function and class nodes contain properly formatted agentspec YAML docstring blocks with required and recommended metadata fields. The method extracts the docstring, locates the "---agentspec"/"

### Raw YAML Block

```yaml
what: |
  Validates that function and class nodes contain properly formatted agentspec YAML docstring blocks with required and recommended metadata fields. The method extracts the docstring, locates the "---agentspec"/"
```

---

## check

**Location:** `agentspec/lint.py:379`

### What This Does

Returns a tuple containing two lists of accumulated linting results from the checker instance.
The first list contains errors as Tuple[int, str] pairs (line number and error message).
The second list contains warnings as Tuple[int, str] pairs (line number and warning message).
This method provides direct access to internal state without filtering, sorting, or transformation.
Line numbers are integers (0 if unavailable), and messages are string descriptions of the linting issue.
The method returns references to the internal lists, not copies, making it a lightweight accessor.

### Dependencies

### Why This Approach

The simple getter pattern avoids unnecessary copying overhead when callers need to inspect accumulated linting results.
Returning a tuple with fixed (errors, warnings) order provides type safety and semantic clarity about which list contains which category of issues.
Direct reference returns are appropriate here since the caller receives the authoritative state of the linter at the moment of the call.
This design supports efficient batch retrieval of all linting diagnostics without intermediate transformations.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT add filtering, sorting, or transformation logic to the returned lists**
- **DO NOT change the return type from Tuple[List[Tuple[int, str]], List[Tuple[int, str]]]**
- **ALWAYS preserve the (errors, warnings) order in the returned tuple**
- **ALWAYS return direct references to self.errors and self.warnings without copying**
- **DO NOT modify the structure or content of error/warning tuples before returning**

### Changelog

- 2025-10-31: Clean up docstring formatting

### Raw YAML Block

```yaml
what: |
  Returns a tuple containing two lists of accumulated linting results from the checker instance.
  The first list contains errors as Tuple[int, str] pairs (line number and error message).
  The second list contains warnings as Tuple[int, str] pairs (line number and warning message).
  This method provides direct access to internal state without filtering, sorting, or transformation.
  Line numbers are integers (0 if unavailable), and messages are string descriptions of the linting issue.
  The method returns references to the internal lists, not copies, making it a lightweight accessor.
deps:
      imports:
        - agentspec.utils.collect_python_files
        - ast
        - pathlib.Path
        - sys
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Tuple
        - yaml


why: |
  The simple getter pattern avoids unnecessary copying overhead when callers need to inspect accumulated linting results.
  Returning a tuple with fixed (errors, warnings) order provides type safety and semantic clarity about which list contains which category of issues.
  Direct reference returns are appropriate here since the caller receives the authoritative state of the linter at the moment of the call.
  This design supports efficient batch retrieval of all linting diagnostics without intermediate transformations.

guardrails:
  - DO NOT add filtering, sorting, or transformation logic to the returned lists
  - DO NOT change the return type from Tuple[List[Tuple[int, str]], List[Tuple[int, str]]]
  - ALWAYS preserve the (errors, warnings) order in the returned tuple
  - ALWAYS return direct references to self.errors and self.warnings without copying
  - DO NOT modify the structure or content of error/warning tuples before returning

changelog:

  - "2025-10-31: Clean up docstring formatting"
```

---

## check_file

**Location:** `agentspec/lint.py:423`

### What This Does

Validates a single Python file for AgentSpec compliance by parsing its AST and running a linter visitor.

Inputs:
- filepath: Path object pointing to a Python file to validate
- min_lines: integer threshold (default 10) for minimum acceptable docstring/block length; passed to AgentSpecLinter for strictness control

Outputs:
- Returns Tuple[List[Tuple[int, str]], List[Tuple[int, str]]] where:
  - First list contains violations (line_number, error_message pairs)
  - Second list contains warnings (line_number, warning_message pairs)

Behavior:
- Reads file with UTF-8 encoding to ensure cross-platform consistency
- Parses source to AST using ast.parse with filename context
- Instantiates AgentSpecLinter visitor with filepath and min_lines parameter
- Visits AST tree to collect compliance issues
- Calls checker.check() to finalize and unpack violations/warnings lists

Error handling:
- SyntaxError: caught separately, preserves line number (or 0 if unavailable), returns as violation with "Syntax error:" prefix
- All other exceptions: caught broadly, reported as line 0 error with "Error parsing {filepath}:" prefix, returns empty warnings list
- Ensures function never raises; always returns valid tuple structure

### Dependencies

**Calls:**
- `AgentSpecLinter`
- `ast.parse`
- `checker.check`
- `checker.visit`
- `filepath.read_text`
- `str`

### Why This Approach

AST parsing provides accurate Python structure detection compared to fragile regex-based approaches, enabling reliable identification of docstrings, function signatures, and code blocks.

Visitor pattern (AgentSpecLinter) allows modular, extensible rule checking without modifying this function's core logic; new compliance rules can be added to the visitor without touching check_file.

Separate violations/warnings lists enable downstream callers to apply different severity handling—violations may fail CI/CD while warnings only log.

Broad exception handling ensures robustness on malformed or edge-case files instead of crashing the entire linting process; line 0 errors signal parse-time failures distinct from content violations.

min_lines parameter exposed as function argument allows external control over strictness without hardcoding thresholds.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT remove encoding="utf-8" from read_text(); ensures consistent behavior across Windows, macOS, and Linux**
- **DO NOT change return type signature; downstream code (CLI, CI integrations) depends on Tuple[List[Tuple[int, str]], List[Tuple[int, str]]]**
- **DO NOT skip checker.check() unpacking; may perform critical post-processing, aggregation, or filtering of collected violations/warnings**
- **ALWAYS pass min_lines through to AgentSpecLinter constructor; omitting it removes external strictness control**
- **ALWAYS preserve str(filepath) conversion for Path object compatibility with AgentSpecLinter and error messages**
- **DO NOT catch SyntaxError in the broad Exception handler; must preserve line number context from SyntaxError.lineno**

### Changelog

- 2025-10-31: Clean up docstring formatting

### Raw YAML Block

```yaml
what: |
  Validates a single Python file for AgentSpec compliance by parsing its AST and running a linter visitor.

  Inputs:
  - filepath: Path object pointing to a Python file to validate
  - min_lines: integer threshold (default 10) for minimum acceptable docstring/block length; passed to AgentSpecLinter for strictness control

  Outputs:
  - Returns Tuple[List[Tuple[int, str]], List[Tuple[int, str]]] where:
    - First list contains violations (line_number, error_message pairs)
    - Second list contains warnings (line_number, warning_message pairs)

  Behavior:
  - Reads file with UTF-8 encoding to ensure cross-platform consistency
  - Parses source to AST using ast.parse with filename context
  - Instantiates AgentSpecLinter visitor with filepath and min_lines parameter
  - Visits AST tree to collect compliance issues
  - Calls checker.check() to finalize and unpack violations/warnings lists

  Error handling:
  - SyntaxError: caught separately, preserves line number (or 0 if unavailable), returns as violation with "Syntax error:" prefix
  - All other exceptions: caught broadly, reported as line 0 error with "Error parsing {filepath}:" prefix, returns empty warnings list
  - Ensures function never raises; always returns valid tuple structure
deps:
      calls:
        - AgentSpecLinter
        - ast.parse
        - checker.check
        - checker.visit
        - filepath.read_text
        - str
      imports:
        - agentspec.utils.collect_python_files
        - ast
        - pathlib.Path
        - sys
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Tuple
        - yaml


why: |
  AST parsing provides accurate Python structure detection compared to fragile regex-based approaches, enabling reliable identification of docstrings, function signatures, and code blocks.

  Visitor pattern (AgentSpecLinter) allows modular, extensible rule checking without modifying this function's core logic; new compliance rules can be added to the visitor without touching check_file.

  Separate violations/warnings lists enable downstream callers to apply different severity handling—violations may fail CI/CD while warnings only log.

  Broad exception handling ensures robustness on malformed or edge-case files instead of crashing the entire linting process; line 0 errors signal parse-time failures distinct from content violations.

  min_lines parameter exposed as function argument allows external control over strictness without hardcoding thresholds.

guardrails:
  - DO NOT remove encoding="utf-8" from read_text(); ensures consistent behavior across Windows, macOS, and Linux
  - DO NOT change return type signature; downstream code (CLI, CI integrations) depends on Tuple[List[Tuple[int, str]], List[Tuple[int, str]]]
  - DO NOT skip checker.check() unpacking; may perform critical post-processing, aggregation, or filtering of collected violations/warnings
  - ALWAYS pass min_lines through to AgentSpecLinter constructor; omitting it removes external strictness control
  - ALWAYS preserve str(filepath) conversion for Path object compatibility with AgentSpecLinter and error messages
  - DO NOT catch SyntaxError in the broad Exception handler; must preserve line number context from SyntaxError.lineno

changelog:

  - "2025-10-31: Clean up docstring formatting"
```

---

## run

**Location:** `agentspec/lint.py:505`

### What This Does

Executes batch linting validation on Python files within a target directory to verify agentspec block compliance. Collects all Python files from the target path (file or directory), invokes check_file on each to validate agentspec requirements, and aggregates error and warning counts. Returns exit code 0 on success (no errors, and either no warnings or strict mode disabled), or exit code 1 on failure (errors present, or warnings present in strict mode). Prints per-file diagnostics with line numbers and messages, followed by a summary line showing total files checked and issue counts. Edge case: empty directory returns 0 with zero files checked and no output per file.

### Dependencies

**Calls:**
- `Path`
- `check_file`
- `collect_python_files`
- `len`
- `print`

### Why This Approach

Provides a CLI-friendly batch validation entry point for enforcing agentspec compliance across entire codebases. Separates errors (blocking issues) from warnings (advisory issues) to allow flexible enforcement policies. Strict mode enables CI/CD pipelines to enforce zero-warning policies by treating warnings as failures, while permissive mode allows warnings to pass. Summary statistics printed before exit code ensure visibility into validation scope and results.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT return 0 when strict=True and total_warnings > 0; strict mode must treat warnings as blocking failures to enforce zero-warning policies in CI/CD**
- **DO NOT skip summary statistics output; always print the separator line and final status message to ensure visibility of validation results**
- **DO NOT modify or filter files during linting; only validate and report, preserving immutability of the target codebase**
- **DO NOT assume target path exists; rely on Path and collect_python_files to handle missing paths gracefully**

### Changelog

- 2025-10-31: Clean up docstring formatting

### Raw YAML Block

```yaml
what: |
  Executes batch linting validation on Python files within a target directory to verify agentspec block compliance. Collects all Python files from the target path (file or directory), invokes check_file on each to validate agentspec requirements, and aggregates error and warning counts. Returns exit code 0 on success (no errors, and either no warnings or strict mode disabled), or exit code 1 on failure (errors present, or warnings present in strict mode). Prints per-file diagnostics with line numbers and messages, followed by a summary line showing total files checked and issue counts. Edge case: empty directory returns 0 with zero files checked and no output per file.
deps:
      calls:
        - Path
        - check_file
        - collect_python_files
        - len
        - print
      imports:
        - agentspec.utils.collect_python_files
        - ast
        - pathlib.Path
        - sys
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Tuple
        - yaml


why: |
  Provides a CLI-friendly batch validation entry point for enforcing agentspec compliance across entire codebases. Separates errors (blocking issues) from warnings (advisory issues) to allow flexible enforcement policies. Strict mode enables CI/CD pipelines to enforce zero-warning policies by treating warnings as failures, while permissive mode allows warnings to pass. Summary statistics printed before exit code ensure visibility into validation scope and results.

guardrails:
  - DO NOT return 0 when strict=True and total_warnings > 0; strict mode must treat warnings as blocking failures to enforce zero-warning policies in CI/CD
  - DO NOT skip summary statistics output; always print the separator line and final status message to ensure visibility of validation results
  - DO NOT modify or filter files during linting; only validate and report, preserving immutability of the target codebase
  - DO NOT assume target path exists; rely on Path and collect_python_files to handle missing paths gracefully

changelog:

  - "2025-10-31: Clean up docstring formatting"
```

---

## _is_anthropic_model

**Location:** `agentspec/llm.py:17`

### What This Does

This function performs model identifier classification to determine if a given string represents an Anthropic-provided language model.

**Input Processing:**
- Accepts a single parameter `model` of type `str` (though None is handled defensively)
- Normalizes input by applying the defensive pattern `(model or '')` which coerces None to empty string, then converts to lowercase via `.lower()`
- This normalization ensures consistent comparison regardless of input casing or None values

**Core Logic:**
- Performs two independent prefix checks on the normalized string using `.startswith()` method
- Returns True if the normalized model string begins with either 'claude' OR 'anthropic'
- Returns False if neither prefix matches
- Uses short-circuit OR evaluation, so if first condition is True, second is not evaluated

**Edge Cases Handled:**
- None input: Coerced to empty string, returns False (empty string doesn't start with 'claude' or 'anthropic')
- Empty string: Returns False
- Mixed case inputs: 'Claude-2', 'ANTHROPIC-CLAUDE', 'cLaUdE-3' all correctly identified as True
- Partial matches: 'claude-2-100k', 'anthropic-claude-v1' correctly identified as True
- Non-matching strings: 'gpt-4', 'llama-2', 'mistral' correctly return False
- Whitespace: Leading/trailing whitespace is NOT stripped; ' claude-2' would return False

**Return Value:**
- Boolean primitive (True or False) suitable for conditional branching in model routing logic
- No exceptions raised under any input condition (defensive design prevents AttributeError)

### Dependencies

**Calls:**
- `lower`
- `m.startswith`

### Why This Approach

**Case-Insensitive Matching:**
Model identifiers from various sources (user input, configuration files, API responses) may use inconsistent casing. Case-insensitive comparison ensures robust identification regardless of source formatting conventions.

**Defensive None Handling:**
The pattern `(model or '')` is a defensive programming practice that prevents AttributeError when None is passed. This is critical because the function signature accepts `str` but callers may pass None due to optional parameters or missing configuration. Rather than forcing callers to validate input, this function gracefully handles the edge case.

**Dual Prefix Strategy:**
Checking both 'claude' and 'anthropic' accommodates potential future naming conventions. Anthropic may release models under either prefix, and this approach future-proofs the function without requiring code changes if naming conventions evolve.

**Performance Characteristics:**
String prefix matching is O(n) where n is the length of the prefix being checked (typically 6-10 characters). This is significantly faster than regex compilation/matching or list lookups against a registry. For a function called frequently in request routing paths, this lightweight approach minimizes latency overhead.

**Alternatives Rejected:**
- Regex matching: Higher overhead, less readable, unnecessary complexity for simple prefix matching
- Exact matching against a hardcoded list: Brittle when Anthropic releases new model variants; requires code changes for each new model
- External model registry lookup: Introduces I/O latency and external dependency; inappropriate for a simple classification utility
- Whitespace normalization: Not included because model identifiers are typically well-formed; adding `.strip()` would mask upstream data quality issues

### ⚠️ Guardrails (CRITICAL)

- **DO NOT modify the prefix strings ('claude', 'anthropic') without auditing all downstream code that depends on this function's classification. Changes here affect model routing throughout the system and could cause requests to be sent to wrong API endpoints.**
- **DO NOT remove the defensive `(model or '')` pattern without ensuring all callers guarantee non-None input and adding explicit type validation. This pattern is the only safeguard against AttributeError from None values.**
- **DO NOT add `.strip()` to normalize whitespace without verifying that all upstream model identifier sources are properly formatted. Silently accepting malformed identifiers could mask data quality issues.**
- **DO NOT change the return type from boolean without updating all conditional logic that depends on this function. This function is used in if/elif chains and ternary operators throughout the codebase.**
- **DO NOT add regex or complex matching logic without performance testing. This function may be called in hot paths (per-request model selection); any performance regression could impact API latency.**
- **ALWAYS maintain both prefix checks ('claude' AND 'anthropic') unless Anthropic's official documentation explicitly deprecates one naming convention.**
- **ALWAYS preserve case-insensitivity behavior; model identifiers from configuration and user input cannot be guaranteed to use consistent casing.**
- **{'CRITICAL': "This function is a gatekeeper for routing requests to Anthropic's API. Any logic error here will cause misrouting of requests, potentially sending Anthropic-destined requests to other providers or vice versa, resulting in authentication failures or incorrect API behavior."}**

### Changelog

- 2025-10-31: Clean up docstring formatting

### Raw YAML Block

```yaml
what: |
  This function performs model identifier classification to determine if a given string represents an Anthropic-provided language model.

  **Input Processing:**
  - Accepts a single parameter `model` of type `str` (though None is handled defensively)
  - Normalizes input by applying the defensive pattern `(model or '')` which coerces None to empty string, then converts to lowercase via `.lower()`
  - This normalization ensures consistent comparison regardless of input casing or None values

  **Core Logic:**
  - Performs two independent prefix checks on the normalized string using `.startswith()` method
  - Returns True if the normalized model string begins with either 'claude' OR 'anthropic'
  - Returns False if neither prefix matches
  - Uses short-circuit OR evaluation, so if first condition is True, second is not evaluated

  **Edge Cases Handled:**
  - None input: Coerced to empty string, returns False (empty string doesn't start with 'claude' or 'anthropic')
  - Empty string: Returns False
  - Mixed case inputs: 'Claude-2', 'ANTHROPIC-CLAUDE', 'cLaUdE-3' all correctly identified as True
  - Partial matches: 'claude-2-100k', 'anthropic-claude-v1' correctly identified as True
  - Non-matching strings: 'gpt-4', 'llama-2', 'mistral' correctly return False
  - Whitespace: Leading/trailing whitespace is NOT stripped; ' claude-2' would return False

  **Return Value:**
  - Boolean primitive (True or False) suitable for conditional branching in model routing logic
  - No exceptions raised under any input condition (defensive design prevents AttributeError)
deps:
      calls:
        - lower
        - m.startswith
      imports:
        - __future__.annotations
        - os
        - typing.Dict
        - typing.List
        - typing.Optional


why: |
  **Case-Insensitive Matching:**
  Model identifiers from various sources (user input, configuration files, API responses) may use inconsistent casing. Case-insensitive comparison ensures robust identification regardless of source formatting conventions.

  **Defensive None Handling:**
  The pattern `(model or '')` is a defensive programming practice that prevents AttributeError when None is passed. This is critical because the function signature accepts `str` but callers may pass None due to optional parameters or missing configuration. Rather than forcing callers to validate input, this function gracefully handles the edge case.

  **Dual Prefix Strategy:**
  Checking both 'claude' and 'anthropic' accommodates potential future naming conventions. Anthropic may release models under either prefix, and this approach future-proofs the function without requiring code changes if naming conventions evolve.

  **Performance Characteristics:**
  String prefix matching is O(n) where n is the length of the prefix being checked (typically 6-10 characters). This is significantly faster than regex compilation/matching or list lookups against a registry. For a function called frequently in request routing paths, this lightweight approach minimizes latency overhead.

  **Alternatives Rejected:**
  - Regex matching: Higher overhead, less readable, unnecessary complexity for simple prefix matching
  - Exact matching against a hardcoded list: Brittle when Anthropic releases new model variants; requires code changes for each new model
  - External model registry lookup: Introduces I/O latency and external dependency; inappropriate for a simple classification utility
  - Whitespace normalization: Not included because model identifiers are typically well-formed; adding `.strip()` would mask upstream data quality issues

guardrails:
  - DO NOT modify the prefix strings ('claude', 'anthropic') without auditing all downstream code that depends on this function's classification. Changes here affect model routing throughout the system and could cause requests to be sent to wrong API endpoints.
  - DO NOT remove the defensive `(model or '')` pattern without ensuring all callers guarantee non-None input and adding explicit type validation. This pattern is the only safeguard against AttributeError from None values.
  - DO NOT add `.strip()` to normalize whitespace without verifying that all upstream model identifier sources are properly formatted. Silently accepting malformed identifiers could mask data quality issues.
  - DO NOT change the return type from boolean without updating all conditional logic that depends on this function. This function is used in if/elif chains and ternary operators throughout the codebase.
  - DO NOT add regex or complex matching logic without performance testing. This function may be called in hot paths (per-request model selection); any performance regression could impact API latency.
  - ALWAYS maintain both prefix checks ('claude' AND 'anthropic') unless Anthropic's official documentation explicitly deprecates one naming convention.
  - ALWAYS preserve case-insensitivity behavior; model identifiers from configuration and user input cannot be guaranteed to use consistent casing.
  - CRITICAL: This function is a gatekeeper for routing requests to Anthropic's API. Any logic error here will cause misrouting of requests, potentially sending Anthropic-destined requests to other providers or vice versa, resulting in authentication failures or incorrect API behavior.

changelog:

  - "2025-10-31: Clean up docstring formatting"
```

---

## generate_chat

**Location:** `agentspec/llm.py:95`

### What This Does

---agentspec
    what: |
      generate_chat() is a unified LLM interface that routes requests to either Anthropic Claude or OpenAI-compatible providers (including local Ollama instances). It accepts a model identifier, message list, temperature, max_tokens, optional base_url, and provider hint, returning a single string response.

### Raw YAML Block

```yaml
    ---agentspec
    what: |
      generate_chat() is a unified LLM interface that routes requests to either Anthropic Claude or OpenAI-compatible providers (including local Ollama instances). It accepts a model identifier, message list, temperature, max_tokens, optional base_url, and provider hint, returning a single string response.

      **Anthropic Path (Claude models):**
      - Triggered when provider='anthropic' is explicit, or when _is_anthropic_model(model) returns True and provider is not forced to 'openai'
      - Concatenates all 'system' and 'user' role messages with "

" separator into a single prompt string
      - Filters out 'assistant' role messages (one-way conversation)
      - Creates Anthropic client with lazy import; raises RuntimeError if anthropic SDK not installed
      - Calls client.messages.create() with model, max_tokens, temperature, and reconstructed single-message format
      - Returns resp.content[0].text directly

      **OpenAI-Compatible Path (default):**
      - Triggered for all non-Anthropic models or when provider='openai' is explicit
      - Resolves API key from environment: OPENAI_API_KEY → AGENTSPEC_OPENAI_API_KEY → 'not-needed' (permissive fallback for local services)
      - Resolves base_url from parameter → OPENAI_BASE_URL → AGENTSPEC_OPENAI_BASE_URL → OLLAMA_BASE_URL → 'https://api.openai.com/v1' (default OpenAI)
      - Creates OpenAI client with resolved base_url and api_key
      - **Primary attempt: Responses API** (newer OpenAI interface)
        - Concatenates system + user/assistant messages with "

" separator into input_text
        - Calls client.responses.create() with model, input, temperature, max_output_tokens
        - Extracts text via defensive attribute chain: output_text → output[].content.text → text
        - Returns first non-empty text found; silently catches all exceptions and falls through
      - **Fallback: Chat Completions API** (OpenAI-compatible standard)
        - Normalizes message roles: unknown roles default to 'user'
        - Preserves original message structure (system/user/assistant roles intact)
        - Calls client.chat.completions.create() with model, messages, temperature, max_tokens
        - Returns comp.choices[0].message.content or empty string if response malformed

      **Edge Cases Handled:**
      - Missing dependencies: Raises RuntimeError with installation instructions (lazy import pattern)
      - Empty/None content fields: Defaults to empty string
      - Malformed response objects: Defensive hasattr/getattr chain with fallbacks
      - Responses API unavailable: Silent exception catch, automatic fallback to Chat Completions
      - Invalid message roles: Coerced to 'user' role
      - Missing API key for local services: Accepts 'not-needed' placeholder
      - Empty response choices: Returns empty string instead of crashing
    deps:
          calls:
            - Anthropic
            - OpenAI
            - RuntimeError
            - _is_anthropic_model
            - completions.create
            - getattr
            - hasattr
            - isinstance
            - join
            - lower
            - m.get
            - messages.create
            - oai_messages.append
            - os.getenv
            - responses.create
            - str
            - user_content.append
          imports:
            - __future__.annotations
            - os
            - typing.Dict
            - typing.List
            - typing.Optional


    why: |
      **Provider Routing:** The dual-path design accommodates two distinct LLM ecosystems with incompatible APIs. Anthropic's message format differs fundamentally from OpenAI's, requiring separate client initialization and message reconstruction. The provider parameter allows explicit control while defaulting to auto-detection via _is_anthropic_model(), reducing caller burden.

      **Lazy Imports:** Both anthropic and openai SDKs are imported only when needed. This avoids hard dependencies and allows users to install only the SDK(s) they require, reducing package bloat and installation friction.

      **Message Concatenation (Anthropic):** Claude's API expects a different message structure than the input format. Rather than complex transformation logic, concatenating system+user content into a single prompt is sufficient for most use cases and simplifies the interface. Assistant messages are dropped because the Anthropic path reconstructs messages as a single user message, which doesn't preserve multi-turn conversation history.

      **Responses API with Chat Completions Fallback:** The Responses API is OpenAI's newer, simpler interface but not all providers support it (e.g., Ollama, local deployments). The try/except pattern attempts the modern API first, then silently falls back to the widely-supported Chat Completions API. This maximizes compatibility without requiring caller awareness of provider capabilities.

      **Defensive Response Extraction:** Response objects vary across providers and API versions. The hasattr/getattr chain with multiple fallback paths (output_text → output → text) ensures robustness against schema variations without requiring strict type checking.

      **Environment Variable Hierarchy:** Multiple environment variable names (OPENAI_API_KEY, AGENTSPEC_OPENAI_API_KEY, OLLAMA_BASE_URL) allow flexible configuration across different deployment contexts (CI/CD, Docker, local dev) without code changes. The 'not-needed' fallback permits local services that don't require authentication.

      **Tradeoff: Simplicity vs. Fidelity:** Message concatenation loses conversation structure (no role preservation in Anthropic path). This is acceptable for single-turn use cases but limits multi-turn dialogue. The alternative (full message transformation) would add complexity and maintenance burden.

    guardrails:
      - "DO NOT remove the lazy import pattern for anthropic/openai. Hard dependencies would break installations for users who only need one provider. The try/except ImportError is critical for graceful degradation."
      - "DO NOT change the message concatenation separator from '\n\n' without testing against actual Claude models. This separator is semantic—changing it alters prompt meaning and model behavior."
      - "DO NOT remove the Responses API try/except fallback. Silently catching exceptions here is intentional for provider compatibility. Removing it would break Ollama and other Chat Completions-only providers."
      - "DO NOT modify the environment variable resolution order without coordinating with deployment documentation. The hierarchy (parameter → OPENAI_BASE_URL → AGENTSPEC_OPENAI_BASE_URL → OLLAMA_BASE_URL → default) is relied upon by infrastructure automation."
      - "DO NOT change the 'not-needed' API key fallback without understanding local service requirements. Some providers (Ollama, local LLaMA) don't validate API keys; removing this breaks their usage."
      - "DO NOT add strict type validation to response extraction (e.g., isinstance
    changelog:
      - "2025-10-31: Clean up docstring formatting"

    
```

---

## _is_excluded_by_dir

**Location:** `agentspec/utils.py:36`

### What This Does

Checks if a file path contains any excluded directory names by iterating through all path components.

Inputs:
- path: A pathlib.Path object representing a file or directory path

Behavior:
- Decomposes the path into individual components using Path.parts (cross-platform safe)
- Iterates through each component sequentially
- Compares each component against DEFAULT_EXCLUDE_DIRS set for membership
- Returns True immediately upon finding the first excluded directory name
- Returns False if iteration completes without matches

Outputs:
- Boolean: True if any path component matches an excluded directory name, False otherwise

Edge cases:
- Handles nested excluded directories at any depth (e.g., .git/objects/pack)
- Works correctly with relative and absolute paths
- Preserves Windows and Unix path separator semantics via pathlib.Path
- Empty paths or single-component paths are handled safely

### Dependencies

### Why This Approach

Enables efficient filtering of version control, build, and cache directories during file system traversal without recursing into excluded subtrees.

Design rationale:
- Early return on first match optimizes common case where excluded dirs appear near root
- Set membership testing (DEFAULT_EXCLUDE_DIRS) provides O(1) lookup per component
- Path.parts abstraction ensures code works identically on Windows and Unix without manual separator handling
- Checking all components catches excluded dirs at any nesting level, preventing accidental traversal into .venv/lib or .git/objects

### ⚠️ Guardrails (CRITICAL)

- **DO NOT use string.split() instead of Path.parts; manual splitting breaks cross-platform compatibility and requires separator awareness**
- **DO NOT assume DEFAULT_EXCLUDE_DIRS is defined; verify it exists at module scope before calling this function**
- **ALWAYS use pathlib.Path for path decomposition to maintain platform independence**
- **ALWAYS ensure DEFAULT_EXCLUDE_DIRS contains only universally excluded directory names (.git, .venv, __pycache__, node_modules, etc.) that should never be traversed**
- **DO NOT modify the path object; this function is read-only and must remain side-effect free**

### Changelog

- - 2025-10-30: feat: robust docstring generation and Haiku defaults
- - 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate

### Raw YAML Block

```yaml
what: |
  Checks if a file path contains any excluded directory names by iterating through all path components.

  Inputs:
  - path: A pathlib.Path object representing a file or directory path

  Behavior:
  - Decomposes the path into individual components using Path.parts (cross-platform safe)
  - Iterates through each component sequentially
  - Compares each component against DEFAULT_EXCLUDE_DIRS set for membership
  - Returns True immediately upon finding the first excluded directory name
  - Returns False if iteration completes without matches

  Outputs:
  - Boolean: True if any path component matches an excluded directory name, False otherwise

  Edge cases:
  - Handles nested excluded directories at any depth (e.g., .git/objects/pack)
  - Works correctly with relative and absolute paths
  - Preserves Windows and Unix path separator semantics via pathlib.Path
  - Empty paths or single-component paths are handled safely
deps:
      imports:
        - __future__.annotations
        - os
        - pathlib.Path
        - subprocess
        - typing.Iterable
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  Enables efficient filtering of version control, build, and cache directories during file system traversal without recursing into excluded subtrees.

  Design rationale:
  - Early return on first match optimizes common case where excluded dirs appear near root
  - Set membership testing (DEFAULT_EXCLUDE_DIRS) provides O(1) lookup per component
  - Path.parts abstraction ensures code works identically on Windows and Unix without manual separator handling
  - Checking all components catches excluded dirs at any nesting level, preventing accidental traversal into .venv/lib or .git/objects

guardrails:
  - DO NOT use string.split() instead of Path.parts; manual splitting breaks cross-platform compatibility and requires separator awareness
  - DO NOT assume DEFAULT_EXCLUDE_DIRS is defined; verify it exists at module scope before calling this function
  - ALWAYS use pathlib.Path for path decomposition to maintain platform independence
  - ALWAYS ensure DEFAULT_EXCLUDE_DIRS contains only universally excluded directory names (.git, .venv, __pycache__, node_modules, etc.) that should never be traversed
  - DO NOT modify the path object; this function is read-only and must remain side-effect free

changelog:
      - "- 2025-10-30: feat: robust docstring generation and Haiku defaults"
      - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate"
```

---

## _find_git_root

**Location:** `agentspec/utils.py:99`

### What This Does

Locates the root directory of a Git repository by traversing upward from a starting path.

Accepts a Path object representing either a file or directory and resolves it to an absolute path.
If the input path points to a file, extracts its parent directory as the starting search point.
Iterates through the directory hierarchy from the current location upward through all ancestor directories.
For each directory in the traversal chain, checks whether a `.git` subdirectory exists at that location.
Returns the first ancestor directory containing a `.git` folder (indicating a Git repository root), or None if no Git repository is found in the entire ancestry chain.

Edge cases handled:
- File inputs are converted to their parent directory before searching
- Symlinks are resolved to their canonical paths via resolve()
- Returns None gracefully when operating outside any Git repository
- Efficiently terminates on first match without traversing entire filesystem

### Dependencies

**Calls:**
- `cur.is_file`
- `exists`
- `start.resolve`

### Why This Approach

Enables repository boundary detection for operations like respecting .gitignore files and determining project scope without making external Git subprocess calls.

Using pathlib.Path provides cross-platform compatibility (Windows, macOS, Linux) without manual path separator handling.
The resolve() call ensures absolute paths are used, preventing issues with relative path traversal and symlink resolution.
The file-to-parent conversion handles both file and directory inputs gracefully, allowing callers to pass either without special handling.
Iterating through [cur, *cur.parents] is more efficient than a while loop with manual parent traversal, as it leverages pathlib's built-in parents tuple.
Checking for .git directory existence is the standard Git convention for identifying repository roots (more reliable than checking for .gitignore alone, which may not exist in all repos).
Early return on first match avoids unnecessary traversal of the entire filesystem hierarchy.
Returning None (rather than raising an exception) allows graceful degradation when operating outside a Git repository, enabling callers to implement fallback behavior.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT modify the .git directory name check; it is a Git standard and must remain hardcoded**
- **DO NOT change the return type from Path | None to raise exceptions instead; callers depend on None for non-repository contexts**
- **DO NOT remove the file-to-parent conversion logic; it enables flexible input handling for both files and directories**
- **ALWAYS preserve the resolve() call to ensure absolute path handling and symlink resolution**
- **ALWAYS maintain the iteration order from current directory upward; ancestors must be checked in order from closest to furthest**
- **{'NOTE': 'This function performs filesystem I/O operations (exists() checks) for each ancestor directory; in deeply nested directory structures or slow filesystems, this could be a performance bottleneck if called repeatedly without caching'}**

### Changelog

- 2025-10-31: Clean up docstring formatting

### Raw YAML Block

```yaml
what: |
  Locates the root directory of a Git repository by traversing upward from a starting path.

  Accepts a Path object representing either a file or directory and resolves it to an absolute path.
  If the input path points to a file, extracts its parent directory as the starting search point.
  Iterates through the directory hierarchy from the current location upward through all ancestor directories.
  For each directory in the traversal chain, checks whether a `.git` subdirectory exists at that location.
  Returns the first ancestor directory containing a `.git` folder (indicating a Git repository root), or None if no Git repository is found in the entire ancestry chain.

  Edge cases handled:
  - File inputs are converted to their parent directory before searching
  - Symlinks are resolved to their canonical paths via resolve()
  - Returns None gracefully when operating outside any Git repository
  - Efficiently terminates on first match without traversing entire filesystem
deps:
      calls:
        - cur.is_file
        - exists
        - start.resolve
      imports:
        - __future__.annotations
        - os
        - pathlib.Path
        - subprocess
        - typing.Iterable
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  Enables repository boundary detection for operations like respecting .gitignore files and determining project scope without making external Git subprocess calls.

  Using pathlib.Path provides cross-platform compatibility (Windows, macOS, Linux) without manual path separator handling.
  The resolve() call ensures absolute paths are used, preventing issues with relative path traversal and symlink resolution.
  The file-to-parent conversion handles both file and directory inputs gracefully, allowing callers to pass either without special handling.
  Iterating through [cur, *cur.parents] is more efficient than a while loop with manual parent traversal, as it leverages pathlib's built-in parents tuple.
  Checking for .git directory existence is the standard Git convention for identifying repository roots (more reliable than checking for .gitignore alone, which may not exist in all repos).
  Early return on first match avoids unnecessary traversal of the entire filesystem hierarchy.
  Returning None (rather than raising an exception) allows graceful degradation when operating outside a Git repository, enabling callers to implement fallback behavior.

guardrails:
  - DO NOT modify the .git directory name check; it is a Git standard and must remain hardcoded
  - DO NOT change the return type from Path | None to raise exceptions instead; callers depend on None for non-repository contexts
  - DO NOT remove the file-to-parent conversion logic; it enables flexible input handling for both files and directories
  - ALWAYS preserve the resolve() call to ensure absolute path handling and symlink resolution
  - ALWAYS maintain the iteration order from current directory upward; ancestors must be checked in order from closest to furthest
  - NOTE: This function performs filesystem I/O operations (exists() checks) for each ancestor directory; in deeply nested directory structures or slow filesystems, this could be a performance bottleneck if called repeatedly without caching

changelog:

  - "2025-10-31: Clean up docstring formatting"
```

---

## _git_check_ignore

**Location:** `agentspec/utils.py:165`

### Raw YAML Block

```yaml
what: |
  Batch-checks which file paths are ignored by Git according to .gitignore rules, returning only the ignored subset as a Set[Path].

  Converts input paths to absolute form, then to relative paths anchored at repo_root to minimize stdin payload. Chunks the relative paths into groups of 1024 to prevent subprocess buffer exhaustion on large file lists. Constructs NUL-delimited input payload (each path followed by  ) and invokes `git check-ignore -z --stdin` with stderr suppressed. Parses the NUL-delimited output by splitting on  , decodes each segment back to a path string, resolves to absolute form, and accumulates into the ignored set. Returns empty set on any exception (Git unavailable, not a Git repository, or subprocess failure), enabling graceful degradation.
deps:
      calls:
        - encode
        - ignored.add
        - join
        - len
        - out.split
        - p.resolve
        - range
        - rel_s.decode
        - relative_to
        - resolve
        - set
        - str
        - subprocess.run
      imports:
        - __future__.annotations
        - os
        - pathlib.Path
        - subprocess
        - typing.Iterable
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  NUL-delimited format (via -z flag) is the only reliable mechanism to handle filenames containing embedded newlines, spaces, or other special characters without escaping ambiguity or parsing errors. Chunking balances throughput and memory efficiency against subprocess buffer limits; 1024 paths per chunk is a conservative threshold that avoids payload bloat while maintaining reasonable batch size. Converting to relative paths before passing to Git reduces stdin size and ensures Git interprets paths correctly relative to the repository root. Silent exception handling allows the function to degrade gracefully when Git is unavailable or the directory is not a Git repository, rather than propagating errors to callers.

guardrails:
  - DO NOT modify the chunking size (1024) without benchmarking against large file lists; changing it may cause subprocess buffer exhaustion or unnecessary overhead.
  - DO NOT remove the try-except wrapper; it ensures the function returns an empty set rather than raising exceptions when Git is unavailable or the repo is invalid.
  - DO NOT change the NUL delimiter scheme ( ); any other delimiter (newline, space, etc.) will fail on filenames containing those characters.
  - ALWAYS resolve paths to absolute form before returning; relative paths would be ambiguous to callers and inconsistent with input semantics.
  - ALWAYS use relative_to(repo_root) before passing paths to Git; this ensures Git interprets them correctly within the repository context.
  - ALWAYS preserve the -z flag with git check-ignore; without it, the command cannot reliably parse filenames with special characters.

changelog:

  - "2025-10-31: Clean up docstring formatting"
```

---

## _find_agentspecignore

**Location:** `agentspec/utils.py:243`

### What This Does

Find .agentspecignore file in repo root.

### Raw YAML Block

```yaml
Find .agentspecignore file in repo root.
```

---

## _parse_agentspecignore

**Location:** `agentspec/utils.py:250`

### What This Does

Parse .agentspecignore file and return list of patterns (filtered for comments and empty lines).

### Raw YAML Block

```yaml
Parse .agentspecignore file and return list of patterns (filtered for comments and empty lines).
```

---

## _matches_pattern

**Location:** `agentspec/utils.py:264`

### What This Does

Check if a path matches a gitignore-style pattern.

### Raw YAML Block

```yaml
Check if a path matches a gitignore-style pattern.

Supports:
- * wildcards (via fnmatch)
- **/ for any directory depth
- Leading / for absolute match from repo root
- Trailing / for directories only
```

---

## _check_agentspecignore

**Location:** `agentspec/utils.py:321`

### What This Does

Check if a path is ignored by .agentspecignore. Returns True if ignored.

### Raw YAML Block

```yaml
Check if a path is ignored by .agentspecignore. Returns True if ignored.
```

---

## collect_python_files

**Location:** `agentspec/utils.py:338`

### What This Does

Recursively discovers Python files in a target path, respecting .gitignore rules and excluding common non-source directories.

For file input: validates .py extension and checks if the file is in an excluded directory or gitignored; returns a single-element list containing the file, or an empty list if validation fails.

For directory input: recursively globs all .py files using rglob("*.py"), filters out files in excluded directories (.venv, __pycache__, .git, build, dist, and similar), then applies .gitignore filtering if a git repository root is found.

Returns a sorted list of absolute Path objects representing all discovered Python files that pass all filters. Returns an empty list if the target is a non-.py file, is in an excluded directory, or is gitignored.

Gracefully degrades to unfiltered discovery (still excluding common directories) if no git repository root is found, allowing the function to work outside git repositories.

Edge cases: symlinks are resolved before gitignore comparison to ensure correct path matching; lazy evaluation of repo_root and ignored set avoids expensive git operations when not needed; sorting by string representation ensures deterministic, human-readable output across different runs and platforms.

### Dependencies

**Calls:**
- `_find_git_root`
- `_git_check_ignore`
- `_is_excluded_by_dir`
- `files.sort`
- `p.is_file`
- `p.resolve`
- `str`
- `target.is_file`
- `target.resolve`
- `target.rglob`

### Why This Approach

.gitignore integration respects developer intent by excluding files already marked as ignored, reducing noise in analysis and respecting repository conventions.

Excluded directory filtering prevents wasteful traversal of virtual environments, build artifacts, and cache directories, which would be incorrect to analyze and degrade performance.

Graceful degradation when git is unavailable or target is not in a repository ensures the function remains useful in non-git contexts.

Two-path branching (file vs. directory) allows efficient handling of both single-file and bulk discovery scenarios without redundant logic.

Use of resolved paths in gitignore checks ensures consistent comparison even with symlinks or relative path variations.

Sorting by string representation of paths ensures deterministic output order across different runs and platforms, critical for reproducibility.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT remove or bypass the _is_excluded_by_dir check; it prevents analysis of virtual environments and build artifacts that should not be traversed**
- **DO NOT change the sorting key from `str(p)` without ensuring output remains deterministic across platforms**
- **DO NOT modify the .resolve() calls in gitignore comparisons; they are necessary for correct path matching with symlinks**
- **DO NOT remove the graceful fallback when repo_root is None; this allows the function to work outside git repositories**
- **ALWAYS preserve the two-branch logic (file vs. directory) to maintain efficiency and clarity**
- **ALWAYS ensure that returned paths are absolute for consistency with downstream consumers**
- **{'ALWAYS maintain the order of operations': 'suffix check → excluded dir check → gitignore check, to fail fast on obvious non-matches'}**
- **{'NOTE': 'This function depends on external git availability; if git is not installed or the target is not in a git repository, gitignore filtering is silently skipped (not an error condition)'}**
- **{'NOTE': 'Performance scales with the number of .py files in the target tree; for very large codebases, gitignore queries may be slow; consider caching results if called repeatedly on the same tree'}**

### Changelog

- 2025-10-31: Clean up docstring formatting

### Raw YAML Block

```yaml
what: |
  Recursively discovers Python files in a target path, respecting .gitignore rules and excluding common non-source directories.

  For file input: validates .py extension and checks if the file is in an excluded directory or gitignored; returns a single-element list containing the file, or an empty list if validation fails.

  For directory input: recursively globs all .py files using rglob("*.py"), filters out files in excluded directories (.venv, __pycache__, .git, build, dist, and similar), then applies .gitignore filtering if a git repository root is found.

  Returns a sorted list of absolute Path objects representing all discovered Python files that pass all filters. Returns an empty list if the target is a non-.py file, is in an excluded directory, or is gitignored.

  Gracefully degrades to unfiltered discovery (still excluding common directories) if no git repository root is found, allowing the function to work outside git repositories.

  Edge cases: symlinks are resolved before gitignore comparison to ensure correct path matching; lazy evaluation of repo_root and ignored set avoids expensive git operations when not needed; sorting by string representation ensures deterministic, human-readable output across different runs and platforms.
deps:
      calls:
        - _find_git_root
        - _git_check_ignore
        - _is_excluded_by_dir
        - files.sort
        - p.is_file
        - p.resolve
        - str
        - target.is_file
        - target.resolve
        - target.rglob
      imports:
        - __future__.annotations
        - os
        - pathlib.Path
        - subprocess
        - typing.Iterable
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  .gitignore integration respects developer intent by excluding files already marked as ignored, reducing noise in analysis and respecting repository conventions.

  Excluded directory filtering prevents wasteful traversal of virtual environments, build artifacts, and cache directories, which would be incorrect to analyze and degrade performance.

  Graceful degradation when git is unavailable or target is not in a repository ensures the function remains useful in non-git contexts.

  Two-path branching (file vs. directory) allows efficient handling of both single-file and bulk discovery scenarios without redundant logic.

  Use of resolved paths in gitignore checks ensures consistent comparison even with symlinks or relative path variations.

  Sorting by string representation of paths ensures deterministic output order across different runs and platforms, critical for reproducibility.

guardrails:
  - DO NOT remove or bypass the _is_excluded_by_dir check; it prevents analysis of virtual environments and build artifacts that should not be traversed
  - DO NOT change the sorting key from `str(p)` without ensuring output remains deterministic across platforms
  - DO NOT modify the .resolve() calls in gitignore comparisons; they are necessary for correct path matching with symlinks
  - DO NOT remove the graceful fallback when repo_root is None; this allows the function to work outside git repositories
  - ALWAYS preserve the two-branch logic (file vs. directory) to maintain efficiency and clarity
  - ALWAYS ensure that returned paths are absolute for consistency with downstream consumers
  - ALWAYS maintain the order of operations: suffix check → excluded dir check → gitignore check, to fail fast on obvious non-matches
  - NOTE: This function depends on external git availability; if git is not installed or the target is not in a git repository, gitignore filtering is silently skipped (not an error condition)
  - NOTE: Performance scales with the number of .py files in the target tree; for very large codebases, gitignore queries may be slow; consider caching results if called repeatedly on the same tree

changelog:

  - "2025-10-31: Clean up docstring formatting"
```

---

## load_env_from_dotenv

**Location:** `agentspec/utils.py:436`

### What This Does

Loads environment variables from a .env file by searching standard locations in order of precedence: explicit env_path parameter, current working directory and its parents, git repository root, and package root directory. Returns the Path to the first .env file found, or None if no file exists.

Parsing behavior: reads file with UTF-8 encoding (ignoring decode errors), splits into lines, strips whitespace, and skips empty lines, comment lines (starting with #), and lines without an = delimiter. Extracts key-value pairs by splitting on first = only, strips surrounding whitespace from both key and value, and removes surrounding quotes (both single and double) from values.

Environment variable assignment respects the override flag: when False (default), only sets variables that do not already exist in os.environ; when True, overwrites existing variables. All exceptions during file access or parsing are silently caught and result in None return value, enabling graceful degradation.

Inputs: optional env_path (Path object or None) to specify explicit file location; override boolean flag (default False) to control whether existing environment variables are overwritten. Outputs: Path object pointing to the loaded .env file, or None if file not found or parsing failed.

Edge cases: handles missing files gracefully, tolerates malformed lines by skipping them, preserves intentional environment overrides when override=False, and continues searching candidates if any candidate file access fails.

### Dependencies

**Calls:**
- `Path`
- `Path.cwd`
- `_find_git_root`
- `c.exists`
- `c.is_file`
- `candidates.append`
- `chosen.read_text`
- `k.strip`
- `line.strip`
- `resolve`
- `s.split`
- `s.startswith`
- `splitlines`
- `strip`
- `v.strip`

### Why This Approach

This approach enables flexible configuration management across development, repository, and package contexts without requiring code changes. The search hierarchy (CWD → parents → git root → package root) accommodates both monorepo and single-package layouts while allowing local overrides to take precedence.

Non-destructive default behavior (override=False) prevents accidental clobbering of intentionally set environment variables, which is critical in environments where variables may be set via shell, CI/CD systems, or parent processes. Silent error handling allows .env files to be optional, supporting both configured and unconfigured deployments without initialization failures.

Quote stripping from values accommodates common .env conventions where values may be quoted for readability or to preserve whitespace, while the flexible parsing (skipping malformed lines) tolerates real-world .env files that may contain comments or incomplete entries.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT raise exceptions on missing files or parse errors; always return None to allow graceful degradation and optional .env configuration**
- **DO NOT modify os.environ when override=False and a key already exists, to preserve intentional environment variable overrides from shell, CI/CD, or parent processes**
- **DO NOT process lines that are empty, start with**
- **DO NOT assume UTF-8 encoding will always succeed; use errors="ignore" to handle mixed or legacy encodings without crashing**
- **DO NOT split on all = characters; split only on the first = to allow = characters in values (e.g., connection strings, base64 data)**

### Changelog

- - 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features

### Raw YAML Block

```yaml
what: |
  Loads environment variables from a .env file by searching standard locations in order of precedence: explicit env_path parameter, current working directory and its parents, git repository root, and package root directory. Returns the Path to the first .env file found, or None if no file exists.

  Parsing behavior: reads file with UTF-8 encoding (ignoring decode errors), splits into lines, strips whitespace, and skips empty lines, comment lines (starting with #), and lines without an = delimiter. Extracts key-value pairs by splitting on first = only, strips surrounding whitespace from both key and value, and removes surrounding quotes (both single and double) from values.

  Environment variable assignment respects the override flag: when False (default), only sets variables that do not already exist in os.environ; when True, overwrites existing variables. All exceptions during file access or parsing are silently caught and result in None return value, enabling graceful degradation.

  Inputs: optional env_path (Path object or None) to specify explicit file location; override boolean flag (default False) to control whether existing environment variables are overwritten. Outputs: Path object pointing to the loaded .env file, or None if file not found or parsing failed.

  Edge cases: handles missing files gracefully, tolerates malformed lines by skipping them, preserves intentional environment overrides when override=False, and continues searching candidates if any candidate file access fails.
deps:
      calls:
        - Path
        - Path.cwd
        - _find_git_root
        - c.exists
        - c.is_file
        - candidates.append
        - chosen.read_text
        - k.strip
        - line.strip
        - resolve
        - s.split
        - s.startswith
        - splitlines
        - strip
        - v.strip
      imports:
        - __future__.annotations
        - os
        - pathlib.Path
        - subprocess
        - typing.Iterable
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  This approach enables flexible configuration management across development, repository, and package contexts without requiring code changes. The search hierarchy (CWD → parents → git root → package root) accommodates both monorepo and single-package layouts while allowing local overrides to take precedence.

  Non-destructive default behavior (override=False) prevents accidental clobbering of intentionally set environment variables, which is critical in environments where variables may be set via shell, CI/CD systems, or parent processes. Silent error handling allows .env files to be optional, supporting both configured and unconfigured deployments without initialization failures.

  Quote stripping from values accommodates common .env conventions where values may be quoted for readability or to preserve whitespace, while the flexible parsing (skipping malformed lines) tolerates real-world .env files that may contain comments or incomplete entries.

guardrails:
  - DO NOT raise exceptions on missing files or parse errors; always return None to allow graceful degradation and optional .env configuration
  - DO NOT modify os.environ when override=False and a key already exists, to preserve intentional environment variable overrides from shell, CI/CD, or parent processes
  - DO NOT process lines that are empty, start with #, or lack an = delimiter, to avoid silent failures on malformed entries and respect comment syntax
  - DO NOT assume UTF-8 encoding will always succeed; use errors="ignore" to handle mixed or legacy encodings without crashing
  - DO NOT split on all = characters; split only on the first = to allow = characters in values (e.g., connection strings, base64 data)

changelog:
      - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features"
```

---

