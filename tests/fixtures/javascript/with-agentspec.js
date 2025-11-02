/**
 * ---agentspec
 * what: |
 *   Example function with an agentspec block in JSDoc.
 *   Used for extraction and lint tests.
 * deps:
 *   calls: []
 *   called_by: []
 * why: |
 *   Ensures JS/TS parity for spec extraction.
 * guardrails:
 *   - DO NOT remove this fixture without adjusting tests
 * changelog:
 *   - "2025-11-01: Initial fixture"
 * ---/agentspec
 */
export function demo(x, y) {
  return x + y;
}

