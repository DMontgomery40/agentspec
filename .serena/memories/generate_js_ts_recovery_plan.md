Diagnosis (generate JS/TS)
- generate.run collects only Python files via collect_python_files and ignores --language.
- process_file is Python-only (AST + insert_docstring_at_line), no JS/TS path.
- CLI prints generic “Done!” even when no files/candidates processed → misleading.
- Missing logging parity for non-Python paths; no per-file/candidate counts.

Plan to fix
1) Design language‑agnostic generate API
- Cross-language symbol model: {name, kind, lineno, has_doc, has_agentspec, source}.
- Discovery per language:
  • Python: reuse extract_function_info(require_agentspec/update_existing flags).
  • JS/TS: add symbol discovery using tree-sitter when available; fallback regex for function/class/const-arrow/exports.
- Filters: update_existing (include all) and require_agentspec (JSDoc with ---agentspec markers).
- Acceptance: For JS file lacking JSDoc, discovery returns symbol w/ correct line; honors flags.

2) Implement JS JSDoc insertion
- Use JavaScriptAdapter.insert_docstring(filepath, lineno, docstring) for narrative phase.
- When update_existing=True, adapter locates and replaces existing JSDoc (via _find_preceding_jsdoc).
- Support force_context: append a short console.log('[AGENTSPEC_CONTEXT] <fn>…') or a comment after insertion, behind flag.
- Two-phase write (narrative then deterministic): inject_deterministic_metadata(narrative, metadata, as_agentspec_yaml) and reinsert/replace JSDoc.
- Acceptance: For fixture JS function with/without docs, generate inserts or replaces a valid JSDoc and validates syntax.

3) Unify generate logging and --diff
- Use collect_source_files with --language filter:
  • auto → process .py + { .js, .mjs, .jsx, .ts, .tsx }
  • js → JS/TS only; py → Python only
- Per-file logging: “Processing <file>”, “Found N candidates”, per-symbol actions, dry-run notices.
- If zero files or zero candidates: print clear message before final summary.
- Apply diff_summary to both languages (append DIFF SUMMARY section to narrative).
- Acceptance: User sees detailed logs; no silent no-ops.

4) Add JS generate tests
- Introduce offline stub provider (provider='noop') or AGENTSPEC_GENERATE_STUB=1 to bypass network and return stub narrative.
- Tests:
  • Insert narrative+metadata into JS file without JSDoc (no network).
  • Update-existing replaces JSDoc.
  • force_context adds a console.log or comment marker.
  • Logging: stdout contains “Processing”, “Found”, “Done” lines; no-ops report correctly.
- Acceptance: Tests pass in CI without Anthropic/OpenAI or Ollama.

5) Update docs + agentspec
- README/CLI: JS/TS support for generate, --language behavior, offline stub provider.
- Agentspec updates for generate.run/process_file/new process_js_file noting guardrails and multi-language.

6) Full validation and release notes
- Run pytest; manual CLI checks:
  • agentspec generate tests/fixtures/javascript/imports-exports.js --dry-run --language js --provider noop
  • agentspec generate tests/fixtures/javascript/imports-exports.js --update-existing --language js --provider noop
  • agentspec generate tests/test_extract_javascript_agentspec.py --update-existing --force-context --language py --provider noop
- Draft release notes: multi-language generate, logging parity, diff support, tests.

Known risks / mitigations
- Tree-sitter missing → rely on regex discovery + adapter insert (with syntax validation); document optional deps.
- Over-matching regex → constrain to top-of-line patterns; cap lookahead lines after JSDoc; add tests.
- Logging noise → gate verbosity with --terse and use concise per-file summaries.
