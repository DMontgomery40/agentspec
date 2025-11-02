# Prompt V2 Summary - Clean Versions with No Metadata Leakage

## What Was Created

Created v2 versions of all three prompt files with:
1. **ZERO metadata mentions** - No `{hard_data}`, no "use deps.calls/imports", no instructions about deterministic data
2. **Extensive bug-catching examples** - 7 examples per prompt showing common bug patterns
3. **Anthropic best practices** - XML tags for data separation, few-shot prompting, clear structure
4. **Explicit anti-hallucination instructions** - "CRITICAL: DO NOT ASSUME THE CODE IS CORRECT" at the top

## Files Created

### 1. agentspec/prompts/agentspec_yaml_v2.md
- **Used for:** `agentspec generate --agentspec-yaml` (YAML block output)
- **Size:** ~12KB (up from 1.3KB in v1)
- **Examples:** 7 detailed bug patterns with good/bad comparisons
- **Format:** YAML block with what/why/guardrails sections
- **Key change:** Removed ALL references to deterministic metadata injection

### 2. agentspec/prompts/verbose_docstring_v2.md
- **Used for:** `agentspec generate` (standard verbose docstring output)
- **Size:** ~15KB (up from 1.6KB in v1)
- **Examples:** 7 detailed bug patterns with good/bad comparisons
- **Format:** Plain text with WHAT THIS DOES / WHY THIS APPROACH / AGENT INSTRUCTIONS
- **Key change:** Removed ALL references to deterministic metadata injection

### 3. agentspec/prompts/terse_docstring_v2.md
- **Used for:** `agentspec generate --terse` (concise docstring output)
- **Size:** ~6KB (up from 483 bytes in v1)
- **Examples:** 7 concise bug patterns with good/bad comparisons
- **Format:** Plain text with WHAT / WHY / GUARDRAILS
- **Key change:** Removed ALL references to deterministic metadata injection

## Bug Patterns Covered in Examples

All three prompts include these 7 bug pattern examples:

1. **Division by Zero** - No check before division, raises ZeroDivisionError
2. **Off-by-One in Range** - Using `range(0, len(items), batch_size + 1)` instead of `batch_size`
3. **Wrong Comparison Operator** - Using `== 400` instead of `>= 400` for HTTP errors
4. **Missing Await** - Forgetting `await` on async coroutine, causing type errors
5. **Silent Error Swallowing** - `try/except: pass` creating data inconsistency
6. **Boundary Condition** - Using `>=` instead of `>` for TTL expiration
7. **Hardcoded Return** - Ignoring parameters, returning fixed value (placeholder/stub)

Each example shows:
- ✅ **GOOD** documentation that catches the bug explicitly
- ❌ **BAD** documentation that hallucinates ideal behavior

## Anthropic Best Practices Applied

### 1. XML Tags for Data Separation
```markdown
<filepath>{filepath}</filepath>

<code>
{code}
</code>
```

### 2. Few-Shot Prompting
Each prompt has 7 complete examples showing:
- The buggy code
- Good documentation (catches bug)
- Bad documentation (hallucination)

### 3. Clear Structure
- Instructions first
- Examples second
- Context (code/filepath) last
- Explicit output format at top

### 4. Direct, Specific Instructions
- "CRITICAL: DO NOT ASSUME THE CODE IS CORRECT"
- "Reference specific lines/variables - Don't make vague claims"
- "Document bugs explicitly with line numbers"

### 5. Explicit Format Requirements
Each prompt specifies EXACT output structure with delimiters

## Key Differences from V1

### REMOVED (Metadata Leakage):
```markdown
❌ Deterministic metadata collected from the repository (if any):
{hard_data}

❌ Use deps.calls and deps.imports directly when present in hard_data

❌ If deterministic metadata is provided, integrate it naturally

❌ Changelog: {changelog}
```

### ADDED (Bug Detection):
```markdown
✅ 7 detailed examples of common bugs
✅ "CRITICAL: DO NOT ASSUME THE CODE IS CORRECT" warning
✅ Specific line number referencing instructions
✅ Good vs Bad comparison for each example
✅ XML tags for data separation
✅ Explicit anti-hallucination guidance
```

## Two-Pass Architecture (Clean)

### Pass 1: Narrative Generation (LLM)
```python
# Use v2 prompts - NO metadata mentions
prompt = get_agentspec_yaml_prompt_v2()  # or verbose/terse v2
content = prompt.format(code=code, filepath=filepath)
# NO hard_data parameter!

# LLM generates pure narrative description
llm_response = call_llm(content)
# Output: what/why/guardrails based ONLY on code analysis
```

