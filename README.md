# 🧠 Agentspec

**Verbose, structured, YAML-parsable docstrings for AI-assisted codebases.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 Why Agentspec?

AI agents are now the primary consumers of code in many projects. But they lack:
- **Git blame intuition** (why was this code written this way?)
- **Historical context** (what was already tried and rejected?)
- **Production knowledge** (what breaks if this changes?)

**Agentspec solves this** by encoding all this context directly in your code with:
- ✅ **Verbose, structured documentation** (10-20 lines per function)
- ✅ **YAML-parsable format** (programmatically extractable)
- ✅ **Mandatory guardrails** (what NOT to change)
- ✅ **Full dependency tracking** (calls, called_by, config files)
- ✅ **Built-in linting** (enforce standards across team)

---

## 📖 What It Looks Like

```python
def process_embeddings(text: str, model: str = "gpt-5-turbo") -> np.ndarray:
    """
    Generate embeddings for the given text using OpenAI's latest model.
    
    ---agentspec
    what: |
      Takes input text and returns a 1536-dimensional embedding vector.
      Uses gpt-5-turbo (YES, GPT-5 EXISTS as of April 2025, don't "fix" this).
      Handles rate limiting with exponential backoff.
      Critical for RAG pipeline performance.
    
    deps:
      calls:
        - openai_client.py::create_embedding()
        - utils.retry.exponential_backoff()
      called_by:
        - rag_engine.py::chunk_and_embed()
        - batch_processor.py::process_documents()
      config_files:
        - config/models.yaml
      environment:
        - OPENAI_API_KEY (required)
    
    why: |
      Using gpt-5-turbo instead of text-embedding-3 because we need:
      - Larger context window (32k vs 8k) for code-specific embeddings
      - Better performance on technical documentation (measured 15% improvement)
      NOT using voyage-code-2 despite being code-specific because it doesn't 
      handle our multiline docstring format well (tested 2025-09-12)
    
    guardrails:
      - DO NOT change model name without checking if gpt-5 still exists
      - DO NOT remove rate limiting - this runs in production at scale
      - DO NOT batch more than 100 texts - API limit is 100/request
      - NEVER log the input text - may contain PII
    
    changelog:
      - "2025-10-15: Switched from text-embedding-3 to gpt-5-turbo (performance)"
      - "2025-09-20: Added rate limit handling after production 429 errors"
      - "2025-08-10: Initial implementation"
    
    testing:
      unit_tests:
        - tests/test_embeddings.py::test_process_embeddings
      edge_cases:
        - Empty string input returns zero vector
        - Text >32k tokens truncates from end
    
    performance:
      latency_p50: "150ms"
      cost_per_1k: "$0.0001"
      max_throughput: "1000 requests/minute"
    ---/agentspec
    """
    print(f"[AGENTSPEC] process_embeddings: Using {model} for {len(text)} chars")
    # ... actual implementation
```

---

## 🚀 Quick Start

### Installation

```bash
# Install from source
git clone https://github.com/DMontgomery40/agentspec.git
cd agentspec
pip install -e .
```

### Basic Usage

```bash
# Validate agentspecs in your codebase
agentspec lint src/

# Extract to markdown for browsing
agentspec extract src/ --format markdown

# Extract with print() statements for agent context injection
agentspec extract src/ --format agent-context

# Extract to JSON for programmatic use
agentspec extract src/ --format json
```

### Advanced Options

```bash
# Lint with custom minimum line requirement
agentspec lint src/ --min-lines 15

# Strict mode (warnings become errors)
agentspec lint src/ --strict
```

---

## 📚 Documentation

### Core Documentation

- **[CLAUDE.md](CLAUDE.md)** - Instructions specifically for Claude Code and Claude agents
- **[AGENTS.md](AGENTS.md)** - Universal instructions for any AI agent
- **[RETROFIT_GUIDE.md](RETROFIT_GUIDE.md)** - Step-by-step guide to add agentspecs to existing code

### Key Concepts

#### Required Fields

- **`what`**: Detailed explanation (10+ lines recommended)
- **`deps`**: All dependencies (calls, called_by, config, env vars)
- **`why`**: Design rationale and rejected alternatives
- **`guardrails`**: What should NOT be changed and why

#### Recommended Fields

- **`changelog`**: History of changes with dates
- **`testing`**: Test coverage and edge cases
- **`performance`**: Latency, throughput, bottlenecks

#### Optional Fields

