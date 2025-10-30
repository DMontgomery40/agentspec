# 🔧 Agentspec Retrofit Guide

Use this guide to add comprehensive agentspecs to existing codebases.

## 📝 The Retrofit Prompt

Copy the prompt below and use it with your AI agent. Attach the file(s) you want to retrofit.

**Best Practice:** Process 500 lines at a time to avoid skipping functions.

---

## PROMPT START

```
Please add comprehensive agentspec blocks to ALL functions and classes in the attached file.

REQUIREMENTS:

1. EVERY function and class needs an agentspec block
2. Minimum 10 lines in the 'what' section - be EXTREMELY verbose
3. Valid YAML formatting (use | for multiline strings)
4. Specific, actionable guardrails (not vague warnings)

FORMAT:

def function_name(params):
    """
    Brief one-line summary.
    
    ---agentspec
    what: |
      [10-20 lines of detailed explanation]
      - What does this function do? (not just "processes data" - HOW?)
      - What are inputs? Expected formats? Validation?
      - What are outputs? Structure? Format?
      - What edge cases does it handle?
      - What assumptions does it make?
      - Any important algorithms or business logic?
      - Performance characteristics?
      - Error handling approach?
      
      Context: [Why this function exists in the system]
      
      Example usage:
      result = function_name(param="value")
      # Returns: {expected: "structure"}
    
    deps:
      calls:
        - [List every function/method called, with module paths]
        - Example: "src/utils/validators.py::validate_email()"
        - Example: "openai.ChatCompletion.create()"
      called_by:
        - [List files/functions that call this]
        - Search the codebase if needed
        - If unknown: "⚠️ Callers unknown - needs codebase audit"
      config_files:
        - [Any config files read]
        - Example: "config/models.yaml"
      environment:
        - [Environment variables with (required) or (optional)]
        - Example: "OPENAI_API_KEY (required)"
      external_services:
        - [Any external APIs/services called]
        - Example: "OpenAI API (chat completions endpoint)"
    
    why: |
      [Explain design decisions - be detective-like]
      
      Why this approach specifically?
      - [Reason 1 - e.g., "Synchronous to avoid race conditions"]
      - [Reason 2 - e.g., "Uses regex instead of parser for performance"]
      
      What alternatives were rejected?
      - [Alternative 1]: [Why not used]
      - [Alternative 2]: [Why not used]
      
      Known tradeoffs:
      - [Tradeoff 1 - e.g., "Slower but more reliable"]
      - [Tradeoff 2 - e.g., "Uses more memory but avoids disk I/O"]
      
      If you can't determine why, write:
      "⚠️ Design rationale unclear from code - needs developer documentation"
    
    guardrails:
      - [3-5 specific things that should NOT be changed]
      - Format: "DO NOT [action] because [consequence]"
      - Examples:
      - "DO NOT make this async - causes race condition in downstream cache"
      - "DO NOT change model name from gpt-5 - it exists and is intentional"
      - "DO NOT remove input validation - leads to SQL injection in caller"
      - "DO NOT batch >100 items - API hard limit causes 400 errors"
      - "NEVER log the response - may contain PII/credentials"
    
    changelog:
      - "2025-10-29: Added initial agentspec for AI agent compatibility"
      - [If you can infer changes from git/comments, add them]
      - Format: "YYYY-MM-DD: [What changed] - [Why it changed]"
    
    testing:
      unit_tests:
        - [List test files/functions that cover this]
        - If none: "⚠️ No unit tests found - needs test coverage"
      integration_tests:
        - [List integration tests if any]
      edge_cases:
        - "Empty string input → returns None"
        - "Null value → raises ValueError"
        - "Invalid format → logs warning and skips"
        - [List all edge cases handled]
      known_failures:
        - [Any known bugs or limitations]
        - Link to issues if applicable
    
    performance:
      # Only include if relevant/measurable
      typical_latency: "100ms for 1KB input"
      memory_usage: "~50MB peak for batch of 100"
      scalability: "Linear O(n) with input size"
      bottlenecks: "Network I/O to external API"
    
    security:
      # Only include if relevant
      auth_required: "Yes - requires API key"
      pii_handling: "Logs are sanitized of PII"
      rate_limiting: "100 requests/minute"
    ---/agentspec
    """
    # existing code unchanged
```

PROCESS:

1. Read the entire file first
2. Identify all functions and classes
3. For EACH function/class, add the agentspec
4. DO NOT skip any functions - even small helpers
5. DO NOT change the actual code, only add docstrings

OUTPUT FORMAT:

Return the entire file with agentspecs added. Make NO other changes.

SPECIAL INSTRUCTIONS:

