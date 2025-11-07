# 🔬 REAL MERGE ANALYSIS - DEEP CODE DIVE

**Generated**: 2025-11-07  
**Analysis Type**: ACTUAL CODE COMPARISON (not filenames)

You were right - I was doing surface-level analysis. Here's what the code actually shows.

---

## 🎯 WHAT I FOUND IN THE CODE

### system-prompt-gen/cli.py (1086 lines)

**IMPORTS** (Line 13):
```python
from agentspec import lint, extract, strip  # <-- strip is imported!
```

**NEW COMMANDS IN RICH HELP** (Lines 427-431):
```python
commands_table.add_row("lint", "Validate agentspec blocks in Python files")
commands_table.add_row("extract", "Extract agentspec blocks to markdown or JSON")
commands_table.add_row("generate", "Auto-generate verbose agentspec docstrings using Claude")
commands_table.add_row("strip", "Remove agentspec-generated docstrings from Python files")  # <-- NEW!
commands_table.add_row("prompts", "Prompts and examples toolkit")  # <-- NEW!
```

**STRIP COMMAND IMPLEMENTATION** (Lines 976-983):
```python
# strip
strip_parser = subparsers.add_parser("strip", help="Remove agentspec blocks")
strip_parser.add_argument("target", help="File or directory")
strip_parser.add_argument(
    "--mode",
    choices=["all", "yaml", "docstrings"],
    default="all",
)
strip_parser.add_argument("--dry-run", action="store_true")
```

**PROMPTS COMMAND** (Lines 985-997):
```python
# prompts (new)
prompts_parser = subparsers.add_parser("prompts", help="Prompts and examples toolkit")
prompts_parser.add_argument("path", nargs="?", help="Optional file path (same as --file)")
prompts_parser.add_argument("--add-example", dest="add_example", action="store_true")
prompts_parser.add_argument("--file", dest="file", required=False)
prompts_parser.add_argument("--function", dest="function", required=False)
prompts_parser.add_argument("--subject-function", dest="subject_function", required=False)
prompts_parser.add_argument("--bad-output", dest="bad_output", required=False)
prompts_parser.add_argument("--good-output", dest="good_output", required=False)
prompts_parser.add_argument("--correction", dest="correction", required=False)
prompts_parser.add_argument("--require-ask-user", dest="require_ask_user", action="store_true")
prompts_parser.add_argument("--dry-run", action="store_true")
prompts_parser.add_argument("--strict-ratio", dest="strict_ratio", action="store_true")
```

**BONUS SURPRISE** (Line 973):
```python
generate_parser.add_argument("--strip", dest="strip", action="store_true")
```
**There's ALSO a --strip FLAG within the generate command!**

**COMMAND DISPATCH** (Lines 1048-1051, 1053-1076):
```python
elif args.command == "strip":
    from agentspec import strip as _strip
    rc = _strip.run(target=args.target, mode=args.mode, dry_run=args.dry_run)
    sys.exit(0 if rc == 0 else 1)

elif args.command == "prompts":
    if getattr(args, "add_example", False):
        target_file = args.file or args.path
        if not target_file:
            print("❌ --file (or positional <path>) is required when using --add-example", file=sys.stderr)
            sys.exit(1)
        from agentspec.tools.add_example import _main_impl as _add_example
        _add_example(
            file_path=target_file,
            function_name=args.function,
            subject_function=args.subject_function,
            bad_output=args.bad_output,
            good_output=args.good_output,
            correction=args.correction,
            require_ask_user=args.require_ask_user,
            dry_run=args.dry_run,
            strict_ratio=args.strict_ratio,
        )
```

**RICH TUI FUNCTIONS** (system-prompt-gen has dedicated help for EACH command):
- `_show_rich_help()` - Global help
- `_show_generate_rich_help()` - Generate-specific with provider guide
- `_show_lint_rich_help()` - Lint-specific
- `_show_extract_rich_help()` - Extract-specific  
- `_show_strip_rich_help()` - Strip-specific (Lines 723-781)
- `_show_prompts_rich_help()` - Prompts-specific (Lines 536-616)

---

## 📂 FILES THAT EXIST IN system-prompt-gen

### 1. `agentspec/strip.py`
**What it does**: Removes agentspec-generated content
- `strip_file()` function with AST parsing
- Per-edit compile checks
- Three modes: `all`, `yaml`, `docstrings`
- Detects agentspec markers to avoid deleting user docs
- Bottom-to-top processing to preserve line numbers

**From the commit messages**:
- Has `_detect_agentspec_doc()` heuristics
- Removes adjacent `[AGENTSPEC_CONTEXT]` prints
- Safe: never breaks Python syntax

### 2. `agentspec/prompts.py`
**What it does**: Loads prompt templates from external `.md` files
```python
from agentspec.prompts import (
    get_verbose_docstring_prompt,
    get_terse_docstring_prompt,
    load_provider_base_prompt,
)
```

