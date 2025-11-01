/**
 * Arrow function examples demonstrating modern JavaScript syntax.
 */

/**
 * Calculate factorial recursively using arrow function.
 * 
 * ---agentspec
 * what: |
 *   Recursive factorial calculator using arrow function syntax.
 *   Demonstrates modern ES6 syntax.
 * 
 * deps:
 *   calls: []
 *   imports: []
 * 
 * why: |
 *   Shows tree-sitter handling of arrow function nodes.
 * 
 * guardrails:
 *   - DO NOT remove base case check
 * 
 * changelog:
 *   - "2025-10-31: Arrow function test case"
 * ---/agentspec
 */
const factorial = (n) => {
  if (n <= 1) return 1;
  return n * factorial(n - 1);
};

/**
 * Higher-order function that returns a multiplier.
 */
const createMultiplier = (factor) => (value) => value * factor;

/**
 * Array mapping with arrow functions.
 */
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(n => n * 2);
const filtered = numbers.filter(n => n % 2 === 0);

module.exports = { factorial, createMultiplier, doubled, filtered };
