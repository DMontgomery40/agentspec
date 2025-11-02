# AgentSpec YAML Block Generation 
You are documenting Python code by generating agentspec YAML blocks. Your job is to describe what the code ACTUALLY does, even if it contains bugs or questionable design choices.

**CRITICAL: DO NOT ASSUME THE CODE IS CORRECT.**

## Output Format

Output ONLY a YAML block fenced by these exact delimiters:

```
---agentspec
what: |
  (detailed explanation of what the code ACTUALLY does)
why: |
  (rationale for the implementation approach)
guardrails:
  - DO NOT ... (explain why)
  - ALWAYS ... (explain why)
---/agentspec
```

## Instructions for "what" Section

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
```python
def success_rate(self) -> float:
    return (len(self.successful) / self.total_items) * 100
```

✅ **GOOD:**
```yaml
what: |
  Calculates success rate as a percentage by dividing successful item count by total items.

  BUG: No check for total_items == 0 before division on line 2. Will raise ZeroDivisionError
  when called on empty batches or when total_items is initialized to 0.

  Returns: float percentage (e.g., 75.0 for 75%)
```

❌ **BAD (hallucinated correctness):**
```yaml
what: |
  Safely calculates the success rate as a percentage of completed items.
  Returns: float between 0-100
```

### Example 2: Off-by-One in Range
```python
def _create_batches(self, items):
    batches = []
    for i in range(0, len(items), self.batch_size + 1):
        batch = items[i:i + self.batch_size]
        batches.append(batch)
    return batches
```

✅ **GOOD:**
```yaml
what: |
  Attempts to split items into batches but contains off-by-one error.

  BUG: Line 3 uses step of `self.batch_size + 1` instead of `self.batch_size`.
  This causes the loop to skip items between batches. For batch_size=50, it iterates
  at i=0, 51, 102, 153... missing items at indices 50, 101, 152, etc.

  Example: [0-49] processed, [50] SKIPPED, [51-100] processed, [101] SKIPPED
```

❌ **BAD (hallucinated correctness):**
```yaml
what: |
  Splits a list of items into fixed-size batches for processing.
  Uses efficient slicing to create sublists.
```

### Example 3: Wrong Comparison Operator
```python
if resp.status_code == 400:
    raise Exception(f"API error: {error_msg}")
```

✅ **GOOD:**
```yaml
what: |
  Checks HTTP response status and raises exception on errors.

  BUG: Line 1 uses == 400 instead of >= 400. Only catches exactly 400 (Bad Request),
  but misses:
  - 401 Unauthorized
  - 403 Forbidden
  - 404 Not Found
  - 500 Internal Server Error
  - All other 4xx and 5xx errors

  This causes silent failures when API returns non-400 error codes.
```

❌ **BAD (hallucinated correctness):**
```yaml
what: |
  Handles API errors by checking the status code and raising appropriate exceptions.
```

### Example 4: Missing Await
```python
async def download_file(self, file_id: str, output_path: Path):
    resp = await session.get(f"/files/{file_id}")
    content = resp.read()  # BUG: missing await
    output_path.write_bytes(content)
```

✅ **GOOD:**
```yaml
what: |
  Downloads a file and saves to disk.

  BUG: Line 3 calls resp.read() without await. Since httpx responses return coroutines
  for async reading, this will assign a coroutine object to `content` instead of bytes.
  Line 4 will then fail with "write_bytes() argument must be bytes, not coroutine".

  Runtime error: TypeError at line 4, not line 3 where the actual bug is.
```

❌ **BAD (hallucinated correctness):**
```yaml
what: |
  Asynchronously downloads a file from the API and saves it to the specified path.
  Properly handles async operations.
```

### Example 5: Silent Error Swallowing
```python
try:
    idx = self._query_hashes.index(hash_key)
    del self._embeddings[idx]
    del self._query_hashes[idx]
except ValueError:
    pass  # Hash not found in list
```

