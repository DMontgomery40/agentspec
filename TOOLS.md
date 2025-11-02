---

## CLI Toolbelt


| Tool | What it is | Typical command(s) | Why it's an upgrade |
|------|------------|-------------------|---------------------|
| `fd` | Fast, user‑friendly file finder | `fd src`, `fd -e ts foo` | Simpler than find, respects .gitignore, very fast |
| `ripgrep` (`rg`) | Recursive code searcher | `rg "TODO"`, `rg -n --glob '!dist'` | Much faster than grep/ack/ag; great defaults |
| `ast-grep` (`sg`) | AST‑aware search & refactor | `sg -p 'if ($A) { $B }'` | Searches syntax, not text; precise refactors |
| `jq` | JSON processor | `jq '.items[].id' < resp.json` | Structured JSON queries, filters, transforms |
| `fzf` | Fuzzy finder (any list ➜ filtered) | `fzf`, <code>history &#124; fzf</code> | Interactive filtering for any command output |
| `bat` | cat with syntax, paging, git | `bat file.ts`, `bat -p README.md` | Syntax highlighting, line numbers, Git integration |
| `eza` | Modern ls | `eza -l --git`, `eza -T` | Better defaults, icons/trees/git info |
| `zoxide` | Smart cd (learns paths) | `z foo`, `zi my/project` | Jumps to dirs by frecency; fewer long paths |
| `httpie` (`http`) | Human‑friendly HTTP client | `http GET api/foo`, `http POST api bar=1` | Cleaner than curl for JSON; shows colors/headers |
| `git-delta` | Better git diff/pager | `git -c core.pager=delta diff` | Side‑by‑side, syntax‑colored diffs in terminal |

**Preferred defaults inside Codex**

Use rg for searching code and logs; fall back to grep only if needed.

Use fd for finding files; fall back to find only if needed.

Use jq to parse/pretty‑print JSON from APIs and logs.

Use httpie for ad‑hoc API exploration; use curl for fine‑grained CORS/DNS tests.

