# Verbose Docstring Generation (Clean - No Metadata Leakage)

You are documenting Python code by generating comprehensive docstrings designed for AI agent consumption. Your job is to describe what the code ACTUALLY does, even if it contains bugs or questionable design choices.

**CRITICAL: DO NOT ASSUME THE CODE IS CORRECT.**

## Output Format

Generate a docstring following this EXACT structure:

```
Brief one-line description.

WHAT THIS DOES:
- Detailed multi-line explanation of what the code ACTUALLY does
- Include specific line references when describing behavior
- Document bugs explicitly with line numbers
- Describe edge cases, error handling, return values
- Be specific about types and data flow

WHY THIS APPROACH:
- Explain the implementation rationale
- Document what this TRIES to do vs what it achieves
- Note design tradeoffs and alternatives
- Acknowledge if behavior seems intentional vs buggy

AGENT INSTRUCTIONS:
- DO NOT [specific things agents should not change, with explanations]
- ALWAYS [specific things agents must preserve, with explanations]
- NOTE: [critical warnings about this code]
```

## Instructions for "WHAT THIS DOES" Section

Describe what the code ACTUALLY does, not what it SHOULD do:

1. **Reference specific lines/variables** - Don't make vague claims
   - ✅ "Line 15 uses `>=` instead of `>`, causing..."
   - ❌ "The function validates the input"

2. **Document bugs and edge cases explicitly**
   - ✅ "No check for zero before division on line 22, will raise ZeroDivisionError when total_items is 0"
   - ❌ "Calculates a percentage"

3. **Don't hallucinate ideal behavior**
   - ✅ "Returns hardcoded value 0.25 regardless of income, state, or year parameters"
   - ❌ "Calculates tax rate based on income and state"

4. **Call out subtle off-by-one errors**
   - ✅ "range(max_attempts) on line 107 gives 2 retries instead of 3 (iterates 0,1,2)"
   - ❌ "Retries failed operations"

5. **Note comparison operator issues**
   - ✅ "Line 297 checks == 400, missing 401/403/500 errors"
   - ❌ "Handles API errors"

6. **Document silent failures**
   - ✅ "try/except with pass on line 238 silently ignores ValueError, creating data inconsistency"
   - ❌ "Handles errors gracefully"

## Examples of GOOD Documentation

### Example 1: Division by Zero Bug

<code>
def success_rate(self) -> float:
    return (len(self.successful) / self.total_items) * 100
</code>

✅ **GOOD:**
```
Calculates success rate as a percentage.

WHAT THIS DOES:
- Divides count of successful items by total items and multiplies by 100
- Returns float percentage (e.g., 75.0 for 75%)

BUG: No check for total_items == 0 before division on line 2. Will raise
ZeroDivisionError when:
- Called on empty batches
- total_items is initialized to 0
- All items removed but total_items not updated

WHY THIS APPROACH:
- Simple percentage calculation for reporting/metrics
- Assumes total_items is always positive (invalid assumption)
- Should use defensive check or property that validates state

AGENT INSTRUCTIONS:
- DO NOT remove the division operation, but DO add zero-check before it
- ALWAYS validate that total_items > 0 before calling this method
- NOTE: This will crash in production if called on empty data structures
```

❌ **BAD (hallucinated correctness):**
```
Safely calculates the success rate as a percentage.

WHAT THIS DOES:
- Computes the success rate from completed items
- Returns float between 0-100 representing percentage

WHY THIS APPROACH:
- Clean, efficient calculation
- Standard percentage formula

AGENT INSTRUCTIONS:
- DO NOT modify without testing
```

### Example 2: Off-by-One in Range

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
Attempts to split items into batches but contains off-by-one error.

WHAT THIS DOES:
- Iterates through items list using range with step of batch_size + 1
- Creates batches of size batch_size using slicing
- Returns list of batches

BUG: Line 3 uses step of `self.batch_size + 1` instead of `self.batch_size`.
This causes the loop to skip items between batches.

Concrete example with batch_size=50:
- Iteration 1: i=0, processes items[0:50] ✅
- Iteration 2: i=51, processes items[51:100] ❌ (skips item 50)
- Iteration 3: i=102, processes items[102:151] ❌ (skips item 101)
- Pattern: Items at indices 50, 101, 152, 203... are silently dropped

Impact: Data loss. For 1000 items with batch_size=50, approximately 20 items
are silently excluded from processing.

WHY THIS APPROACH:
- Attempts standard batch slicing pattern
- The +1 is a typo or misunderstanding of range() step parameter
- Should be range(0, len(items), self.batch_size)

AGENT INSTRUCTIONS:
- DO NOT assume batch sizes are flexible - this is a bug, not a feature
- ALWAYS use batch_size as step, never batch_size + 1
- NOTE: This has been silently losing data - check if downstream processes
  are missing records
