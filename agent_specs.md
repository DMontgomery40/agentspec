# 🤖 Extracted Agent Specifications

**This document is auto-generated for AI agent consumption.**

---

## FuzzyArgumentParser

**Location:** `/Users/davidmontgomery/agentspec/agentspec/cli.py:17`

### What This Does

Custom ArgumentParser with fuzzy matching for unknown arguments.

### Raw YAML Block

```yaml
Custom ArgumentParser with fuzzy matching for unknown arguments.
```

---

## __init__

**Location:** `/Users/davidmontgomery/agentspec/agentspec/cli.py:20`

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

**Location:** `/Users/davidmontgomery/agentspec/agentspec/cli.py:55`

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

**Location:** `/Users/davidmontgomery/agentspec/agentspec/cli.py:123`

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

**Location:** `/Users/davidmontgomery/agentspec/agentspec/cli.py:267`

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

**Location:** `/Users/davidmontgomery/agentspec/agentspec/cli.py:351`

### What This Does

Renders a formatted help screen to stdout using Rich library with four main sections:
1. Title panel introducing Agentspec as "Structured, enforceable docstrings for AI agents"
2. Commands table listing primary commands (lint, extract, generate, strip) with descriptions
3. Quick-start examples panel showing common usage patterns for each command
4. Key flags reference table documenting important CLI flags grouped by command (--strict for lint, --format for extract, --terse/--update-existing/--diff-summary for generate, --mode for strip)

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
```

---

## _check_python_version

**Location:** `/Users/davidmontgomery/agentspec/agentspec/cli.py:476`

### What This Does

Check Python version meets minimum requirements.

### Raw YAML Block

```yaml
Check Python version meets minimum requirements.
```

---

## main

**Location:** `/Users/davidmontgomery/agentspec/agentspec/cli.py:503`

### What This Does

CLI entry point that parses command-line arguments and dispatches to three subcommands: lint, extract, and generate.

**Lint subcommand**: Validates agentspec docstring blocks in Python files against format and verbosity requirements. Accepts target (file or directory), --min-lines (minimum lines in agentspec blocks, default 10), and --strict flag (treats warnings as errors). Calls lint.run() with parsed arguments.

**Extract subcommand**: Exports agentspec blocks from Python files to portable formats. Accepts target (file or directory) and --format flag (choices: markdown, json, agent-context; default markdown). Calls extract.run() with parsed arguments.

**Generate subcommand**: Auto-generates or refreshes agentspec docstrings using Claude or OpenAI-compatible APIs. Accepts target (file or directory), --dry-run (preview without modifying), --force-context (add print() statements for LLM context), --model (model identifier), --agentspec-yaml (embed YAML block), --provider (auto/anthropic/openai, default auto), --base-url (for OpenAI-compatible endpoints), --update-existing (regenerate existing docstrings), --terse (shorter output), and --diff-summary (add git diff summaries). Lazy-imports generate module to avoid requiring anthropic dependency unless command is used. Calls generate.run() with all parsed arguments.

**Strip subcommand**: Safely removes agentspec-generated YAML or narrative docstrings from Python files. Accepts target (file or directory), --mode (all/yaml/docstrings; default all), and --dry-run to preview removals. Calls strip.run() which performs per-edit compile verification before writing changes.

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
- `strip.run`
- `strip_parser.add_argument`
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

Subcommand pattern isolates lint, extract, generate, and strip logic for independent testing, maintenance, and feature development without tight coupling. Rich-based help formatter improves CLI UX for both end users and agent consumption. Lazy import of generate module avoids requiring anthropic dependency unless generate command is explicitly invoked, reducing installation friction for users who only need lint/extract. Early exit on missing command prevents ambiguous behavior and ensures explicit user feedback via help text. Explicit if/elif dispatch chain is more readable and debuggable than dict-based dispatch at this scale; easier for agents to trace execution flow. Default values (--min-lines=10, --format=markdown, --model=claude-haiku-4-5) provide sensible out-of-the-box behavior for common workflows. sys.exit() calls ensure process terminates cleanly; Python does not auto-exit from main(). Strip command centralizes docstring removal tooling that previously required separate scripts, keeping lifecycle operations in a single CLI entry point.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT modify the if/elif dispatch logic without updating corresponding submodule signatures in lint.py, extract.py, and generate.py**
- **DO NOT remove sys.exit() calls; they are required for proper CLI exit behavior and process termination**
- **DO NOT add new subcommands without documenting them in this docstring's WHAT section and updating help text**
- **DO NOT rename strip --mode choices without updating agentspec.strip guardrails and tests**
- **DO NOT change argument parameter names (e.g., target, format, model, provider, base_url) as they are consumed by downstream modules via args object attributes**
- **DO NOT remove or rename --dry-run and --force-context flags for generate; these are critical safety mechanisms**
- **ALWAYS preserve help text on all CLI flags for end-user clarity and discoverability**
- **ALWAYS validate that new CLI flags have sensible defaults to avoid breaking existing automation scripts and CI/CD pipelines**
- **ALWAYS ensure subcommand descriptions include common workflows and examples in epilog for agent/user guidance**
- **ALWAYS lazy-import optional dependencies (like generate module) to avoid requiring them unless explicitly needed**
- **ALWAYS call load_env_from_dotenv() at entry point to allow users to configure via .env without manual export**

### Changelog

- 2025-10-31: Clean up docstring formatting
- 2025-10-31: Add strip subcommand wiring and documentation

### Raw YAML Block

```yaml
what: |
  CLI entry point that parses command-line arguments and dispatches to three subcommands: lint, extract, and generate.

  **Lint subcommand**: Validates agentspec docstring blocks in Python files against format and verbosity requirements. Accepts target (file or directory), --min-lines (minimum lines in agentspec blocks, default 10), and --strict flag (treats warnings as errors). Calls lint.run() with parsed arguments.

  **Extract subcommand**: Exports agentspec blocks from Python files to portable formats. Accepts target (file or directory) and --format flag (choices: markdown, json, agent-context; default markdown). Calls extract.run() with parsed arguments.

  **Generate subcommand**: Auto-generates or refreshes agentspec docstrings using Claude or OpenAI-compatible APIs. Accepts target (file or directory), --dry-run (preview without modifying), --force-context (add print() statements for LLM context), --model (model identifier), --agentspec-yaml (embed YAML block), --provider (auto/anthropic/openai, default auto), --base-url (for OpenAI-compatible endpoints), --update-existing (regenerate existing docstrings), --terse (shorter output), and --diff-summary (add git diff summaries). Lazy-imports generate module to avoid requiring anthropic dependency unless command is used. Calls generate.run() with all parsed arguments.

  **Strip subcommand**: Safely removes agentspec-generated YAML or narrative docstrings from Python files. Accepts target (file or directory), --mode (all/yaml/docstrings; default all), and --dry-run to preview removals. Calls strip.run() which performs per-edit compile verification before writing changes.

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
        - strip.run
        - strip_parser.add_argument
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
  Subcommand pattern isolates lint, extract, generate, and strip logic for independent testing, maintenance, and feature development without tight coupling. Rich-based help formatter improves CLI UX for both end users and agent consumption. Lazy import of generate module avoids requiring anthropic dependency unless generate command is explicitly invoked, reducing installation friction for users who only need lint/extract. Early exit on missing command prevents ambiguous behavior and ensures explicit user feedback via help text. Explicit if/elif dispatch chain is more readable and debuggable than dict-based dispatch at this scale; easier for agents to trace execution flow. Default values (--min-lines=10, --format=markdown, --model=claude-haiku-4-5) provide sensible out-of-the-box behavior for common workflows. sys.exit() calls ensure process terminates cleanly; Python does not auto-exit from main(). Strip command centralizes docstring removal tooling that previously required separate scripts, keeping lifecycle operations in a single CLI entry point.

guardrails:
  - DO NOT modify the if/elif dispatch logic without updating corresponding submodule signatures in lint.py, extract.py, and generate.py
  - DO NOT remove sys.exit() calls; they are required for proper CLI exit behavior and process termination
  - DO NOT add new subcommands without documenting them in this docstring's WHAT section and updating help text
  - DO NOT rename strip --mode choices without updating agentspec.strip guardrails and tests
  - DO NOT change argument parameter names (e.g., target, format, model, provider, base_url) as they are consumed by downstream modules via args object attributes
  - DO NOT remove or rename --dry-run and --force-context flags for generate; these are critical safety mechanisms
  - ALWAYS preserve help text on all CLI flags for end-user clarity and discoverability
  - ALWAYS validate that new CLI flags have sensible defaults to avoid breaking existing automation scripts and CI/CD pipelines
  - ALWAYS ensure subcommand descriptions include common workflows and examples in epilog for agent/user guidance
  - ALWAYS lazy-import optional dependencies (like generate module) to avoid requiring them unless explicitly needed
  - ALWAYS call load_env_from_dotenv() at entry point to allow users to configure via .env without manual export

changelog:

  - "2025-10-31: Clean up docstring formatting"
  - "2025-10-31: Add strip subcommand wiring and documentation"
```

---

## _normalize_metadata_list

**Location:** `/Users/davidmontgomery/agentspec/agentspec/collect.py:59`

### What This Does

Normalize metadata values to a sorted list of unique strings.

### Raw YAML Block

```yaml
Normalize metadata values to a sorted list of unique strings.
```

---

## _collect_python_deps

**Location:** `/Users/davidmontgomery/agentspec/agentspec/collect.py:72`

### What This Does

Collect call/import metadata for Python files using AST helpers.

### Raw YAML Block

```yaml
Collect call/import metadata for Python files using AST helpers.
```

---

## _collect_git_changelog

**Location:** `/Users/davidmontgomery/agentspec/agentspec/collect.py:94`

### What This Does

Collect deterministic git changelog entries for a function.

### Raw YAML Block

```yaml
Collect deterministic git changelog entries for a function.

