# Reference Test Files

**IMPORTANT:** These symlinks point to REAL production files for testing agentspec.

## LLM Configuration for Tests

**ALWAYS use these parameters:**
- **Provider:** `openai`
- **Base URL:** `http://localhost:11434/v1`
- **Model:** `qwen3-coder:30b`
- **Mode:** `--update-existing` (default)
  - Only use `--strip` when explicitly told to start fresh

## DO NOT create temporary test files!

Instead, use these permanent reference files:

### TypeScript/TSX
- **Symlink:** `ref_Dashboard.tsx`
- **Target:** `/Users/davidmontgomery/faxbot_folder/faxbot/api/admin_ui/src/components/Dashboard.tsx`
- **Use for:** ALL TypeScript/TSX testing (generate, extract, lint, strip, --terse, --update-existing, --diff-summary, --strict, everything)

### Python
- **Symlink:** `ref_phaxio_service.py`
- **Target:** `/Users/davidmontgomery/faxbot_folder/faxbot/api/app/phaxio_service.py`
- **Use for:** ALL Python testing (generate, extract, lint, strip, --terse, --update-existing, --diff-summary, --strict, everything)

### JavaScript
- **Symlink:** `ref_indexing.js`
- **Target:** `/Users/davidmontgomery/agro/gui/js/indexing.js`
- **Use for:** ALL JavaScript testing (generate, extract, lint, strip, --terse, --update-existing, --diff-summary, --strict, everything)

## Why?

1. Real git history for changelog testing
2. Production code complexity for realistic testing
3. No temp files to clean up
4. Reproducible results

## Example Test Commands

### Default (Update Existing)
```bash
agentspec generate /Users/davidmontgomery/faxbot_folder/faxbot/api/admin_ui/src/components/Dashboard.tsx \
  --provider openai \
  --base-url http://localhost:11434/v1 \
  --model qwen3-coder:30b \
  --terse \
  --force-context \
  --agentspec-yaml \
  --update-existing
```

### Fresh Start (Only When Explicitly Requested)
```bash
agentspec generate /Users/davidmontgomery/faxbot_folder/faxbot/api/admin_ui/src/components/Dashboard.tsx \
  --provider openai \
  --base-url http://localhost:11434/v1 \
  --model qwen3-coder:30b \
  --terse \
  --force-context \
  --agentspec-yaml \
  --update-existing \
  --strip
```

## Memory

See `.serena/memories/permanent_test_files.md` for detailed usage instructions.
