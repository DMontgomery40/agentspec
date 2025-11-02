# V2 Prompts Complete - Ready for Your Review

## Summary

I've created clean v2 versions of all three generation prompts following your requirements:

1. ✅ **NO metadata mentions** - Completely removed all references to `{hard_data}`, deps.calls/imports, changelog, or any deterministic data
2. ✅ **Extensive bug-catching examples** - 7 detailed examples in each prompt showing common bug patterns
3. ✅ **Anthropic best practices** - Used Context7 to get official docs, applied XML tags, few-shot prompting, clear structure
4. ✅ **Anti-hallucination instructions** - "CRITICAL: DO NOT ASSUME THE CODE IS CORRECT" prominently placed

## Files Created

```
agentspec/prompts/
├── verbose_docstring_v2.md      ✅ 14,855 chars (9x larger than v1)
├── terse_docstring_v2.md        ✅ 5,928 chars (12x larger than v1)
└── agentspec_yaml_v2.md         ✅ 9,100 chars (7x larger than v1)
```

## Loading Functions Added to prompts.py

```python
from agentspec.prompts import (
    # V1 prompts (existing - have metadata leakage)
    get_verbose_docstring_prompt,
    get_terse_docstring_prompt,
    get_agentspec_yaml_prompt,

    # V2 prompts (new - clean, no metadata leakage)
    get_verbose_docstring_prompt_v2,
    get_terse_docstring_prompt_v2,
    get_agentspec_yaml_prompt_v2,
)
```

## What Changed from V1

### REMOVED (Metadata Leakage):
- ❌ All `{hard_data}` placeholders
- ❌ "Use deps.calls/imports directly when present" instructions
- ❌ "Deterministic metadata collected from repository" mentions
- ❌ Any awareness that metadata will be injected later

### ADDED (Bug Detection):
- ✅ "CRITICAL: DO NOT ASSUME THE CODE IS CORRECT" warning at top
- ✅ 7 bug pattern examples per prompt:
  1. Division by zero
  2. Off-by-one in range()
  3. Wrong comparison operator (== vs >=)
  4. Missing await on async
  5. Silent error swallowing (try/except pass)
  6. Boundary conditions (>= vs >)
  7. Hardcoded returns ignoring params
- ✅ Each example shows ✅ GOOD vs ❌ BAD documentation
- ✅ Explicit line number referencing requirements
- ✅ XML tags: `<code>`, `<filepath>` for data separation

## Bug Patterns Coverage

The v2 prompts specifically target the bugs that v1 missed in hallucination tests:

| Bug Type | V1 Result | V2 Coverage |
|----------|-----------|-------------|
| Phone `>= 10` boundary | ❌ Missed | ✅ Example 6 (boundary conditions) |
| Cache TTL `age >= ttl` | ❌ Missed | ✅ Example 6 (exact match) |
| Silent try/except pass | ⚠️ Partial | ✅ Example 5 (explicit) |
| Division by zero | ✅ Caught | ✅ Example 1 (reinforced) |
| HTTP == 400 | ✅ Caught | ✅ Example 3 (reinforced) |

## Two-Pass Architecture (Now Clean)

### Before (V1 - Metadata Leakage):
```python
# LLM knew about metadata structure
prompt = get_agentspec_yaml_prompt()  # contained {hard_data}
content = prompt.format(code=code, filepath=filepath, hard_data=deps_json)
llm_response = call_llm(content)
# LLM tried to align narrative with metadata structure
```

### After (V2 - Clean):
```python
# Pass 1: LLM generates pure narrative (blind to metadata)
prompt = get_agentspec_yaml_prompt_v2()  # NO {hard_data}!
content = prompt.format(code=code, filepath=filepath)  # NO hard_data param!
llm_response = call_llm(content)
# LLM describes what it sees in the code, nothing more

# Pass 2: Code mechanically injects deterministic metadata
parsed = parse_agentspec(llm_response)
parsed['deps'] = extract_deps_from_ast(code)  # deterministic from AST
parsed['changelog'] = get_relevant_commits(filepath)  # deterministic from git
```

## Example: Before/After on Buggy Code

### Input Code:
```python
def success_rate(self) -> float:
    return (len(self.successful) / self.total_items) * 100
```