Falls back to file-level history if function-level tracking fails
(common for JavaScript files using IIFEs where functions are nested).
```

---

## _collect_javascript_metadata

**Location:** `/Users/davidmontgomery/agentspec/agentspec/collect.py:164`

### What This Does

Collect call/import metadata for JavaScript files via language adapter.

### Raw YAML Block

```yaml
Collect call/import metadata for JavaScript files via language adapter.
```

---

## _extract_block

**Location:** `/Users/davidmontgomery/agentspec/agentspec/extract.py:36`

### What This Does

Extracts the agentspec metadata block from a Python docstring by locating content between "---agentspec" and "

### Raw YAML Block

```yaml
what: |
  Extracts the agentspec metadata block from a Python docstring by locating content between "---agentspec" and "
```

---

## _parse_yaml_block

**Location:** `/Users/davidmontgomery/agentspec/agentspec/extract.py:102`

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

**Location:** `/Users/davidmontgomery/agentspec/agentspec/extract.py:151`

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

**Location:** `/Users/davidmontgomery/agentspec/agentspec/extract.py:210`

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

**Location:** `/Users/davidmontgomery/agentspec/agentspec/extract.py:269`

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

**Location:** `/Users/davidmontgomery/agentspec/agentspec/extract.py:329`

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

**Location:** `/Users/davidmontgomery/agentspec/agentspec/extract.py:383`

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

**Location:** `/Users/davidmontgomery/agentspec/agentspec/extract.py:487`

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

## _strip_jsdoc_stars

**Location:** `/Users/davidmontgomery/agentspec/agentspec/extract.py:561`

### Raw YAML Block

```yaml
what: |
      Normalizes a JSDoc block by removing comment delimiters and leading '*' prefixes from each line.

      Accepts a raw text block that may include '/**', '*/', and lines starting with '*'. Returns the
      cleaned content preserving internal newlines but without JSDoc decoration, suitable for scanning
      for agentspec markers and YAML parsing.

    deps:
      calls:
        - str.splitlines
        - str.strip
        - list.append
        - '
'.join
    why: |
      YAML markers live inside JSDoc; removing decoration yields a clean string for delimiter search using
      the existing `_extract_block` function without duplicating logic.
    guardrails:
      - DO NOT attempt to parse YAML here; return only normalized text
      - ALWAYS preserve relative line order and blank lines
    changelog:
      - "2025-11-01: Initial implementation for JS/TS agentspec extraction"
```

---

## extract_from_js_file

**Location:** `/Users/davidmontgomery/agentspec/agentspec/extract.py:601`

### What This Does

Extracts AgentSpec definitions from JavaScript/TypeScript source by scanning JSDoc blocks for
'---agentspec'/'

### Raw YAML Block

```yaml
what: |
  Extracts AgentSpec definitions from JavaScript/TypeScript source by scanning JSDoc blocks for
  '---agentspec'/'
```

---

## export_markdown

**Location:** `/Users/davidmontgomery/agentspec/agentspec/extract.py:706`

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

**Location:** `/Users/davidmontgomery/agentspec/agentspec/extract.py:826`

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

**Location:** `/Users/davidmontgomery/agentspec/agentspec/extract.py:894`

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

**Location:** `/Users/davidmontgomery/agentspec/agentspec/extract.py:971`

### What This Does

Extracts agent specification blocks from Python and JavaScript/TypeScript files in a target directory and exports them in the specified format.

Behavior:
- Accepts a target path (file or directory) and optional format string (markdown, json, or agent-context)
- Collects source files using collect_source_files (Python via collect_python_files, JS/TS via language adapters)
- Iterates through collected files and extracts AgentSpec objects from embedded YAML blocks and docstrings using extract_from_file (Python) and extract_from_js_file (JS/TS)
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
- 2025-11-01: Add JS/TS extraction via collect_source_files and extract_from_js_file

### Raw YAML Block

```yaml
what: |
  Extracts agent specification blocks from Python and JavaScript/TypeScript files in a target directory and exports them in the specified format.

  Behavior:
  - Accepts a target path (file or directory) and optional format string (markdown, json, or agent-context)
  - Collects source files using collect_source_files (Python via collect_python_files, JS/TS via language adapters)
  - Iterates through collected files and extracts AgentSpec objects from embedded YAML blocks and docstrings using extract_from_file (Python) and extract_from_js_file (JS/TS)
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
        - agentspec.utils.collect_source_files
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
  - "2025-11-01: Add JS/TS extraction via collect_source_files and extract_from_js_file"
```

---

## _get_client

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:17`

### Raw YAML Block

```yaml
what: |
  Initializes and returns a singleton Anthropic client instance. The function performs environment setup by loading variables from a .env file (if present) to ensure ANTHROPIC_API_KEY is available in the environment, then lazily imports the Anthropic class and instantiates it. The Anthropic constructor automatically reads the ANTHROPIC_API_KEY from environment variables. Returns an Anthropic client object ready for API calls.

  Inputs: None
  Outputs: anthropic.Anthropic instance configured with credentials from environment

  Edge cases:
  - If ANTHROPIC_API_KEY is not set in environment or .env file, Anthropic() will raise an authentication error
  - If .env file does not exist, load_env_from_dotenv() handles gracefully without raising
  - Lazy import means anthropic package must be installed; ImportError raised if missing
    deps:
      calls:
        - Anthropic
        - load_env_from_dotenv
      imports:
        - agentspec.collect.collect_metadata
        - agentspec.utils.collect_source_files
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
  Lazy importing the Anthropic class defers the dependency load until the client is actually needed, reducing startup time for code paths that don't use the API. Loading .env first ensures credentials are available before instantiation, supporting both explicit environment variables and .env file-based configuration. This pattern centralizes client creation logic, making it easier to manage authentication and swap implementations if needed.

guardrails:
  - DO NOT call this function multiple times in tight loops; consider caching the result since creating new client instances is unnecessary overhead
  - DO NOT assume ANTHROPIC_API_KEY is set; always handle potential authentication errors from Anthropic() constructor
  - DO NOT modify this function to hardcode API keys; rely exclusively on environment variables for security
  - DO NOT remove the load_env_from_dotenv() call; it is essential for .env file support in development environments

    changelog:
      - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
      - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
      - "- 2025-10-30: feat: robust docstring generation and Haiku defaults (e428337)"
      - "- 2025-10-29: Add auto-generator for verbose agentspec docstrings using Claude API (7baa9a8)"
```

---

## extract_function_info

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:187`

### Raw YAML Block

```yaml
what: |
  Extracts function definitions from a Python source file and returns metadata for functions requiring documentation. Parses the AST to identify all function and async function definitions, evaluates whether each needs an agentspec docstring based on three modes: (1) require_agentspec=True checks for missing docstrings or absence of "---agentspec" marker, (2) require_agentspec=False checks for missing or undersized docstrings (< 5 lines), (3) update_existing=True forces processing of all functions regardless of existing documentation. Returns a list of tuples containing line number, function name, and extracted source code. Results are sorted in descending line order to enable safe top-down insertion of docstrings without invalidating subsequent line numbers.
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
        - agentspec.utils.collect_source_files
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
  Reverse sorting by line number prevents line number drift during batch docstring insertion—when docstrings are added to functions, earlier insertions would shift line numbers of functions below them. Processing bottom-to-top preserves the validity of cached line numbers. The dual-mode checking (agentspec-specific vs. general docstring quality) allows flexible workflows: strict mode enforces agentspec compliance, while lenient mode targets underdocumented functions. The update_existing flag enables regeneration of existing documentation without re-parsing, supporting iterative refinement workflows.

guardrails:
  - DO NOT rely on line numbers after insertion without re-parsing, as the returned list is only valid for the original source state.
  - DO NOT use this function on files with syntax errors; ast.parse() will raise SyntaxError and halt processing.
  - DO NOT assume docstring presence correlates with quality; require_agentspec=False may skip functions with minimal or placeholder docstrings.
  - DO NOT process extremely large files without memory consideration; ast.walk() traverses the entire tree and source is held in memory.
  - DO NOT mix update_existing=True with require_agentspec=True in the same call; update_existing bypasses all skip logic, making require_agentspec ineffective.

    changelog:
      - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
      - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
      - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate (172e0a7)"
      - "- 2025-10-29: CRITICAL FIX: Process functions bottom-to-top to prevent line number invalidation and syntax errors (bab4295)"
```

---

## inject_deterministic_metadata

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:269`

### What This Does

Injects deterministic metadata (dependencies and changelog) into LLM-generated documentation output. Accepts an LLM output string, a metadata dictionary containing 'deps' (with 'calls' and 'imports' keys) and 'changelog' (list of git history entries), and a format flag. When as_agentspec_yaml is True, formats metadata as YAML and injects it into an agentspec block by locating the "why:" section and inserting deps before it, then forcefully replaces any existing changelog section with deterministic data before the closing "

### Raw YAML Block

