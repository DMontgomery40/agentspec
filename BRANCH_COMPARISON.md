# 🌳 BRANCH COMPARISON: Visual Guide

## Branch Divergence Map

```
                    main (stable)
                       │
                       │
          ┌────────────┴────────────┐
          │                         │
          │                         │
    modular-refactor          system-prompt-gen
    (current branch)          (29 ahead, 11 behind)
    (15 behind origin)
          │                         │
          │                         │
      P0 FIXED                 ALL FEATURES
      ✅ Collectors            ✅ Strip
      ✅ Two-phase            ✅ Prompts
      ✅ Metadata             ✅ JavaScript
      ❌ Strip                ✅ GPT-5
      ❌ Prompts              ✅ Notebook UI
      ❌ JavaScript           ✅ Tests
      
      DELETED MODULES:
      ❌ collectors/
      ❌ generators/
      ❌ models/
      ❌ parsers/
```

---

## File-by-File Comparison

### Current Branch (modular-refactor)

```
agentspec/
├── cli.py                 ✅ Rich TUI, 3 commands (lint, extract, generate)
├── collect.py             ✅ Metadata collection
├── extract.py             ✅ Extract agentspecs
├── generate.py            ✅ Generate docstrings
├── lint.py                ✅ Lint agentspecs
├── llm.py                 ✅ LLM abstraction
├── utils.py               ✅ Utilities
├── collectors/            ✅ Metadata collectors
│   ├── code_analysis/     ✅ Signature, deps, complexity
│   ├── git_analysis/      ✅ Blame, commit history
│   └── orchestrator.py    ✅ Collector orchestration
├── generators/            ✅ Generation pipeline
│   ├── formatters/        ✅ Python formatters
│   ├── prompts/           ✅ Prompt builders
│   └── providers/         ✅ Anthropic, OpenAI
├── models/                ✅ Pydantic models
└── parsers/               ✅ Python parser

MISSING:
❌ strip.py
❌ prompts.py
❌ prompts/ (external .md files)
❌ langs/ (JavaScript support)
❌ notebook_ui.py
```

### system-prompt-gen Branch

```
agentspec/
├── cli.py                 ✅ Rich TUI, 5 commands (lint, extract, generate, strip, prompts)
├── collect.py             ✅ Monolithic collection (all in one file)
├── extract.py             ✅ Extract agentspecs
├── generate.py            ✅ Monolithic generation (all in one file)
├── lint.py                ✅ Lint agentspecs
├── llm.py                 ✅ LLM abstraction
├── strip.py               ✅ Strip agentspecs
├── prompts.py             ✅ Prompt management
├── notebook_ui.py         ✅ Jupyter integration
├── utils.py               ✅ Utilities
├── prompts/               ✅ External prompt templates
│   ├── base_prompt.md     ✅ Main prompt
│   ├── terse_prompt.md    ✅ Terse mode
│   ├── examples.json      ✅ Example dataset
│   └── ... (many more)
├── langs/                 ✅ Language adapters
│   ├── javascript_adapter.py  ✅ Tree-sitter JS
│   └── python_adapter.py      ✅ Python adapter
└── tests/                 ✅ Comprehensive test suite

DELETED:
❌ collectors/
❌ generators/
❌ models/
❌ parsers/
```

---

## Feature Matrix

| Feature | Current | system-prompt-gen | Priority |
|---------|---------|-------------------|----------|
| **Core Commands** |
| `agentspec lint` | ✅ | ✅ | N/A |
| `agentspec extract` | ✅ | ✅ | N/A |
| `agentspec generate` | ✅ | ✅ | N/A |
| `agentspec strip` | ❌ | ✅ | 🔥 HIGH |
| `agentspec prompts` | ❌ | ✅ | 💭 USER DECISION |
| **Architecture** |
| Modular collectors | ✅ | ❌ | - |
| Modular generators | ✅ | ❌ | - |
| Modular providers | ✅ | ❌ | - |
| Pydantic models | ✅ | ❌ | - |
| **Prompt Management** |
| External .md files | ❌ | ✅ | 🔥 HIGH |
| Example dataset | ❌ | ✅ | 💭 MEDIUM |
| Prompt toolkit | ❌ | ✅ | 💭 DEFER? |
| **Language Support** |
| Python | ✅ | ✅ | N/A |
| JavaScript | ❌ | ✅ | 🔥 HIGH |
| TypeScript | ❌ | ✅ | 🔥 HIGH |
| **LLM Support** |
| Anthropic Claude | ✅ | ✅ | N/A |
| OpenAI Chat | ✅ | ✅ | N/A |
| GPT-5 Responses API | ❌ | ✅ | 💭 MEDIUM |
| **Advanced Features** |
| Notebook UI | ❌ | ✅ | 💭 LOW |
| Hallucination detection | ❌ | ✅ | 💭 LOW |
| Quality rubric | ❌ | ✅ | 💭 LOW |
| **Testing** |
| Basic tests | ✅ | - | - |
| Comprehensive suite | ❌ | ✅ | 🔥 HIGH |
| Hallucination tests | ❌ | ✅ | 💭 MEDIUM |
| JS/TS tests | ❌ | ✅ | 💭 MEDIUM |

---

## Code Size Comparison

### Current Branch
```
agentspec/cli.py:                935 lines
agentspec/collect.py:            [need count]
agentspec/generate.py:          1960 lines
agentspec/collectors/*:         ~2000 lines
agentspec/generators/*:         ~3000 lines
agentspec/models/*:             ~800 lines
agentspec/parsers/*:            ~800 lines

TOTAL: ~10,000 lines
```