**Functions**:
- `load_prompt(prompt_name: str) -> str` - Loads from `agentspec/prompts/*.md`
- `load_base_prompt() -> str` - Loads main prompt
- `load_provider_base_prompt(provider, terse)` - Provider-specific prompts

### 3. `agentspec/prompts/` directory
**Files**:
- `base_prompt.md` - Main generation prompt
- `base_prompt_anthropic.md` - Claude-specific
- `base_prompt_openai_responses.md` - GPT-5 Responses API
- `base_prompt_chat_local.md` - Ollama/local
- `base_prompt_terse.md` - Terse mode
- `terse_docstring.md`, `terse_docstring_v2.md`
- `verbose_docstring.md`, `verbose_docstring_v2.md`
- `examples.json` - Example dataset
- `examples_terse.json` - Terse examples
- `lint_rules.json` - Linting rules
- `diff_summary.md` - Diff summary prompt

### 4. `agentspec/tools/add_example.py`
**What it does**: Manages example dataset for prompts
- Adds good/bad documentation examples
- Maintains good:bad ratio
- Validates ASK USER guardrails
- Dry-run preview

### 5. `agentspec/notebook_ui.py`
**What it does**: Jupyter notebook integration
- UI for interactive documentation generation

---

## 🔍 CURRENT BRANCH ARCHITECTURE

### Current cli.py (935 lines)
**Has**:
- `lint`, `extract`, `generate` commands
- Rich TUI help (global only)
- Fuzzy argument matching
- NO `strip` command
- NO `prompts` command

### Current generate.py (976 lines)
**Architecture**:
- Uses modular `agentspec/generators/` directory
- Imports from `agentspec.generators.prompts.base`
- Prompts are INLINE strings (GENERATION_PROMPT, GENERATION_PROMPT_TERSE)
- Has `inject_deterministic_metadata()` function

**Prompts are inline** (Lines 22-134):
```python
GENERATION_PROMPT = """You are helping to document a Python codebase..."""
GENERATION_PROMPT_TERSE = """You are helping to document a Python codebase with concise docstrings..."""
AGENTSPEC_YAML_PROMPT = """You are helping to document a Python codebase by creating an embedded agentspec YAML block..."""
```

### Current modular architecture:
```
agentspec/generators/
├── formatters/
│   ├── python/
│   │   ├── google_docstring.py
│   │   ├── numpy_docstring.py
│   │   └── sphinx_docstring.py
│   └── base.py
├── prompts/
│   ├── base.py (BasePrompt ABC)
│   ├── verbose.py (VerbosePrompt class)
│   └── terse.py (TersePrompt class)
└── providers/
    ├── base.py
    ├── anthropic.py
    ├── openai.py
    └── local.py
```

---

## 💥 THE ACTUAL PROBLEM

### What You Said:
> "prompts.py got split out with other logic across other files"

### What Really Happened:

**system-prompt-gen**:
- Prompts are in **external .md files** loaded at runtime
- `agentspec/prompts.py` has loader functions
- `agentspec/prompts/*.md` files contain actual prompts
- `agentspec/generate.py` imports from `agentspec.prompts`

**Current Branch (modular-refactor)**:
- Prompts are split into **classes** (`VerbosePrompt`, `TersePrompt`)
- Located in `agentspec/generators/prompts/`
- But the actual prompt text is **INLINE strings in generate.py**
- NOT using the classes at all currently!

**The Disconnect**:
Your refactor created a beautiful modular architecture with `BasePrompt`, `VerbosePrompt`, `TersePrompt` classes... but then `generate.py` doesn't actually USE them. It still has inline prompt strings.

Meanwhile, system-prompt-gen went a completely different direction: external `.md` files with a simple loader.

---

## 📊 FEATURE COMPARISON (ACTUAL CODE)

| Feature | Current Branch | system-prompt-gen | Winner |
|---------|----------------|-------------------|--------|
| **Strip Command** | ❌ None | ✅ Full implementation | system-prompt-gen |
| **Prompts Command** | ❌ None | ✅ Full dataset toolkit | system-prompt-gen |
| **Prompt Storage** | Inline strings in generate.py | External .md files | system-prompt-gen |
| **Prompt Classes** | ✅ Created but unused | ❌ Deleted | Current |
| **Modular Formatters** | ✅ Full architecture | ❌ Monolithic | Current |
| **Modular Providers** | ✅ Full architecture | ❌ Monolithic | Current |
| **Generate File Size** | 976 lines | 2001 lines | Current (cleaner) |
| **CLI File Size** | 935 lines | 1086 lines | Current (slightly) |

---

## 🎭 THE IRONY

**Your Modular Refactor**:
- Created beautiful abstractions (`BasePrompt`, `VerbosePrompt`, `TersePrompt`)
- Split providers into separate files
- Split formatters into separate files
- Created proper separation of concerns

**But**:
- `generate.py` still uses inline prompt strings
- The `generators/prompts/` classes are **NOT USED**
- The architecture is there but not wired up

**Meanwhile, system-prompt-gen**:
- Deleted all your modular architecture
- Made everything monolithic again
- BUT actually implemented external prompt loading
- AND added strip/prompts commands

