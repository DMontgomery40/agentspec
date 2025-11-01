David — ast-grep is perfect for “guardrails + codemods” on **agentspec**. You can use it to:

1. enforce your spec & style (consistent tool names, no `print()`s in library code, argparse flags always have `help=...`),
2. catch dangerous patterns (`subprocess.run(..., shell=True)`, `os.system(...)`, `eval/exec`),
3. auto-migrate API usage (e.g., old OpenAI call shapes and `max_tokens` → `max_completion_tokens`),
4. make CI fail fast on spec drift.

Below is a drop-in “starter pack” tuned for your Python repo (I see `agentspec/cli.py`, `agentspec/llm.py`, `agentspec/generate.py`, plus `pyproject.toml` in your repo). Copy these files into the repo root and run the commands under “Run it”.

---

# 0) Install + (optional) alias

```bash
brew install ast-grep
```

(Optional alias if you prefer `ag` as the command name):

```bash
echo 'alias ag=sg' >> ~/.zshrc
exec zsh
```

---

# 1) Config (repo root)

**`sgconfig.yaml`**

```yaml
# ast-grep config for agentspec
ruleDirs:
  - sg/rules

# What files to scan
include:
  - agentspec/**/*.py
  - **/*.py

# Ignore typical build and venv output
ignore:
  - .git/**
  - .venv/**
  - venv/**
  - build/**
  - dist/**
  - __pycache__/**
```

Create the directory:

```bash
mkdir -p sg/rules
```

---

# 2) Rules — “Modern OpenAI” (migrations + papercuts)

These two catch common API breakage and nudge toward current patterns. They also show how you can auto-rewrite.

**`sg/rules/modern-openai.yml`**

```yaml
# Migrate deprecated Chat Completions -> Responses API
- id: openai-chat-to-responses
  message: "Use client.responses.create(...) instead of client.chat.completions.create(...)."
  severity: warning
  language: python
  rule:
    pattern: $CLIENT.chat.completions.create($$$ARGS)
  fix: $CLIENT.responses.create($$$ARGS)

# Rename max_tokens -> max_completion_tokens (for models that use the new param)
- id: openai-max-tokens-rename
  message: "Use 'max_completion_tokens=' instead of 'max_tokens='."
  severity: warning
  language: python
  rule:
    pattern: $CALL(max_tokens=$VAL, $$$REST)
  fix: $CALL(max_completion_tokens=$VAL, $$$REST)
```

> Tip: Run with `--fix` to apply the second rule automatically; keep the first as warning if you want to sanity-check before changing call shapes.

---

# 3) Rules — Safety hardening (command execution & code execution)

**`sg/rules/safety.yml`**

```yaml
# subprocess.run(..., shell=True) -> dangerous unless carefully sanitized
- id: dangerous-subprocess-shell-true
  message: "Avoid shell=True; prefer list args and shlex.split, and set check=True."
  severity: error
  language: python
  rule:
    pattern: subprocess.run($$ARGS, shell=True, $$$REST)

# os.system(...) is shell=True by definition
- id: os-system-shell
  message: "Avoid os.system(...); use subprocess.run([...], check=True)."
  severity: error
  language: python
  rule:
    pattern: os.system($$ARGS)

# eval(...) is almost never appropriate in library code
- id: ban-eval
  message: "Avoid eval(...); parse or map inputs safely."
  severity: error
  language: python
  rule:
    pattern: eval($$ARGS)

# exec(...) is dangerous and breaks introspection/typing
- id: ban-exec
  message: "Avoid exec(...); import/dispatch explicitly."
  severity: error
  language: python
  rule:
    pattern: exec($$ARGS)
```

---

# 4) Rules — Library hygiene (no prints, argparse flags must document themselves)

**`sg/rules/hygiene.yml`**

```yaml
# Disallow print(...) in library code (keeps CLI/logging consistent)
- id: no-print-in-library
  message: "Use logging instead of print(...)."
  severity: warning
  language: python
  rule:
    pattern: print($$ARGS)

# argparse: require help=... for every add_argument call
# This is intentionally broad; it flags arguments missing any help kwarg.
- id: argparse-require-help
  message: "Every argparse flag should include help= for CLI discoverability."
  severity: warning
  language: python
  rule:
    pattern: $PARSER.add_argument($$ARGS)
  constraints:
    # Flag the ones that *do not* include "help=" anywhere in the call text.
    # (ast-grep constraint on text is pragmatic and effective here)
    not:
      regex: "help\\s*="
```