### system-prompt-gen Branch
```
agentspec/cli.py:               ~1400 lines
agentspec/collect.py:           ~1500 lines
agentspec/generate.py:          ~3500 lines (includes all generation logic)
agentspec/strip.py:             ~400 lines
agentspec/prompts.py:           ~600 lines
agentspec/langs/*:              ~2500 lines
agentspec/prompts/*:            ~3000 lines (templates)
tests/*:                        ~5000 lines

TOTAL: ~18,000 lines
```

---

## What `strip` Command Does

From `origin/system-prompt-gen:agentspec/strip.py`:

```bash
# Remove all agentspec content (YAML + narrative docstrings)
agentspec strip src/ --mode all

# Remove only YAML blocks
agentspec strip src/ --mode yaml

# Remove only narrative docstrings
agentspec strip src/ --mode docstrings

# Preview without changes
agentspec strip src/ --dry-run
```

**Safety Features**:
- ✅ Per-edit compile checks (never breaks syntax)
- ✅ Bottom-to-top processing (avoids line shifts)
- ✅ Detects agentspec markers only (won't delete user docs)
- ✅ Removes associated `[AGENTSPEC_CONTEXT]` prints

**Use Cases**:
1. Clean up before refactor
2. Remove old specs before regenerating
3. Strip YAML but keep narrative
4. Testing generation pipeline

---

## What `prompts` Command Does

From `origin/system-prompt-gen:agentspec/prompts.py`:

```bash
# Add example to dataset
agentspec prompts --add-example \
  --file tests/test_generate.py \
  --function test_basic_generation \
  --subject-function agentspec.generate.run

# With bad/good output examples
agentspec prompts --add-example \
  --file src/auth.py \
  --bad-output "Brief function." \
  --good-output "Comprehensive agentspec..." \
  --correction "Should include dependencies, guardrails"

# Preview without saving
agentspec prompts --add-example --dry-run --file src/auth.py
```

**Functionality**:
- Add examples to prompt dataset (`examples.json`)
- Track good vs bad documentation
- Record corrections for LLM training
- Build "ASK USER" guardrails database

**Use Cases**:
1. Curate high-quality examples
2. Document failure modes
3. Train LLM with good patterns
4. Build automated quality checks

---

## Migration Complexity Estimate

### Phase 1: Strip Command (EASY)
**Effort**: 2-3 hours  
**Complexity**: ⭐⭐☆☆☆  
**Files to port**: 1 (`strip.py`)  
**Dependencies**: None (standalone)  
**Risk**: LOW

```python
# Simple port:
git show origin/system-prompt-gen:agentspec/strip.py > agentspec/strip.py

# Add to cli.py:
strip_parser = subparsers.add_parser("strip", ...)
```

### Phase 2: Prompt Management (MEDIUM)
**Effort**: 3-4 hours  
**Complexity**: ⭐⭐⭐☆☆  
**Files to port**: 
- `prompts.py` (prompt loading)
- `prompts/` directory (all .md files)
- Update `generate.py` to use external prompts

**Dependencies**: Must update generation pipeline  
**Risk**: MEDIUM (need to refactor prompt building)

### Phase 3: JavaScript Support (HARD)
**Effort**: 4-5 hours  
**Complexity**: ⭐⭐⭐⭐☆  
**Files to port**:
- `langs/javascript_adapter.py` (~1700 lines)
- `langs/python_adapter.py` (refactored version)
- Add tree-sitter-javascript dependency
- Update `extract.py`, `lint.py`, `generate.py` for JS

**Dependencies**: Tree-sitter, language detection  
**Risk**: MEDIUM-HIGH (large file, many dependencies)

### Phase 4: Advanced Features (VERY HARD)
**Effort**: 4-6 hours  
**Complexity**: ⭐⭐⭐⭐⭐  
**Files to port**:
- GPT-5 Responses API
- Notebook UI
- Hallucination detection
- Quality rubric
- Comprehensive test suite

**Dependencies**: Multiple systems  
**Risk**: HIGH (complex integrations)

---

## Decision Matrix

### If You Want Strip ASAP
→ **Phase 1 only** (2-3 hours)

### If You Want Core Features
→ **Phases 1-2** (5-7 hours)
- Strip command
- External prompt management
- Improved prompt quality

### If You Want Full Feature Parity
→ **Phases 1-3** (9-12 hours)
- Strip command
- External prompts
- JavaScript/TypeScript support

### If You Want Everything
→ **All Phases** (13-18 hours)
- Full feature set from system-prompt-gen
- Integrated into modular architecture
- Comprehensive tests

---

## Recommendation Summary

### ✅ DEFINITELY PORT
1. **Strip command** - Critical utility
2. **External prompt files** - Better maintainability
3. **JavaScript support** - Major feature gap

### 💭 MAYBE PORT (User Decision)
4. **Prompts CLI command** - Nice tooling, but not essential
5. **GPT-5 Responses API** - Advanced feature
6. **Notebook UI** - Specialized use case

### ⏸️ DEFER FOR LATER
7. **Hallucination detection** - Research feature
8. **Quality rubric** - Nice-to-have validation

---

## Next Steps

**Awaiting your decision on**:
1. Cherry-pick strategy (Option A)? **YES/NO**
2. Keep `prompts` command? **KEEP/REMOVE/DEFER**
3. JavaScript priority? **HIGH/MEDIUM/LOW**

Once confirmed, I will:
1. Create integration branch
2. Port strip command
3. Test thoroughly
4. Create smoke tests
5. Proceed to next phases as directed

**Ready to execute on your command.**