---

## 🧩 WHAT NEEDS TO HAPPEN

### The Real Merge Challenge:

1. **Prompts**: Two incompatible approaches
   - **Current**: Unused classes in `generators/prompts/`
   - **system-prompt-gen**: External `.md` files with loader

   **Decision**: Pick one or merge both
   - Option A: Keep classes but load text from `.md` files
   - Option B: Delete classes, use system-prompt-gen loader
   - Option C: Actually USE the classes (wire them up)

2. **Strip**: Easy to port
   - Just copy `agentspec/strip.py`
   - Add to cli.py imports and subcommands
   - **Estimated**: 2-3 hours

3. **Prompts Command**: Medium complexity
   - Copy `agentspec/tools/add_example.py`
   - Copy `agentspec/prompts/*.json` files
   - Add to cli.py
   - **Estimated**: 3-4 hours

4. **Prompt Architecture**: Hard decision
   - Reconcile inline strings vs .md files vs classes
   - **Estimated**: 4-6 hours to design + implement

---

## ⚠️ CRITICAL INSIGHT

**The user said**:
> "Codex is saying --strip is here but I can't find it"

**What's actually happening**:
- There IS a `--strip` FLAG in system-prompt-gen's generate command (line 973)
- There IS a `strip` SUBCOMMAND in system-prompt-gen (line 976-983)
- There is NO strip in current branch AT ALL

So maybe you saw Codex's analysis of system-prompt-gen and thought it was in current branch?

---

## 🎯 ACTUAL RECOMMENDATIONS

### 1. Strip Command - PORT IT
**Complexity**: EASY  
**Time**: 2-3 hours  
**Value**: HIGH (you explicitly want this)

**Steps**:
1. `git show origin/system-prompt-gen:agentspec/strip.py > agentspec/strip.py`
2. Add to cli.py imports
3. Add strip_parser
4. Add dispatch logic
5. Test

### 2. External Prompts - HYBRID APPROACH
**Complexity**: MEDIUM  
**Time**: 4-5 hours  
**Value**: HIGH (better maintainability)

**Strategy**:
1. Keep your modular class architecture
2. But load prompt TEXT from `.md` files
3. Best of both worlds: OOP design + external editability

**Implementation**:
```python
# In generators/prompts/verbose.py
from agentspec.prompts import load_prompt

class VerbosePrompt(BasePrompt):
    def build_system_prompt(self, language: str, style: str) -> str:
        # Load from external file instead of inline string
        return load_prompt("verbose_docstring")
```

### 3. Prompts Command - MAYBE SKIP
**Complexity**: MEDIUM  
**Time**: 3-4 hours  
**Value**: LOW (nice-to-have, not critical)

**Decision**: Defer until after strip and external prompts

### 4. Fix Current Architecture - CRITICAL
**Complexity**: MEDIUM  
**Time**: 2-3 hours  
**Value**: HIGH (finish what you started)

**Problem**: You created prompt classes but don't use them

**Fix**: Wire up the classes in generate.py:
```python
# Instead of:
GENERATION_PROMPT = """..."""

# Do:
from agentspec.generators.prompts.verbose import VerbosePrompt
prompt_builder = VerbosePrompt()
system_prompt = prompt_builder.build_system_prompt(language="python", style="google")
```

---

## 📋 REVISED RECOVERY PLAN

### Phase 1: Fix Current Architecture (2-3 hrs)
**Goal**: Actually USE the modular architecture you built
1. Wire up prompt classes in generate.py
2. Remove inline prompt strings
3. Test that generation still works

### Phase 2: External Prompt Files (3-4 hrs)
**Goal**: Move prompts to .md files
1. Create `agentspec/prompts/` directory
2. Copy `.md` files from system-prompt-gen
3. Modify prompt classes to load from files
4. Test

### Phase 3: Strip Command (2-3 hrs)
**Goal**: Add strip functionality
1. Port `strip.py`
2. Add to CLI
3. Test with --dry-run
4. Create smoke tests

### Phase 4: JavaScript Support (OPTIONAL, 6-8 hrs)
**Goal**: Add JS/TS support
1. Port `agentspec/langs/` directory
2. Update extract/lint/generate
3. Test

### Phase 5: Prompts Command (OPTIONAL, 3-4 hrs)
**Goal**: Add dataset management
1. Port `tools/add_example.py`
2. Add to CLI
3. Test

---

##  TOTAL EFFORT ESTIMATE

**Minimum Viable** (Phases 1-3): 7-10 hours  
**With JavaScript** (Phases 1-4): 13-18 hours  
**Full Feature Parity** (All Phases): 16-22 hours

**My previous estimate of "5-7 hours" was WRONG**. You were right to call that out.

---

## ❓ AWAITING YOUR DECISIONS

1. **Confirm approach**: Fix current architecture + external prompts + strip?
2. **Skip prompts command**: Defer or include?
3. **JavaScript priority**: Now or later?
4. **Start immediately**: Or more analysis needed?

**I apologize for the surface-level analysis earlier. This is the real picture.**

