# Bug Fix Summary: JavaScript Vendor/Minified File Exclusion

**Date:** 2025-11-01
**Issue:** `agentspec generate` was processing hundreds of minified vendor files in `.worktrees/gh-pages/assets/` directories

---

## Root Cause Analysis

Three separate but related bugs:

### Bug 1: `collect_source_files` didn't post-filter JS files through .gitignore
**File:** `agentspec/utils.py:436`
**Problem:** JavaScript files from adapters weren't filtered through `.gitignore` and `.agentspecignore` like Python files were.
**Fix:** Added post-filtering for all non-Python files discovered by adapters.

### Bug 2: `inject_deterministic_metadata` had regex backslash interpretation issue
**File:** `agentspec/generate.py:269`
**Problem:** Using string replacements in `re.sub()` caused Python to interpret backslashes in metadata (like `\u` from JS code) as escape sequences, throwing "bad escape \u" errors.
**Fix:** Changed all metadata injection `re.sub()` calls to use callable replacements (lambda functions).

### Bug 3: `JavaScriptAdapter.discover_files` missing critical exclusions ⭐ **MAIN ISSUE**
**File:** `agentspec/langs/javascript_adapter.py:127`
**Problem:** Hardcoded exclusion list was missing:
- `.worktrees/` (git worktrees)
- `gh-pages/` (GitHub Pages builds)
- `assets/` (vendor/static files)
- `*.min.js` (minified files)

**This was the primary cause of the vendor file spam.**

---

## Fixes Applied

### 1. Updated `collect_source_files` (utils.py:436)
```python
# Added post-filtering for non-Python files
if non_python_files:
    repo_root = _find_git_root(target)
    if repo_root:
        ignored = _git_check_ignore(repo_root, non_python_files)
        filtered = [p for p in non_python_files if p.resolve() not in ignored]
        filtered = [p for p in filtered if not _check_agentspecignore(p, repo_root)]
        files.extend(filtered)
```

### 2. Updated `inject_deterministic_metadata` (generate.py:269)
```python
# Changed from string replacement to callable
output = re.sub(
    r'(\n\s*why[:\|])',
    lambda m: deps_yaml + m.group(1),  # ✅ Callable prevents backslash interpretation
    llm_output,
    count=1
)
```

### 3. Updated `JavaScriptAdapter.discover_files` (javascript_adapter.py:127)
```python
exclude_dirs = {
    'node_modules', '.git', '.venv', '__pycache__',
    'dist', 'build', '.next', '.nuxt', 'coverage',
    '.rollup.cache', '.turbo',
    # Added:
    '.worktrees', 'gh-pages', 'assets', 'vendor',
    'public', 'static', '.cache', '.webpack'
}

# Added explicit minified file filtering
if p.name.endswith('.min.js') or p.name.endswith('.min.mjs'):
    continue
```

---

## Tests Created

**File:** `tests/test_javascript_exclusions.py`

5 new tests that prove the fixes work:

1. `test_excludes_minified_files` - Verifies `*.min.js` files are excluded
2. `test_excludes_worktrees_directory` - Verifies `.worktrees/` is excluded
3. `test_excludes_gh_pages_directory` - Verifies `gh-pages/` is excluded
4. `test_excludes_assets_directory` - Verifies `assets/` is excluded
5. `test_excludes_node_modules` - Verifies existing exclusions still work

**All 5 tests PASS** ✅

---

## Test Results

```bash
$ source .venv/bin/activate && pytest -q

============================== test session starts ===============================
tests/test_basic.py ..                                                   [  6%]
tests/test_collect_javascript.py .                                       [ 10%]
tests/test_extract_javascript_agentspec.py .                             [ 13%]
tests/test_generate_javascript.py ..                                     [ 20%]
tests/test_javascript_adapter.py ..................                      [ 80%]
tests/test_javascript_exclusions.py .....                                [ 96%]
tests/test_lint_javascript.py .                                          [100%]

============================== 30 passed in 0.47s ================================
```

**30/30 tests passing** (25 existing + 5 new)

---

## Verification

To verify the fix works on your faxbot codebase:

```bash
agentspec generate faxbot_folder/faxbot --provider openai \
  --base-url http://localhost:11434/v1 --model qwen3-coder:7b-instruct \
  --update-existing --strip --agentspec-yaml
```

**You should see:**
- ❌ NO `.worktrees/` files processed
- ❌ NO `gh-pages/` files processed
- ❌ NO `assets/` files processed
- ❌ NO `*.min.js` files processed
- ✅ ONLY your actual source files

The spam of "Processing .../lunr.nl.min.js" is gone.

---

## Documentation Updated

**File:** `CLAUDE.md`

Completely rewritten to integrate:
1. **Test requirements:** Test the EXACT code you changed, not random tests
2. **Agentspec workflow:** Read → Print → Respect → Update
3. **No stubs/placeholders:** Always prove functionality with tests
4. **Clear examples:** Shows WRONG vs RIGHT testing workflows

Key addition:
```markdown
## 🚨 IF YOU CANNOT WRITE A TEST THAT EXERCISES YOUR CODE CHANGE,
      YOU DO NOT UNDERSTAND THE BUG

**DO NOT:**
- Run random existing tests and claim success
```

---

## Lessons Learned

### What went wrong initially:

1. Fixed `collect_source_files` first
2. Ran 25 existing tests (none tested file discovery)
3. Claimed success because tests passed
4. User reported **STILL BROKEN**
5. Found the real bug in `JavaScriptAdapter.discover_files`
6. Wrote 5 new tests that actually test exclusions
7. **NOW** it's actually fixed

### Why it failed:

Running tests that don't exercise the code you changed proves **nothing**.

### What should have happened:

1. Read agentspecs for `discover_files`
2. Write test: `test_excludes_worktrees_directory()`
3. Run test → FAILS ❌
4. Fix `discover_files` to exclude `.worktrees/`
5. Run test → PASSES ✅
6. Run full suite → all pass
7. Point to specific test as proof

---

## Files Changed

- `agentspec/utils.py` (collect_source_files)
- `agentspec/generate.py` (inject_deterministic_metadata)
- `agentspec/langs/javascript_adapter.py` (discover_files)
- `tests/test_javascript_exclusions.py` (NEW - 5 tests)
- `CLAUDE.md` (comprehensive rewrite)

---

## Agentspec Updates

All modified functions had their agentspecs updated with:
- Updated `what` sections describing new behavior
- Added changelog entries dated 2025-11-01
- New guardrails where applicable

Example:
```yaml
changelog:
  - "2025-11-01: Fix .gitignore/.agentspecignore filtering for non-Python languages"
  - "2025-11-01: Add .worktrees, gh-pages, assets, *.min.js exclusions"
```
