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

## _show_generate_rich_help

**Location:** `/Users/davidmontgomery/agentspec/agentspec/cli.py:477`

### What This Does

Render a dyslexia-friendly Rich help for `agentspec generate`, including a Quick Provider Guide with
copy/paste examples for OpenAI (CFG default), Anthropic, and Ollama. Uses big panels and short lines.

### Raw YAML Block

```yaml
what: |
  Render a dyslexia-friendly Rich help for `agentspec generate`, including a Quick Provider Guide with
  copy/paste examples for OpenAI (CFG default), Anthropic, and Ollama. Uses big panels and short lines.
```

---

## _show_prompts_rich_help

**Location:** `/Users/davidmontgomery/agentspec/agentspec/cli.py:536`

### What This Does

Render a Rich-formatted help screen for the `prompts` subcommand with full TUI parity to generate -h.
Includes usage guide, workflow explanation, examples, and complete flags table. Critical accessibility
requirement for dyslexia accommodation.

### Raw YAML Block

```yaml
what: |
  Render a Rich-formatted help screen for the `prompts` subcommand with full TUI parity to generate -h.
  Includes usage guide, workflow explanation, examples, and complete flags table. Critical accessibility
  requirement for dyslexia accommodation.
```

---

## _show_lint_rich_help

**Location:** `/Users/davidmontgomery/agentspec/agentspec/cli.py:618`

### What This Does

Rich TUI help for agentspec lint command.

### Raw YAML Block

```yaml
Rich TUI help for agentspec lint command.
```

---

## _show_extract_rich_help

**Location:** `/Users/davidmontgomery/agentspec/agentspec/cli.py:672`

### What This Does

Rich TUI help for agentspec extract command.

### Raw YAML Block

```yaml
Rich TUI help for agentspec extract command.
```

---

## _show_strip_rich_help

**Location:** `/Users/davidmontgomery/agentspec/agentspec/cli.py:723`

### What This Does

Rich TUI help for agentspec strip command.

### Raw YAML Block

```yaml
Rich TUI help for agentspec strip command.
```

---

## _check_python_version

**Location:** `/Users/davidmontgomery/agentspec/agentspec/cli.py:783`

### Raw YAML Block

```yaml
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
```

---

## main

**Location:** `/Users/davidmontgomery/agentspec/agentspec/cli.py:863`

### What This Does

CLI entry point that parses command-line arguments and dispatches to subcommands: lint, extract, generate, strip, and prompts.

Behavior: Loads .env via load_env_from_dotenv(). Uses argparse with Rich help when available. Intercepts
-h/--help and missing provider value for generate to render dyslexia-friendly Rich help panels instead of
raw argparse errors.

### Raw YAML Block

```yaml
what: |
  CLI entry point that parses command-line arguments and dispatches to subcommands: lint, extract, generate, strip, and prompts.

  Behavior: Loads .env via load_env_from_dotenv(). Uses argparse with Rich help when available. Intercepts
  -h/--help and missing provider value for generate to render dyslexia-friendly Rich help panels instead of
  raw argparse errors.
```

---

## _get_function_calls

**Location:** `/Users/davidmontgomery/agentspec/agentspec/collect.py:28`

### Raw YAML Block

```yaml
what: |
  Extracts all function call names from an AST node and returns them as a sorted, deduplicated list of strings.

  Traverses the entire AST subtree using ast.walk() to find all Call nodes. For each Call node, inspects the func attribute to determine the call type:
  - If func is an ast.Attribute (method call like obj.method()), constructs a qualified name by extracting the base object identifier (either from ast.Name.id or nested ast.Attribute.attr) and appending the method name with dot notation (e.g., "obj.method").
  - If func is an ast.Name (simple function call like func()), appends just the function identifier.
  - Ignores calls where the base cannot be determined (base is None for Attribute nodes with non-Name/non-Attribute values).

  Returns a sorted list with duplicates removed. Empty strings are filtered out before deduplication.

  Inputs: node (ast.AST) - any AST node to analyze
  Outputs: List[str] - sorted, unique function call names found in the node and all descendants

  Edge cases:
  - Nested method chains (e.g., obj.method1().method2()) extract only the outermost call names
  - Attribute access on non-Name/non-Attribute values (e.g., function returns) are skipped silently
  - Lambda calls and dynamic calls via variables are captured by their variable name, not their runtime target
  - Empty input nodes produce empty output list
    deps:
      calls:
        - ast.walk
        - calls.append
        - isinstance
        - sorted
      imports:
        - __future__.annotations
        - agentspec.langs.LanguageRegistry
        - ast
        - difflib
        - pathlib.Path
        - re
        - subprocess
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Tuple


why: |
  This function enables static analysis of code to identify which functions and methods are invoked within a given code block. The approach uses ast.walk() for simplicity and completeness rather than manual recursion, ensuring all nested calls are discovered. Deduplication and sorting provide a canonical, readable output suitable for dependency tracking, call graph construction, or code impact analysis. The qualified name format (base.method) preserves semantic meaning for method calls while remaining simple to parse and compare.

guardrails:
  - DO NOT rely on this function to determine runtime behavior or actual call targets, as it performs static analysis only and cannot resolve dynamic dispatch, monkey-patching, or indirect calls through variables.
  - DO NOT assume the extracted names are valid or callable; they are syntactic identifiers that may reference undefined symbols, built-ins, or non-existent attributes.
  - DO NOT use this for security analysis without additional validation, as it does not distinguish between safe library calls and potentially dangerous operations.
  - DO NOT expect this to handle all call patterns; it misses calls via getattr(), operator overloading, or calls stored in data structures.

    changelog:
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
      - "- 2025-10-30: feat: enhance CLI help and add rich formatting support (cb3873d)"
      - "- 2025-10-30: feat: robust docstring generation and Haiku defaults (e428337)"
```

---

## _get_module_imports

**Location:** `/Users/davidmontgomery/agentspec/agentspec/collect.py:103`

### Raw YAML Block

```yaml
what: |
  Extracts all module import names from an AST (Abstract Syntax Tree) by traversing the tree's body and collecting both direct imports (ast.Import) and from-imports (ast.ImportFrom).

  For ast.Import nodes, appends the full module name (e.g., "os", "numpy.random").
  For ast.ImportFrom nodes, constructs qualified names by joining the source module with the imported name (e.g., "os.path" from "from os import path").

  Returns a sorted, deduplicated list of import strings. Filters out empty strings that may result from malformed or relative imports where module is None.

  Inputs:
  - tree: ast.AST object (typically ast.Module from ast.parse())

  Outputs:
  - List[str]: sorted unique import identifiers

  Edge cases:
  - Handles relative imports where node.module is None by treating as empty string
  - Deduplicates imports using set comprehension before sorting
  - Gracefully handles trees without a body attribute via getattr with empty list default
  - Filters out empty strings to avoid polluting results from edge cases
    deps:
      calls:
        - getattr
        - imports.append
        - isinstance
        - join
        - sorted
      imports:
        - __future__.annotations
        - agentspec.langs.LanguageRegistry
        - ast
        - difflib
        - pathlib.Path
        - re
        - subprocess
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Tuple


why: |
  This function enables static analysis of Python source code to identify external dependencies without executing the code. Sorting and deduplication ensure consistent, clean output for downstream processing (e.g., dependency tracking, import validation).

  Using ast module avoids regex fragility and handles Python syntax edge cases correctly. The approach trades off some complexity for robustness—parsing the full AST is more reliable than string matching.

guardrails:
  - DO NOT execute the code or import modules—ast parsing is static analysis only, preventing side effects and security risks
  - DO NOT assume all imports are absolute—relative imports (from . import x) have module=None and must be handled gracefully
  - DO NOT skip deduplication—multiple import statements for the same module would pollute results without set filtering
  - DO NOT return unsorted results—consumers expect deterministic, comparable output for testing and caching

    changelog:
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
      - "- 2025-10-30: feat: enhance CLI help and add rich formatting support (cb3873d)"
      - "- 2025-10-30: feat: robust docstring generation and Haiku defaults (e428337)"
```

---

## _normalize_metadata_list

**Location:** `/Users/davidmontgomery/agentspec/agentspec/collect.py:177`

### Raw YAML Block

```yaml
what: |
  Normalizes arbitrary metadata values into a canonical sorted list of unique strings.

  Accepts multiple input types:
  - None/empty values: returns empty list []
  - Iterables (list, tuple, set): converts each element to string, strips whitespace, deduplicates via set, returns sorted list
  - Scalar values: converts to string, strips whitespace, returns single-element list if non-empty, else empty list

  All string conversions use str() to handle non-string types. Whitespace stripping occurs before deduplication to treat "value" and " value " as identical. Empty strings after stripping are filtered out. Final output is always sorted alphabetically for deterministic ordering.

  Edge cases handled:
  - Falsy iterables (empty list/tuple/set) return []
  - Whitespace-only strings become [] after strip
  - Mixed-type iterables (e.g., [1, "two", None]) are all converted to strings
  - Duplicate values across different types (e.g., 1 and "1") deduplicate to single "1"
    deps:
      calls:
        - isinstance
        - sorted
        - str
        - strip
      imports:
        - __future__.annotations
        - agentspec.langs.LanguageRegistry
        - ast
        - difflib
        - pathlib.Path
        - re
        - subprocess
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Tuple


why: |
  Metadata often arrives from heterogeneous sources in inconsistent formats (user input, config files, API responses). Normalization ensures:
  1. Consistent representation for comparison and storage
  2. Deduplication prevents redundant metadata entries
  3. Sorted output enables deterministic behavior and easier testing
  4. Whitespace tolerance handles common formatting variations
  5. Type coercion via str() provides robustness without strict validation

  This permissive approach prioritizes usability over strictness, accepting any input and producing valid output rather than raising errors.

guardrails:
  - DO NOT assume input is already a string or list—handle all types via str() conversion to prevent TypeErrors
  - DO NOT skip whitespace stripping—leading/trailing spaces cause false duplicates and inconsistent comparisons
  - DO NOT preserve input order—sorting is required for deterministic output and cache-friendly behavior
  - DO NOT return None or non-list types—callers expect a list always, even if empty
  - DO NOT mutate input—use set comprehension and sorted() to create new collections
  - DO NOT allow None elements in output—filter after strip() to prevent ["", None] artifacts

    changelog:
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
      - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
```

---

## _collect_python_deps

**Location:** `/Users/davidmontgomery/agentspec/agentspec/collect.py:251`

### Raw YAML Block

```yaml
what: |
  Extracts call and import metadata from a Python source file for a specific function using Abstract Syntax Tree (AST) parsing.

  **Inputs:**
  - filepath: Path object pointing to a Python source file
  - func_name: String name of the target function to analyze

  **Outputs:**
  - Returns a tuple of (deps_calls, imports) where:
    - deps_calls: List of function/method calls made within the target function
    - imports: List of module imports present in the file
  - Returns None if the file cannot be parsed, the function is not found, or any exception occurs during processing

  **Behavior:**
  1. Reads the source file as UTF-8 text
  2. Parses the source into an AST using ast.parse()
  3. Walks the AST to locate a FunctionDef or AsyncFunctionDef node matching func_name
  4. If found, extracts function calls via _get_function_calls() and module imports via _get_module_imports()
  5. Returns both lists as a tuple

  **Edge Cases:**
  - File encoding issues: Assumes UTF-8; non-UTF-8 files will raise an exception and return None
  - Syntax errors: Malformed Python files will fail ast.parse() and return None
  - Function not found: Returns None if func_name does not exist in the file
  - Duplicate function names: Returns the first matching FunctionDef or AsyncFunctionDef encountered during tree walk
  - Empty files or files with no imports/calls: Returns empty lists, not None
    deps:
      calls:
        - _get_function_calls
        - _get_module_imports
        - ast.parse
        - ast.walk
        - filepath.read_text
        - isinstance
        - str
      imports:
        - __future__.annotations
        - agentspec.langs.LanguageRegistry
        - ast
        - difflib
        - pathlib.Path
        - re
        - subprocess
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Tuple


why: |
  AST-based static analysis provides accurate, syntax-aware extraction of dependencies without executing code, avoiding side effects and security risks. Using ast.walk() ensures all nested scopes are examined. The broad exception handling allows graceful degradation when files are unparseable or inaccessible, preventing the collection pipeline from crashing on malformed inputs. Returning None on failure signals to the caller that metadata could not be obtained, enabling fallback strategies. This approach scales to large codebases and integrates with automated tooling for dependency graph construction.

guardrails:
  - DO NOT execute the source code; AST parsing is static analysis only to prevent arbitrary code execution and maintain security
  - DO NOT assume UTF-8 encoding without validation; explicitly specify encoding to handle files with different encodings gracefully
  - DO NOT raise exceptions to the caller; catch all exceptions and return None to allow batch processing of multiple files without pipeline interruption
  - DO NOT modify the source file or filesystem; this function is read-only and must have no side effects
  - DO NOT assume func_name is unique; document that the first match is returned and callers should handle potential ambiguity
  - DO NOT parse files larger than available memory; very large files may cause memory exhaustion; consider adding file size checks upstream

    changelog:
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
      - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
```

---

## _collect_git_changelog

**Location:** `/Users/davidmontgomery/agentspec/agentspec/collect.py:341`

### Raw YAML Block

```yaml
what: |
  Collects deterministic git changelog entries for a specified function within a file.

  **Inputs:**
  - filepath: Path object pointing to a source file (Python, JavaScript, etc.)
  - func_name: String name of the function to track

  **Outputs:**
  - List of strings formatted as "- YYYY-MM-DD: commit message (short hash)"
  - Returns up to 5 most recent commits
  - Falls back to ["- no git history available"] on any unrecoverable error

  **Behavior:**
  1. Resolves filepath to absolute path and locates the git repository root by walking up parent directories until .git is found
  2. Computes relative path from git root to target file
  3. Attempts function-level history using `git log -L :func_name:rel_path` to track changes to the specific function
  4. If function-level tracking fails (common for nested functions in IIFEs or JavaScript closures), falls back to file-level history using `git log` on the entire file
  5. Validates all output lines against regex pattern `^-\s+\d{4}-\d{2}-\d{2}:\s+.+\([a-f0-9]{4,}\)$` to ensure deterministic, well-formed entries
  6. Returns empty list as ["- none yet"] if no valid commits found after fallback

  **Edge cases:**
  - File not in any git repository: returns ["- no git history available"]
  - Function name not found in file: silently falls back to file-level history
  - Subprocess errors (git not installed, permission denied): caught and returns ["- no git history available"]
  - Malformed git output: filtered out by regex validation, only well-formed lines included
  - Unicode decode errors: handled with errors="ignore" to prevent crashes
    deps:
      calls:
        - commit_pattern.match
        - decode
        - exists
        - filepath.is_file
        - filepath.relative_to
        - filepath.resolve
        - lines.append
        - list
        - ln.strip
        - out.splitlines
        - re.compile
        - str
        - subprocess.check_output
      imports:
        - __future__.annotations
        - agentspec.langs.LanguageRegistry
        - ast
        - difflib
        - pathlib.Path
        - re
        - subprocess
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Tuple


why: |
  Function-level git tracking provides fine-grained change history for documentation purposes, enabling readers to understand when and why specific functions were modified. The fallback to file-level history is necessary because git's `-L` option (line-range tracking) does not work reliably for nested functions in JavaScript IIFEs or other dynamically-scoped constructs where function boundaries are not statically determinable by git.

  The regex validation ensures output is deterministic and parseable by downstream consumers, preventing malformed or partial git output from corrupting documentation. Running git commands in the correct repository root (not current working directory) ensures correctness when the codebase spans multiple git repositories or when the tool is invoked from arbitrary directories.

  Limiting to 5 commits balances completeness with readability in generated documentation. The short hash (4+ chars) provides sufficient uniqueness for most repositories while keeping output compact.

guardrails:
  - DO NOT run git commands in the current working directory without first locating the file's actual git root; this causes failures when the file is in a different repository than the CWD
  - DO NOT assume function-level history will succeed; always provide a file-level fallback for languages/patterns where function boundaries are ambiguous
  - DO NOT include malformed or partial git output in results; validate all lines against the expected format regex to maintain determinism
  - DO NOT raise exceptions on git failures; always return a sensible fallback message so that missing history does not break documentation generation
  - DO NOT decode git output as UTF-8 without error handling; use errors="ignore" to gracefully handle non-UTF-8 bytes in commit messages

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
      - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
```

---

## _collect_javascript_metadata

**Location:** `/Users/davidmontgomery/agentspec/agentspec/collect.py:485`

### Raw YAML Block

