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
 * Create a router with middleware.
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