- If a function seems obvious, the agentspec should be even MORE detailed
- If you can't determine dependencies, explicitly say so in the spec
- If guardrails aren't obvious, think about what would break if someone refactored
- ALWAYS include at least 3 guardrails per function
- Minimum 10 lines for 'what' section - be absurdly verbose
```

## PROMPT END

---

## 🎯 Usage Tips

### For Large Files (>500 lines)

Break into chunks:

```bash
# Split file into 500-line chunks
split -l 500 large_file.py chunk_

# Process each chunk
# Then manually recombine
```

Or use this prompt modification:

```
Please add agentspecs to functions in lines 1-500 of this file.
Output ONLY those lines with specs added.
```

### For Entire Codebases

Create a script:

```python
#!/usr/bin/env python3
"""Process all Python files in a directory."""
import os
from pathlib import Path

def get_python_files(directory):
    return list(Path(directory).rglob("*.py"))

files = get_python_files("src/")
print(f"Found {len(files)} files to process")
print("\nProcess these files with the retrofit prompt:")
for f in files:
    print(f"  - {f}")
```

### Quality Checklist

After retrofitting, run:

```bash
# Lint to verify format
agentspec lint src/

# Extract to review
agentspec extract src/ --format markdown

# Read the output and verify:
# ✅ All functions have specs
# ✅ 'what' sections are verbose (10+ lines)
# ✅ Guardrails are specific and actionable
# ✅ YAML is valid
# ✅ Dependencies are listed
```

## 🚨 Common Issues

### Issue: Agent skips functions

**Solution:** Process fewer lines per batch (300-400 instead of 500)

### Issue: 'what' sections are too brief

**Example of TOO BRIEF:**
```yaml
what: Processes the input data
```

**Example of GOOD:**
```yaml
what: |
  Processes raw JSON input from the API endpoint by:
  1. Validating the JSON structure against schema v2.1
  2. Extracting user_id and timestamp fields
  3. Converting timestamp from ISO8601 to Unix epoch
  4. Normalizing user_id to lowercase
  5. Checking against blacklist (blacklist.json)
  6. If validation fails, logs error and returns None
  7. If validation succeeds, returns dict with normalized fields
  
  This function is the entry point for all incoming webhook data.
  Performance critical - runs on every webhook (5000+ per minute).
```

**Fix:** Tell the agent: "The 'what' section is too brief. Rewrite with 15+ lines explaining step-by-step what happens."

### Issue: Guardrails are vague

**Example of VAGUE:**
```yaml
guardrails:
  - Be careful with this function
  - Don't change without testing
```

**Example of SPECIFIC:**
```yaml
guardrails:
  - DO NOT remove the timestamp conversion - downstream systems expect Unix epoch
  - DO NOT skip blacklist check - required for compliance (GDPR Article 17)
  - DO NOT make this async - must maintain sequential processing order
  - NEVER remove the try/catch - crashes take down entire webhook handler
```

**Fix:** Tell the agent: "Rewrite guardrails to be specific. Format: 'DO NOT [action] because [specific consequence]'"

### Issue: Dependencies are incomplete

**Fix:** Tell the agent:

```
Search the codebase for all calls to this function.
Update the 'called_by' section with actual callers.
Use grep or search tools to find references.
```

## 📊 Progress Tracking

Create a tracking file:

```markdown
# Agentspec Retrofit Progress

## Status by Directory

- [ ] src/api/ (12 files)
- [ ] src/core/ (8 files)
- [ ] src/utils/ (15 files)
- [ ] src/models/ (6 files)

## Completed Files

- [x] src/api/handlers.py (2025-10-29)
- [x] src/api/routes.py (2025-10-29)

## Known Issues

- validators.py: Agent skipped 3 small helper functions
- database.py: Guardrails too vague, need rewrite

## Time Spent

~15 minutes per file average
```

## 🎓 Learning From Agentspecs

As you retrofit, you'll discover:

- **Functions you didn't know existed**
- **Dependencies you didn't know about**
- **Design decisions that now make sense**
- **Guardrails that prevent past bugs**

This is GOOD. This is the point.

Document everything you learn in the agentspecs.

---

## 🚀 Final Workflow

1. **Pick a file** (start with core/critical files)
2. **Use the retrofit prompt** (with 500 lines max)
3. **Review the output** (check verbosity, guardrails, YAML)
4. **Run agentspec lint** (verify format)
5. **Commit** (with message: "Add agentspecs to [filename]")
6. **Repeat**

After completing a project:

```bash
# Generate documentation
agentspec extract src/ --format markdown

# Commit the generated docs
git add agent_specs.md
git commit -m "Add extracted agentspec documentation"
```

Now all future agents (and humans) can read the full context before making changes.
