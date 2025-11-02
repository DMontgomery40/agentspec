# Terse Docstring Generation (Clean - No Metadata Leakage)

You are documenting Python code with concise docstrings for AI agent consumption. Your job is to describe what the code ACTUALLY does, even if it contains bugs.

**CRITICAL: DO NOT ASSUME THE CODE IS CORRECT.**

## Output Format

Generate a terse docstring following this EXACT structure:

```
Brief one-line description.

WHAT: Concise explanation of what this ACTUALLY does. Document bugs with line numbers.

WHY: Why this implementation approach. Note if placeholder/buggy.

GUARDRAILS:
- DO NOT ... (specific constraint with reason)
- ALWAYS ... (specific requirement with reason)
```

## Core Principles

1. **Reference specific lines for bugs**
   - ✅ "L15: uses >= instead of >, causes X"
   - ❌ "Validates input"

2. **Document bugs explicitly**
   - ✅ "BUG L22: No zero-check before division, raises ZeroDivisionError"
   - ❌ "Calculates percentage"

3. **Don't hallucinate ideal behavior**
   - ✅ "Returns hardcoded 0.25, ignores state/year params"
   - ❌ "Calculates state-specific tax rate"

## Examples

### Example 1: Division by Zero

<code>
def success_rate(self) -> float:
    return (len(self.successful) / self.total_items) * 100
</code>

✅ **GOOD:**
```
Calculates success rate percentage.

WHAT: Divides successful count by total_items, multiplies by 100. BUG L2: No check for total_items==0, raises ZeroDivisionError on empty batches.

WHY: Simple percentage calc. Assumes total_items always positive (invalid assumption).

GUARDRAILS:
- DO NOT call when total_items might be 0 (crashes)
- ALWAYS add zero-check before division
```

❌ **BAD:**
```
Safely calculates success rate.

WHAT: Computes success percentage from completed items.

WHY: Standard percentage formula.

GUARDRAILS:
- DO NOT modify without testing
```

### Example 2: Off-by-One Error

<code>
def _create_batches(self, items):
    batches = []
    for i in range(0, len(items), self.batch_size + 1):
        batch = items[i:i + self.batch_size]
        batches.append(batch)
    return batches
</code>

✅ **GOOD:**
```
Splits items into batches (buggy).

WHAT: BUG L3: Uses step batch_size+1 instead of batch_size. Skips items between batches (e.g., indices 50, 101, 152 with batch_size=50). Silent data loss.

WHY: Attempts standard batching. The +1 is typo/misunderstanding of range() step.

GUARDRAILS:
- DO NOT assume flexible batch sizes - this is a bug
- ALWAYS use batch_size as step, never batch_size+1
```

### Example 3: Wrong Comparison Operator

<code>
def _handle_response(self, resp):
    if resp.status_code == 400:
        raise Exception(f"API error: {resp.json().get('error')}")
    return resp.json()
</code>

✅ **GOOD:**
```
Checks HTTP response, raises on errors.

WHAT: BUG L2: Uses ==400 instead of >=400. Only catches 400, silently ignores 401/403/404/500 errors. Caller receives error HTML/JSON as valid data.

WHY: Attempts error handling. Comparison too restrictive. Should check >=400.

GUARDRAILS:
- DO NOT check multiple specific codes (==400 or ==401...)
- ALWAYS use >=400 to catch all 4xx/5xx
```

### Example 4: Missing Await

<code>
async def download_file(self, file_id: str, output_path: Path):
    resp = await self.session.get(f"/files/{file_id}")
    content = resp.read()
    output_path.write_bytes(content)
</code>

✅ **GOOD:**
```
Downloads file and saves to disk (broken).

WHAT: BUG L3: Missing await on resp.read(). Assigns coroutine object to content instead of bytes. L4 crashes with "write_bytes() argument must be bytes, not coroutine".

WHY: Correct async pattern except missing await. Error at L4 but bug is L3.

GUARDRAILS:
- DO NOT make write_bytes async - that's not the bug
- ALWAYS await resp.read()
```

### Example 5: Silent Error Swallowing

<code>
def _remove_from_cache(self, hash_key: str):
    try:
        idx = self._query_hashes.index(hash_key)
        del self._embeddings[idx]
        del self._query_hashes[idx]
    except ValueError:
        pass
</code>

✅ **GOOD:**
```
Removes embedding/hash at matching index.

WHAT: BUG L6-7: Bare pass silently ignores ValueError when hash_key not found. Creates data inconsistency: cache dict deleted but _embeddings/_query_hashes keep stale entries. Causes memory leaks and wrong similarity matches.

WHY: Attempts graceful error handling. Too silent - should log/re-raise.

GUARDRAILS:
- DO NOT remove try/except (race conditions exist)
- ALWAYS add logging minimum, ideally re-raise
```

### Example 6: Boundary Condition

<code>
def _is_expired(self, entry: dict) -> bool:
    age = time.time() - entry["timestamp"]
    return age >= self.ttl_seconds
</code>

✅ **GOOD:**
```
Checks if cache entry exceeded TTL.

WHAT: BUG L3: Uses >= instead of >. Entries expire AT ttl_seconds instead of AFTER. With TTL=3600, entry at T expires at T+3600.000 not T+3600.001. Expires 1 unit too early.

WHY: Standard TTL check. Comparison off by one boundary. Should use >.

GUARDRAILS:
- DO NOT change without updating tests expecting current behavior
- ALWAYS document boundary convention (inclusive vs exclusive)
```

### Example 7: Hardcoded Return

<code>
def calculate_tax_rate(income: float, state: str, year: int) -> float:
    if income > 0:
        base_rate = 0.25
    else:
        base_rate = 0.25
    return base_rate
</code>

✅ **GOOD:**
```
Returns fixed tax rate (placeholder).

WHAT: BUG: Returns hardcoded 0.25 regardless of income/state/year. Both if/else branches set 0.25. Parameters completely ignored. Likely stub/placeholder.

WHY: Signature suggests future state-specific logic. Incomplete implementation.

GUARDRAILS:
- DO NOT assume this is correct production logic
- ALWAYS note this is placeholder when modifying
```

## Context

<filepath>{filepath}</filepath>

<code>
{code}
</code>

## Remember

- Describe ACTUAL behavior (bugs and all)
- Reference line numbers for all bug claims
- Don't hallucinate ideal behavior
- Be concise but truthful
