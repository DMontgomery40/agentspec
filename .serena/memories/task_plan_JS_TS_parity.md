High-level JS/TS parity plan executed:

1. Extend JavaScript adapter for .js, .mjs, .jsx, .ts, .tsx discovery
2. Add multi-language file discovery utility `collect_source_files`
3. Implement JS/TS extraction via JSDoc scanning and YAML parsing
4. Generalize CLI extract to Python + JS/TS (no path existence assumption)
5. Add JS/TS linter scanning JSDoc blocks for YAML and required keys
6. Improve JS metadata fallback (regex-based) when tree-sitter is absent
7. Add tests + fixtures for JS extraction and lint; keep metadata test passing without tree-sitter
8. Integrate ast-grep config and rule packs (safety, hygiene, agentspec, openai modernizations)
9. Minimal docs are already JS/TS-aware; readme already announces JS support

All tests pass (23/23). Optional extras `agentspec[javascript]` already defined for tree-sitter.
