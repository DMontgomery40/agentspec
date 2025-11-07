# 🔥 MERGE HELL RECOVERY PLAN 🔥

**Generated**: 2025-11-07  
**Current Branch**: `claude/agentspec-modular-refactor-011CUrtxucCQwoza3qagGn1d`  
**Status**: CRITICAL - 60% through massive refactor, tragically diverged from two other active branches

---

## 📊 SITUATION ANALYSIS

### Current Branch State (modular-refactor)
- **15 commits behind** `origin/claude/agentspec-modular-refactor-011CUrtxucCQwoza3qagGn1d`
- **Complete modular architecture refactor** (Phases 1-3)
- **Collectors architecture** for deterministic metadata extraction
- **Two-phase generation** (metadata → LLM)
- **P0 critical issues RESOLVED** ✅
- **End-to-end testing COMPLETE** ✅

### Diverged Branches

#### 1. `system-prompt-gen` (29 commits ahead, 11 behind)
**Key Features**:
- ✅ **`strip` command** - Top-level CLI command (CONFIRMED)
- ✅ **`prompts` command** - Top-level CLI command (CONFIRMED)
- ✅ **Prompt management system** (`agentspec/prompts.py`)
- ✅ **Prompt templates as .md files** (`agentspec/prompts/` directory)
- ✅ **Examples management** (`examples.json`, `examples_terse.json`)
- ✅ **Rich TUI overhaul** for all commands
- ✅ **JavaScript/TypeScript tree-sitter support**
- ✅ **Notebook UI** for Jupyter integration
- ✅ **GPT-5 Responses API support** with CFG
- ✅ **Hallucination detection tests**
- ✅ **Quality rubric** for agentspec validation
- ⚠️ **Deleted modular architecture** (collectors/, generators/, models/, parsers/)
- ⚠️ **Monolithic codebase** (all in single files)

#### 2. `main` (merged recently)
**Key Features**:
- Python version checking
- Basic CLI structure
- Stable release state
- **NO** modular architecture
- **NO** strip command
- **NO** prompts command
- **NO** JavaScript support

---

## 🎯 YOUR REQUIREMENTS

1. ✅ **NO MORE YAML** - Keep YAML generation but don't force it
   - Current: `--agentspec-yaml` flag (optional)
   - Status: ALREADY SATISFIED in current branch
   
2. ✅ **`strip` as top-level command** - Remove agentspec blocks
   - Location: `origin/system-prompt-gen:agentspec/strip.py`
   - Status: EXISTS in system-prompt-gen, MISSING in current branch
   
3. ❓ **`prompts` command decision** - Keep or remove?
   - Location: `origin/system-prompt-gen:agentspec/prompts.py`
   - Functionality: Add examples to prompt dataset, manage prompt templates
   - Status: EXISTS in system-prompt-gen, MISSING in current branch

---

## 🔍 DETAILED COMPARISON

### Modular Refactor (Current) vs System-Prompt-Gen

| Feature | Current Branch | system-prompt-gen | Winner |
|---------|----------------|-------------------|---------|
| **Architecture** | Modular (collectors, generators, providers) | Monolithic (single files) | 🏆 **Current** |
| **Maintainability** | High (separation of concerns) | Low (god files) | 🏆 **Current** |
| **Strip Command** | ❌ Missing | ✅ Implemented | 🏆 **system-prompt-gen** |
| **Prompts Command** | ❌ Missing | ✅ Implemented | 🏆 **system-prompt-gen** |
| **Prompt Management** | Inline strings | External .md files | 🏆 **system-prompt-gen** |
| **JavaScript Support** | ❌ Missing | ✅ Tree-sitter adapter | 🏆 **system-prompt-gen** |
| **Tests** | Modular tests | Comprehensive suite | 🏆 **system-prompt-gen** |
| **GPT-5 Responses API** | ❌ Missing | ✅ Implemented | 🏆 **system-prompt-gen** |
| **Quality Rubric** | ❌ Missing | ✅ Implemented | 🏆 **system-prompt-gen** |
| **Notebook UI** | ❌ Missing | ✅ Implemented | 🏆 **system-prompt-gen** |
| **Hallucination Detection** | ❌ Missing | ✅ Implemented | 🏆 **system-prompt-gen** |
| **Code Quality** | Clean, documented | Working, tested | 🏆 **system-prompt-gen** |

### What Current Branch Has That system-prompt-gen Deleted

