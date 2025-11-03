# 🚀 Agentspec CLI Quick Reference

A practical guide to agentspec commands, including update-existing and diff summaries.

At a glance (new essentials)
- `--language {auto|py|js}` to select Python vs JS/TS
- `--strip` to pre‑clean stale agentspec blocks (Python + JS/TS)
- JSDoc replacement (not append) with syntax validation
- Two‑phase write (narrative + deterministic metadata) under the hood
- Export everything: `agentspec extract <path> --format markdown`

---

## 📚 Table of Contents

- [Highlights](#highlights)
- [Basic Commands](#basic-commands)
- [JavaScript/TypeScript Support](#javascripttypescript-support)
- [Single File Operations](#single-file-operations)
- [Update Existing Docstrings](#update-existing-docstrings)
- [Creative Workflows](#creative-workflows)
- [Model Selection](#model-selection)
- [Output Control Flags](#output-control-flags)
- [Troubleshooting](#troubleshooting)

---

## Highlights

### 🔍 High‑Accuracy Guidance (for important code)

```bash
# Thorough generation for critical paths (auth, payments, security)
agentspec generate src/auth.py

# Choose your best model explicitly when needed
agentspec generate src/payments/ --model <your_best_model>

# Combine with update-existing to refresh docs
agentspec generate src/security.py --update-existing

# Dry run to preview changes
agentspec generate src/core.py --dry-run
```

**Recommendations:**
- Avoid `--terse` for high‑stakes code; allow more room for context
- Use a stronger model when accuracy matters (pick based on your setup)
- Uses two-pass generation: Generate → Verify
- Employs ULTRATHINK prompts for deeper reasoning
- Lower temperature for consistency
- Defaults to higher-quality models

**Use Critical Mode For:**
- Authentication/authorization code
- Payment processing
- Security boundaries
- Data integrity checks
- Core business logic
- Any code where documentation errors could cause incidents

### 🔄 Update Existing - Regenerate When Code Changes

```bash
# Regenerate ALL docstrings (even existing ones)
agentspec generate src/ --update-existing

# Update single file after code changes
agentspec generate src/api.py --update-existing

# Preview pending changes
agentspec generate src/ --update-existing --dry-run

# Update with specific model
agentspec generate src/ --update-existing --model claude-haiku-4-5

# Combine with update-existing for maximum coverage on updates
agentspec generate src/core/ --update-existing
```

**When to Use --update-existing:**
- Code has changed but docstrings haven't
- Switching documentation formats
- Upgrading from old docstring style to agentspec
- Periodic documentation refresh
- After major refactoring

---

## Basic Commands

### Generate Docstrings

```bash
# Generate for entire codebase (auto-detects Python/JS/TS)
agentspec generate src/

# Preview without changes (ALWAYS START WITH THIS)
agentspec generate src/ --dry-run

# Force language (when auto-detection isn't enough)
agentspec generate src/ --language js     # JavaScript/TypeScript
agentspec generate src/ --language py     # Python

# Generate with context-forcing print statements
agentspec generate src/ --force-context

# Generate agentspec YAML blocks
agentspec generate src/ --agentspec-yaml

# Strip old agentspecs before generating fresh ones
agentspec generate src/ --strip --update-existing
```

### Lint & Validate

```bash
# Lint entire codebase (auto-detects language)
agentspec lint src/

# Strict mode (warnings become errors)
agentspec lint src/ --strict

# Force language for lint
agentspec lint src/ --language js --strict

# Custom minimum line requirement
agentspec lint src/ --min-lines 20
```

### Extract Documentation

```bash
# Extract to markdown (default, auto-detects language)
agentspec extract src/

# Extract to JSON
agentspec extract src/ --format json

# Extract with agent context
agentspec extract src/ --format agent-context

# Force language for extraction
agentspec extract src/ --language js --format json
```

---

## JavaScript/TypeScript Support

### Language Detection

```bash
# Auto-detect (default) - uses file extension
agentspec generate src/              # Processes .py, .js, .mjs, .jsx, .ts, .tsx

# Force JavaScript/TypeScript for mixed codebases
agentspec generate src/ --language js

# Force Python only
agentspec generate src/ --language py
```

### JavaScript/TypeScript Examples

```bash
# Generate JSDoc for React components
agentspec generate src/components/ --language js --agentspec-yaml

# Lint TypeScript files
agentspec lint src/ --language js --strict

# Extract from Node.js project
agentspec extract src/ --language js --format json

# Strip JSDoc from JavaScript
agentspec strip src/ --dry-run        # Preview first
agentspec strip src/                  # Remove JSDoc
```

### Supported Extensions

- **.js** - JavaScript
- **.mjs** - ECMAScript modules
- **.jsx** - React JSX
- **.ts** - TypeScript
- **.tsx** - TypeScript + JSX

---

## Single File Operations

**THE POWER OF SINGLE FILES** - All commands work on individual files!

### Generate for One File

```bash
# Basic generation
agentspec generate src/utils.py

# With all the flags
agentspec generate src/critical_auth.py \
  --update-existing \
  --force-context \
  --model <your_best_model>

# Quick preview
agentspec generate src/api.py --dry-run
```

### Lint One File

```bash
# Basic lint
agentspec lint src/database.py

# Strict with high standards
agentspec lint src/payments.py --strict --min-lines 25
```

### Extract from One File

```bash
# Extract to see current state
agentspec extract src/models.py

# Extract as JSON for tooling
agentspec extract src/config.py --format json
```

---

## High-Accuracy Tips

### When to Use Critical Mode

```bash
# Payment processing — prefer thorough output and a stronger model
agentspec generate src/payments/

# Authentication - accuracy is paramount
agentspec generate src/auth/ --model <your_best_model>

# Security boundaries
agentspec generate src/security/ --force-context

# Data validation that affects business logic
agentspec generate src/validators/
```

### Critical Mode Workflow

```bash
# Step 1: Preview thoroughly
agentspec generate src/critical_module.py --dry-run

# Step 2: Generate with verification
agentspec generate src/critical_module.py

# Step 3: Lint to ensure quality
agentspec lint src/critical_module.py --strict --min-lines 20

# Step 4: Extract for review
agentspec extract src/critical_module.py
```

### Performance Considerations

```bash
# For less critical code, fast defaults are fine:
agentspec generate src/utils/

# For important code, the extra time is worth it:
agentspec generate src/auth/

# Mix and match per folder or file:
agentspec generate src/auth/
agentspec generate src/ui/
```

---

## Update Existing Docstrings

### Common Update Scenarios

```bash
# After refactoring a module
agentspec generate src/refactored_module.py --update-existing

# When code behavior changed
agentspec generate src/api.py --update-existing

# Switching from old docstring format to agentspec
agentspec generate src/ --update-existing --agentspec-yaml

# Refreshing documentation periodically
agentspec generate src/ --update-existing --model claude-haiku-4-5
```

### Update Workflow

```bash
# Step 1: Check current state
agentspec lint src/

# Step 2: Preview updates
agentspec generate src/ --update-existing --dry-run

# Step 3: Apply updates
agentspec generate src/ --update-existing

# Step 4: Verify quality
agentspec lint src/ --strict
```

### Selective Updates

```bash
# Update only key files with high accuracy
agentspec generate src/core/ --update-existing

# Update UI files with standard mode
agentspec generate src/ui/ --update-existing

# Update tests with minimal docs
agentspec generate tests/ --update-existing --model claude-haiku-4-5
```

---

## Creative Workflows

### The "Paranoid" Workflow (Maximum Safety)

```bash
# For the most critical code in your system
# 1. Extract current state for backup
agentspec extract src/payments.py --format json > backup.json

# 2. Dry run
agentspec generate src/payments.py --update-existing --dry-run

# 3. Generate with verification
agentspec generate src/payments.py --update-existing

# 4. Lint with maximum strictness
agentspec lint src/payments.py --strict --min-lines 30

# 5. Extract and review
agentspec extract src/payments.py

# 6. If issues, restore from backup
```

### The "CI/CD Integration" Workflow

```bash
# In your CI pipeline
#!/bin/bash
set -e  # Exit on error

# Ensure all functions have docs
agentspec lint src/ --strict

# Generate missing docs
agentspec generate src/ --model claude-haiku-4-5

# Re-lint to verify
agentspec lint src/ --strict

# Extract for artifacts
agentspec extract src/ --format json
```

### The "Progressive Enhancement" Workflow

```bash
# Start with fast/cheap generation
agentspec generate src/ --model claude-haiku-4-5

# Identify critical files
CRITICAL_FILES="src/auth.py src/payments.py src/security.py"

# Regenerate critical files with high accuracy
for file in $CRITICAL_FILES; do
  agentspec generate "$file" --update-existing
done

# Verify everything passes
agentspec lint src/ --strict
```

### The "Git-Aware Update" Workflow

```bash
# Only update files that changed
git diff --name-only main | grep '\.py$' | while read file; do
  echo "Updating $file..."
  agentspec generate "$file" --update-existing
done

# Or for key files in the changeset
git diff --name-only main | grep -E '(auth|payment|security).*\.py$' | while read file; do
  echo "Critical update for $file..."
  agentspec generate "$file" --update-existing
done
```

---

## Model Selection

### For Important Code

```bash
# Best accuracy (but slower)
agentspec generate src/critical.py --model <your_best_model>

# Good balance
agentspec generate src/important.py --model <your_best_model>
```

### For Bulk Documentation

```bash
# Fast and cheap
agentspec generate src/ --model claude-haiku-4-5

# Local/free with local LLM (Ollama, vLLM, LM Studio, etc.)
agentspec generate src/ --model <your-model> --provider local --base-url http://localhost:11434/v1
```

### Model Comparison

```bash
# Test different models on same file
agentspec generate src/test.py --model claude-haiku-4-5 --dry-run > haiku.txt
agentspec generate src/test.py --model claude-haiku-4-5 --dry-run > haiku2.txt
agentspec generate src/test.py --model gpt-5 --provider openai --dry-run > gpt5.txt

# Compare outputs
diff haiku.txt gpt5.txt
```

---

## Output Control Flags

### Terse Mode (--terse)

For LLM consumption - shorter, more concise output:

```bash
# Terse output (better for LLM context windows)
agentspec generate src/ --terse

# Terse example
agentspec generate src/auth/ --terse

# Regular verbose output (better for human learning)
agentspec generate src/
```

**What --terse does:**
- Uses temperature=0.0 (deterministic)
- Limits max_tokens=1500 (vs 2000-3000 default)
- Uses concise prompts requesting shorter sections
- Still includes ALL sections (WHAT, WHY, GUARDRAILS, DEPENDENCIES, CHANGELOG)
- Just more concise per section

### Diff Summary (--diff-summary)

Add LLM-generated summaries of git diffs (separate API call):

```bash
# Add diff summaries to understand what changed
agentspec generate src/ --diff-summary

# Works with terse
agentspec generate src/auth.py --diff-summary --terse
```

**What happens:**
1. CHANGELOG section shows commit messages only (no diffs)
2. Separate API call analyzes the actual git diffs
3. Section added: `CHANGELOG DIFF SUMMARY (LLM-generated):`
4. One-line summaries of what changed in each commit
5. Still limited to last 5 commits

**Why separate API call:**
- Doesn't conflict with --terse token limits
- Can use full 1000 tokens just for diff analysis
- Diffs can be huge - separate call prevents truncation

---

## Troubleshooting

### "All functions already have verbose docstrings"

```bash
# Use --update-existing to regenerate
agentspec generate src/ --update-existing
```

### Performance Tips

```bash
# Process in smaller batches
agentspec generate src/auth/
agentspec generate src/models/
agentspec generate src/api/

# For less critical files
agentspec generate src/utils/
```

### Syntax Errors

```bash
# Check Python syntax first
python -m py_compile src/broken.py

# Fix syntax, then generate
agentspec generate src/broken.py
```

### Rate Limits

```bash
# Use local models to avoid rate limits
export OLLAMA_BASE_URL=http://localhost:11434/v1
agentspec generate src/ --model <your-model> --provider local --base-url http://localhost:11434/v1

# Or add delays between files
for file in src/*.py; do
  agentspec generate "$file"
  sleep 2
done
```

---

## Environment Variables

```bash
# Anthropic (Claude)
export ANTHROPIC_API_KEY="sk-ant-..."

# OpenAI
export OPENAI_API_KEY="sk-..."

# Local Ollama (no key needed)
export OLLAMA_BASE_URL="http://localhost:11434/v1"

# Or use .env file (auto-loaded)
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

---

## Quick Command Reference

| Task | Command |
|------|---------|
| **Generate** | `agentspec generate src/` |
| **Generate (terse)** | `agentspec generate src/ --terse` |
| **Update existing** | `agentspec generate src/ --update-existing` |
| **Strip then generate** | `agentspec generate src/ --strip --update-existing` |
| **With diff summaries** | `agentspec generate src/ --diff-summary` |
| **Preview changes** | `agentspec generate src/ --dry-run` |
| **Single file** | `agentspec generate src/file.py` |
| **Force JS/TS** | `agentspec generate src/ --language js` |
| **Force Python** | `agentspec generate src/ --language py` |
| **YAML format** | `agentspec generate src/ --agentspec-yaml` |
| **Force context prints** | `agentspec generate src/ --force-context` |
| **Lint strict** | `agentspec lint src/ --strict` |
| **Lint JS/TS** | `agentspec lint src/ --language js` |
| **Extract markdown** | `agentspec extract src/` |
| **Extract JSON** | `agentspec extract src/ --format json` |
| **Extract JS/TS** | `agentspec extract src/ --language js` |
| **Use Local LLM** | `agentspec generate src/ --model <your-model> --provider local --base-url http://localhost:11434/v1` |
| **Strip all** | `agentspec strip src/` |
| **Strip preview** | `agentspec strip src/ --dry-run` |

---

## Pro Tips

1. **Always start with --dry-run** to preview changes
2. **Avoid --terse for auth, payments, security** code
3. **Use --update-existing after refactoring** to keep docs in sync
4. **Combine flags** for power: `--update-existing --force-context`
5. **Process single files** for surgical precision
6. **Pick models based on your environment** (no single best model)
7. **Extract after generation** to review quality
8. **Lint after updates** to ensure standards

---

## The Most Powerful Commands You'll Use

```bash
# The "Fix Everything" Command
agentspec generate src/ --update-existing --model claude-haiku-4-5

# The "Document Critical Code Thoroughly" Command
agentspec generate src/auth/ --force-context --model <your_best_model>

# The "Quick Single File Update" Command
agentspec generate src/changed_file.py --update-existing

# The "Paranoid Preview" Command
agentspec generate src/payments.py --update-existing --dry-run

# The "Free Local Generation" Command
agentspec generate src/ --model <your-model> --provider local --base-url http://localhost:11434/v1
```

---

Remember: **--dry-run is your friend!** Always preview before applying changes.
