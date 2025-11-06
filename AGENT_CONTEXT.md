# 🤖 AGENT CONTEXT: Function Specifications

**AGENTS: You MUST print() and read these specifications before modifying code.**

## SPEC: BaseFormatter (agentspec/generators/formatters/base.py:58)

```python
print("[AGENTSPEC] Reading spec for BaseFormatter")
print("[AGENTSPEC] Location: agentspec/generators/formatters/base.py:58")
print("[AGENTSPEC] What: Defines the contract all docstring formatters must implement.

**Required Methods:**
- format(spec) ...")
print("[AGENTSPEC] GUARDRAILS (4 items):")
print("[AGENTSPEC]   1. DO NOT maintain state between format() calls")
print("[AGENTSPEC]   2. ALWAYS validate AgentSpec before formatting")
print("[AGENTSPEC]   3. DO NOT modify input AgentSpec (read-only)")
print("[AGENTSPEC]   4. ALWAYS produce spec-compliant output")
```

**Full Specification (YAML):**

```yaml
what: |
  Defines the contract all docstring formatters must implement.

  **Required Methods:**
  - format(spec) → str: Main formatting method
  - format_section(name, content) → str: Format individual section
  - validate_output(docstring) → bool: Validate output

  **Optional Overrides:**
  - wrap_text(text, width) → str: Text wrapping logic
  - indent(text, spaces) → str: Indentation logic

  Formatters should:
  - Be stateless (no instance state between format() calls)
  - Handle missing optional fields gracefully
  - Produce PEP 257 or JSDoc compliant output
  - Wrap text to appropriate line length

why: |
  ABC ensures all formatters implement consistent interface.
  Polymorphic usage enables swapping formatters without code changes.

guardrails:
  - DO NOT maintain state between format() calls
  - ALWAYS validate AgentSpec before formatting
  - DO NOT modify input AgentSpec (read-only)
  - ALWAYS produce spec-compliant output
```

---

## SPEC: format (agentspec/generators/formatters/base.py:94)

```python
print("[AGENTSPEC] Reading spec for format")
print("[AGENTSPEC] Location: agentspec/generators/formatters/base.py:94")
print("[AGENTSPEC] What: Format AgentSpec as docstring....")
```

**Full Specification (Raw Docstring):**

```
Format AgentSpec as docstring.

Args:
    spec: Validated AgentSpec object

Returns:
    Formatted docstring text (including triple quotes)

Raises:
    ValueError: If spec is invalid
    Exception: Formatting errors

Rationale:
    Primary interface for docstring generation. Returns complete
    docstring ready for insertion into source code.

Guardrails:
    - ALWAYS include triple quotes (''' or """)
    - ALWAYS start with summary line (PEP 257 requirement)
    - DO NOT modify input spec
    - ALWAYS handle missing optional fields
```

---

## SPEC: format_section (agentspec/generators/formatters/base.py:121)

```python
print("[AGENTSPEC] Reading spec for format_section")
print("[AGENTSPEC] Location: agentspec/generators/formatters/base.py:121")
print("[AGENTSPEC] What: Format individual section (Args, Returns, Rationale, etc.)....")
```

**Full Specification (Raw Docstring):**

```
Format individual section (Args, Returns, Rationale, etc.).

Args:
    name: Section name (e.g., "Args", "Rationale")
    content: Section content

Returns:
    Formatted section text

Rationale:
    Allows style-specific section formatting (Google uses indented
    bullet lists, NumPy uses underlined headers, Sphinx uses directives).

Guardrails:
    - DO NOT add section if content is empty
    - ALWAYS follow style conventions for this section
    - ALWAYS indent content appropriately
```

---

## SPEC: validate_output (agentspec/generators/formatters/base.py:143)

```python
print("[AGENTSPEC] Reading spec for validate_output")
print("[AGENTSPEC] Location: agentspec/generators/formatters/base.py:143")
print("[AGENTSPEC] What: Validate formatted docstring is compliant....")
```

**Full Specification (Raw Docstring):**

```
Validate formatted docstring is compliant.

Args:
    docstring: Formatted docstring text

Returns:
    True if valid

Raises:
    ValueError: If docstring is invalid (with explanation)

Rationale:
    Catches formatting bugs before inserting into code.
    Ensures PEP 257/JSDoc compliance.

Guardrails:
    - DO NOT return False (raise ValueError with explanation)
    - ALWAYS check basic requirements (triple quotes, summary line)
```

---

## SPEC: wrap_text (agentspec/generators/formatters/base.py:174)

```python
print("[AGENTSPEC] Reading spec for wrap_text")
print("[AGENTSPEC] Location: agentspec/generators/formatters/base.py:174")
print("[AGENTSPEC] What: Wrap text to specified width with optional indentation....")
```

**Full Specification (Raw Docstring):**

```
Wrap text to specified width with optional indentation.

Args:
    text: Text to wrap
    width: Maximum line width (default 79 for PEP 8)
    indent: Number of spaces to indent wrapped lines

Returns:
    Wrapped and indented text

Rationale:
    Helper for maintaining consistent line length. Uses textwrap
    module for smart wrapping (respects word boundaries).

Guardrails:
    - DO NOT break words mid-word
    - ALWAYS respect existing paragraph breaks
    - DO NOT wrap code blocks or lists
```

---

## SPEC: indent_block (agentspec/generators/formatters/base.py:208)

```python
print("[AGENTSPEC] Reading spec for indent_block")
print("[AGENTSPEC] Location: agentspec/generators/formatters/base.py:208")
print("[AGENTSPEC] What: Indent all lines in text block....")
```

**Full Specification (Raw Docstring):**

```
Indent all lines in text block.

Args:
    text: Text to indent
    spaces: Number of spaces to indent

Returns:
    Indented text

Rationale:
    Helper for indenting sections, examples, etc.

Guardrails:
    - DO NOT indent empty lines (PEP 8 style)
    - ALWAYS preserve relative indentation
```

---

## SPEC: name (agentspec/generators/formatters/base.py:234)

```python
print("[AGENTSPEC] Reading spec for name")
print("[AGENTSPEC] Location: agentspec/generators/formatters/base.py:234")
print("[AGENTSPEC] What: Formatter name (for logging/debugging)....")
```

**Full Specification (Raw Docstring):**

```
Formatter name (for logging/debugging).
```

---