```yaml
what: |
  Collects call and import metadata for JavaScript files by delegating to a language-specific adapter.

  **Inputs:**
  - filepath: Path object pointing to a JavaScript file
  - func_name: Name of the function or entity to analyze within the file

  **Outputs:**
  - Returns a dictionary with "deps" (containing "calls" and "imports" lists) and "changelog" metadata, or None if no adapter is available
  - "calls": sorted list of detected function/method calls (e.g., ["foo.bar", "baz"])
  - "imports": sorted list of detected import statements or require() calls
  - "changelog": git history metadata for the file and function

  **Behavior:**
  1. Retrieves the appropriate language adapter from LanguageRegistry based on file path
  2. Attempts to gather metadata via adapter.gather_metadata(); silently catches exceptions and defaults to empty dict
  3. Validates that returned metadata is a dict; coerces to empty dict if not
  4. Normalizes both "calls" and "imports" lists via _normalize_metadata_list()
  5. If adapter extraction yields no calls or imports, performs lightweight fallback regex scanning on raw source:
     - Regex pattern `([A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)?)\s*\(` captures function/method names followed by `(`
     - Scans for lines starting with "import " or containing "require(" to collect import statements
  6. Collects git changelog metadata via _collect_git_changelog()
  7. Returns structured dict or None if no adapter found

  **Edge cases:**
  - File read failures (encoding errors, permissions) are caught and treated as empty source
  - Adapter exceptions are silently swallowed; metadata defaults to {}
  - Non-dict adapter returns are coerced to {}
  - Regex fallback is naive and may over-capture or under-capture in complex JavaScript
    deps:
      calls:
        - LanguageRegistry.get_by_path
        - _collect_git_changelog
        - _normalize_metadata_list
        - _re.findall
        - adapter.gather_metadata
        - filepath.read_text
        - import_lines.append
        - isinstance
        - line.strip
        - metadata.get
        - set
        - sorted
        - src.splitlines
        - startswith
      imports:
        - __future__.annotations
        - agentspec.langs.LanguageRegistry
        - ast
        - difflib
        - pathlib.Path
        - re
        - subprocess
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Tuple


why: |
  This function provides a resilient, multi-layered approach to extracting JavaScript dependencies:
  - **Adapter delegation** allows language-specific parsing (e.g., tree-sitter) for accuracy
  - **Exception handling** prevents crashes from missing dependencies or malformed files
  - **Regex fallback** ensures partial metadata extraction even when advanced parsing is unavailable, improving coverage
  - **Normalization** guarantees consistent list types and prevents downstream type errors
  - **Git changelog integration** provides historical context for dependency changes

  The tradeoff is that regex fallback is imprecise (may capture false positives or miss dynamic calls), but it gracefully degrades when the primary adapter fails rather than returning nothing.

guardrails:
  - DO NOT assume adapter.gather_metadata() always returns a valid dict—always validate and coerce to {} to prevent KeyError or AttributeError downstream
  - DO NOT skip the regex fallback if adapter extraction is incomplete; missing deps metadata reduces traceability and may cause incomplete dependency graphs
  - DO NOT use raw regex patterns without bounds checking on source file size; extremely large files could cause performance degradation (consider adding file size limits if needed)
  - DO NOT expose raw regex matches without deduplication and sorting; inconsistent ordering breaks reproducibility and complicates testing
  - DO NOT fail silently on file read errors without logging; silent failures make debugging difficult when source files are inaccessible

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
      - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
```

---

## collect_changelog_diffs

**Location:** `/Users/davidmontgomery/agentspec/agentspec/collect.py:617`

### Raw YAML Block

```yaml
what: |
  Retrieves the git history of a specific function within a file using `git log -L` (line-based history).

  **Inputs:**
  - filepath: Path object pointing to the target Python file
  - func_name: String name of the function to trace (e.g., "my_function")

  **Outputs:**
  - List of dictionaries, each containing:
    - "hash": commit SHA (short form)
    - "date": commit date in YYYY-MM-DD format
    - "message": commit message subject line
    - "diff": accumulated diff/patch content for that commit
  - Empty list [] if git command fails or no history found

  **Behavior:**
  - Executes `git log -L :func_name:filepath` to extract function-specific history (last 5 commits)
  - Parses output using custom delimiter "COMMIT_START|||" to separate commit metadata from diff content
  - Accumulates multi-line diff output per commit and associates it with commit metadata
  - Handles UTF-8 decoding with error suppression to tolerate non-UTF8 bytes in diffs
  - Gracefully returns empty list on any exception (git not available, file not in repo, invalid path, etc.)

  **Edge cases:**
  - Function name not found in file: git returns empty output, function returns []
  - File not tracked by git: git command fails, exception caught, returns []
  - Malformed commit header (fewer than 4 pipe-delimited parts): header skipped, diff lines discarded
  - Non-UTF8 characters in diff: decoded with errors="ignore", lossy but non-fatal
  - No commits in history: returns []
  - Uncommitted changes: not included (git log only shows committed history)
    deps:
      calls:
        - commits.append
        - decode
        - diff_lines.append
        - join
        - len
        - line.split
        - line.startswith
        - out.splitlines
        - subprocess.check_output
      imports:
        - __future__.annotations
        - agentspec.langs.LanguageRegistry
        - ast
        - difflib
        - pathlib.Path
        - re
        - subprocess
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Tuple


why: |
  This function enables automated documentation generation by extracting the evolution of a specific function.
  Using `git log -L` is the most precise method to track function-level changes rather than file-level history,
  avoiding noise from unrelated modifications in the same file. The custom delimiter parsing allows robust
  separation of structured metadata (hash/date/message) from unstructured diff content. Silent exception handling
  ensures the documentation pipeline continues even in non-git environments or edge cases, with graceful degradation
  to an empty changelog rather than pipeline failure.

guardrails:
  - DO NOT assume git is installed or the file is in a git repository; always catch exceptions and return [] to prevent pipeline crashes
  - DO NOT parse commit metadata by line count or position; use the explicit "COMMIT_START|||" delimiter to handle variable-length messages and diffs
  - DO NOT strip or normalize diff content; preserve raw output to maintain patch fidelity for downstream consumers
  - DO NOT increase the commit limit (-n5) without considering performance impact on large histories; current limit balances recency with query speed
  - DO NOT assume func_name exactly matches the git function signature; git's -L heuristic may fail on complex nested functions or lambdas

    changelog:
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
      - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
```

---

## _extract_function_source_without_docstring

**Location:** `/Users/davidmontgomery/agentspec/agentspec/collect.py:744`

### Raw YAML Block

```yaml
what: |
  Extracts the source code of a named function while removing its docstring and comment-only lines.

  Takes a source code string and function name, parses it into an AST, locates the matching function definition (sync or async), and returns the function source with:
  - Leading docstring removed (if present as first statement)
  - All pure comment-only lines stripped
  - Indentation preserved for remaining code lines

  Inputs:
    - src: Complete Python source code as string
    - func_name: Name of function to extract

  Outputs:
    - String containing function definition and body without docstring/comments
    - Empty string if function not found or parsing fails

  Edge cases:
    - Handles both ast.Constant (Python 3.8+) and legacy ast.Str docstring representations
    - Gracefully returns empty string on any parse/extraction exception
    - Correctly maps absolute line numbers to relative slice indices when removing docstring
    - Preserves original indentation of remaining lines
    - Handles functions with no docstring (no-op removal)
    - Handles async function definitions identically to sync functions
    deps:
      calls:
        - ast.parse
        - ast.walk
        - cleaned.append
        - getattr
        - hasattr
        - isinstance
        - join
        - ln.lstrip
        - max
        - src.split
        - stripped.startswith
      imports:
        - __future__.annotations
        - agentspec.langs.LanguageRegistry
        - ast
        - difflib
        - pathlib.Path
        - re
        - subprocess
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Tuple


why: |
  This function supports code introspection workflows where docstrings and comments need to be excluded from analysis or serialization. The dual AST node type handling (ast.Constant and ast.Str) ensures compatibility across Python versions. Exception suppression with empty string fallback prevents crashes during exploratory code analysis. Line-by-line comment filtering is simpler and more reliable than regex-based approaches for preserving code structure.

guardrails:
  - DO NOT assume docstring is always present—check body existence and first statement type before removal to avoid index errors
  - DO NOT use only ast.Constant for docstring detection—legacy Python versions use ast.Str, requiring dual-path checking
  - DO NOT rely on relative line numbers without mapping to absolute indices—off-by-one errors occur when slicing extracted function lines
  - DO NOT strip lines that contain code followed by comments—only remove lines that are pure comments (after lstrip, start with #)
  - DO NOT raise exceptions on malformed source—catch all exceptions and return empty string to allow graceful degradation in batch processing

    changelog:
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
      - "- 2025-10-30: feat: enhance CLI help and add rich formatting support (cb3873d)"
```

---

## collect_function_code_diffs

**Location:** `/Users/davidmontgomery/agentspec/agentspec/collect.py:856`

### Raw YAML Block

```yaml
what: |
  Collects git commit history for a specific file and extracts code-level diffs for a named function across recent commits.

  Inputs:
    - filepath: Path object pointing to a Python source file
    - func_name: String name of the function to track
    - limit: Maximum number of recent commits to inspect (default 5)

  Outputs:
    - List of dictionaries, each containing:
      - date: Commit date in YYYY-MM-DD format
      - message: Commit message
      - hash: 7-character short commit hash
      - diff: Unified diff showing only added/removed code lines (excluding headers and context)

  Behavior:
    1. Queries git log for the N most recent commits touching the file
    2. For each commit, retrieves the function source at that commit and its parent
    3. Extracts function bodies (excluding docstrings) using _extract_function_source_without_docstring
    4. Computes unified diff between parent and current versions
    5. Filters diff output to include only +/- lines, excluding:
       - File/hunk headers (+++, ---, @@)
       - Context lines (leading space)
       - Comment-only changes (lines containing only whitespace and # after the +/-)
    6. Skips commits where the function did not exist in either version or had no code changes
    7. Returns empty list on any top-level exception (git command failure, subprocess errors, etc.)

  Edge cases:
    - Function does not exist in current or parent commit: gracefully skipped
    - Commit has no parent (initial commit): prev_src set to empty string
    - File encoding issues: handled via errors="ignore" in decode
    - Malformed git log output: lines with fewer than 3 pipe-separated parts are skipped
    - No code changes detected (only comments changed): commit excluded from results
    deps:
      calls:
        - _extract_function_source_without_docstring
        - changes.append
        - content.lstrip
        - curr_func.splitlines
        - decode
        - difflib.unified_diff
        - dl.startswith
        - int
        - join
        - len
        - line.split
        - ln.strip
        - log_out.splitlines
        - prev_func.splitlines
        - results.append
        - startswith
        - str
        - subprocess.check_output
      imports:
        - __future__.annotations
        - agentspec.langs.LanguageRegistry
        - ast
        - difflib
        - pathlib.Path
        - re
        - subprocess
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Tuple


why: |
  This function enables historical analysis of function-level changes without requiring full file diffs, reducing noise and focusing on semantic code modifications. By filtering comment-only changes, it avoids cluttering results with documentation updates. The git-based approach leverages existing repository history rather than external APIs or databases. Graceful error handling ensures robustness in environments with incomplete git history or encoding anomalies. The limit parameter allows tuning between comprehensiveness and performance.

guardrails:
  - DO NOT include comment-only changes in diffs; they obscure actual code evolution and inflate result size
  - DO NOT fail the entire operation on individual commit retrieval errors; use try-except per commit to maximize partial results
  - DO NOT assume function exists in all commits; absence in both versions is a valid skip condition
  - DO NOT parse git output without validating field count; malformed lines can cause index errors
  - DO NOT expose raw subprocess exceptions to caller; wrap in empty list return to maintain consistent interface
  - DO NOT include file/hunk headers or context lines in diff output; they add no semantic value for function-level tracking

    changelog:
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
      - "- 2025-10-30: feat: enhance CLI help and add rich formatting support (cb3873d)"
```

---

## collect_metadata

**Location:** `/Users/davidmontgomery/agentspec/agentspec/collect.py:1024`

### Raw YAML Block

```yaml
what: |
  Collects metadata about a function across multiple dimensions: dependency calls, module imports, and git changelog history.

  Accepts a filepath (string or Path object) and function name, then routes to language-specific collectors based on file extension.

  For JavaScript/TypeScript files (.js, .mjs, .jsx, .ts, .tsx): delegates to _collect_javascript_metadata(), extracting calls, imports, and changelog from the result structure.

  For Python files: calls _collect_python_deps() to extract function calls and imports, then _collect_git_changelog() to retrieve commit history for that function.

  Returns a dictionary with structure: {"deps": {"calls": [...], "imports": [...]}, "changelog": [...]}.

  Prints diagnostic output with [AGENTSPEC_METADATA] prefix showing function name, file path, call count, import count, and first 3 changelog entries.

  Returns empty dict {} if language-specific collection returns falsy value (None, empty dict, etc.).

  Edge cases: handles mixed case file extensions via .lower(), gracefully degrades when no metadata found, normalizes Path objects.
    deps:
      calls:
        - Path
        - _collect_git_changelog
        - _collect_javascript_metadata
        - _collect_python_deps
        - get
        - join
        - js_result.get
        - len
        - print
        - suffix.lower
      imports:
        - __future__.annotations
        - agentspec.langs.LanguageRegistry
        - ast
        - difflib
        - pathlib.Path
        - re
        - subprocess
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Tuple


why: |
  Centralizes metadata collection across heterogeneous codebases (Python + JavaScript/TypeScript) under a single interface, enabling unified dependency analysis and change tracking.

  Language-specific routing avoids forcing incompatible parsing logic; each language collector handles its own AST/syntax requirements.

  Structured output (deps + changelog) supports both static analysis (what does this function call?) and temporal analysis (how has it changed?), useful for impact analysis and documentation generation.

  Diagnostic printing aids debugging and provides visibility into collection success/failure without requiring external logging infrastructure.

  Early return on empty results prevents downstream processing of incomplete metadata.

guardrails:
  - DO NOT assume file extension case consistency; always normalize via .lower() before comparison to handle .JS, .Js, etc.
  - DO NOT mix language-specific result structures; ensure JavaScript and Python paths both normalize to identical output schema before returning.
  - DO NOT print sensitive information in diagnostic output; changelog entries may contain commit messages with credentials or internal details.
  - DO NOT silently fail on malformed paths; Path() constructor should validate but caller should handle non-existent files explicitly.
  - DO NOT assume function exists in file; language collectors must handle missing function gracefully and return empty/falsy rather than raising.
  - DO NOT return partial results; if any collection step fails, return {} rather than incomplete deps or missing changelog to prevent downstream assumptions.

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
      - "- 2025-10-30: feat: enhance CLI help and add rich formatting support (cb3873d)"
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

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:23`

### What This Does

Lazy-loads and returns singleton Anthropic client. Calls `load_env_from_dotenv()` to populate environment, then imports `Anthropic` class and instantiates with `Anthropic()` (reads ANTHROPIC_API_KEY from env automatically).

Inputs: None
Outputs: anthropic.Anthropic instance

Edge cases:
- Missing ANTHROPIC_API_KEY: Anthropic() raises auth error
- Missing .env: load_env_from_dotenv() handles gracefully
- anthropic package not installed: ImportError on lazy import
  deps:
    calls:
      - Anthropic
      - load_env_from_dotenv
    imports:
      - agentspec.collect.collect_metadata
      - agentspec.prompts.get_agentspec_yaml_prompt
      - agentspec.prompts.get_terse_docstring_prompt
      - agentspec.prompts.get_verbose_docstring_prompt
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

Lazy import defers dependency load until needed, reducing startup time. Loading .env before instantiation ensures credentials available for both env vars and .env files. Centralizes client creation for easier auth management and implementation swaps.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT call in tight loops; client creation is expensive, cache result**
- **DO NOT assume ANTHROPIC_API_KEY exists; handle Anthropic() auth errors gracefully**
- **DO NOT hardcode API keys; use environment variables only**
- **DO NOT remove load_env_from_dotenv() call; required for .env support**
- **{'NOTE': 'This function is called at module load time; if it fails, entire module fails to import'}**
- **{'NOTE': 'This is production auth client; test credential loading before deploying', 'changelog': ['- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)', '- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)', '- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)', '- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)', '- 2025-10-30: feat: robust docstring generation and Haiku defaults (e428337)']}**

### Raw YAML Block

```yaml
what: |
  Lazy-loads and returns singleton Anthropic client. Calls `load_env_from_dotenv()` to populate environment, then imports `Anthropic` class and instantiates with `Anthropic()` (reads ANTHROPIC_API_KEY from env automatically).

  Inputs: None
  Outputs: anthropic.Anthropic instance

  Edge cases:
  - Missing ANTHROPIC_API_KEY: Anthropic() raises auth error
  - Missing .env: load_env_from_dotenv() handles gracefully
  - anthropic package not installed: ImportError on lazy import
    deps:
      calls:
        - Anthropic
        - load_env_from_dotenv
      imports:
        - agentspec.collect.collect_metadata
        - agentspec.prompts.get_agentspec_yaml_prompt
        - agentspec.prompts.get_terse_docstring_prompt
        - agentspec.prompts.get_verbose_docstring_prompt
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
  Lazy import defers dependency load until needed, reducing startup time. Loading .env before instantiation ensures credentials available for both env vars and .env files. Centralizes client creation for easier auth management and implementation swaps.

guardrails:
  - DO NOT call in tight loops; client creation is expensive, cache result
  - DO NOT assume ANTHROPIC_API_KEY exists; handle Anthropic() auth errors gracefully
  - DO NOT hardcode API keys; use environment variables only
  - DO NOT remove load_env_from_dotenv() call; required for .env support
  - NOTE: This function is called at module load time; if it fails, entire module fails to import
  - NOTE: This is production auth client; test credential loading before deploying

    changelog:
      - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
      - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
      - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
      - "- 2025-10-30: feat: robust docstring generation and Haiku defaults (e428337)"
```

---

## extract_function_info

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:87`

### What This Does

Parses Python files to find functions needing docstrings. Flags functions based on `require_agentspec` and `update_existing` flags. Returns list of `(line_number, function_name, source_code)` tuples sorted descending by line number.

AI SLOP DETECTED:
- Docstring contains hallucinated dependencies and imports
- Changelog entries are not part of the function's actual behavior
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
      - agentspec.prompts.get_agentspec_yaml_prompt
      - agentspec.prompts.get_terse_docstring_prompt
      - agentspec.prompts.get_verbose_docstring_prompt
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

Descending line sort prevents line-number drift during batch docstring insertion. When docstrings are prepended to functions, earlier insertions shift all subsequent line numbers downward; processing bottom-to-top preserves cached line validity. Dual-mode checking (agentspec-strict vs. general-quality) supports flexible workflows: strict enforces agentspec compliance, lenient targets underdocumented code. `update_existing` flag enables regeneration without re-parsing, supporting iterative refinement.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT rely on returned line numbers after any source modification; re-parse to get fresh coordinates**
- **DO NOT call on files with syntax errors; `ast.parse()` raises `SyntaxError` and halts**
- **DO NOT assume docstring presence = quality; `require_agentspec=False` skips minimal/placeholder docstrings silently**
- **DO NOT process extremely large files without memory budget; `ast.walk()` traverses entire tree, source held in RAM**
- **DO NOT combine `update_existing=True` with `require_agentspec=True`; `update_existing` bypasses all skip logic, rendering `require_agentspec` ineffective**
- **ALWAYS re-parse after docstring insertion before calling this function again on modified source**
- **{'NOTE': 'This function is only safe for well-formed Python source files', 'changelog': ['- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)', '- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)', '- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)', '- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)', '- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate (172e0a7)']}**

### Raw YAML Block

```yaml
what: |
  Parses Python files to find functions needing docstrings. Flags functions based on `require_agentspec` and `update_existing` flags. Returns list of `(line_number, function_name, source_code)` tuples sorted descending by line number.

  AI SLOP DETECTED:
  - Docstring contains hallucinated dependencies and imports
  - Changelog entries are not part of the function's actual behavior
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
        - agentspec.prompts.get_agentspec_yaml_prompt
        - agentspec.prompts.get_terse_docstring_prompt
        - agentspec.prompts.get_verbose_docstring_prompt
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
  Descending line sort prevents line-number drift during batch docstring insertion. When docstrings are prepended to functions, earlier insertions shift all subsequent line numbers downward; processing bottom-to-top preserves cached line validity. Dual-mode checking (agentspec-strict vs. general-quality) supports flexible workflows: strict enforces agentspec compliance, lenient targets underdocumented code. `update_existing` flag enables regeneration without re-parsing, supporting iterative refinement.

guardrails:
  - DO NOT rely on returned line numbers after any source modification; re-parse to get fresh coordinates
  - DO NOT call on files with syntax errors; `ast.parse()` raises `SyntaxError` and halts
  - DO NOT assume docstring presence = quality; `require_agentspec=False` skips minimal/placeholder docstrings silently
  - DO NOT process extremely large files without memory budget; `ast.walk()` traverses entire tree, source held in RAM
  - DO NOT combine `update_existing=True` with `require_agentspec=True`; `update_existing` bypasses all skip logic, rendering `require_agentspec` ineffective
  - ALWAYS re-parse after docstring insertion before calling this function again on modified source
  - NOTE: This function is only safe for well-formed Python source files

    changelog:
      - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
      - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
      - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
      - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate (172e0a7)"
```

---

## inject_deterministic_metadata

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:181`

### Raw YAML Block

```yaml
` block)
  - Plain text (appended at the end)

### Parameters:
| Parameter | Type | Description |
|----------|------|-------------|
| `llm_output` | `str` | The raw LLM-generated documentation string |
| `metadata` | `Dict[str, Any]` | Dictionary containing `deps` and `changelog` |
| `as_agentspec_yaml` | `bool` | Whether to inject into an `---agentspec` YAML block |
| `diff_summary_lines` | `list[str] | None` | Optional list of diff summary lines to append after changelog |

---

## 🧠 Key Design Decisions

### 1. **Separation of Concerns**
You explicitly avoid modifying narrative content (`what`, `why`, `guardrails`) and only touch metadata sections.

### 2. **Forceful Replacement**
You **never conditionally inject or merge** metadata — always **replace** existing sections with deterministic ones.

### 3. **Callable Replacements in `re.sub`**
This prevents issues like:
```python
# Bad:
re.sub(r'foo', '\u0041', text)  # Escapes interpreted as Unicode

# Good:
re.sub(r'foo', lambda m: '\u0041', text)
```

### 4. **Robust Regex Boundaries**
You use:
- `(?ms)` flags for multiline and dotall matching.
-
```yaml
---agentspec
what: |
  Authenticates user via bcrypt; validates password hash.
  AI SLOP DETECTED:
  - Stub implementation returns True unconditionally
  - Bypasses real credential checks
    deps:
      calls:
        - _tw.fill
        - _wrap_bullet
        - deps_data.get
        - join
        - len
        - llm_output.endswith
        - m.group
        - metadata.get
        - output.rfind
        - print
        - re.sub
        - strip
        - wrapped.splitlines
      imports:
        - agentspec.collect.collect_metadata
        - agentspec.prompts.get_agentspec_yaml_prompt
        - agentspec.prompts.get_terse_docstring_prompt
        - agentspec.prompts.get_verbose_docstring_prompt
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
  Uses bcrypt for secure password hashing; prevents timing attacks.
  This approach avoids plain text storage and supports secure credential validation.

guardrails:
  - DO NOT remove bcrypt validation; prevents rainbow table attacks
  - ALWAYS validate user exists before checking password
  - NOTE: This is production auth; test thoroughly before changes

    changelog:
      - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
      - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
      - "- 2025-10-30: fix(changelog): aggressively strip any LLM-emitted CHANGELOG/DEPENDENCIES sections and append deterministic ones with hashes (646ff28)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
      - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
    diff_summary:
      - >-
        2025-11-01: refactor: Extract system prompts to separate .md files for easier
        editing (136cb30): Diff Summary: - Refactored string replacement operations to
        use lambda functions for more flexible pattern matching - Replaced direct string
        concatenation with lambda-based transformations for dependency YAML handling -
        Updated changelog YAML processing to use lambda function for stripping
        whitespace - Changed from simple regex replacement to more dynamic lambda-based
        replacement logic - Modified dependency handling to use group-based string
        manipulation instead of direct concatenation
```

---

## _wrap_bullet

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:334`

### What This Does

Converts text into YAML bullet list format with intelligent line wrapping.
Short text (≤76 chars): Returns quoted single-line item `"- "text""`
Long text: Uses folded block scalar `- >-` with wrapped lines indented to content_indent.

AI SLOP DETECTED:
- Inconsistent max_width usage in length check
- No validation of bullet_indent/content_indent constraints
  deps:
    calls:
      - _tw.fill
      - join
      - len
      - wrapped.splitlines
    imports:
      - agentspec.collect.collect_metadata
      - agentspec.prompts.get_agentspec_yaml_prompt
      - agentspec.prompts.get_terse_docstring_prompt
      - agentspec.prompts.get_verbose_docstring_prompt
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

Uses folded scalars (`>-`) to preserve semantic line breaks while avoiding
excessive quoting in YAML. Prevents malformed YAML when text contains colons,
quotes, or newlines. textwrap.fill() respects max_width for consistent formatting.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT change bullet_indent/content_indent without updating AgentSpec parser; breaks alignment**
- **DO NOT remove textwrap import; function depends on it**
- **ALWAYS validate max_width >= content_indent + 10; prevents infinite loop on short widths**
- **{'NOTE': 'Folded block scalar (`>-`) strips trailing newlines; use `|-` if trailing whitespace required', 'changelog': ['- 2025-11-03: feat: Enhance prompt generation with terse option and adjust output token base (f533292)', '- 2025-11-03: fix: CRITICAL - Include FULL examples in prompts, not just IDs (8f1beb3)', '- 2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help, create safety system (72bbaf5)', '- 2025-11-02: feat: updated test and new prompt and examples structure , added new responses api params CFG and FFC (a86e643)', '- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)']}**

### Raw YAML Block

```yaml
what: |
  Converts text into YAML bullet list format with intelligent line wrapping.
  Short text (≤76 chars): Returns quoted single-line item `"- "text""`
  Long text: Uses folded block scalar `- >-` with wrapped lines indented to content_indent.

  AI SLOP DETECTED:
  - Inconsistent max_width usage in length check
  - No validation of bullet_indent/content_indent constraints
    deps:
      calls:
        - _tw.fill
        - join
        - len
        - wrapped.splitlines
      imports:
        - agentspec.collect.collect_metadata
        - agentspec.prompts.get_agentspec_yaml_prompt
        - agentspec.prompts.get_terse_docstring_prompt
        - agentspec.prompts.get_verbose_docstring_prompt
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
  Uses folded scalars (`>-`) to preserve semantic line breaks while avoiding
  excessive quoting in YAML. Prevents malformed YAML when text contains colons,
  quotes, or newlines. textwrap.fill() respects max_width for consistent formatting.

guardrails:
  - DO NOT change bullet_indent/content_indent without updating AgentSpec parser; breaks alignment
  - DO NOT remove textwrap import; function depends on it
  - ALWAYS validate max_width >= content_indent + 10; prevents infinite loop on short widths
  - NOTE: Folded block scalar (`>-`) strips trailing newlines; use `|-` if trailing whitespace required

    changelog:
      - "- 2025-11-03: feat: Enhance prompt generation with terse option and adjust output token base (f533292)"
      - "- 2025-11-03: fix: CRITICAL - Include FULL examples in prompts, not just IDs (8f1beb3)"
      - "- 2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help, create safety system (72bbaf5)"
      - "- 2025-11-02: feat: updated test and new prompt and examples structure , added new responses api params CFG and FFC (a86e643)"
      - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
```

---

## strip_js_agentspec_blocks

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:494`

### Raw YAML Block

```yaml
` or related markers.
    - Preserve file line endings and non-matching JSDoc.
    - Handle malformed blocks gracefully.
    - Support dry-run mode for previewing changes.
    - Be efficient and safe for batch operations.

    Here’s a **review and analysis** of your implementation, followed by **suggestions for improvement or clarification**.

    ---

    ## ✅ **Strengths**

    ### 1. **Clear Logic Flow**
    The logic is easy to follow:
    - Read file as text.
    - Iterate line-by-line.
    - Detect JSDoc start (`/**`) and collect until end (`*/`).
    - Check if the block contains agentspec markers.
    - If yes, skip it; otherwise, keep it.
    - Write back only if not in dry-run mode.

    ### 2. **Robustness**
    - Handles malformed blocks (missing `*/`) by preserving them.
    - Uses `errors="ignore"` in `read_text()` but catches exceptions — good for batch processing.
    - Preserves exact line endings and whitespace.
    - Dry-run mode allows safe preview.

    ### 3. **Efficiency**
    - Line-by-line processing avoids full YAML parsing overhead.
    - Uses `any(m in content for m in markers)` — fast substring search.
    - No unnecessary memory allocations or complex state machines.

    ### 4. **Documentation**
    - Inline docstrings are detailed and include AI SLOP DETECTED, WHY, and GUARDRAILS sections.
    - These are helpful for understanding intent and preventing misuse.

    ---

    ## 🔍 **Suggestions for Improvement**

    ### 1. **Improve `is_agentspec_block` Logic**
    Currently, it checks if any of the 5 markers are present in the joined block content.

    #### Suggestion:
    Use a more precise check to avoid false positives:
    ```python
    def is_agentspec_block(block_lines: list[str]) -> bool:
        content = "
".join(block_lines)
        # Match only full lines that contain markers
        for line in block_lines:
            if any(marker in line for marker in [
                "---agentspec",
                "
```

---

## is_agentspec_block

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:634`

### What This Does

Checks if a list of lines contains any of five agentspec markers. Returns True if any marker found, False otherwise.
AI SLOP DETECTED:
- Docstring is bloated with irrelevant metadata (deps, changelog, diff_summary)
- Lists non-existent imports not used in function
- Claims "no validation" which is obvious from code
- Over-explains behavior already clear from function name and logic
  deps:
    calls:
      - any
      - join
    imports:
      - agentspec.collect.collect_metadata
      - agentspec.prompts.get_agentspec_yaml_prompt
      - agentspec.prompts.get_terse_docstring_prompt
      - agentspec.prompts.get_verbose_docstring_prompt
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

Uses fast O(n) substring search to detect agentspec blocks before full parsing. Markers are chosen to avoid false positives in regular text. Designed for preprocessing, not validation.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT use for agentspec validation; only detects presence, not structure**
- **DO NOT assume marker presence = complete block; missing closing fence passes**
- **DO NOT rely on this for security; markers in comments/strings cause false positives**
- **DO NOT call on huge lists without memory consideration; use incremental check for streaming**
- **{'ALWAYS replace docstring with 1-line comment': '# Fast heuristic: check for agentspec markers in joined lines.', 'changelog': ['- 2025-11-03: feat: Enhance prompt generation with terse option and adjust output token base (f533292)', '- 2025-11-03: fix: CRITICAL - Include FULL examples in prompts, not just IDs (8f1beb3)', '- 2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help, create safety system (72bbaf5)', '- 2025-11-02: feat: updated test and new prompt and examples structure , added new responses api params CFG and FFC (a86e643)', '- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)'], 'diff_summary': ['2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30): Diff Summary: - Added new function `is_agentspec_block` to identify agentspec-related blocks using defined markers - Function accepts list of strings and returns boolean indicating block type - Uses string containment checks against multiple markers including agentspec delimiters and context indicators - No behavioral changes to existing codebase beyond new utility function - Function designed to support extraction of system prompts to separate markdown files']}**

### Raw YAML Block

```yaml
what: |
  Checks if a list of lines contains any of five agentspec markers. Returns True if any marker found, False otherwise.
  AI SLOP DETECTED:
  - Docstring is bloated with irrelevant metadata (deps, changelog, diff_summary)
  - Lists non-existent imports not used in function
  - Claims "no validation" which is obvious from code
  - Over-explains behavior already clear from function name and logic
    deps:
      calls:
        - any
        - join
      imports:
        - agentspec.collect.collect_metadata
        - agentspec.prompts.get_agentspec_yaml_prompt
        - agentspec.prompts.get_terse_docstring_prompt
        - agentspec.prompts.get_verbose_docstring_prompt
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
  Uses fast O(n) substring search to detect agentspec blocks before full parsing. Markers are chosen to avoid false positives in regular text. Designed for preprocessing, not validation.

guardrails:
  - DO NOT use for agentspec validation; only detects presence, not structure
  - DO NOT assume marker presence = complete block; missing closing fence passes
  - DO NOT rely on this for security; markers in comments/strings cause false positives
  - DO NOT call on huge lists without memory consideration; use incremental check for streaming
  - ALWAYS replace docstring with 1-line comment: "# Fast heuristic: check for agentspec markers in joined lines."

    changelog:
      - "- 2025-11-03: feat: Enhance prompt generation with terse option and adjust output token base (f533292)"
      - "- 2025-11-03: fix: CRITICAL - Include FULL examples in prompts, not just IDs (8f1beb3)"
      - "- 2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help, create safety system (72bbaf5)"
      - "- 2025-11-02: feat: updated test and new prompt and examples structure , added new responses api params CFG and FFC (a86e643)"
      - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
    diff_summary:
      - >-
        2025-11-01: refactor: Extract system prompts to separate .md files for easier
        editing (136cb30): Diff Summary: - Added new function `is_agentspec_block` to
        identify agentspec-related blocks using defined markers - Function accepts list
        of strings and returns boolean indicating block type - Uses string containment
        checks against multiple markers including agentspec delimiters and context
        indicators - No behavioral changes to existing codebase beyond new utility
        function - Function designed to support extraction of system prompts to separate
        markdown files
```

---

## generate_docstring

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:743`

### Raw YAML Block

```yaml
...
```

---

## _estimate_tokens

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:915`

### Raw YAML Block

```yaml
what: |
  Estimates token count via character heuristic: `max(1, len(s) // 4)`.
  Assumes ~4 chars per token. Returns minimum 1 token (prevents zero-token edge case).
  Bare `except Exception` swallows all errors and returns 1; masks bugs silently.

  AI SLOP DETECTED:
  - Bare `except Exception` catches and hides real errors (AttributeError, TypeError, etc.)
  - No logging; silent failures make debugging impossible in production
  - Heuristic accuracy unknown; no validation against actual tokenizer
    deps:
      calls:
        - len
        - max
      imports:
        - agentspec.collect.collect_metadata
        - agentspec.prompts.get_agentspec_yaml_prompt
        - agentspec.prompts.get_terse_docstring_prompt
        - agentspec.prompts.get_verbose_docstring_prompt
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
  Character-based heuristic avoids expensive tokenizer calls for quick budgeting.
  However, bare exception handler is defensive programming anti-pattern; it hides bugs
  instead of surfacing them. Should catch only `TypeError` (non-string input) explicitly.
  The 4-char assumption is reasonable for English but untested against actual token distributions.

guardrails:
  - DO NOT remove `max(1, ...)` floor; breaks downstream token accounting if zero returned
  - DO NOT catch bare `Exception`; replace with explicit `TypeError` only
  - ALWAYS log exceptions before returning fallback; silent failures hide bugs
  - NOTE: This is a heuristic, not ground truth; validate against `tiktoken` or model tokenizer in tests
  - ASK USER: Should this call actual tokenizer for accuracy, or is speed critical?

security:
  denial_of_service:
    - Unbounded string input could consume memory during len() call
    - Exploit: Pass multi-GB string; len() allocates full buffer
    - Impact: Agent process OOM; service unavailable

    changelog:
      - "- 2025-11-03: feat: Enhance prompt generation with terse option and adjust output token base (f533292)"
      - "- 2025-11-03: fix: CRITICAL - Include FULL examples in prompts, not just IDs (8f1beb3)"
      - "- 2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help, create safety system (72bbaf5)"
      - "- 2025-11-02: feat: updated test and new prompt and examples structure , added new responses api params CFG and FFC (a86e643)"
      - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
    diff_summary:
      - >-
        2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help,
        create safety system (72bbaf5): Diff Summary: - Added exception handling to
        return 1 token estimate if string length calculation fails, preventing potential
        crashes during token estimation
      - >-
        2025-11-01: refactor: Extract system prompts to separate .md files for easier
        editing (136cb30): Diff Summary: - Replaced previous token estimation logic with
        a simple heuristic calculating tokens as length divided by 4, with a minimum
        value of 1 - No meaningful changes found.
```

---

## _yaml_complete

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:995`

### What This Does

Checks if text contains both "---agentspec" and "

### Raw YAML Block

```yaml
what: |
  Checks if text contains both "---agentspec" and "
```

---

## _yaml_has_core_sections

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:1070`

### What This Does

Validates YAML contains required sections: `what: |`, `why: |`, `guardrails:`.
Uses regex with multiline anchors to check section headers.
Returns True only if all three present; False otherwise.

AI SLOP DETECTED:
- Regex checks structure only, not content quality
- Does not validate `---agentspec` delimiters or closing `

### Raw YAML Block

```yaml
what: |
  Validates YAML contains required sections: `what: |`, `why: |`, `guardrails:`.
  Uses regex with multiline anchors to check section headers.
  Returns True only if all three present; False otherwise.

  AI SLOP DETECTED:
  - Regex checks structure only, not content quality
  - Does not validate `---agentspec` delimiters or closing `
```

---

## _call_llm

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:1203`

### Raw YAML Block

```yaml
what: |
  Calls `generate_chat()` with adaptive reasoning/verbosity based on code complexity and `terse` flag.
  Sets `reasoning_effort='minimal'` if terse OR code ≤12 lines; else None.
  Sets `verbosity='low'` if terse, else 'medium'.
  Temperature 0.0 if terse, else 0.2.
  Passes `grammar_lark` only if `as_agentspec_yaml=True`.

  AI SLOP DETECTED:
  - Function signature declares only `user_content` and `max_tokens`; implementation uses 9 undefined variables: `code`, `model`, `system_text`, `base_url`, `provider`, `grammar_lark`, `as_agentspec_yaml`, `terse`, `max_out`.
  - Will crash immediately with NameError on first call.
  - Diff history shows `max_tokens` renamed to `max_out` in implementation but signature never updated.
  - Docstring YAML is incomplete stub; deps/changelog listed but not integrated into function logic.
    deps:
      calls:
        - code.splitlines
        - generate_chat
        - len
      imports:
        - agentspec.collect.collect_metadata
        - agentspec.prompts.get_agentspec_yaml_prompt
        - agentspec.prompts.get_terse_docstring_prompt
        - agentspec.prompts.get_verbose_docstring_prompt
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
  Scales reasoning effort by code complexity heuristic: short code (≤12 lines) uses minimal reasoning to avoid over-analysis.
  Temperature tuning: 0.0 for deterministic terse docs; 0.2 for slight variance in normal mode.
  Grammar constraint only for YAML output (prevents hallucinated keys).

  CRITICAL: This is non-functional. Missing all variable definitions. Diff shows parameters were renamed but function signature was never updated. Requires full dependency injection before use.

guardrails:
  - DO NOT call this function; will crash with NameError on undefined `code`, `model`, `system_text`, `base_url`, `provider`, `grammar_lark`, `as_agentspec_yaml`, `terse`, `max_out`.
  - ALWAYS add all 9 undefined variables as function parameters or inject via dependency container before any edit.
  - ALWAYS update function signature to match implementation (currently declares 2 params, uses 11).
  - DO NOT edit this function until all dependencies are properly injected and signature is updated.
  - DO NOT assume `code` or `terse` are defined; they must be passed in or loaded from context.
  - DO NOT assume `max_out` is an alias for `max_tokens`; function signature must reflect actual parameter names used.
---
```yaml
---agentspec
what: |
  Authenticates user via bcrypt; validates password hash.
  AI SLOP DETECTED:
  - Stub implementation returns True unconditionally
  - Bypasses real credential checks

why: |
  Uses bcrypt for secure password hashing; prevents timing attacks.
  This approach avoids plain text storage and supports secure credential validation.

guardrails:
  - DO NOT remove bcrypt validation; prevents rainbow table attacks
  - ALWAYS validate user exists before checking password
  - NOTE: This is production auth; test thoroughly before changes

    changelog:
      - "- 2025-11-03: feat: Enhance prompt generation with terse option and adjust output token base (f533292)"
      - "- 2025-11-03: fix: CRITICAL - Include FULL examples in prompts, not just IDs (8f1beb3)"
      - "- 2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help, create safety system (72bbaf5)"
      - "- 2025-11-02: feat: updated test and new prompt and examples structure , added new responses api params CFG and FFC (a86e643)"
      - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
    diff_summary:
      - >-
        2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help,
        create safety system (72bbaf5): Diff Summary: - Replaced fixed system prompt
        with dynamic `system_text` variable - Renamed `max_tokens` parameter to
        `max_out` for clarity - Added conditional `grammar_lark` parameter based on
        `as_agentspec_yaml` flag - No other functional changes to `_call_llm` behavior
        or contract
      - >-
        2025-11-02: feat: updated test and new prompt and examples structure , added new
        responses api params CFG and FFC (a86e643): Diff Summary: - Added logic to
        calculate code line count and set effort level based on code length and terse
        flag - Introduced verbosity setting based on terse flag with 'low' or 'medium'
        values - Included new reasoning_effort and verbosity parameters in LLM call -
        Implemented error handling for code line counting with default to 0 - Added
        conditional effort calculation using 'minimal' for
      - >-
        2025-11-01: refactor: Extract system prompts to separate .md files for easier
        editing (136cb30): Diff Summary: - Refactored _call_llm to extract system prompt
        into a separate .md file for easier maintenance - Changed function signature to
        accept user_content and max_tokens parameters - Updated system prompt to focus
        on generating only narrative sections without deps or changelog - Modified
        temperature setting to use terse variable for conditional behavior - Added
        base_url and provider parameters to the generate_chat call
```

---

## insert_docstring_at_line

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:1419`

### What This Does

```yaml
---agentspec
what: |
  Inserts or replaces a Python function docstring at a specified file location.

### Raw YAML Block

```yaml
```yaml
---agentspec
what: |
  Inserts or replaces a Python function docstring at a specified file location.

  **Inputs:** filepath, lineno (1-based), func_name, docstring (string), force_context (bool)
  **Output:** True if written; False if syntax validation failed.

  **Core flow:**
  1. Locates function via regex on `func_name`, falls back to `lineno`
  2. Uses AST to find function node and first statement (handles decorators, multi-line signatures)
  3. Detects existing docstring via AST node boundaries; deletes using 1-based→0-based index conversion
  4. Removes trailing `[AGENTSPEC_CONTEXT]` print if present
  5. Selects delimiter (`"""` or `'''`) based on content; escapes conflicting quotes
  6. Formats new docstring with proper indentation
  7. If `force_context=True`, extracts up to 3 bullet points and appends print statement
  8. **Compile-tests candidate on temp file before writing** (prevents corrupting source on syntax error)
  9. Writes only if compilation succeeds

  **Edge cases:** Multi-line signatures (AST handles), existing docstrings (deleted via AST end_lineno), docstring contains delimiters (escaped or switched), AST parse failure (falls back to textual scan), empty function body (inserts after def line).
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
        - agentspec.prompts.get_agentspec_yaml_prompt
        - agentspec.prompts.get_terse_docstring_prompt
        - agentspec.prompts.get_verbose_docstring_prompt
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
  AST-based approach is essential: regex/textual scanning fails on decorators, type hints, multi-line signatures. Python's `ast` module reports 1-based line numbers (editor convention), but Python lists are 0-indexed—the 1-based→0-based conversion (`docstring_start_line - 1`) is critical to avoid off-by-one deletion of wrong lines.

  Compile-testing before write prevents corrupting source on syntax errors (e.g., unescaped quotes in docstring). Fallback textual scan handles parse failures gracefully.

guardrails:
  - DO NOT remove compile-test; prevents writing broken Python
I'm ready to generate AgentSpec YAML documentation. However, I don't see any code provided yet for me to audit.

Please share the code you'd like me to document, and I'll produce a concise, accurate YAML block following the format and guidelines you've outlined.

**What I need:**
- The code to audit (function, class, module, or file)
- Context (language, purpose, production vs. test)
- Any known issues or concerns (optional)

Once you provide the code, I'll deliver:
1. **what**: Concise description + AI slop detection
2. **why**: Reasoning behind the approach
3. **guardrails**: Specific, actionable constraints for AI agents
4. **security**: Vulnerabilities (if 2+ issues exist)

Ready when you are.
I'm ready to generate AgentSpec YAML documentation. However, I don't see any code provided yet for me to audit.

Please share the code you'd like me to document, and I'll produce a concise, accurate YAML block following the format and guidelines you've outlined.

**What I need:**
- The code to audit (function, class, module, or file)
- Context (language, purpose, production vs. test)
- Any known issues or concerns (optional)

Once you provide the code, I'll deliver:
1. **what**: Concise description + AI slop detection
2. **why**: Reasoning behind the approach
3. **guardrails**: Specific, actionable constraints for AI agents
4. **security**: Vulnerabilities (if 2+ issues exist)

Ready when you are.

    changelog:
      - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
      - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
      - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
      - "- 2025-10-30: feat: robust docstring generation and Haiku defaults (e428337)"
    diff_summary:
      - >-
        2025-11-01: refactor: Extract system prompts to separate .md files for easier
        editing (136cb30): Diff Summary: - Added explicit type annotation (`list[str]`)
        to the `sections` variable for clarity and type-checking.
```

---

## _discover_js_functions

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:1763`

### Raw YAML Block

```yaml
` marker.
4. **Filters candidates** based on flags:
   - `require_agentspec=True`: Only functions with JSDoc but missing `---agentspec`.
   - `update_existing=True`: Includes all functions (even those already documented).
5. **Returns a list of tuples**:
   - `(line_number, function_name, code_snippet)`
   - Sorted in **reverse line order** to support safe insertion of documentation.

---

### 🧠 **Key Design Choices**

| Feature | Description |
|--------|-------------|
| **Reverse Sorting** | Ensures line numbers remain valid when inserting docs sequentially. |
| **20-Line Limit** | Balances performance and coverage; typical JSDoc fits in this window. |
| **Exact `---agentspec` Match** | Prevents false positives from substrings like `---agentspec-old`. |
| **Nested `has_jsdoc()` Helper** | Distinguishes between "no docs" and "docs exist but no agentspec". |
| **Robust Regex Matching** | Handles `export`, `const`, `let`, `var`, and arrow functions. |
| **Error Handling** | Returns empty list on file read errors to avoid pipeline breakage. |

---

### 🛠️ **Potential Improvements**

1. **Regex for Arrow Functions**:
   - The current arrow function regex (`const name = (...) =>`) may not catch all valid cases (e.g., multiline, complex expressions).
   - Consider a more robust pattern or use AST parsing for full accuracy.

2. **Marker Detection Precision**:
   - Sub
```yaml
---agentspec
what: |
  Authenticates user via bcrypt; validates password hash.
  AI SLOP DETECTED:
  - Stub implementation returns True unconditionally
  - Bypasses real credential checks
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
        - print
        - range
        - re.compile
        - s.endswith
        - strip
        - text.splitlines
      imports:
        - agentspec.collect.collect_metadata
        - agentspec.prompts.get_agentspec_yaml_prompt
        - agentspec.prompts.get_terse_docstring_prompt
        - agentspec.prompts.get_verbose_docstring_prompt
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
  Uses bcrypt for secure password hashing; prevents timing attacks.
  This approach avoids plain text storage and supports secure credential validation.

guardrails:
  - DO NOT remove bcrypt validation; prevents rainbow table attacks
  - ALWAYS validate user exists before checking password
  - NOTE: This is production auth; test thoroughly before changes

    changelog:
      - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
    diff_summary:
      - >-
        2025-11-01: refactor: Extract system prompts to separate .md files for easier
        editing (136cb30): Diff Summary: - Refactored `_discover_js_functions` to
        extract system prompts into separate .md files, improving maintainability. -
        Added optional parameters `require_agentspec` and `update_existing` to control
        function discovery behavior. - Implemented regex patterns to detect JavaScript
        function declarations and arrow functions. - Introduced `has_jsdoc` helper to
        identify JSDoc comments and agentspec markers within
```

---

## has_jsdoc

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:1894`

### What This Does

Scans backward up to 20 lines for JSDoc blocks (`/** ... */`) and detects `---agentspec` marker.
Returns (found_jsdoc: bool, has_agentspec_marker: bool).
Logic: First finds `*/`, then looks for `/**` in preceding lines; extracts block and checks for marker.
AI SLOP DETECTED:
- Incomplete JSDoc detection logic
- May miss multi-line JSDoc if `/**` not on same line as `*/`
  deps:
    calls:
      - join
      - max
      - range
      - s.endswith
      - strip
    imports:
      - agentspec.collect.collect_metadata
      - agentspec.prompts.get_agentspec_yaml_prompt
      - agentspec.prompts.get_terse_docstring_prompt
      - agentspec.prompts.get_verbose_docstring_prompt
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

Enables incremental documentation by skipping already-documented functions.
20-line window balances coverage vs. performance; typical JSDoc blocks fit comfortably.
Two-part return allows callers to distinguish "no docs" from "docs exist, needs update."

### ⚠️ Guardrails (CRITICAL)

- **DO NOT search beyond 20 lines; prevents O(n) degradation on large files**
- **DO NOT assume marker is case-insensitive; uses exact string match `"---agentspec"`**
- **DO NOT return True for found_jsdoc if only `*/` found without `/**`; requires both markers**
- **ALWAYS call .strip() on lines; handles whitespace robustly before endswith/contains checks**
- **{'NOTE': 'Marker detection is substring-based; `---agentspec-old` will match. Consider regex if strict format required.'}**
- **{'NOTE': 'Block extraction uses `lines[i:idx]` which may include partial JSDoc if `/**` is not on same line as `*/`; verify behavior with multi-line blocks', 'changelog': ['- 2025-11-03: feat: Enhance prompt generation with terse option and adjust output token base (f533292)', '- 2025-11-03: fix: CRITICAL - Include FULL examples in prompts, not just IDs (8f1beb3)', '- 2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help, create safety system (72bbaf5)', '- 2025-11-02: feat: updated test and new prompt and examples structure , added new responses api params CFG and FFC (a86e643)', '- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)'], 'diff_summary': ['2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30): Diff Summary: - Refactored `has_jsdoc` to parse backward from a given index, detecting JSDoc blocks and checking for "---agentspec" markers within 20 lines prior to the index. - Implemented logic to track JSDoc block boundaries using "*/" and "/**" delimiters to identify and inspect relevant code sections. - Added return type annotation `tuple[']}**

### Raw YAML Block

```yaml
what: |
  Scans backward up to 20 lines for JSDoc blocks (`/** ... */`) and detects `---agentspec` marker.
  Returns (found_jsdoc: bool, has_agentspec_marker: bool).
  Logic: First finds `*/`, then looks for `/**` in preceding lines; extracts block and checks for marker.
  AI SLOP DETECTED:
  - Incomplete JSDoc detection logic
  - May miss multi-line JSDoc if `/**` not on same line as `*/`
    deps:
      calls:
        - join
        - max
        - range
        - s.endswith
        - strip
      imports:
        - agentspec.collect.collect_metadata
        - agentspec.prompts.get_agentspec_yaml_prompt
        - agentspec.prompts.get_terse_docstring_prompt
        - agentspec.prompts.get_verbose_docstring_prompt
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
  Enables incremental documentation by skipping already-documented functions.
  20-line window balances coverage vs. performance; typical JSDoc blocks fit comfortably.
  Two-part return allows callers to distinguish "no docs" from "docs exist, needs update."

guardrails:
  - DO NOT search beyond 20 lines; prevents O(n) degradation on large files
  - DO NOT assume marker is case-insensitive; uses exact string match `"---agentspec"`
  - DO NOT return True for found_jsdoc if only `*/` found without `/**`; requires both markers
  - ALWAYS call .strip() on lines; handles whitespace robustly before endswith/contains checks
  - NOTE: Marker detection is substring-based; `---agentspec-old` will match. Consider regex if strict format required.
  - NOTE: Block extraction uses `lines[i:idx]` which may include partial JSDoc if `/**` is not on same line as `*/`; verify behavior with multi-line blocks

    changelog:
      - "- 2025-11-03: feat: Enhance prompt generation with terse option and adjust output token base (f533292)"
      - "- 2025-11-03: fix: CRITICAL - Include FULL examples in prompts, not just IDs (8f1beb3)"
      - "- 2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help, create safety system (72bbaf5)"
      - "- 2025-11-02: feat: updated test and new prompt and examples structure , added new responses api params CFG and FFC (a86e643)"
      - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
    diff_summary:
      - >-
        2025-11-01: refactor: Extract system prompts to separate .md files for easier
        editing (136cb30): Diff Summary: - Refactored `has_jsdoc` to parse backward from
        a given index, detecting JSDoc blocks and checking for "---agentspec" markers
        within 20 lines prior to the index. - Implemented logic to track JSDoc block
        boundaries using "*/" and "/**" delimiters to identify and inspect relevant code
        sections. - Added return type annotation `tuple[
```

---

## process_js_file

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:2000`

### Raw YAML Block

```yaml
what: |
  Processes JavaScript files to generate and insert embedded agentspec JSDoc documentation.

  Main flow:
  1. Pre-cleans existing agentspec blocks if `update_existing=True` via `strip_js_agentspec_blocks()`
  2. Discovers functions via `_discover_js_functions()` with optional filtering
  3. In dry-run mode, prints candidates without modifying files
  4. For each function: generates LLM docstring, collects metadata, optionally summarizes recent diffs, inserts JSDoc via `apply_docstring_with_metadata()`

  AI SLOP DETECTED:
  - `strip_js_agentspec_blocks()` called but not defined in this module; assumed external
  - Exception handlers silently pass (`except Exception: pass`); masks failures in metadata and diff collection
  - `collect_function_code_diffs()`, `get_diff_summary_prompt()`, `_gen_chat` assumed to exist; not validated
  - Diff truncation at 1600 chars without user warning; may lose critical context
  - Silent failures in metadata collection mean docstring inserted without deterministic metadata
    deps:
      calls:
        - _discover_js_functions
        - _gen_chat
        - apply_docstring_with_metadata
        - c.get
        - collect_function_code_diffs
        - collect_metadata
        - diff_summary_lines.append
        - generate_docstring
        - get_diff_summary_prompt
        - len
        - print
        - replace
        - str
        - strip
        - strip_js_agentspec_blocks
      imports:
        - agentspec.collect.collect_metadata
        - agentspec.prompts.get_agentspec_yaml_prompt
        - agentspec.prompts.get_terse_docstring_prompt
        - agentspec.prompts.get_verbose_docstring_prompt
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
  Pre-cleaning ensures idempotency when re-running with `update_existing=True`; prevents stale/duplicate JSDoc.

  Dry-run mode allows safe preview before file modification (CI/review workflows).

  Metadata and diff collection wrapped in try-except to degrade gracefully if external modules unavailable; however, silent failures mask bugs and produce incomplete documentation.

  LLM-based generation allows flexible, context-aware docs; model/provider/base_url params support multi-backend flexibility.

  Diff summarization provides change history context in JSDoc; limited to 5 commits and 1600 chars per diff to control LLM token usage.

guardrails:
  - Ensure all external dependencies like `strip_js_agentspec_blocks`, `collect_function_code_diffs`, etc., are properly imported or defined before use
  - Replace silent exception handlers with explicit logging or error propagation to avoid masking bugs
  - Validate that `diff_summary_lines` truncation does not silently omit critical context; consider adding a warning when truncation occurs
  - Fail fast if required metadata or diff collection fails, rather than proceeding with incomplete documentation
  - Enforce deterministic metadata collection to ensure consistent docstring insertion

security: |
  - Silent exception handling may hide security-related issues such as unauthorized access to diffs or metadata
```yaml
---agentspec
what: |
  Authenticates user via bcrypt; validates password hash.
  AI SLOP DETECTED:
  - Stub implementation returns True unconditionally
  - Bypasses real credential checks

why: |
  Uses bcrypt for secure password hashing; prevents timing attacks.
  This approach avoids plain text storage and supports secure credential validation.

guardrails:
  - DO NOT remove bcrypt validation; prevents rainbow table attacks
  - ALWAYS validate user exists before checking password
  - NOTE: This is production auth; test thoroughly before changes

    changelog:
      - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
    diff_summary:
      - >-
        2025-11-01: refactor: Extract system prompts to separate .md files for easier
        editing (136cb30): Diff Summary: - Added new parameters `update_existing`,
        `terse`, and `diff_summary` to control behavior and output format. - Implemented
        logic to strip existing agentspec blocks when `update_existing` is enabled and
        not in dry-run mode. - Enhanced error handling to gracefully skip files with
        parsing errors. - Introduced dry-run support to preview docstring generation
        without writing changes. - Updated function
```

---

## process_file

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:2217`

### Raw YAML Block

```yaml
what: |
  Orchestrates end-to-end docstring generation for a single Python file. Extracts functions lacking docstrings, generates LLM narratives, collects deterministic metadata (deps, imports, changelog) separately, then applies both via compile-safe insertion.

  **Flow:**
  1. Extracts functions via `extract_function_info(filepath, require_agentspec=as_agentspec_yaml, update_existing=update_existing)`
  2. Returns early if no functions found or `dry_run=True` after printing plan
  3. Sorts functions in reverse line-number order (bottom-to-top) to prevent line-shift invalidation during insertion
  4. For each function: calls `generate_docstring()` (LLM narrative only), then `collect_metadata()` (deterministic, never passed to LLM), then `apply_docstring_with_metadata()` (compile-safe insertion)
  5. Metadata collection wrapped in try-except; failures fall back to empty dict and do not block insertion
  6. Prints progress at each stage (extraction, generation, success/failure)

  **AI SLOP DETECTED:**
  - Metadata collection wrapped in try-except; failures fall back to empty dict and do not block insertion
  - Compile-safety check may skip insertion if docstring breaks syntax
    deps:
      calls:
        - _gen_chat
        - apply_docstring_with_metadata
        - c.get
        - collect_function_code_diffs
        - collect_metadata
        - diff_summary_lines.append
        - extract_function_info
        - functions.sort
        - generate_docstring
        - get_diff_summary_prompt
        - len
        - print
        - replace
        - str
        - strip
      imports:
        - agentspec.collect.collect_metadata
        - agentspec.prompts.get_agentspec_yaml_prompt
        - agentspec.prompts.get_terse_docstring_prompt
        - agentspec.prompts.get_verbose_docstring_prompt
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
  **Bottom-to-top processing (reverse sort by line number)** prevents line-number invalidation. Inserting docstrings shifts all subsequent line numbers downward; ascending order would cause insertion failures. Reverse order ensures line numbers remain valid throughout loop.

  **Two-phase generation (LLM narrative + separate metadata collection)** maintains clean separation: LLM only handles narrative, deterministic metadata is collected separately and never passed to LLM, ensuring reproducibility and safety.

guardrails: |
  - Always sort functions in reverse line-number order before processing
  - Never pass metadata to LLM; collect it deterministically
  - Wrap metadata collection in try-except; fallback to empty dict on failure
  - Validate compile safety before inserting docstring
  - Do not modify source files unless `dry_run=False`
  - Use `update_existing=True` only when intended to overwrite existing docstrings
  - Ensure `model` is valid and supports the required prompt formats
  - Limit diff summary to 5 recent commits with max 1600 chars per diff snippet

security:
```yaml
---agentspec
what: |
  Authenticates user via bcrypt; validates password hash.
  AI SLOP DETECTED:
  - Stub implementation returns True unconditionally
  - Bypasses real credential checks

why: |
  Uses bcrypt for secure password hashing; prevents timing attacks.
  This approach avoids plain text storage and supports secure credential validation.

guardrails:
  - DO NOT remove bcrypt validation; prevents rainbow table attacks
  - ALWAYS validate user exists before checking password
  - NOTE: This is production auth; test thoroughly before changes

    changelog:
      - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
      - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
      - "- 2025-10-30: refactor(injection): move deps/changelog injection out of LLM path via safe two‑phase writer (219a717)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
      - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
```

---

## run

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:2402`

### Raw YAML Block

```yaml
what: |
  Orchestrates agentspec generation across Python and JS/TS files with per-run metrics.

  Behavior:
  - Loads .env, auto-detects provider (anthropic for claude models, openai otherwise)
  - Discovers files via `collect_source_files`, filters by `language` flag (py/js/auto)
  - Validates target path exists; returns 1 if missing
  - Clears `GEN_METRICS` before processing, prints summary after
  - Delegates per-file: `process_file` (Python), `process_js_file` (JS/TS)
  - Prints per-run token stats (min/avg/max) and continuation count

  Edge cases:
  - Invalid target path: returns 1 with error
  - No files found: returns 0 (silent success)
  - Provider auto-detection: claude models → anthropic, others → openai
  - Missing API keys: only fails if not dry_run; falls back to localhost:11434 for openai
  - Empty GEN_METRICS: silently skips summary (try/except swallows)

  AI SLOP DETECTED:
  - Nested agentspec docstring in `_fmt_stats` (inner function): This is a 3-line utility, not a public API. Nested agentspec blocks are confusing; should be removed or extracted to module level.
  - `_fmt_stats` defined inside exception handler scope: Will fail silently if GEN_METRICS collection fails; metrics summary becomes unreliable.
  - Excessive dependency metadata in nested docstring: Lists imports from parent scope (agentspec.collect, agentspec.prompts, etc.) that don't belong to `_fmt_stats`; indicates AI-generated boilerplate.
    deps:
      calls:
        - GEN_METRICS.clear
        - Path
        - _fmt_stats
        - _stats.mean
        - collect_source_files
        - int
        - len
        - load_env_from_dotenv
        - lower
        - m.get
        - max
        - min
        - os.getenv
        - path.exists
        - print
        - process_file
        - process_js_file
        - startswith
        - suffix.lower
        - sum
      imports:
        - agentspec.collect.collect_metadata
        - agentspec.prompts.get_agentspec_yaml_prompt
        - agentspec.prompts.get
```yaml
---agentspec
what: |
  Authenticates user via bcrypt; validates password hash.
  AI SLOP DETECTED:
  - Stub implementation returns True unconditionally
  - Bypasses real credential checks
    deps:
      calls:
        - GEN_METRICS.clear
        - Path
        - _fmt_stats
        - _stats.mean
        - collect_source_files
        - int
        - len
        - load_env_from_dotenv
        - lower
        - m.get
        - max
        - min
        - os.getenv
        - path.exists
        - print
        - process_file
        - process_js_file
        - startswith
        - suffix.lower
        - sum
      imports:
        - agentspec.collect.collect_metadata
        - agentspec.prompts.get_agentspec_yaml_prompt
        - agentspec.prompts.get_terse_docstring_prompt
        - agentspec.prompts.get_verbose_docstring_prompt
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
  Uses bcrypt for secure password hashing; prevents timing attacks.
  This approach avoids plain text storage and supports secure credential validation.

guardrails:
  - DO NOT remove bcrypt validation; prevents rainbow table attacks
  - ALWAYS validate user exists before checking password
  - NOTE: This is production auth; test thoroughly before changes

    changelog:
      - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
      - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
      - "- 2025-10-30: refactor(injection): move deps/changelog injection out of LLM path via safe two‑phase writer (219a717)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
      - "- 2025-10-30: feat: enhance docstring generation with optional dependencies and new CLI features (e54b379)"
    diff_summary:
      - >-
        2025-11-02: feat: updated test and new prompt and examples structure , added new
        responses api params CFG and FFC (a86e643): Diff Summary: - Added comprehensive
        docstring and edge case documentation for the run function's statistics
        formatting behavior. - Integrated new agentspec metadata collection and prompt
        retrieval dependencies. - Implemented numeric value validation and formatting
        using min, max, and mean operations. - Introduced int() truncation for mean
        calculation instead of rounding. - Extended function to handle iterable inputs
        and raise appropriate ValueError/TypeError exceptions. - Added
      - >-
        2025-11-01: refactor: Extract system prompts to separate .md files for easier
        editing (136cb30): Diff Summary: - Added `language` parameter to filter files by
        Python or JavaScript, with "auto" as default. - Replaced `collect_python_files`
        with `collect_source_files` to support multiple file types. - Implemented logic
        to select files based on the specified language or auto-detect both Python and
        JavaScript. - Updated file processing loop to handle filtered file list and
        added a check for
```

---

## _fmt_stats

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:2631`

### Raw YAML Block

```yaml
what: |
  Formats numeric values into "min=X avg=Y max=Z" string.
  Uses `min()`, `_stats.mean()`, `max()`; truncates mean with `int()` (not round).
  Edge cases: Empty seq raises ValueError; non-numeric raises TypeError; single value returns identical stats.
  AI SLOP DETECTED:
  - Uses `int()` for truncation, not rounding
  - No validation of input types beyond `min`/`max` calls
    deps:
      calls:
        - _stats.mean
        - int
        - max
        - min
      imports:
        - agentspec.collect.collect_metadata
        - agentspec.prompts.get_agentspec_yaml_prompt
        - agentspec.prompts.get_terse_docstring_prompt
        - agentspec.prompts.get_verbose_docstring_prompt
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
  Provides compact log/debug display. Truncation avoids noise while staying deterministic.
  Uses built-ins for correctness; `int()` truncates toward zero, not rounds.

guardrails:
  - DO NOT pass empty sequences; `min()`/`max()` raise ValueError
  - DO NOT use for statistical precision; `int()` truncates, not rounds
  - DO NOT use with non-numeric iterables; TypeError propagates
  - DO NOT assume `vals` is reusable; if generator, second call returns empty
  - NOTE: This is display-only; do not use for calculations or comparisons

changelog:
      - "- 2025-11-03: feat: Enhance prompt generation with terse option and adjust output token base (f533292)"
      - "- 2025-11-03: fix: CRITICAL - Include FULL examples in prompts, not just IDs (8f1beb3)"
      - "- 2025-11-03: fix: prevent work loss - disable worktrees, add prompts to help, create safety system (72bbaf5)"
      - "- 2025-11-02: feat: updated test and new prompt and examples structure , added new responses api params CFG and FFC (a86e643)"
      - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
    diff_summary:
      - >-
        2025-11-01: refactor: Extract system prompts to separate .md files for easier
        editing (136cb30): Diff Summary: - Extracted system prompts to separate .md
        files (136cb30) - No meaningful changes found to _fmt_stats function.
```

---

## main

**Location:** `/Users/davidmontgomery/agentspec/agentspec/generate.py:2703`

### Raw YAML Block

```yaml
what: |
  CLI entry point parsing command-line arguments and delegating to run().

  Requires: positional argument (file/directory path).
  Optional flags: --dry-run (preview mode), --force-context (inject print statements), --model MODEL (default: claude-haiku-4-5).

  Validates presence of path argument; prints usage and exits with code 1 if missing.
  Extracts model name via `sys.argv.index('--model')` and reads next argument if present; silently retains default if --model is final argument or absent.

  Calls `run(path, language="auto", dry_run, force_context, model)` and propagates exit code via `sys.exit()`.

  AI SLOP DETECTED:
  - Usage string lists 3 model options but code accepts any string without validation
  - No validation that ANTHROPIC_API_KEY exists before calling run()
    deps:
      calls:
        - argv.index
        - len
        - print
        - run
        - sys.exit
      imports:
        - agentspec.collect.collect_metadata
        - agentspec.prompts.get_agentspec_yaml_prompt
        - agentspec.prompts.get_terse_docstring_prompt
        - agentspec.prompts.get_verbose_docstring_prompt
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
  Manual argument parsing avoids external dependencies (argparse) for simple 3-flag CLI.

  Default model claude-haiku-4-5 balances cost and performance for typical documentation tasks.

  Boolean presence checks (--dry-run, --force-context) reduce parsing complexity; no values required.

  Thin main() delegates business logic to run(), keeping CLI concerns separate and testable.

  Propagating exit codes unchanged preserves caller's ability to detect success/failure in shell scripts.

guardrails:
  - DO NOT modify sys.exit(1) for missing arguments; required for proper shell exit codes in automation
  - DO NOT change default model without updating usage string and considering API cost impact
  - DO NOT add positional arguments without updating usage string to stay synchronized
  - DO NOT remove or rename --dry-run, --force-context, or --model flags; they are public CLI contract
  - DO NOT alter usage string without ensuring it reflects all supported flags accurately
  - DO NOT suppress or modify exit code from run(); callers depend on it for success/failure detection
  - ALWAYS keep usage string synchronized with actual supported flags and descriptions
  - ALWAYS preserve ANTHROPIC_API_KEY validation before calling run()

    changelog:
      - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
      - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
      - "- 2025-10-30: feat: robust docstring generation and Haiku defaults (e428337)"
      - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate (172e0a7)"
    diff_summary:
      - >-
        2025-11-01: refactor: Extract system prompts to separate .md files for easier
        editing (136cb30): Diff Summary: - Added explicit `language="auto"` parameter to
        `run()` call within `main()` to improve language detection handling.
```

---

## _compile_ok

**Location:** `/Users/davidmontgomery/agentspec/agentspec/insert_metadata.py:18`

### Raw YAML Block

```yaml
what: |
  Validates whether a Python file at the given path compiles successfully without syntax errors.

  Takes a Path object pointing to a Python source file and attempts to compile it using py_compile.compile()
  with the doraise=True flag, which causes compilation errors to be raised as exceptions rather than logged.

  Returns True if compilation succeeds (file is syntactically valid Python), False if any exception occurs
  during compilation (syntax errors, file not found, permission denied, encoding issues, etc.).

  Inputs:
    - path: Path object or path-like pointing to a .py file

  Outputs:
    - bool: True if file compiles cleanly, False otherwise

  Edge cases:
    - Non-existent files: Returns False (FileNotFoundError caught)
    - Unreadable files: Returns False (PermissionError caught)
    - Invalid encoding: Returns False (UnicodeDecodeError caught)
    - Syntax errors: Returns False (SyntaxError caught)
    - All exceptions are silently suppressed and treated as compilation failure
    deps:
      calls:
        - py_compile.compile
        - str
      imports:
        - __future__.annotations
        - os
        - pathlib.Path
        - py_compile
        - tempfile
        - typing.Any
        - typing.Dict
        - typing.Optional


why: |
  This utility provides a safe, non-throwing way to validate Python syntax before processing files.
  Using a broad Exception catch ensures robustness across all failure modes without requiring
  caller to handle multiple exception types. The boolean return value is simpler for conditional
  logic than exception handling. This is useful in metadata insertion workflows where you need to
  skip or flag files with syntax issues without halting the entire process.

guardrails:
  - DO NOT rely on this for security validation—it only checks syntax, not code safety or intent
  - DO NOT use this as a substitute for actual linting or type checking tools
  - DO NOT assume False means the file is unreadable vs. syntactically invalid; both are treated identically
  - DO NOT call this on non-Python files; behavior is undefined for non-.py content

    changelog:
      - "- 2025-10-30: refactor(injection): move deps/changelog injection out of LLM path via safe two‑phase writer (219a717)"
```

---

## apply_docstring_with_metadata

**Location:** `/Users/davidmontgomery/agentspec/agentspec/insert_metadata.py:81`

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

### Raw YAML Block

```yaml
what: |
  Returns a set of file extensions that this language adapter is responsible for processing and analyzing. Each extension is a string prefixed with a dot (e.g., '.py', '.pyi', '.js'). The method enables the adapter registry to route files to the correct language-specific handler based on their file extension. The returned set is immutable after retrieval and represents all extensions this adapter claims ownership over. Extensions are lowercase and include the leading dot character. An adapter may handle multiple related extensions (e.g., a Python adapter handling both '.py' and '.pyi' files).
    deps:
      imports:
        - __future__.annotations
        - agentspec.langs.javascript_adapter.JavaScriptAdapter
        - agentspec.langs.python_adapter.PythonAdapter
        - pathlib.Path
        - typing.Dict
        - typing.Optional
        - typing.Protocol
        - typing.Set


why: |
  File extension-based routing is the primary mechanism for dispatching source files to language-specific adapters. By centralizing extension declarations in this method, the adapter registry can build a comprehensive mapping without requiring adapters to register themselves imperatively. This approach decouples adapter discovery from adapter instantiation and allows the system to validate extension conflicts or overlaps at initialization time. Returning a set (rather than a list or tuple) emphasizes that order is irrelevant and that extensions are unique within an adapter.

guardrails:
  - DO NOT return extensions without the leading dot character, as this breaks downstream file matching logic that expects normalized '.ext' format
  - DO NOT return uppercase extensions; maintain lowercase convention for case-insensitive file system compatibility
  - DO NOT return an empty set unless the adapter genuinely handles no files; this indicates a misconfigured or incomplete adapter
  - DO NOT mutate or return a mutable reference that callers could modify; return a defensive copy or immutable collection to prevent registry corruption
  - DO NOT include extensions for file types this adapter cannot actually parse or analyze; only declare extensions for which language-specific logic exists

    changelog:
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## discover_files

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/__init__.py:104`

### Raw YAML Block

```yaml
what: |
  Discovers all source files within a target directory or returns a single file if the target is a file path.

  Behavior:
  - If target is a file: returns a list containing only that file path
  - If target is a directory: recursively traverses and collects all source files matching language-specific patterns
  - Respects language-specific ignore patterns (e.g., __pycache__, node_modules, .git, build artifacts)
  - Respects common exclusion directories across all languages (e.g., .venv, venv, dist, build)
  - Returns results as a list of Path objects for consistent downstream processing

  Inputs:
  - target: Path object pointing to either a file or directory

  Outputs:
  - list[Path]: ordered collection of discovered source files

  Edge cases:
  - Empty directories return empty list
  - Symlinks are followed based on Path.rglob behavior
  - Non-existent paths may raise FileNotFoundError or return empty list depending on implementation
  - Deeply nested directories are fully traversed
  - Files with no extension or unknown extensions are excluded
    deps:
      imports:
        - __future__.annotations
        - agentspec.langs.javascript_adapter.JavaScriptAdapter
        - agentspec.langs.python_adapter.PythonAdapter
        - pathlib.Path
        - typing.Dict
        - typing.Optional
        - typing.Protocol
        - typing.Set


why: |
  This method provides a unified entry point for file discovery across multiple language contexts. By centralizing discovery logic, we ensure consistent filtering behavior and avoid duplicating ignore patterns across language-specific implementations. The method abstracts away filesystem traversal complexity from callers, allowing them to focus on processing discovered files rather than path manipulation.

  Returning Path objects (rather than strings) provides type safety and enables callers to use Path methods for further manipulation. Supporting both file and directory inputs increases flexibility for different usage patterns (single file analysis vs. batch directory processing).

guardrails:
  - DO NOT include hidden files (dotfiles) unless explicitly part of language source conventions, as they typically represent configuration or metadata rather than source code
  - DO NOT follow symlinks that create cycles, as this could cause infinite traversal or performance degradation
  - DO NOT return duplicate paths if the same file is reachable through multiple symlink paths
  - DO NOT raise exceptions for permission-denied directories; instead skip them and continue discovery to maximize coverage
  - DO NOT include generated or compiled artifacts (*.pyc, *.class, *.o, etc.) as these are not source files
  - DO NOT traverse into version control directories (.git, .hg, .svn) as they contain metadata, not source code

    changelog:
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## extract_docstring

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/__init__.py:161`

### Raw YAML Block

```yaml
what: |
  Extracts the raw docstring from a function or class definition at a specified line number in a given file.

  Inputs:
    - filepath: Path object pointing to a Python source file
    - lineno: Integer line number (1-indexed) where the function/class definition begins

  Outputs:
    - Returns the complete docstring as a string if present, including any embedded agentspec YAML blocks
    - Returns None if no docstring exists at the specified location

  Behavior:
    - Parses the Python file at filepath to locate the AST node at lineno
    - Retrieves the docstring from that node using ast.get_docstring() or equivalent introspection
    - Preserves all formatting, indentation, and special blocks (including agentspec YAML) in raw form
    - Handles edge cases: missing files, invalid line numbers, non-function/class definitions, nodes without docstrings

  Edge cases:
    - lineno points to a line that is not a function or class definition → returns None
    - lineno is out of bounds for the file → returns None or raises appropriate error
    - File cannot be parsed as valid Python → propagates parse error
    - Docstring uses different quote styles (single, double, triple) → all preserved as-is
    deps:
      imports:
        - __future__.annotations
        - agentspec.langs.javascript_adapter.JavaScriptAdapter
        - agentspec.langs.python_adapter.PythonAdapter
        - pathlib.Path
        - typing.Dict
        - typing.Optional
        - typing.Protocol
        - typing.Set


why: |
  This method serves as the core extraction point for the agentspec documentation pipeline. By returning raw docstrings with embedded YAML blocks intact, it allows downstream processors to parse and validate agentspec blocks without losing formatting context. This design decouples extraction from interpretation, enabling flexible post-processing and validation workflows. Returning None for missing docstrings provides a clear signal for filtering and error handling rather than raising exceptions, improving robustness in batch processing scenarios.

guardrails:
  - DO NOT modify or normalize the docstring content; preserve exact formatting and whitespace to maintain agentspec block integrity
  - DO NOT attempt to parse or validate YAML within this method; that responsibility belongs to downstream processors
  - DO NOT assume lineno is 0-indexed; clarify and document the indexing convention to prevent off-by-one errors
  - DO NOT silently ignore parse errors on malformed Python files; propagate them to allow callers to handle invalid source gracefully
  - DO NOT cache results without invalidating on file modification; ensure freshness for development workflows

    changelog:
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## insert_docstring

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/__init__.py:215`

### Raw YAML Block

```yaml
what: |
  Inserts or replaces a docstring for a function or class at a specified line number in a given file.

  Inputs:
    - filepath: Path object pointing to the target source file
    - lineno: Integer line number where the function/class definition begins (1-indexed)
    - docstring: String containing the complete docstring to insert (should include quotes and formatting)

  Outputs:
    - None (modifies file in-place)

  Behavior:
    - Locates the function or class definition at the specified line number
    - Determines the appropriate indentation level based on the definition's context
    - Inserts the docstring immediately after the function/class signature, or replaces an existing docstring
    - Preserves surrounding code structure and indentation
    - Handles language-specific docstring conventions (e.g., Python triple quotes, proper placement after def/class keyword)

  Edge cases:
    - Function/class already has a docstring: replaces the existing one while maintaining indentation
    - Nested functions/classes: correctly determines indentation relative to parent scope
    - Multi-line function signatures: correctly identifies where docstring should be inserted
    - Files with mixed indentation or non-standard formatting: adapts to existing style
    - Invalid line numbers: behavior depends on implementation (may raise error or handle gracefully)
    deps:
      imports:
        - __future__.annotations
        - agentspec.langs.javascript_adapter.JavaScriptAdapter
        - agentspec.langs.python_adapter.PythonAdapter
        - pathlib.Path
        - typing.Dict
        - typing.Optional
        - typing.Protocol
        - typing.Set


why: |
  This method abstracts the language-specific complexity of docstring insertion, allowing callers to work with a uniform interface regardless of the target language. By accepting a line number, it enables precise targeting of specific definitions without requiring the caller to parse the file. The method handles indentation automatically, reducing boilerplate and ensuring consistency with the file's existing style. This is essential for automated documentation generation tools that need to inject docstrings into source files while preserving code integrity.

guardrails:
  - DO NOT assume the docstring parameter is already properly formatted with language-specific quotes or delimiters; validate or document whether the caller is responsible for this
  - DO NOT modify file permissions or ownership; preserve the original file metadata
  - DO NOT insert docstrings at incorrect indentation levels, as this will break syntax and code structure
  - DO NOT overwrite or corrupt existing code beyond the target docstring; use precise line-based insertion
  - DO NOT assume line numbers are 0-indexed; clarify and enforce 1-indexed convention to match editor conventions
  - DO NOT handle files that cannot be read or written without raising appropriate exceptions; do not silently fail

    changelog:
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## gather_metadata

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/__init__.py:272`

### Raw YAML Block

```yaml
what: |
  Extracts and aggregates metadata from a Python source file for a specified function.

  Takes a filepath and function name as inputs and returns a dictionary containing:
  - 'calls': List of functions/methods invoked within the target function
  - 'imports': All import statements present in the file (both absolute and relative)
  - 'called_by': Functions or methods that call the target function
  - 'signature': Function signature including parameters and return type annotation if present
  - 'docstring': Extracted docstring content if available
  - 'decorators': Any decorators applied to the function
  - 'line_range': Start and end line numbers of the function definition

  Handles edge cases including:
  - Functions with no docstrings (returns None or empty string)
  - Nested function definitions (captures scope appropriately)
  - Dynamic imports and conditional imports (includes all discovered imports)
  - Methods within classes (distinguishes between instance, class, and static methods)
  - Functions with no callers or callees (returns empty lists)
  - Malformed or incomplete function definitions (graceful degradation)
    deps:
      imports:
        - __future__.annotations
        - agentspec.langs.javascript_adapter.JavaScriptAdapter
        - agentspec.langs.python_adapter.PythonAdapter
        - pathlib.Path
        - typing.Dict
        - typing.Optional
        - typing.Protocol
        - typing.Set


why: |
  This method serves as a central extraction point for static analysis of Python code.
  It enables downstream analysis tools to understand function dependencies, call graphs,
  and documentation without requiring full AST traversal at call sites. By consolidating
  metadata extraction into a single method, we reduce code duplication and provide a
  consistent interface for analysis operations. The dictionary return format allows
  flexible consumption by different analysis stages without tight coupling.

guardrails:
  - DO NOT attempt to execute the code or resolve runtime imports; this is static analysis only
  - DO NOT modify the source file during metadata extraction; this must be read-only
  - DO NOT assume function names are globally unique; include class context in results when applicable
  - DO NOT include transitive call chains; only direct calls should be listed in 'calls' and 'called_by'
  - DO NOT resolve relative imports to absolute paths; preserve import statements as written in source
  - DO NOT fail silently on parse errors; raise or log exceptions for malformed Python syntax

    changelog:
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## validate_syntax

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/__init__.py:329`

### What This Does

Rationale for this validation step is to catch errors introduced during code generation or modification before the file is used or committed. This prevents downstream failures and provides immediate feedback. The boolean return type allows for graceful degradation in some contexts, while exception raising allows strict validation in others. Language-specific implementation is necessary because syntax rules vary significantly across Python, JavaScript, Go, etc.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT assume file encoding; respect encoding declarations or use safe fallbacks to avoid UnicodeDecodeError**
- **DO NOT modify the file during validation; this is a read-only check operation**
- **DO NOT catch all exceptions silently; distinguish between syntax errors and I/O errors (file not found, permission denied)**
- **DO NOT validate only partial syntax; ensure the entire file is checked for consistency**
- **DO NOT skip validation for empty files without explicit language-specific rules; some languages treat empty files as valid, others do not**

### Raw YAML Block

```yaml
what: |
  Validates whether a file has syntactically correct code after modifications.

  Accepts a Path object pointing to a file on disk. Returns True if the file's syntax is valid and parseable by the target language's parser. Returns False or raises an exception if syntax is invalid.

  The method should perform language-specific syntax checking appropriate to the file type (determined by extension or other metadata). It validates the complete file contents, not partial snippets. Edge cases include: empty files (typically valid), files with encoding declarations, files with syntax errors at various positions (start, middle, end), and files with mixed line endings.

  Output is a boolean True for valid syntax. Invalid syntax should either return False or raise a descriptive exception indicating the nature of the syntax error and its location.
what: |
  Rationale for this validation step is to catch errors introduced during code generation or modification before the file is used or committed. This prevents downstream failures and provides immediate feedback. The boolean return type allows for graceful degradation in some contexts, while exception raising allows strict validation in others. Language-specific implementation is necessary because syntax rules vary significantly across Python, JavaScript, Go, etc.
guardrails:
  - DO NOT assume file encoding; respect encoding declarations or use safe fallbacks to avoid UnicodeDecodeError
  - DO NOT modify the file during validation; this is a read-only check operation
  - DO NOT catch all exceptions silently; distinguish between syntax errors and I/O errors (file not found, permission denied)
  - DO NOT validate only partial syntax; ensure the entire file is checked for consistency
  - DO NOT skip validation for empty files without explicit language-specific rules; some languages treat empty files as valid, others do not
```

---

## get_comment_delimiters

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/__init__.py:382`

### Raw YAML Block

```yaml
what: |
  Returns a tuple of two strings representing the opening and closing delimiters for multi-line comments in the target programming language.

  The function retrieves language-specific comment syntax by returning a (start_delimiter, end_delimiter) pair. For example:
  - JavaScript/C-style: ('/*', '*/')
  - Python docstrings: ('"""', '"""')
  - HTML/XML: ('<!--', '-->')
  - Lua: ('--[[', ']]')

  This is used by the language abstraction layer to identify and parse multi-line comment blocks during code analysis and transformation. The delimiters are language-specific and must match the exact syntax recognized by the target language's parser.

  Edge cases:
  - Languages without multi-line comments may return empty strings or raise NotImplementedError
  - Some languages use identical start/end delimiters (Python), others use distinct pairs (JavaScript)
  - Delimiters are case-sensitive and must include any required whitespace or special characters
    deps:
      imports:
        - __future__.annotations
        - agentspec.langs.javascript_adapter.JavaScriptAdapter
        - agentspec.langs.python_adapter.PythonAdapter
        - pathlib.Path
        - typing.Dict
        - typing.Optional
        - typing.Protocol
        - typing.Set


why: |
  This method abstracts language-specific comment syntax behind a uniform interface, allowing the agentspec system to work with multiple programming languages without hardcoding syntax rules throughout the codebase. By centralizing delimiter definitions in the language module, changes to language support only require updates in one location. The tuple return type provides a simple, immutable contract that is easy to unpack and use in string operations.

guardrails:
  - DO NOT return delimiters that don't match the actual language syntax, as this will cause comment parsing to fail silently or produce incorrect results
  - DO NOT assume delimiters are symmetric; some languages use different start/end markers and both must be returned in the correct order
  - DO NOT include escape characters or regex patterns; return literal delimiter strings only
  - DO NOT return None or single-element tuples; always return exactly a 2-tuple of strings

    changelog:
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## parse

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/__init__.py:428`

### Raw YAML Block

```yaml
what: |
  Parses source code strings into language-specific Abstract Syntax Tree (AST) or tree structures.

  Input: A string containing source code in the target language (e.g., Python, JavaScript, Go).
  Output: A language-agnostic tree object representing the hierarchical structure of the code, with nodes for statements, expressions, declarations, and other syntactic elements.

  The method serves as the entry point for code analysis workflows. It delegates to language-specific parsers (e.g., ast module for Python, tree-sitter for compiled languages) and normalizes their output into a common traversable format.

  Edge cases:
  - Malformed or syntactically invalid source code raises ParseError with line/column information
  - Empty strings return an empty tree or minimal valid AST
  - Unicode and multi-byte characters are preserved and correctly positioned in error reporting
  - Very large source files (>10MB) may trigger memory or timeout constraints depending on parser implementation
  - Mixed line endings (CRLF/LF) are normalized before parsing
    deps:
      imports:
        - __future__.annotations
        - agentspec.langs.javascript_adapter.JavaScriptAdapter
        - agentspec.langs.python_adapter.PythonAdapter
        - pathlib.Path
        - typing.Dict
        - typing.Optional
        - typing.Protocol
        - typing.Set


why: |
  Abstracting parse logic into a single method enables consistent AST access across multiple languages without caller code duplication. By returning a normalized tree structure, downstream adapter methods (traversal, transformation, analysis) can operate uniformly regardless of the underlying parser library.

  This design supports incremental language support: new languages can be added by implementing language-specific parse logic without modifying consumer code. The tree abstraction also enables caching and memoization of parse results for repeated analysis on the same source.

guardrails:
  - DO NOT assume the returned tree is mutable; some parser backends return immutable structures. Callers should not modify tree nodes in place.
  - DO NOT rely on parser-specific node types leaking through the interface; always use the adapter's tree traversal methods to access node properties.
  - DO NOT pass untrusted source code without resource limits; parsing can be computationally expensive and may be exploited for denial-of-service attacks.
  - DO NOT assume parse errors include full source context; truncate or summarize large files in error messages to avoid memory bloat.
  - DO NOT parse binary or non-text data; validate input is valid UTF-8 or declared encoding before calling parse.

    changelog:
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## LanguageRegistry

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/__init__.py:477`

### What This Does

Global registry mapping file extensions to language adapters.

### Raw YAML Block

```yaml
Global registry mapping file extensions to language adapters.
```

---

## register

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/__init__.py:485`

### Raw YAML Block

```yaml
what: |
  Registers a LanguageAdapter instance for all file extensions it declares support for.

  Takes a LanguageAdapter object and iterates through its `file_extensions` attribute,
  storing a reference to the adapter in the class-level `_adapters` dictionary keyed by
  each extension (normalized to lowercase). This enables the registry to map file extensions
  to their corresponding language adapters for later lookup and instantiation.

  Inputs:
    - adapter: LanguageAdapter instance with a `file_extensions` iterable of strings

  Outputs:
    - None (mutates class-level `_adapters` dict as side effect)

  Edge cases:
    - Empty file_extensions: adapter registered but unreachable via extension lookup
    - Duplicate extensions across adapters: later registration overwrites earlier one
    - Mixed case extensions: normalized to lowercase for case-insensitive matching
    - None or invalid adapter: will raise AttributeError when accessing file_extensions
    deps:
      calls:
        - ext.lower
      imports:
        - __future__.annotations
        - agentspec.langs.javascript_adapter.JavaScriptAdapter
        - agentspec.langs.python_adapter.PythonAdapter
        - pathlib.Path
        - typing.Dict
        - typing.Optional
        - typing.Protocol
        - typing.Set


why: |
  Centralizes adapter registration logic into a single class method to maintain a
  consistent registry pattern. Normalizing extensions to lowercase ensures predictable
  lookups regardless of how extensions are specified. Using a dictionary keyed by
  extension provides O(1) lookup performance for the common case of "find adapter for
  this file extension." Class-level storage allows all instances to share the same
  registry without duplication.

guardrails:
  - DO NOT assume adapter.file_extensions is non-empty; validate before registration if
    empty adapters should be rejected
  - DO NOT allow unvalidated adapter objects; verify adapter implements LanguageAdapter
    protocol before storing to prevent runtime errors during adapter usage
  - DO NOT silently overwrite existing adapters for an extension; log or raise on
    collision to catch configuration errors early
  - DO NOT mutate the adapter object itself; only store references in the registry

    changelog:
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## unregister

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/__init__.py:547`

### Raw YAML Block

```yaml
what: |
  Unregisters a language adapter from the internal adapter registry by its file extension.

  Takes a single extension string parameter (e.g., "py", "js", "ts") and removes the corresponding
  adapter from the class-level _adapters dictionary. The extension lookup is case-insensitive
  (converted to lowercase before removal). If the extension does not exist in the registry,
  the operation silently succeeds (no exception raised) due to the dict.pop() default None behavior.

  Returns None. This is a class method that modifies shared state across all instances.

  Typical use case: removing support for a language adapter at runtime, cleaning up after
  dynamic registration, or disabling specific language handlers without restarting the application.

  Edge cases:
  - Extension not found: silently ignored (pop with default None)
  - Empty string extension: will be lowercased to empty string and removed if it exists
  - None passed as extension: will raise AttributeError (str method .lower() called on None)
  - Whitespace in extension: preserved as-is before lowercasing (e.g., " py " becomes " py ")
    deps:
      calls:
        - _adapters.pop
        - extension.lower
      imports:
        - __future__.annotations
        - agentspec.langs.javascript_adapter.JavaScriptAdapter
        - agentspec.langs.python_adapter.PythonAdapter
        - pathlib.Path
        - typing.Dict
        - typing.Optional
        - typing.Protocol
        - typing.Set


why: |
  The silent failure approach (pop with default) prevents exceptions when unregistering
  non-existent adapters, making the API forgiving and idempotent. Case-insensitive lookup
  ensures consistency with typical file extension handling across operating systems.

  Using a class method allows centralized adapter lifecycle management without requiring
  instance creation. The _adapters dictionary is the single source of truth for registered
  adapters, so direct mutation is the appropriate mechanism.

  Tradeoff: silent failure means caller cannot distinguish between successful removal and
  attempted removal of non-existent adapter. This is acceptable for cleanup operations but
  may hide bugs if strict validation is needed elsewhere.

guardrails:
  - DO NOT pass None as extension—will raise AttributeError; validate input is string before calling
  - DO NOT rely on return value for confirmation of removal—always returns None; check registry state separately if verification needed
  - DO NOT assume case sensitivity—extension is always lowercased, so "PY" and "py" target the same adapter
  - DO NOT use this to remove adapters during active adapter lookups in other threads without synchronization—_adapters is not thread-safe

    changelog:
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## get_by_extension

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/__init__.py:610`

### Raw YAML Block

```yaml
what: |
  Retrieves a LanguageAdapter instance for a given file extension by performing a case-insensitive lookup in the internal adapter registry. Accepts a file extension string (e.g., '.py', '.js', '.ts') and returns the corresponding LanguageAdapter if registered, or None if no adapter exists for that extension. The lookup normalizes the input extension to lowercase before querying the _adapters dictionary to ensure consistent matching regardless of input case variation (e.g., '.PY', '.Py', '.py' all resolve identically). This is a class method that accesses the shared _adapters registry maintained across all instances.
    deps:
      calls:
        - _adapters.get
        - extension.lower
      imports:
        - __future__.annotations
        - agentspec.langs.javascript_adapter.JavaScriptAdapter
        - agentspec.langs.python_adapter.PythonAdapter
        - pathlib.Path
        - typing.Dict
        - typing.Optional
        - typing.Protocol
        - typing.Set


why: |
  File extensions are conventionally case-insensitive in most filesystems and development workflows, but Python string comparisons are case-sensitive by default. Normalizing to lowercase ensures robust matching across different naming conventions users might employ. Using a class method with a shared registry provides efficient O(1) lookup performance and centralizes adapter management. Returning Optional[LanguageAdapter] allows graceful handling of unsupported file types without raising exceptions, enabling caller code to implement fallback logic or user-friendly error messages.

guardrails:
  - DO NOT assume the extension parameter includes a leading dot—validate or document whether callers must provide '.py' vs 'py' format
  - DO NOT modify the _adapters registry during lookup; this method must be read-only to maintain thread-safety and prevent accidental state corruption
  - DO NOT return a default adapter if the extension is not found; returning None forces explicit handling and prevents silent mismatches
  - DO NOT perform expensive operations (file I/O, network calls) during lookup; this must remain a simple dictionary access for performance

    changelog:
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## get_by_path

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/__init__.py:647`

### Raw YAML Block

```yaml
what: |
  Retrieves a LanguageAdapter instance for a given file path by extracting and normalizing its file extension.

  **Inputs:**
  - filepath: Path | str - A file path as either a pathlib.Path object or string (e.g., "/path/to/file.py", "script.js")

  **Outputs:**
  - Optional[LanguageAdapter] - Returns a LanguageAdapter matching the file extension, or None if no adapter exists for that extension

  **Behavior:**
  1. Normalizes string input to Path object if needed
  2. Extracts file extension using Path.suffix (includes leading dot, e.g., ".py")
  3. Converts extension to lowercase for case-insensitive matching
  4. Delegates to get_by_extension() for adapter lookup

  **Edge cases:**
  - Files with no extension (suffix is empty string) - returns None via get_by_extension
  - Mixed-case extensions (e.g., ".PY", ".Js") - normalized to lowercase before lookup
  - Compound extensions (e.g., ".tar.gz") - only rightmost extension is used (Path.suffix behavior)
  - Non-existent file paths - Path object creation succeeds; adapter lookup determines result
    deps:
      calls:
        - Path
        - cls.get_by_extension
        - isinstance
        - suffix.lower
      imports:
        - __future__.annotations
        - agentspec.langs.javascript_adapter.JavaScriptAdapter
        - agentspec.langs.python_adapter.PythonAdapter
        - pathlib.Path
        - typing.Dict
        - typing.Optional
        - typing.Protocol
        - typing.Set


why: |
  This method provides a convenient file-path-based entry point to the adapter registry, abstracting away extension extraction logic. By normalizing to lowercase, it ensures consistent matching regardless of filesystem or user input casing conventions. Delegating to get_by_extension() maintains single responsibility and reuses existing lookup logic. The Optional return type allows graceful handling of unsupported file types without raising exceptions.

guardrails:
  - DO NOT assume the file exists on disk - Path objects are created without validation, only the extension string matters
  - DO NOT use Path.name or other path components for adapter selection - only the file extension suffix is relevant
  - DO NOT perform case-sensitive extension matching - always normalize to lowercase to handle cross-platform and user input variations
  - DO NOT handle compound extensions specially (e.g., treating ".tar.gz" as a unit) - rely on Path.suffix which returns only the final component

    changelog:
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## supported_extensions

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/__init__.py:707`

### Raw YAML Block

```yaml
what: |
  Returns a set of all file extensions currently registered in the language adapter registry.

  This is a class method that provides read-only access to the keys of the internal `_adapters` dictionary,
  which maps file extensions (strings like ".py", ".js", ".ts") to their corresponding language adapter instances.

  The method converts the dictionary keys to a set to provide a clean, deduplicated collection of supported extensions.
  Extensions are stored without normalization, so the exact format depends on how adapters were registered.

  Returns an empty set if no adapters have been registered yet. The returned set is a shallow copy,
  so modifications to it do not affect the internal registry.

  Typical use cases: checking capability before processing a file, displaying supported formats to users,
  or validating file extensions against the registry.
    deps:
      calls:
        - _adapters.keys
        - set
      imports:
        - __future__.annotations
        - agentspec.langs.javascript_adapter.JavaScriptAdapter
        - agentspec.langs.python_adapter.PythonAdapter
        - pathlib.Path
        - typing.Dict
        - typing.Optional
        - typing.Protocol
        - typing.Set


why: |
  Exposing the adapter keys as a set provides a simple, immutable view of supported extensions without
  revealing the internal adapter implementation details or allowing callers to modify the registry.

  Using a set (rather than returning keys() directly) provides a standard collection type that is
  hashable, iterable, and supports set operations (union, intersection, etc.) that callers may need.

  This class method pattern allows querying capabilities without instantiating the class, following
  the registry pattern where the class itself acts as a factory and capability provider.

guardrails:
  - DO NOT modify the returned set expecting changes to persist in the registry—the set is a copy
  - DO NOT assume extension format is normalized (e.g., ".py" vs "py")—use exact values from the registry
  - DO NOT call this method in tight loops without caching if performance is critical, as it reconstructs the set each call
  - DO NOT rely on extension ordering—sets are unordered; sort if deterministic output is needed

    changelog:
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## list_adapters

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/__init__.py:763`

### Raw YAML Block

```yaml
what: |
  Returns a shallow copy of all currently registered language adapters as a dictionary.

  The method accesses the class-level `_adapters` dictionary (a private registry mapping language identifiers to LanguageAdapter instances) and returns a new dictionary containing all registered adapters. This ensures callers receive a snapshot of the adapter registry at call time without holding a reference to the internal mutable state.

  Inputs: None (class method, no instance parameters required)

  Outputs: Dict[str, LanguageAdapter] where keys are language identifiers (strings) and values are LanguageAdapter instances

  Edge cases:
  - If no adapters have been registered, returns an empty dictionary
  - Modifications to the returned dictionary do not affect the internal `_adapters` registry (shallow copy isolation)
  - Adapter instances themselves remain mutable references; modifications to adapter state will be reflected across all copies
    deps:
      calls:
        - dict
      imports:
        - __future__.annotations
        - agentspec.langs.javascript_adapter.JavaScriptAdapter
        - agentspec.langs.python_adapter.PythonAdapter
        - pathlib.Path
        - typing.Dict
        - typing.Optional
        - typing.Protocol
        - typing.Set


why: |
  Returning a copy rather than the internal registry directly prevents external code from accidentally mutating the adapter registry through direct dictionary manipulation (e.g., adding, removing, or replacing adapters). This provides a controlled public interface for introspection while maintaining encapsulation of the internal registration mechanism.

  Using a class method allows access to the shared adapter registry without requiring an instance, supporting a singleton-like pattern for language adapter management across the application.

guardrails:
  - DO NOT return the internal `_adapters` dictionary directly; always return a copy to prevent external mutation of the registry
  - DO NOT assume the registry is non-empty; callers must handle empty dictionary responses gracefully
  - DO NOT modify adapter state through this method; it is read-only introspection only

    changelog:
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
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

### Raw YAML Block

```yaml
what: |
  Initializes a JavaScript language adapter with tree-sitter parsers for three JavaScript-family languages: JavaScript, TypeScript, and TSX. The initializer attempts to import the optional tree-sitter-languages dependency and instantiate language-specific parsers for each supported file type. On successful initialization, the default parser is set to the JavaScript parser and an internal flag (_tree_sitter_available) is set to True, enabling downstream parsing operations. If the tree-sitter-languages package is not installed, an ImportError is caught, logged at error level with installation instructions, and the method returns early without raising an exception, leaving all parser attributes as None. If parser instantiation fails after successful import, an exception is raised after logging diagnostic information. Special handling detects version mismatches between tree-sitter and tree-sitter-languages by inspecting exception messages for "takes exactly" and "argument" keywords, providing targeted remediation guidance to users.
    deps:
      calls:
        - logger.debug
        - logger.error
        - logger.exception
        - str
        - tree_sitter_languages.get_parser
      imports:
        - __future__.annotations
        - logging
        - pathlib.Path
        - re
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  Tree-sitter is an optional dependency because not all users require JavaScript/TypeScript parsing support, keeping the base installation lightweight. Graceful degradation on missing dependencies allows the broader agentspec package to function for other languages while clearly communicating to users what is needed for JavaScript support. The three separate parser instances (js_parser, ts_parser, tsx_parser) enable language-specific parsing strategies and future extensibility for language-variant-specific logic. Defaulting to the JavaScript parser provides a sensible fallback for ambiguous cases. Version mismatch detection with specific error messaging reduces user friction during dependency installation and configuration, as tree-sitter has strict version coupling requirements.

guardrails:
  - DO NOT silently fail if tree-sitter-languages is installed but parser instantiation fails; raise the exception after logging to ensure users are aware of configuration problems rather than experiencing silent degradation downstream.
  - DO NOT assume tree-sitter-languages is available globally; always attempt import and handle ImportError gracefully to support optional dependency patterns.
  - DO NOT initialize self.parser to a non-None value if any parser instantiation fails; leave it as None to signal to calling code that parsing is unavailable rather than risking use of a partially-initialized adapter.
  - DO NOT catch and suppress the exception from parser instantiation without re-raising; defensive logging is appropriate but the error must propagate so installation/configuration issues are surfaced to the user.

    changelog:
      - "- 2025-11-04: fix: slice UTF-8 bytes then decode to avoid multibyte misalignment"
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## file_extensions

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:166`

### Raw YAML Block

```yaml
what: |
  Returns a set of file extensions that the JavaScript/TypeScript adapter is responsible for handling.

  The method returns exactly five extensions as strings: '.js' (standard JavaScript), '.mjs' (ES modules),
  '.jsx' (React/JSX syntax), '.ts' (TypeScript), and '.tsx' (TypeScript with JSX). Each extension is
  prefixed with a dot and stored in a set data structure for O(1) lookup performance.

  This is a stateless accessor method with no parameters. It always returns the same immutable set
  of extensions regardless of adapter state or configuration. The returned set can be used by the
  adapter registry or file routing logic to determine which files should be processed by this adapter.
    deps:
      imports:
        - __future__.annotations
        - logging
        - pathlib.Path
        - re
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  Using a set provides efficient membership testing when routing files to appropriate language adapters.
  Returning a set (rather than a list or tuple) makes the intent clear that order is irrelevant and
  duplicates are impossible. This method centralizes the definition of supported extensions in one place,
  making it easy to audit which file types are handled and reducing the risk of inconsistencies across
  the codebase. The method is simple and pure, with no side effects, making it safe to call repeatedly.

guardrails:
  - DO NOT modify the returned set in-place; callers should treat it as immutable to prevent unexpected
    behavior in other parts of the adapter system that may rely on the same set reference.
  - DO NOT add or remove extensions without updating documentation and considering downstream impact on
    file routing logic and language detection heuristics.
  - DO NOT return None or an empty set; this method must always return the complete set of supported
    extensions to avoid silent failures in file routing.

    changelog:
      - "- 2025-11-04: fix: use byte-slice+decode for import text extraction"
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## discover_files

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:217`

### Raw YAML Block

```yaml
what: |
  Discovers all JavaScript/TypeScript files within a target directory or validates a single file.

  Accepts either a string path or Path object as input. If target is a file with a supported extension (.js, .mjs, .jsx, .ts, .tsx), returns a list containing that single resolved file path. If target is a directory, recursively globs for all files matching supported extensions, filtering out paths containing '.git' directory component, and returns a sorted list of resolved absolute paths. If target is neither file nor directory, returns empty list.

  Supported extensions: .js, .mjs, .jsx, .ts, .tsx

  Edge cases:
  - String paths are converted to Path objects for consistent handling
  - Single files are validated against extension whitelist before inclusion
  - Only .git directories are excluded at discovery time; all other exclusions (.venv, node_modules, build, dist, etc.) are deferred to downstream .gitignore-based filtering in collect_source_files
  - Non-existent paths return empty list rather than raising exceptions
  - Results are sorted for deterministic output across runs
  - All returned paths are resolved to absolute paths
    deps:
      calls:
        - Path
        - add_glob
        - files.append
        - files.sort
        - isinstance
        - p.is_file
        - p.resolve
        - target.is_dir
        - target.is_file
        - target.resolve
        - target.rglob
      imports:
        - __future__.annotations
        - logging
        - pathlib.Path
        - re
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  Minimal pre-filtering at discovery stage keeps this function focused and fast. Deferring comprehensive exclusion logic to .gitignore-based post-filtering (in collect_source_files) provides several benefits: respects project-specific ignore patterns, avoids hardcoding exclusion lists that may become stale, and centralizes exclusion logic in one place. Only .git is excluded here because it is a universal concern that should never contain source files and its presence in path.parts is a reliable indicator. This two-stage approach (minimal discovery + comprehensive filtering) balances performance with flexibility.

guardrails:
  - DO NOT apply comprehensive exclusion patterns here (node_modules, .venv, build, etc.) because these should be driven by .gitignore configuration, allowing projects to customize what is ignored
  - DO NOT raise exceptions for missing or invalid paths; return empty list instead to allow graceful handling by callers
  - DO NOT skip the .resolve() call; absolute paths prevent ambiguity and path traversal issues in downstream processing
  - DO NOT omit the sort() call; deterministic ordering is essential for reproducible results and testing
  - DO NOT accept file extensions beyond the defined whitelist without explicit code change; this prevents accidental inclusion of non-source files

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## add_glob

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:289`

### Raw YAML Block

```yaml
what: |
  Recursively globs for files matching a given extension pattern within a target directory.

  Inputs:
    - ext (str): File extension pattern to match (e.g., '.js', '.ts'). Pattern is passed directly to rglob().
    - target (Path): Root directory to search from (implicit, from enclosing scope).
    - files (list): Accumulator list to append resolved file paths to (implicit, from enclosing scope).

  Behavior:
    - Uses Path.rglob() to recursively search all subdirectories for files matching the pattern '*{ext}'.
    - Filters out any paths containing '.git' in their path components to exclude version control metadata.
    - Only appends entries that are actual files (not directories) via is_file() check.
    - Resolves each matched file to its absolute path before appending.

  Outputs:
    - Mutates the files list by appending Path objects (absolute, resolved paths).
    - Returns None (side-effect function).

  Edge cases:
    - Symlinks are followed by rglob() by default; resolved paths will point to their targets.
    - Empty extension strings or malformed patterns may yield no matches without error.
    - .git exclusion is path-component based, so directories named '.git' anywhere in the hierarchy are skipped.
    - If target is not readable or does not exist, rglob() will raise an exception.
    deps:
      calls:
        - files.append
        - p.is_file
        - p.resolve
        - target.rglob
      imports:
        - __future__.annotations
        - logging
        - pathlib.Path
        - re
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  This approach balances simplicity with practical filtering needs for JavaScript/TypeScript file collection.

  Rationale:
    - rglob() provides concise recursive traversal without manual stack management.
    - Explicit .git filtering is necessary because .gitignore rules are not automatically applied by Path methods; this ensures build artifacts and dependencies in node_modules (often under .git-adjacent structures) are excluded.
    - is_file() check prevents directories from being added, which would cause downstream processing errors.
    - resolve() ensures consistent absolute paths regardless of relative symlinks or working directory state.

  Tradeoffs:
    - Does not parse .gitignore files, so other ignored patterns (e.g., node_modules, dist/) must be handled elsewhere or require additional filtering logic.
    - .git filtering is coarse-grained (any path component named '.git'); more granular control would require regex or explicit path matching.
    - No caching of glob results; repeated calls with the same ext will re-traverse the filesystem.

guardrails:
  - DO NOT rely on .gitignore rules being respected; this function only excludes .git directories. Callers must implement additional filtering for build artifacts, dependencies, and other ignored patterns.
  - DO NOT assume the extension pattern is validated; malformed patterns (e.g., missing dot, regex syntax) will be passed to rglob() as-is and may produce unexpected results.
  - DO NOT use this function on very large directory trees without considering performance; rglob() traverses all subdirectories and may be slow on deep hierarchies with many files.
  - DO NOT modify the files list concurrently from other threads; this function mutates a shared accumulator without synchronization.

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## extract_docstring

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:373`

### Raw YAML Block

```yaml
what: |
  Extracts JSDoc comment blocks preceding a function or class declaration at a specified line number in a JavaScript/TypeScript file.

  **Inputs:**
  - filepath: Path object pointing to a JavaScript/TypeScript source file
  - lineno: Integer line number where the target function/class is declared

  **Outputs:**
  - Returns the docstring content as a string (JSDoc text without /** */ delimiters), or None if extraction fails

  **Behavior:**
  1. Returns None immediately if tree-sitter parser is unavailable (graceful degradation)
  2. Attempts to read the source file with UTF-8 encoding
  3. Parses the source code into an abstract syntax tree (AST) using tree-sitter
  4. Delegates to _find_preceding_jsdoc() to locate and extract the JSDoc block that precedes the declaration at lineno
  5. Returns extracted docstring or None on any parsing/IO failure

  **Edge cases:**
  - File not found or unreadable (IOError) → returns None
  - File contains invalid UTF-8 sequences → returns None
  - Parser fails on malformed JavaScript/TypeScript → returns None
  - No JSDoc comment precedes the target declaration → returns None (delegated to _find_preceding_jsdoc)
  - Line number out of bounds or not a function/class → returns None (delegated to _find_preceding_jsdoc)
    deps:
      calls:
        - f.read
        - open
        - parser.parse
        - self._find_preceding_jsdoc
        - source.encode
      imports:
        - __future__.annotations
        - logging
        - pathlib.Path
        - re
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  This method provides a robust, fault-tolerant interface for extracting documentation from JavaScript source files. By returning None on any error rather than raising exceptions, it allows calling code to gracefully handle missing or unparseable files without try-catch overhead. The tree-sitter dependency check prevents runtime errors in environments where the parser is unavailable. Delegating AST traversal to _find_preceding_jsdoc separates concerns: this method handles I/O and parsing setup, while the helper handles AST navigation logic. This design supports incremental documentation extraction across large codebases where some files may be malformed or inaccessible.

guardrails:
  - DO NOT assume the file encoding is UTF-8 without attempting to decode; some legacy JavaScript files may use other encodings, but UTF-8 is the modern standard and failures should be caught gracefully
  - DO NOT raise exceptions for file I/O or parse errors; return None to allow batch processing of multiple files without interruption
  - DO NOT modify the source file or tree-sitter parser state; this method must be read-only to avoid side effects
  - DO NOT assume lineno is 1-indexed vs 0-indexed without verifying against the caller's convention; document this contract in the calling code
  - DO NOT attempt to extract docstrings if tree-sitter is unavailable; the early return prevents cascading failures in environments without native parser bindings

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## insert_docstring

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:453`

### Raw YAML Block

```yaml
what: |
  Inserts or replaces a JSDoc documentation block for a JavaScript function or class at a specified line number.

  Inputs:
  - filepath: Path object pointing to the JavaScript source file
  - lineno: 1-indexed line number where the target function/class is declared
  - docstring: Raw documentation text (without JSDoc formatting)

  Outputs:
  - Modifies the file in-place with formatted JSDoc block
  - JSDoc block is properly indented to match the target function/class indentation
  - Each line is prefixed with " * " and wrapped with /** and */ delimiters

  Behavior:
  - Reads source file with UTF-8 encoding; raises ValueError if file cannot be read or line is out of range
  - Extracts indentation from the target function line and applies it to all JSDoc lines
  - Searches backward up to 200 lines from the target to find an existing JSDoc block (/** ... */)
  - If an existing JSDoc block is found immediately preceding the function, replaces it entirely
  - If no existing JSDoc block is found, inserts the new block directly before the function line
  - Validates the modified source syntax using tree-sitter parser if available
  - Writes modified source back to file with UTF-8 encoding

  Edge cases:
  - Handles empty docstring lines by outputting " *" without trailing content
  - Stops backward search if non-comment code is encountered before finding JSDoc start
  - Gracefully handles missing tree-sitter parser (validation is optional)
  - Normalizes line indices to handle 1-indexed input against 0-indexed internal arrays
    deps:
      calls:
        - ValueError
        - candidate.insert
        - docstring.split
        - endswith
        - filepath.read_text
        - filepath.write_text
        - getattr
        - join
        - jsdoc_lines.append
        - len
        - list
        - lstrip
        - max
        - range
        - s.endswith
        - s.startswith
        - self.validate_syntax_string
        - source.split
        - strip
      imports:
        - __future__.annotations
        - logging
        - pathlib.Path
        - re
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  JSDoc blocks must be precisely positioned and formatted to be recognized by documentation generators and IDE tooling.
  The backward search with a 200-line limit balances finding legitimate preceding comments while avoiding false matches
  with unrelated documentation far above the target. Indentation preservation ensures the generated documentation
  visually aligns with the code structure. Optional tree-sitter validation catches syntax errors early without requiring
  external tooling to be mandatory. In-place file modification allows integration into automated documentation workflows.

guardrails:
  - DO NOT assume the file encoding is anything other than UTF-8; explicitly handle encoding errors to prevent silent data corruption
  - DO NOT search backward indefinitely; the 200-line limit prevents pathological performance on large files with many comments
  - DO NOT replace JSDoc blocks that are not immediately preceding the function; verify start_replace <= end_replace < func_line_idx to avoid replacing unrelated documentation
  - DO NOT fail silently if tree-sitter validation is unavailable; use getattr with defaults to gracefully degrade
  - DO NOT modify the file if syntax validation fails; call validate_syntax_string before write_text to prevent introducing broken code
  - DO NOT assume the target line exists; validate func_line_idx is within bounds before accessing lines array

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## gather_metadata

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:590`

### Raw YAML Block

```yaml
what: |
  Extracts structural metadata from a Python source file for a specified function using tree-sitter parsing.

  Inputs:
    - filepath: Path object pointing to a Python source file
    - function_name: string identifier of the target function to analyze

  Outputs:
    - Dictionary with three keys:
      - 'calls': list of function names called within the target function
      - 'imports': list of import statements present in the file
      - 'called_by': empty list (cross-file analysis not yet implemented)

  Behavior:
    - Returns early with empty metadata dict if tree-sitter parser is unavailable
    - Attempts to read file with UTF-8 encoding; returns empty dict on IOError or UnicodeDecodeError
    - Parses source code into AST using tree-sitter; returns empty dict on parse failure
    - Delegates extraction logic to helper methods (_extract_function_calls, _extract_imports)
    - Gracefully degrades to empty results rather than raising exceptions

  Edge cases:
    - Missing or inaccessible files: returns empty metadata
    - Files with encoding issues: returns empty metadata
    - Malformed Python syntax: returns empty metadata
    - tree-sitter unavailable: returns empty metadata immediately
    - 'called_by' field is placeholder; cross-file call graph analysis not implemented
    deps:
      calls:
        - f.read
        - open
        - parser.parse
        - self._extract_function_calls
        - self._extract_imports
        - source.encode
      imports:
        - __future__.annotations
        - logging
        - pathlib.Path
        - re
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  Defensive error handling ensures the metadata extraction pipeline remains robust when encountering file system issues, encoding problems, or syntactically invalid code. Early return for unavailable tree-sitter prevents unnecessary file I/O. Delegating extraction to helper methods maintains separation of concerns and allows independent testing of parsing logic. Returning empty dicts instead of raising exceptions allows callers to handle missing metadata gracefully without try-catch overhead.

guardrails:
  - DO NOT assume tree-sitter is available; check _tree_sitter_available flag first to avoid runtime errors on systems without native bindings
  - DO NOT raise exceptions for file I/O or parse failures; return empty metadata dict to maintain caller stability
  - DO NOT implement cross-file 'called_by' analysis in this method; it requires separate indexing infrastructure and should be deferred to a dedicated call-graph builder
  - DO NOT modify the source file or cache results; this method must be side-effect-free for safe repeated invocation
  - DO NOT assume function_name exists in the file; extraction helpers must handle missing targets gracefully

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## validate_syntax

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:678`

### Raw YAML Block

```yaml
what: |
  Validates JavaScript syntax by reading a file from disk and re-parsing its contents.

  **Inputs:**
  - filepath: Path object pointing to a JavaScript source file

  **Outputs:**
  - Returns True if the file contains valid JavaScript syntax
  - Raises ValueError if the file cannot be read or contains invalid syntax

  **Behavior:**
  1. Opens the file at the given filepath with UTF-8 encoding
  2. Reads the entire file contents into memory as a string
  3. Delegates syntax validation to validate_syntax_string() method
  4. Propagates any ValueError raised by the validation method

  **Edge Cases:**
  - File does not exist: IOError caught and wrapped in ValueError
  - File is not readable (permissions): IOError caught and wrapped in ValueError
  - File contains invalid UTF-8 sequences: UnicodeDecodeError caught and wrapped in ValueError
  - Empty files: Passed to validate_syntax_string() for handling
  - Very large files: Entire contents loaded into memory (potential memory concern)
  - Symbolic links and special files: Handled by standard open() behavior
    deps:
      calls:
        - ValueError
        - f.read
        - open
        - self.validate_syntax_string
      imports:
        - __future__.annotations
        - logging
        - pathlib.Path
        - re
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  This method provides a file-based entry point to syntax validation, abstracting away I/O concerns from the core validation logic. By delegating to validate_syntax_string(), it maintains separation of concerns: file handling is isolated from parsing logic, making both easier to test and reuse independently. The explicit exception wrapping (IOError/UnicodeDecodeError → ValueError) provides a consistent error contract to callers, who need not handle multiple exception types. Re-parsing the source (rather than using cached AST or metadata) ensures validation reflects the actual current file state on disk.

guardrails:
  - DO NOT assume the file encoding is anything other than UTF-8; explicitly specify encoding to avoid platform-dependent defaults
  - DO NOT silently ignore read errors; wrap and re-raise as ValueError to maintain consistent error semantics with validate_syntax_string()
  - DO NOT load extremely large files without considering memory implications; callers should validate file size if needed
  - DO NOT modify the file or its permissions during validation; this is a read-only operation
  - DO NOT cache file contents across calls; always re-read to detect external modifications

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## validate_syntax_string

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:747`

### Raw YAML Block

```yaml
what: |
  Validates JavaScript, TypeScript, and TSX source code syntax using tree-sitter parsing.

  Accepts a source code string and optional filepath. Selects the appropriate parser based on file extension:
  - .tsx files use tsx_parser
  - .ts files use ts_parser
  - .js, .mjs, .jsx files use js_parser (or default js_parser if no filepath provided)

  Encodes the source string to UTF-8 bytes and parses it into an abstract syntax tree (AST).
  Inspects the resulting tree for ERROR nodes, which indicate parse failures or syntax violations.

  Returns True if parsing succeeds with no ERROR nodes present.
  Raises ValueError with descriptive message if ERROR nodes are detected in the tree.
  Raises RuntimeError if tree-sitter is not available in the runtime environment.

  Edge cases:
  - Empty source strings parse successfully (valid empty program)
  - Filepath parameter is optional; omission defaults to JavaScript parser
  - File extension matching is case-insensitive
  - UTF-8 encoding handles Unicode characters in source code
  - Malformed syntax produces ERROR nodes rather than exceptions during parsing
    deps:
      calls:
        - RuntimeError
        - ValueError
        - parser.parse
        - self._has_error_nodes
        - source.encode
        - suffix.lower
      imports:
        - __future__.annotations
        - logging
        - pathlib.Path
        - re
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  Tree-sitter provides robust, incremental parsing for multiple language variants without requiring external processes or language runtimes.
  Parser selection by file extension ensures language-specific syntax rules are applied (e.g., TypeScript type annotations, JSX elements).
  ERROR node detection is the standard tree-sitter pattern for identifying parse failures without exception handling overhead.
  UTF-8 encoding is required by tree-sitter's C API and handles modern JavaScript source files universally.
  Returning boolean on success and raising exceptions on failure provides clear success/failure semantics for validation workflows.

guardrails:
  - DO NOT assume tree-sitter is installed; always check _tree_sitter_available flag first to avoid ImportError at runtime
  - DO NOT parse untrusted source without resource limits; tree-sitter can consume significant memory on pathologically nested code
  - DO NOT rely on ERROR node detection alone for security validation; syntax validity does not imply semantic safety
  - DO NOT modify the source string before encoding; preserve original whitespace and line endings for accurate error reporting
  - DO NOT use this for runtime code execution validation; syntax validation does not guarantee the code is safe to execute

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## get_comment_delimiters

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:832`

### Raw YAML Block

```yaml
what: |
  Returns a tuple of two strings representing the standard JSDoc multi-line comment delimiters used in JavaScript.

  Output: A tuple containing exactly two elements:
  - First element: '/**' (opening delimiter for JSDoc blocks)
  - Second element: '*/' (closing delimiter for JSDoc blocks)

  This method provides the canonical comment syntax for JavaScript documentation generation tools. JSDoc is the de facto standard for documenting JavaScript code and is recognized by IDEs, linters, and documentation generators.

  The delimiters are hardcoded and language-specific, reflecting JavaScript's fixed syntax for multi-line comments. No parameters are required as the delimiters are invariant for the JavaScript language.

  Edge cases: None applicable—the return value is constant and deterministic.
    deps:
      imports:
        - __future__.annotations
        - logging
        - pathlib.Path
        - re
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  This method abstracts language-specific comment syntax into a consistent interface. By centralizing delimiter definitions, the codebase can programmatically generate or parse documentation blocks without hardcoding language details throughout the adapter layer.

  The tuple return type (rather than separate methods or a dict) provides a lightweight, ordered pair that maps directly to opening and closing delimiters, making it intuitive for callers to unpack and use immediately.

  JSDoc delimiters are standardized and non-configurable in JavaScript, so a static return is appropriate and efficient.

guardrails:
  - DO NOT modify the returned delimiters at runtime—they are language-defined constants and changing them would break JSDoc compliance and IDE recognition.
  - DO NOT assume these delimiters work for single-line comments—JSDoc requires multi-line comment syntax; use '//' only for non-documentation comments.
  - DO NOT return delimiters in reverse order—callers expect (opening, closing) tuple order for correct block construction.

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## parse

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:881`

### Raw YAML Block

```yaml
what: |
  Parses JavaScript source code into a tree-sitter Tree object for syntactic analysis.

  **Inputs:**
  - source_code (str): Raw JavaScript source code to be parsed

  **Outputs:**
  - tree-sitter Tree object: Abstract syntax tree representation of the input code, enabling traversal and node inspection

  **Behavior:**
  - Encodes the input string to UTF-8 bytes before passing to the underlying tree-sitter parser
  - Returns the complete parse tree, including all nodes and their relationships
  - Raises RuntimeError if tree-sitter is not available (checked via _tree_sitter_available flag)

  **Edge Cases:**
  - Empty strings: Will parse successfully, returning a minimal tree with root node
  - Malformed JavaScript: tree-sitter will still produce a tree with error nodes; does not raise an exception
  - Non-UTF-8 compatible strings: Encoding step may fail if source_code contains invalid UTF-8 sequences
  - Very large files: No built-in size limits, but memory usage scales with code size
    deps:
      calls:
        - RuntimeError
        - parser.parse
        - source_code.encode
      imports:
        - __future__.annotations
        - logging
        - pathlib.Path
        - re
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  tree-sitter provides incremental, robust parsing that handles incomplete or malformed code gracefully, making it suitable for IDE-like use cases and incremental analysis. UTF-8 encoding is the standard for tree-sitter's byte-based API. The availability check prevents cryptic downstream errors when the native tree-sitter library is not installed. Returning the raw Tree object preserves flexibility for callers to traverse and analyze the AST according to their needs.

guardrails:
  - DO NOT assume the returned tree is always valid or error-free; tree-sitter produces partial trees for malformed code, so callers must inspect error nodes
  - DO NOT pass non-string types to source_code; the encode() call will fail on non-string inputs
  - DO NOT rely on this method to validate JavaScript syntax; use the tree's error nodes to detect parse failures
  - DO NOT cache or reuse Tree objects across multiple parse calls without understanding tree-sitter's memory model; trees may reference shared parser state

    changelog:
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## _find_preceding_jsdoc

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:940`

### Raw YAML Block

```yaml
what: |
  Searches backward from a given line number to locate a JSDoc comment block (/** ... */) that immediately precedes a function or class declaration. Returns the extracted JSDoc content as a string, or None if no valid JSDoc is found or tree-sitter is unavailable.

  Inputs:
    - source: Full source code as a single string
    - tree: AST tree object (currently unused but available for future enhancement)
    - lineno: Line number of the function/class declaration (1-indexed)

  Outputs:
    - String containing extracted JSDoc content if found
    - None if tree-sitter is disabled, no JSDoc found, or extraction fails

  Behavior:
    1. Returns None immediately if tree-sitter is not available (graceful degradation)
    2. Splits source into lines and searches backward from lineno-2 up to 50 lines prior
    3. Identifies JSDoc end marker (*/) and then searches backward for start marker (**)
    4. Extracts comment lines between markers and processes via _extract_jsdoc_content()
    5. Returns processed content if non-empty, otherwise continues searching or returns None
    6. Stops searching after finding first complete JSDoc block or reaching 50-line boundary

  Edge cases:
    - lineno beyond source length: safely skipped via bounds check
    - Malformed JSDoc (missing /** or **): ignored, search continues
    - Multiple JSDoc blocks in 50-line window: returns first (closest) one found
    - Empty JSDoc content after extraction: treated as invalid, search continues
    - tree-sitter unavailable: returns None without attempting parse
    deps:
      calls:
        - len
        - line.endswith
        - max
        - range
        - self._extract_jsdoc_content
        - source.split
        - strip
      imports:
        - __future__.annotations
        - logging
        - pathlib.Path
        - re
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  JSDoc comments are critical metadata for JavaScript/TypeScript documentation extraction. Searching backward from declaration line is efficient because JSDoc conventionally appears immediately above the declaration. The 50-line limit prevents excessive backward scanning in large files while accommodating reasonable comment spacing. Graceful fallback to None when tree-sitter is unavailable allows the adapter to function in degraded mode. Delegating content extraction to _extract_jsdoc_content() maintains separation of concerns and allows flexible comment normalization.

guardrails:
  - DO NOT assume lineno is always valid or within source bounds; always check array indices to prevent IndexError
  - DO NOT search beyond 50 lines backward; this prevents performance degradation on large files and catches only reasonably-positioned JSDoc
  - DO NOT return partial or malformed JSDoc; validate via _extract_jsdoc_content() to ensure content quality
  - DO NOT proceed if tree-sitter is unavailable; the early return prevents cascading failures in downstream parsing
  - DO NOT assume JSDoc markers are on separate lines; handle cases where /** and */ may share lines with code

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## _extract_jsdoc_content

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:1032`

### Raw YAML Block

```yaml
what: |
  Extracts the textual content from JSDoc comment lines by removing JSDoc syntax markers and normalizing whitespace.

  Input: A list of strings representing lines from a JSDoc comment block (e.g., ['/**', ' * @param foo description', ' */'])

  Processing:
  - Skips lines that are pure JSDoc delimiters (lines starting with '/**' or ending with '*/')
  - Removes leading asterisk ('*') from each line and strips surrounding whitespace
  - Filters out empty lines after normalization
  - Joins remaining content lines with newline characters

  Output: A single string containing the cleaned docstring content without JSDoc markup

  Edge cases:
  - Handles mixed indentation and spacing around asterisks
  - Preserves internal content structure and line breaks
  - Returns empty string if input contains only JSDoc delimiters or whitespace
  - Does not parse or validate JSDoc tags (@param, @returns, etc.) — only removes syntax markers
    deps:
      calls:
        - content.append
        - join
        - line.strip
        - lstrip
        - stripped.endswith
        - stripped.startswith
      imports:
        - __future__.annotations
        - logging
        - pathlib.Path
        - re
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  JSDoc comments use a specific syntax (/** ... */) that must be stripped to extract human-readable documentation.
  This function normalizes the raw comment lines into clean text suitable for downstream processing or display.
  By separating syntax removal from semantic parsing, the function maintains a single responsibility and allows
  tag parsing to operate on clean content. The line-by-line approach handles variable indentation gracefully
  without requiring regex or complex state machines.

guardrails:
  - DO NOT assume consistent indentation — JSDoc lines may have varying leading whitespace before the asterisk
  - DO NOT strip internal whitespace or collapse multiple spaces within content — preserve formatting intent
  - DO NOT attempt to parse JSDoc tags in this function — that is a separate concern for tag extraction
  - DO NOT return lines that are only whitespace — empty lines should be filtered to avoid spurious newlines
  - DO NOT modify the order or structure of content lines — maintain document flow for downstream consumers

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## _find_node_at_line

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:1105`

### Raw YAML Block

```yaml
what: |
  Locates a function or class declaration node at a specific line number within a tree-sitter AST.

  **Inputs:**
  - tree: A tree-sitter Tree object containing the parsed AST
  - lineno: Target line number (1-based indexing) to search for

  **Outputs:**
  - Returns the AST node if a matching function/class declaration is found at the exact line
  - Returns None if tree-sitter is unavailable, no match exists, or tree is malformed

  **Behavior:**
  - Performs depth-first recursive traversal of the AST starting from tree.root_node
  - Converts tree-sitter's 0-based line numbering to 1-based for comparison
  - Matches against five node types: function_declaration, arrow_function, function_expression, method_definition, class_declaration
  - Returns immediately upon first match (does not continue searching siblings after finding a result)
  - Handles missing or None nodes gracefully without raising exceptions

  **Edge cases:**
  - Returns None if _tree_sitter_available flag is False (graceful degradation)
  - Handles sparse ASTs where target line has no declaration
  - Correctly processes nested declarations (inner functions/classes)
  - Works with arrow functions and method definitions in addition to standard declarations
    deps:
      calls:
        - find_in_node
      imports:
        - __future__.annotations
        - logging
        - pathlib.Path
        - re
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  Tree-sitter provides fast, incremental parsing with precise line/column information needed for accurate source mapping.
  The recursive approach is natural for AST traversal and avoids maintaining explicit stack state.
  Early return on match optimizes for common case where declarations are not deeply nested.
  The availability check prevents runtime errors when tree-sitter is not installed or initialized.
  1-based line numbering conversion aligns with editor conventions and user expectations.

guardrails:
  - DO NOT assume tree.root_node exists without checking—malformed or uninitialized trees may cause AttributeError
  - DO NOT modify node state during traversal; this is a read-only inspection operation
  - DO NOT search beyond the first matching node at the target line—multiple declarations on same line are ambiguous and first match is sufficient
  - DO NOT rely on this function for line ranges; it only matches exact line numbers where declaration starts
  - DO NOT skip the _tree_sitter_available check—calling without it may fail if tree-sitter dependency is missing

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## find_in_node

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:1170`

### Raw YAML Block

```yaml
what: |
  Recursively traverses a tree-sitter AST to locate a function or class declaration at a specific target line number. Accepts a node parameter (typically the root of an AST subtree) and searches depth-first through all children until finding a node whose type matches one of the supported declaration types (function_declaration, arrow_function, function_expression, method_definition, class_declaration) AND whose start line equals the target lineno.

  Inputs: node (tree-sitter Node object or None), lineno (integer, 1-based line number from caller context)
  Outputs: Returns the matching tree-sitter Node object if found, otherwise None

  Edge cases handled:
  - Null/None node input returns None immediately (base case)
  - Line number conversion: tree-sitter uses 0-based indexing; function adds 1 to node.start_point[0] to match 1-based line numbers expected by callers
  - Multiple nested declarations at same line: returns first match found via depth-first traversal
  - No matching declaration at target line: returns None after exhausting all children
    deps:
      calls:
        - find_in_node
      imports:
        - __future__.annotations
        - logging
        - pathlib.Path
        - re
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  Tree-sitter provides efficient incremental parsing and precise AST node location data. Recursive depth-first search is the natural traversal pattern for AST structures and avoids maintaining explicit stack state. Converting to 1-based line numbers at the node level (rather than at call sites) centralizes the indexing logic and reduces caller burden. Early return on match optimizes for the common case where target is found in a shallow subtree.

guardrails:
  - DO NOT assume node.start_point exists without checking node is not None first; tree-sitter nodes may have incomplete metadata in edge cases
  - DO NOT modify the node object or its children during traversal; this function must be read-only to preserve AST integrity for subsequent operations
  - DO NOT rely on this function to disambiguate between multiple declarations at the same line; if multiple functions/classes start at lineno, only the first discovered is returned (depth-first order)
  - DO NOT use this on unparsed or malformed AST trees; caller must ensure tree-sitter parsing succeeded before invoking

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## _extract_function_calls

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:1237`

### Raw YAML Block

```yaml
what: |
  Extracts all unique function call names from within a specific function's AST subtree.

  **Inputs:**
  - tree: A tree-sitter Tree object (or object with root_node attribute) representing parsed source code
  - source: The original source code string, used to extract call names from AST nodes
  - function_name: The name of the target function (currently unused in extraction logic; caller responsible for tree scoping)

  **Outputs:**
  - Returns a sorted list of unique function call names (strings) found within the function body
  - Returns empty list if tree-sitter is unavailable

  **Behavior:**
  - Performs depth-first recursive traversal of the AST starting from tree.root_node
  - Identifies all nodes with type 'call_expression'
  - Extracts the call name from each call_expression node via _extract_call_name helper
  - Deduplicates results using set conversion before sorting
  - Gracefully degrades to empty list if tree-sitter dependency is not available

  **Edge Cases:**
  - Handles missing or None nodes without crashing (early return in recursion)
  - Filters out None/empty call names returned by _extract_call_name
  - Works with any tree-sitter compatible language parser (not JavaScript-specific despite file location)
    deps:
      calls:
        - calls.append
        - collect_calls
        - hasattr
        - list
        - self._extract_call_name
        - set
        - sorted
      imports:
        - __future__.annotations
        - logging
        - pathlib.Path
        - re
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  Recursive tree traversal is necessary because call_expression nodes can appear at arbitrary depths within nested scopes (blocks, conditionals, loops). Deduplication and sorting provide a canonical, deterministic output suitable for dependency analysis and comparison. The tree-sitter availability check prevents runtime errors in environments where the native binding is not installed. Delegating call name extraction to _extract_call_name allows language-specific parsing logic to be isolated and reused.

guardrails:
  - DO NOT assume tree.root_node exists without checking hasattr; some tree-sitter versions or mock objects may not expose this attribute
  - DO NOT skip the tree-sitter availability check; calling tree-sitter methods when unavailable will raise AttributeError
  - DO NOT rely on function_name parameter for filtering; the caller must pass a pre-scoped tree containing only the target function's AST
  - DO NOT return unsorted or non-deduplicated results; callers depend on canonical ordering for caching and comparison
  - DO NOT assume _extract_call_name always returns a non-empty string; filter out falsy values to avoid polluting the call list

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## collect_calls

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:1305`

### Raw YAML Block

```yaml
what: |
  Recursively traverses an Abstract Syntax Tree (AST) node and its descendants to identify and collect all function/method call expressions. For each node of type 'call_expression' encountered, extracts the call name using the _extract_call_name helper method and appends it to a calls list if extraction succeeds. The recursion terminates when a None node is encountered or when all children have been processed. Handles edge cases where call_name extraction returns None or falsy values by skipping those entries. Returns implicitly via side-effect mutation of the outer scope's calls list.

  Inputs: node (AST node object with .type and .children attributes, or None)
  Outputs: None (side-effect: populates calls list in enclosing scope)
  Edge cases: None nodes, nodes without children attribute, failed call name extraction, deeply nested AST structures
    deps:
      calls:
        - calls.append
        - collect_calls
        - self._extract_call_name
      imports:
        - __future__.annotations
        - logging
        - pathlib.Path
        - re
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set

why: |
  Recursive tree traversal is the natural approach for AST analysis since call expressions can appear at arbitrary nesting depths. Using a nested function allows access to the outer scope's calls list and source context without parameter threading. Early None-check prevents AttributeError on null nodes. Conditional append only on successful extraction avoids polluting results with None or empty strings, maintaining data quality.
guardrails:
  - DO NOT assume node.children exists without type checking—some AST implementations may have sparse or missing children attributes, causing AttributeError
  - DO NOT skip the None guard at function entry—recursive calls may pass None and cause crashes if not handled
  - DO NOT append call_name without truthiness validation—failed extractions (None, empty string) corrupt the calls collection
  - DO NOT use this function on extremely deep AST trees without stack depth monitoring—Python's default recursion limit (~1000) may be exceeded on pathological inputs

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## _extract_call_name

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:1358`

### Raw YAML Block

```yaml
what: |
  Extracts the name of a called function from a tree-sitter call_expression AST node.

  Takes a call_node (tree-sitter Node object) and the original source code string as inputs.
  Returns the extracted function name as a string, or None if extraction fails.

  Process:
  1. Validates call_node exists and has tree-sitter Node interface (child_by_field_name method)
  2. Retrieves the 'function' child field from the call_node using tree-sitter's field API
  3. Extracts byte offsets (start_byte, end_byte) from the function node
  4. Validates byte range is within source bounds (0 <= start < end <= source length in UTF-8 bytes)
  5. Slices source string using byte offsets and strips whitespace
  6. Returns cleaned name or None if name is empty string

  Edge cases handled:
  - Missing or malformed call_node (returns None)
  - Missing 'function' field in call_node (returns None)
  - Invalid byte ranges or out-of-bounds offsets (returns None)
  - UTF-8 encoding edge cases (byte length validation before slicing)
  - Exception during extraction (caught and returns None)
  - Whitespace-only function names (stripped to None)
    deps:
      calls:
        - call_node.child_by_field_name
        - hasattr
        - len
        - name.strip
        - source.encode
      imports:
        - __future__.annotations
        - logging
        - pathlib.Path
        - re
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  Tree-sitter provides byte-offset-based source extraction rather than direct text in AST nodes.
  This approach:
  - Avoids reliance on tree-sitter's potentially incomplete node.text property
  - Enables precise extraction by directly indexing the source with validated byte offsets
  - Handles UTF-8 multi-byte characters correctly by validating encoded byte length
  - Provides defensive null-checking at each step to prevent crashes on malformed AST
  - Strips whitespace to normalize function names that may include formatting

  Tradeoff: Requires passing original source string (memory overhead) but ensures accuracy
  for JavaScript call expressions across different syntax variations.

guardrails:
  - DO NOT assume call_node has tree-sitter Node interface without hasattr check; external callers may pass invalid types
  - DO NOT slice source using byte offsets without validating against UTF-8 encoded length; multi-byte characters can cause index misalignment
  - DO NOT skip the bounds check (0 <= start < end <= len); malformed AST nodes can produce out-of-range offsets
  - DO NOT return whitespace-only strings; strip and convert empty results to None for consistent null semantics
  - DO NOT let exceptions propagate; catch all exceptions during extraction to maintain robustness in AST traversal loops

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## _extract_imports

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:1444`

### Raw YAML Block

```yaml
what: |
  Recursively traverses a tree-sitter parse tree to extract import statements from JavaScript/TypeScript source code.

  Inputs:
    - tree: A tree-sitter Tree object (or None if tree-sitter unavailable)
    - source: The original source code string as UTF-8 encoded text

  Outputs:
    - List[str]: Deduplicated list of import statement text strings extracted from the source

  Behavior:
    - Returns empty list immediately if tree-sitter is not available (graceful degradation)
    - Recursively traverses all nodes in the parse tree via depth-first traversal
    - Identifies import nodes by type: 'import_statement', 'import_clause', or 'require_clause'
    - Extracts raw source text using byte offsets (start_byte, end_byte) from the tree node
    - Validates byte offsets are within bounds of UTF-8 encoded source before extraction
    - Strips whitespace from extracted import text and filters empty strings
    - Silently catches and ignores any extraction exceptions (malformed nodes, encoding issues)
    - Deduplicates results using set() before returning

  Edge cases:
    - Tree-sitter unavailable: returns empty list without error
    - Malformed parse tree or invalid byte offsets: silently skipped via exception handling
    - Empty or whitespace-only import nodes: filtered out
    - UTF-8 encoding edge cases: bounds checking prevents index errors
    - Duplicate imports in source: automatically deduplicated in output
    deps:
      calls:
        - collect_imports
        - hasattr
        - imports.append
        - len
        - list
        - set
        - source.encode
        - strip
      imports:
        - __future__.annotations
        - logging
        - pathlib.Path
        - re
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  Tree-sitter provides precise AST parsing for multiple languages including JavaScript. Using byte offsets directly from the parse tree is more reliable than regex-based extraction because it respects actual syntax boundaries and handles complex nested structures.

  Deduplication via set() is applied at the end rather than during collection to avoid repeated set operations during recursion, improving performance for large trees.

  Silent exception handling is intentional: malformed nodes or encoding issues should not crash the entire import extraction process. This allows partial extraction to succeed even if some nodes are problematic.

  The bounds check (0 <= start < end <= len(source.encode('utf-8'))) prevents index errors and handles edge cases where tree-sitter offsets might be slightly out of sync with the actual source encoding.

guardrails:
  - DO NOT assume tree-sitter is always available; always check _tree_sitter_available flag first to prevent AttributeError
  - DO NOT use string slicing directly on byte offsets without validating bounds; UTF-8 encoding can have variable-width characters that cause index misalignment
  - DO NOT re-encode source on every bounds check; cache the encoded length or validate offsets against the original string length to avoid performance degradation
  - DO NOT raise exceptions on malformed nodes; silently skip them to allow partial extraction and maintain robustness
  - DO NOT skip deduplication; imports may appear multiple times in source and duplicates should be removed before returning

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## collect_imports

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:1526`

### Raw YAML Block

```yaml
what: |
  Recursively traverses a tree-sitter AST node to extract and collect import statements from source code.

  Behavior:
  - Accepts a tree-sitter node object (or None)
  - Returns early if node is falsy to prevent recursion errors
  - Identifies import-related nodes by type: 'import_statement', 'import_clause', 'require_clause'
  - For matching nodes, extracts byte range (start_byte to end_byte) and validates bounds against UTF-8 encoded source length
  - Slices source code using byte indices, strips whitespace, and appends non-empty import text to shared imports list
  - Silently catches and ignores any extraction exceptions to prevent parse failures from blocking traversal
  - Recursively processes all child nodes depth-first

  Inputs:
  - node: tree-sitter Node object or None
  - Implicit dependency on outer scope: source (string), imports (list accumulator)

  Outputs:
  - Mutates imports list by appending extracted import statement strings
  - Returns None

  Edge cases:
  - Handles None/falsy nodes gracefully
  - Validates byte indices are within valid range before slicing
  - Tolerates UTF-8 encoding edge cases and extraction errors
  - Processes nodes with no children without error
    deps:
      calls:
        - collect_imports
        - imports.append
        - len
        - source.encode
        - strip
      imports:
        - __future__.annotations
        - logging
        - pathlib.Path
        - re
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  Tree-sitter provides byte-indexed AST nodes that require careful boundary validation when slicing source text, especially with multi-byte UTF-8 characters. Recursive traversal is necessary because import statements can appear at various nesting levels in the AST. Silent exception handling prevents a single malformed node from halting the entire import collection process, prioritizing robustness over strict error reporting. The byte-range validation guards against off-by-one errors and corrupted AST metadata that could cause index out-of-bounds exceptions.

guardrails:
  - DO NOT assume node.start_byte and node.end_byte are always valid—always validate against encoded source length to prevent IndexError on corrupted or edge-case AST nodes
  - DO NOT use string indices directly on source without converting byte indices, as Python string indexing is character-based and will misalign with multi-byte UTF-8 sequences
  - DO NOT re-raise exceptions during import extraction—silent failure ensures one malformed import statement does not block collection of valid imports from sibling/parent nodes
  - DO NOT modify the source string or node structure during traversal—only append to the imports accumulator to maintain functional purity and prevent side effects
  - DO NOT assume all nodes have a children attribute—always iterate safely or check hasattr to avoid AttributeError on leaf nodes

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## _has_error_nodes

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:1609`

### Raw YAML Block

```yaml
what: |
  Recursively inspects a tree-sitter parse tree to detect parsing failures and syntax errors.

  Returns True if the tree contains ERROR nodes (indicating malformed syntax that tree-sitter could not parse) or MISSING nodes (indicating incomplete or invalid syntax such as unclosed JSX tags).

  Returns True immediately if the input tree is None, falsy, or lacks a root_node attribute, treating these as error conditions.

  The function performs depth-first traversal of the tree starting from root_node. For each node:
  - Checks if node.type equals 'ERROR' (direct parse failure indicator)
  - Checks if 'MISSING' string appears in node.sexp() output (incomplete syntax indicator that doesn't surface as node.type)
  - Recursively checks all child nodes

  Returns False only if tree is valid, has a root_node, and no ERROR or MISSING nodes exist anywhere in the tree hierarchy.
    deps:
      calls:
        - has_errors
        - hasattr
        - node.sexp
      imports:
        - __future__.annotations
        - logging
        - pathlib.Path
        - re
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  Tree-sitter represents parse failures in two distinct ways: ERROR nodes for syntax it cannot parse, and MISSING nodes for incomplete constructs (e.g., unclosed JSX tags). Checking only node.type misses MISSING nodes since they appear in the s-expression representation but not as a distinct type. This dual-check approach ensures comprehensive error detection across both failure modes.

  Early return on invalid tree input (None, no root_node) treats malformed input as an error condition rather than silently returning False, which is safer for downstream consumers expecting a valid parse tree.

  Recursive traversal ensures errors deep in the tree are not missed, which is critical for validating complete parse trees before further processing.

guardrails:
  - DO NOT rely solely on node.type == 'ERROR' without checking sexp() for MISSING nodes, as incomplete syntax (unclosed tags) will be missed
  - DO NOT assume tree.root_node exists without hasattr check, as malformed or None trees will cause AttributeError
  - DO NOT skip the initial tree validity check (if not tree or not hasattr), as None or invalid trees should signal error state
  - DO NOT assume all nodes have a sexp() method; use hasattr guard to prevent AttributeError on nodes that lack this method
  - DO NOT modify the tree during traversal; this is a read-only inspection function

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## has_errors

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/javascript_adapter.py:1666`

### Raw YAML Block

```yaml
what: |
  Recursively traverses a tree-sitter parse tree node to detect syntax errors and incomplete syntax.

  Returns True if any error condition is found, False otherwise.

  Detection logic:
  - Returns False immediately if node is None or falsy (base case for recursion)
  - Checks node.type == 'ERROR': tree-sitter marks malformed syntax with ERROR node type
  - Checks for 'MISSING' string in node.sexp() output: tree-sitter represents incomplete syntax (e.g., unclosed tags, missing tokens) as MISSING in s-expression form, even though MISSING does not appear as a direct node.type value
  - Recursively checks all child nodes via node.children, returning True on first error found in any subtree
  - Returns False only if node exists and no errors detected in node or any descendants

  Inputs: node (tree-sitter Node object or None)
  Outputs: boolean indicating presence of syntax errors or incomplete syntax anywhere in subtree

  Edge cases:
  - Handles None/falsy nodes gracefully (returns False)
  - Handles nodes without sexp() method via hasattr check (defaults to empty string)
  - Short-circuits recursion on first error found for efficiency
    deps:
      calls:
        - has_errors
        - hasattr
        - node.sexp
      imports:
        - __future__.annotations
        - logging
        - pathlib.Path
        - re
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  Tree-sitter represents syntax problems in two distinct ways that must both be checked:
  1. ERROR node type for malformed/unparseable syntax
  2. MISSING token in s-expression for incomplete syntax (unclosed delimiters, missing required tokens)

  Checking only node.type would miss incomplete syntax. Checking only sexp() would be inefficient and miss some error types. Recursive traversal ensures errors anywhere in the parse tree are caught, not just at the root level.

  This approach prioritizes correctness (catching all error types) over performance, which is appropriate for syntax validation where missing an error is worse than slight overhead.

guardrails:
  - DO NOT rely solely on node.type == 'ERROR' without checking sexp() for MISSING, as incomplete syntax is not marked with ERROR type
  - DO NOT assume all nodes have sexp() method; use hasattr guard to prevent AttributeError on unexpected node types
  - DO NOT skip recursive checks on child nodes; errors can be nested deep in the tree and must be detected
  - DO NOT return True prematurely without checking all children if an error is found at current level, as the function should detect any error in the entire subtree

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-11-01: chore: sync agent configuration files (AGENTS.md, CLAUDE.md, .cursor/.rules) (9c93cab)"
      - "- 2025-10-31: feat: Implement tree-sitter JavaScript adapter with full metadata extraction (69cf4c6)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
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

### Raw YAML Block

```yaml
what: |
  Returns a set containing the file extensions that the Python adapter is responsible for handling. Specifically returns {'.py', '.pyi'}, representing Python source files and Python stub files respectively.

  The method takes no parameters beyond self and returns a Set[str] containing exactly two string elements: '.py' for standard Python source code files and '.pyi' for Python type stub files used by type checkers and IDEs.

  This is a read-only accessor that provides a consistent interface for querying which file types this adapter processes. The returned set is immutable in intent (though technically mutable as a set object) and should be treated as a constant definition of the adapter's scope.

  Edge cases: The method always returns the same set regardless of adapter state or configuration. There are no conditional branches or dynamic behavior—it is purely declarative.
    deps:
      imports:
        - __future__.annotations
        - ast
        - inspect
        - pathlib.Path
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  This method exists to provide a standardized way for the adapter framework to determine file type compatibility without hardcoding extension lists throughout the codebase. By centralizing extension definitions in the adapter itself, the system can dynamically discover which file types each language adapter supports.

  The choice to include both '.py' and '.pyi' reflects that Python type stubs are semantically part of the Python ecosystem and should be processed with the same logic as source files. This design allows a single adapter to handle both file types rather than requiring separate adapters.

  Returning a set (rather than a list or tuple) emphasizes that order is irrelevant and membership testing is the primary use case, which is semantically clearer and potentially more efficient for lookups.

guardrails:
  - DO NOT modify the returned set in-place, as it may be cached or reused by the framework; treat the return value as read-only
  - DO NOT add or remove extensions dynamically based on runtime state; this method should always return the same set to maintain predictable adapter behavior
  - DO NOT return extensions without the leading dot (e.g., 'py' instead of '.py'), as the framework expects normalized extension format with dots

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## discover_files

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/python_adapter.py:113`

### Raw YAML Block

```yaml
what: |
  Discovers all Python files within a target directory or returns a single file if target is a file path.

  Accepts a Path object pointing to either a directory or a file. When given a directory, recursively collects all Python source files (.py extension) from that directory tree. When given a file path, returns that file wrapped in a list.

  Delegates to agentspec.utils.collect_python_files() for the actual discovery logic, which applies intelligent filtering:
  - Respects .gitignore rules to exclude version-controlled ignored paths
  - Excludes common non-source directories: .venv, venv, __pycache__, .git, .tox, node_modules, dist, build, *.egg-info
  - Skips hidden directories (prefixed with .)
  - Returns results as a list of Path objects in consistent order

  Handles edge cases:
  - Empty directories return empty list
  - Symlinks are followed during traversal
  - Permission errors on subdirectories are silently skipped
  - Non-existent paths raise FileNotFoundError from underlying pathlib operations

  Returns: List[Path] - ordered collection of discovered Python file paths, may be empty if no Python files found
    deps:
      calls:
        - collect_python_files
      imports:
        - __future__.annotations
        - ast
        - inspect
        - pathlib.Path
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  Centralizes file discovery logic to ensure consistent behavior across the codebase. Delegating to a shared utility function (collect_python_files) prevents duplication and ensures all adapters respect the same filtering rules.

  Importing collect_python_files locally within the method avoids circular dependency issues that would occur if imported at module level, since utils may import from other adapter modules.

  Respecting .gitignore is important for development workflows where developers intentionally exclude directories from version control (e.g., virtual environments, build artifacts). Including these would pollute analysis results and slow discovery.

  Excluding __pycache__ and build artifacts prevents analyzing stale bytecode or generated files that don't represent actual source intent.

guardrails:
  - DO NOT modify .gitignore during discovery - treat it as read-only configuration that reflects developer intent
  - DO NOT follow symlinks that create cycles - this would cause infinite recursion; rely on os.walk's cycle detection
  - DO NOT raise exceptions for permission-denied on individual files/subdirectories - silently skip them to allow partial discovery of accessible portions
  - DO NOT cache results across calls - each invocation should reflect current filesystem state in case files were added/removed
  - DO NOT assume target path exists before calling - let pathlib raise appropriate FileNotFoundError for missing paths

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## extract_docstring

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/python_adapter.py:173`

### Raw YAML Block

```yaml
what: |
  Extracts the docstring from a Python function, async function, or class definition located at a specific line number in a given file.

  **Inputs:**
  - filepath: Path object pointing to a Python source file
  - lineno: Integer line number where the target function/class is defined

  **Outputs:**
  - Returns the raw docstring as a string if found (including any embedded agentspec YAML blocks)
  - Returns None if the file cannot be parsed, the line number doesn't match any definition, or no docstring exists

  **Behavior:**
  - Opens and reads the file with UTF-8 encoding
  - Parses the entire file into an AST (Abstract Syntax Tree)
  - Walks the AST to find function, async function, or class nodes matching the exact line number
  - Uses ast.get_docstring() to extract the docstring, which handles both raw strings and formatted docstrings
  - Silently returns None on parse failures (SyntaxError, UnicodeDecodeError) rather than raising

  **Edge cases:**
  - File encoding issues: caught and returns None
  - Invalid Python syntax: caught and returns None
  - Line number mismatch: no matching node found, returns None
  - Docstring absence: ast.get_docstring() returns None for definitions without docstrings
  - Multiple definitions on same line: returns docstring of first match found during walk
    deps:
      calls:
        - ast.get_docstring
        - ast.parse
        - ast.walk
        - f.read
        - isinstance
        - open
        - str
      imports:
        - __future__.annotations
        - ast
        - inspect
        - pathlib.Path
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  This approach uses Python's built-in ast module for reliable, syntax-aware parsing rather than regex or line-based text matching. AST parsing correctly handles complex syntax (decorators, nested definitions, multi-line signatures) and provides precise node location matching via lineno. The silent failure mode (returning None) allows callers to gracefully handle unparseable files without exception handling overhead. Using ast.get_docstring() ensures compatibility with PEP 257 docstring conventions and automatically strips leading indentation.

guardrails:
  - DO NOT assume the file is valid Python syntax; always catch SyntaxError and return None rather than propagating exceptions that could crash the extraction pipeline
  - DO NOT use regex-based docstring extraction; it will fail on edge cases like docstrings containing triple quotes or complex string escaping
  - DO NOT modify or validate the docstring content; return it raw to preserve embedded agentspec blocks and allow downstream processors to parse them
  - DO NOT assume lineno uniquely identifies a definition; use exact equality matching and return on first match to handle edge cases consistently
  - DO NOT attempt to handle file I/O errors (PermissionError, FileNotFoundError) separately; let them propagate as they indicate configuration or environment issues, not parsing failures

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## insert_docstring

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/python_adapter.py:249`

### Raw YAML Block

```yaml
what: |
  Inserts or replaces a docstring for a function, async function, or class at a specified line number in a Python source file.

  **Inputs:**
  - filepath: Path object pointing to a Python source file
  - lineno: Integer line number where target function/class definition begins
  - docstring: String content to insert as the docstring (without quotes)

  **Outputs:**
  - Modifies the file in-place; no return value
  - Writes updated source back to filepath with docstring inserted/replaced

  **Behavior:**
  1. Reads entire source file and parses it into an AST
  2. Walks AST to find FunctionDef, AsyncFunctionDef, or ClassDef node at exact lineno
  3. Detects if a docstring already exists (first statement is string Expr)
  4. If docstring exists: replaces lines from docstring start to end
  5. If no docstring: inserts after function/class definition line
  6. Preserves indentation by extracting indent from target node and applying to all docstring lines
  7. Formats docstring with triple double-quotes and writes file back

  **Edge cases:**
  - File with syntax errors raises ValueError
  - No matching function/class at lineno raises ValueError
  - Empty docstring string is valid and produces empty triple-quoted string
  - Multi-line docstrings preserve internal line structure with consistent indentation
  - Handles both old-style ast.Str and new-style ast.Constant string nodes
    deps:
      calls:
        - ValueError
        - _get_indent
        - ast.parse
        - ast.walk
        - chr
        - f.read
        - f.write
        - isinstance
        - join
        - open
        - quoted_docstring.split
        - source.split
        - str
      imports:
        - __future__.annotations
        - ast
        - inspect
        - pathlib.Path
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  AST-based approach ensures precise targeting of the correct definition by line number rather than fragile text pattern matching. Parsing validates file syntax upfront. Walking the tree finds the exact node, avoiding ambiguity with nested functions or classes. Detecting existing docstrings allows safe replacement without duplicating or orphaning old content. Preserving indentation maintains code style consistency. Reading entire file and writing back is simpler than seeking/truncating and avoids partial-write corruption risks.

guardrails:
  - DO NOT assume lineno matches the first line of a multi-line function signature; use AST node.lineno which points to the def/class keyword line
  - DO NOT modify the file if AST parsing fails; raise ValueError to prevent corrupting unparseable source
  - DO NOT attempt to preserve comments or formatting beyond indentation; AST round-trip loses non-semantic whitespace
  - DO NOT insert docstring if target node body is empty; this would create invalid syntax (class/function with only docstring and no pass)
  - DO NOT use string slicing to find old docstring boundaries; rely on AST node.lineno and node.end_lineno for accuracy across quote styles and escape sequences

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## gather_metadata

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/python_adapter.py:369`

### Raw YAML Block

```yaml
what: |
  Extracts static metadata from a Python source file for a specified function using Abstract Syntax Tree (AST) parsing.

  **Inputs:**
  - filepath (Path): File system path to a Python source file
  - function_name (str): Name of the target function to analyze

  **Outputs:**
  - Dict with three keys:
    - 'calls': List of function calls made within the target function
    - 'imports': List of module-level imports in the file
    - 'called_by': List of callers of the target function (currently empty, reserved for future use)

  **Behavior:**
  1. Opens and reads the file with UTF-8 encoding
  2. Parses file contents into an AST
  3. Walks the AST to locate a FunctionDef or AsyncFunctionDef node matching function_name
  4. Extracts function calls from the matched function body using agentspec.collect._get_function_calls()
  5. Extracts all module-level imports using agentspec.collect._get_module_imports()
  6. Returns empty lists for all keys if file cannot be parsed or function not found

  **Edge Cases:**
  - SyntaxError or UnicodeDecodeError during file read returns empty metadata dict
  - Function name not found in AST results in empty 'calls' list but imports still populated
  - Async functions handled identically to sync functions
  - Multiple functions with same name: only first match processed (ast.walk order)
    deps:
      calls:
        - ast.parse
        - ast.walk
        - collect._get_function_calls
        - collect._get_module_imports
        - f.read
        - isinstance
        - open
        - str
      imports:
        - __future__.annotations
        - ast
        - inspect
        - pathlib.Path
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  AST-based static analysis provides accurate, dependency-free extraction of code structure without executing code. This approach:
  - Avoids runtime side effects and security risks of dynamic execution
  - Handles both sync and async functions uniformly
  - Gracefully degrades on malformed Python files rather than crashing
  - Integrates with agentspec.collect utilities for consistent metadata extraction across the codebase
  - Enables dependency graph construction and call chain analysis for documentation and tooling

guardrails:
  - DO NOT execute the parsed code or use eval/exec—AST parsing is intentionally static to prevent arbitrary code execution
  - DO NOT assume function_name is unique—only the first matching function is analyzed; document this limitation if multiple definitions exist
  - DO NOT rely on 'called_by' field—it is currently unpopulated and reserved; do not assume it contains meaningful data
  - DO NOT skip error handling for file I/O—encoding errors and syntax errors are common in large codebases and must return safe defaults
  - DO NOT parse files without UTF-8 encoding declaration without explicit user confirmation—non-UTF-8 files may silently fail or corrupt metadata

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## validate_syntax

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/python_adapter.py:466`

### Raw YAML Block

```yaml
what: |
  Validates Python source file syntax by attempting to compile the file contents.

  **Inputs:**
  - filepath: Path object pointing to a Python source file

  **Outputs:**
  - Returns True if file contains valid Python syntax
  - Raises ValueError (wrapping SyntaxError) if syntax is invalid, with message containing filepath and original error details

  **Behavior:**
  - Opens file with UTF-8 encoding
  - Reads entire file contents into memory
  - Attempts compilation using Python's built-in compile() function with 'exec' mode
  - Catches SyntaxError exceptions and re-raises as ValueError with contextual information

  **Edge cases:**
  - File not found: FileNotFoundError propagates uncaught
  - Encoding errors: UnicodeDecodeError propagates uncaught
  - Empty files: Valid (compile succeeds on empty string)
  - Large files: Entire contents loaded into memory (potential memory concern for very large files)
  - Permission denied: PermissionError propagates uncaught
    deps:
      calls:
        - ValueError
        - compile
        - f.read
        - open
        - str
      imports:
        - __future__.annotations
        - ast
        - inspect
        - pathlib.Path
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  Using compile() with 'exec' mode provides accurate syntax validation matching Python's actual parser behavior, avoiding regex-based or AST-based approximations that could miss edge cases. Re-raising as ValueError provides a consistent exception interface for the adapter layer rather than exposing language-specific SyntaxError. UTF-8 encoding is standard for Python source files per PEP 263. The try-except pattern is minimal and explicit about which error condition is handled, allowing other I/O errors to surface naturally for debugging.

guardrails:
  - DO NOT silently return False on syntax errors—raising an exception forces callers to handle validation failures explicitly rather than accidentally proceeding with invalid code
  - DO NOT catch FileNotFoundError or PermissionError—these indicate environmental issues that should propagate to the caller for proper handling, not be masked as syntax problems
  - DO NOT use ast.parse() as the sole validation method without compile()—compile() catches additional syntax issues that AST parsing might defer
  - DO NOT load entire file into memory without considering file size limits—very large files could cause memory exhaustion; consider streaming or size checks for production use
  - DO NOT modify the exception message format without updating dependent error handling code that may parse the filepath from the ValueError message

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## validate_syntax_string

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/python_adapter.py:531`

### Raw YAML Block

```yaml
what: |
  Validates Python source code syntax by attempting to compile it without execution.

  **Inputs:**
  - source (str): Python source code to validate
  - filepath (Path, optional): File path for error reporting context; defaults to '<string>' if not provided

  **Outputs:**
  - Returns True if syntax is valid
  - Raises ValueError wrapping the original SyntaxError if syntax is invalid

  **Behavior:**
  - Uses Python's built-in compile() function with 'exec' mode to parse the entire source
  - Catches SyntaxError exceptions and re-raises them as ValueError with formatted error message
  - Filepath parameter is converted to string for compile() compatibility; None values are replaced with '<string>' placeholder

  **Edge Cases:**
  - Empty strings compile successfully (valid Python)
  - Incomplete code (e.g., unclosed parentheses) raises SyntaxError → ValueError
  - Unicode and encoding issues in source may raise SyntaxError → ValueError
  - Very large source strings are processed without truncation
  - Filepath=None produces generic '<string>' in error messages, reducing debugging context
    deps:
      calls:
        - ValueError
        - compile
        - str
      imports:
        - __future__.annotations
        - ast
        - inspect
        - pathlib.Path
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  Using compile() with 'exec' mode provides the most accurate syntax validation without executing code, matching Python's own parser behavior. Re-raising as ValueError (rather than SyntaxError) provides a consistent exception interface for the adapter layer, allowing callers to handle validation errors uniformly without importing language-specific exceptions. The optional filepath parameter enables better error diagnostics when validating files, while gracefully degrading to a placeholder for in-memory strings. This approach is lightweight and leverages the standard library rather than external parsing tools.

guardrails:
  - DO NOT execute the compiled code; compile() with 'exec' mode only parses without running, preventing arbitrary code execution during validation
  - DO NOT suppress or silently ignore SyntaxError; re-raising as ValueError ensures validation failures are visible to callers
  - DO NOT assume filepath is always provided; the None check prevents TypeError when passing None to str()
  - DO NOT modify the source string; validation must be read-only to avoid side effects
  - DO NOT validate semantics (e.g., undefined variables, type mismatches); this function only checks syntax, not runtime correctness

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## get_comment_delimiters

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/python_adapter.py:593`

### Raw YAML Block

```yaml
what: |
  Returns a tuple containing the opening and closing delimiters for Python multi-line string comments.

  The function constructs the delimiter by repeating the double-quote character (ASCII 34) three times,
  producing the standard Python triple-quote string delimiter (""").

  Inputs: None (instance method, no parameters)

  Outputs: A tuple of two strings, each containing three double-quote characters.
  The tuple format is (opening_delimiter, closing_delimiter), both identical for Python's symmetric
  triple-quote syntax.

  Edge cases:
  - The function uses chr(34) to obtain the double-quote character, ensuring proper character encoding
    regardless of string literal representation in the source code.
  - Both elements of the returned tuple are identical since Python uses the same delimiter for opening
    and closing multi-line strings.
  - This method is deterministic and stateless; it always returns the same value.
    deps:
      calls:
        - chr
      imports:
        - __future__.annotations
        - ast
        - inspect
        - pathlib.Path
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  This method abstracts the language-specific comment delimiter syntax into a reusable interface.
  By using chr(34) instead of hardcoding a string literal, the code avoids potential issues with
  quote escaping and makes the intent explicit: we are constructing delimiters programmatically.

  The tuple return type (rather than separate methods) allows callers to unpack delimiters in a
  single operation and supports polymorphic implementations across different language adapters.

  Returning identical opening and closing delimiters reflects Python's symmetric triple-quote syntax,
  simplifying downstream logic that wraps content with these delimiters.

