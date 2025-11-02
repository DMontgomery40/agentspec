# ast-grep (sg) Implementation Plan for agentspec — ACCURATE VERSION

## Executive Summary

The `sg/rules/` directory was created from a Claude conversation (serena_task.md) but contains **critical misunderstandings** about the codebase. This plan provides a **fact-checked** analysis using Serena + Context7 and defines the correct implementation path.

---

## Source Analysis Complete

**Tools Used:**
- ✅ Serena MCP: Analyzed actual codebase patterns
- ✅ Context7 MCP: Verified OpenAI API documentation
- ✅ Web Search: Confirmed max_tokens vs max_completion_tokens usage

---

## Current State (Verified via Serena)

### What EXISTS and WORKS
1. **ast-grep installed**: `/opt/homebrew/bin/sg`
2. **sgconfig.yaml**: Properly configured for `agentspec/**/*.py`
3. **sg/rules/**: 4 YAML files (safety, hygiene, modern-openai, agentspec)
4. **agentspec/llm.py architecture**:
   - Line 250: **ALREADY USES** `client.responses.create()` as PRIMARY
   - Line 287: **ALREADY USES** `client.chat.completions.create()` as FALLBACK for Ollama
   - Line 254: Uses `max_output_tokens` for Responses API
   - Line 291: Uses `max_tokens` for Chat Completions API
   - Comments at lines 242-244 document this is INTENTIONAL

---

## Rule-by-Rule Analysis (Serena + Context7 Verified)

### ❌ modern-openai.yml — BOTH RULES ARE WRONG

#### Rule 1: `openai-chat-to-responses`
```yaml
- id: openai-chat-to-responses
  message: "Use client.responses.create(...) instead of client.chat.completions.create(...)."
```

**Problem**: 
- The codebase ALREADY uses Responses API as primary (line 250)
- The Chat Completions call (line 287) is a DELIBERATE fallback for Ollama compatibility
- This rule would flag the fallback as bad, which is WRONG

**Evidence** (agentspec/llm.py:242-244):
```python
# Prefer Responses API. If provider doesn't support it, fall back to
# Chat Completions for compatibility (e.g., Ollama).
try:
```

**Verdict**: ❌ **DELETE THIS RULE** — it misunderstands the intentional architecture

#### Rule 2: `openai-max-tokens-rename`
```yaml
- id: openai-max-tokens-rename
  message: "Use 'max_completion_tokens=' instead of 'max_tokens='."
```

**Problem**:
- Responses API uses `max_output_tokens` (NOT `max_completion_tokens`)
- Chat Completions API uses `max_tokens` (which is STILL VALID per OpenAI docs)
- `max_completion_tokens` is specific to o1 reasoning models
- This rule would create INCORRECT code

**Evidence**:
- Context7 docs: Responses API uses `max_output_tokens`
- Web search: `max_completion_tokens` is for o1 models only
- Code: line 254 uses `max_output_tokens`, line 291 uses `max_tokens`

**Verdict**: ❌ **DELETE THIS RULE** — factually incorrect parameter names

---

### ✅ safety.yml — KEEP AS-IS (Preventative, No Violations)

**Serena Analysis Results:**
```
shell=True patterns: 0 matches
os.system() patterns: 0 matches
eval() patterns: 0 matches
exec() patterns: 0 matches
```

**All 4 rules**:
- `dangerous-subprocess-shell-true` ✅
- `os-system-shell` ✅
- `ban-eval` ✅
- `ban-exec` ✅

**Verdict**: ✅ **KEEP** — good preventative measures, no false positives

---

### ⚠️ hygiene.yml — REQUIRES MAJOR MODIFICATION

#### Rule 1: `no-print-in-library`
```yaml
- id: no-print-in-library
  message: "Use logging instead of print(...)."
  severity: warning
```

**Problem**:
- agentspec is a **CLI TOOL**, not a library
- Found 100+ legitimate print() statements in cli.py, generate.py, extract.py, lint.py, strip.py
- These are user-facing output, NOT library code
- Rule would create massive false positives

**Serena Evidence**:
- cli.py: 18 print() statements (all legitimate CLI output)
- generate.py: 53 print() statements (progress/status output)
- extract.py: 14 print() statements (format output)
- lint.py: 9 print() statements (error reporting)
- strip.py: 11 print() statements (status messages)
- collect.py: 10 print() statements (metadata display)

**Options**:
1. **DELETE the rule entirely** (recommended for CLI tool)
2. **Modify to only check agentspec/utils.py and agentspec/langs/*** (not CLI modules)
3. **Downgrade to info and add comment explaining it's advisory**

**Verdict**: ⚠️ **MODIFY OR DELETE** — current form inappropriate for CLI tool

#### Rule 2: `argparse-require-help`
```yaml
- id: argparse-require-help
  message: "Every argparse flag should include help= for CLI discoverability."
```

**Serena Analysis**: Spot-checked 20 add_argument() calls in cli.py, all have `help=`

**Verdict**: ✅ **KEEP** — no false positives, good practice

---

### ⚠️ agentspec.yml — MIXED QUALITY

#### Rule 1: `require-module-logger`
```yaml
- id: require-module-logger
  message: "Prefer a module-level logger: logger = logging.getLogger(__name__)."
  severity: info
```

**Verdict**: ✅ **KEEP** — good practice, info severity is appropriate

#### Rule 2: `cli-has-main`
```yaml
- id: cli-has-main
  message: "Prefer an explicit CLI entrypoint guarded by if __name__ == '__main__': main()."
  severity: info
  rule:
    pattern: if __name__ == "__main__": $MAIN()
```

**Problem**: This rule FINDS the pattern, it doesn't ENFORCE it
- The pattern match means "flag when this pattern IS present"
- But the message suggests it should be present
- This is backwards logic

**Verdict**: ⚠️ **FIX OR DELETE** — logic is inverted

#### Rule 3: `discourage-shell-in-fstring`
```yaml
- id: discourage-shell-in-fstring
  message: "Avoid composing shell commands inside f-strings; pass argv as list to subprocess."
  severity: warning
```

**Verdict**: ✅ **KEEP** — good preventative measure

#### Rule 4: `no-leftover-todos`
```yaml
- id: no-leftover-todos
  message: "Resolve TODO before merge (or track in an issue)."
  severity: info
```

**Problem**: TODOs are often intentional placeholders, this is too aggressive

**Verdict**: ⚠️ **DELETE OR DOWNGRADE** — too noisy for minimal value

---

## What's Missing from Original Proposal (From serena_task.md)

### 1. Helper Scripts (Lines 330-375)

**Proposed**:
- `scripts/scan_repo.sh` — Multi-tool scanner (rg + sg)
- `scripts/browse.sh` — Interactive code browser (requires fd, fzf, bat)
- `scripts/todos.sh` — Find TODO/FIXME/NOTE comments

**Assessment**:
- ✅ scan_repo.sh: Useful once rules are fixed
- ⚠️ browse.sh: Requires external tools (fd, fzf, bat) not in project deps
- ✅ todos.sh: Simple and useful

**Verdict**: Implement scan_repo.sh and todos.sh, browse.sh is optional

### 2. Makefile Targets (Lines 378-384)

**Proposed**:
```makefile
.PHONY: scan browse todos tree
scan:   ; scripts/scan_repo.sh
browse: ; scripts/browse.sh
todos:  ; scripts/todos.sh
tree:   ; eza -T -L 2 --git
```

**Assessment**: Useful convenience wrappers

**Verdict**: ✅ Implement (but skip `browse` and `tree` if tools not installed)

### 3. Pre-commit Hook (Lines 227-247)

**Proposed**:
```yaml
- id: ast-grep-scan
  entry: sg scan -c sgconfig.yaml
```

**Assessment**: Would fail immediately with current broken rules

**Verdict**: ✅ Implement AFTER fixing rules

### 4. GitHub Actions CI (Lines 249-270)

**Proposed**: Run ast-grep on PRs

**Assessment**: Good idea, but blocked by broken rules

**Verdict**: ✅ Implement AFTER fixing rules

---

## CORRECTED Implementation Plan

### Phase 1: FIX BROKEN RULES (CRITICAL — Blocks Everything)

#### 1.1 Delete modern-openai.yml
```bash
rm sg/rules/modern-openai.yml
```

**Reason**: Both rules are factually incorrect and would break the code

#### 1.2 Fix hygiene.yml

**Option A (Recommended)**: Delete no-print-in-library rule entirely
```yaml
---
# argparse: require help=... for every add_argument call
- id: argparse-require-help
  message: "Every argparse flag should include help= for CLI discoverability."
  severity: warning
  language: python
  rule:
    pattern: $PARSER.add_argument($$ARGS)
  constraints:
    not:
      regex: "help\\s*="
```

**Option B**: Modify to only check non-CLI modules
```yaml
- id: no-print-in-library
  message: "Use logging instead of print(...) in utility modules."
  severity: warning
  language: python
  rule:
    pattern: print($$ARGS)
  # Would need path constraints (not supported in basic ast-grep)
```

**Recommendation**: Use Option A (delete), print() is legitimate for CLI

#### 1.3 Fix agentspec.yml

**Remove broken/low-value rules**:
```yaml
---
# Use logging best practice
- id: require-module-logger
  message: "Prefer a module-level logger: logger = logging.getLogger(__name__)."
  severity: info
  language: python
  rule:
    pattern: logging.getLogger(__name__)

# Discourage shell pipelines in f-strings
- id: discourage-shell-in-fstring
  message: "Avoid composing shell commands inside f-strings; pass argv as list to subprocess."
  severity: warning
  language: python
  rule:
    pattern: f"$CMD"
  constraints:
    regex: "\\b(;|\\|\\||\\|)\\b"
```

**Removed**:
- `cli-has-main` (backwards logic)
- `no-leftover-todos` (too noisy)

#### 1.4 Keep safety.yml unchanged
No modifications needed, all rules are preventative and valid.

---

### Phase 2: VERIFY RULES WORK

```bash
# Test that scan runs without errors
sg scan -c sgconfig.yaml

# Test that no false positives on current codebase
# Should see 0 errors (safety rules have no violations)
# May see warnings (argparse, logging patterns)

# Verify JSON output works
sg scan -c sgconfig.yaml --json | jq '.'
```

**Success Criteria**:
- No errors on current codebase
- Warnings are actionable (not false positives)
- JSON output is valid

---

### Phase 3: ADD PRACTICAL TOOLING

#### 3.1 Create scripts/scan_repo.sh

**Note**: Update to reflect FIXED rules (remove modern-openai checks)

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "== Security Checks =="
rg -n --hidden "subprocess\\.run\\(.*shell\\s*=\\s*True" agentspec || true
rg -n --hidden "os\\.system\\(" agentspec || true
rg -n --hidden "\\beval\\(" agentspec || true
rg -n --hidden "\\bexec\\(" agentspec || true

echo
echo "== Argparse flags missing help= =="
rg -n --hidden "add_argument\\(" agentspec | rg -n -v "help\\s*=" || true

echo
echo "== ast-grep summary =="
if command -v sg >/dev/null 2>&1 && [ -f "sgconfig.yaml" ]; then
  sg scan -c sgconfig.yaml --json \
  | jq -r 'group_by(.id) | map({id: .[0].id, count: length})
           | sort_by(-.count)[] | "\\(.count)\\t\\(.id)"'
else
  echo "ast-grep not configured or sgconfig.yaml missing."
fi
```

**DO NOT** include the broken OpenAI API checks from original proposal

#### 3.2 Create scripts/todos.sh

```bash
#!/usr/bin/env bash
set -euo pipefail
rg -n --hidden -e "\\bTODO\\b|\\bFIXME\\b|\\bNOTE\\b" agentspec || true
```

#### 3.3 Create Makefile

```makefile
.PHONY: scan todos sg-scan

scan:
\t@scripts/scan_repo.sh

todos:
\t@scripts/todos.sh

sg-scan:
\t@sg scan -c sgconfig.yaml

help:
\t@echo "Available targets:"
\t@echo "  scan     - Run full codebase scan (rg + sg)"
\t@echo "  todos    - Find TODO/FIXME/NOTE comments"
\t@echo "  sg-scan  - Run ast-grep only"
```

**Skip** `browse` and `tree` targets (require external tools)

---

### Phase 4: INTEGRATE WITH WORKFLOWS

#### 4.1 Pre-commit Hook

Create/update `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: ast-grep-scan
        name: ast-grep (code quality)
        entry: sg scan -c sgconfig.yaml
        language: system
        pass_filenames: false
        types: [python]
```

Install:
```bash
pip install pre-commit
pre-commit install
```

#### 4.2 GitHub Actions (if .github exists)

Create `.github/workflows/ast-grep.yml`:

```yaml
name: ast-grep

on:
  pull_request:
    branches: [ main ]
  push:
    branches: [ main ]

jobs:
  ast-grep:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install ast-grep
        run: |
          curl -sSL https://raw.githubusercontent.com/ast-grep/ast-grep/main/install.sh | bash
          echo "$HOME/.local/bin" >> $GITHUB_PATH
      
      - name: Run ast-grep scan
        run: sg scan -c sgconfig.yaml
```

---

### Phase 5: DOCUMENTATION

#### 5.1 Create sg/README.md

```markdown
# ast-grep Rules for agentspec

## Overview

This directory contains ast-grep rules for code quality and security checks.

## Rules

### safety.yml (Preventative Security)
- Blocks `subprocess.run(shell=True)`
- Blocks `os.system()`
- Blocks `eval()` and `exec()`

All rules are severity: error

### hygiene.yml (Code Quality)
- Requires `help=` parameter for all argparse flags

### agentspec.yml (Best Practices)
- Encourages module-level loggers
- Prevents shell command composition in f-strings

## Running Locally

\`\`\`bash
# Full scan
make scan

# ast-grep only
make sg-scan

# Find TODOs
make todos
\`\`\`

## Why NOT modern-openai.yml?

The original proposal included rules to migrate to Responses API, but:
1. The codebase ALREADY uses Responses API as primary (llm.py:250)
2. Chat Completions fallback is INTENTIONAL for Ollama compatibility
3. Parameter names were incorrect (`max_completion_tokens` is o1-specific)

Those rules were deleted to prevent breaking the intentional architecture.
```

#### 5.2 Update TOOLS.md

Add section:

```markdown
## ast-grep (Code Quality Scanner)

Run code quality and security checks:

\`\`\`bash
# Full scan (includes ripgrep + ast-grep)
make scan

# ast-grep only
sg scan -c sgconfig.yaml

# Auto-fix safe issues (none currently)
sg fix -c sgconfig.yaml

# JSON output for CI
sg scan -c sgconfig.yaml --json
\`\`\`

See `sg/README.md` for rule details.
```

#### 5.3 Update CLAUDE.md

Add to checklist:

```markdown
## Before Committing

- [ ] Run `make scan` to check code quality
- [ ] Verify no new safety violations (shell=True, eval, exec)
- [ ] Ensure argparse flags have `help=` parameters
```

---

## What NOT to Do (Lessons from Original Proposal)

### ❌ DO NOT add rules without verifying against actual code
- Original proposal assumed Chat Completions was "old"
- Reality: Code already uses both APIs intentionally
- Always use Serena to analyze actual usage first

### ❌ DO NOT ban print() in CLI tools
- Original proposal treated agentspec as a library
- Reality: It's a CLI tool that NEEDS print() for user output
- Context matters more than blanket rules

### ❌ DO NOT assume API migrations without checking docs
- Original proposal confused `max_tokens` / `max_completion_tokens` / `max_output_tokens`
- Reality: Different APIs use different parameter names
- Always verify with Context7 before creating migration rules

### ❌ DO NOT create rules that flag intentional patterns
- Original proposal would flag the Ollama fallback
- Reality: Fallback is documented and necessary
- Read code comments before writing rules

---

## Testing Strategy

### Before Implementation
```bash
# Backup current rules
cp -r sg/rules sg/rules.backup

# Test current state (will have violations due to broken rules)
sg scan -c sgconfig.yaml
```

### After Phase 1 (Fix Rules)
```bash
# Should have 0 errors
sg scan -c sgconfig.yaml

# Verify JSON output
sg scan -c sgconfig.yaml --json | jq '.[] | {id, message, file}'
```

### After Phase 3 (Scripts)
```bash
# Test scan script
./scripts/scan_repo.sh

# Test todos script
./scripts/todos.sh

# Test make targets
make scan
make todos
make sg-scan
```

### After Phase 4 (Integrations)
```bash
# Test pre-commit
git add .
git commit -m "test: verify ast-grep pre-commit hook"

# Should run sg scan before commit
```

---

## Success Criteria

1. ✅ `sg scan` runs without errors on current codebase
2. ✅ No false positives on legitimate patterns
3. ✅ Security rules catch actual dangerous patterns (test with examples)
4. ✅ Helper scripts provide useful output
5. ✅ Pre-commit hook catches violations before commit
6. ✅ CI enforces rules on PRs (if .github exists)
7. ✅ Documentation explains what each rule does and why
8. ✅ No violation of CLAUDE.md (no stubs, all working code)

---

## Summary of Changes from Original Proposal

| Item | Original Proposal | Corrected Plan | Reason |
|------|------------------|----------------|---------|
| modern-openai.yml | Keep both rules | **DELETE FILE** | Both rules are factually wrong |
| hygiene.yml print() rule | Ban all print() | **DELETE RULE** | Inappropriate for CLI tool |
| agentspec.yml cli-has-main | Keep | **DELETE** | Logic is backwards |
| agentspec.yml no-leftover-todos | Keep | **DELETE** | Too noisy |
| scan_repo.sh | Include OpenAI checks | **REMOVE THOSE** | Based on wrong assumptions |
| browse.sh | Include | **OPTIONAL** | Requires external deps |
| Makefile tree target | Include | **SKIP** | Requires eza (not installed) |

---

## Estimated Effort

- **Phase 1 (Fix Rules)**: 30 minutes — edit 3 YAML files
- **Phase 2 (Verify)**: 15 minutes — run tests, check output
- **Phase 3 (Scripts)**: 45 minutes — write and test 3 files
- **Phase 4 (Integration)**: 30 minutes — pre-commit + CI
- **Phase 5 (Docs)**: 45 minutes — README, TOOLS.md, CLAUDE.md updates

**Total**: 2.5-3 hours (can be done incrementally)

---

## Next Steps for Implementation

1. Review this plan with user
2. Get confirmation on hygiene.yml approach (delete vs. modify)
3. Execute Phase 1 (fix rules)
4. Test and verify
5. Execute remaining phases
6. Document results

**HOLD HERE** for fresh context window before implementation.
