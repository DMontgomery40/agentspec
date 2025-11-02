# Permanent Test Files for Agentspec

These are the canonical test files to use when validating agentspec functionality.
DO NOT create temporary files - ALWAYS use these real-world files for testing.

## TypeScript/TSX Tests
**File:** `/Users/davidmontgomery/faxbot_folder/faxbot/api/admin_ui/src/components/Dashboard.tsx`
- **Use for:** ALL TypeScript/TSX testing - generate, extract, lint, strip, --terse, --update-existing, --diff-summary, --strict, EVERYTHING
- Large real-world React component with TypeScript
- Has extensive git history for changelog testing

## Python Tests  
**File:** `/Users/davidmontgomery/faxbot_folder/faxbot/api/app/phaxio_service.py`
- **Use for:** ALL Python testing - generate, extract, lint, strip, --terse, --update-existing, --diff-summary, --strict, EVERYTHING
- Production Python file with dependencies and git history

## JavaScript Tests
**File:** `/Users/davidmontgomery/agro/gui/js/indexing.js`
- **Use for:** ALL JavaScript testing - generate, extract, lint, strip, --terse, --update-existing, --diff-summary, --strict, EVERYTHING
- Real production JavaScript file

## LLM Configuration

**ALWAYS use these parameters for testing:**
- **Provider:** `openai` (OpenAI-compatible API)
- **Base URL:** `http://localhost:11434/v1` (local Ollama)
- **Model:** `qwen3-coder:30b`
- **Mode:** `--update-existing` (ALWAYS, unless explicitly told to `--strip` first)

## Usage Rules

1. **NEVER create temp files** like `tmp_test.tsx`, `tmp_simple.js`, etc.
2. **ALWAYS use these files** when testing TypeScript, Python, or JavaScript functionality
3. **ALWAYS use qwen3-coder:30b via local Ollama** for all tests
4. **ALWAYS use --update-existing** (unless explicitly told to --strip first and start fresh)
5. **Use full absolute paths** - required for git history to work correctly
6. **Test against real output** - these files have actual git history and realistic code

## Test Commands

### TypeScript/TSX Test
```bash
cd /Users/davidmontgomery/agentspec
source .venv/bin/activate

# Test metadata collection
python3 -c "
from pathlib import Path
from agentspec.collect import collect_metadata

filepath = Path('/Users/davidmontgomery/faxbot_folder/faxbot/api/admin_ui/src/components/Dashboard.tsx')
func_name = 'Dashboard'

metadata = collect_metadata(filepath, func_name)
print(f'Changelog entries: {len(metadata.get(\"changelog\", []))}')
for entry in metadata.get('changelog', [])[:5]:
    print(entry)
"

# STANDARD test (update existing docstrings)
agentspec generate /Users/davidmontgomery/faxbot_folder/faxbot/api/admin_ui/src/components/Dashboard.tsx \
  --provider openai \
  --base-url http://localhost:11434/v1 \
  --model qwen3-coder:30b \
  --terse \
  --force-context \
  --agentspec-yaml \
  --update-existing

# FRESH START test (only when explicitly requested)
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

### Python Test
```bash
cd /Users/davidmontgomery/agentspec
source .venv/bin/activate

# Test metadata collection
python3 -c "
from pathlib import Path
from agentspec.collect import collect_metadata

filepath = Path('/Users/davidmontgomery/faxbot_folder/faxbot/api/app/phaxio_service.py')
func_name = 'send_fax'

metadata = collect_metadata(filepath, func_name)
print(f'Changelog entries: {len(metadata.get(\"changelog\", []))}')
for entry in metadata.get('changelog', [])[:5]:
    print(entry)
"

# STANDARD test (update existing docstrings)
agentspec generate /Users/davidmontgomery/faxbot_folder/faxbot/api/app/phaxio_service.py \
  --provider openai \
  --base-url http://localhost:11434/v1 \
  --model qwen3-coder:30b \
  --terse \
  --force-context \
  --agentspec-yaml \
  --update-existing

# FRESH START test (only when explicitly requested)
agentspec generate /Users/davidmontgomery/faxbot_folder/faxbot/api/app/phaxio_service.py \
  --provider openai \
  --base-url http://localhost:11434/v1 \
  --model qwen3-coder:30b \
  --terse \
  --force-context \
  --agentspec-yaml \
  --update-existing \
  --strip
```

### JavaScript Test
```bash
cd /Users/davidmontgomery/agentspec
source .venv/bin/activate

# Test metadata collection
python3 -c "
from pathlib import Path
from agentspec.collect import collect_metadata

filepath = Path('/Users/davidmontgomery/agro/gui/js/indexing.js')
func_name = 'indexData'

metadata = collect_metadata(filepath, func_name)
print(f'Changelog entries: {len(metadata.get(\"changelog\", []))}')
for entry in metadata.get('changelog', [])[:5]:
    print(entry)
"

# STANDARD test (update existing docstrings)
agentspec generate /Users/davidmontgomery/agro/gui/js/indexing.js \
  --provider openai \
  --base-url http://localhost:11434/v1 \
  --model qwen3-coder:30b \
  --terse \
  --force-context \
  --agentspec-yaml \
  --update-existing

# FRESH START test (only when explicitly requested)
agentspec generate /Users/davidmontgomery/agro/gui/js/indexing.js \
  --provider openai \
  --base-url http://localhost:11434/v1 \
  --model qwen3-coder:30b \
  --terse \
  --force-context \
  --agentspec-yaml \
  --update-existing \
  --strip
```

## Standard Test Command Template

**DEFAULT (update existing docstrings):**
```bash
agentspec generate <FILEPATH> \
  --provider openai \
  --base-url http://localhost:11434/v1 \
  --model qwen3-coder:30b \
  --terse \
  --force-context \
  --agentspec-yaml \
  --update-existing
```

**FRESH START (only when explicitly requested to strip first):**
```bash
agentspec generate <FILEPATH> \
  --provider openai \
  --base-url http://localhost:11434/v1 \
  --model qwen3-coder:30b \
  --terse \
  --force-context \
  --agentspec-yaml \
  --update-existing \
  --strip
```

## Why These Files?

- **Real git history**: Actual commit history for changelog testing
- **Production code**: Complex, real-world code paths
- **No cleanup needed**: No temp files to clean up
- **Reproducible**: Same files, same results every time
- **Real-world validation**: Tests against actual production complexity

## Symlinks

Reference symlinks exist in `/Users/davidmontgomery/agentspec/tests/`:
- `ref_Dashboard.tsx` → TypeScript/TSX file
- `ref_phaxio_service.py` → Python file
- `ref_indexing.js` → JavaScript file