guardrails:
  - DO NOT modify the delimiter strings after retrieval; they represent immutable language syntax rules.
  - DO NOT assume the delimiters are unique across different language adapters; other languages may
    use different or asymmetric delimiters (e.g., /* */ in C-style languages).
  - DO NOT use this method for single-line comment detection; Python single-line comments use # and
    require a separate method.

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## parse

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/python_adapter.py:654`

### Raw YAML Block

```yaml
what: |
  Parses Python source code string into an Abstract Syntax Tree (AST) module object.

  Input: A string containing valid Python source code (single or multi-line).
  Output: An ast.Module object representing the parsed code structure, containing nodes for all top-level statements, expressions, and definitions.

  The function delegates directly to Python's built-in ast.parse() with default parameters. This produces a complete AST suitable for traversal, analysis, or transformation. The resulting Module node contains a body list of statement nodes and type_ignores metadata.

  Edge cases:
  - Syntax errors in source_code raise SyntaxError with line/column information
  - Empty strings parse successfully to an empty Module with body=[]
  - Incomplete or malformed code raises SyntaxError before AST construction
  - Unicode and multi-byte characters are handled transparently by ast.parse()
  - The function does not validate semantic correctness, only syntactic structure
    deps:
      calls:
        - ast.parse
      imports:
        - __future__.annotations
        - ast
        - inspect
        - pathlib.Path
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  Using ast.parse() directly provides a standard, well-tested entry point to Python's compiler infrastructure. This approach:
  - Leverages the official Python parser, ensuring compatibility across Python versions
  - Avoids reimplementing parsing logic, reducing maintenance burden and bugs
  - Produces canonical AST nodes that integrate seamlessly with ast module utilities (NodeVisitor, NodeTransformer, etc.)
  - Maintains consistency with Python tooling ecosystem expectations
  - Delegates error handling to the standard library, providing clear SyntaxError messages with location data

