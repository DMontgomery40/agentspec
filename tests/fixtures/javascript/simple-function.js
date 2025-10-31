/**
 * Calculates the sum of two numbers.
 * 
 * ---agentspec
 * what: |
 *   Simple addition function that takes two numbers and returns their sum.
 *   Handles only numeric inputs; no validation of input types.
 * 
 * deps:
 *   calls:
 *     - console.log
 *   imports: []
 * 
 * why: |
 *   Basic arithmetic operation used as example for tree-sitter extraction.
 * 
 * guardrails:
 *   - DO NOT remove the parameter validation
 *   - DO NOT change the return type
 * 
 * changelog:
 *   - "2025-10-31: Initial implementation"
 * ---/agentspec
 */
function add(a, b) {
  console.log('Adding:', a, b);
  return a + b;
}

/**
 * Multiplies two numbers together.
 */
function multiply(x, y) {
  return x * y;
}

module.exports = { add, multiply };