## SPEC: JSDocFormatter (agentspec/generators/formatters/javascript/jsdoc.py:63)

```python
print("[AGENTSPEC] Reading spec for JSDocFormatter")
print("[AGENTSPEC] Location: agentspec/generators/formatters/javascript/jsdoc.py:63")
print("[AGENTSPEC] What: JSDoc formatter for JavaScript....")
```

**Full Specification (Raw Docstring):**

```
JSDoc formatter for JavaScript.

NOTE: This is a stub implementation for architecture completeness.
Full JSDoc support requires JavaScript parser integration (tree-sitter).
```

---

## SPEC: format (agentspec/generators/formatters/javascript/jsdoc.py:71)

```python
print("[AGENTSPEC] Reading spec for format")
print("[AGENTSPEC] Location: agentspec/generators/formatters/javascript/jsdoc.py:71")
print("[AGENTSPEC] What: Format AgentSpec as JSDoc comment....")
```

**Full Specification (Raw Docstring):**

```
Format AgentSpec as JSDoc comment.
```

---

## SPEC: format_section (agentspec/generators/formatters/javascript/jsdoc.py:121)

```python
print("[AGENTSPEC] Reading spec for format_section")
print("[AGENTSPEC] Location: agentspec/generators/formatters/javascript/jsdoc.py:121")
print("[AGENTSPEC] What: Format individual section (stub implementation)....")
```

**Full Specification (Raw Docstring):**

```
Format individual section (stub implementation).
```

---

## SPEC: TSDocFormatter (agentspec/generators/formatters/javascript/tsdoc.py:52)

```python
print("[AGENTSPEC] Reading spec for TSDocFormatter")
print("[AGENTSPEC] Location: agentspec/generators/formatters/javascript/tsdoc.py:52")
print("[AGENTSPEC] What: TSDoc formatter for TypeScript....")
```

**Full Specification (Raw Docstring):**

```
TSDoc formatter for TypeScript.

NOTE: This is a stub implementation for architecture completeness.
Full TSDoc support requires TypeScript parser integration (tree-sitter).
```

---

## SPEC: format (agentspec/generators/formatters/javascript/tsdoc.py:60)

```python
print("[AGENTSPEC] Reading spec for format")
print("[AGENTSPEC] Location: agentspec/generators/formatters/javascript/tsdoc.py:60")
print("[AGENTSPEC] What: Format AgentSpec as TSDoc comment....")
```

**Full Specification (Raw Docstring):**

```
Format AgentSpec as TSDoc comment.
```

---

## SPEC: format_section (agentspec/generators/formatters/javascript/tsdoc.py:103)

```python
print("[AGENTSPEC] Reading spec for format_section")
print("[AGENTSPEC] Location: agentspec/generators/formatters/javascript/tsdoc.py:103")
print("[AGENTSPEC] What: Format individual section (stub implementation)....")
```

**Full Specification (Raw Docstring):**

```
Format individual section (stub implementation).
```

---

## SPEC: GoogleDocstringFormatter (agentspec/generators/formatters/python/google_docstring.py:89)

```python
print("[AGENTSPEC] Reading spec for GoogleDocstringFormatter")
print("[AGENTSPEC] Location: agentspec/generators/formatters/python/google_docstring.py:89")
print("[AGENTSPEC] What: Implements BaseFormatter for Google-style Python docstrings.

**Formatting Rules:**
1. Start with tr...")
print("[AGENTSPEC] GUARDRAILS (3 items):")
print("[AGENTSPEC]   1. DO NOT reorder sections without team discussion (standardization)")
print("[AGENTSPEC]   2. ALWAYS include Rationale and Guardrails (even if short)")
print("[AGENTSPEC]   3. DO NOT wrap code examples (breaks syntax)")
```

**Full Specification (YAML):**

```yaml
what: |
  Implements BaseFormatter for Google-style Python docstrings.

  **Formatting Rules:**
  1. Start with triple quotes (""")
  2. One-line summary (no period at end)
  3. Blank line
  4. Extended description (if present)
  5. Blank line before first section
  6. Sections in order: Args, Returns, Raises, Examples, Rationale, Guardrails, Dependencies
  7. Each section: "Name:" followed by indented content
  8. Close with triple quotes

  **Text Wrapping:**
  - Summary: max 79 chars
  - Description: wrapped at 79 chars
  - Section content: wrapped at 75 chars (4-space indent)

why: |
  Google style provides clear visual hierarchy and good readability.
  Section-based format makes it easy for both humans and tools to parse.

guardrails:
  - DO NOT reorder sections without team discussion (standardization)
  - ALWAYS include Rationale and Guardrails (even if short)
  - DO NOT wrap code examples (breaks syntax)
```

---

## SPEC: format (agentspec/generators/formatters/python/google_docstring.py:123)

```python
print("[AGENTSPEC] Reading spec for format")
print("[AGENTSPEC] Location: agentspec/generators/formatters/python/google_docstring.py:123")
print("[AGENTSPEC] What: Format AgentSpec as Google-style docstring....")
```

**Full Specification (Raw Docstring):**

```
Format AgentSpec as Google-style docstring.

Args:
    spec: Validated AgentSpec object

Returns:
    Complete Google-style docstring with triple quotes

Rationale:
    Builds docstring section by section, following Google style guide.
    Each section is formatted independently, then assembled.

Guardrails:
    - ALWAYS validate spec before formatting
    - DO NOT skip required sections
    - ALWAYS wrap text to 79 chars
```

---

## SPEC: format_section (agentspec/generators/formatters/python/google_docstring.py:214)

```python
print("[AGENTSPEC] Reading spec for format_section")
print("[AGENTSPEC] Location: agentspec/generators/formatters/python/google_docstring.py:214")
print("[AGENTSPEC] What: Format individual section in Google style....")
```

**Full Specification (Raw Docstring):**

```
Format individual section in Google style.

Args:
    name: Section name (e.g., "Args", "Rationale")
    content: Section content text
    items: Optional structured items (for Args, Raises)

Returns:
    Formatted section text

Rationale:
    Google style uses "Section Name:" followed by indented content.
    For structured sections like Args, each item is formatted as:
    "    param_name (type): Description"

Guardrails:
    - ALWAYS indent content by 4 spaces
    - DO NOT add blank lines within section content
    - ALWAYS wrap text to 75 chars (accounting for indent)
```

---