### Pass 2: Metadata Injection (Code)
```python
# Code mechanically injects deterministic metadata
parsed = parse_agentspec(llm_response)
parsed['deps'] = extract_deps_from_ast(code)  # deterministic
parsed['changelog'] = get_relevant_commits(filepath)  # deterministic

# Final agentspec = LLM narrative + mechanically injected metadata
```

## Testing the V2 Prompts

### Option 1: Update prompts.py to add v2 loading functions
```python
def get_agentspec_yaml_prompt_v2() -> str:
    return load_prompt("agentspec_yaml_v2")

def get_verbose_docstring_prompt_v2() -> str:
    return load_prompt("verbose_docstring_v2")

def get_terse_docstring_prompt_v2() -> str:
    return load_prompt("terse_docstring_v2")
```

### Option 2: Temporarily swap v1 with v2 for testing
```bash
# Test agentspec YAML v2
mv agentspec/prompts/agentspec_yaml.md agentspec/prompts/agentspec_yaml_v1_backup.md
mv agentspec/prompts/agentspec_yaml_v2.md agentspec/prompts/agentspec_yaml.md

# Run generation
agentspec generate tests/fixtures/python/buggy_code.py --agentspec-yaml

# Swap back
mv agentspec/prompts/agentspec_yaml.md agentspec/prompts/agentspec_yaml_v2.md
mv agentspec/prompts/agentspec_yaml_v1_backup.md agentspec/prompts/agentspec_yaml.md
```

### Option 3: Add --use-v2-prompts flag to CLI
```python
# In generate.py
if use_v2_prompts:
    if as_agentspec_yaml:
        prompt = get_agentspec_yaml_prompt_v2()
    elif terse:
        prompt = get_terse_docstring_prompt_v2()
    else:
        prompt = get_verbose_docstring_prompt_v2()
else:
    # existing logic
```

## Expected Improvements

Based on hallucination test results (81% caught, 14% missed, 5% hallucinated):

### Bugs V1 Missed (Should Catch with V2):
1. **Phone number `>= 10` boundary** - Now has Example 6 on boundary conditions
2. **Cache TTL `age >= ttl`** - Exact match in Example 6
3. **Silent try/except pass** - Exact match in Example 5

### Hallucinations V1 Had (Should Fix with V2):
1. **"Safely calculates"** when division has no zero-check
   - Now Example 1 explicitly shows this as BAD
2. **"Handles errors gracefully"** when try/except has pass
   - Now Example 5 explicitly shows this as BAD

### New Strengths:
- Line number referencing is now mandatory
- Every example shows "what it ACTUALLY does" vs "what it SHOULD do"
- XML tags prevent code from bleeding into instructions
- 7 different bug patterns give LLM strong pattern matching

## File Sizes Comparison

| Prompt | V1 Size | V2 Size | Increase |
|--------|---------|---------|----------|
| agentspec_yaml | 1.3 KB | 12 KB | 9x |
| verbose_docstring | 1.6 KB | 15 KB | 9x |
| terse_docstring | 483 B | 6 KB | 12x |

**Total prompt token increase:** ~8-10x more tokens per generation call

**Justification:** User said "claude can take max input tokens up to 25k, openai a bit more, qwen3 32B can take even more, so i'm not going to be shy about SHIT TONS of examples"

## Next Steps

1. **User will heavily edit these prompts** (user quote: "i'll obviously HEAVILY edit")
2. **Add v2 loading functions to prompts.py** if keeping both versions
3. **Run comparative testing** - Generate with v1 vs v2 on hallucination test files
4. **Measure improvement** - Should catch phone number `>= 10` bug now
5. **Consider adding --use-v2-prompts flag** for gradual rollout

## Files Location

```
agentspec/
├── prompts/
│   ├── README.md                       # Existing docs
│   ├── agentspec_yaml.md               # V1 (has metadata leakage)
│   ├── agentspec_yaml_v2.md            # NEW: Clean version
│   ├── verbose_docstring.md            # V1 (has metadata leakage)
│   ├── verbose_docstring_v2.md         # NEW: Clean version
│   ├── terse_docstring.md              # V1 (has metadata leakage)
│   └── terse_docstring_v2.md           # NEW: Clean version
└── prompts.py                          # Needs v2 loading functions added
```

---

**Status: Ready for User Review and Heavy Editing**

These prompts follow Anthropic best practices and include extensive examples, but user explicitly stated they will "obviously HEAVILY edit" - consider these drafts for collaborative refinement.
