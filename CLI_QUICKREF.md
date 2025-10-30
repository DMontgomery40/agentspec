# 🚀 Agentspec CLI Quick Reference

A practical guide to agentspec commands, including powerful new features like critical mode and update-existing.

---

## 📚 Table of Contents

- [Essential New Features](#essential-new-features)
- [Basic Commands](#basic-commands)
- [Single File Operations](#single-file-operations)
- [Critical Mode (Ultra-Accurate)](#critical-mode-ultra-accurate)
- [Update Existing Docstrings](#update-existing-docstrings)
- [Creative Workflows](#creative-workflows)
- [Model Selection](#model-selection)
- [Troubleshooting](#troubleshooting)

---

## Essential New Features

### 🔬 Critical Mode - For Your Most Important Code

```bash
# Ultra-accurate generation with verification for critical code
agentspec generate src/auth.py --critical

# Critical mode with specific model (defaults to high-quality)
agentspec generate src/payments/ --critical --model claude-opus-4-1-20250805

# Combine with update-existing to regenerate critical docs
agentspec generate src/security.py --critical --update-existing

# Dry run to preview critical mode
agentspec generate src/core.py --critical --dry-run
```

**What Critical Mode Does:**
- Processes ONE function at a time (no context pollution)
- Collects metadata for each function AND its dependencies
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

# Preview what would be updated
agentspec generate src/ --update-existing --dry-run

# Update with specific model
agentspec generate src/ --update-existing --model claude-haiku-4-5

# Combine with critical for maximum accuracy on updates
agentspec generate src/core/ --update-existing --critical
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
# Generate for entire codebase
agentspec generate src/

# Preview without changes (ALWAYS START WITH THIS)
agentspec generate src/ --dry-run

# Generate with context-forcing print statements
agentspec generate src/ --force-context

# Generate agentspec YAML blocks
agentspec generate src/ --agentspec-yaml
```

### Lint & Validate

```bash
# Lint entire codebase
agentspec lint src/

# Strict mode (warnings become errors)
agentspec lint src/ --strict

# Custom minimum line requirement
agentspec lint src/ --min-lines 20
```

### Extract Documentation

```bash
# Extract to markdown (default)
agentspec extract src/

# Extract to JSON
agentspec extract src/ --format json

# Extract with agent context
agentspec extract src/ --format agent-context
```

---

## Single File Operations

**THE POWER OF SINGLE FILES** - All commands work on individual files!

### Generate for One File

```bash
# Basic generation
agentspec generate src/utils.py

# With all the flags
agentspec generate src/critical_auth.py \
  --critical \
  --update-existing \
  --force-context \
  --model claude-sonnet-4-5-20250929

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

## Critical Mode (Ultra-Accurate)

### When to Use Critical Mode

```bash
# Payment processing - ALWAYS use critical
agentspec generate src/payments/ --critical

# Authentication - accuracy is paramount
agentspec generate src/auth/ --critical --model claude-sonnet-4-5-20250929

# Security boundaries
agentspec generate src/security/ --critical --force-context

# Data validation that affects business logic
agentspec generate src/validators/ --critical
```

### Critical Mode Workflow

```bash
# Step 1: Preview in critical mode
agentspec generate src/critical_module.py --critical --dry-run

# Step 2: Generate with verification
agentspec generate src/critical_module.py --critical

# Step 3: Lint to ensure quality
agentspec lint src/critical_module.py --strict --min-lines 20

# Step 4: Extract for review
agentspec extract src/critical_module.py
```

### Performance Considerations

```bash
# Critical mode is SLOWER but MORE ACCURATE
# For non-critical code, use standard mode:
agentspec generate src/utils/ --model claude-haiku-4-5

# For critical code, the time is worth it:
agentspec generate src/auth/ --critical

# Mix and match - critical for some, standard for others:
agentspec generate src/auth/ --critical
agentspec generate src/ui/  # standard mode
```

---

## Update Existing Docstrings

### Common Update Scenarios

```bash
# After refactoring a module
agentspec generate src/refactored_module.py --update-existing

# When code behavior changed
agentspec generate src/api.py --update-existing --critical

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
# Update only critical files with high accuracy
agentspec generate src/core/ --update-existing --critical

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

# 2. Dry run with critical mode
agentspec generate src/payments.py --critical --update-existing --dry-run

# 3. Generate with verification
agentspec generate src/payments.py --critical --update-existing

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
  agentspec generate "$file" --critical --update-existing
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

# Or for critical files in the changeset
git diff --name-only main | grep -E '(auth|payment|security).*\.py$' | while read file; do
  echo "Critical update for $file..."
  agentspec generate "$file" --critical --update-existing
done
```

---

## Model Selection

### For Critical Code

```bash
# Best accuracy (but slower)
agentspec generate src/critical.py --critical --model claude-sonnet-4-5-20250929

# Good balance
agentspec generate src/important.py --critical --model claude-haiku-4-5
```

### For Bulk Documentation

```bash
# Fast and cheap
agentspec generate src/ --model claude-haiku-4-5

# Local/free with Ollama
agentspec generate src/ --model llama3.2 --provider openai --base-url http://localhost:11434/v1
```

### Model Comparison

```bash
# Test different models on same file
agentspec generate src/test.py --model claude-haiku-4-5 --dry-run > haiku.txt
agentspec generate src/test.py --model claude-sonnet-4-5-20250929 --dry-run > sonnet.txt
agentspec generate src/test.py --model gpt-4o-mini --provider openai --dry-run > gpt4.txt

# Compare outputs
diff haiku.txt sonnet.txt
```

---

## Output Control Flags

### Terse Mode (--terse)

For LLM consumption - shorter, more concise output:

```bash
# Terse output (better for LLM context windows)
agentspec generate src/ --terse

# Terse + critical (high quality, concise)
agentspec generate src/auth/ --critical --terse

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

# Works with all modes
agentspec generate src/auth.py --critical --diff-summary --terse
```

**What happens:**
1. CHANGELOG section shows commit messages only (no diffs)
2. Separate API call analyzes the actual git diffs
3. New section added: `CHANGELOG DIFF SUMMARY (LLM-generated):`
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

### Critical Mode Takes Too Long

```bash
# Process in smaller batches
agentspec generate src/auth/ --critical
agentspec generate src/models/ --critical
agentspec generate src/api/ --critical

# Or use standard mode for less critical files
agentspec generate src/utils/  # no --critical flag
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
agentspec generate src/ --model llama3.2 --provider openai

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
| **Generate (standard)** | `agentspec generate src/` |
| **Generate (critical)** | `agentspec generate src/ --critical` |
| **Generate (terse)** | `agentspec generate src/ --terse` |
| **Update existing** | `agentspec generate src/ --update-existing` |
| **Ultra-accurate update** | `agentspec generate src/ --critical --update-existing` |
| **With diff summaries** | `agentspec generate src/ --diff-summary` |
| **Preview changes** | `agentspec generate src/ --dry-run` |
| **Single file** | `agentspec generate src/file.py` |
| **Lint strict** | `agentspec lint src/ --strict` |
| **Extract markdown** | `agentspec extract src/` |
| **Extract JSON** | `agentspec extract src/ --format json` |
| **Force context prints** | `agentspec generate src/ --force-context` |
| **Use Ollama** | `agentspec generate src/ --model llama3.2 --provider openai` |

---

## Pro Tips

1. **Always start with --dry-run** to preview changes
2. **Use --critical for auth, payments, security** code
3. **Use --update-existing after refactoring** to keep docs in sync
4. **Combine flags** for power: `--critical --update-existing --force-context`
5. **Process single files** for surgical precision
6. **Use Haiku for bulk**, Sonnet/Opus for critical
7. **Extract after generation** to review quality
8. **Lint after updates** to ensure standards

---

## The Most Powerful Commands You'll Use

```bash
# The "Fix Everything" Command
agentspec generate src/ --update-existing --model claude-haiku-4-5

# The "Document Critical Code Perfectly" Command
agentspec generate src/auth/ --critical --force-context --model claude-sonnet-4-5-20250929

# The "Quick Single File Update" Command
agentspec generate src/changed_file.py --update-existing

# The "Paranoid Preview" Command
agentspec generate src/payments.py --critical --update-existing --dry-run

# The "Free Local Generation" Command
agentspec generate src/ --model llama3.2 --provider openai --base-url http://localhost:11434/v1
```

---

Remember: **--dry-run is your friend!** Always preview before applying changes.