guardrails:
  - DO NOT attempt to catch and suppress SyntaxError silently; callers must handle parse failures explicitly to avoid masking malformed input
  - DO NOT modify or normalize source_code before parsing; pass it as-is to preserve original line/column information in error messages
  - DO NOT assume the AST is semantically valid; ast.parse() only validates syntax, not name resolution, type correctness, or runtime behavior
  - DO NOT use mode parameter variations without explicit caller intent; default 'exec' mode is appropriate for module-level code analysis

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## _get_indent

**Location:** `/Users/davidmontgomery/agentspec/agentspec/langs/python_adapter.py:707`

### Raw YAML Block

```yaml
what: |
  Extracts the indentation level of an AST node and returns it as a string of spaces.

  Takes an ast.AST node as input and retrieves its col_offset attribute, which represents
  the column position (0-indexed) where the node begins in its source line. This column
  offset is converted directly to a string of spaces matching that width.

  Returns a string containing only space characters, with length equal to the node's
  col_offset. For nodes at the start of a line (col_offset=0), returns an empty string.
  For nodes indented 4 spaces, returns '    ' (4 spaces).

  Edge cases:
  - Nodes without col_offset attribute default to 0, returning empty string
  - Does not validate that col_offset is non-negative
  - Does not account for tabs or mixed whitespace in original source
  - Assumes col_offset directly maps to space-based indentation (may not reflect actual source if tabs were used)
    deps:
      calls:
        - getattr
      imports:
        - __future__.annotations
        - ast
        - inspect
        - pathlib.Path
        - typing.Dict
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  This utility function normalizes AST node positioning into a consistent indentation
  representation for code generation or formatting tasks. Using col_offset directly
  provides a simple, deterministic way to preserve relative indentation when reconstructing
  or modifying code from AST nodes.

  The approach trades accuracy for simplicity: it assumes space-based indentation and
  doesn't reconstruct the exact original whitespace. This is acceptable for most code
  generation scenarios where consistent spacing is more important than byte-for-byte
  fidelity to the source.

guardrails:
  - DO NOT assume col_offset reflects the actual whitespace in the source file; it is a character position count, not a whitespace type indicator. Original source may use tabs.
  - DO NOT use this for round-trip source preservation where exact whitespace must be maintained; use the tokenize module or source lines directly instead.
  - DO NOT rely on this for indentation validation; col_offset can be any non-negative integer and doesn't guarantee valid Python indentation.
  - DO NOT call this on nodes that may not have col_offset defined without explicit error handling, as the getattr fallback silently masks missing position information.

    changelog:
      - "- 2025-10-31: feat: Implement language adapter architecture for multi-language support (231e272)"
```