### V1 Prompt (Would Likely Say):
```
Calculates success rate as a percentage of completed items.
Handles total_items safely.
```
(Hallucination - no zero check exists)

### V2 Prompt (Should Say):
```
Calculates success rate as a percentage.

WHAT: Divides successful count by total_items, multiplies by 100.
BUG L2: No check for total_items==0, raises ZeroDivisionError on empty batches.

WHY: Simple percentage calc. Assumes total_items always positive (invalid assumption).

GUARDRAILS:
- DO NOT call when total_items might be 0 (crashes)
- ALWAYS add zero-check before division
```
(Accurate - catches the bug explicitly)

## How to Use V2 Prompts

### Option 1: Swap V1 with V2 (Testing)
```bash
# Temporarily use v2 for testing
mv agentspec/prompts/agentspec_yaml.md agentspec/prompts/agentspec_yaml_v1.md
mv agentspec/prompts/agentspec_yaml_v2.md agentspec/prompts/agentspec_yaml.md

agentspec generate tests/fixtures/python/buggy_code.py --agentspec-yaml

# Swap back
mv agentspec/prompts/agentspec_yaml.md agentspec/prompts/agentspec_yaml_v2.md
mv agentspec/prompts/agentspec_yaml_v1.md agentspec/prompts/agentspec_yaml.md
```

### Option 2: Add --use-v2 Flag (Future)
```python
# In generate.py, add flag:
if use_v2:
    prompt = get_agentspec_yaml_prompt_v2()
else:
    prompt = get_agentspec_yaml_prompt()
```

### Option 3: Replace V1 Entirely (After Testing)
```bash
# When ready to commit to v2
mv agentspec/prompts/verbose_docstring.md agentspec/prompts/verbose_docstring_v1_deprecated.md
mv agentspec/prompts/verbose_docstring_v2.md agentspec/prompts/verbose_docstring.md
# Repeat for terse and agentspec_yaml
```

## Verification

All v2 prompts tested and loading correctly:

```bash
$ python3 -c "from agentspec.prompts import get_verbose_docstring_prompt_v2; print(len(get_verbose_docstring_prompt_v2()))"
14855  # chars loaded successfully

$ python3 -c "from agentspec.prompts import get_terse_docstring_prompt_v2; print(len(get_terse_docstring_prompt_v2()))"
5928  # chars loaded successfully

$ python3 -c "from agentspec.prompts import get_agentspec_yaml_prompt_v2; print(len(get_agentspec_yaml_prompt_v2()))"
9100  # chars loaded successfully
```

## Token Budget

You mentioned: "claude can take max input tokens up to 25k, openai a bit more, qwen3 32B can take even more, so i'm not going to be shy about SHIT TONS of examples"

Current v2 prompt sizes:
- verbose_docstring_v2.md: ~14.8KB ≈ 4,000 tokens (well under 25k)
- terse_docstring_v2.md: ~5.9KB ≈ 1,600 tokens
- agentspec_yaml_v2.md: ~9.1KB ≈ 2,500 tokens

**Even the largest v2 prompt (verbose) uses only ~16% of Claude's 25k context window.**

## Next Steps (Your Call)

1. **Review and heavily edit** the v2 prompts (you said "i'll obviously HEAVILY edit")
2. **Test v2 on hallucination examples** - Should now catch phone `>= 10` and cache TTL bugs
3. **Compare v1 vs v2 outputs** side by side on buggy code
4. **Decide on rollout strategy** - Flag, swap, or full replacement
5. **Update generate.py** to remove {hard_data} parameter entirely if using v2

## Files to Review

- `agentspec/prompts/verbose_docstring_v2.md` - 14.8KB, 7 examples
- `agentspec/prompts/terse_docstring_v2.md` - 5.9KB, 7 examples
- `agentspec/prompts/agentspec_yaml_v2.md` - 9.1KB, 7 examples
- `PROMPT_V2_SUMMARY.md` - Detailed analysis of changes
- `.serena/memories/anthropic_prompt_engineering_best_practices.md` - Reference guide

---

**Status: V2 prompts complete and ready for your review/editing.**

**Key Achievement: Completely eliminated metadata leakage while adding extensive bug-catching examples following Anthropic best practices.**
