# AI Slop Detection Patterns

## What is AI Slop?

AI slop is code that compiles/runs but is fundamentally wrong due to:
- AI predicting probable output vs actual requirements
- Loss of context during generation
- Hallucinated functions that look plausible but don't work
- Vibe coding - code that "feels right" but isn't

## Primary Detection Patterns

### 1. Stubs and Walking Skeletons

**Signs:**
- Functions with `pass`, `todo`, `NotImplementedError`
- Classes with only `__init__` defined
- Routes that return mock data or `{"status": "ok"}`
- Handlers that log but don't process

**Example:**
```python
class UserService:
    def authenticate(self, username: str, password: str) -> bool:
        # TODO: Implement actual authentication
        return True  # Always succeeds!
```

### 2. Multiple Abandoned Versions

**Signs:**
- `process_v1()`, `process_v2()`, `process_v3()` all exist
- `old_`, `new_`, `temp_` prefixes on functions
- Commented-out blocks of similar logic
- Multiple implementations of same interface

**Example:**
```javascript
// Original implementation
function fetchUserData(id) { ... }

// New implementation (never finished)
function fetchUserDataV2(id) {
  // TODO: Add caching
  return fetchUserData(id);
}

// Latest attempt (also abandoned)
async function fetchUserDataV3(id) {
  // Supposed to use GraphQL but falls back to v1
  return fetchUserData(id);
}
```

### 3. Documentation That Lies

**Signs:**
- Docstring says "validates input" but no validation exists
- JSDoc claims async but function is sync
- Comments reference removed parameters
- README describes features not in code

**Example:**
```typescript
/**
 * Validates email format and checks against blocklist.
 * Throws ValidationError if invalid.
 * @param email - Email address to validate
 * @returns true if valid
 */
function validateEmail(email: string): boolean {
  return email.includes('@');  // No blocklist check, never throws
}
```

### 4. Bridges to Nowhere

