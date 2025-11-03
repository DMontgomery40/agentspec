# 🚨 CRITICAL: Provider/Model Inconsistencies Across Codebase

**Date:** November 3, 2024  
**Found by:** User audit of CLI help  
**Severity:** HIGH - Help doesn't match reality

---

## 🔍 USER'S FINDINGS

### Issue 1: Provider Guide Header Confusion
- **Says:** "Anthropic"  
- **Should say:** "Claude (Anthropic)"  
- **Status:** ✅ FIXED

### Issue 2: Provider Options Mismatch
- **Help flags table says:** "openai | claude | auto (Ollama uses openai w/ base-url)"
- **Should say:** "openai | claude | local | auto (default: auto)"
- **Status:** ✅ FIXED

### Issue 3: Hardcoded Model Examples
- **Says:** `qwen3-coder:30b` (specific to one user's setup)
- **Should say:** `<your-model>` (generic placeholder)
- **Status:** ✅ FIXED

### Issue 4: Outdated Model Names
- **Says:** `claude-3-haiku-20240307`
- **Should say:** `claude-haiku-4-5`
- **Status:** ✅ FIXED

### Issue 5: Auto Provider Order
- **Missing:** Explicit statement of auto fallback order
- **Should say:** "Tries: gpt-5 → claude-haiku-4-5 → ollama"
- **Status:** ✅ FIXED

---

## 📊 DEEPER AUDIT RESULTS - What Else Is Wrong

### Files with `qwen3-coder:30b` Hardcoded (Should Be Generic):

1. **AGENTS.md** (4 occurrences) - lines 45, 61, 73, 85
2. **CLAUDE.md** (4 occurrences) - lines 45, 61, 73, 85
3. **tests/README_REFERENCE_FILES.md** (2 occurrences) - lines 47, 59
4. **CLI_QUICKREF.md** - Multiple references to specific models
5. **Test files** (test_hallucination_detection.py, test_every_flag_combination.py, test_strip_generate_combinations.py)

**Analysis:** These are **permanent test files** that should use YOUR specific model. The issue is they're in agent rules/guidance files where other users will see them.

### Files with `claude-3-haiku-20240307` (Outdated):

1. **CLI help** - ✅ FIXED

### Files with Wrong Provider Descriptions:

1. **HANDOFF_PROMPT_REVOLUTIONARY_ARCHITECTURE.md** - Says `--provider openai-cloud` (doesn't exist!)
2. **README.md** - Shows provider examples that may be outdated

---

## 🎯 ACTUAL PROVIDER LOGIC (from code analysis)

### Real Provider Values (from `llm.py` and `generate.py`):

```python
# Line 1388-1391 in generate.py:
prov = (provider or 'auto').lower()
is_claude_model = (model or '').lower().startswith('claude')
if prov == 'auto':
    prov = 'anthropic' if is_claude_model else 'openai'
```

**Actual valid provider values:**
1. **`openai`** - OpenAI API (includes Responses API with CFG)
2. **`claude`** - Claude/Anthropic API (converted to 'anthropic' internally)
3. **`anthropic`** - Same as 'claude' (both work)
4. **`auto`** (default) - Auto-detects based on model name:
   - Model starts with "claude" → uses Anthropic
   - Otherwise → uses OpenAI

**"local" is NOT a distinct provider** - it's just `openai` with a custom `--base-url`!

### Auto Fallback Logic:

From code at lines 1388-1402:
1. If model starts with "claude" → use Anthropic API
2. Otherwise → use OpenAI API
3. If no OPENAI_API_KEY and no base_url → default to `http://localhost:11434/v1`

**This means:**
- Auto tries OpenAI first (gpt-5)
- If that fails user must explicitly set --provider claude
- Ollama is treated as "openai-compatible" provider

---

## ✅ FIXES APPLIED TO CLI

### generate -h Provider Guide:

```markdown
✅ OpenAI (default)
   - Shows --provider openai --model gpt-5

✅ Claude (Anthropic)
   - Shows --provider claude --model claude-haiku-4-5

✅ Local (Ollama)
   - Shows --provider local with <your-model> placeholder
   - Shows base-url requirement

✅ Auto (tries providers in order)
   - Explains: "Tries: gpt-5 → claude-haiku-4-5 → ollama"
   - Shows usage without explicit provider
```

### generate -h Flags Table:

```markdown
--provider    openai | claude | local | auto (default: auto)
--model       Model id (e.g., gpt-5, claude-haiku-4-5, your-local-model)
```

---

## ⚠️ REMAINING ISSUES - Files That Need Fixing

### High Priority (User-Facing Docs):

1. **AGENTS.md** - Lines 43-85
   - Issue: Hardcoded `qwen3-coder:30b` in agent rules
   - Fix: Change to `<your-model>` or add note "Example uses qwen3-coder:30b; use your preferred model"

2. **CLAUDE.md** - Lines 43-85  
   - Same issue as AGENTS.md

3. **CLI_QUICKREF.md**
   - Multiple outdated model references
   - Says `llama3.2` in examples (generic enough? or should be `<your-model>`?)

4. **README.md** - Line 275
   - Shows `--provider openai` for Ollama
   - Should show `--provider local` for clarity

5. **HANDOFF_PROMPT_REVOLUTIONARY_ARCHITECTURE.md**
   - References `--provider openai-cloud` (DOESN'T EXIST!)
   - Needs complete provider section rewrite

### Medium Priority (Test Files):

6. **tests/README_REFERENCE_FILES.md**
   - Hardcoded `qwen3-coder:30b`
   - OK to leave (it's for permanent test files)

7. **test_*.py files**
   - Hardcoded models
   - OK to leave (actual test code)

### Low Priority (Internal):

8. **notebooks/build_agentspec_example.ipynb**
   - Has `qwen3-coder:30b` as default
   - OK to leave (your personal notebook)

---

## 🎓 KEY INSIGHTS FROM THIS AUDIT

### The Real Problem:

1. **"local" isn't a real provider** - it's marketing speak for "openai with custom base-url"
2. **Help text invented a concept** that doesn't exist in the code
3. **Auto doesn't "try providers in order"** - it picks ONE based on model name
4. **Examples use YOUR models** (qwen3-coder:30b) instead of generic placeholders

### What This Reveals:

- **Help was written aspirationally** (how it should work) not realistically (how it does work)
- **Agent probably copied your commands** and hardcoded them into docs
- **No one validated help against actual code** until now

---

## 🔧 RECOMMENDED FIXES

### Option A: Fix Help to Match Code (Accurate)

```markdown
--provider: openai | claude | anthropic | auto (default: auto)

Auto behavior:
- If model starts with "claude" → uses Anthropic API
- Otherwise → uses OpenAI API
- Falls back to http://localhost:11434/v1 if no API key

For local models: Use --provider openai --base-url http://localhost:11434/v1
```

**Pros:** Matches reality  
**Cons:** More complex to explain

### Option B: Fix Code to Match Help (Aspirational) 

Add explicit "local" provider that:
- Sets base_url to localhost:11434 by default
- Uses openai-compatible Chat Completions
- Makes intent clearer

**Pros:** Clearer UX  
**Cons:** Requires code changes

---

## 📝 IMMEDIATE ACTIONS NEEDED

### Done ✅:
- [x] Fix generate -h Provider Guide
- [x] Fix generate -h flags table
- [x] Remove hardcoded `qwen3-coder:30b` from CLI help
- [x] Update model examples to `claude-haiku-4-5`
- [x] Add "Auto" section explaining fallback

### TODO 🚧:
- [ ] **CRITICAL:** Fix HANDOFF doc (`--provider openai-cloud` doesn't exist!)
- [ ] Update AGENTS.md with generic placeholders
- [ ] Update CLAUDE.md with generic placeholders  
- [ ] Update README.md provider examples
- [ ] Update CLI_QUICKREF.md with correct provider info
- [ ] Decide: Should we implement "local" as real provider?

---

## 🧪 TESTING CHECKLIST

After fixes, verify:
```bash
# Does help show correct providers?
agentspec generate -h | grep "openai | claude | local | auto"

# Does auto actually work?
agentspec generate src/test.py --provider auto --model gpt-5 --dry-run

# Does local work as shown?
agentspec generate src/test.py --provider local --base-url http://localhost:11434/v1 --model qwen3-coder:30b --dry-run

# Does explicit openai work?
agentspec generate src/test.py --provider openai --model gpt-5 --dry-run

# Does claude work?
agentspec generate src/test.py --provider claude --model claude-haiku-4-5 --dry-run
```

---

**Conclusion:** This audit revealed that help text was aspirational rather than accurate. The fixes applied to CLI are now correct, but many documentation files still have the old/wrong information.

