# AgentSpec System Prompts

All system prompts for agentspec generation are stored here as separate `.md` files for easy editing and iteration.

## Available Prompts

### 1. `verbose_docstring.md`
**Used for:** Standard `agentspec generate` command
**Format:** Plain text docstring with WHAT THIS DOES / WHY THIS APPROACH / AGENT INSTRUCTIONS
**Variables:** `{code}`, `{filepath}`, `{hard_data}`

### 2. `terse_docstring.md`
**Used for:** `agentspec generate --terse` command
**Format:** Concise docstring with WHAT / WHY / GUARDRAILS
**Variables:** `{code}`, `{filepath}`

### 3. `agentspec_yaml.md`
**Used for:** `agentspec generate --agentspec-yaml` command
**Format:** YAML block fenced by `---agentspec` / `---/agentspec`
**Variables:** `{code}`, `{filepath}`, `{hard_data}`

## How Prompts Are Loaded

Prompts are loaded via `agentspec/prompts.py`:

```python
from agentspec.prompts import (
    get_verbose_docstring_prompt,
    get_terse_docstring_prompt,
    get_agentspec_yaml_prompt,
)

# Load and format a prompt
prompt = get_verbose_docstring_prompt()
formatted = prompt.format(code="def foo(): pass", filepath="test.py", hard_data="...")
```

## Editing Prompts

1. Open the `.md` file you want to modify
2. Edit the prompt text (keep the `{variable}` placeholders intact)
3. Save the file
4. No code changes needed - changes take effect immediately

## Testing Prompt Changes

```bash
# Test with a single file
agentspec generate myfile.py --dry-run

# Generate on a test file
agentspec generate tests/fixtures/python/test.py

# Compare before/after with --diff-summary
agentspec generate myfile.py --diff-summary
```

## Variables Reference

### `{code}`
The function's source code as a string.

### `{filepath}`
The full path to the file containing the function.

### `{hard_data}`
Deterministic metadata collected from the repository (deps, changelog).
This is a placeholder string that gets replaced with actual metadata during processing.

## Adding a New Prompt

1. Create a new `.md` file in this directory (e.g., `my_custom_prompt.md`)
2. Add a loading function to `agentspec/prompts.py`:
   ```python
   def get_my_custom_prompt() -> str:
       return load_prompt("my_custom_prompt")
   ```
3. Use it in `agentspec/generate.py` or wherever needed

## Prompt Engineering Tips

### DO:
- ✅ Be explicit about output format requirements
- ✅ Provide examples of desired output structure
- ✅ Specify what NOT to include
- ✅ Tell the LLM to use deterministic metadata when available
- ✅ Request comprehensive coverage of edge cases

### DON'T:
- ❌ Make assumptions about what the LLM "knows"
- ❌ Use vague terms like "good documentation"
- ❌ Rely on implicit formatting
- ❌ Skip edge case instructions
- ❌ Forget to tell it what NOT to hallucinate

## Debugging

If a prompt isn't working as expected:

1. **Check variable formatting:**
   Ensure all `{variables}` match what's passed in `format()`

2. **Test the raw prompt:**
   ```bash
   python -c "from agentspec.prompts import get_verbose_docstring_prompt; print(get_verbose_docstring_prompt())"
   ```

3. **Inspect what gets sent to LLM:**
   Add `print(content)` before the `_call_llm()` call in `generate.py`

4. **Compare against known-good output:**
   Use `--update-existing` on files with existing good docstrings to see if the LLM matches