```yaml
what: |
  Injects deterministic metadata (dependencies and changelog) into LLM-generated documentation output. Accepts an LLM output string, a metadata dictionary containing 'deps' (with 'calls' and 'imports' keys) and 'changelog' (list of git history entries), and a format flag. When as_agentspec_yaml is True, formats metadata as YAML and injects it into an agentspec block by locating the "why:" section and inserting deps before it, then forcefully replaces any existing changelog section with deterministic data before the closing "
```

---

## strip_js_agentspec_blocks

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:434`

### What This Does

Scans a JavaScript/TypeScript file and removes JSDoc comment blocks (/** ... */) that contain agentspec-related markers or metadata. The function identifies candidate blocks by searching for specific keywords: "---agentspec", "

### Raw YAML Block

```yaml
what: |
  Scans a JavaScript/TypeScript file and removes JSDoc comment blocks (/** ... */) that contain agentspec-related markers or metadata. The function identifies candidate blocks by searching for specific keywords: "---agentspec", "
```

---

## is_agentspec_block

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:494`

### What This Does

Detects whether a list of text lines constitutes an agentspec block by checking for the presence of any marker strings that indicate agentspec content. The function joins the input lines into a single string and searches for five specific markers: the opening fence "---agentspec", the closing fence "

### Raw YAML Block

```yaml
what: |
  Detects whether a list of text lines constitutes an agentspec block by checking for the presence of any marker strings that indicate agentspec content. The function joins the input lines into a single string and searches for five specific markers: the opening fence "---agentspec", the closing fence "
```

---

## generate_docstring

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:578`

### What This Does

Generates narrative-only docstrings (or agentspec YAML) for a function. Implements continuation for
long YAML by detecting incomplete fences/sections and issuing follow-up calls (max 2). Provides
per-call token budgeting with environment overrides and emits per-function proof logs. Honors
AGENTSPEC_GENERATE_STUB=1 to force deterministic narrative for testing (no provider calls).

### ⚠️ Guardrails (CRITICAL)

- **DO NOT include deps/changelog here; injected in a separate phase**
- **ALWAYS produce YAML-only output when as_agentspec_yaml=True (no prose outside fences)**
- **ALWAYS validate YAML fences and required sections; continue generation if incomplete**

### Changelog

- 2025-11-01: Add continuation + token budgeting + proof logs + stub toggle

### Raw YAML Block

```yaml
what: |
  Generates narrative-only docstrings (or agentspec YAML) for a function. Implements continuation for
  long YAML by detecting incomplete fences/sections and issuing follow-up calls (max 2). Provides
  per-call token budgeting with environment overrides and emits per-function proof logs. Honors
  AGENTSPEC_GENERATE_STUB=1 to force deterministic narrative for testing (no provider calls).

guardrails:
  - DO NOT include deps/changelog here; injected in a separate phase
  - ALWAYS produce YAML-only output when as_agentspec_yaml=True (no prose outside fences)
  - ALWAYS validate YAML fences and required sections; continue generation if incomplete
changelog:
  - "2025-11-01: Add continuation + token budgeting + proof logs + stub toggle"
```

---

## insert_docstring_at_line

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:756`

### Raw YAML Block

