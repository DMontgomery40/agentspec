# AI Agent Instructions

## 🎯 Core Principle

This codebase uses **agentspec** — structured YAML blocks in docstrings that provide context, dependencies, guardrails, and historical information for every function and class.

**You MUST read and respect agentspecs** or you will break production systems.

## 📖 How To Use Agentspecs

### Step 1: Extract the Spec

When you encounter a function with an agentspec block:

```python
def process_data(input: str) -> dict:
    """
    Process input data through the pipeline.
    
    ---agentspec
    what: |
      Takes raw input string, validates format, transforms to dict,
      and applies business rules. Critical path for data ingestion.
    
    deps:
      calls:
        - validators.validate_input()
        - transformers.to_dict()
      called_by:
        - api_handler.post_data()
        - batch_processor.process_batch()
    
    why: |
      Using synchronous processing because async caused race conditions
      in the transformation step (see issue #1234)
    
    guardrails:
      - DO NOT make this async without fixing issue #1234
      - DO NOT remove input validation - causes downstream crashes
      - NEVER return partial results on error
    
    changelog:
      - "2025-10-01: Reverted to sync after async race conditions"
      - "2025-09-15: Added comprehensive input validation"
    ---/agentspec
    """
```

### Step 2: Print It (Mandatory)

Print the spec to stdout **before** making any changes:

```python
print("[AGENTSPEC] Reading spec for process_data")
print("[AGENTSPEC] What: Takes raw input string, validates format...")
print("[AGENTSPEC] Guardrails:")
print("[AGENTSPEC]   - DO NOT make this async without fixing issue #1234")
print("[AGENTSPEC]   - DO NOT remove input validation")
print("[AGENTSPEC]   - NEVER return partial results on error")
```

**Why printing?** It forces the information into your active context. Skipping this step leads to mistakes.

### Step 3: Check Guardrails

Every guardrail exists because something broke in production. Before making changes:

1. Read all guardrails
2. Verify your change doesn't violate any
3. If it does, explain why and get human approval

### Step 4: Update the Spec

After making changes, update the relevant sections:

```python
# If you modify the function
- Update 'what' if behavior changed
- Add entry to 'changelog' with date and reason
- Update 'deps' if you add/remove calls

# If you add guardrails
- Document what NOT to do and why

# If you change approach
- Update 'why' to explain the new approach
```

## 🚨 Common Mistakes (DON'T DO THESE)

### ❌ Mistake 1: "Cleaning Up Unused Code"

```python
# You see:
def rarely_used_function():
    """Only called in special edge case"""
    pass

# You think: "This is never used, I'll delete it"
# Reality: It's called via dynamic import in config-driven routing
# Result: Production breaks during edge case
```

**Fix:** Always check `called_by` in the agentspec before deleting.

### ❌ Mistake 2: "Fixing Obvious Typos"

```python
# You see:
model = "gpt-5-turbo"

# You think: "That's a typo, gpt-5 doesn't exist"
# Reality: GPT-5 was released in April 2025
# Result: You downgrade to an inferior model
```

**Fix:** If something seems wrong, read the agentspec `why` section first.

### ❌ Mistake 3: "Optimizing Suboptimal Code"

```python
# You see:
def slow_sequential_processor():
    for item in items:
        process(item)  # Why not use multiprocessing?

# You think: "I'll parallelize this for better performance"
# Reality: The agentspec says "DO NOT parallelize - causes data corruption"
# Result: Silent data corruption in production
```

**Fix:** Read the `why` section to understand architectural decisions.

### ❌ Mistake 4: "Removing Redundant Checks"

```python
# You see:
if not input:
    raise ValueError("Input required")
if len(input) == 0:  # Redundant check?
    raise ValueError("Input cannot be empty")

# You think: "The second check is redundant"
# Reality: First check catches None, second catches empty string explicitly
# Result: Silent failures on empty string inputs
```

**Fix:** Read guardrails before removing "redundant" code.

## 📋 Agentspec Fields Reference

### Required Fields

- **`what`**: Detailed explanation of functionality (be verbose!)
- **`deps`**: All dependencies (calls, called_by, config files, env vars)
- **`why`**: Why this approach vs alternatives
- **`guardrails`**: What NOT to change and why

### Recommended Fields

- **`changelog`**: History of changes with dates
- **`testing`**: Test coverage details
- **`performance`**: Latency, throughput, resource usage

### Optional Fields

- **`security`**: Security considerations
- **`monitoring`**: What metrics/alerts exist
- **`known_issues`**: Documented bugs or limitations

## 🛠️ Creating Agentspecs

When you write new code, ALWAYS include an agentspec:

```python
def new_function(param: str) -> bool:
    """
    Brief one-line description.
    
    ---agentspec
    what: |
      Detailed multi-line explanation.
      - What does it do?
      - What are inputs/outputs?
      - What edge cases does it handle?
      
      Be VERBOSE. Future agents (and humans) will thank you.
    
    deps:
      calls:
        - List every function/method you call
      called_by:
        - Initially empty, update as callers emerge
      config_files:
        - Any config files this reads
      environment:
        - Any env vars (mark as required/optional)
    
    why: |
      Why does this function exist?
      Why this specific implementation?
      What alternatives did you consider?
      Why did you reject them?
    
    guardrails:
      - At least 2-3 things that should NOT be changed
      - Based on your design decisions
      - Be specific: "DO NOT X because Y"
    
    changelog:
      - "YYYY-MM-DD: Initial implementation"
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

Integrate these into your CI/CD pipeline.

## 🤖 Multi-Agent Scenarios

If multiple agents are working on the same codebase:

1. **Always read specs from other agents' changes**
2. **Don't override specs without human review**
3. **Add to changelog, don't replace it**
4. **Coordinate on guardrails** (don't create conflicts)

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

## 🎓 Philosophy

Agentspecs exist because:

1. **AI agents lack git blame intuition** — you don't know why code was written this way
2. **Codebases evolve through failures** — guardrails encode hard-learned lessons
3. **Context is expensive** — but cheaper than production incidents
4. **Humans forget too** — specs help everyone, not just AI

The verbosity is intentional. The redundancy is intentional. The "obvious" explanations are intentional.

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