- ✅ **Collectors architecture** (`agentspec/collectors/`)
- ✅ **Provider abstraction** (`agentspec/generators/providers/`)
- ✅ **Formatter abstraction** (`agentspec/generators/formatters/`)
- ✅ **Prompt abstraction** (`agentspec/generators/prompts/`)
- ✅ **Parser abstraction** (`agentspec/parsers/`)
- ✅ **Pydantic models** (`agentspec/models/`)
- ✅ **Orchestrator pattern** (clean separation)

**But**: These were 30% stubs according to AUDIT.md (now resolved)

---

## 💀 THE BRUTAL TRUTH

### Current Branch Status
**Architecture**: ⭐⭐⭐⭐⭐ (5/5) - Beautiful modular design  
**Completeness**: ⭐⭐⭐⭐☆ (4/5) - P0 issues fixed, but missing features  
**Tests**: ⭐⭐⭐☆☆ (3/5) - Basic tests passing  
**Features**: ⭐⭐☆☆☆ (2/5) - Missing strip, prompts, JS support  

### system-prompt-gen Status
**Architecture**: ⭐⭐☆☆☆ (2/5) - Monolithic, harder to maintain  
**Completeness**: ⭐⭐⭐⭐⭐ (5/5) - Everything works  
**Tests**: ⭐⭐⭐⭐⭐ (5/5) - Comprehensive test suite  
**Features**: ⭐⭐⭐⭐⭐ (5/5) - Strip, prompts, JS, GPT-5, all there  

### The Dilemma
- **Current branch**: Beautiful architecture, missing critical features
- **system-prompt-gen**: All features work, but monolithic codebase

---

## 🚨 CRITICAL DECISION POINT

### Option A: Cherry-Pick Features Into Current Branch ✅ **RECOMMENDED**
**Strategy**: Keep modular architecture, port features over

**Pros**:
- ✅ Preserves beautiful modular architecture
- ✅ Maintains separation of concerns
- ✅ Better long-term maintainability
- ✅ Can selectively import features

**Cons**:
- ⏰ Time-consuming (estimate: 8-12 hours)
- 🔧 Requires refactoring system-prompt-gen code
- 🧪 Need extensive testing

**What to Port**:
1. ✅ `strip` command (high priority)
2. ✅ `prompts` command (if desired)
3. ✅ Prompt management system (external .md files)
4. ✅ JavaScript tree-sitter support
5. ✅ GPT-5 Responses API support
6. ✅ Notebook UI
7. ✅ Hallucination detection
8. ✅ Quality rubric
9. ✅ Comprehensive test suite

**Estimated Work**: 200-300 tool calls

---

### Option B: Abandon Current Branch, Use system-prompt-gen ❌ **NOT RECOMMENDED**
**Strategy**: Throw away modular architecture, use working code

**Pros**:
- ✅ Everything already works
- ✅ Comprehensive test coverage
- ✅ No merge conflicts
- ✅ Immediate productivity

**Cons**:
- ❌ **LOSE 60% OF REFACTOR WORK**
- ❌ Monolithic codebase harder to maintain
- ❌ Harder to add new features later
- ❌ All the architectural benefits gone
- ❌ Waste of effort on modular design

---

### Option C: Parallel Merge (Frankenstein) ⚠️ **RISKY**
**Strategy**: Merge both branches, resolve conflicts manually

**Pros**:
- ✅ Keep both architectures
- ✅ No work lost

**Cons**:
- ❌ **HIGH RISK OF BREAKING EVERYTHING**
- ❌ Massive merge conflicts (46 files changed, 56,000+ lines)
- ❌ Will take 20+ hours
- ❌ Likely to introduce subtle bugs
- ❌ No guarantee it will work

---

## 🎯 RECOMMENDED PLAN: Option A (Cherry-Pick)

### Phase 1: Immediate (Strip Command)
**Priority**: CRITICAL  
**Estimated Time**: 2-3 hours

1. Port `agentspec/strip.py` from system-prompt-gen
2. Add `strip` subcommand to `agentspec/cli.py`
3. Add strip tests
4. **Smoke test**: `agentspec strip tests/ --dry-run`

### Phase 2: Prompt Management
**Priority**: HIGH  
**Estimated Time**: 3-4 hours

1. Create `agentspec/prompts/` directory
2. Extract prompts to .md files (already done in system-prompt-gen)
3. Port `agentspec/prompts.py` (prompt loading logic)
4. **Decision Point**: Keep or remove `prompts` CLI command?
   - If **KEEP**: Add full `prompts` subcommand with example management
   - If **REMOVE**: Just use prompt loading in generate.py