---

## __init__

**Location:** `/Users/davidmontgomery/agentspec/agentspec/lint.py:23`

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
        - agentspec.utils.collect_source_files
        - ast
        - pathlib.Path
        - re
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
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
      - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate (172e0a7)"
      - "- 2025-10-29: Enhanced lint.py with YAML validation and verbose checks (7a34cb3)"
```

---

## visit_FunctionDef

**Location:** `/Users/davidmontgomery/agentspec/agentspec/lint.py:92`

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
  - Functions with empty bodies or only pass statements are still validated for docstrings
  - Async function definitions (async def) are handled by visit_AsyncFunctionDef, not this method
    deps:
      calls:
        - self._check_docstring
        - self.generic_visit
      imports:
        - agentspec.utils.collect_python_files
        - agentspec.utils.collect_source_files
        - ast
        - pathlib.Path
        - re
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
  - DO NOT process async functions here; they require a separate visit_AsyncFunctionDef implementation to maintain correct dispatch

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
      - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate (172e0a7)"
      - "- 2025-10-29: Enhanced lint.py with YAML validation and verbose checks (7a34cb3)"
```

---

## visit_AsyncFunctionDef

**Location:** `/Users/davidmontgomery/agentspec/agentspec/lint.py:157`

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
        - agentspec.utils.collect_source_files
        - ast
        - pathlib.Path
        - re
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
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
      - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate (172e0a7)"
      - "- 2025-10-29: Enhanced lint.py with YAML validation and verbose checks (7a34cb3)"
