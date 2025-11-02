#!/usr/bin/env python3
"""
Prompt loading and management for agentspec generation.

All system prompts are stored as .md files in agentspec/prompts/
for easy editing and iteration.
"""
from pathlib import Path
from typing import Dict, Any

# Directory containing all prompt templates
PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt(prompt_name: str) -> str:
    """
    ---agentspec
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
        ---/agentspec
    """
    prompt_file = PROMPTS_DIR / f"{prompt_name}.md"
    if not prompt_file.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {prompt_file}\n"
            f"Available prompts in {PROMPTS_DIR}:\n"
            + "\n".join(f"  - {p.stem}" for p in PROMPTS_DIR.glob("*.md"))
        )
    return prompt_file.read_text(encoding="utf-8")


def load_base_prompt() -> str:
    """
    ---agentspec
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
    ---/agentspec
    """
    return (PROMPTS_DIR / "base_prompt.md").read_text(encoding="utf-8")


def load_examples_json() -> Dict[str, Any]:
    """
    ---agentspec
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
    ---/agentspec
    """
    import json
    text = (PROMPTS_DIR / "examples.json").read_text(encoding="utf-8")
    return json.loads(text)


def load_agentspec_yaml_grammar() -> str:
    """
    ---agentspec
    what: |
      Load and return the CFG grammar used to constrain agentspec YAML generation. The grammar enforces the presence and order of sections (what, why, guardrails) and exact block fences `---agentspec` / `---/agentspec`.

      Inputs: none
      Outputs: string contents of `agentspec/prompts/agentspec_yaml.lark`

    deps:
      calls:
        - PROMPTS_DIR.joinpath
        - read_text
      imports:
        - pathlib.Path
        - typing.Any
        - typing.Dict

    why: |
      Format drift leads to post-processing and brittle parsing. Centralizing grammar loading lets the generator pass it to an API (e.g., Responses API with grammar tools) and enables test validation.

    guardrails:
      - DO NOT modify this function to parse/validate grammar; loading only
      - DO NOT change the filename without updating all call sites
      - ALWAYS keep fences and section names synchronized with generation expectations

    changelog:
      - "- 2025-11-02: feat: Add grammar loader for YAML block enforcement (handoff execution)"
    ---/agentspec
    """
    return (PROMPTS_DIR / "agentspec_yaml.lark").read_text(encoding="utf-8")


def get_verbose_docstring_prompt() -> str:
    """
    ---agentspec
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
        ---/agentspec
    """
    return load_prompt("verbose_docstring")


def get_terse_docstring_prompt() -> str:
    """
    ---agentspec
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
        ---/agentspec
    """
    return load_prompt("terse_docstring")


def get_agentspec_yaml_prompt() -> str:
    """
    ---agentspec
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
        ---/agentspec
    """
    return load_prompt("agentspec_yaml")


# V2 Prompts (Clean - No Metadata Leakage)
# These prompts have:
# - NO metadata mentions (no {hard_data}, no deps.calls/imports instructions)
# - Extensive bug-catching examples (7 patterns each)
# - Anthropic best practices (XML tags, few-shot prompting)
# - Explicit anti-hallucination instructions

def get_verbose_docstring_prompt_v2() -> str:
    """
    ---agentspec
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
        ---/agentspec
    """
    return load_prompt("verbose_docstring_v2")


def get_terse_docstring_prompt_v2() -> str:
    """
    ---agentspec
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
        ---/agentspec
    """
    return load_prompt("terse_docstring_v2")


def get_agentspec_yaml_prompt_v2() -> str:
    """
    ---agentspec
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
        ---/agentspec
    """
    return load_prompt("agentspec_yaml_v2")


def format_prompt(template: str, **kwargs: Any) -> str:
    """
    ---agentspec
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
        ---/agentspec
    """
    return template.format(**kwargs)
