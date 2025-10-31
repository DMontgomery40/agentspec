/**
 * Data processor for handling incoming events.
 * 
 * ---agentspec
 * what: |
 *   Class that processes data events asynchronously.
 *   Stores processed results in an internal array and provides methods
 *   to query and clear the results.
 * 
 * deps:
 *   calls:
 *     - this.log
 *   imports:
 *     - EventEmitter
 * 
 * why: |
 *   Demonstrates class-based structure for tree-sitter JSDoc extraction.
 * 
 * guardrails:
 *   - DO NOT remove error handling in process()
 *   - DO NOT expose _results directly
 * 
 * changelog:
 *   - "2025-10-31: Initial class implementation"
 * ---/agentspec
 */
class DataProcessor {
  constructor() {
    this._results = [];
  }

  /**
   * Process an event asynchronously.
   */
  async process(event) {
    this.log('Processing event:', event);
    try {
      const result = await this.handleEvent(event);
      this._results.push(result);
      return result;
    } catch (error) {
      console.error('Error processing event:', error);
      throw error;
    }
  }

  /**
   * Get all results collected so far.
   */
  getResults() {
    return [...this._results];
  }

  /**
   * Internal helper to handle events.
   */
  async handleEvent(event) {
    // Simulate async work
    return new Promise(resolve => {
      setTimeout(() => resolve({ processed: true, event }), 100);
    });
  }

  log(...args) {
    console.log('[DataProcessor]', ...args);
  }
}

module.exports = DataProcessor;