## SPEC: NumpyDocstringFormatter (agentspec/generators/formatters/python/numpy_docstring.py:78)

```python
print("[AGENTSPEC] Reading spec for NumpyDocstringFormatter")
print("[AGENTSPEC] Location: agentspec/generators/formatters/python/numpy_docstring.py:78")
print("[AGENTSPEC] What: NumPy-style docstring formatter....")
```

**Full Specification (Raw Docstring):**

```
NumPy-style docstring formatter.
```

---

## SPEC: format (agentspec/generators/formatters/python/numpy_docstring.py:81)

```python
print("[AGENTSPEC] Reading spec for format")
print("[AGENTSPEC] Location: agentspec/generators/formatters/python/numpy_docstring.py:81")
print("[AGENTSPEC] What: Format AgentSpec as NumPy-style docstring....")
```

**Full Specification (Raw Docstring):**

```
Format AgentSpec as NumPy-style docstring.
```

---

## SPEC: format_section (agentspec/generators/formatters/python/numpy_docstring.py:139)

```python
print("[AGENTSPEC] Reading spec for format_section")
print("[AGENTSPEC] Location: agentspec/generators/formatters/python/numpy_docstring.py:139")
print("[AGENTSPEC] What: Format section with NumPy-style underlined header....")
```

**Full Specification (Raw Docstring):**

```
Format section with NumPy-style underlined header.

NumPy style uses:
Section Name
------------
Content here
```

---

## SPEC: SphinxDocstringFormatter (agentspec/generators/formatters/python/sphinx_docstring.py:68)

```python
print("[AGENTSPEC] Reading spec for SphinxDocstringFormatter")
print("[AGENTSPEC] Location: agentspec/generators/formatters/python/sphinx_docstring.py:68")
print("[AGENTSPEC] What: Sphinx-style docstring formatter....")
```

**Full Specification (Raw Docstring):**

```
Sphinx-style docstring formatter.
```

---

## SPEC: format (agentspec/generators/formatters/python/sphinx_docstring.py:71)

```python
print("[AGENTSPEC] Reading spec for format")
print("[AGENTSPEC] Location: agentspec/generators/formatters/python/sphinx_docstring.py:71")
print("[AGENTSPEC] What: Format AgentSpec as Sphinx-style docstring....")
```

**Full Specification (Raw Docstring):**

```
Format AgentSpec as Sphinx-style docstring.
```

---

## SPEC: format_section (agentspec/generators/formatters/python/sphinx_docstring.py:142)

```python
print("[AGENTSPEC] Reading spec for format_section")
print("[AGENTSPEC] Location: agentspec/generators/formatters/python/sphinx_docstring.py:142")
print("[AGENTSPEC] What: Format section with Sphinx directives (not used in main flow, but required by ABC)....")
```

**Full Specification (Raw Docstring):**

```
Format section with Sphinx directives (not used in main flow, but required by ABC).
```

---

## SPEC: Orchestrator (agentspec/generators/orchestrator.py:104)

```python
print("[AGENTSPEC] Reading spec for Orchestrator")
print("[AGENTSPEC] Location: agentspec/generators/orchestrator.py:104")
print("[AGENTSPEC] What: Coordinates the entire generation flow from source code to formatted docstring.

**Initialization:**...")
print("[AGENTSPEC] GUARDRAILS (4 items):")
print("[AGENTSPEC]   1. DO NOT initialize components in method calls (do it in __init__)")
print("[AGENTSPEC]   2. ALWAYS validate config in __init__ (fail fast)")
print("[AGENTSPEC]   3. DO NOT modify config during generation (read-only)")
print("[AGENTSPEC]   4. ALWAYS use dependency injection (testability)")
```

**Full Specification (YAML):**

```yaml
what: |
  Coordinates the entire generation flow from source code to formatted docstring.

  **Initialization:**
  - Takes GenerationConfig
  - Initializes parser, provider, formatter, prompt builder based on config
  - Validates all components are configured correctly

  **Main Method:**
  - generate_docstring(code, function_name, context) → GenerationResult
  - Runs full pipeline and returns result object

  **Component Selection:**
  - Provider: auto-detect from model name, or use explicit config
  - Formatter: based on style config (google/numpy/sphinx)
  - Prompt: based on terse flag (verbose by default)
  - Parser: based on language (currently only Python)

why: |
  Centralized orchestration makes it easy to:
  - Configure entire pipeline from one config object
  - Test end-to-end flow with real components
  - Swap implementations without changing calling code
  - Add new languages/styles/providers incrementally

guardrails:
  - DO NOT initialize components in method calls (do it in __init__)
  - ALWAYS validate config in __init__ (fail fast)
  - DO NOT modify config during generation (read-only)
  - ALWAYS use dependency injection (testability)
```

---

## SPEC: __init__ (agentspec/generators/orchestrator.py:142)

```python
print("[AGENTSPEC] Reading spec for __init__")
print("[AGENTSPEC] Location: agentspec/generators/orchestrator.py:142")
print("[AGENTSPEC] What: Initialize orchestrator with configuration....")
```

**Full Specification (Raw Docstring):**

```
Initialize orchestrator with configuration.

Args:
    config: Generation configuration

Raises:
    RuntimeError: If configuration is invalid
    ValueError: If unsupported options specified

Rationale:
    Initialize all components up front (fail fast if misconfigured).
    Lazy initialization would delay errors until first generate() call.

Guardrails:
    - ALWAYS validate provider is configured correctly
    - DO NOT initialize parser until needed (language-specific)
    - ALWAYS validate style is supported
```

---

## SPEC: _create_provider (agentspec/generators/orchestrator.py:179)

```python
print("[AGENTSPEC] Reading spec for _create_provider")
print("[AGENTSPEC] Location: agentspec/generators/orchestrator.py:179")
print("[AGENTSPEC] What: Create LLM provider based on config....")
```

**Full Specification (Raw Docstring):**

```
Create LLM provider based on config.

Returns:
    Initialized provider

Rationale:
    Auto-detect provider from model name if provider="auto".
    Otherwise use explicit provider setting.

Guardrails:
    - ALWAYS check model name for anthropic/claude prefix
    - DO NOT assume OpenAI if model unknown (could be Ollama)
    - ALWAYS pass full config to provider (don't filter)
```

---

## SPEC: _create_formatter (agentspec/generators/orchestrator.py:219)