```

### Example 3: Wrong Comparison Operator

<code>
def _handle_api_response(self, resp):
    if resp.status_code == 400:
        error_msg = resp.json().get("error", "Unknown error")
        raise Exception(f"API error: {error_msg}")
    return resp.json()
</code>

✅ **GOOD:**
```
Checks HTTP response and raises exception on API errors.

WHAT THIS DOES:
- Checks if status_code is exactly 400
- If 400, extracts error message from JSON and raises Exception
- Otherwise, returns response JSON

BUG: Line 2 uses == 400 instead of >= 400. Only catches exactly 400
(Bad Request), but silently ignores:
- 401 Unauthorized → returns data as if successful
- 403 Forbidden → returns data as if successful
- 404 Not Found → returns data as if successful
- 500 Internal Server Error → returns data as if successful
- All other 4xx and 5xx errors → treated as success

Impact: Caller receives error responses (HTML error pages, JSON error objects)
as if they were valid data, causing downstream parsing failures or incorrect
business logic execution.

WHY THIS APPROACH:
- Attempts to handle API errors
- Comparison operator is too restrictive
- Should check status_code >= 400 or use resp.raise_for_status()

AGENT INSTRUCTIONS:
- DO NOT change to checking multiple specific codes (== 400 or == 401 or ...)
- ALWAYS use >= 400 to catch entire 4xx and 5xx range
- NOTE: This is causing silent failures in production when API returns non-400 errors
```

### Example 4: Missing Await

<code>
async def download_file(self, file_id: str, output_path: Path):
    resp = await self.session.get(f"/files/{file_id}")
    content = resp.read()  # BUG: missing await
    output_path.write_bytes(content)
</code>

✅ **GOOD:**
```
Downloads a file and attempts to save to disk.

WHAT THIS DOES:
- Line 2: Awaits async GET request for file download
- Line 3: Calls resp.read() without await
- Line 4: Attempts to write content to file

BUG: Line 3 calls resp.read() without await. Since httpx (and aiohttp) responses
return coroutines for async reading, this assigns a coroutine object to `content`
instead of bytes.

Error sequence:
1. Line 3 executes without error (just creates coroutine object)
2. Line 4 fails with: "write_bytes() argument must be bytes, not coroutine"
3. Developer sees error at line 4, but actual bug is line 3

Impact: Function always crashes. Error message is misleading (points to line 4,
actual bug is line 3).

WHY THIS APPROACH:
- Correct pattern for async file download
- Missing await is a common async/await mistake
- Should be: content = await resp.read()

AGENT INSTRUCTIONS:
- DO NOT try to "fix" by converting write_bytes to async - that's not the issue
- ALWAYS add await before resp.read()
- NOTE: This function has never worked in production - check if it's actually called
```

### Example 5: Silent Error Swallowing

<code>
def _remove_from_cache(self, hash_key: str):
    try:
        idx = self._query_hashes.index(hash_key)
        del self._embeddings[idx]
        del self._query_hashes[idx]
    except ValueError:
        pass  # Hash not found in list
</code>

✅ **GOOD:**
```
Attempts to remove embedding and hash at matching index.

WHAT THIS DOES:
- Line 3: Finds index of hash_key in _query_hashes list
- Lines 4-5: Deletes entries at that index from both lists
- Lines 6-7: Silently ignores ValueError if hash_key not found

BUG: Lines 6-7 use bare `pass` in except block, silently swallowing ValueError
when hash_key is not found. This creates data structure inconsistency:

Timeline of corruption:
1. Caller deletes entry from cache dict (before calling this)
2. This method called to clean up _embeddings and _query_hashes
3. ValueError raised (hash not found)
4. Exception silently ignored via `pass`
5. Result: Cache dict has entry deleted, but _embeddings and _query_hashes still
   have stale entries

Impact: Over time, _embeddings and _query_hashes grow unbounded while cache gets
cleared, eventually causing:
- Memory leaks (growing lists never cleaned)
- Incorrect similarity matching (comparing against wrong embeddings)
- Index misalignment between _embeddings and _query_hashes

WHY THIS APPROACH:
- Attempts graceful handling of missing entries
- `pass` is too silent - should at least log warning
- Better design: validate hash_key exists before deletion, or use try/except
  with logging/re-raising

AGENT INSTRUCTIONS:
- DO NOT remove the try/except entirely (race conditions exist)
- ALWAYS add logging at minimum, ideally re-raise after cleanup
- NOTE: This is causing production memory leaks - _embeddings has 10x more entries
  than cache dict in monitoring
```

### Example 6: Boundary Condition Error

<code>
def _is_expired(self, entry: dict) -> bool:
    age_seconds = time.time() - entry["timestamp"]
    return age_seconds >= self.ttl_seconds
</code>

✅ **GOOD:**
```
Checks if cache entry has exceeded its time-to-live.

WHAT THIS DOES:
- Line 2: Calculates age by subtracting entry timestamp from current time
- Line 3: Returns True if age is greater than or equal to TTL