```

---

## visit_ClassDef

**Location:** `/Users/davidmontgomery/agentspec/agentspec/lint.py:219`

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
  - Empty classes or classes with only pass statements are still subject to docstring validation
    deps:
      calls:
        - self._check_docstring
        - self.generic_visit
      imports:
        - agentspec.utils.collect_python_files
        - agentspec.utils.collect_source_files
        - ast
        - pathlib.Path
        - re
        - sys
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Tuple
        - yaml


why: |
  The visitor pattern (ast.NodeVisitor) provides a standard, maintainable mechanism for AST traversal with automatic node-type dispatch via method naming convention (visit_[NodeType]). By validating the parent class docstring before recursing into children, the validator establishes clear error context and ensures that documentation requirements are checked top-down through the class hierarchy. This ordering also allows parent-level validation errors to be reported before child-level errors, improving readability of lint output. The approach balances comprehensive validation coverage with predictable error reporting semantics.

guardrails:
  - DO NOT remove the generic_visit() call; it is essential for recursive traversal of all child nodes (methods, nested classes, attributes) and omitting it will cause child nodes to be silently skipped during validation
  - DO NOT rename this method; ast.NodeVisitor uses reflection to dispatch to visit_[NodeType] methods by name, and renaming breaks the automatic dispatch mechanism
  - DO NOT call _check_docstring() after generic_visit(); always validate the parent node before recursing into children to maintain proper error reporting order and context
  - DO NOT modify the method signature; it must accept exactly one parameter (node) to conform to the ast.NodeVisitor interface contract
  - DO NOT assume node has a docstring attribute without defensive checks in _check_docstring(); some class definitions may lack docstrings entirely

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
      - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate (172e0a7)"
      - "- 2025-10-29: Enhanced lint.py with YAML validation and verbose checks (7a34cb3)"
```

