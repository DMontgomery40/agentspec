# JavaScript Agentspec Style Guide

This guide documents how to write agentspec blocks in JavaScript/TypeScript files using JSDoc comments.

## Agentspec in JavaScript

Agentspec blocks in JavaScript files live inside JSDoc comments (`/** ... */`) immediately preceding the function or class definition.

### Basic Format

```javascript
/**
 * Brief one-line description of what this does.
 * 
 * ---agentspec
 * what: |
 *   Detailed multi-line explanation of the function's behavior,
 *   inputs, outputs, and edge cases.
 * 
 * deps:
 *   calls:
 *     - functionName
 *     - module.method
 *   imports:
 *     - import statement or require
 *   called_by:
 *     - otherModule.caller
 * 
 * why: |
 *   Explanation of why this implementation was chosen
 *   over alternatives, with rationale for design decisions.
 * 
 * guardrails:
 *   - DO NOT remove error handling without fixing async issues
 *   - DO NOT change Promise behavior to synchronous
 * 
 * changelog:
 *   - "2025-10-31: Initial implementation"
 *   - "2025-10-30: Fixed race condition in event loop"
 * ---/agentspec
 */
function myFunction(param) {
  // Implementation
}
```

## Key Formatting Rules

### 1. Indentation and Comments

- JSDoc lines must start with ` * ` (space-star-space)
- Maintain consistent indentation with the function/class being documented
- Close JSDoc blocks with ` */`

```javascript
/**
 * Function description
 * 
 * ---agentspec
 * what: | Multi-line content
 *   Line 1
 *   Line 2
 * ---/agentspec
 */
export function exportedFunction() { }
```

### 2. Multi-line YAML Fields

Use the pipe (`|`) character for multi-line YAML fields. Indent continuation lines by 2 spaces:

```javascript
/**
 * ---agentspec
 * what: |
 *   First line of description
 *   Second line (note: 2-space indent from 'what:')
 *   Third line
 * ---/agentspec
 */
```

### 3. List Format

For lists in YAML, use the dash format with proper indentation:

```javascript
/**
 * ---agentspec
 * guardrails:
 *   - DO NOT remove validation
 *   - DO NOT make this async
 * changelog:
 *   - "2025-10-31: Added retry logic"
 * ---/agentspec
 */
```

## Function Documentation Examples

### Simple Function

```javascript
/**
 * Calculates the sum of two numbers.
 * 
 * ---agentspec
 * what: |
 *   Pure function that adds two numbers and returns the result.
 *   Handles both integers and floats correctly.
 * 
 * deps:
 *   calls: []
 *   imports: []
 * 
 * why: |
 *   Simple arithmetic utility for common operations.
 * 
 * guardrails:
 *   - DO NOT add type coercion
 * 
 * changelog:
 *   - "2025-10-31: Initial implementation"
 * ---/agentspec
 */
export function add(a, b) {
  return a + b;
}
```

### Async Function

```javascript
/**
 * Fetch user data from API and parse response.
 * 
 * ---agentspec
 * what: |
 *   Async function that fetches user data from the remote API,
 *   handles errors, and returns parsed JSON.
 *   
 *   Throws NetworkError if fetch fails.
 *   Throws ParseError if JSON is malformed.
 * 
 * deps:
 *   calls:
 *     - fetch
 *     - response.json
 *   imports:
 *     - fetch (built-in)
 *   called_by:
 *     - handlers.getUserProfile
 * 
 * why: |
 *   Centralized async API client prevents duplicate
 *   error handling across multiple call sites.
 * 
 * guardrails:
 *   - DO NOT remove try/catch blocks
 *   - DO NOT make this synchronous
 * 
 * changelog:
 *   - "2025-10-31: Added timeout handling"
 * ---/agentspec
 */
export async function fetchUser(userId) {
  const response = await fetch(`/api/users/${userId}`);
  if (!response.ok) throw new Error('User not found');
  return response.json();
}
```

### Class Documentation