BUG: Line 3 uses >= instead of >. This causes entries to be considered expired
EXACTLY at TTL instead of AFTER TTL.

Concrete example with ttl_seconds=3600 (1 hour):
- Entry created at timestamp T
- At time T+3599.999: entry is valid ✅
- At time T+3600.000: entry is expired ❌ (should still be valid)
- At time T+3600.001: entry is expired ✅

Impact:
- Entries expire 1 unit too early (1 second for seconds, 1ms for milliseconds)
- For most use cases this is negligible
- Breaks tests expecting exact TTL boundaries
- Violates principle of least surprise (users expect "TTL=3600" means "valid for 3600 seconds")
- In high-frequency systems, causes premature cache misses

WHY THIS APPROACH:
- Standard TTL check pattern
- Comparison operator is off by one boundary
- Should use > for "expired after TTL" vs >= for "expired at or after TTL"
- Current behavior: "expired at exactly TTL"
- Desired behavior: "expired after TTL"

AGENT INSTRUCTIONS:
- DO NOT change to > without updating tests that may depend on current behavior
- ALWAYS document which boundary convention is used (inclusive vs exclusive)
- NOTE: This affects cache hit rates - investigate if 1-second-early expiration
  is causing measurable performance impact
```

### Example 7: Hardcoded Return Ignoring Parameters

<code>
def calculate_tax_rate(income: float, state: str, year: int) -> float:
    """Calculate tax rate based on income, state, and year."""
    if income > 0:
        base_rate = 0.25
    else:
        base_rate = 0.25
    return base_rate
</code>

✅ **GOOD:**
```
Returns a fixed tax rate regardless of input parameters.

WHAT THIS DOES:
- Lines 3-6: Checks if income > 0 and sets base_rate to 0.25 in both branches
- Line 7: Returns base_rate (always 0.25)
- Parameters state and year are completely ignored

BUGS:
1. Lines 3-6: Both if/else branches set base_rate to 0.25, making income check pointless
2. Line 7: Returns base_rate without using `state` or `year` parameters at all
3. Function signature promises state-specific and year-specific rates but delivers
   a flat 25% rate for all inputs

Test cases demonstrating bug:
- calculate_tax_rate(50000, "CA", 2024) → 0.25
- calculate_tax_rate(500000, "CA", 2024) → 0.25 (same rate for 10x income)
- calculate_tax_rate(50000, "TX", 2024) → 0.25 (same rate for different state)
- calculate_tax_rate(50000, "CA", 2020) → 0.25 (same rate for different year)

WHY THIS APPROACH:
- This is almost certainly a placeholder/stub implementation
- The signature suggests future state-specific and year-specific logic
- The pointless if/else suggests copy-paste or incomplete refactoring
- Real implementation would need tax tables keyed by (state, year, income_bracket)

AGENT INSTRUCTIONS:
- DO NOT assume this is correct and document it as "calculating tax rates"
- ALWAYS note this is a stub/placeholder when modifying
- NOTE: If this is in production, all tax calculations are wrong - using flat 25%
  instead of actual progressive/state-specific rates
```

## Instructions for "WHY THIS APPROACH" Section

Explain the implementation WITHOUT assuming it's correct:

1. **State what the code TRIES to do** (vs. what it achieves)
   - ✅ "Attempts to normalize phone numbers to E.164 format, but >= 10 adds + prefix to exactly 10-digit numbers too"
   - ❌ "Normalizes phone numbers to E.164 format"

2. **Document design tradeoffs**
   - ✅ "Uses simple string reversal for 'encryption' - this is clearly not cryptographic, likely a placeholder or test stub"
   - ❌ "Implements secure password encryption"

3. **Note if behavior seems intentional vs. buggy**
   - ✅ "The consistent 0.25 return suggests this is a stub/placeholder, not a bug - real tax logic not yet implemented"
   - ❌ "Efficiently calculates tax rates"

## Instructions for "AGENT INSTRUCTIONS" Section

List specific constraints with explanations:

✅ **GOOD:**
```
AGENT INSTRUCTIONS:
- DO NOT use this function when total_items might be 0, as it will raise ZeroDivisionError
- DO NOT rely on range(max_attempts) for retry logic, as it gives one fewer retry than intended
- DO NOT assume == 400 catches all API errors; it misses 401, 403, 500, etc.
- ALWAYS validate inputs before calling division operations
- ALWAYS use >= 400 for HTTP error checking, not == 400
- NOTE: The try/except pass is causing memory leaks in production
```

❌ **BAD (vague):**
```
AGENT INSTRUCTIONS:
- DO NOT modify without testing
- ALWAYS handle errors
- NOTE: Be careful with this code
```

## Context

<filepath>{filepath}</filepath>

<code>
{code}
</code>

## Remember

- Describe what code ACTUALLY does (even if buggy)
- Reference specific line numbers for all claims
- Document bugs explicitly with impact analysis
- Don't hallucinate ideal behavior
- Be comprehensive but truthful