✅ **GOOD:**
```yaml
what: |
  Attempts to remove embedding and hash at matching index.

  BUG: Lines 5-6 use bare `pass` in except block, silently ignoring ValueError when
  hash_key is not found in _query_hashes. This creates data inconsistency:
  - Cache dict has entry deleted
  - But embeddings list still has stale entry
  - And query_hashes list still has stale hash

  Over time, this causes _embeddings and _query_hashes to grow unbounded while
  cache gets cleared, eventually causing memory leaks and incorrect similarity matching.
```

❌ **BAD (hallucinated correctness):**
```yaml
what: |
  Safely removes entries from the cache, embeddings, and hashes lists.
  Gracefully handles missing entries without crashing.
```

### Example 6: Boundary Condition Error
```python
def _is_expired(self, entry):
    age_seconds = time.time() - entry["timestamp"]
    return age_seconds >= self.ttl_seconds
```

✅ **GOOD:**
```yaml
what: |
  Checks if cache entry has exceeded its time-to-live.

  BUG: Line 3 uses >= instead of >. This causes entries to be considered expired
  EXACTLY at TTL instead of AFTER TTL. For TTL=3600, an entry created at timestamp
  T will expire at T+3600.000 instead of T+3600.001.

  Impact: Entries expire 1 second (or 1 unit) too early. For most use cases this is
  negligible, but breaks tests expecting exact TTL boundaries and violates principle
  of least surprise (users expect "TTL=3600" means "valid for 3600 seconds").
```

❌ **BAD (hallucinated correctness):**
```yaml
what: |
  Determines if a cache entry has expired based on TTL configuration.
  Calculates age and compares to threshold.
```

### Example 7: Hardcoded Return Ignoring Parameters
```python
def calculate_tax_rate(income: float, state: str, year: int) -> float:
    if income > 0:
        base_rate = 0.25
    else:
        base_rate = 0.25
    return base_rate  # state and year completely ignored
```

✅ **GOOD:**
```yaml
what: |
  Returns a fixed tax rate of 0.25 (25%) regardless of input parameters.

  BUGS:
  1. Lines 2-5: Both branches set base_rate to 0.25, making income check pointless
  2. Line 6: Returns base_rate without using `state` or `year` parameters at all
  3. Function signature promises state-specific and year-specific rates but delivers
     a flat 25% rate for all inputs

  This is either a placeholder implementation or a serious logic error. The function
  accepts parameters it completely ignores.
```

❌ **BAD (hallucinated correctness):**
```yaml
what: |
  Calculates the tax rate based on income level, state jurisdiction, and tax year.
  Uses a base rate calculation with adjustments for different scenarios.
```

## Instructions for "why" Section

Explain the implementation approach WITHOUT assuming it's correct:

1. **State what the code TRIES to do** (vs. what it achieves)
   - ✅ "Attempts to normalize phone numbers to E.164 format, but >= 10 adds + prefix to exactly 10-digit numbers too"
   - ❌ "Normalizes phone numbers to E.164 format"

2. **Document design tradeoffs**
   - ✅ "Uses simple string reversal for 'encryption' - this is clearly not cryptographic, likely a placeholder or test stub"
   - ❌ "Implements secure password encryption"

3. **Note if behavior seems intentional vs. buggy**
   - ✅ "The consistent 0.25 return suggests this is a stub/placeholder, not a bug - real tax logic not yet implemented"
   - ❌ "Efficiently calculates tax rates"

## Instructions for "guardrails" Section

List what NOT to do, WITH EXPLANATIONS:

✅ **GOOD:**
```yaml
guardrails:
  - DO NOT use this function when total_items might be 0, as it will raise ZeroDivisionError
  - DO NOT rely on range(max_attempts) for retry logic, as it gives one fewer retry than intended
  - DO NOT assume == 400 catches all API errors; it misses 401, 403, 500, etc.
```

❌ **BAD (vague):**
```yaml
guardrails:
  - DO NOT modify without testing
  - ALWAYS handle errors
```

## Context

Function to document:
```python
{code}
```

File path: {filepath}

## Remember

- Describe what code ACTUALLY does (even if buggy)
- Reference specific line numbers for claims
- Document bugs explicitly
- Don't hallucinate ideal behavior
- Be comprehensive but truthful
