# AI Agent Instructions: DO NOT CREATE STUBS, DO NOT CREATE PLACEHOLDERS, DO NOT CREATE/EDIT WITHOUT VERIFIED SMOKE TESTS

***NEVER return to the user with a "success!" or "complete" or "done" message WITHOUT A VERIFIED AND DOCUMENTED SMOKE TEST PROVING FUNCTIONALITY*** Tests should be saved in `agentspec/tests/`
MANDATORY: USE `agentspec/TOOLS.md` for your commands 


# This codebase uses **agentspec** — structured YAML and JS Doc blocks in docstrings that provide context, dependencies, guardrails, and historical information for every function and class.

**You MUST read and respect agentspecs** or you will break production systems.

## 📖 How To Use Agentspecs

### Step 1: Extract the Spec

### Step 2: Print It **(MANDATORY)**

  - ***Print the spec to stdout BEFORE making any changes:***

**Why printing?** It forces the information into your active context. Skipping this step leads to mistakes.

### Step 3: Check Guardrails, 'NOTE' entries

Every guardrail exists because something broke in production. Before making changes:

1. Read all guardrails
2. Verify your change doesn't violate any

### Step 4: Ensure your changes do not confilict with the 'what', 'why', or the Dependencies ('deps')

  - REAL consequences that have occured when this is not done: 
    - Agent removes "unused" imports (breaks dynamic loading)
    - Agent deletes "dead code" (actually used via config-driven dispatch)
    - Agent makes function async (reintroduces race condition from 3 commits ago)


## 📋 Agentspec Fields Reference

### Required Fields

- **`what`**: Detailed explanation of functionality (be verbose!)
- **`deps`**: All dependencies (calls, called_by, config files, env vars)
- **`why`**: Why this approach vs alternatives
- **`guardrails`**: What NOT to change and why

### Optional Fields

- **`security`**: Security considerations
- **`monitoring`**: What metrics/alerts exist
- **`known_issues`**: Documented bugs or limitations

# 🛠️ APPENDING Agentspecs - ***CRITICAL***

## ALWAYS: When you write OR EDIT code, ALWAYS include/UPDATE agentspec:

```
    """
    Brief one-line description.
    
    ---agentspec
    what: |
      Detailed multi-line explanation.
      - What does it do?
      - What are inputs/outputs?
      - What edge cases does it handle?
      
      Be VERBOSE. Future agents (and humans) will thank you.
    
    why: |
      Why DID YOU MAKE THIS CHAGE?
      Why this specific implementation?
      What alternatives did you consider?
      Why did you reject them?
    
    guardrails:
      - At least 2-3 things that should NOT be changed
      - Based on your design decisions
      - Be specific: "DO NOT X because Y"
   
    ---/agentspec
    """
    # Implementation
```

## 🧪 Testing Agentspecs

This codebase uses `agentspec` tooling:

```bash
# Lint all specs
agentspec lint src/

# Extract specs to markdown
agentspec extract src/ --format markdown

# Extract with print() statements
agentspec extract src/ --format agent-context
```


## 📊 Success Metrics

Good agent behavior:
- ✅ Always prints specs before modifications
- ✅ Updates changelog for every change
- ✅ Respects all guardrails
- ✅ Asks humans before violating guardrails

Bad agent behavior:
- ❌ Deletes "unused" code without checking deps
- ❌ "Fixes" things that specs say are intentional
- ❌ Refactors without reading `why` sections
- ❌ Skips printing specs "to save tokens"


**Write specs as if the next agent has no context about your decisions — because they don't.**

## 🚀 Final Checklist

Before submitting any code changes:

- [ ] Read all relevant agentspecs
- [ ] Printed specs to stdout
- [ ] Checked no guardrails violated
- [ ] Updated `what` if behavior changed
- [ ] Added changelog entry
- [ ] Updated `deps` if calls changed
- [ ] Added new guardrails if applicable
- [ ] Verified tests still pass
- [ ] Ran `agentspec lint` successfully

---

**Remember:** The goal isn't to slow you down — it's to prevent the "helpful" changes that cause 3am production incidents.

Read the specs. Print the specs. Respect the specs.