```javascript
/**
 * Manager for handling event subscriptions and dispatches.
 * 
 * ---agentspec
 * what: |
 *   Event emitter that maintains subscriptions and
 *   dispatches events to all registered listeners.
 *   
 *   Methods:
 *   - on(event, listener): Subscribe to event
 *   - off(event, listener): Unsubscribe from event
 *   - emit(event, data): Dispatch event to listeners
 * 
 * deps:
 *   calls:
 *     - Map methods
 *     - listener calls
 * 
 * why: |
 *   Custom event system provides loose coupling between
 *   components and simplifies testing through dependency injection.
 * 
 * guardrails:
 *   - DO NOT make this synchronous; async is required for proper event ordering
 *   - DO NOT remove listener cleanup; it prevents memory leaks
 * 
 * changelog:
 *   - "2025-10-31: Add EventEmitter class"
 * ---/agentspec
 */
export class EventEmitter {
  constructor() {
    this.events = new Map();
  }

  /**
   * Subscribe to an event.
   */
  on(event, listener) {
    if (!this.events.has(event)) {
      this.events.set(event, []);
    }
    this.events.get(event).push(listener);
  }

  /**
   * Emit an event to all subscribers.
   */
  emit(event, data) {
    if (!this.events.has(event)) return;
    for (const listener of this.events.get(event)) {
      listener(data);
    }
  }
}
```

## Common Patterns

### Arrow Functions

```javascript
/**
 * ---agentspec
 * what: |
 *   Pure function that doubles input value.
 * deps:
 *   calls: []
 * ---/agentspec
 */
export const double = (x) => x * 2;
```

### Higher-Order Functions

```javascript
/**
 * Creates a debounced version of a function.
 * 
 * ---agentspec
 * what: |
 *   Returns a function that delays execution until
 *   the specified milliseconds have passed without
 *   being called again. Useful for throttling rapid
 *   events like resize or search input.
 * 
 * deps:
 *   calls:
 *     - clearTimeout
 *     - setTimeout
 *   called_by:
 *     - components.handleSearch
 * 
 * guardrails:
 *   - DO NOT remove timeout tracking; required for debounce
 * ---/agentspec
 */
export function debounce(fn, delay) {
  let timeoutId = null;
  return function(...args) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), delay);
  };
}
```

## Common Mistakes to Avoid

### ❌ Incorrect Indentation

```javascript
// WRONG: JSDoc lines not indented properly
/**
 ---agentspec
 what: |
   Bad indentation
 ---/agentspec
*/
```

### ❌ Unmatched Delimiters

```javascript
// WRONG: Missing closing ---/agentspec
/**
 * ---agentspec
 * what: |
 *   Description here
 */
```

### ❌ Mixing YAML Formats

```javascript
// WRONG: Inconsistent YAML format
/**
 * ---agentspec
 * what: |
 *   Description
 * deps:
 *   calls: [func1, func2]  # ← Don't mix inline arrays with multi-line format
 *   imports:
 *     - module1
 * ---/agentspec
 */
```

## Best Practices

1. **Keep descriptions concise but complete** - Aim for 3-5 sentences per section
2. **List all dependencies** - Even seemingly obvious ones help future agents
3. **Document why, not what** - Comments should explain reasoning, not just repeat code
4. **Use guardrails liberally** - Encode production lessons as "DO NOT" statements
5. **Update changelog on modifications** - Include date and reason for each change
6. **Test parsing** - Run `agentspec lint src/` with `--language js` to validate

## Extraction and Linting

### Extract agentspecs from JavaScript

```bash
agentspec extract src/ --language js --format markdown
agentspec extract src/ --language js --format json
```

### Lint JavaScript agentspecs

```bash
agentspec lint src/ --language js --strict
```

### Auto-detect language (Python + JavaScript)

```bash
agentspec lint src/ --language auto
agentspec extract src/ --language auto
```

## Integration with Type Definitions

For TypeScript files or JSDoc with type annotations:

```typescript
/**
 * Validate and transform user input.
 * 
 * ---agentspec
 * what: |
 *   Validates input against schema and returns
 *   transformed object if valid, throws if not.
 * 
 * deps:
 *   calls:
 *     - validateSchema
 *     - transformData
 * 
 * why: |
 *   Centralized validation ensures consistent
 *   error messages and transformation logic.
 * ---/agentspec
 */
export function processUserData(input: UserInput): ProcessedUser {
  validateSchema(input);
  return transformData(input);
}
```

## Getting Help

For issues with JavaScript agentspec parsing:
1. Run `agentspec lint src/file.js --strict` for detailed error messages
2. Check that all `/**` have matching `*/`
3. Ensure YAML indentation is exactly 2 spaces
4. Verify the file has valid JavaScript syntax

For bugs or suggestions, see the project repository.
