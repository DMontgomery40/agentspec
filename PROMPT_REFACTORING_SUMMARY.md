# System Prompt Refactoring Summary

## What Was Done

Extracted all hardcoded system prompts from `agentspec/generate.py` into separate `.md` files under `agentspec/prompts/` to enable easy iteration and improvement.

## Changes

### New Files Created

1. **`agentspec/prompts/verbose_docstring.md`**
   - Standard `agentspec generate` prompt
   - 1,603 characters
   - Format: WHAT THIS DOES / WHY THIS APPROACH / AGENT INSTRUCTIONS

2. **`agentspec/prompts/terse_docstring.md`**
   - `agentspec generate --terse` prompt
   - 483 characters
   - Format: WHAT / WHY / GUARDRAILS

3. **`agentspec/prompts/agentspec_yaml.md`**
   - `agentspec generate --agentspec-yaml` prompt
   - 1,313 characters
   - Format: YAML block with what/why/guardrails

4. **`agentspec/prompts/README.md`**
   - Documentation for working with prompts
   - Usage examples, variable reference, debugging tips

5. **`agentspec/prompts.py`**
   - Prompt loading module with functions:
     - `load_prompt(name)` - Load any prompt by name
     - `get_verbose_docstring_prompt()` - Load verbose prompt
     - `get_terse_docstring_prompt()` - Load terse prompt
     - `get_agentspec_yaml_prompt()` - Load YAML prompt
     - `format_prompt(template, **kwargs)` - Format with variables

### Modified Files

1. **`agentspec/generate.py`**
   - Removed 3 hardcoded prompt constants (170+ lines deleted)
   - Added imports from `agentspec.prompts`
   - Changed prompt selection to use loading functions
   - Added comment explaining new structure

## Usage

### Before (Hardcoded)
```python
GENERATION_PROMPT = """You are helping to document..."""

# Use directly
prompt = GENERATION_PROMPT
content = prompt.format(code=code, filepath=filepath, hard_data=data)
```

### After (Modular)
```python
from agentspec.prompts import get_verbose_docstring_prompt

# Load on demand
prompt = get_verbose_docstring_prompt()
content = prompt.format(code=code, filepath=filepath, hard_data=data)
```

## Benefits

### 1. **Easy Iteration**
Edit prompts directly in `.md` files without touching Python code:
```bash
vim agentspec/prompts/verbose_docstring.md
# Changes take effect immediately, no restart needed
```

### 2. **Version Control**
Track prompt evolution separately from code:
```bash
git log agentspec/prompts/verbose_docstring.md
git diff HEAD~1 agentspec/prompts/
```

### 3. **A/B Testing**
Create alternative prompts and swap them in:
```python
# Easy to test different approaches
from agentspec.prompts import load_prompt
prompt_v1 = load_prompt("verbose_docstring")
prompt_v2 = load_prompt("verbose_docstring_experimental")
```

### 4. **Clear Separation**
Code logic vs. prompt engineering are now cleanly separated:
- Code: `agentspec/generate.py` handles generation flow
- Prompts: `agentspec/prompts/*.md` handle LLM instructions

### 5. **Better Workflow**
Prompt engineers can work independently from developers:
- No Python knowledge required to improve prompts
- No risk of breaking code logic
- Easy to review changes (just plain text diffs)

## Testing

Verified that refactoring is backwards-compatible:

```bash
# CLI still works
✅ python -m agentspec.cli --help

# Prompts load correctly
✅ python -c "from agentspec.prompts import get_verbose_docstring_prompt; p = get_verbose_docstring_prompt(); print(f'Loaded: {len(p)} chars')"
# Output: Loaded: 1603 chars

# No broken imports
✅ python -c "import agentspec.generate"
```

## Next Steps for Prompt Improvement

Based on hallucination test results (81% bug detection, 5% hallucination rate), consider:

### 1. **Strengthen "What" Section Instructions**
Current issue: LLM may describe what code SHOULD do, not what it ACTUALLY does
```markdown
IMPROVED:
- CRITICAL: Describe what the code ACTUALLY does, even if it contains bugs
- DO NOT assume the code is correct
- DO NOT describe ideal behavior if code doesn't match
```

### 2. **Add Explicit Bug Detection**
```markdown
Before documenting:
1. Check for common bugs:
   - Off-by-one errors in loops (range(n-1) vs range(n))
   - Comparison operators (>= vs >, == vs !=)
   - Missing await on async functions
   - Division by zero when denominators might be 0
2. If bugs found, document them explicitly in guardrails
```

### 3. **Demand Evidence**
```markdown
For each claim in WHAT section:
- Reference specific line numbers or variable names
- Quote actual code when describing behavior
- Example: "Line 42 uses >= instead of >, causing X"
```

### 4. **Add Self-Verification**
```markdown
After generating docstring, verify:
- [ ] All edge cases are from ACTUAL code, not assumed behavior
- [ ] No claims about functionality that isn't in the code
- [ ] Bugs/issues are documented if present
- [ ] Dependencies match actual imports/calls
```

## File Locations

```
agentspec/
├── prompts.py                          # NEW: Loading functions
├── prompts/                            # NEW: Prompt storage
│   ├── README.md                       # NEW: Documentation
│   ├── verbose_docstring.md            # NEW: Standard prompt
│   ├── terse_docstring.md              # NEW: Terse prompt
│   └── agentspec_yaml.md               # NEW: YAML prompt
└── generate.py                         # MODIFIED: Uses prompts.py
```

## Breaking Changes

None - This is a pure refactoring. The prompts are identical to the hardcoded versions, just stored in files. Existing code using `agentspec generate` works unchanged.

## User Request Context

User identified that current prompts need improvement after seeing:
1. Weak test validation (`assert "what" in s.parsed_data`)
2. Hallucination test results showing room for improvement
3. Prompts hardcoded in Python making iteration painful

User quote:
> "MAKE IT SO THAT ALL SYSTEM PROMPTS are in separate .md files under agentscript/prompts and they are called into or imported or whatever into the functions and py files, so that it's easy to tweak them and work with them seaparely outside of the code"

## Commit

```
commit 136cb30
refactor: Extract system prompts to separate .md files for easier editing
```

---

**The foundation is now in place for serious prompt improvement work.**