```python
print("[AGENTSPEC] Reading spec for _create_formatter")
print("[AGENTSPEC] Location: agentspec/generators/orchestrator.py:219")
print("[AGENTSPEC] What: Create formatter based on style config....")
```

**Full Specification (Raw Docstring):**

```
Create formatter based on style config.

Returns:
    Initialized formatter

Rationale:
    Map style string to formatter class. Default to Google if invalid.

Guardrails:
    - ALWAYS support google/numpy/sphinx for Python
    - DO NOT fail on unknown style (default to google)
    - ALWAYS log warning if defaulting
```

---

## SPEC: _create_prompt (agentspec/generators/orchestrator.py:249)

```python
print("[AGENTSPEC] Reading spec for _create_prompt")
print("[AGENTSPEC] Location: agentspec/generators/orchestrator.py:249")
print("[AGENTSPEC] What: Create prompt builder based on config....")
```

**Full Specification (Raw Docstring):**

```
Create prompt builder based on config.

Returns:
    Initialized prompt builder

Rationale:
    Use TersePrompt if terse flag set, otherwise VerbosePrompt.

Guardrails:
    - ALWAYS default to verbose (better quality)
    - DO NOT use terse for complex/critical code
```

---

## SPEC: _detect_language (agentspec/generators/orchestrator.py:268)

```python
print("[AGENTSPEC] Reading spec for _detect_language")
print("[AGENTSPEC] Location: agentspec/generators/orchestrator.py:268")
print("[AGENTSPEC] What: Maps file extensions to language identifiers for:
- Parser selection
- Prompt customization
- Format...")
print("[AGENTSPEC] GUARDRAILS (4 items):")
print("[AGENTSPEC]   1. ALWAYS use suffix (not full path) for detection")
print("[AGENTSPEC]   2. DO NOT fail on unknown extensions (default to python)")
print("[AGENTSPEC]   3. ALWAYS lowercase extension for comparison")
print("[AGENTSPEC]   4. DO NOT parse file content (too slow for detection)")
```

**Full Specification (YAML):**

```yaml
what: |
  Maps file extensions to language identifiers for:
  - Parser selection
  - Prompt customization
  - Formatter selection

  Supported extensions:
  - .py, .pyw → python
  - .js, .jsx, .mjs, .cjs → javascript
  - .ts, .tsx → typescript

  Defaults to "python" for unknown extensions (backwards compatibility).

why: |
  Language detection is required because:
  - Different languages have different parsers (PythonParser vs JSParser)
  - Prompts need language-specific instructions
  - Formatters produce different output (docstrings vs JSDoc)

  File extension is the most reliable signal (faster than parsing).

guardrails:
  - ALWAYS use suffix (not full path) for detection
  - DO NOT fail on unknown extensions (default to python)
  - ALWAYS lowercase extension for comparison
  - DO NOT parse file content (too slow for detection)
```

---

## SPEC: generate_docstring (agentspec/generators/orchestrator.py:322)

```python
print("[AGENTSPEC] Reading spec for generate_docstring")
print("[AGENTSPEC] Location: agentspec/generators/orchestrator.py:322")
print("[AGENTSPEC] What: Generate docstring for a function....")
```

**Full Specification (Raw Docstring):**

```
Generate docstring for a function.

Args:
    code: Function source code
    function_name: Name of function
    context: Optional context (file_path, parent_class, etc.)

Returns:
    GenerationResult with success status and generated docstring

Raises:
    Exception: If generation fails (LLM error, validation failure, etc.)

Rationale:
    Main entry point for generation. Runs full pipeline:
    1. Build prompts
    2. Call LLM provider
    3. Get structured AgentSpec
    4. Format as docstring
    5. Return result

Guardrails:
    - ALWAYS wrap in try/except (capture all errors)
    - ALWAYS populate result.errors on failure
    - DO NOT modify input code
    - ALWAYS include original_code in result (for rollback)
```

---

## SPEC: generate_for_file (agentspec/generators/orchestrator.py:462)

```python
print("[AGENTSPEC] Reading spec for generate_for_file")
print("[AGENTSPEC] Location: agentspec/generators/orchestrator.py:462")
print("[AGENTSPEC] What: Generate docstrings for all functions in a file....")
```

**Full Specification (Raw Docstring):**

```
Generate docstrings for all functions in a file.

Args:
    file_path: Path to source file

Returns:
    Dict mapping function names to GenerationResult objects

Rationale:
    Batch process entire file. Useful for CLI commands that operate
    on files/directories.

Guardrails:
    - DO NOT fail entire file if one function fails
    - ALWAYS continue processing remaining functions
    - ALWAYS return results for all functions (even failures)
```

---

## SPEC: BasePrompt (agentspec/generators/prompts/base.py:41)

```python
print("[AGENTSPEC] Reading spec for BasePrompt")
print("[AGENTSPEC] Location: agentspec/generators/prompts/base.py:41")
print("[AGENTSPEC] What: Defines the interface for building LLM prompts.

Prompts are split into:
- System prompt: Overall in...")
print("[AGENTSPEC] GUARDRAILS (3 items):")
print("[AGENTSPEC]   1. DO NOT put code in system prompt (only instructions)")
print("[AGENTSPEC]   2. ALWAYS include format specification (Google/NumPy/etc.)")
print("[AGENTSPEC]   3. DO NOT make prompts language-specific in base class")
```

**Full Specification (YAML):**

```yaml
what: |
  Defines the interface for building LLM prompts.

  Prompts are split into:
  - System prompt: Overall instructions and guidelines
  - User prompt: Specific code to document

  This separation enables better prompt engineering and clearer
  separation of concerns.

why: |
  ABC ensures consistent prompt interface across all modes.
  Enables polymorphic usage (verbose/terse/custom prompts).

guardrails:
  - DO NOT put code in system prompt (only instructions)
  - ALWAYS include format specification (Google/NumPy/etc.)
  - DO NOT make prompts language-specific in base class
```

---

## SPEC: build_system_prompt (agentspec/generators/prompts/base.py:68)

```python
print("[AGENTSPEC] Reading spec for build_system_prompt")
print("[AGENTSPEC] Location: agentspec/generators/prompts/base.py:68")
print("[AGENTSPEC] What: Build system-level prompt with instructions....")
```

**Full Specification (Raw Docstring):**