### Phase 3: JavaScript Support
**Priority**: MEDIUM  
**Estimated Time**: 4-5 hours

1. Port `agentspec/langs/javascript_adapter.py`
2. Add tree-sitter-javascript dependency
3. Update extract/lint/generate to support JS files
4. Add JS test fixtures
5. **Smoke test**: `agentspec generate tests/fixtures/javascript/`

### Phase 4: Advanced Features
**Priority**: LOW  
**Estimated Time**: 4-6 hours

1. Port GPT-5 Responses API support
2. Port notebook UI
3. Port hallucination detection
4. Port quality rubric
5. Add comprehensive test suite

---

## 🚦 DECISION REQUIRED FROM USER

### Question 1: `prompts` Command
**Context**: system-prompt-gen has a full `prompts` CLI command for:
- Adding examples to dataset
- Managing prompt templates
- Testing prompt quality

**Options**:
- A) **KEEP**: Full `prompts` subcommand (more tooling)
- B) **REMOVE**: Only keep prompt loading (simpler)
- C) **DEFER**: Add later if needed

**Recommendation**: **B (REMOVE)** - The example management is nice-to-have but not critical. Keep the prompt loading (external .md files) but skip the CLI command.

### Question 2: Architecture Strategy
**Options**:
- A) **CHERRY-PICK** (Recommended) - Port features into modular architecture
- B) **ABANDON** - Use system-prompt-gen, lose modular work
- C) **MERGE** - Try to merge both (high risk)

**Recommendation**: **A (CHERRY-PICK)** - Preserve the modular architecture, port features over carefully.

### Question 3: JavaScript Priority
**Options**:
- A) **HIGH** - Port JS support immediately (Phase 1)
- B) **MEDIUM** - Port after strip command (Phase 3)
- C) **LOW** - Defer JS support

**Recommendation**: **B (MEDIUM)** - Get strip command working first, then JS support.

---

## 📋 IMMEDIATE ACTION PLAN (Next 30 Minutes)

### Step 1: Create New Integration Branch
```bash
git checkout -b merge-recovery-strip-prompts
```

### Step 2: Port Strip Command
```bash
# Extract strip.py from system-prompt-gen
git show origin/system-prompt-gen:agentspec/strip.py > agentspec/strip.py

# Add to cli.py (manual edit required)
# Test it works
agentspec strip --help
```

### Step 3: Verify Current Functionality Still Works
```bash
# Run existing tests
pytest agentspec/tests/

# Test generate command
agentspec generate tests/ --dry-run

# Test lint command
agentspec lint agentspec/
```

### Step 4: Create Smoke Test for Strip
```bash
# Test strip command
agentspec strip tests/fixtures/ --dry-run --mode yaml
agentspec strip tests/fixtures/ --dry-run --mode docstrings
```

---

## 🎓 LESSONS LEARNED

### What Went Wrong
1. ❌ **Diverged branches without sync** - modular-refactor and system-prompt-gen evolved separately
2. ❌ **No feature flags** - couldn't toggle between architectures
3. ❌ **Massive refactor without incremental merges** - 60% done but isolated
4. ❌ **No branch protection** - allowed 29 commits to diverge

### What to Do Different
1. ✅ **Merge often** - Don't let branches diverge more than 5 commits
2. ✅ **Feature flags** - Allow toggling between old/new implementations
3. ✅ **Incremental refactors** - Small PRs, not massive rewrites
4. ✅ **Branch protection** - Require reviews before merging

---

## 🚀 NEXT STEPS

### User Decisions Needed:
1. **Confirm Option A (Cherry-Pick)** - Yes/No?
2. **`prompts` command** - Keep/Remove/Defer?
3. **JavaScript priority** - High/Medium/Low?

### Once Decided:
I will execute the recovery plan with:
- ✅ Verified smoke tests at each step
- ✅ No stubs or placeholders
- ✅ Full agentspec documentation
- ✅ Clean commit history

**Estimated Total Time**: 12-16 hours (200-300 tool calls)

---

## 📞 AWAITING YOUR INPUT

Please respond with:
1. **Confirm strategy**: Option A (Cherry-Pick)?
2. **Prompts command**: Keep/Remove/Defer?
3. **JS priority**: High/Medium/Low?
4. **Other concerns**: Anything else I should know?

Once you confirm, I'll start executing Phase 1 (Strip Command) immediately.