---

## _check_docstring

**Location:** `/Users/davidmontgomery/agentspec/agentspec/lint.py:280`

### What This Does

Validates that function and class nodes contain properly formatted agentspec YAML docstring blocks with required and recommended metadata fields. The method extracts the docstring, locates the "---agentspec"/"

### Raw YAML Block

```yaml
what: |
  Validates that function and class nodes contain properly formatted agentspec YAML docstring blocks with required and recommended metadata fields. The method extracts the docstring, locates the "---agentspec"/"
```

---

## check

**Location:** `/Users/davidmontgomery/agentspec/agentspec/lint.py:427`

### Raw YAML Block

```yaml
what: |
  Returns a tuple containing two lists of accumulated linting results from the checker instance.
  The first list contains errors as Tuple[int, str] pairs (line number and error message).
  The second list contains warnings as Tuple[int, str] pairs (line number and warning message).
  This method provides direct access to internal state without filtering, sorting, or transformation.
  Line numbers are integers (0 if unavailable), and messages are string descriptions of the linting issue.
  The method returns references to the internal lists, not copies, making it a lightweight accessor.
  Callers receive the authoritative state of the linter at the moment of invocation.
  Edge case: if no linting has been performed, both lists may be empty.
  Edge case: line numbers may be 0 or None if source location information is unavailable.
    deps:
      imports:
        - agentspec.utils.collect_python_files
        - agentspec.utils.collect_source_files
        - ast
        - pathlib.Path
        - re
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
  Maintaining internal list references allows the checker to continue accumulating results across multiple check cycles if needed.

guardrails:
  - DO NOT add filtering, sorting, or transformation logic to the returned lists; preserve raw accumulation order
  - DO NOT change the return type from Tuple[List[Tuple[int, str]], List[Tuple[int, str]]]
  - ALWAYS preserve the (errors, warnings) order in the returned tuple for consistent caller expectations
  - ALWAYS return direct references to self.errors and self.warnings without copying to maintain performance
  - DO NOT modify the structure or content of error/warning tuples before returning; return them as-is
  - DO NOT add validation or sanitization of line numbers or messages; return accumulated state faithfully

    changelog:
      - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
      - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate (172e0a7)"
      - "- 2025-10-29: Enhanced lint.py with YAML validation and verbose checks (7a34cb3)"
      - "- 2025-10-29: Add agent spec linter for Python files (4421824)"
```

---

## check_file

**Location:** `/Users/davidmontgomery/agentspec/agentspec/lint.py:481`

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
        - agentspec.utils.collect_source_files
        - ast
        - pathlib.Path
        - re
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
      - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
      - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate (172e0a7)"
      - "- 2025-10-29: Enhanced lint.py with YAML validation and verbose checks (7a34cb3)"
      - "- 2025-10-29: Add agent spec linter for Python files (4421824)"
```

---

## _extract_agentspec_from_text

**Location:** `/Users/davidmontgomery/agentspec/agentspec/lint.py:568`

### What This Does

Extracts a YAML agentspec block from a docstring or text document.

Takes a string input and searches for content bounded by the delimiters "---agentspec" and "

### Raw YAML Block

```yaml
what: |
  Extracts a YAML agentspec block from a docstring or text document.

  Takes a string input and searches for content bounded by the delimiters "---agentspec" and "
```

---

## check_js_file

**Location:** `/Users/davidmontgomery/agentspec/agentspec/lint.py:642`

### What This Does

Lints a JavaScript/TypeScript file for agentspec compliance by scanning JSDoc blocks for
YAML sections delimited by '---agentspec' and '

### Raw YAML Block

```yaml
what: |
  Lints a JavaScript/TypeScript file for agentspec compliance by scanning JSDoc blocks for
  YAML sections delimited by '---agentspec' and '
```

---

## run

**Location:** `/Users/davidmontgomery/agentspec/agentspec/lint.py:766`

### Raw YAML Block

```yaml
what: |
  Executes batch linting validation on Python and JavaScript/TypeScript files within a target directory to verify agentspec block compliance. Collects all source files from the target path (file or directory), invokes language-specific checkers (`check_file` for Python, `check_js_file` for JS/TS) to validate agentspec requirements, and aggregates error and warning counts. Returns exit code 0 on success (no errors, and either no warnings or strict mode disabled), or exit code 1 on failure (errors present, or warnings present in strict mode). Prints per-file diagnostics with line numbers and messages, followed by a summary line showing total files checked and issue counts. Edge case: empty directory returns 0 with zero files checked and no per-file output.
    deps:
      calls:
        - Path
        - check_file
        - check_js_file
        - collect_source_files
        - len
        - print
      imports:
        - agentspec.utils.collect_python_files
        - agentspec.utils.collect_source_files
        - ast
        - pathlib.Path
        - re
        - sys
        - typing.Any
        - typing.Dict
        - typing.List
        - typing.Tuple
        - yaml


why: |
  Provides a CLI-friendly batch validation entry point for enforcing agentspec compliance across entire codebases. Separates errors (blocking issues) from warnings (advisory issues) to allow flexible enforcement policies. Strict mode enables CI/CD pipelines to enforce zero-warning policies by treating warnings as failures, while permissive mode allows warnings to pass. Summary statistics printed before exit code ensure visibility into validation scope and results. Language-agnostic file collection and dispatch pattern supports future linting extensions without modifying core logic.

guardrails:
  - DO NOT return 0 when strict=True and total_warnings > 0; strict mode must treat warnings as blocking failures to enforce zero-warning policies in CI/CD pipelines
  - DO NOT skip summary statistics output; always print the separator line and final status message to ensure visibility of validation results and file counts
  - DO NOT modify or filter files during linting; only validate and report, preserving immutability of the target codebase
  - DO NOT assume target path exists; rely on Path and collect_source_files to handle missing paths gracefully without raising uncaught exceptions
  - DO NOT mix error and warning counts in per-file output; maintain separate line-by-line reporting to enable downstream filtering and severity-based handling

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
      - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate (172e0a7)"
      - "- 2025-10-29: Enhanced lint.py with YAML validation and verbose checks (7a34cb3)"
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

Unified LLM interface routing to Anthropic (Claude) or OpenAI‑compatible providers. Uses OpenAI
Responses API by default, with automatic fallback to Chat Completions for OpenAI‑compatible
runtimes that do not implement Responses (e.g., Ollama/vLLM/LM Studio).

Inputs: model, messages, temperature, max_tokens, base_url, provider, optional reasoning/verbosity
and grammar_lark (Responses/CFG only).

Behavior:
- Anthropic path (provider == 'claude' or model startswith 'claude'): call messages.create
- OpenAI path: try responses.create; if it raises a transport error or returns 404, fallback to
  chat.completions.create with a translated message format

### ⚠️ Guardrails (CRITICAL)

- **DO NOT apply grammar_lark on Anthropic; CFG is Responses‑specific**
- **Preserve existing message order and content; only reformat for chat.completions**
- **Keep fallback narrow (transport failure or 404) to avoid masking real API errors**

### Changelog

- 2025-11-02: feat(llm): Add Chat Completions fallback for OpenAI‑compatible providers (Ollama)

### Raw YAML Block

```yaml
what: |
  Unified LLM interface routing to Anthropic (Claude) or OpenAI‑compatible providers. Uses OpenAI
  Responses API by default, with automatic fallback to Chat Completions for OpenAI‑compatible
  runtimes that do not implement Responses (e.g., Ollama/vLLM/LM Studio).

  Inputs: model, messages, temperature, max_tokens, base_url, provider, optional reasoning/verbosity
  and grammar_lark (Responses/CFG only).

  Behavior:
  - Anthropic path (provider == 'claude' or model startswith 'claude'): call messages.create
  - OpenAI path: try responses.create; if it raises a transport error or returns 404, fallback to
    chat.completions.create with a translated message format

guardrails:
  - DO NOT apply grammar_lark on Anthropic; CFG is Responses‑specific
  - Preserve existing message order and content; only reformat for chat.completions
  - Keep fallback narrow (transport failure or 404) to avoid masking real API errors

changelog:
  - "2025-11-02: feat(llm): Add Chat Completions fallback for OpenAI‑compatible providers (Ollama)"
```

---

## create_ui_only_toggle

**Location:** `/Users/davidmontgomery/agentspec/agentspec/notebook_ui.py:5`

### What This Does

Returns an ipywidgets Button configured with an on-click handler that
toggles the CSS class 'ui-only' on document.body using a Javascript
snippet. When the class is present, notebook CSS can hide everything
except the primary UI container. The function does not alter global
state until the button is clicked, making it safe to import.

### Dependencies

### Why This Approach

Encapsulating the toggle logic in a reusable function allows unit
testing outside of the notebook runtime and avoids repeatedly embedding
anonymous JS strings. It centralizes the 'ui-only' behavior so that
future changes (e.g., class name or script) occur in one place.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT execute Javascript on import; only when button is clicked.**
- **KEEP the CSS class name 'ui-only' stable; CSS relies on it.**
- **USE IPython.display.Javascript and display(); avoid other side effects.**

### Changelog

- 2025-11-03: Added create_ui_only_toggle for UI-only notebook mode

### Raw YAML Block

```yaml
what: |
  Returns an ipywidgets Button configured with an on-click handler that
  toggles the CSS class 'ui-only' on document.body using a Javascript
  snippet. When the class is present, notebook CSS can hide everything
  except the primary UI container. The function does not alter global
  state until the button is clicked, making it safe to import.

deps:
  imports:
    - IPython.display.Javascript
    - IPython.display.display
    - ipywidgets.Button
    - ipywidgets.Layout

why: |
  Encapsulating the toggle logic in a reusable function allows unit
  testing outside of the notebook runtime and avoids repeatedly embedding
  anonymous JS strings. It centralizes the 'ui-only' behavior so that
  future changes (e.g., class name or script) occur in one place.

guardrails:
  - DO NOT execute Javascript on import; only when button is clicked.
  - KEEP the CSS class name 'ui-only' stable; CSS relies on it.
  - USE IPython.display.Javascript and display(); avoid other side effects.

changelog:
  - "2025-11-03: Added create_ui_only_toggle for UI-only notebook mode"
```

---

## load_prompt

**Location:** `/Users/davidmontgomery/agentspec/agentspec/prompts.py:15`

### Raw YAML Block

```yaml
what: |
  Loads a prompt template file from the designated prompts directory by name. The function accepts a prompt_name parameter (string without file extension), constructs a Path object pointing to a .md file in PROMPTS_DIR, validates file existence, and returns the file contents as a UTF-8 encoded string. If the file does not exist, raises FileNotFoundError with a detailed message that lists all available prompt files in the directory to aid debugging. Edge cases include: missing files (handled with informative error), encoding issues (UTF-8 assumed), and empty prompt files (returned as empty string, not an error).
    deps:
      calls:
        - FileNotFoundError
        - PROMPTS_DIR.glob
        - join
        - prompt_file.exists
        - prompt_file.read_text
      imports:
        - pathlib.Path
        - typing.Any
        - typing.Dict


why: |
  Centralizing prompt loading through a single function provides consistent file resolution, encoding handling, and error messaging across the codebase. Using Path objects ensures cross-platform compatibility. The detailed error message with available prompts reduces friction when users reference non-existent prompt names. Accepting only the stem (name without extension) simplifies the API and enforces a single file format convention (.md).

guardrails:
  - DO NOT assume prompt_name is sanitized; Path construction with user input could enable directory traversal attacks if prompt_name contains "../" sequences. Validate or restrict prompt_name to alphanumeric and underscore characters.
  - DO NOT silently return empty strings for missing files; always raise FileNotFoundError so callers can distinguish between "file not found" and "file exists but is empty".
  - DO NOT change the encoding assumption without updating all call sites; UTF-8 is a contract that must be documented and consistent.
  - DO NOT glob the prompts directory on every error; pre-compute or cache available prompts if this function is called frequently in error paths.

    changelog:
      - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
```

---

## load_base_prompt

**Location:** `/Users/davidmontgomery/agentspec/agentspec/prompts.py:56`

### What This Does

Load and return the base prompt used for agentspec YAML generation. This file provides the core rules (honesty, brevity, weakness callouts, ASK USER guardrails) and the required output format, without embedding examples. The examples are appended separately at runtime.

Inputs: none
Outputs: string contents of `agentspec/prompts/base_prompt.md` (UTF-8)

### Dependencies

**Calls:**
- `PROMPTS_DIR.joinpath`
- `read_text`

### Why This Approach

Separating a lightweight, principle-focused base prompt from examples enables a living examples dataset while keeping the core guidance stable and easy to review.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT embed examples in this file; examples are managed via examples.json**
- **DO NOT mutate the returned string; callers should treat it as read-only**
- **ALWAYS read with UTF-8 encoding for cross-platform consistency**

### Changelog

- - 2025-11-02: feat: Add base prompt loader for revolutionary architecture (handoff execution)

### Raw YAML Block

```yaml
what: |
  Load and return the base prompt used for agentspec YAML generation. This file provides the core rules (honesty, brevity, weakness callouts, ASK USER guardrails) and the required output format, without embedding examples. The examples are appended separately at runtime.

  Inputs: none
  Outputs: string contents of `agentspec/prompts/base_prompt.md` (UTF-8)
deps:
  calls:
    - PROMPTS_DIR.joinpath
    - read_text
  imports:
    - pathlib.Path
    - typing.Any
    - typing.Dict

why: |
  Separating a lightweight, principle-focused base prompt from examples enables a living examples dataset while keeping the core guidance stable and easy to review.

guardrails:
  - DO NOT embed examples in this file; examples are managed via examples.json
  - DO NOT mutate the returned string; callers should treat it as read-only
  - ALWAYS read with UTF-8 encoding for cross-platform consistency

changelog:
  - "- 2025-11-02: feat: Add base prompt loader for revolutionary architecture (handoff execution)"
```

---

## load_provider_base_prompt

**Location:** `/Users/davidmontgomery/agentspec/agentspec/prompts.py:88`

### What This Does

Select and load a provider-specific base prompt file for agentspec YAML generation.

Mapping:
- provider 'openai' → 'base_prompt_openai_responses.md' (Responses API + CFG)
- provider 'claude' or 'anthropic' → 'base_prompt_anthropic.md' (Claude Messages API, uses system=)
- provider 'local' → 'base_prompt_chat_local.md' (OpenAI-compatible Chat Completions / Ollama)
- fallback → 'base_prompt.md'

The `terse` flag is accepted for signature parity but currently uses the same provider file.

### Dependencies

**Calls:**
- `PROMPTS_DIR.joinpath`
- `read_text`

### Why This Approach

Different providers have different API semantics and reliability characteristics.
Responses+CFG benefits from a minimal prompt (grammar enforces structure),
Anthropic should use a concise role prompt in `system=`, and Chat fallback needs
conservative instructions to reduce prompt echo.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT include full example bodies in Anthropic or Chat fallback prompts; risk of echo.**
- **KEEP mapping stable; changes alter generation behavior across providers.**
- **If a file is missing, fall back to 'base_prompt.md' rather than crashing.**

### Changelog

- 2025-11-04: feat(prompts): add provider-specific base prompt loader

### Raw YAML Block

```yaml
what: |
  Select and load a provider-specific base prompt file for agentspec YAML generation.

  Mapping:
  - provider 'openai' → 'base_prompt_openai_responses.md' (Responses API + CFG)
  - provider 'claude' or 'anthropic' → 'base_prompt_anthropic.md' (Claude Messages API, uses system=)
  - provider 'local' → 'base_prompt_chat_local.md' (OpenAI-compatible Chat Completions / Ollama)
  - fallback → 'base_prompt.md'

  The `terse` flag is accepted for signature parity but currently uses the same provider file.

deps:
  calls:
    - PROMPTS_DIR.joinpath
    - read_text
  imports:
    - pathlib.Path
    - typing.Optional

why: |
  Different providers have different API semantics and reliability characteristics.
  Responses+CFG benefits from a minimal prompt (grammar enforces structure),
  Anthropic should use a concise role prompt in `system=`, and Chat fallback needs
  conservative instructions to reduce prompt echo.

guardrails:
  - DO NOT include full example bodies in Anthropic or Chat fallback prompts; risk of echo.
  - KEEP mapping stable; changes alter generation behavior across providers.
  - If a file is missing, fall back to 'base_prompt.md' rather than crashing.

changelog:
  - "2025-11-04: feat(prompts): add provider-specific base prompt loader"
```

---

## load_lint_rules

**Location:** `/Users/davidmontgomery/agentspec/agentspec/prompts.py:143`

### What This Does

Load lint rules used to validate generated agentspec blocks and prevent prompt echo/slop.
Returns a dict read from 'agentspec/prompts/lint_rules.json'. If file is missing,
returns a conservative default with an empty rule set.

### Dependencies

**Calls:**
- `read_text`

### Why This Approach

Converting bad example patterns into deterministic lint rules allows the pipeline to reject
polluted outputs before writing to source code, especially on non-Responses paths.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT hard-fail on missing file; return defaults to avoid blocking workflows.**
- **Keep schema simple (forbidden_phrases, max_blocks) to minimize coupling.**

### Changelog

- 2025-11-04: feat(lint): add lint rules loader

### Raw YAML Block

```yaml
what: |
  Load lint rules used to validate generated agentspec blocks and prevent prompt echo/slop.
  Returns a dict read from 'agentspec/prompts/lint_rules.json'. If file is missing,
  returns a conservative default with an empty rule set.

deps:
  calls:
    - read_text
  imports:
    - json

why: |
  Converting bad example patterns into deterministic lint rules allows the pipeline to reject
  polluted outputs before writing to source code, especially on non-Responses paths.

guardrails:
  - DO NOT hard-fail on missing file; return defaults to avoid blocking workflows.
  - Keep schema simple (forbidden_phrases, max_blocks) to minimize coupling.

changelog:
  - "2025-11-04: feat(lint): add lint rules loader"
```

---

## load_examples_json

**Location:** `/Users/davidmontgomery/agentspec/agentspec/prompts.py:179`

### What This Does

Load the living examples dataset as a JSON object. Returns a dict with keys: version, last_updated, and examples (list). Each example may include `code`, `code_context` (file, function, subject_function), and good/bad documentation with guardrails.

Inputs: none
Outputs: Python dict parsed from `agentspec/prompts/examples.json`

### Dependencies

**Calls:**
- `read_text`
- `json.loads`

### Why This Approach

Examples evolve with the user’s codebase. Loading structured JSON allows appending and programmatic validation, and supports future tooling like add_example.py.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT silently ignore parse errors; allow exceptions to surface to callers for visibility**
- **DO NOT write to this file from here; this function is read-only**
- **ALWAYS include `code_context` for anchored examples to provide real context to the model**

### Changelog

- - 2025-11-02: feat: Add examples.json loader with anchored context (handoff execution)

### Raw YAML Block

```yaml
what: |
  Load the living examples dataset as a JSON object. Returns a dict with keys: version, last_updated, and examples (list). Each example may include `code`, `code_context` (file, function, subject_function), and good/bad documentation with guardrails.

  Inputs: none
  Outputs: Python dict parsed from `agentspec/prompts/examples.json`

deps:
  calls:
    - read_text
    - json.loads
  imports:
    - json
    - pathlib.Path
    - typing.Any
    - typing.Dict

why: |
  Examples evolve with the user’s codebase. Loading structured JSON allows appending and programmatic validation, and supports future tooling like add_example.py.

guardrails:
  - DO NOT silently ignore parse errors; allow exceptions to surface to callers for visibility
  - DO NOT write to this file from here; this function is read-only
  - ALWAYS include `code_context` for anchored examples to provide real context to the model

changelog:
  - "- 2025-11-02: feat: Add examples.json loader with anchored context (handoff execution)"
```

---

## load_agentspec_yaml_grammar

**Location:** `/Users/davidmontgomery/agentspec/agentspec/prompts.py:215`

### What This Does

Load and return the CFG grammar used to constrain agentspec YAML generation. The grammar enforces the presence and order of sections (what, why, guardrails) and exact block fences `---agentspec` / `

### Raw YAML Block

```yaml
what: |
  Load and return the CFG grammar used to constrain agentspec YAML generation. The grammar enforces the presence and order of sections (what, why, guardrails) and exact block fences `---agentspec` / `
```

---

## get_verbose_docstring_prompt

**Location:** `/Users/davidmontgomery/agentspec/agentspec/prompts.py:248`

### Raw YAML Block

```yaml
what: |
  Retrieves and returns the verbose docstring generation prompt template as a string.

  This function loads a pre-defined prompt from the prompts module using the key "verbose_docstring".
  The prompt is designed to guide LLM-based documentation generation for creating detailed,
  multi-line docstrings that explain function behavior, parameters, return values, and edge cases.

  Input: None (no parameters)
  Output: A string containing the complete prompt template for verbose docstring generation

  Edge cases:
  - If the prompt file is missing or corrupted, load_prompt() will raise an exception
  - If the "verbose_docstring" key does not exist in the prompts configuration, load_prompt() will fail
  - Returns the prompt exactly as stored; no post-processing or validation is performed
    deps:
      calls:
        - load_prompt
      imports:
        - pathlib.Path
        - typing.Any
        - typing.Dict


why: |
  This function abstracts prompt loading logic into a reusable, testable interface rather than
  embedding prompt strings directly in calling code. This approach enables:
  - Centralized prompt management and versioning
  - Easy updates to prompts without code changes
  - Separation of concerns between prompt content and prompt consumption
  - Consistent prompt retrieval across the codebase

  The function acts as a facade over load_prompt(), making the intent explicit and allowing
  future enhancements (caching, validation, prompt composition) without affecting callers.

guardrails:
  - DO NOT modify or interpolate the prompt string before returning it; preserve exact formatting
    to ensure LLM prompt consistency and reproducibility
  - DO NOT assume the prompt exists; callers must handle exceptions from load_prompt() gracefully
  - DO NOT use this function for non-docstring prompts; it is semantically specific to verbose
    docstring generation and should not be repurposed for other prompt types

    changelog:
      - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
```

---

## get_terse_docstring_prompt

**Location:** `/Users/davidmontgomery/agentspec/agentspec/prompts.py:299`

### Raw YAML Block