---

# 5) Rules — Agentspec “consistency cops” (adjust to your taste)

You can use ast-grep to encode working agreements for your spec. Here are a few practical ones I recommend for agent/tool ecosystems:

**`sg/rules/agentspec.yml`**

```yaml
# Use logging best practice
- id: require-module-logger
  message: "Prefer a module-level logger: logger = logging.getLogger(__name__)."
  severity: info
  language: python
  rule:
    pattern: logging.getLogger(__name__)

# Ensure CLI entrypoint pattern exists in CLI modules
- id: cli-has-main
  message: "Prefer an explicit CLI entrypoint guarded by if __name__ == '__main__': main()."
  severity: info
  language: python
  rule:
    pattern: if __name__ == "__main__": $MAIN()

# For tool runners: discourage shell pipelines in f-strings (very easy injection footgun)
- id: discourage-shell-in-fstring
  message: "Avoid composing shell commands inside f-strings; pass argv as list to subprocess."
  severity: warning
  language: python
  rule:
    pattern: f"$CMD"
  constraints:
    regex: "\\b(;|\\|\\||\\|)\\b"

# (Optional) catch TODOs that ship
- id: no-leftover-todos
  message: "Resolve TODO before merge (or track in an issue)."
  severity: info
  language: python
  rule:
    pattern: "# TODO"
```

> Want deeper spec checks (e.g., “every tool has `name`, `description`, `schema`, `examples`”)? If you model tools as Python dataclasses or pydantic models, we can write rules that assert those attributes exist at the call sites that register them. If they live in JSON/YAML, ast-grep can target those formats too; we can add JSON/YAML rules next.

---

# 6) Run it

Scan (no changes):

```bash
sg scan -c sgconfig.yaml
```

Auto-fix only the safe, mechanical migration (param rename):

```bash
sg fix -c sgconfig.yaml --id openai-max-tokens-rename
```

Review all matches as JSON (for ad-hoc scripts or CI annotations):

```bash
sg scan -c sgconfig.yaml --json > sg-report.json
```

---

# 7) Wire it into pre-commit and CI

**`.pre-commit-config.yaml`**

```yaml
repos:
  - repo: local
    hooks:
      - id: ast-grep-scan
        name: ast-grep (scan)
        entry: sg scan -c sgconfig.yaml
        language: system
        pass_filenames: false
```

Install locally:

```bash
pip install pre-commit
pre-commit install
```

**`.github/workflows/ast-grep.yml`**

```yaml
name: ast-grep
on:
  pull_request:
    branches: [ main ]
  push:
    branches: [ main ]

jobs:
  ast-grep:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install ast-grep
        run: |
          curl -sSL https://raw.githubusercontent.com/ast-grep/ast-grep/main/install.sh | bash
          echo "$HOME/.local/bin" >> $GITHUB_PATH
      - name: Scan
        run: sg scan -c sgconfig.yaml
```

---

# 8) Where this concretely helps **agentspec**

* **Breakage proofing:** If anything reintroduces `client.chat.completions.create(...)` or `max_tokens=...`, CI flags it immediately.
* **Security posture:** Blocks the common gotchas (shell=True, os.system, eval/exec), which matter a lot for tool-calling agents.
* **CLI quality:** Every flag stays documented; `print()` can’t creep back into library paths.
* **Spec stability:** “Consistency cops” turn your informal rules into automated checks.
* **Codemods on demand:** You can add one-off rules to rewrite signatures, rename symbols, or refactor call sites across the repo in seconds.