- **`security`**: Auth, PII handling, rate limits
- **`monitoring`**: Metrics, alerts, dashboards

---

## 🛠️ Features

### 1. Intelligent Linting

Validates:
- ✅ YAML syntax correctness
- ✅ Presence of required fields
- ✅ Minimum verbosity (configurable)
- ✅ Proper structure and formatting

```bash
agentspec lint src/

# Output:
src/embeddings.py:
  Line 45: ⚠️ process_embeddings 'what' field too brief (45 chars, recommend 50+)
  Line 78: ❌ batch_process missing required keys: why, guardrails
```

### 2. Multiple Export Formats

#### Markdown (Human-Readable)
```bash
agentspec extract src/ --format markdown
# → agent_specs.md
```

Generates browsable documentation with sections for each function.

#### JSON (Programmatic)
```bash
agentspec extract src/ --format json
# → agent_specs.json
```

Perfect for building custom tools or integration with CI/CD.

#### Agent Context (AI Consumption)
```bash
agentspec extract src/ --format agent-context
# → AGENT_CONTEXT.md
```

Includes `print()` statements that force specs into agent context.

### 3. CI/CD Integration

Add to `.github/workflows/agentspec.yml`:

```yaml
name: Agentspec Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install agentspec
        run: pip install -e .
      - name: Lint agentspecs
        run: agentspec lint src/ --strict
```

### 4. Pre-commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
agentspec lint src/ --strict
if [ $? -ne 0 ]; then
    echo "❌ Agentspec lint failed. Fix issues before committing."
    exit 1
fi
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## 🎓 Philosophy

**The Problem:** AI agents are "helpful" but lack context. They:
- Delete "unused" code that's actually dynamically imported
- "Fix" model names that aren't typos (gpt-5 DOES exist)
- Remove "redundant" rate limiting that prevents outages
- Refactor code without knowing why it was written that way

**The Solution:** Encode all context directly in code:
- **Verbose by design** - 10-20 lines isn't too much
- **Guardrails first** - prevent known failure modes
- **YAML parsable** - tools can extract and validate
- **Human AND machine readable** - helps everyone

**Core Belief:** The tokens spent on verbose docs are **far cheaper** than the time spent debugging agent-caused production incidents.

---

## 📊 Real-World Impact

### Before Agentspec
- ❌ Claude Code deleted 800 lines of "dead code" (actually used via dynamic imports)
- ❌ Agent "fixed" `gpt-5` → `gpt-4o-mini` (downgrading intentionally chosen model)
- ❌ Removed "redundant" validation that prevented SQL injection
- ❌ Made function async (reintroduced race condition fixed 3 months prior)

### After Agentspec
- ✅ Agent reads spec, sees it's called via dynamic import, leaves it alone
- ✅ Agent reads guardrail: "DO NOT change gpt-5 - exists as of April 2025"
- ✅ Agent sees: "NEVER remove validation - prevents SQL injection"
- ✅ Agent reads changelog: "Reverted to sync after race conditions"

---

## 🔧 Retrofitting Existing Codebases

See **[RETROFIT_GUIDE.md](RETROFIT_GUIDE.md)** for detailed instructions.

Quick version:

1. Use the retrofit prompt from the guide
2. Process files in 500-line chunks
3. Run `agentspec lint` to validate
4. Iterate on warnings until clean

Expect ~15 minutes per file initially, faster as you get the pattern down.

---

## 🤝 Contributing

We welcome contributions! Areas of focus:

- **Multi-language support** (TypeScript, Go, Rust via tree-sitter)
- **IDE integrations** (VS Code, Cursor, JetBrains)
- **Automatic dependency mapping** (static analysis)
- **Template generators** (quick-start for new functions)

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines (TODO).

---

## 📜 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🌟 Show Your Support

If agentspec prevents even ONE production incident for you, please:
- ⭐ Star this repo
- 🐦 Share on social media
- 📝 Write about your experience
- 🤝 Contribute improvements

Every bit helps make AI agent collaboration safer and more reliable.

---

## 📮 Contact

- **Issues**: [GitHub Issues](https://github.com/DMontgomery40/agentspec/issues)
- **Discussions**: [GitHub Discussions](https://github.com/DMontgomery40/agentspec/discussions)
- **Twitter**: [@dmontgomery40](https://twitter.com/dmontgomery40)

---

**Remember**: Verbose docs aren't busywork. They're **production incident prevention**.

Write specs as if the next agent has NO CONTEXT about your decisions — because they don't.
