# CLI AUDIT FINDINGS - Missing Flags in Rich Help Displays

**Date:** November 3, 2024  
**Issue:** Rich TUI help displays missing critical flags that exist in argparse  
**Priority:** CRITICAL ACCESSIBILITY (dyslexia accommodation requirement)

---

## 🚨 CONFIRMED MISSING FLAGS

### `agentspec generate -h` (_show_generate_rich_help)

**Argparse defines these flags:**
```python
--target          (positional, required)
--dry-run         ❌ MISSING from Rich help
--force-context   ❌ MISSING from Rich help
--model           ✅ In Rich help
--agentspec-yaml  ✅ In Rich help
--provider        ✅ In Rich help
--base-url        ✅ In Rich help
--update-existing ✅ In Rich help
--terse           ✅ In Rich help
--diff-summary    ❌ MISSING from Rich help
```

**Impact:** Users don't know about `--dry-run`, `--force-context`, or `--diff-summary` when viewing generate-specific help.

---

## 📋 AUDIT CHECKLIST

### Commands WITH Rich Help Functions:
- [ ] `_show_rich_help()` - Main help (shows ALL commands)
  - Status: --diff-summary IS included here
  - Missing: Needs audit for other commands' flags
  
- [ ] `_show_generate_rich_help()` - Generate command
  - **Status: 3 flags missing (see above)**
  - Needs: --dry-run, --force-context, --diff-summary
  
- [ ] `_show_prompts_rich_help()` - Prompts command
  - **Status: EXISTS but incomplete** (per user report)
  - Needs: Full TUI parity with generate -h
  - Missing: Provider-style guide, better examples

### Commands WITHOUT Rich Help Functions:
- [ ] **lint** - Only has argparse help
  - Flags: target, --min-lines, --strict
  - **Needs: Rich TUI implementation**
  
- [ ] **extract** - Only has argparse help
  - Flags: target, --format
  - **Needs: Rich TUI implementation**
  
- [ ] **strip** - Only has argparse help
  - Flags: target, --mode, --dry-run
  - **Needs: Rich TUI implementation**

---

## 🎯 CONSISTENCY ISSUES

### Format Inconsistencies:
1. **Main help** uses `Panel.fit()` for title → ✅ Good
2. **generate help** uses `Panel.fit()` → ✅ Good  
3. **prompts help** uses `Panel.fit()` → ✅ Good
4. **lint, extract, strip** use NO Rich formatting → ❌ Bad

### Content Inconsistencies:
1. **generate** has Provider Guide panel → ✅ Excellent for accessibility
2. **generate** has Examples panel → ✅ Good
3. **generate** has Key Flags table → ✅ Good (but incomplete)
4. **prompts** has all three → ✅ Good structure
5. **lint, extract, strip** have NONE of this → ❌ Bad

---

## 📐 ACCESSIBILITY STANDARDS (Required for Dyslexia)

Every command's `-h` output MUST have:

### 1. Visual Hierarchy
- ✅ Title panel with command name + description
- ✅ Clear sections with borders
- ✅ Color coding (cyan borders, yellow flags, green examples, white text)

### 2. Structured Information
- ✅ Provider/Usage guide (if applicable)
- ✅ Examples panel with copy-pasteable commands
- ✅ Flags table (ALL flags, not subset)
- ✅ Short, scannable lines (not paragraphs)

### 3. Consistency
- ✅ Same structure across all commands
- ✅ Same visual style (box types, colors, padding)
- ✅ Same level of detail

---

## 🔧 FIX PLAN

### Phase 1: Fix Missing Flags in Existing Rich Helps
1. **generate -h**: Add --dry-run, --force-context, --diff-summary to Key Flags table
2. **prompts -h**: Already has structure, needs content review

### Phase 2: Create Rich Help for Missing Commands
1. **Create `_show_lint_rich_help()`**
   - Title panel
   - Usage guide (what files/dirs it checks)
   - Examples (common use cases)
   - Flags table: --min-lines, --strict
   
2. **Create `_show_extract_rich_help()`**
   - Title panel
   - Format guide (markdown vs json vs agent-context)
   - Examples (piping to files, viewing in terminal)
   - Flags table: --format
   
3. **Create `_show_strip_rich_help()`**
   - Title panel
   - Mode guide (all vs yaml vs docstrings)
   - Examples (dry-run first, then real)
   - Flags table: --mode, --dry-run

### Phase 3: Audit for Parity
- [ ] Every command has same visual quality
- [ ] Every flag in argparse is in Rich help
- [ ] Every Rich help has examples
- [ ] All copy-pasteable commands tested

---

## 🧪 TESTING CHECKLIST

For each command:
```bash
# Does it show Rich formatting?
agentspec <command> -h

# Are all flags documented?
diff <(agentspec <command> --help 2>&1 | grep -- '--') \
     <(grep 'add_argument.*--' agentspec/cli.py | grep <command>_parser)

# Is it dyslexia-friendly? (Visual check)
- Clear sections? 
- Color coded?
- Short lines?
- Scannable layout?
```

---

## 📝 IMPLEMENTATION NOTES

### Where to Intercept Help:
```python
# In main() function, around line 697-712
if len(sys.argv) >= 2:
    if sys.argv[1] == "lint" and any(h in sys.argv for h in ("-h", "--help")):
        try:
            _show_lint_rich_help(); sys.exit(0)
        except Exception:
            pass
    # Repeat for extract, strip
```

### Template for New Rich Help Functions:
```python
def _show_<command>_rich_help():
    """Rich help for agentspec <command>"""
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich import box
    
    c = Console()
    
    # Title
    c.print(Panel.fit(
        "[bold magenta]agentspec <command>[/bold magenta]\n"
        "[dim]Brief description[/dim]",
        border_style="cyan", 
        padding=(1,2)
    ))
    
    # Guide/Usage
    guide = "..."
    c.print(Panel(guide, title="Usage Guide", border_style="dim", padding=(0,1)))
    
    # Examples
    examples = "..."
    c.print(Panel(examples, title="Examples", border_style="dim", padding=(0,1)))
    
    # Flags table
    t = Table(title="Flags", box=box.SIMPLE_HEAVY, show_header=False)
    t.add_column("Flag", style="yellow")
    t.add_column("Description")
    t.add_row("--flag", "Description")
    c.print(t)
```

---

## 🎯 SUCCESS CRITERIA

- [ ] Every command has Rich TUI help
- [ ] Every flag is documented in its command's Rich help
- [ ] Visual consistency across all commands
- [ ] All help screens tested with dyslexia in mind
- [ ] Copy-paste commands verified to work
- [ ] No missing flags between argparse and Rich help

---

**Next Steps:**
1. Fix `_show_generate_rich_help()` (add 3 missing flags)
2. Enhance `_show_prompts_rich_help()` to match generate quality
3. Create `_show_lint_rich_help()`
4. Create `_show_extract_rich_help()`
5. Create `_show_strip_rich_help()`
6. Final audit comparing argparse to Rich helps

