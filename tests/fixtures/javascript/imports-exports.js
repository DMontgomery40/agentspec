/**
 * Module demonstrating various import and export patterns.
 */

import { readFile, writeFile } from 'fs/promises';
import path from 'path';
import express, { Router } from 'express';
const { config } = require('./config');
const logger = require('./logger');

/**
 * Handler for processing files.
 */
export async function processFile(filepath) {
  const content = await readFile(filepath, 'utf8');
  return content.trim();
}

/**
 * """
 * Creates an Express router with a health check endpoint.
 *
 * WHAT:
 * - Initializes a new Express Router instance
 * - Registers GET /health endpoint that returns {status: 'ok'}
 * - Returns configured router for mounting in main app
 *
 * WHY:
 * - Provides lightweight liveness probe for monitoring/orchestration
 * - Separates routing logic into reusable module
 *
 * GUARDRAILS:
 * - DO NOT add authentication to /health without updating monitoring systems
 * - ALWAYS ensure /health responds synchronously without external dependencies
 * """
 *
 * DEPENDENCIES (from code analysis):
 * Calls: Router, content.trim, logger.info, readFile, require, res.json, router.get
 * Imports: express, { Router }, import express, { Router } from 'express';, import path from 'path';, import { readFile, writeFile } from 'fs/promises';, path, { readFile, writeFile }
 *
 * CHANGELOG (from git history):
 * - 2025-10-31: feat: Add JavaScript test fixtures and comprehensive adapter test suite (1ee084f)
 * AGENTSPEC_CONTEXT: function createRouter documented
 */
export const createRouter = () => {
  const router = Router();
  
  router.get('/health', (req, res) => {
    res.json({ status: 'ok' });
  });
  
  return router;
};

/**
 * Default export function.
 */
export default function main() {
  logger.info('Starting application');
  return { config, logger };
}