```
Build system-level prompt with instructions.

Args:
    language: Programming language (python, javascript, typescript)
    style: Docstring style (google, numpy, sphinx, jsdoc, tsdoc)

Returns:
    System prompt text

Rationale:
    System prompt contains general instructions that apply to all
    code in the session. Separating it from user prompt enables
    multi-turn conversations if needed.

Guardrails:
    - ALWAYS include PEP 257/JSDoc compliance requirement
    - ALWAYS emphasize Rationale and Guardrails importance
    - DO NOT include specific code examples (use user prompt)
```

---

## SPEC: build_user_prompt (agentspec/generators/prompts/base.py:92)

```python
print("[AGENTSPEC] Reading spec for build_user_prompt")
print("[AGENTSPEC] Location: agentspec/generators/prompts/base.py:92")
print("[AGENTSPEC] What: Build user prompt with specific code to document....")
```

**Full Specification (Raw Docstring):**

```
Build user prompt with specific code to document.

Args:
    code: Function/class source code
    function_name: Name of function to document
    context: Optional context (file path, existing docstring, etc.)

Returns:
    User prompt text

Rationale:
    User prompt contains the specific code and any context needed
    for documentation generation.

Guardrails:
    - ALWAYS include the full code (don't truncate)
    - ALWAYS include function name (helps LLM focus)
    - DO NOT include existing docstring in code (provide separately)
```

---

## SPEC: get_examples (agentspec/generators/prompts/base.py:120)

```python
print("[AGENTSPEC] Reading spec for get_examples")
print("[AGENTSPEC] Location: agentspec/generators/prompts/base.py:120")
print("[AGENTSPEC] What: Get few-shot examples (optional)....")
```

**Full Specification (Raw Docstring):**

```
Get few-shot examples (optional).

Returns:
    List of example prompts/responses

Rationale:
    Few-shot examples can improve LLM output quality for
    specific formatting or edge cases. Optional because
    they increase token usage.

Guardrails:
    - DO NOT include more than 2-3 examples (token cost)
    - ALWAYS use realistic, high-quality examples
```

---

## SPEC: TersePrompt (agentspec/generators/prompts/terse.py:50)

```python
print("[AGENTSPEC] Reading spec for TersePrompt")
print("[AGENTSPEC] Location: agentspec/generators/prompts/terse.py:50")
print("[AGENTSPEC] What: Generates prompts that instruct LLMs to create focused, concise docstrings.

Key instructions:
- Be ...")
print("[AGENTSPEC] GUARDRAILS (2 items):")
print("[AGENTSPEC]   1. DO NOT skip required sections (Rationale, Guardrails still mandatory)")
print("[AGENTSPEC]   2. ALWAYS maintain minimum quality (no placeholders)")
```

**Full Specification (YAML):**

```yaml
what: |
  Generates prompts that instruct LLMs to create focused, concise docstrings.

  Key instructions:
  - Be concise but complete
  - Focus on critical information
  - Minimum 2 guardrails (not 3+)
  - Shorter rationale (but still present)
  - Skip verbose examples

why: |
  Some situations benefit from concise docs (simple functions,
  context window limits, cost optimization). Terse mode provides
  core safety while reducing verbosity.

guardrails:
  - DO NOT skip required sections (Rationale, Guardrails still mandatory)
  - ALWAYS maintain minimum quality (no placeholders)
```

---

## SPEC: build_system_prompt (agentspec/generators/prompts/terse.py:76)

```python
print("[AGENTSPEC] Reading spec for build_system_prompt")
print("[AGENTSPEC] Location: agentspec/generators/prompts/terse.py:76")
print("[AGENTSPEC] What: Build concise system prompt for terse mode....")
```

**Full Specification (Raw Docstring):**

```
Build concise system prompt for terse mode.
```

---

## SPEC: build_user_prompt (agentspec/generators/prompts/terse.py:130)

```python
print("[AGENTSPEC] Reading spec for build_user_prompt")
print("[AGENTSPEC] Location: agentspec/generators/prompts/terse.py:130")
print("[AGENTSPEC] What: Constructs terse user prompt with essential information only:
- Function identification
- Source cod...")
print("[AGENTSPEC] GUARDRAILS (3 items):")
print("[AGENTSPEC]   1. ALWAYS handle metadata=None case (backwards compatibility)")
print("[AGENTSPEC]   2. DO NOT include verbose metadata formatting (defeats terse purpose)")
print("[AGENTSPEC]   3. ALWAYS include essential facts (params, exceptions, complexity)")
```

**Full Specification (YAML):**

```yaml
what: |
  Constructs terse user prompt with essential information only:
  - Function identification
  - Source code
  - Key metadata (if available, formatted concisely)
  - Generation instructions

why: |
  Terse mode optimizes for token efficiency while maintaining quality.
  Metadata still included but more concisely formatted than verbose mode.

guardrails:
  - ALWAYS handle metadata=None case (backwards compatibility)
  - DO NOT include verbose metadata formatting (defeats terse purpose)
  - ALWAYS include essential facts (params, exceptions, complexity)
```

---

## SPEC: AnthropicProvider (agentspec/generators/providers/anthropic.py:61)

```python
print("[AGENTSPEC] Reading spec for AnthropicProvider")
print("[AGENTSPEC] Location: agentspec/generators/providers/anthropic.py:61")
print("[AGENTSPEC] What: Implements BaseProvider for Claude models using the Anthropic Python SDK
and Instructor for structur...")
print("[AGENTSPEC] GUARDRAILS (4 items):")
print("[AGENTSPEC]   1. DO NOT change message concatenation separator from \n\n (semantic impact)")
print("[AGENTSPEC]   2. DO NOT remove lazy import try/except (breaks optional dependency)")
print("[AGENTSPEC]   3. ALWAYS preserve system message content (contains critical instructions)")
print("[AGENTSPEC]   4. DO NOT modify Instructor client creation (specific API required)")
```

**Full Specification (YAML):**