If you want, I can extend this with JSON/YAML rules for your tool definitions (e.g., enforce `name/description/schema/examples` and kebab-case tool names), or add more codemods tailored to `agentspec/llm.py` once you decide what the “final” call shapes should be.
""""
Great prompt. Let’s wire the rest of that toolbelt directly into how you work on agentspec. I’ll keep it practical and repo-ready.

Quick wins you can run from the repo root
1) ripgrep (rg) — find the exact refactors you care about
# Find old OpenAI calls you want to eliminate
rg -n --hidden "client\\.chat\\.completions\\.create\\(" agentspec

# Find the deprecated param we want to migrate
rg -n --hidden "max_tokens\\s*=" agentspec

# Security checks you never want creeping in
rg -n --hidden "subprocess\\.run\\(.*shell\\s*=\\s*True" agentspec
rg -n --hidden "os\\.system\\(" agentspec
rg -n --hidden "\\beval\\(" agentspec
rg -n --hidden "\\bexec\\(" agentspec

# Argparse flags missing help= (rough cut)
rg -n --hidden "add_argument\\(" agentspec | rg -n -v "help\\s*="
2) fd + fzf + bat — lightning-fast “open the thing I’m thinking of”
# Browse Python files, preview with bat, open chosen file in $EDITOR
fd -t f -e py agentspec | fzf --preview 'bat --style=numbers --color=always {}'

# Grep-like live jump: pick a match, see it highlighted, press Enter to copy the path:line
rg --line-number --no-heading --color=always . agentspec \
| fzf --ansi --delimiter : \
      --preview 'bat --style=numbers --color=always --highlight-line {2} {1}'
3) ast-grep (sg) + jq — make spec drift visible at a glance
# JSON summary of rule hits (by rule id, sorted by count)
sg scan -c sgconfig.yaml --json \
| jq -r 'group_by(.id) | map({id: .[0].id, count: length}) 
         | sort_by(-.count)[] | "\(.count)\t\(.id)"'
4) eza — instant tree with git context
eza -T -L 2 --git
5) httpie — quick sanity checks for local/dev HTTP
# Example: ping a local service you’re iterating on
http GET http://127.0.0.1:8000/health
6) zoxide — jump back to the repo from anywhere
z agentspec
7) git-delta — make diffs readable (and fast to review)
git config --global core.pager "delta"
git config --global delta.navigate true
git config --global interactive.diffFilter "delta --color-only"
git config --global delta.syntax-theme "OneHalfDark"

Drop-in helper scripts (stick these in scripts/)
Run each cat once from repo root, then chmod +x the script. No placeholders—ready to paste.
A) Security + legacy API scan (scripts/scan_repo.sh)
mkdir -p scripts
cat > scripts/scan_repo.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

echo "== OpenAI (legacy) =="
rg -n --hidden "client\\.chat\\.completions\\.create\\(" agentspec || true
rg -n --hidden "max_tokens\\s*=" agentspec || true

echo
echo "== Dangerous exec/shell =="
rg -n --hidden "subprocess\\.run\\(.*shell\\s*=\\s*True" agentspec || true
rg -n --hidden "os\\.system\\(" agentspec || true
rg -n --hidden "\\beval\\(" agentspec || true
rg -n --hidden "\\bexec\\(" agentspec || true

echo
echo "== Argparse flags missing help= =="
rg -n --hidden "add_argument\\(" agentspec | rg -n -v "help\\s*=" || true

echo
echo "== ast-grep summary (if configured) =="
if command -v sg >/dev/null 2>&1 && [ -f "sgconfig.yaml" ]; then
  sg scan -c sgconfig.yaml --json \
  | jq -r 'group_by(.id) | map({id: .[0].id, count: length})
           | sort_by(-.count)[] | "\(.count)\t\(.id)"'
else
  echo "ast-grep not configured or sgconfig.yaml missing."
fi
EOF
chmod +x scripts/scan_repo.sh
B) Interactive code browser (scripts/browse.sh)
cat > scripts/browse.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
fd -t f -e py agentspec | fzf --preview 'bat --style=numbers --color=always {}'
EOF
chmod +x scripts/browse.sh
C) TODO/NOTE audit (scripts/todos.sh)
cat > scripts/todos.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
rg -n --hidden -e "\\bTODO\\b|\\bFIXME\\b|\\bNOTE\\b" agentspec || true
EOF
chmod +x scripts/todos.sh

Optional: tiny Makefile so your agents (and you) can call one-liners
cat > Makefile <<'EOF'
.PHONY: scan browse todos tree
scan:   ; scripts/scan_repo.sh
browse: ; scripts/browse.sh
todos:  ; scripts/todos.sh
tree:   ; eza -T -L 2 --git
EOF
Now you’ve got:
	•	rg to find the exact places you want to change,
	•	sg to enforce/fix them safely,
	•	jq to summarize drift,
	•	fzf + bat + fd to jump around code fast,
	•	eza for structure,
	•	httpie for quick HTTP probes,
	•	zoxide to jump to the repo,
	•	git-delta to make reviews pleasant.
If you want, I can open a PR that drops in scripts/, sgconfig.yaml, and the GitHub Action so it’s all live on the next commit.
