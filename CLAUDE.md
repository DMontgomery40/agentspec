# 🧪 MANDATORY: TEST THE CODE YOU ACTUALLY CHANGED

## ⚠️ CRITICAL: Running tests ≠ Proving your fix works

**DO NOT claim success just because existing tests pass.**

When you edit code, you MUST:

1. **BEFORE claiming success:** Write a test that exercises the EXACT code path you modified
2. **VERIFY the test would FAIL without your fix** (or write it to fail first, then make it pass)
3. **VERIFY the test PASSES with your fix**
4. **RUN the full test suite** to ensure no regressions
5. **SAVE tests in `agentspec/tests/`**

### Commands

**TO RUN ALL TESTS:** `source .venv/bin/activate && pytest -q`
**TO RUN SPECIFIC TEST:** `source .venv/bin/activate && pytest tests/test_filename.py -v`

---

## 🎯 Testing Agentspec Functionality (PERMANENT TEST FILES)

### ⚠️ NEVER CREATE TEMPORARY TEST FILES

**DO NOT** create files like `tmp_test.tsx`, `tmp_simple.js`, `test_example.py`, etc.

**ALWAYS** use these permanent production files for testing:

- **TypeScript/TSX:** `/Users/davidmontgomery/faxbot_folder/faxbot/api/admin_ui/src/components/Dashboard.tsx`
- **Python:** `/Users/davidmontgomery/faxbot_folder/faxbot/api/app/phaxio_service.py`
- **JavaScript:** `/Users/davidmontgomery/agro/gui/js/indexing.js`

Symlinks exist in `/tests/`:
- `ref_Dashboard.tsx`
- `ref_phaxio_service.py`
- `ref_indexing.js`

### LLM Configuration (MANDATORY for agentspec generate tests)

**ALWAYS use these parameters:**
```bash
--provider openai \
--base-url http://localhost:11434/v1 \
--model qwen3-coder:30b \
--terse \
--force-context \
--agentspec-yaml \
--update-existing
```

**Only add `--strip` when explicitly told to start fresh.**

### Example Test Commands

**TypeScript/TSX Test:**
```bash
agentspec generate /Users/davidmontgomery/faxbot_folder/faxbot/api/admin_ui/src/components/Dashboard.tsx \
  --provider openai \
  --base-url http://localhost:11434/v1 \
  --model qwen3-coder:30b \
  --terse \
  --force-context \
  --agentspec-yaml \
  --update-existing
```

**Python Test:**
```bash
agentspec generate /Users/davidmontgomery/faxbot_folder/faxbot/api/app/phaxio_service.py \
  --provider openai \
  --base-url http://localhost:11434/v1 \
  --model qwen3-coder:30b \
  --terse \
  --force-context \
  --agentspec-yaml \
  --update-existing
```

**JavaScript Test:**
```bash
agentspec generate /Users/davidmontgomery/agro/gui/js/indexing.js \
  --provider openai \
  --base-url http://localhost:11434/v1 \
  --model qwen3-coder:30b \
  --terse \
  --force-context \
  --agentspec-yaml \
  --update-existing
```

**Why these files?**
- Real git history for changelog testing
- Production complexity for realistic testing
- No temp file cleanup needed
- Reproducible results

See `.serena/memories/permanent_test_files.md` and `tests/README_REFERENCE_FILES.md` for details.

---

## Example of CORRECT testing workflow:

### ❌ **WRONG:**
```
User: "Fix bug where .worktrees/ files are processed"
Agent: *edits collect_source_files()*
Agent: *runs pytest -q*
Agent: "25 tests pass ✅ Bug fixed!"
User: "STILL BROKEN"
```

**Why this failed:** The 25 tests didn't exercise file discovery. They tested completely different code paths.

### ✅ **RIGHT:**
```
User: "Fix bug where .worktrees/ files are processed"
Agent: *reads agentspec for collect_source_files()*
Agent: *prints the 'what' and 'guardrails' sections*
Agent: *writes test_excludes_worktrees_directory() that:
        - creates a .worktrees/ directory with JS files
        - calls discover_files()
        - asserts .worktrees/ files are NOT in results*
Agent: *runs new test - it FAILS* ❌
Agent: *edits discover_files() to exclude .worktrees/*
Agent: *updates agentspec with changelog entry*
Agent: *runs new test - it PASSES* ✅
Agent: *runs full suite - all pass*
Agent: "Bug fixed with proof: tests/test_exclusions.py::test_excludes_worktrees_directory PASSES"
```

**Why this works:** The test exercises the exact code that was changed and proves it works.

---

## 🚨 IF YOU CANNOT WRITE A TEST THAT EXERCISES YOUR CODE CHANGE, YOU DO NOT UNDERSTAND THE BUG

**DO NOT:**
- Run random existing tests and claim success
- Skip writing tests because "it's a simple fix"
- Assume your change works without proving it
- Return success messages without verified smoke tests

**DO:**
- Write tests that exercise your changed code
- Verify tests fail before your fix (or write them to fail first)
- Run full suite to check for regressions
- Document what test proves your fix works

---

# AI Agent Instructions: DO NOT CREATE STUBS, DO NOT CREATE PLACEHOLDERS

***NEVER return to the user with a "success!" or "complete" or "done" message WITHOUT A VERIFIED AND DOCUMENTED SMOKE TEST PROVING FUNCTIONALITY***

Tests should be saved in `agentspec/tests/`

MANDATORY: USE `agentspec/TOOLS.md` for your commands

---

# This codebase uses **agentspec** — structured YAML and JS Doc blocks in docstrings

**You MUST read and respect agentspecs** or you will break production systems.