```yaml
what: |
  Implements BaseProvider for Claude models using the Anthropic Python SDK
  and Instructor for structured outputs.

  **Initialization:**
  - Lazy-loads anthropic and instructor libraries (optional dependencies)
  - Reads ANTHROPIC_API_KEY from environment
  - Creates Instructor-wrapped client on first use

  **Message Handling:**
  - Concatenates system and user messages with \n\n separator
  - Sends as single user message (Claude's preferred format for this use case)
  - Filters out assistant messages (one-way generation, not conversation)

  **Structured Outputs:**
  - Uses Instructor's `client.chat.completions.create()` with response_model
  - Returns validated AgentSpec Pydantic model
  - Automatic retries with exponential backoff (Instructor feature)

why: |
  Message concatenation (vs multi-turn format) simplifies the interface for
  single-shot docstring generation. Claude handles concatenated prompts well
  and this avoids complex conversation state management.

  Instructor provides automatic validation, retries, and error handling,
  reducing boilerplate code and improving reliability.

guardrails:
  - DO NOT change message concatenation separator from \n\n (semantic impact)
  - DO NOT remove lazy import try/except (breaks optional dependency)
  - ALWAYS preserve system message content (contains critical instructions)
  - DO NOT modify Instructor client creation (specific API required)
```

---

## SPEC: __init__ (agentspec/generators/providers/anthropic.py:101)

```python
print("[AGENTSPEC] Reading spec for __init__")
print("[AGENTSPEC] Location: agentspec/generators/providers/anthropic.py:101")
print("[AGENTSPEC] What: Initialize Anthropic provider with config....")
```

**Full Specification (Raw Docstring):**

```
Initialize Anthropic provider with config.
```

---

## SPEC: _ensure_client (agentspec/generators/providers/anthropic.py:107)

```python
print("[AGENTSPEC] Reading spec for _ensure_client")
print("[AGENTSPEC] Location: agentspec/generators/providers/anthropic.py:107")
print("[AGENTSPEC] What: Lazy initialize Anthropic client....")
```

**Full Specification (Raw Docstring):**

```
Lazy initialize Anthropic client.
```

---

## SPEC: validate_config (agentspec/generators/providers/anthropic.py:142)

```python
print("[AGENTSPEC] Reading spec for validate_config")
print("[AGENTSPEC] Location: agentspec/generators/providers/anthropic.py:142")
print("[AGENTSPEC] What: Validate Anthropic configuration....")
```

**Full Specification (Raw Docstring):**

```
Validate Anthropic configuration.

Checks:
- ANTHROPIC_API_KEY is set
- anthropic library is installed
- instructor library is installed

Returns:
    True if valid

Raises:
    RuntimeError: If configuration is invalid
```

---

## SPEC: generate (agentspec/generators/providers/anthropic.py:160)

```python
print("[AGENTSPEC] Reading spec for generate")
print("[AGENTSPEC] Location: agentspec/generators/providers/anthropic.py:160")
print("[AGENTSPEC] What: Generate structured AgentSpec using Claude....")
```

**Full Specification (Raw Docstring):**

```
Generate structured AgentSpec using Claude.

Args:
    prompt: User prompt describing the code
    system_prompt: System instructions (generation guidelines)
    **kwargs: Additional parameters (ignored for now)

Returns:
    Validated AgentSpec object

Raises:
    RuntimeError: If provider not configured
    ValueError: If prompt is empty
    Exception: API errors, rate limits, etc.

Rationale:
    Uses Instructor's response_model parameter to get structured output.
    Instructor handles JSON parsing, validation, and retries automatically.

Guardrails:
    - ALWAYS validate prompt is non-empty
    - DO NOT modify temperature/max_tokens from config without reason
    - ALWAYS use response_model for structured outputs
```

---

## SPEC: generate_chat (agentspec/generators/providers/anthropic.py:223)

```python
print("[AGENTSPEC] Reading spec for generate_chat")
print("[AGENTSPEC] Location: agentspec/generators/providers/anthropic.py:223")
print("[AGENTSPEC] What: Lower-level chat interface (returns raw text)....")
```

**Full Specification (Raw Docstring):**

```
Lower-level chat interface (returns raw text).

Args:
    messages: List of {role, content} dicts
    temperature: Override config temperature
    max_tokens: Override config max_tokens
    **kwargs: Additional parameters

Returns:
    Raw text response from Claude

Rationale:
    For workflows that need raw text instead of structured AgentSpec.
    Uses the same concatenation logic as generate().

Guardrails:
    - DO NOT modify message concatenation logic
    - ALWAYS filter to system/user roles only
```

---

## SPEC: BaseProvider (agentspec/generators/providers/base.py:59)

```python
print("[AGENTSPEC] Reading spec for BaseProvider")
print("[AGENTSPEC] Location: agentspec/generators/providers/base.py:59")
print("[AGENTSPEC] What: Defines the contract all LLM providers must implement. Subclasses handle
provider-specific details (...")
print("[AGENTSPEC] GUARDRAILS (4 items):")
print("[AGENTSPEC]   1. DO NOT perform I/O in __init__ (lazy initialization only)")
print("[AGENTSPEC]   2. ALWAYS validate API keys before first API call")
print("[AGENTSPEC]   3. DO NOT swallow exceptions (let them propagate with context)")
print("[AGENTSPEC]   4. ALWAYS return AgentSpec from generate() (not dict or JSON string)")
```

**Full Specification (YAML):**

```yaml
what: |
  Defines the contract all LLM providers must implement. Subclasses handle
  provider-specific details (API clients, message formatting, etc.) while
  presenting a uniform interface to the orchestrator.

  **Required Methods:**
  - generate(prompt, config) → AgentSpec: Generate structured docstring spec
  - generate_chat(messages, config) → str: Lower-level chat interface
  - validate_config() → bool: Check provider configuration is valid

  **Lifecycle:**
  1. Instantiate provider (lazy initialization, no I/O)
  2. Call validate_config() to check auth/connectivity
  3. Call generate() with prompt and config
  4. Provider returns validated AgentSpec or raises exception

  Subclasses should implement lazy initialization (defer API client creation
  until first generate() call) to avoid blocking during import.

why: |
  ABC pattern enables polymorphism - the orchestrator can work with any
  provider without knowing implementation details. This is critical for:
  - Testing (use mock provider without real API calls)
  - Multi-provider support (fallback from Claude to Ollama)
  - User choice (users pick their preferred provider)

guardrails:
  - DO NOT perform I/O in __init__ (lazy initialization only)
  - ALWAYS validate API keys before first API call
  - DO NOT swallow exceptions (let them propagate with context)
  - ALWAYS return AgentSpec from generate() (not dict or JSON string)
```

---

## SPEC: __init__ (agentspec/generators/providers/base.py:98)

