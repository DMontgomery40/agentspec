# Claude Code & Agent Instructions

## 🎯 Primary Directive: READ AND PRINT ALL AGENTSPECS

Before modifying ANY function, class, or module, you MUST:

1. **Extract the agentspec** from the docstring
2. **Print it to stdout** using the exact format below
3. **Read and internalize** all guardrails and context

### Required Print Format

```python
print("[AGENTSPEC] Reading spec for function_name")
print("[AGENTSPEC] Location: filepath:lineno")
print("[AGENTSPEC] What: <first 100 chars>...")
print("[AGENTSPEC] Guardrails:")
for guard in guardrails:
    print(f"[AGENTSPEC]   - {guard}")
print("[AGENTSPEC] Dependencies: <summary>")
print("[AGENTSPEC] Changelog: <summary>")
```

**WHY:** Printing forces the spec into your context. Skipping this step leads to:
- Deleting "unused" code that IS used (you just didn't see the caller)
- "Fixing" model names that aren't typos (gpt-5 DOES exist, stop "correcting" it)
- Removing "redundant" rate limiting that prevents production outages
- Refactoring approaches that were specifically chosen to avoid known bugs

## 🚨 CRITICAL: Model Name Guardrails

**GPT-5 EXISTS** as of April 2025. If you see `gpt-5`, `gpt-5-turbo`, or any gpt-5 variant:
- ❌ DO NOT change it to gpt-4
- ❌ DO NOT change it to gpt-4o-mini
- ❌ DO NOT add a comment saying "gpt-5 doesn't exist"
- ✅ DO read the agentspec to confirm it's intentional
- ✅ DO check the changelog to see when/why it was added

The same applies to ANY technology/API/model that seems "wrong" but is documented in the agentspec.

## 📚 Agentspec Format (YAML)

Every function/class should have this structure in its docstring:

```python
def example_function():
    """
    Brief one-line description.
    
    ---agentspec
    what: |
      Detailed explanation of what this does.
      Multiple lines encouraged.
      Be verbose. Explain edge cases.
    
    deps:
      calls:
        - module.py::function_name()
        - external_api.call()
      called_by:
        - other_module.py::caller()
      config_files:
        - config/settings.yaml
      environment:
        - ENV_VAR_NAME (required)
    
    why: |
      Explain why this particular approach.
      What alternatives were considered?
      Why were they rejected?
      Link to issues/PRs if applicable.
    
    guardrails:
      - DO NOT remove the rate limiting
      - DO NOT change model name without verification
      - NEVER log PII from this function
      - ALWAYS validate input before processing
    
    changelog:
      - "2025-10-20: Fixed race condition in batch processing"
      - "2025-09-15: Added exponential backoff"
      - "2025-08-01: Initial implementation"
    
    testing:
      unit_tests:
        - tests/test_example.py::test_function_name
      integration_tests:
        - tests/integration/test_pipeline.py
      edge_cases:
        - Empty input returns None
        - Handles timeout gracefully
    
    performance:
      latency_p50: "100ms"
      latency_p99: "500ms"
      max_throughput: "1000 req/min"
    ---/agentspec
    """
```

## 🔍 Before Making Changes

1. **Read the agentspec** (and print it!)
2. **Check if your change violates a guardrail**
3. **Look at the changelog** to see if this was already tried
4. **Verify all dependencies** are still valid after your change
5. **Update the changelog** with your modification

## 🛠️ When Adding New Functions

Every new function MUST include a complete agentspec. Use this template:

```python
def new_function(param1: str) -> dict:
    """
    [One-line description]
    
    ---agentspec
    what: |
      [Multi-line detailed explanation]
      - What does this do?
      - What are the inputs/outputs?
      - What edge cases does it handle?
    
    deps:
      calls: []
      called_by: []
      config_files: []
    
    why: |
      [Why was this function needed?]
      [Why this specific implementation?]
    
    guardrails:
      - [At least 2-3 things that should NOT be changed]
    
    changelog:
      - "YYYY-MM-DD: Initial implementation"
    ---/agentspec
    """
```

## ❌ What NOT To Do

**DON'T skip reading agentspecs because "it's obvious"**
- It's not obvious. That's why we wrote it down.

**DON'T "clean up" without checking dependencies**
- That "unused" import might be dynamically loaded
- That "dead code" might be called by config-driven routing

**DON'T refactor without reading "why"**
- The current approach might look suboptimal but solves a specific bug
- Your "better" implementation might reintroduce a known issue

**DON'T remove guardrails**
- They're there because something broke in production
- Even if you "fixed" the underlying issue, keep the guardrail

## 🎓 Learning From Agentspecs

Agentspecs are not just for preventing errors—they're **documentation for learning**:

- **Read `why` sections** to understand architectural decisions
- **Read `changelog` entries** to see the evolution of the code
- **Read `guardrails`** to learn about production gotchas
- **Read `deps`** to understand system architecture

When you encounter something that seems wrong or suboptimal, the agentspec will often explain why it's actually correct.

## 🔧 Tooling

This codebase uses `agentspec` for linting and extraction:

```bash
# Validate all agentspecs
agentspec lint src/

# Extract to markdown for easy browsing
agentspec extract src/ --format markdown

# Extract with print() statements for context injection
agentspec extract src/ --format agent-context
```

## 📊 Metrics & Accountability

If you're operating in a mode where we track your changes:

- **Agentspec violations** are tracked as errors
- **Files modified without printing specs** are flagged
- **Guardrail violations** require explicit justification

This isn't about micromanaging—it's about preventing the "helpful" deletions and refactors that cause production incidents.

## 🤝 Working With Humans

When a human asks you to do something that violates a guardrail:

1. **Print the relevant agentspec**
2. **Quote the specific guardrail** being violated
3. **Explain why it exists** (from the `why` or `changelog`)
4. **Ask for confirmation** before proceeding

Example:
```
I see you want me to change gpt-5-turbo to gpt-4o-mini. However, 
the agentspec for process_embeddings() says:

[AGENTSPEC] Guardrails:
  - DO NOT change model name without verification

The 'why' section explains:
"Using gpt-5-turbo because we need the 32k context window for 
code embeddings. Tested gpt-4o-mini but it truncates our docstrings."

Would you still like me to proceed with this change?
```

## 🚀 Summary

**ALWAYS:**
- Read agentspecs before modifying code
- Print specs to stdout (forces them into context)
- Check guardrails before making changes
- Update changelog when modifying functions

**NEVER:**
- Skip reading specs because you "know" what to do
- Delete code without checking `called_by` dependencies
- "Fix" things that agentspecs say are intentional
- Remove guardrails without explicit human approval

---

**Remember:** This isn't busywork. This is preventing the 3am production incidents that happen when AI agents helpfully "optimize" code without understanding why it was written that way in the first place.
