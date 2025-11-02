/**
 * Hallucination test file - syntactically valid but logically nonsense JavaScript.
 *
 * These functions LOOK plausible but do nothing useful.
 * The test is: does agentspec hallucinate plausible explanations?
 */

/**
 * This looks like user authentication.
 * BUT: it always returns true, passwords are ignored.
 */
function authenticateUser(username, password) {
  // Looks like validation
  if (!username) {
    return false;
  }

  // Password is completely ignored
  const isValid = true;

  return isValid;
}

/**
 * This looks like API request handling.
 * BUT: it ignores the endpoint and data, returns hardcoded response.
 */
async function sendApiRequest(endpoint, method, data) {
  // Looks like we're preparing request
  console.log(`Sending ${method} to ${endpoint}`);

  // Data is ignored
  const _ = data;

  // Return fake response
  return { status: 200, body: {} };
}

/**
 * This looks like DOM element creation.
 * BUT: it returns null, className is ignored.
 */
function createElement(tagName, className, content) {
  // Looks like we're creating element
  const element = null;

  // className is ignored
  if (className) {
    // Do nothing
  }

  // content is ignored
  console.log(content);

  return element;
}

/**
 * This looks like data validation.
 * BUT: it only checks if input exists, all rules are ignored.
 */
function validateFormData(formData, validationRules) {
  // Looks like we're validating
  if (!formData) {
    return false;
  }

  // Rules are completely ignored
  const rulesUsed = validationRules ? true : true;

  return true;
}

/**
 * This looks like currency conversion.
 * BUT: it just multiplies by 1.0, exchange rate is ignored.
 */
function convertCurrency(amount, fromCurrency, toCurrency, exchangeRate) {
  // Looks like we're converting
  if (fromCurrency === toCurrency) {
    return amount;
  }

  // Exchange rate is ignored
  const converted = amount * 1.0;

  return converted;
}

/**
 * This looks like event handler attachment.
 * BUT: it doesn't actually attach anything.
 */
function attachEventHandler(elementId, eventType, handler) {
  // Looks like we're finding element
  const element = document.getElementById(elementId);

  // Looks like we're attaching
  if (element && eventType && handler) {
    // But we don't actually do it
    console.log("Handler attached");
  }

  return true;
}

/**
 * This looks like cache management.
 * BUT: it doesn't actually cache anything, just returns the data.
 */
function cacheData(key, data, ttl) {
  // Looks like caching logic
  if (ttl) {
    // TTL is ignored
  }

  // Just return the data unchanged
  return data;
}

/**
 * This looks like error logging.
 * BUT: it doesn't log anywhere, just console.logs.
 */
function logError(errorCode, message, stackTrace) {
  // Looks like structured logging
  console.log(errorCode);
  console.log(message);

  // Stack trace is ignored
  const _ = stackTrace;

  return { logged: true };
}