```python
print("[AGENTSPEC] Reading spec for __init__")
print("[AGENTSPEC] Location: agentspec/generators/providers/base.py:98")
print("[AGENTSPEC] What: Initialize provider with configuration....")
```

**Full Specification (Raw Docstring):**

```
Initialize provider with configuration.

Args:
    config: Generation configuration (model, temperature, etc.)

Rationale:
    Store config for later use but don't initialize API clients yet.
    Lazy initialization avoids blocking imports and allows validation
    before making expensive API calls.

Guardrails:
    - DO NOT make API calls in __init__
    - DO NOT validate API keys here (do it in validate_config)
    - ALWAYS store config for later use
```

---

## SPEC: generate (agentspec/generators/providers/base.py:118)

```python
print("[AGENTSPEC] Reading spec for generate")
print("[AGENTSPEC] Location: agentspec/generators/providers/base.py:118")
print("[AGENTSPEC] What: Generate structured AgentSpec from prompt....")
```

**Full Specification (Raw Docstring):**

```
Generate structured AgentSpec from prompt.

Args:
    prompt: User prompt describing the code to document
    system_prompt: Optional system prompt with instructions
    **kwargs: Provider-specific parameters

Returns:
    Validated AgentSpec object

Raises:
    RuntimeError: If provider is not configured correctly
    ValueError: If prompt is empty or invalid
    ConnectionError: If API is unreachable
    Exception: Provider-specific errors (rate limits, auth failures, etc.)

Rationale:
    This is the primary interface for generating docstrings. Returns
    structured Pydantic models instead of raw text to ensure validation.

Guardrails:
    - ALWAYS use Instructor for structured outputs
    - DO NOT parse JSON manually (Instructor handles it)
    - ALWAYS validate returned AgentSpec before returning
    - DO NOT retry on failures (let orchestrator handle retries)
```

---

## SPEC: generate_chat (agentspec/generators/providers/base.py:154)

```python
print("[AGENTSPEC] Reading spec for generate_chat")
print("[AGENTSPEC] Location: agentspec/generators/providers/base.py:154")
print("[AGENTSPEC] What: Lower-level chat interface for custom workflows....")
```

**Full Specification (Raw Docstring):**

```
Lower-level chat interface for custom workflows.

Args:
    messages: List of message dicts with 'role' and 'content' keys
    temperature: Sampling temperature (overrides config)
    max_tokens: Max tokens in response (overrides config)
    **kwargs: Provider-specific parameters

Returns:
    Raw text response from LLM

Raises:
    RuntimeError: If provider is not configured correctly
    ConnectionError: If API is unreachable
    Exception: Provider-specific errors

Rationale:
    Some workflows need raw chat interface (e.g., multi-turn conversations,
    custom JSON parsing). This method provides escape hatch from structured
    outputs while maintaining consistent error handling.

Guardrails:
    - DO NOT use this for standard generation (use generate() instead)
    - ALWAYS normalize message format before sending to API
    - DO NOT modify messages list in-place
```

---

## SPEC: validate_config (agentspec/generators/providers/base.py:191)

```python
print("[AGENTSPEC] Reading spec for validate_config")
print("[AGENTSPEC] Location: agentspec/generators/providers/base.py:191")
print("[AGENTSPEC] What: Validate provider configuration....")
```

**Full Specification (Raw Docstring):**

```
Validate provider configuration.

Returns:
    True if configuration is valid (API key present, model accessible, etc.)

Raises:
    RuntimeError: If configuration is invalid (missing API key, etc.)

Rationale:
    Explicit validation allows early failure with clear error messages
    instead of cryptic API errors on first generate() call.

Guardrails:
    - DO NOT make expensive API calls (just check config)
    - ALWAYS raise descriptive exceptions (include what's wrong)
    - DO NOT return False (raise exception instead for clarity)
```

---

## SPEC: name (agentspec/generators/providers/base.py:213)

```python
print("[AGENTSPEC] Reading spec for name")
print("[AGENTSPEC] Location: agentspec/generators/providers/base.py:213")
print("[AGENTSPEC] What: Provider name (for logging/debugging)....")
```

**Full Specification (Raw Docstring):**

```
Provider name (for logging/debugging).
```

---

## SPEC: LocalProvider (agentspec/generators/providers/local.py:60)

```python
print("[AGENTSPEC] Reading spec for LocalProvider")
print("[AGENTSPEC] Location: agentspec/generators/providers/local.py:60")
print("[AGENTSPEC] What: Extends OpenAIProvider with defaults optimized for local LLM services:
- Base URL defaults to http:/...")
print("[AGENTSPEC] GUARDRAILS (3 items):")
print("[AGENTSPEC]   1. DO NOT override generate() or generate_chat() (use parent implementations)")
print("[AGENTSPEC]   2. DO NOT add custom logic (keep it generic for all local services)")
print("[AGENTSPEC]   3. ALWAYS inherit from OpenAIProvider (don't duplicate code)")
```

**Full Specification (YAML):**

```yaml
what: |
  Extends OpenAIProvider with defaults optimized for local LLM services:
  - Base URL defaults to http://localhost:11434/v1 (Ollama)
  - API key defaults to "not-needed" (no auth)
  - Otherwise identical to OpenAIProvider

  This is purely a convenience class - users can achieve the same result
  by using OpenAIProvider with --base-url http://localhost:11434/v1.

why: |
  Explicit LocalProvider class improves UX:
  - Clearer intent (--provider local vs --provider openai --base-url ...)
  - Better error messages (can detect Ollama not running)
  - Easier documentation (one section for local, one for cloud)

guardrails:
  - DO NOT override generate() or generate_chat() (use parent implementations)
  - DO NOT add custom logic (keep it generic for all local services)
  - ALWAYS inherit from OpenAIProvider (don't duplicate code)
```

---

## SPEC: __init__ (agentspec/generators/providers/local.py:87)

```python
print("[AGENTSPEC] Reading spec for __init__")
print("[AGENTSPEC] Location: agentspec/generators/providers/local.py:87")
print("[AGENTSPEC] What: Initialize local provider with Ollama defaults....")
```

**Full Specification (Raw Docstring):**