Agentspecs provide context, dependencies, guardrails, and historical information for every function and class.

---

## 📖 How To Use Agentspecs (MANDATORY WORKFLOW)

### Step 1: Find the function/class you need to edit

Use `agentspec extract` or read the source file.

### Step 2: Read the agentspec

Every function has:
- **`what`**: What it does (be thorough)
- **`deps`**: Dependencies (calls, imports, config, env vars)
- **`why`**: Why this approach (vs alternatives)
- **`guardrails`**: What NOT to change and why

### Step 3: Print the spec to stdout **(MANDATORY)**

**Why printing?** It forces the information into your active context. Skipping this step leads to mistakes.

Print at minimum:
- The `what` section (so you understand what it does)
- The `guardrails` section (so you don't break it)

### Step 4: Check Guardrails

Every guardrail exists because something broke in production. Before making changes:

1. Read ALL guardrails
2. Verify your change doesn't violate ANY of them
3. If you must violate a guardrail, ASK THE USER FIRST

### Step 5: Ensure your changes don't conflict with 'what', 'why', or 'deps'

REAL consequences when this is ignored:
- Agent removes "unused" imports → breaks dynamic loading
- Agent deletes "dead code" → actually used via config-driven dispatch
- Agent makes function async → reintroduces race condition from 3 commits ago
- Agent "optimizes" by removing checks → breaks edge case handling

---

## 📋 Agentspec Fields Reference

### Required Fields

- **`what`**: Detailed explanation of functionality (be verbose!)
- **`deps`**: All dependencies
  - `calls`: Functions/methods this calls
  - `imports`: Modules/packages imported
  - `config`: Config files read
  - `environment`: Env vars used
- **`why`**: Why this approach vs alternatives
- **`guardrails`**: What NOT to change and why (minimum 2-3)

### Optional Fields

- **`security`**: Security considerations
- **`monitoring`**: What metrics/alerts exist
- **`known_issues`**: Documented bugs or limitations
- **`changelog`**: Dated entries of changes made

---

## 🛠️ When you write OR EDIT code, ALWAYS update the agentspec

### For NEW functions:

```python
def my_new_function(param: str) -> bool:
    """
    Brief one-line description.

    ---agentspec
    what: |
      Detailed multi-line explanation.
      - What does it do?
      - What are inputs/outputs?
      - What edge cases does it handle?

      Be VERBOSE. Future agents (and humans) will thank you.

    deps:
      calls:
        - other_function
        - module.method
      imports:
        - pathlib.Path
        - typing.List

    why: |
      Why this specific implementation?
      What alternatives did you consider?
      Why did you reject them?

    guardrails:
      - DO NOT remove the X check; it prevents Y edge case
      - DO NOT make this async; it's called from synchronous context
      - ALWAYS validate inputs; downstream code assumes clean data

    changelog:
      - "2025-11-01: Initial implementation for feature X"
    ---/agentspec
    """
    # Implementation
```

### For EDITED functions:

1. **Read** the existing agentspec
2. **Print** the `what` and `guardrails` to stdout
3. **Verify** your change doesn't violate guardrails
4. **Update** these fields:
   - `what` if behavior changed
   - `deps` if calls/imports changed
   - `why` if approach changed
   - `guardrails` if new constraints added
   - **`changelog`** - ALWAYS add dated entry describing your change

---

## 🧪 Testing Agentspecs

```bash
# Lint all specs (check for required fields, valid YAML)
agentspec lint agentspec/ --strict

# Extract specs to markdown (for review)
agentspec extract agentspec/ --format markdown

# Extract with context (includes function signatures)
agentspec extract agentspec/ --format agent-context
```

Run `agentspec lint` before claiming your change is complete.

---

## 📊 Success Metrics

### Good agent behavior:
- ✅ Always reads agentspecs before editing
- ✅ Prints `what` and `guardrails` to stdout
- ✅ Verifies changes don't violate guardrails
- ✅ Updates agentspec fields (especially changelog)
- ✅ Writes tests that exercise changed code
- ✅ Verifies tests fail before fix, pass after fix
- ✅ Asks humans before violating guardrails

### Bad agent behavior:
- ❌ Edits code without reading agentspec
- ❌ Deletes "unused" code without checking `deps.called_by`
- ❌ "Fixes" things that `why` says are intentional
- ❌ Refactors without reading `why` sections
- ❌ Skips printing specs "to save tokens"
- ❌ Runs random tests and claims success
- ❌ Claims success without tests proving the fix

---

## 🚀 Final Checklist (MANDATORY before claiming success)

Before submitting any code changes:

- [ ] Read all relevant agentspecs
- [ ] Printed `what` and `guardrails` to stdout
- [ ] Checked no guardrails violated
- [ ] Updated `what` if behavior changed
- [ ] Added dated `changelog` entry
- [ ] Updated `deps` if calls/imports changed
- [ ] Added new `guardrails` if applicable
- [ ] **Wrote test that exercises the EXACT code you changed**
- [ ] **Verified test fails without your fix**
- [ ] **Verified test passes with your fix**
- [ ] Ran full test suite (`pytest -q`) - all pass
- [ ] Ran `agentspec lint agentspec/ --strict` - passes
- [ ] Can point to specific test that proves your fix works

---

## 🎯 Summary: The Three Rules

1. **READ THE SPEC** before touching code
2. **TEST THE CODE YOU CHANGED** (not random tests)
3. **UPDATE THE SPEC** to document your change

**Remember:** The goal isn't to slow you down — it's to prevent the "helpful" changes that cause 3am production incidents and wasted user time debugging "fixes" that don't actually work.

Read the specs. Print the specs. Respect the specs. Test what you change.