```yaml
what: |
  Inserts or replaces a docstring for a specified function in a Python file at a given line number.

  **Inputs:**
  - `filepath`: Path object pointing to the target Python file
  - `lineno`: Approximate line number where the function is defined (1-based)
  - `func_name`: Name of the function to document
  - `docstring`: The docstring content to insert (plain text, without delimiters)
  - `force_context`: Boolean flag to append a context print statement after the docstring

  **Outputs:**
  - Returns `True` if insertion succeeded and file was written; `False` if syntax validation failed

  **Behavior:**
  1. Reads the entire file into memory as a list of lines
  2. Locates the function definition using regex pattern matching on `func_name`, falling back to the provided `lineno` if not found
  3. Uses AST parsing to robustly identify the function node and its first statement, handling multi-line signatures, annotations, and decorators
  4. Detects and removes any existing docstring (Expr node containing a Constant or Str value) using AST line number metadata
  5. Also removes any trailing `[AGENTSPEC_CONTEXT]` print statement if present
  6. Determines appropriate indentation from the function definition line
  7. Selects delimiter (`"""` or `'''`) based on content, preferring triple-double unless it appears in the docstring and triple-single does not
  8. Escapes conflicting delimiters within the docstring content
  9. Formats the new docstring with proper indentation and line breaks
  10. If `force_context=True`, extracts up to 3 bullet points (lines starting with `-`) and appends a print statement with escaped content
  11. Performs a compile-test on a temporary file to validate syntax before writing
  12. Writes the modified file only if compilation succeeds

  **Edge cases:**
  - Multi-line function signatures: AST parsing handles these robustly
  - Existing docstrings: Detected and deleted using AST node boundaries (1-based to 0-based index conversion)
  - Docstring content containing delimiters: Escaped or delimiter switched to avoid breakage
  - AST parsing failure: Falls back to textual scanning using parenthesis depth tracking and colon detection
  - Syntax errors in candidate: Rejected with warning; original file left untouched
  - Empty or missing function body: Inserts after function definition line
    deps:
      calls:
        - abs
        - ast.parse
        - ast.walk
        - candidate.insert
        - candidates.append
        - docstring.split
        - enumerate
        - f.readlines
        - f.writelines
        - func_line.lstrip
        - hasattr
        - isinstance
        - join
        - len
        - line.count
        - line.startswith
        - line.strip
        - list
        - max
        - min
        - new_lines.append
        - open
        - os.close
        - os.remove
        - path.exists
        - pattern.match
        - print
        - print_content.replace
        - py_compile.compile
        - re.compile
        - re.escape
        - replace
        - reversed
        - safe_doc.replace
        - safe_doc.split
        - sections.append
        - strip
        - tempfile.mkstemp
        - tf.writelines
      imports:
        - agentspec.collect.collect_metadata
        - agentspec.utils.collect_python_files
        - agentspec.utils.collect_source_files
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
  AST-based approach provides robustness against complex Python syntax (decorators, type hints, multi-line signatures) that regex or simple textual scanning cannot reliably handle. The 1-based to 0-based index conversion is critical because Python's `ast` module reports line numbers as 1-based (matching editor conventions) while Python lists are 0-indexed.

  Compile-testing before write prevents leaving the file in a broken state due to escaping errors or malformed docstring formatting. Fallback to textual scanning ensures graceful degradation if AST parsing encounters unsupported syntax or edge cases.

  Delimiter selection logic avoids breaking docstrings that contain triple quotes. Context print extraction and escaping supports downstream tooling that parses `[AGENTSPEC_CONTEXT]` markers while preventing quote/backslash injection attacks.

guardrails:
  - DO NOT assume AST line numbers are 0-based; they are always 1-based per Python spec. Failure to convert causes off-by-one deletion of wrong lines.
  - DO NOT write to the file without first validating syntax via `py_compile`; this prevents corrupting the source file if docstring formatting is malformed.
  - DO NOT skip escaping triple quotes in docstring content; unescaped delimiters will break the syntax of the inserted docstring.
  - DO NOT assume the function definition is always on a single line; use AST to find the actual first statement in the function body, not just `lineno + 1`.
  - DO NOT leave temporary files behind; always clean up in a `finally` block to avoid disk space leaks.
  - DO NOT assume existing docstrings are always single-line; use AST `end_lineno` to correctly identify multi-line docstring boundaries.

    changelog:
      - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
      - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
      - "- 2025-10-30: feat: robust docstring generation and Haiku defaults (e428337)"
      - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate (172e0a7)"
```

---

## _discover_js_functions

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:1083`

### Raw YAML Block

```yaml
what: |
  Discovers JavaScript functions in a file that require agentspec documentation.

  Scans a JavaScript file line-by-line to identify function declarations (both traditional `function name()` and arrow function assignments `const name = () =>`), including those with `export` modifiers. For each discovered function, examines up to 20 lines above to detect existing JSDoc blocks and checks for the presence of an agentspec marker (`---agentspec`).

  Returns a list of tuples containing (line_number, function_name, code_snippet) sorted in reverse line order. Each tuple represents a function candidate that either lacks documentation entirely, lacks an agentspec block when required, or is flagged for update. The code snippet captures the function declaration plus approximately 8 subsequent lines for context.

  Handles file read errors gracefully by returning an empty list. Regex patterns match standard JavaScript function naming conventions (alphanumeric, underscore, dollar sign).

  Input parameters control filtering behavior: `require_agentspec=True` identifies functions with JSDoc but missing agentspec markers; `update_existing=True` includes all discovered functions regardless of documentation state.
    deps:
      calls:
        - arrow_pat.match
        - candidates.append
        - candidates.sort
        - enumerate
        - filepath.read_text
        - func_pat.match
        - has_jsdoc
        - join
        - len
        - m1.group
        - m2.group
        - max
        - min
        - range
        - re.compile
        - s.endswith
        - strip
        - text.splitlines
      imports:
        - agentspec.collect.collect_metadata
        - agentspec.utils.collect_python_files
        - agentspec.utils.collect_source_files
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
  This discovery mechanism enables automated or semi-automated generation of agentspec documentation blocks for JavaScript codebases. By identifying undocumented or partially documented functions, it supports tooling that can prompt developers or generate templates for specification. Reverse sorting by line number allows downstream processors to insert documentation without invalidating earlier line references. The configurable filtering logic accommodates different workflows: initial documentation generation, targeted agentspec addition to existing JSDoc, or bulk updates.

guardrails:
  - DO NOT assume file encoding beyond UTF-8 with error ignoring; malformed files should fail silently and return empty results to prevent pipeline breakage.
  - DO NOT match function names in comments or strings; regex patterns are line-anchored to reduce false positives, but multi-line string literals or commented-out code may still be detected.
  - DO NOT look beyond 20 lines above for JSDoc markers; this bounds search cost and assumes JSDoc is reasonably proximate to function declarations.
  - DO NOT include functions that already have complete agentspec documentation when `update_existing=False` and `require_agentspec=False`; this prevents redundant processing.
  - DO NOT return candidates in original line order; reverse sorting is essential to prevent line number shifts when inserting documentation blocks sequentially.

    changelog:
      - "- no git history available"
```

---

## has_jsdoc

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:1159`

### Raw YAML Block

```yaml
what: |
  Scans up to 20 lines above a given line index to detect JSDoc comment blocks and identify whether they contain an agentspec marker. Returns a tuple of two booleans: (has_any_jsdoc, has_agentspec_marker). The function searches backward from the target line, looking for the closing */ of a JSDoc block, then locates the opening /** to determine if the complete block contains the "---agentspec" marker string. If no JSDoc block is found within the 20-line window, returns (False, False). If a JSDoc block is found but lacks the marker, returns (True, False). If both are present, returns (True, True).
    deps:
      calls:
        - join
        - max
        - range
        - s.endswith
        - strip
      imports:
        - agentspec.collect.collect_metadata
        - agentspec.utils.collect_python_files
        - agentspec.utils.collect_source_files
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
  This function enables detection of pre-existing agentspec documentation blocks in JavaScript/TypeScript source files, supporting incremental documentation workflows where some functions may already be documented. The 20-line lookback window balances thoroughness against performance, capturing typical comment blocks while avoiding excessive backward scanning. The two-part return tuple allows callers to distinguish between "no JSDoc found" and "JSDoc found but no agentspec marker," enabling different handling strategies (e.g., skip vs. update).
guardrails:
  - DO NOT assume lines are already stripped; the function explicitly calls .strip() to handle leading/trailing whitespace robustly.
  - DO NOT search beyond 20 lines backward; this prevents performance degradation on large files and focuses on proximate documentation.
  - DO NOT return True for has_any_jsdoc if only */ is found without a corresponding /**; the function requires both markers to confirm a valid JSDoc block.
  - DO NOT treat "---agentspec" as case-sensitive; the marker check uses exact string matching, so variations in casing will not be detected.

    changelog:
      - "- no git history available"
```

---

## process_js_file

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:1237`

### What This Does

Processes a JavaScript file to discover functions and generate embedded agentspec documentation.

Behavior additions:
- When update_existing=True, pre-cleans existing agentspec JSDoc blocks (YAML or narrative) to prevent duplicates.

### Raw YAML Block

```yaml
what: |
  Processes a JavaScript file to discover functions and generate embedded agentspec documentation.

  Behavior additions:
  - When update_existing=True, pre-cleans existing agentspec JSDoc blocks (YAML or narrative) to prevent duplicates.
```

---

## process_file

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:1326`

### Raw YAML Block

```yaml
what: |
  Orchestrates end-to-end docstring generation for a single Python file by extracting all functions requiring documentation, generating AI-powered narratives via LLM, collecting deterministic metadata (deps, imports, changelog) separately, and applying both through a two-phase insertion process with compile-safety verification.

  **Inputs:**
  - filepath (Path): Target Python file to process
  - dry_run (bool): Preview mode; prints plan without writing changes
  - force_context (bool): Injects print() statements for agent observability
  - model (str): LLM model identifier (default: "claude-haiku-4-5")
  - as_agentspec_yaml (bool): Generate structured agentspec YAML instead of traditional docstrings
  - base_url (str | None): Custom LLM provider endpoint
  - provider (str | None): LLM provider selection ('auto' for automatic detection)
  - update_existing (bool): Force regeneration of existing docstrings
  - terse (bool): Generate concise documentation
  - diff_summary (bool): Include diff summaries in changelog

  **Processing Flow:**
  1. Extracts all functions lacking verbose docstrings or marked for update via extract_function_info
  2. Returns early if no functions need processing or if dry_run=True after printing the plan
  3. Sorts functions in reverse line-number order (bottom-to-top) to prevent line-shift invalidation during insertion
  4. For each function: generates LLM narrative, collects deterministic metadata independently, applies both via compile-safe insertion
  5. Handles syntax errors gracefully by catching and reporting without crashing
  6. Prints detailed progress including function names, line numbers, model selection, and success/failure status

  **Outputs:**
  - None (side effects: modified filepath with inserted docstrings, console output with progress)
  - Early returns on: syntax errors, no functions found, dry_run=True
  - Graceful degradation: metadata collection failures do not block docstring insertion

  **Edge Cases:**
  - Syntax errors in target file are caught and reported; processing halts without exception
  - Metadata collection failures (missing markers, import errors, format issues) fall back to empty dict
  - Compile-safety verification may skip insertion if docstring would break syntax; reported as warning
  - Multiple LLM providers/models with configurable endpoints; invalid model/provider combinations fail at LLM call time
  - Bottom-to-top processing ensures line numbers remain valid throughout loop without recalculation
    deps:
      calls:
        - apply_docstring_with_metadata
        - collect_metadata
        - extract_function_info
        - functions.sort
        - generate_docstring
        - len
        - print
        - str
      imports:
        - agentspec.collect.collect_metadata
        - agentspec.utils.collect_python_files
        - agentspec.utils.collect_source_files
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
  **Bottom-to-top processing (reverse sort by line number)** is essential because inserting docstrings shifts all subsequent line numbers downward; processing in reverse order ensures line numbers remain valid throughout the loop without recalculation. Ascending order would cause line-number invalidation and insertion failures.

  **Two-phase generation (narrative from LLM, metadata collected separately)** maintains clean separation of concerns: the LLM generates human-readable documentation without knowledge of internal implementation details (deps, imports, changelog), while deterministic metadata is collected from the codebase independently and merged only at insertion time. This prevents LLM hallucination of technical details and keeps the LLM focused on narrative quality.

  **Metadata collection wrapped in try-except with fallback to empty dict** ensures metadata extraction failures (missing agentspec markers, import errors, file format issues) never block docstring insertion. Graceful degradation allows partial success rather than total failure.

  **Compile-safety verification via apply_docstring_with_metadata** prevents insertion of syntactically invalid docstrings that would break the file. The function returns a boolean indicating success, allowing the caller to report skips without raising exceptions.

  **Dry-run mode** allows users to preview which functions will be processed and with which model before committing any changes, reducing risk of unintended modifications.

  **Support for as_agentspec_yaml flag** enables generation of structured agent specifications instead of traditional docstrings, allowing the same pipeline to serve different documentation formats without code duplication.

  **Early return conditions** (no functions found, dry_run=True) are intentional gates that prevent unnecessary LLM calls or file writes, improving efficiency and reducing API costs.

guardrails:
  - DO NOT modify the bottom-to-top sort order (reverse=True on line number); changing to ascending order will cause line-number invalidation and docstring insertion failures
  - DO NOT remove the try-except wrapper around collect_metadata or the fallback to empty dict; metadata collection failures must not block docstring generation
  - DO NOT pass metadata to generate_docstring; the LLM must only receive code and filepath, never implementation details like deps or changelog
  - DO NOT skip the compile-safety check via apply_docstring_with_metadata; always use this function for insertion rather than direct file manipulation
  - DO NOT attempt to process files with syntax errors; catch SyntaxError from extract_function_info and return early without attempting further processing
  - DO NOT pass string paths to extract_function_info or apply_docstring_with_metadata; filepath must be a Path object for compatibility
  - DO NOT assume model/provider combinations are valid; invalid selections will fail at LLM call time with authentication/availability errors
  - ALWAYS preserve the two-phase generation pattern: narrative first (LLM), then metadata insertion (deterministic)
  - ALWAYS call extract_function_info with require_agentspec and update_existing parameters matching the function's own flags
  - ALWAYS print progress messages at key stages (extraction, generation start, success/failure) for agent observability and user feedback

    changelog:
      - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
      - "- 2025-10-30: refactor(injection): move deps/changelog injection out of LLM path via safe two‑phase writer (219a717)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
      - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
      - "- 2025-10-30: feat: robust docstring generation and Haiku defaults (e428337)"
```

---

## run

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:1480`

### What This Does

Orchestrates generation across Python and JS/TS with per-run metrics and proof logs.

Behavior:
- Loads .env and resolves provider/base_url
- Discovers files via collect_source_files and filters by --language
- Clears per-run token metrics before processing, prints summary afterward
- Delegates per-file processing (process_file for Python, process_js_file for JS/TS)

### ⚠️ Guardrails (CRITICAL)

- **DO NOT perform file edits in dry_run**
- **ALWAYS handle invalid target path**
- **ALWAYS print per-run metrics summary when any functions were processed**

### Changelog

- 2025-11-01: Add per-run metrics summary

### Raw YAML Block

```yaml
what: |
  Orchestrates generation across Python and JS/TS with per-run metrics and proof logs.

  Behavior:
  - Loads .env and resolves provider/base_url
  - Discovers files via collect_source_files and filters by --language
  - Clears per-run token metrics before processing, prints summary afterward
  - Delegates per-file processing (process_file for Python, process_js_file for JS/TS)

guardrails:
  - DO NOT perform file edits in dry_run
  - ALWAYS handle invalid target path
  - ALWAYS print per-run metrics summary when any functions were processed
changelog:
  - "2025-11-01: Add per-run metrics summary"
```

---

## main

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:1606`

### What This Does

Entry point for the documentation generation CLI that parses command-line arguments and delegates processing to the core run() function.

Parses the following arguments:
- Positional argument (required): file or directory path to process
- --dry-run flag (optional): boolean presence check; enables preview mode without file modifications
- --force-context flag (optional): boolean presence check; injects print() statements to force LLM context loading
- --model flag (optional): accepts a model name string; defaults to "claude-haiku-4-5" if not specified

Validates that at least one positional argument is provided; prints usage instructions and exits with code 1 if missing. Extracts the model name by locating the --model flag in sys.argv and reading the next argument if present; silently retains default if --model is the final argument or missing.

Delegates actual processing to run() with parameters: path, language="auto", dry_run boolean, force_context boolean, and model string. Propagates the exit code returned by run() back to the system via sys.exit(), allowing callers to detect success (0) or failure (non-zero).

Supported model options documented in usage string: claude-haiku-4-5 (default), claude-3-5-sonnet-20241022, claude-3-5-haiku-20241022. Requires ANTHROPIC_API_KEY environment variable to be set before execution.
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
      - agentspec.utils.collect_source_files
      - agentspec.utils.load_env_from_dotenv
      - ast
      - json
      - os
      - pathlib.Path
      - re
      - sys
      - typing.Any
      - typing.Dict

### Why This Approach

Manual argument parsing (rather than argparse) minimizes dependencies and suits a small CLI with few options, allowing simple inline flag detection without external libraries.

Default model is claude-haiku-4-5 (cost-effective) to balance performance and API costs for typical documentation generation tasks. The --model flag is positioned after the path argument to maintain intuitive CLI ordering (target first, then options).

Dry-run and force-context flags use simple boolean presence checks (no values required) to reduce parsing complexity and improve usability. Early validation and usage printing ensures users understand environment requirements before attempting to run.

Delegating to run() keeps main() thin and testable, separating CLI concerns from business logic. Propagating exit codes unchanged preserves the caller's ability to detect success/failure in shell scripts and automation.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT modify the sys.exit(1) call for missing arguments; it ensures proper shell exit codes for scripting and automation**
- **DO NOT change the default model without updating documentation and considering API cost implications for end users**
- **DO NOT add new positional arguments without updating the usage string to remain synchronized**
- **DO NOT remove or rename the --dry-run, --force-context, or --model flags; they are part of the public CLI contract**
- **DO NOT alter the usage string without ensuring it accurately reflects all supported flags and options**
- **DO NOT suppress or modify the exit code from run(); callers depend on it to detect success/failure**
- **ALWAYS ensure the usage string remains synchronized with actual supported flags and their descriptions**
- **ALWAYS preserve exact flag names as they are part of the public CLI contract**
- **{'NOTE': 'sys.argv indexing assumes well-formed input; if --model is the last argument with no value following it, model silently remains at default (this is safe but may confuse users)'}**
- **{'NOTE': 'The model parameter is passed as a string directly to run(); ensure run() validates or handles unknown model names gracefully to provide clear error messages', 'changelog': ['- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)', '- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)', '- 2025-10-30: feat: robust docstring generation and Haiku defaults (e428337)', '- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate (172e0a7)', '- 2025-10-29: CRITICAL FIX: Process functions bottom-to-top to prevent line number invalidation and syntax errors (bab4295)']}**

### Raw YAML Block

```yaml
what: |
  Entry point for the documentation generation CLI that parses command-line arguments and delegates processing to the core run() function.

  Parses the following arguments:
  - Positional argument (required): file or directory path to process
  - --dry-run flag (optional): boolean presence check; enables preview mode without file modifications
  - --force-context flag (optional): boolean presence check; injects print() statements to force LLM context loading
  - --model flag (optional): accepts a model name string; defaults to "claude-haiku-4-5" if not specified

  Validates that at least one positional argument is provided; prints usage instructions and exits with code 1 if missing. Extracts the model name by locating the --model flag in sys.argv and reading the next argument if present; silently retains default if --model is the final argument or missing.

  Delegates actual processing to run() with parameters: path, language="auto", dry_run boolean, force_context boolean, and model string. Propagates the exit code returned by run() back to the system via sys.exit(), allowing callers to detect success (0) or failure (non-zero).

  Supported model options documented in usage string: claude-haiku-4-5 (default), claude-3-5-sonnet-20241022, claude-3-5-haiku-20241022. Requires ANTHROPIC_API_KEY environment variable to be set before execution.
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
        - agentspec.utils.collect_source_files
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
  Manual argument parsing (rather than argparse) minimizes dependencies and suits a small CLI with few options, allowing simple inline flag detection without external libraries.

  Default model is claude-haiku-4-5 (cost-effective) to balance performance and API costs for typical documentation generation tasks. The --model flag is positioned after the path argument to maintain intuitive CLI ordering (target first, then options).

  Dry-run and force-context flags use simple boolean presence checks (no values required) to reduce parsing complexity and improve usability. Early validation and usage printing ensures users understand environment requirements before attempting to run.

  Delegating to run() keeps main() thin and testable, separating CLI concerns from business logic. Propagating exit codes unchanged preserves the caller's ability to detect success/failure in shell scripts and automation.

guardrails:
  - DO NOT modify the sys.exit(1) call for missing arguments; it ensures proper shell exit codes for scripting and automation
  - DO NOT change the default model without updating documentation and considering API cost implications for end users
  - DO NOT add new positional arguments without updating the usage string to remain synchronized
  - DO NOT remove or rename the --dry-run, --force-context, or --model flags; they are part of the public CLI contract
  - DO NOT alter the usage string without ensuring it accurately reflects all supported flags and options
  - DO NOT suppress or modify the exit code from run(); callers depend on it to detect success/failure
  - ALWAYS ensure the usage string remains synchronized with actual supported flags and their descriptions
  - ALWAYS preserve exact flag names as they are part of the public CLI contract
  - NOTE: sys.argv indexing assumes well-formed input; if --model is the last argument with no value following it, model silently remains at default (this is safe but may confuse users)
  - NOTE: The model parameter is passed as a string directly to run(); ensure run() validates or handles unknown model names gracefully to provide clear error messages

    changelog:
      - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
      - "- 2025-10-30: feat: robust docstring generation and Haiku defaults (e428337)"
      - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate (172e0a7)"
      - "- 2025-10-29: CRITICAL FIX: Process functions bottom-to-top to prevent line number invalidation and syntax errors (bab4295)"
```

---

## apply_docstring_with_metadata

**Location:** `/Users/davidmontgomery/agentspec/agentspec/insert_metadata.py:26`

### What This Does

Single-pass docstring insertion with metadata injection.

Builds the complete docstring (narrative + deterministic metadata) FIRST,
then inserts it ONCE into the file.

Supported languages:
- Python (.py): uses insert_docstring_at_line() and py_compile
- JS/TS (.js, .mjs, .jsx, .ts, .tsx): uses LanguageRegistry adapter.insert_docstring() and adapter.validate_syntax_string()

### Dependencies

**Calls:**
- `insert_docstring_at_line (Python)`
- `LanguageRegistry.get_by_extension (JS/TS)`
- `adapter.insert_docstring (JS/TS)`
- `adapter.validate_syntax_string (JS/TS)`
- `inject_deterministic_metadata`
- `os.replace`
- `py_compile.compile (Python)`

### Why This Approach

Previous implementation did a "two-phase" insert that called insert_docstring TWICE,
creating duplicate JSDoc blocks. This version builds the complete docstring first,
then inserts it once.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT call insert_docstring/insert_docstring_at_line more than ONCE per function**
- **ALWAYS build the complete docstring (narrative + metadata) BEFORE inserting**
- **ALWAYS operate on a temp copy and perform an atomic replace on success**
- **ALWAYS route by file extension; do not try to parse JS with Python tooling**

### Changelog

- 2025-11-01: Fix duplicate JSDoc insertion bug - build complete docstring first, insert once
- 2025-11-01: Add JS/TS support and unify two-phase flow

### Raw YAML Block

```yaml
what: |
  Single-pass docstring insertion with metadata injection.

  Builds the complete docstring (narrative + deterministic metadata) FIRST,
  then inserts it ONCE into the file.

  Supported languages:
  - Python (.py): uses insert_docstring_at_line() and py_compile
  - JS/TS (.js, .mjs, .jsx, .ts, .tsx): uses LanguageRegistry adapter.insert_docstring() and adapter.validate_syntax_string()

deps:
  calls:
    - insert_docstring_at_line (Python)
    - LanguageRegistry.get_by_extension (JS/TS)
    - adapter.insert_docstring (JS/TS)
    - adapter.validate_syntax_string (JS/TS)
    - inject_deterministic_metadata
    - os.replace
    - py_compile.compile (Python)
  imports:
    - agentspec.generate (inject_deterministic_metadata, insert_docstring_at_line)
    - agentspec.langs.LanguageRegistry

why: |
  Previous implementation did a "two-phase" insert that called insert_docstring TWICE,
  creating duplicate JSDoc blocks. This version builds the complete docstring first,
  then inserts it once.

guardrails:
  - DO NOT call insert_docstring/insert_docstring_at_line more than ONCE per function
  - ALWAYS build the complete docstring (narrative + metadata) BEFORE inserting
  - ALWAYS operate on a temp copy and perform an atomic replace on success
  - ALWAYS route by file extension; do not try to parse JS with Python tooling

changelog:
  - "2025-11-01: Fix duplicate JSDoc insertion bug - build complete docstring first, insert once"
  - "2025-11-01: Add JS/TS support and unify two-phase flow"
```

---

## LanguageAdapter

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/__init__.py:62`

### What This Does

Protocol defining the interface for language-specific adapters.

### Raw YAML Block

```yaml
Protocol defining the interface for language-specific adapters.

Any language adapter must implement all methods and properties defined here.
```

---

## file_extensions

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/__init__.py:70`

### What This Does

Return set of file extensions this adapter handles (e.g., {'.py', '.pyi'}).

### Raw YAML Block

```yaml
Return set of file extensions this adapter handles (e.g., {'.py', '.pyi'}).
```

---

## discover_files

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/__init__.py:76`

### What This Does

Discover all source files in target directory or return single file if target is a file.

### Raw YAML Block

```yaml
Discover all source files in target directory or return single file if target is a file.

Should respect language-specific ignore patterns and common exclusion directories.
```

---

## extract_docstring

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/__init__.py:84`

### What This Does

Extract docstring from the function/class at lineno in filepath.

### Raw YAML Block

```yaml
Extract docstring from the function/class at lineno in filepath.

Returns the raw docstring content including any agentspec blocks, or None.
```

---

## insert_docstring

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/__init__.py:92`

### What This Does

Insert or replace the docstring for the function/class at lineno in filepath.

### Raw YAML Block

```yaml
Insert or replace the docstring for the function/class at lineno in filepath.

Should handle proper indentation and formatting for the language.
```

---

## gather_metadata

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/__init__.py:100`

### What This Does

Extract function calls, imports, and other metadata for analysis.

### Raw YAML Block

```yaml
Extract function calls, imports, and other metadata for analysis.

Returns a dict with keys like 'calls', 'imports', 'called_by', etc.
```

---

## validate_syntax

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/__init__.py:108`

### What This Does

Check if the file has valid syntax after modifications.

### Raw YAML Block

```yaml
Check if the file has valid syntax after modifications.

Should return True if syntax is valid, False or raise if invalid.
```

---

## get_comment_delimiters

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/__init__.py:116`

### What This Does

Return the (start, end) delimiters for multi-line comments in this language.

### Raw YAML Block

```yaml
Return the (start, end) delimiters for multi-line comments in this language.

E.g., ('/*', '*/') for JavaScript, (', ') for Python docstrings.
```

---

## parse

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/__init__.py:124`

### What This Does

Parse source code into a language-specific AST or tree structure.

### Raw YAML Block

```yaml
Parse source code into a language-specific AST or tree structure.

Returns the parsed tree which can be traversed by other adapter methods.
```

---

## LanguageRegistry

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/__init__.py:133`

### What This Does

Global registry mapping file extensions to language adapters.

### Raw YAML Block

```yaml
Global registry mapping file extensions to language adapters.
```

---

## register

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/__init__.py:141`

### What This Does

Register an adapter for all its supported extensions.

### Raw YAML Block

```yaml
Register an adapter for all its supported extensions.
```

---

## unregister

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/__init__.py:147`

### What This Does

Unregister an adapter by extension.

### Raw YAML Block

```yaml
Unregister an adapter by extension.
```

---

## get_by_extension

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/__init__.py:152`

### What This Does

Get adapter for a file extension (e.g., '.py', '.js').

### Raw YAML Block

```yaml
Get adapter for a file extension (e.g., '.py', '.js').
```

---

## get_by_path

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/__init__.py:157`

### What This Does

Get adapter for a file by its path.

### Raw YAML Block

```yaml
Get adapter for a file by its path.
```

---

## supported_extensions

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/__init__.py:165`

### What This Does

Return all currently registered file extensions.

### Raw YAML Block

```yaml
Return all currently registered file extensions.
```

---

## list_adapters

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/__init__.py:170`

### What This Does

Return all registered adapters.

### Raw YAML Block

```yaml
Return all registered adapters.
```

---

## JavaScriptAdapter

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:83`

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

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:91`

### What This Does

Initialize the JavaScript adapter with tree-sitter parsers for JavaScript, TypeScript, and TSX.

### Raw YAML Block

```yaml
Initialize the JavaScript adapter with tree-sitter parsers for JavaScript, TypeScript, and TSX.
```

---

## file_extensions

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:127`

### What This Does

Return JavaScript/TypeScript file extensions this adapter handles.

### Raw YAML Block

```yaml
Return JavaScript/TypeScript file extensions this adapter handles.

Supports .js, .mjs, .jsx, .ts, .tsx.
```

---

## discover_files

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:135`

### What This Does

Discover all JavaScript files in target directory or return single file.

### Raw YAML Block

```yaml
Discover all JavaScript files in target directory or return single file.

Minimal pre-filtering (only .git exclusion).
All other exclusions (.venv, node_modules, build, etc.) handled by .gitignore
via collect_source_files post-filtering.
```

---

## extract_docstring

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:170`

### What This Does

Extract JSDoc comment from function/class at lineno in filepath.

### Raw YAML Block

```yaml
Extract JSDoc comment from function/class at lineno in filepath.

Returns the docstring content (without /** */ delimiters), or None.
```

---

## insert_docstring

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:194`

### What This Does

Insert or replace JSDoc block for function/class at lineno.

### Raw YAML Block

```yaml
Insert or replace JSDoc block for function/class at lineno.

Formats docstring with proper JSDoc indentation and * prefix.

Behavior:
- Replaces the closest JSDoc block immediately preceding the target function/class if present,
  regardless of whether we encounter the end (*/) or start (/**) first during scanning.
- Otherwise inserts a new JSDoc block directly before the function line.
- Validates the modified source using tree-sitter when available.
```

---

## gather_metadata

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:258`

### What This Does

Extract function calls, imports, and other metadata for a function.

### Raw YAML Block

```yaml
Extract function calls, imports, and other metadata for a function.

Returns dict with 'calls', 'imports', and 'called_by' keys.
```

---

## validate_syntax

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:286`

### What This Does

Check if file has valid JavaScript syntax by re-parsing.

### Raw YAML Block

```yaml
Check if file has valid JavaScript syntax by re-parsing.

Returns True if valid, raises ValueError if invalid.
```

---

## validate_syntax_string

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:300`

### What This Does

Validate JavaScript/TypeScript/TSX syntax string using tree-sitter.

### Raw YAML Block

```yaml
Validate JavaScript/TypeScript/TSX syntax string using tree-sitter.

Uses TSX parser for .tsx files, TypeScript parser for .ts files,
JavaScript parser for .js/.mjs/.jsx files.

Returns True if valid (no ERROR nodes), raises ValueError if invalid.
```

---

## get_comment_delimiters

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:329`

### What This Does

Return JavaScript multi-line comment delimiters for JSDoc.

### Raw YAML Block

```yaml
Return JavaScript multi-line comment delimiters for JSDoc.
```

---

## parse

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:335`

### What This Does

Parse JavaScript source code using tree-sitter.

### Raw YAML Block

```yaml
Parse JavaScript source code using tree-sitter.

Returns a tree-sitter Tree object.
```

---

## _find_preceding_jsdoc

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:348`

### What This Does

Find JSDoc comment immediately preceding a function/class at lineno.

### Raw YAML Block

```yaml
Find JSDoc comment immediately preceding a function/class at lineno.
```

---

## _extract_jsdoc_content

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:375`

### What This Does

Extract docstring content from JSDoc lines.

### Raw YAML Block

```yaml
Extract docstring content from JSDoc lines.
```

---

## _find_node_at_line

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:388`

### What This Does

Find function or class declaration node at specific line.

### Raw YAML Block

```yaml
Find function or class declaration node at specific line.
```

---

## find_in_node

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:393`

### What This Does

Recursively search for function/class at target line.

### Raw YAML Block

```yaml
Recursively search for function/class at target line.
```

---

## _extract_function_calls

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:417`

### What This Does

Extract function call names from a specific function.

### Raw YAML Block

```yaml
Extract function call names from a specific function.
```

---

## collect_calls

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:423`

### What This Does

Recursively collect call_expression nodes.

### Raw YAML Block

```yaml
Recursively collect call_expression nodes.
```

---

## _extract_call_name

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:438`

### What This Does

Extract the name of a called function from a call_expression node.

### Raw YAML Block

```yaml
Extract the name of a called function from a call_expression node.
```

---

## _extract_imports

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:455`

### What This Does

Extract import statements from the module.

### Raw YAML Block

```yaml
Extract import statements from the module.
```

---

## _has_error_nodes

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:481`

### What This Does

Check if parse tree contains ERROR or MISSING nodes.

### Raw YAML Block

```yaml
Check if parse tree contains ERROR or MISSING nodes.

ERROR nodes indicate parsing failures.
MISSING nodes indicate incomplete/invalid syntax (e.g., unclosed JSX tags).
```

---

## PythonAdapter

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/python_adapter.py:62`

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

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/python_adapter.py:71`

### What This Does

Return Python file extensions this adapter handles.

### Raw YAML Block

```yaml
Return Python file extensions this adapter handles.
```

---

## discover_files

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/python_adapter.py:77`

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

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/python_adapter.py:88`

### What This Does

Extract docstring from function/class at lineno in filepath.

### Raw YAML Block

```yaml
Extract docstring from function/class at lineno in filepath.

Returns the raw docstring including any agentspec blocks, or None.
```

---

## insert_docstring

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/python_adapter.py:108`

### What This Does

Insert or replace docstring for function/class at lineno in filepath.

### Raw YAML Block

```yaml
Insert or replace docstring for function/class at lineno in filepath.

Handles proper indentation and preservation of function body.
```

---

## gather_metadata

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/python_adapter.py:163`

### What This Does

Extract function calls, imports, and other metadata for a function.

### Raw YAML Block

```yaml
Extract function calls, imports, and other metadata for a function.

Returns dict with 'calls', 'imports', and 'called_by' keys.
```

---

## validate_syntax

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/python_adapter.py:196`

### What This Does

Check if file has valid Python syntax.

### Raw YAML Block

```yaml
Check if file has valid Python syntax.

Returns True if valid, raises SyntaxError if invalid.
```

---

## validate_syntax_string

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/python_adapter.py:209`

### What This Does

Validate Python syntax string.

### Raw YAML Block

```yaml
Validate Python syntax string.

Returns True if valid, raises ValueError if invalid.
```

---

## get_comment_delimiters

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/python_adapter.py:221`

### What This Does

Return Python multi-line string delimiters.

### Raw YAML Block

```yaml
Return Python multi-line string delimiters.
```

---

## parse

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/python_adapter.py:228`

### What This Does

Parse Python source code into an AST.

### Raw YAML Block

```yaml
Parse Python source code into an AST.
```

---

## _get_indent

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/python_adapter.py:235`

### What This Does

Get indentation string for an AST node.

### Raw YAML Block

```yaml
Get indentation string for an AST node.

Returns the indentation level as a string of spaces.
```

---

## _is_anthropic_model

**Location:** `/Users/davidmontgomery/agentspec/agentspec/llm.py:17`

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

**Location:** `/Users/davidmontgomery/agentspec/agentspec/llm.py:95`

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

## _detect_agentspec_doc

**Location:** `/Users/davidmontgomery/agentspec/agentspec/strip.py:10`

### What This Does

Heuristically detects whether a docstring was generated by agentspec as YAML or narrative form.

Returns a tuple (is_yaml, is_narrative) where:
- is_yaml: True if the docstring contains a fenced agentspec YAML block ('---agentspec' and '

### Raw YAML Block

```yaml
what: |
  Heuristically detects whether a docstring was generated by agentspec as YAML or narrative form.

  Returns a tuple (is_yaml, is_narrative) where:
  - is_yaml: True if the docstring contains a fenced agentspec YAML block ('---agentspec' and '
```

---

## strip_file

**Location:** `/Users/davidmontgomery/agentspec/agentspec/strip.py:54`

### What This Does

Removes agentspec-generated content from a single Python file with compile-safety per edit.

Behavior:
- Parses file with AST, finds functions with docstrings
- Detects agentspec YAML vs narrative docstrings using explicit markers
- Depending on mode ('yaml'|'docstrings'|'all'), deletes matching docstrings
- Also removes immediate following lines containing "[AGENTSPEC_CONTEXT]" prints
- For each deletion candidate, writes a temp file and py_compile checks before committing the change

Inputs:
- filepath: Path to Python file
- mode: One of 'yaml', 'docstrings', 'all'
- dry_run: If True, only prints actions without modifying files

Outputs:
- None; prints progress and performs in-place edits when not dry-run

### Dependencies

**Calls:**
- `ast.parse`
- `ast.walk`
- `isinstance`
- `ast.get_docstring`
- `_detect_agentspec_doc`
- `print`
- `py_compile.compile`

### Why This Approach

Per-edit compile checks ensure we never leave a file in a broken state. Bottom-to-top processing avoids
line shift issues when making multiple deletions in a single file.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT strip non-agentspec docstrings; only remove when explicit markers are found**
- **ALWAYS process functions bottom-to-top to avoid line-number invalidation**
- **ALWAYS use tmp file + py_compile before writing changes**
- **ALWAYS delete adjacent [AGENTSPEC_CONTEXT] print line if present**

### Changelog

- 2025-10-31: Initial implementation

### Raw YAML Block

```yaml
what: |
  Removes agentspec-generated content from a single Python file with compile-safety per edit.

  Behavior:
  - Parses file with AST, finds functions with docstrings
  - Detects agentspec YAML vs narrative docstrings using explicit markers
  - Depending on mode ('yaml'|'docstrings'|'all'), deletes matching docstrings
  - Also removes immediate following lines containing "[AGENTSPEC_CONTEXT]" prints
  - For each deletion candidate, writes a temp file and py_compile checks before committing the change

  Inputs:
  - filepath: Path to Python file
  - mode: One of 'yaml', 'docstrings', 'all'
  - dry_run: If True, only prints actions without modifying files

  Outputs:
  - None; prints progress and performs in-place edits when not dry-run
deps:
  calls:
    - ast.parse
    - ast.walk
    - isinstance
    - ast.get_docstring
    - _detect_agentspec_doc
    - print
    - py_compile.compile
  imports:
    - ast
    - os
    - tempfile
why: |
  Per-edit compile checks ensure we never leave a file in a broken state. Bottom-to-top processing avoids
  line shift issues when making multiple deletions in a single file.
guardrails:
  - DO NOT strip non-agentspec docstrings; only remove when explicit markers are found
  - ALWAYS process functions bottom-to-top to avoid line-number invalidation
  - ALWAYS use tmp file + py_compile before writing changes
  - ALWAYS delete adjacent [AGENTSPEC_CONTEXT] print line if present
changelog:
  - "2025-10-31: Initial implementation"
```

---

## _detect_agentspec_jsdoc

**Location:** `/Users/davidmontgomery/agentspec/agentspec/strip.py:178`

### What This Does

Detect whether a JSDoc block contains agentspec-generated content and whether it is YAML vs narrative.

Returns (is_yaml, is_narrative). A block is YAML if it contains '---agentspec' or '

### Raw YAML Block

```yaml
what: |
  Detect whether a JSDoc block contains agentspec-generated content and whether it is YAML vs narrative.

  Returns (is_yaml, is_narrative). A block is YAML if it contains '---agentspec' or '
```

---

## strip_js_file

**Location:** `/Users/davidmontgomery/agentspec/agentspec/strip.py:211`

### What This Does

Removes agentspec-generated JSDoc blocks from a JavaScript/TypeScript file using textual heuristics.

Behavior:
- Scans for '/**' ... '*/' JSDoc blocks
- Uses _detect_agentspec_jsdoc() to classify each block as YAML vs narrative
- Depending on mode ('yaml'|'docstrings'|'all'), deletes matching blocks
- Also removes single following line if it matches a console.log with 'AGENTSPEC_CONTEXT'
- Writes the file once after all removals; prints actions and respects dry_run

Note: Syntax validation is attempted via language adapter when available; otherwise no validation is performed.

### Dependencies

**Calls:**
- `_detect_agentspec_jsdoc`

### ⚠️ Guardrails (CRITICAL)

- **DO NOT attempt to reformat; only delete exact block spans**
- **ALWAYS respect dry_run**

### Changelog

- 2025-11-01: Add JS/TS strip support

### Raw YAML Block

```yaml
what: |
  Removes agentspec-generated JSDoc blocks from a JavaScript/TypeScript file using textual heuristics.

  Behavior:
  - Scans for '/**' ... '*/' JSDoc blocks
  - Uses _detect_agentspec_jsdoc() to classify each block as YAML vs narrative
  - Depending on mode ('yaml'|'docstrings'|'all'), deletes matching blocks
  - Also removes single following line if it matches a console.log with 'AGENTSPEC_CONTEXT'
  - Writes the file once after all removals; prints actions and respects dry_run

  Note: Syntax validation is attempted via language adapter when available; otherwise no validation is performed.
deps:
  calls:
    - _detect_agentspec_jsdoc
  imports:
    - agentspec.langs.LanguageRegistry
guardrails:
  - DO NOT attempt to reformat; only delete exact block spans
  - ALWAYS respect dry_run
changelog:
  - "2025-11-01: Add JS/TS strip support"
```

---

## run

**Location:** `/Users/davidmontgomery/agentspec/agentspec/strip.py:316`

### What This Does

Batch entry point for stripping agentspec content across Python and JavaScript/TypeScript files.

Accepts file or directory path, collects source files across registered languages, and applies language-specific
strip routines (AST-based for Python; JSDoc heuristic for JS/TS). Dry-run prints intended changes without modifying files.
Returns exit code 0 on success, 1 on errors.

### Dependencies

**Calls:**
- `Path`
- `collect_source_files`
- `strip_file (Python)`
- `strip_js_file (JavaScript/TypeScript)`
- `print`

### Why This Approach

Unifies strip behavior across languages and allows pre-clean runs before regeneration to avoid duplicate blocks.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT require any API credentials**
- **ALWAYS handle both file and directory targets**
- **ALWAYS route by file extension conservatively**

### Changelog

- 2025-11-01: Extend strip to JS/TS via JSDoc heuristic and collect_source_files()

### Raw YAML Block

```yaml
what: |
  Batch entry point for stripping agentspec content across Python and JavaScript/TypeScript files.

  Accepts file or directory path, collects source files across registered languages, and applies language-specific
  strip routines (AST-based for Python; JSDoc heuristic for JS/TS). Dry-run prints intended changes without modifying files.
  Returns exit code 0 on success, 1 on errors.
deps:
  calls:
    - Path
    - collect_source_files
    - strip_file (Python)
    - strip_js_file (JavaScript/TypeScript)
    - print
  imports:
    - agentspec.utils.collect_source_files
    - pathlib.Path
why: |
  Unifies strip behavior across languages and allows pre-clean runs before regeneration to avoid duplicate blocks.
guardrails:
  - DO NOT require any API credentials
  - ALWAYS handle both file and directory targets
  - ALWAYS route by file extension conservatively
changelog:
  - "2025-11-01: Extend strip to JS/TS via JSDoc heuristic and collect_source_files()"
```

---

## _is_excluded_by_dir

**Location:** `/Users/davidmontgomery/agentspec/agentspec/utils.py:37`

### What This Does

Fast pre-filter to skip obviously excluded directories before calling git check-ignore.

ONLY checks for .git directory to avoid recursing into repository metadata.
All other exclusions (.venv, node_modules, etc.) are handled by .gitignore.

Inputs:
- path: A pathlib.Path object

Behavior:
- Checks if '.git' is in any path component
- Returns True only for .git, False otherwise
- All other filtering delegated to git check-ignore

### Dependencies

### Why This Approach

Previous versions tried to maintain a hardcoded exclusion list that would never
cover all cases (.venv311, venv38, etc.). Instead, rely on .gitignore which the
user has already configured correctly. Only exclude .git since it's universal
and we never want to process repository metadata.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT add more directories to this check; use .gitignore instead**
- **ONLY check for .git directory**
- **Let git check-ignore handle all other exclusions**

### Changelog

- 2025-11-01: Simplify to only check .git; delegate all other exclusions to .gitignore
- 2025-11-01: Add pattern matching for versioned virtualenvs (.venv*, venv*, .env*)
- 2025-10-30: feat: robust docstring generation and Haiku defaults

### Raw YAML Block

```yaml
what: |
  Fast pre-filter to skip obviously excluded directories before calling git check-ignore.
  
  ONLY checks for .git directory to avoid recursing into repository metadata.
  All other exclusions (.venv, node_modules, etc.) are handled by .gitignore.

  Inputs:
  - path: A pathlib.Path object

  Behavior:
  - Checks if '.git' is in any path component
  - Returns True only for .git, False otherwise
  - All other filtering delegated to git check-ignore

deps:
      imports:
        - pathlib.Path

why: |
  Previous versions tried to maintain a hardcoded exclusion list that would never
  cover all cases (.venv311, venv38, etc.). Instead, rely on .gitignore which the
  user has already configured correctly. Only exclude .git since it's universal
  and we never want to process repository metadata.

guardrails:
  - DO NOT add more directories to this check; use .gitignore instead
  - ONLY check for .git directory
  - Let git check-ignore handle all other exclusions

changelog:
      - "2025-11-01: Simplify to only check .git; delegate all other exclusions to .gitignore"
      - "2025-11-01: Add pattern matching for versioned virtualenvs (.venv*, venv*, .env*)"
      - "2025-10-30: feat: robust docstring generation and Haiku defaults"
```

---

## _find_git_root

**Location:** `/Users/davidmontgomery/agentspec/agentspec/utils.py:79`

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

**Location:** `/Users/davidmontgomery/agentspec/agentspec/utils.py:145`

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

**Location:** `/Users/davidmontgomery/agentspec/agentspec/utils.py:223`

### What This Does

Find .agentspecignore file.

### Raw YAML Block

```yaml
Find .agentspecignore file. 

Returns agentspec's built-in .agentspecignore from the package installation.
User's project-specific .agentspecignore is checked in addition (via _parse_agentspecignore).
```

---

## _parse_agentspecignore

**Location:** `/Users/davidmontgomery/agentspec/agentspec/utils.py:247`

### What This Does

Parse .agentspecignore file and return list of patterns (filtered for comments and empty lines).

### Raw YAML Block

```yaml
Parse .agentspecignore file and return list of patterns (filtered for comments and empty lines).
```

---

## _matches_pattern

**Location:** `/Users/davidmontgomery/agentspec/agentspec/utils.py:261`

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

**Location:** `/Users/davidmontgomery/agentspec/agentspec/utils.py:321`

### What This Does

Check if a path is ignored by .agentspecignore. Returns True if ignored.

### Raw YAML Block

```yaml
Check if a path is ignored by .agentspecignore. Returns True if ignored.

Loads patterns from:
1. Agentspec's built-in .agentspecignore (stock patterns)
2. User's project .agentspecignore (if it exists - for project-specific overrides)

Both sets of patterns are merged and applied.
```

---

## collect_python_files

**Location:** `/Users/davidmontgomery/agentspec/agentspec/utils.py:363`

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

## collect_source_files

**Location:** `/Users/davidmontgomery/agentspec/agentspec/utils.py:461`

### What This Does

Discover source files across all registered language adapters (Python, JavaScript, TypeScript) while
honoring repository ignore patterns and adapter-specific exclusions.

Behavior:
- Accepts a file or directory `target`
- If `target` is a file, returns `[target]` only if its extension is supported by any registered adapter
- If `target` is a directory, unions results of per-adapter discovery:
  * Python files are discovered via `collect_python_files` (preserves .gitignore and .agentspecignore handling)
  * Other languages use their adapter's `discover_files` method (expected to exclude build/third-party dirs)
  * ALL files (Python and non-Python) are post-filtered through .gitignore and .agentspecignore for consistency
- Deduplicates and returns a sorted list of absolute Paths

Edge cases:
- Nonexistent `target`: returns an empty list (graceful degradation consistent with other collectors)
- Repositories without git: Python discovery still works without .gitignore filtering; adapters may still exclude common directories

### Dependencies

**Calls:**
- `LanguageRegistry.list_adapters`
- `LanguageRegistry.supported_extensions`
- `collect_python_files`
- `adapter.discover_files`
- `target.is_file`
- `target.is_dir`
- `target.suffix`
- `files.sort`
- `_find_git_root`
- `_git_check_ignore`
- `_check_agentspecignore`

### Why This Approach

Agentspec aims to be language-agnostic. Centralizing file discovery avoids duplicating multi-language logic
in each CLI entry point (extract, lint, strip). It preserves robust Python discovery semantics while enabling
pluggable discovery for other languages via their adapters.

The post-filtering through .gitignore and .agentspecignore ensures that ALL languages respect the same
ignore patterns, preventing vendor/minified/build files from being processed regardless of language.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT hard-code extensions here; rely on registered adapters for non-Python languages**
- **DO NOT raise on missing paths; always return an empty list for graceful CLI behavior**
- **ALWAYS delegate Python discovery to `collect_python_files` to preserve .gitignore and .agentspecignore handling**
- **ALWAYS post-filter adapter results through .gitignore and .agentspecignore to maintain parity with Python**
- **ALWAYS return absolute, sorted paths for deterministic downstream processing**

### Changelog

- 2025-11-01: Add multi-language collect_source_files (JS/TS support)
- 2025-11-01: Fix .gitignore/.agentspecignore filtering for non-Python languages (adapter results now post-filtered)

### Raw YAML Block

```yaml
what: |
  Discover source files across all registered language adapters (Python, JavaScript, TypeScript) while
  honoring repository ignore patterns and adapter-specific exclusions.

  Behavior:
  - Accepts a file or directory `target`
  - If `target` is a file, returns `[target]` only if its extension is supported by any registered adapter
  - If `target` is a directory, unions results of per-adapter discovery:
    * Python files are discovered via `collect_python_files` (preserves .gitignore and .agentspecignore handling)
    * Other languages use their adapter's `discover_files` method (expected to exclude build/third-party dirs)
    * ALL files (Python and non-Python) are post-filtered through .gitignore and .agentspecignore for consistency
  - Deduplicates and returns a sorted list of absolute Paths

  Edge cases:
  - Nonexistent `target`: returns an empty list (graceful degradation consistent with other collectors)
  - Repositories without git: Python discovery still works without .gitignore filtering; adapters may still exclude common directories

deps:
  calls:
    - LanguageRegistry.list_adapters
    - LanguageRegistry.supported_extensions
    - collect_python_files
    - adapter.discover_files
    - target.is_file
    - target.is_dir
    - target.suffix
    - files.sort
    - _find_git_root
    - _git_check_ignore
    - _check_agentspecignore
  imports:
    - agentspec.langs.LanguageRegistry
    - pathlib.Path
    - typing.List

why: |
  Agentspec aims to be language-agnostic. Centralizing file discovery avoids duplicating multi-language logic
  in each CLI entry point (extract, lint, strip). It preserves robust Python discovery semantics while enabling
  pluggable discovery for other languages via their adapters.
  
  The post-filtering through .gitignore and .agentspecignore ensures that ALL languages respect the same
  ignore patterns, preventing vendor/minified/build files from being processed regardless of language.

guardrails:
  - DO NOT hard-code extensions here; rely on registered adapters for non-Python languages
  - DO NOT raise on missing paths; always return an empty list for graceful CLI behavior
  - ALWAYS delegate Python discovery to `collect_python_files` to preserve .gitignore and .agentspecignore handling
  - ALWAYS post-filter adapter results through .gitignore and .agentspecignore to maintain parity with Python
  - ALWAYS return absolute, sorted paths for deterministic downstream processing

changelog:
  - "2025-11-01: Add multi-language collect_source_files (JS/TS support)"
  - "2025-11-01: Fix .gitignore/.agentspecignore filtering for non-Python languages (adapter results now post-filtered)"
```

---

## load_env_from_dotenv

**Location:** `/Users/davidmontgomery/agentspec/agentspec/utils.py:581`

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