```
Initialize local provider with Ollama defaults.

Args:
    config: Generation configuration

Rationale:
    Override base_url if not set, defaulting to Ollama. Otherwise
    delegate everything to OpenAIProvider.

Guardrails:
    - DO NOT require API key (local services are unauthenticated)
    - ALWAYS check OLLAMA_BASE_URL before using default
```

---

## SPEC: name (agentspec/generators/providers/local.py:113)

```python
print("[AGENTSPEC] Reading spec for name")
print("[AGENTSPEC] Location: agentspec/generators/providers/local.py:113")
print("[AGENTSPEC] What: Override name for clearer logging....")
```

**Full Specification (Raw Docstring):**

```
Override name for clearer logging.
```

---

## SPEC: OpenAIProvider (agentspec/generators/providers/openai.py:62)

```python
print("[AGENTSPEC] Reading spec for OpenAIProvider")
print("[AGENTSPEC] Location: agentspec/generators/providers/openai.py:62")
print("[AGENTSPEC] What: Implements BaseProvider for OpenAI and any OpenAI-compatible API.

**Initialization:**
- Lazy-loads ...")
print("[AGENTSPEC] GUARDRAILS (4 items):")
print("[AGENTSPEC]   1. DO NOT remove environment variable fallbacks (breaks deployments)")
print("[AGENTSPEC]   2. DO NOT change message format (breaks OpenAI API compliance)")
print("[AGENTSPEC]   3. ALWAYS validate roles are system/user/assistant")
print("[AGENTSPEC]   4. DO NOT remove lazy import (breaks optional dependency)")
```

**Full Specification (YAML):**

```yaml
what: |
  Implements BaseProvider for OpenAI and any OpenAI-compatible API.

  **Initialization:**
  - Lazy-loads openai and instructor libraries
  - Resolves API key and base URL from environment or config
  - Creates Instructor-wrapped client on first use

  **Message Handling:**
  - Preserves system/user/assistant role structure (OpenAI format)
  - Normalizes unknown roles to 'user'
  - No message concatenation (unlike Anthropic provider)

  **Structured Outputs:**
  - Uses Instructor's `client.chat.completions.create()` with response_model
  - Automatic JSON schema generation from Pydantic models
  - Built-in retry logic with exponential backoff

  **Fallback Logic:**
  - API key: Try multiple env vars, fallback to "not-needed" for local services
  - Base URL: Try multiple env vars, fallback to OpenAI default

why: |
  Preserving OpenAI message format (vs Anthropic's concatenation) enables
  proper multi-turn conversations if needed in future. More flexibility.

  Environment variable fallback chain supports diverse deployment scenarios:
  - Cloud: OPENAI_API_KEY + default base URL
  - Ollama: OLLAMA_BASE_URL + "not-needed" API key
  - Custom: AGENTSPEC_OPENAI_BASE_URL + AGENTSPEC_OPENAI_API_KEY

guardrails:
  - DO NOT remove environment variable fallbacks (breaks deployments)
  - DO NOT change message format (breaks OpenAI API compliance)
  - ALWAYS validate roles are system/user/assistant
  - DO NOT remove lazy import (breaks optional dependency)
```

---

## SPEC: __init__ (agentspec/generators/providers/openai.py:106)

```python
print("[AGENTSPEC] Reading spec for __init__")
print("[AGENTSPEC] Location: agentspec/generators/providers/openai.py:106")
print("[AGENTSPEC] What: Initialize OpenAI provider with config....")
```

**Full Specification (Raw Docstring):**

```
Initialize OpenAI provider with config.
```

---

## SPEC: _ensure_client (agentspec/generators/providers/openai.py:112)

```python
print("[AGENTSPEC] Reading spec for _ensure_client")
print("[AGENTSPEC] Location: agentspec/generators/providers/openai.py:112")
print("[AGENTSPEC] What: Lazy initialize OpenAI client....")
```

**Full Specification (Raw Docstring):**

```
Lazy initialize OpenAI client.
```

---

## SPEC: validate_config (agentspec/generators/providers/openai.py:155)

```python
print("[AGENTSPEC] Reading spec for validate_config")
print("[AGENTSPEC] Location: agentspec/generators/providers/openai.py:155")
print("[AGENTSPEC] What: Validate OpenAI configuration....")
```

**Full Specification (Raw Docstring):**

```
Validate OpenAI configuration.

Checks:
- openai library is installed
- instructor library is installed
- API key is set (or "not-needed" for local)
- Base URL is set

Returns:
    True if valid

Raises:
    RuntimeError: If configuration is invalid
```

---

## SPEC: generate (agentspec/generators/providers/openai.py:174)

```python
print("[AGENTSPEC] Reading spec for generate")
print("[AGENTSPEC] Location: agentspec/generators/providers/openai.py:174")
print("[AGENTSPEC] What: Generate structured AgentSpec using OpenAI-compatible API....")
```

**Full Specification (Raw Docstring):**

```
Generate structured AgentSpec using OpenAI-compatible API.

Args:
    prompt: User prompt describing the code
    system_prompt: System instructions (generation guidelines)
    **kwargs: Additional parameters (ignored for now)

Returns:
    Validated AgentSpec object

Raises:
    RuntimeError: If provider not configured
    ValueError: If prompt is empty
    Exception: API errors, rate limits, etc.

Rationale:
    Uses Instructor's response_model parameter to get structured output.
    Preserves OpenAI message format (system/user roles) for compatibility.

Guardrails:
    - ALWAYS validate prompt is non-empty
    - DO NOT modify temperature/max_tokens from config without reason
    - ALWAYS preserve message role structure
```

---

## SPEC: generate_chat (agentspec/generators/providers/openai.py:231)

```python
print("[AGENTSPEC] Reading spec for generate_chat")
print("[AGENTSPEC] Location: agentspec/generators/providers/openai.py:231")
print("[AGENTSPEC] What: Lower-level chat interface (returns raw text)....")
```

**Full Specification (Raw Docstring):**

```
Lower-level chat interface (returns raw text).

Args:
    messages: List of {role, content} dicts
    temperature: Override config temperature
    max_tokens: Override config max_tokens
    **kwargs: Additional parameters

Returns:
    Raw text response from OpenAI

Rationale:
    For workflows that need raw text instead of structured AgentSpec.
    Preserves full message structure (system/user/assistant roles).

Guardrails:
    - DO NOT modify message structure
    - ALWAYS normalize unknown roles to 'user'
    - DO NOT concatenate messages (unlike Anthropic)
```

---