**Signs:**
- Functions called nowhere (dead code detection misses these if they're in interfaces)
- Classes instantiated but never used
- Imports for features that were removed
- Config options that don't affect behavior

**Example:**
```python
# In settings.py
ENABLE_ADVANCED_CACHING = True  # Added for feature that was never implemented

# In cache.py
def get_advanced_cache():
    # This was supposed to be the new caching system
    # But fell back to old system and never got finished
    return get_basic_cache()  # ENABLE_ADVANCED_CACHING ignored
```

### 5. Context-Loss Artifacts

**Signs:**
- Files in different states of refactor (some use new patterns, some old)
- Function signatures changed in some files but not others
- Type definitions out of sync with implementations
- Event handlers for events that don't exist anymore

**Example:**
```javascript
// api.js - updated to use fetch
export async function getData() {
  return fetch('/api/data');
}

// dashboard.js - still expects old XMLHttpRequest callback pattern
getData((error, data) => {  // getData doesn't take callbacks anymore!
  if (error) { ... }
});
```

### 6. Hallucinated Functions

**Signs:**
- Calls to functions that don't exist (but look like they should)
- Uses libraries incorrectly (methods that don't exist)
- Assumes APIs that aren't implemented
- References config that doesn't exist

**Example:**
```typescript
// AI hallucinated that stripe has a .validate() method
const payment = stripe.payments.validate(token);  // .validate() doesn't exist

// AI assumed a utility that was never written
const clean = sanitizeInput(userInput);  // sanitizeInput is not defined

// AI invented a config option
if (config.security.enableCSRF) {  // config.security doesn't have enableCSRF
  // ...
}
```

### 7. Vibe-Coded Security Flaws

**OWASP Top 10 to watch for:**

#### SQL Injection
```python
# Looks right, completely wrong
def get_user(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"  # Injection!
    return db.execute(query)
```

#### XSS (Cross-Site Scripting)
```javascript
// Looks like React, but dangerouslySetInnerHTML without sanitization
function UserProfile({ bio }) {
  return <div dangerouslySetInnerHTML={{ __html: bio }} />;  // XSS!
}
```

#### Insecure Deserialization
```python
import pickle

def load_session(session_data):
    return pickle.loads(session_data)  # Remote code execution!
```

#### Broken Authentication
```javascript
// Looks like auth, but stores password in localStorage
function login(username, password) {
  localStorage.setItem('password', password);  // NEVER store passwords client-side
  return api.login(username, password);
}
```

#### Missing Authorization Checks
```python
@app.route('/admin/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    # No check if requester is admin!
    User.delete(user_id)
    return {"status": "deleted"}
```

### 8. Bloated, Inefficient Patterns

**Signs:**
- Loops that could be replaced with built-ins
- Unnecessary intermediate variables
- Over-abstracted simple logic
- Premature optimization patterns

**Example:**
```javascript
// AI-generated bloat
function findUserById(users, targetId) {
  let result = null;
  let found = false;
  for (let i = 0; i < users.length; i++) {
    const user = users[i];
    if (user.id === targetId) {
      result = user;
      found = true;
      break;
    }
  }
  return found ? result : null;
}

// Should be:
// return users.find(u => u.id === targetId);
```

### 9. UI-Specific AI Slop

#### Missing Error States
```typescript
function UserProfile() {
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    fetchUser().then(setUser);  // No error handling, no loading state
  }, []);
  
  return <div>{user.name}</div>;  // Crashes if user is null
}
```

#### Event Handlers That Don't Work
```javascript
// AI hallucinated event names
<button onClick={handleClick}>  // onClick is correct
<input onValueChange={handleChange}>  // onValueChange doesn't exist! Should be onChange
<form onSubmission={handleSubmit}>  // onSubmission doesn't exist! Should be onSubmit
```

#### Broken React Patterns
```typescript
// AI doesn't understand React rules
function BadComponent() {
  if (someCondition) {
    useEffect(() => { ... });  // Hooks must be at top level!
  }
  
  return <div>...</div>;
}
```

#### CSS That Doesn't Apply
```javascript
// AI generated CSS-in-JS but forgot the template literal
const Button = styled.div`
  color: ${props.color};  // props is undefined, should be ${props => props.color}
  padding: 10px;
`;
```

#### Async UI Updates Without Suspense/Loading
```typescript
async function SearchResults({ query }) {  // Component can't be async!
  const results = await search(query);
  return <ul>{results.map(r => <li>{r}</li>)}</ul>;
}
```

### 10. Test Fabrication

**Signs:**
- Tests that always pass (mock everything)
- Tests that don't actually call the function
- Tests with hardcoded expected values
- Tests that "pass" but assert nothing

**Example:**
```python
def test_user_authentication():
    # AI fabricated this test
    result = True  # Doesn't actually call authenticate()
    assert result == True  # Always passes
```

## Detection Strategy

### Multi-File Context Required

To detect AI slop, you must:

1. **Read the function/class**
2. **Find what calls it** (is it actually used?)
3. **Find what it calls** (do those functions exist?)
4. **Check git history** (was this abandoned mid-refactor?)
5. **Compare documentation** (do docs match reality?)
6. **Look for siblings** (are there v1/v2/v3 versions?)

### Red Flags Checklist

- [ ] Function body is stub (pass, todo, NotImplementedError)
- [ ] Multiple versions exist (v1, v2, v3, old_, new_)
- [ ] Documentation doesn't match implementation
- [ ] Called nowhere (dead code)
- [ ] Calls non-existent functions (hallucination)
- [ ] Uses libraries incorrectly
- [ ] Security vulnerability (SQL injection, XSS, etc.)
- [ ] Bloated pattern that could be 1 line
- [ ] Missing error/loading states (UI)
- [ ] Wrong event handlers (UI)
- [ ] Tests that don't test anything

## Output Format

When documenting AI slop:

```yaml
what: |
  - L5: Stub implementation, returns hardcoded True without auth
  - L10: Calls nonexistent validate_token() (hallucination)
  - Multiple versions exist: authenticateV1, authenticateV2, authenticateV3
  - AI SLOP: Walking skeleton from abandoned OAuth refactor (git: commit abc123)

why: |
  Started as OAuth refactor in Q3 2024, abandoned mid-way. Now calls old
  session-based auth but pretends to be token-based. Documentation lies.

guardrails:
  - DO NOT trust this for production, it's a stub
  - DO NOT call validate_token(), it doesn't exist
  - NOTE: Security risk - always returns True (no actual authentication)
  - NOTE: Check git history for authenticateV3 - the real implementation
```

## Priority

Focus on AI slop FIRST, compile-time bugs SECOND.

Don't waste tokens explaining:
- TypeScript type errors (tsc catches these)
- Missing imports (build fails)
- Syntax errors (parser catches these)

DO explain:
- Code that compiles but is wrong
- Stubs masquerading as features
- Hallucinated functions
- Security vulnerabilities
- Documentation that lies