```yaml
what: |
  Retrieves and returns a pre-configured prompt template string for generating terse (concise, minimal) docstrings. The function calls load_prompt() with the identifier "terse_docstring" to fetch the prompt from the prompt storage system. Returns a string containing the complete prompt template that can be used by downstream code generation or documentation tools to produce brief, focused docstrings. The prompt itself is loaded from external storage, making it configurable without code changes. Edge case: if the prompt identifier "terse_docstring" does not exist in the prompt store, load_prompt() will raise an exception that propagates to the caller.
    deps:
      calls:
        - load_prompt
      imports:
        - pathlib.Path
        - typing.Any
        - typing.Dict


why: |
  Encapsulating prompt retrieval behind a dedicated function provides a single point of access for the terse docstring prompt, enabling consistent usage across the codebase and simplifying maintenance. By delegating to load_prompt(), the function leverages centralized prompt management rather than hardcoding template strings. This approach allows prompts to be updated, versioned, or swapped without modifying function logic. The terse variant specifically supports use cases requiring minimal documentation overhead while maintaining clarity.

guardrails:
  - DO NOT assume the prompt store is always available or that "terse_docstring" exists; callers must handle potential exceptions from load_prompt()
  - DO NOT modify or cache the returned prompt string in ways that could cause stale state; treat the return value as read-only
  - DO NOT use this function for generating verbose or detailed docstrings; it is specifically designed for terse output and using it for other purposes will produce suboptimal results

    changelog:
      - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
```

---

## get_agentspec_yaml_prompt

**Location:** `/Users/davidmontgomery/agentspec/agentspec/prompts.py:328`

### Raw YAML Block

```yaml
what: |
  Retrieves and returns the agentspec YAML block generation prompt as a string.

  This function loads a pre-defined prompt template named "agentspec_yaml" from the prompts module's storage system. The prompt is used to instruct language models or documentation generators on how to create properly formatted YAML blocks that conform to the agentspec schema.

  Inputs: None (no parameters)

  Outputs: A string containing the complete agentspec YAML generation prompt, including instructions for what/why/guardrails sections, schema requirements, and formatting rules.

  Edge cases:
  - If the "agentspec_yaml" prompt file does not exist, load_prompt() will raise an exception
  - If the prompt file is empty or corrupted, an empty or malformed string may be returned
  - The function assumes load_prompt() is properly implemented and available in the same module
    deps:
      calls:
        - load_prompt
      imports:
        - pathlib.Path
        - typing.Any
        - typing.Dict


why: |
  This function centralizes access to the agentspec YAML prompt template, enabling consistent prompt delivery across the codebase without hardcoding. By abstracting the prompt into a loadable resource, the prompt can be updated independently of code changes, and multiple callers can reference the same canonical version. This supports maintainability and reduces duplication of the prompt text throughout the application.

guardrails:
  - DO NOT modify the returned prompt string before passing it to downstream consumers, as this may break schema compliance or instruction clarity
  - DO NOT assume the prompt file exists without error handling; wrap calls in try-except to gracefully handle missing or inaccessible prompt resources
  - DO NOT use this function in performance-critical loops without caching, as file I/O via load_prompt() may be expensive

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
```

---

## get_verbose_docstring_prompt_v2

**Location:** `/Users/davidmontgomery/agentspec/agentspec/prompts.py:376`

### Raw YAML Block

```yaml
what: |
  Retrieves a pre-configured prompt template for generating verbose docstrings (version 2).

  This function loads and returns a string containing a complete prompt specification designed to guide LLM-based docstring generation. The v2 variant is optimized for clean output without metadata leakage—meaning it excludes internal implementation details, file paths, or system artifacts from the generated docstrings.

  Inputs: None (zero-argument function)

  Outputs: A string containing the full prompt template, ready to be passed to an LLM or prompt engine.

  Edge cases:
  - If the prompt file "verbose_docstring_v2" does not exist or cannot be loaded, the underlying load_prompt() call will raise an exception (typically FileNotFoundError or similar).
  - The returned string is immutable and should not be modified by callers; treat as read-only.
  - Prompt content is cached at module load time by load_prompt(); repeated calls return the same object reference.
    deps:
      calls:
        - load_prompt
      imports:
        - pathlib.Path
        - typing.Any
        - typing.Dict


why: |
  Separating prompt templates into external files and loading them via dedicated functions provides several benefits:

  1. Maintainability: Prompts can be updated without modifying code or redeploying the module.
  2. Versioning: Multiple prompt versions (v1, v2, etc.) can coexist, allowing A/B testing or gradual rollout of improvements.
  3. Clarity: The v2 designation signals that this version addresses a specific issue (metadata leakage) from earlier iterations.
  4. Reusability: The same prompt can be invoked from multiple call sites without duplication.

  The v2 variant specifically addresses the need for "clean" output—docstrings that focus on behavior and documentation rather than exposing internal system state.

guardrails:
  - DO NOT assume the prompt file exists at runtime; always handle potential load_prompt() exceptions in calling code, as file availability is not guaranteed.
  - DO NOT modify or concatenate the returned string with other prompts without careful validation; prompt injection or malformed templates can degrade LLM output quality.
  - DO NOT rely on this function for security-sensitive operations; the prompt content itself is not encrypted or access-controlled and should not contain secrets.
  - DO NOT cache the result in calling code if prompt updates are expected during runtime; always call this function fresh to ensure the latest template is used.

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
```

---

## get_terse_docstring_prompt_v2

**Location:** `/Users/davidmontgomery/agentspec/agentspec/prompts.py:424`

### Raw YAML Block

```yaml
what: |
  Retrieves and returns a pre-configured prompt template string for generating terse docstrings (version 2).

  The function loads a prompt artifact named "terse_docstring_v2" from the prompt storage system and returns it as a string.

  Inputs: None (parameterless function)

  Outputs: A string containing the complete prompt template for terse docstring generation

  The v2 variant is specifically designed to produce clean docstrings without metadata leakage—meaning the generated docstrings do not inadvertently include internal implementation details, file paths, or other system metadata that should remain hidden from end users.

  Edge cases:
  - If the prompt artifact "terse_docstring_v2" does not exist in the prompt storage, the underlying load_prompt() call will raise an exception
  - The returned string is immutable and should be used as-is; modifications should not be made to the template at runtime
  - Calling this function multiple times returns the same cached or reloaded prompt content
    deps:
      calls:
        - load_prompt
      imports:
        - pathlib.Path
        - typing.Any
        - typing.Dict


why: |
  This function abstracts prompt template management by centralizing the retrieval of a specific docstring generation prompt. By delegating to load_prompt(), the implementation remains decoupled from storage details (file system, database, etc.).

  The v2 designation indicates this is an improved iteration over a prior version, addressing the specific concern of metadata leakage in generated docstrings. This separation allows different prompt versions to coexist and be selected based on use case requirements.

  Returning the prompt as a string enables flexible downstream usage: the caller can pass it to LLMs, template engines, or other text processing systems without coupling to a specific prompt object type.

guardrails:
  - DO NOT modify the returned prompt string at runtime—treat it as immutable to ensure consistency across multiple calls and prevent subtle bugs from prompt mutation
  - DO NOT assume the prompt artifact exists without error handling—wrap calls in try-except if graceful degradation is required
  - DO NOT include sensitive system paths or internal configuration in the prompt template itself, as this defeats the v2 design goal of preventing metadata leakage
  - DO NOT cache the result in the calling code if prompt updates are expected; rely on load_prompt() to handle caching strategy

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
```

---

## get_agentspec_yaml_prompt_v2

**Location:** `/Users/davidmontgomery/agentspec/agentspec/prompts.py:471`

### Raw YAML Block

```yaml
what: |
  Retrieves and returns the agentspec YAML block generation prompt template (version 2).

  This function loads a pre-written prompt file named "agentspec_yaml_v2" from the prompts directory.
  The prompt is designed to instruct an AI agent on how to generate properly formatted YAML blocks
  for embedding agentspec documentation within Python docstrings.

  The v2 variant is specifically engineered to prevent metadata leakage—ensuring that generated
  YAML blocks contain only the core narrative sections (what, why, guardrails) without accidentally
  including dependency information, changelog entries, or other sensitive metadata that should be
  injected separately by code.

  Input: None (no parameters)
  Output: A string containing the complete prompt template ready for use in agent instructions

  Edge cases:
  - If the prompt file does not exist, the load_prompt() function will raise an exception
  - The returned string may contain newlines and special characters; callers should preserve formatting
  - The prompt is static and does not vary based on runtime state
    deps:
      calls:
        - load_prompt
      imports:
        - pathlib.Path
        - typing.Any
        - typing.Dict


why: |
  Centralizing prompt templates in loadable files rather than hardcoding them provides several benefits:
  - Maintainability: Prompts can be updated without redeploying code
  - Separation of concerns: Prompt logic is isolated from application logic
  - Versioning: Multiple prompt versions (v1, v2, etc.) can coexist for A/B testing or gradual rollouts
  - Reusability: The same prompt can be invoked from multiple call sites

  The v2 designation indicates this is an improved iteration that addresses issues found in v1,
  specifically the prevention of metadata leakage into the YAML output. This ensures cleaner,
  more predictable agent behavior and reduces post-processing requirements.

guardrails:
  - DO NOT hardcode the prompt string directly in this function; use load_prompt() to maintain
    separation between code and prompt content, enabling non-code-based updates
  - DO NOT modify or filter the returned prompt string; return it exactly as loaded to preserve
    the intended agent instructions and prevent subtle behavioral drift
  - DO NOT assume the prompt file exists without error handling at the call site; callers must
    be prepared to catch exceptions from load_prompt() if the file is missing or corrupted
  - DO NOT use this function for generating prompts dynamically based on user input; this function
    returns a static template only, not a parameterized prompt factory

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
```

---

## get_diff_summary_prompt

**Location:** `/Users/davidmontgomery/agentspec/agentspec/prompts.py:530`

### What This Does

Loads the diff summary prompt used to instruct an LLM to summarize
function-scoped git diffs into a short, human-readable changelog.

Inputs: none
Outputs: string contents of `agentspec/prompts/diff_summary.md` (UTF-8)

### ⚠️ Guardrails (CRITICAL)

- **DO NOT embed file paths or raw diffs here; callers provide them as user content**
- **ALWAYS keep this prompt brief; summaries should be concise (<= 8 bullets)**

### Changelog

- 2025-11-04: Add diff summary prompt loader

### Raw YAML Block

```yaml
what: |
  Loads the diff summary prompt used to instruct an LLM to summarize
  function-scoped git diffs into a short, human-readable changelog.

  Inputs: none
  Outputs: string contents of `agentspec/prompts/diff_summary.md` (UTF-8)

guardrails:
  - DO NOT embed file paths or raw diffs here; callers provide them as user content
  - ALWAYS keep this prompt brief; summaries should be concise (<= 8 bullets)
changelog:
  - "2025-11-04: Add diff summary prompt loader"
```

---

## format_prompt

**Location:** `/Users/davidmontgomery/agentspec/agentspec/prompts.py:549`

### Raw YAML Block

```yaml
what: |
  Substitutes keyword arguments into a prompt template string using Python's standard string formatting syntax. Accepts a template containing {placeholder} markers and a variable number of keyword arguments, returning a fully interpolated string ready for LLM consumption.

  Inputs:
    - template (str): A prompt template with zero or more {key} placeholders
    - **kwargs (Any): Arbitrary keyword arguments where keys match placeholder names in template

  Outputs:
    - str: The template with all {placeholder} markers replaced by corresponding kwarg values

  Behavior:
    - Uses Python's str.format() method for substitution
    - Supports any hashable kwarg key that matches a placeholder name
    - Converts non-string values to their string representation via format()
    - Returns template unchanged if no placeholders or kwargs provided
    - Raises KeyError if template contains a placeholder with no matching kwarg
    - Raises ValueError if template contains malformed placeholders (e.g., unmatched braces)

  Edge cases:
    - Empty template returns empty string
    - Empty kwargs with placeholders in template raises KeyError
    - Placeholder names are case-sensitive
    - Numeric and special character placeholders supported (e.g., {0}, {_var})
    - Values containing braces are safely escaped by caller responsibility
    deps:
      calls:
        - template.format
      imports:
        - pathlib.Path
        - typing.Any
        - typing.Dict


why: |
  Standard str.format() provides a simple, built-in mechanism for safe template interpolation without external dependencies. This approach is idiomatic Python and integrates seamlessly with prompt engineering workflows where templates are pre-defined and kwargs are controlled inputs. The function acts as a thin wrapper to establish a consistent interface for prompt preparation across the codebase, enabling future enhancements (logging, validation, caching) without changing call sites.

guardrails:
  - DO NOT use string concatenation or f-strings directly in callers; this function enforces consistent template-based composition and enables audit trails
  - DO NOT pass untrusted template strings without validation; malformed placeholders or injection patterns could cause unexpected errors or expose internal variable names
  - DO NOT assume all kwargs will be used; unused kwargs are silently ignored by str.format(), which may mask typos in placeholder names
  - DO NOT pass mutable objects as kwargs values without understanding their str() representation; complex objects may serialize to unhelpful strings

    changelog:
      - "- 2025-11-01: refactor: Extract system prompts to separate .md files for easier editing (136cb30)"
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

## ExampleParser

**Location:** `/Users/davidmontgomery/agentspec/agentspec/tools/add_example.py:56`

### What This Does

Orchestrates LLM-driven analysis of documentation quality and converts user-provided examples (bad and/or good) into structured training records anchored to real code context. Provides utilities to extract code context from a repository source file (with function scoping where possible), analyze documentation using an LLM middle layer, enforce best-practice guardrails (including mandatory ASK USER guardrails when requested), and compute dataset composition ratios for quality control.

Key behaviors:
- extract_code_context(): returns code snippet and metadata (language, file path, line span) for an anchor function where possible; falls back to whole file
- analyze_documentation(): calls an LLM (or deterministic stub) to produce JSON with fields why_bad, good_what, good_why, good_guardrails, lesson, pattern_type; supports analyzing both bad_output and good_output
- make_example(): assembles an example record with code_context, good/bad docs, and guardrails; injects an ASK USER guardrail when required
- load/save dataset: appends to examples.json unless dry-run
- compute_ratio(): counts good vs bad examples to help maintain a recommended ratio

Inputs: user-provided file, function, subject-function, and example texts
Outputs: structured example record and optional dataset file update

### Dependencies

**Calls:**
- `generate_chat`
- `json.loads`
- `json.dumps`
- `Path.read_text`
- `Path.write_text`

### Why This Approach

Python string rules and heuristics are insufficient to accurately judge documentation quality or extract generalizable lessons; an LLM is placed in the middle to analyze both bad and good documentation and propose guardrails. Deterministic stub mode enables fast, stable tests without external API calls, aligning with the repository's testing philosophy.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT write to examples.json unless explicitly requested (dry-run default is safer)**
- **DO NOT drop the ASK USER guardrail when require_ask_user=True; inject it if missing**
- **ALWAYS anchor examples to real files/functions for context**
- **ALWAYS expose a stub mode (AGENTSPEC_EXAMPLES_STUB=1) for tests; never require network in unit tests**

### Changelog

- 2025-11-02: feat: Initial implementation of LLM-backed training example parser (handoff execution)

### Raw YAML Block

```yaml
what: |
  Orchestrates LLM-driven analysis of documentation quality and converts user-provided examples (bad and/or good) into structured training records anchored to real code context. Provides utilities to extract code context from a repository source file (with function scoping where possible), analyze documentation using an LLM middle layer, enforce best-practice guardrails (including mandatory ASK USER guardrails when requested), and compute dataset composition ratios for quality control.

  Key behaviors:
  - extract_code_context(): returns code snippet and metadata (language, file path, line span) for an anchor function where possible; falls back to whole file
  - analyze_documentation(): calls an LLM (or deterministic stub) to produce JSON with fields why_bad, good_what, good_why, good_guardrails, lesson, pattern_type; supports analyzing both bad_output and good_output
  - make_example(): assembles an example record with code_context, good/bad docs, and guardrails; injects an ASK USER guardrail when required
  - load/save dataset: appends to examples.json unless dry-run
  - compute_ratio(): counts good vs bad examples to help maintain a recommended ratio

  Inputs: user-provided file, function, subject-function, and example texts
  Outputs: structured example record and optional dataset file update

deps:
  calls:
    - generate_chat
    - json.loads
    - json.dumps
    - Path.read_text
    - Path.write_text
  imports:
    - click
    - dataclasses.dataclass
    - json
    - os
    - pathlib.Path
    - typing

why: |
  Python string rules and heuristics are insufficient to accurately judge documentation quality or extract generalizable lessons; an LLM is placed in the middle to analyze both bad and good documentation and propose guardrails. Deterministic stub mode enables fast, stable tests without external API calls, aligning with the repository's testing philosophy.

guardrails:
  - DO NOT write to examples.json unless explicitly requested (dry-run default is safer)
  - DO NOT drop the ASK USER guardrail when require_ask_user=True; inject it if missing
  - ALWAYS anchor examples to real files/functions for context
  - ALWAYS expose a stub mode (AGENTSPEC_EXAMPLES_STUB=1) for tests; never require network in unit tests

changelog:
  - "2025-11-02: feat: Initial implementation of LLM-backed training example parser (handoff execution)"
```

---

## _stub_analysis

**Location:** `/Users/davidmontgomery/agentspec/agentspec/tools/add_example.py:135`

### What This Does

Deterministic analysis used when AGENTSPEC_EXAMPLES_STUB=1.

### Raw YAML Block

```yaml
Deterministic analysis used when AGENTSPEC_EXAMPLES_STUB=1.
```

---

## analyze_documentation

**Location:** `/Users/davidmontgomery/agentspec/agentspec/tools/add_example.py:162`

### What This Does

Analyze documentation using an LLM middle layer (or deterministic stub). Produces a JSON-like dict
containing why_bad, good_what, good_why, good_guardrails, lesson, and pattern_type. If the model
returns extra text around JSON, attempts to extract the first JSON object.

### Dependencies

**Calls:**
- `generate_chat`
- `json.loads`

### Raw YAML Block

```yaml
what: |
  Analyze documentation using an LLM middle layer (or deterministic stub). Produces a JSON-like dict
  containing why_bad, good_what, good_why, good_guardrails, lesson, and pattern_type. If the model
  returns extra text around JSON, attempts to extract the first JSON object.

deps:
  calls:
    - generate_chat
    - json.loads
  imports:
    - json
    - re
```

---

## _main_impl

**Location:** `/Users/davidmontgomery/agentspec/agentspec/tools/add_example.py:291`

### What This Does

CLI entrypoint to add an anchored training example. Loads code context, runs LLM analysis, composes a record, validates the good/bad ratio policy, and optionally writes to the dataset file.

### Dependencies

**Calls:**
- `ExampleParser.extract_code_context`
- `ExampleParser.analyze_documentation`
- `ExampleParser.make_example`
- `ExampleParser.load_dataset`
- `ExampleParser.save_dataset`
- `ExampleParser.compute_ratio`

### Why This Approach

A one-command path from observed bad (or good) documentation to a living dataset accelerates iteration and closes the feedback loop described in the handoff.

### ⚠️ Guardrails (CRITICAL)

- **DO NOT write by default; require explicit consent (no surprises)**
- **DO NOT allow the dataset good ratio to silently degrade below minimum unless user opts out of strict enforcement**

### Raw YAML Block

```yaml
what: |
  CLI entrypoint to add an anchored training example. Loads code context, runs LLM analysis, composes a record, validates the good/bad ratio policy, and optionally writes to the dataset file.

deps:
  calls:
    - ExampleParser.extract_code_context
    - ExampleParser.analyze_documentation
    - ExampleParser.make_example
    - ExampleParser.load_dataset
    - ExampleParser.save_dataset
    - ExampleParser.compute_ratio
  imports:
    - click

why: |
  A one-command path from observed bad (or good) documentation to a living dataset accelerates iteration and closes the feedback loop described in the handoff.

guardrails:
  - DO NOT write by default; require explicit consent (no surprises)
  - DO NOT allow the dataset good ratio to silently degrade below minimum unless user opts out of strict enforcement
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

### Raw YAML Block

```yaml
what: |
  Locates the .agentspecignore configuration file used to exclude paths from agent processing.

  Search strategy (in order):
  1. Attempts to import the agentspec package and locate its built-in .agentspecignore file from the package installation directory (parent of agentspec module root)
  2. Falls back to checking repo_root parameter for a project-specific .agentspecignore file
  3. Returns None if neither location contains the file

  Inputs:
  - repo_root: Path object representing the repository root directory (may be None)

  Outputs:
  - Path object pointing to the .agentspecignore file if found
  - None if no .agentspecignore file exists in either location

  Edge cases:
  - Import of agentspec package fails silently (catches all exceptions during import/path resolution)
  - repo_root is None or invalid: skips fallback check
  - Built-in .agentspecignore exists but is inaccessible: falls back to repo_root check
  - Both locations lack .agentspecignore: returns None (no default behavior)
    deps:
      calls:
        - Path
        - builtin_ignore.exists
        - exists
      imports:
        - __future__.annotations
        - agentspec.langs.LanguageRegistry
        - fnmatch
        - os
        - pathlib.Path
        - subprocess
        - typing.Iterable
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  Dual-source approach balances framework defaults with user customization. Built-in .agentspecignore provides sensible exclusions for common patterns (node_modules, .git, etc.) across all projects. Project-specific .agentspecignore allows teams to override or extend defaults for their repository. Silent exception handling during package import prevents initialization failures when agentspec is in an unusual installation state. Fallback to repo_root ensures functionality even if package metadata is unavailable.

guardrails:
  - DO NOT assume repo_root is always valid—it may be None or point to a non-existent directory, so existence checks are required before use
  - DO NOT raise exceptions during package import—silent fallback is intentional to prevent cascading failures in agent initialization
  - DO NOT modify or create .agentspecignore files—this function is read-only discovery only
  - DO NOT cache the result indefinitely—.agentspecignore files may be created/modified during runtime, so callers should re-invoke as needed

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
```

---

## _parse_agentspecignore

**Location:** `/Users/davidmontgomery/agentspec/agentspec/utils.py:295`

### Raw YAML Block

```yaml
what: |
  Parses a .agentspecignore file and extracts a list of ignore patterns.

  Inputs:
    - ignore_path (Path): File system path to the .agentspecignore file
    - repo_root (Path): Root directory of the repository (currently unused but available for context)

  Outputs:
    - List[str]: Ordered list of non-empty, non-comment pattern strings

  Behavior:
    - Reads the file with UTF-8 encoding, ignoring decode errors via errors="ignore"
    - Splits content by lines and strips whitespace from each line
    - Filters out empty lines and lines starting with '#' (comments)
    - Returns remaining lines as patterns
    - Returns empty list [] on any exception (file not found, permission denied, etc.)

  Edge cases:
    - Missing or inaccessible file: silently returns []
    - Malformed UTF-8 bytes: ignored via errors="ignore" parameter
    - Blank lines and whitespace-only lines: filtered out
    - Comment-only files: returns []
    - Mixed comment and pattern content: correctly separates them
    deps:
      calls:
        - ignore_path.read_text
        - line.startswith
        - line.strip
        - patterns.append
        - splitlines
      imports:
        - __future__.annotations
        - agentspec.langs.LanguageRegistry
        - fnmatch
        - os
        - pathlib.Path
        - subprocess
        - typing.Iterable
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  This utility enables flexible ignore pattern configuration without raising exceptions that would halt processing.
  The lenient error handling (returning [] on failure) allows graceful degradation when .agentspecignore is absent or unreadable.
  Stripping whitespace normalizes patterns and prevents leading/trailing space issues.
  Comment filtering via '#' prefix follows standard convention (matching .gitignore behavior) for user-friendly configuration files.
  The repo_root parameter is included for potential future use (e.g., relative path resolution or validation).

guardrails:
  - DO NOT raise exceptions on file read failures; return [] instead to allow processing to continue without .agentspecignore
  - DO NOT preserve leading/trailing whitespace in patterns; strip() ensures consistent pattern matching
  - DO NOT include comment lines in output; '#' prefix filtering prevents malformed patterns from being used
  - DO NOT assume UTF-8 validity; use errors="ignore" to handle binary corruption or mixed encodings gracefully
  - DO NOT modify or validate pattern syntax; this function only extracts raw strings; validation belongs in the consumer

    changelog:
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
```

---

## _matches_pattern

**Location:** `/Users/davidmontgomery/agentspec/agentspec/utils.py:371`

### Raw YAML Block

```yaml
what: |
  Determines whether a filesystem path matches a gitignore-style pattern string.

  Inputs:
    - path: Path object to test against the pattern
    - pattern: gitignore-style pattern string (e.g., "*.log", "/build/", "**/node_modules/")
    - repo_root: Path object representing the repository root for relative path calculation

  Outputs:
    - Boolean: True if path matches pattern, False otherwise

  Behavior:
    1. Converts the input path to a relative path from repo_root and normalizes path separators to forward slashes for consistent matching
    2. Strips whitespace from pattern and processes special gitignore syntax:
       - Leading /: anchors pattern to repo root (must match from beginning)
       - Trailing /: restricts match to directories only (verifies with is_dir())
       - **/: matches any directory depth; converted to * for fnmatch compatibility
    3. Attempts two matching strategies:
       a) Component-wise matching: splits relative path into parts and tests each component name against the pattern
       b) Full-path matching: tests the entire relative path string against the pattern
    4. For directory-only patterns (trailing /), reconstructs the full path and validates it is actually a directory before returning True
    5. Returns False on any exception (invalid paths, permission errors, etc.)

  Edge cases:
    - Paths with backslashes on Windows are normalized to forward slashes
    - Patterns with **/ in the middle are converted to * (partial support for gitignore semantics)
    - Leading / patterns also match subdirectories via "pattern/*" fallback
    - Directory-only patterns require filesystem verification; non-existent paths return False
    - Exceptions during path resolution or directory checks are silently caught and return False
    deps:
      calls:
        - Path
        - component_path.is_dir
        - enumerate
        - fnmatch.fnmatch
        - path.resolve
        - pattern.endswith
        - pattern.replace
        - pattern.startswith
        - pattern.strip
        - rel_str.split
        - relative_to
        - replace
        - repo_root.resolve
        - str
        - test_full.is_dir
      imports:
        - __future__.annotations
        - agentspec.langs.LanguageRegistry
        - fnmatch
        - os
        - pathlib.Path
        - subprocess
        - typing.Iterable
        - typing.List
        - typing.Optional
        - typing.Set


why: |
  This function provides gitignore-compatible pattern matching for filtering repository contents. The approach uses fnmatch for glob-style wildcard support while layering gitignore-specific semantics (anchoring, directory-only flags, recursive wildcards). Component-wise matching enables patterns like "*.log" to match "dir/file.log" without explicit path separators. The dual matching strategy (component + full-path) accommodates both simple filename patterns and explicit path patterns like "foo/bar/baz". Exception handling ensures robustness when paths don't exist or are inaccessible, defaulting to non-match rather than crashing. Path normalization ensures cross-platform consistency.

guardrails:
  - DO NOT rely on this function for security filtering; it performs pattern matching only and does not validate path traversal attacks or symlink loops
  - DO NOT assume ** semantics are fully gitignore-compliant; the implementation converts **/ to * which is a simplification and may not match complex nested patterns correctly
  - DO NOT use this for real-time filesystem monitoring without caching; repeated is_dir() calls on non-existent paths incur filesystem overhead
  - DO NOT pass non-absolute or non-resolvable paths without ensuring repo_root is also resolvable; relative path calculation will fail silently and return False
  - DO NOT assume exception suppression is safe for all use cases; silent failures on permission errors or invalid paths may mask configuration issues

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
```

---

## _check_agentspecignore

**Location:** `/Users/davidmontgomery/agentspec/agentspec/utils.py:499`

### Raw YAML Block

```yaml
what: |
  Determines whether a given file path should be ignored based on .agentspecignore patterns.

  Returns True if the path matches any ignore pattern, False otherwise.

  Pattern loading strategy (two-tier):
  1. Built-in patterns: Loads agentspec's stock .agentspecignore from the package root directory. These patterns are always applied and provide sensible defaults (e.g., __pycache__, .git, node_modules, etc.).
  2. User patterns: Loads project-specific .agentspecignore from repo_root if it exists. User patterns are merged with built-in patterns, allowing projects to extend or override defaults.

  Matching behavior:
  - Patterns are checked sequentially against the input path
  - First match returns True (path is ignored)
  - If no patterns exist or no matches found, returns False (path is not ignored)
  - Pattern matching is delegated to _matches_pattern() helper

  Edge cases:
  - If repo_root is None, returns False immediately (no context to check patterns)
  - If built-in .agentspecignore cannot be located or loaded, silently continues (exception caught)
  - If user .agentspecignore does not exist, only built-in patterns are used
  - If both ignore files are missing, returns False (nothing to ignore)
  - Empty pattern lists result in False (no matches possible)

  Inputs: path (Path object to check), repo_root (Path to repository root or None)
  Outputs: bool indicating ignore status
    deps:
      calls:
        - Path
        - _matches_pattern
        - _parse_agentspecignore
        - builtin_ignore.exists
        - patterns.extend
        - user_ignore.exists
      imports:
        - __future__.annotations
        - agentspec.langs.LanguageRegistry
        - fnmatch
        - os
        - pathlib.Path
        - subprocess
        - typing.Iterable
        - typing.List
        - typing.Optional
        - typing.Set

why: |
  Two-tier pattern loading provides both sensible defaults and project customization. Built-in patterns protect against common unintended inclusions (compiled artifacts, dependencies, VCS metadata) without requiring every project to maintain identical ignore rules. User patterns enable project-specific filtering (e.g., build directories, generated code, vendor folders) without modifying the package itself.

  Silent exception handling on built-in pattern loading ensures robustness: if the package structure is unusual or agentspec cannot be imported, the function degrades gracefully rather than failing the entire ignore check.

  Early return when repo_root is None prevents unnecessary processing and clarifies intent: ignore checking is meaningless without repository context.

  Sequential pattern matching with early exit (first match wins) is efficient and predictable for users reasoning about which rule caused a path to be ignored.
guardrails:
  - DO NOT apply only user patterns and skip built-in patterns; built-in patterns are mandatory defaults that protect against common mistakes
  - DO NOT raise exceptions if built-in .agentspecignore is missing or unreadable; this would break the function for non-standard installations or edge cases
  - DO NOT return True when repo_root is None; without repository context, ignore status cannot be reliably determined
  - DO NOT modify or cache patterns across multiple calls without invalidation; patterns may change between calls if files are edited
  - DO NOT assume pattern file encoding; delegate encoding handling to _parse_agentspecignore() to ensure consistent UTF-8 or fallback behavior

    changelog:
      - "- 2025-11-02: feat: Enhance multi-language support and improve agentspec handling (2ffec35)"
      - "- 2025-10-31: fix(lint): Fix YAML indentation and whitespace in agentspec blocks (7d7ee57)"
      - "- 2025-10-30: fix(critical): preserve commit hashes in injected CHANGELOG by relaxing section boundary regex (9c524b4)"
```

---

## collect_python_files

**Location:** `/Users/davidmontgomery/agentspec/agentspec/utils.py:599`

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

**Location:** `/Users/davidmontgomery/agentspec/agentspec/utils.py:697`

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

**Location:** `/Users/davidmontgomery/agentspec/agentspec/utils.py:817`

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

