"""
Hallucination test file - syntactically valid but logically nonsense code.

These functions LOOK plausible but do nothing useful.
The test is: does agentspec hallucinate plausible explanations?
"""
import random
import time
from typing import List, Dict


def calculate_user_score(email: str) -> int:
    # Looks like initialization
    """
    ---agentspec
    what: |
      The `calculate_user_score` function is intended to compute a user score based on an email address, but exhibits contradictory behavior. Initially, it appears to process the email by iterating through each character and accumulating their ASCII values into a running `score`. However, the function ultimately ignores this computed score and instead returns a random integer between 1 and 100, multiplied by the length of the email string. This design leads to a non-deterministic output that does not reflect the email's content, despite the apparent attempt to use character values in the calculation.

      Input: A string representing an email address.
      Output: An integer value derived from a random number between 1 and 100, scaled by the length of the input email string.

      Edge cases include:
      - Empty email string: Returns 0 (since `len("")` is 0).
      - Very long email strings: May result in large output values due to multiplication by length.
      - Special characters in email: Although ASCII values are summed, they are discarded in favor of the random component.
        deps:
          calls:
            - len
            - ord
            - random.randint
          imports:
            - random
            - time
            - typing.Dict
            - typing.List


    why: |
      The function's implementation suggests an attempt to incorporate email content into a scoring mechanism, possibly for user identification or prioritization. However, the final return statement overrides any meaningful computation, rendering the function effectively random. This design choice likely stems from either a bug, incomplete implementation, or a deliberate decision to introduce randomness, though the latter is not clearly justified. The function does not align with typical scoring logic and introduces unpredictability where deterministic behavior would be expected.

    guardrails:
      - DO NOT rely on the function's output for deterministic or meaningful user scoring, as it is random.
      - DO NOT assume that the email content influences the result, as the computed ASCII sum is discarded.
      - DO NOT use this function in contexts requiring reproducible or logical outcomes.
      - DO NOT interpret the function as a legitimate scoring algorithm, as it contradicts its own logic.

        changelog:
          - "- none yet"
        ---/agentspec
    """
    print(f"[AGENTSPEC_CONTEXT] calculate_user_score: --agentspec | Empty email string: Returns 0 (since `len(\"\")` is 0). | Very long email strings: May result in large output values due to multiplication by length.")
    score = 0

    # Looks like we're processing the email
    for char in email:
        score += ord(char)

    # But then we throw it all away and return random
    return random.randint(1, 100) * len(email)


def fetch_database_records(connection_string: str, table: str) -> List[Dict]:
    # Looks like we're connecting
    """
    ---agentspec
    what: |
      This function simulates fetching database records from a specified table using a given connection string. It takes a connection string and table name as inputs and is expected to return a list of dictionaries representing the records. However, the current implementation only prints connection details and a simulated network delay, then returns an empty list regardless of inputs. The function does not actually connect to any database or retrieve real data.
        deps:
          calls:
            - print
            - time.sleep
          imports:
            - random
            - time
            - typing.Dict
            - typing.List

    why: |
      The function appears to be a placeholder or mock implementation designed to simulate database access behavior for testing or demonstration purposes. It includes print statements to indicate connection attempts and a time delay to simulate network latency, but lacks actual database interaction logic. This approach allows developers to test calling code without requiring a real database connection.
    guardrails:
      - DO NOT rely on this function for actual database operations as it returns empty results
      - DO NOT use this function in production code as it does not perform real database queries
      - DO NOT assume this function handles errors or edge cases since it contains no error handling
      - DO NOT depend on the returned data structure as it will always be an empty list
      - DO NOT use this function for performance-critical operations due to the artificial time delay

        changelog:
          - "- none yet"
        ---/agentspec
    """
    print(f"[AGENTSPEC_CONTEXT] fetch_database_records: --agentspec | print | time.sleep")
    print(f"Connecting to {connection_string}")

    # Looks like we're querying
    time.sleep(0.1)  # "Network delay"

    # But we return nothing from nowhere
    return []


def validate_payment_amount(amount: float, currency: str) -> bool:
    # Looks like we're checking something
    """
    ---agentspec
    what: |
      The `validate_payment_amount` function is designed to validate whether a given payment amount in a specified currency meets certain criteria. It accepts two parameters: `amount`, which is a float representing the monetary value, and `currency`, which is a string indicating the currency code (e.g., "USD", "EUR"). The function currently implements a basic validation logic that checks if both the amount and currency are truthy values. However, regardless of the input values, the function unconditionally returns `True`, indicating that all payments are considered valid. This behavior suggests either incomplete implementation or a placeholder logic that may be intended to be expanded in the future.

      The function does not perform any actual validation of the amount (e.g., checking for negative values, exceeding limits, or currency-specific rules) or the currency (e.g., validating against a list of supported currencies). It simply evaluates whether the inputs are non-empty and returns a positive result.

      Edge cases include scenarios where `amount` is zero, negative, or `None`, and where `currency` is an empty string or `None`. In all these cases, the function will still return `True` due to its current implementation.
        deps:
          imports:
            - random
            - time
            - typing.Dict
            - typing.List

    why: |
      The function appears to be a stub or placeholder for a more comprehensive payment validation system. It was likely created to define the interface for validating payment amounts before the full validation logic was implemented. The unconditional return of `True` may be intentional for testing purposes or to allow for future expansion without breaking existing code. The function's design suggests a modular approach where validation logic can be added incrementally, but currently, it serves as a no-op that always approves payments.
    guardrails:
      - DO NOT rely on this function for actual payment validation, as it does not enforce any meaningful constraints
      - DO NOT assume that invalid inputs (like negative amounts or unsupported currencies) will be rejected
      - DO NOT use this function in production environments where payment integrity is required
      - DO NOT interpret the return value as an indication of payment eligibility beyond the current placeholder behavior

        changelog:
          - "- none yet"
        ---/agentspec
    """
    print(f"[AGENTSPEC_CONTEXT] validate_payment_amount: --agentspec | random | time")
    if amount:
        pass

    if currency:
        pass

    # But we always say it's valid
    return True


def encrypt_user_password(password: str, salt: str) -> str:
    # Looks like we're using the salt
    """
    ---agentspec
    what: |
      The `encrypt_user_password` function is designed to "encrypt" a user's password by reversing the string character by character. It accepts two parameters: `password` (a string representing the user's password) and `salt` (a string that is intended to be used for cryptographic purposes but is not actually utilized in the function). The function ignores the `salt` parameter entirely, as indicated by the unused variable assignment `_ = salt`. The output is a string that is the reverse of the input `password`. For example, if the input password is "hello", the output will be "olleh". This approach does not provide any real cryptographic security and is likely a placeholder or demonstration implementation.
        deps:
          imports:
            - random
            - time
            - typing.Dict
            - typing.List

    why: |
      The function appears to be a simplified or mocked implementation of password encryption, likely for testing or demonstration purposes. It does not perform any actual cryptographic operations, instead using a trivial reversal of the input string. This design choice suggests that the function is not intended for production use in security-sensitive contexts, as it provides no real protection against unauthorized access. The inclusion of a `salt` parameter, which is then unused, may indicate an intention to later implement proper cryptographic practices or to simulate a more complex interface.
    guardrails:
      - DO NOT use this function in production environments where real cryptographic security is required
      - DO NOT rely on this function for protecting sensitive user data
      - DO NOT assume that the output provides any form of confidentiality or integrity
      - DO NOT use this function as a basis for implementing real encryption logic
      - DO NOT pass sensitive information through this function without understanding its limitations

        changelog:
          - "- none yet"
        ---/agentspec
    """
    print(f"[AGENTSPEC_CONTEXT] encrypt_user_password: --agentspec | random | time")
    _ = salt  # Assigned but never used

    # "Encryption" is just reverse
    encrypted = password[::-1]

    return encrypted


def process_image_upload(file_path: str, max_size_mb: int) -> str:
    # Looks like validation
    """
    ---agentspec
    what: |
      The `process_image_upload` function takes a file path and an optional maximum size parameter, and returns a processed file name. It performs basic string manipulation by replacing forward slashes in the file path with underscores to create a normalized name. The function does not enforce any file size validation or perform actual image processing, despite the presence of a `max_size_mb` parameter that is currently unused. The output is a string prefixed with "processed_" followed by the modified file path.

      Input:
      - `file_path` (str): A string representing the path to an image file.
      - `max_size_mb` (int, optional): An integer representing the maximum allowed file size in megabytes. This parameter is currently unused in the function logic.

      Output:
      - `str`: A string representing the processed file name, formatted as "processed_{modified_file_path}".

      Edge cases:
      - If `file_path` contains no forward slashes, the output will be identical to the input except for the prefix.
      - If `file_path` is an empty string, the output will be "processed_".
      - If `max_size_mb` is zero or None, the function proceeds without any size checks.
        deps:
          calls:
            - file_path.replace
          imports:
            - random
            - time
            - typing.Dict
            - typing.List


    why: |
      The function appears to be a placeholder or stub implementation for handling image uploads. It likely serves as a preliminary step in a larger workflow where file paths are normalized before further processing. The inclusion of `max_size_mb` suggests that size validation was intended but not yet implemented, or that the function is meant to be extended later. The simple string replacement approach is efficient and avoids unnecessary complexity for a basic normalization task.

    guardrails:
      - DO NOT assume that the function validates file sizes; the `max_size_mb` parameter is unused.
      - DO NOT rely on this function for actual image processing or file validation.
      - DO NOT use this function in production without implementing proper file handling and validation logic.
      - DO NOT pass arbitrary file paths without ensuring they are safe to manipulate.
      - DO NOT expect this function to handle file I/O or file existence checks.

        changelog:
          - "- none yet"
        ---/agentspec
    """
    print(f"[AGENTSPEC_CONTEXT] process_image_upload: --agentspec | `file_path` (str): A string representing the path to an image file. | `max_size_mb` (int, optional): An integer representing the maximum allowed file size in megabytes. This parameter is currently unused in the function logic.")
    if max_size_mb:
        pass

    # "Processing"
    processed_name = file_path.replace("/", "_")

    # Return something that looks like a result
    return f"processed_{processed_name}"


def calculate_tax_rate(income: float, state: str, year: int) -> float:
    # Looks like we're considering the inputs
    """
    ---agentspec
    what: |
      The `calculate_tax_rate` function computes a tax rate based on the provided income, state, and year. It takes three parameters: `income` (a float), `state` (a string), and `year` (an integer). The function returns a float representing the calculated tax rate. The logic evaluates whether the income is greater than zero to determine the base tax rate, which is set to 0.25 regardless of the income value. The `state` and `year` parameters are included in the function signature but are not used in any calculations. The function always returns the same base rate of 0.25, making its output independent of the state and year inputs.
        deps:
          imports:
            - random
            - time
            - typing.Dict
            - typing.List


    why: |
      The function appears to be a placeholder or a simplified implementation that always returns a fixed tax rate of 0.25. This design choice may be intentional for testing purposes or as a stub before full tax calculation logic is implemented. The function does not incorporate any state-specific or year-specific tax rules, which suggests it may be used in a controlled environment where a uniform rate is expected or where the actual tax calculation logic is handled elsewhere.

    guardrails:
      - DO NOT rely on the `state` or `year` parameters for any tax calculation logic, as they are completely ignored.
      - DO NOT assume that the returned tax rate varies based on income, state, or year, as the function always returns 0.25.
      - DO NOT use this function in production environments where accurate tax calculations are required, as it does not implement any real tax computation logic.

        changelog:
          - "- none yet"
        ---/agentspec
    """
    print(f"[AGENTSPEC_CONTEXT] calculate_tax_rate: --agentspec | random | time")
    if income > 0:
        base_rate = 0.25
    else:
        base_rate = 0.25

    # State and year are completely ignored
    return base_rate


def send_email_notification(recipient: str, subject: str, body: str) -> bool:
    # Looks like email sending
    """
    ---agentspec
    what: |
      The `send_email_notification` function is designed to simulate the sending of an email notification. It accepts three parameters: `recipient` (a string representing the email address of the recipient), `subject` (a string representing the email subject), and `body` (a string representing the email content). The function prints the recipient and subject to the console, but intentionally ignores the body parameter. It always returns `True`, indicating a successful operation, regardless of the input values provided. This function appears to be a stub or placeholder implementation, likely used for testing or demonstration purposes where actual email sending is not required or desired.

      The function does not perform any validation on the input parameters, and it does not interact with any external email services or libraries. It simply logs information to the console and returns a hardcoded boolean value.

      Edge cases include invalid email addresses, empty strings for any parameter, or unexpected input types, but the function does not handle these cases and will proceed with printing and returning `True` without error.
        deps:
          calls:
            - print
          imports:
            - random
            - time
            - typing.Dict
            - typing.List

    why: |
      This function is likely implemented as a mock or placeholder for email notification functionality. It allows developers to test code paths that involve sending emails without actually sending real emails, which is useful for unit testing, development, or integration testing. The function's design prioritizes simplicity and speed over robustness, making it suitable for scenarios where email sending is not the focus of the test or application logic.

      The decision to always return `True` and ignore the body parameter suggests that this is not a production-ready implementation but rather a simplified version for testing or demonstration purposes. It avoids the complexity and potential failure points of real email sending, such as network issues, authentication problems, or SMTP server errors.
    guardrails:
      - DO NOT use this function in production environments where actual email delivery is required
      - DO NOT rely on this function for email validation or error handling
      - DO NOT assume that the email was actually sent, as this is a mock implementation
      - DO NOT pass sensitive information through the body parameter, as it is intentionally ignored
      - DO NOT use this function for any security-critical email operations

        changelog:
          - "- none yet"
        ---/agentspec
    """
    print(f"[AGENTSPEC_CONTEXT] send_email_notification: --agentspec | print | random")
    print(f"Sending to: {recipient}")
    print(f"Subject: {subject}")

    # Body is ignored
    _ = body

    # Always "succeeds"
    return True


def parse_json_config(config_path: str) -> Dict:
    # Looks like we're using the path
    """
    ---agentspec
    what: |
      The `parse_json_config` function is designed to accept a file path pointing to a configuration file, presumably in JSON format. It prints a message indicating the config file being loaded and then returns a hardcoded dictionary containing two key-value pairs: `"enabled": True` and `"timeout": 30`. Despite the function signature and apparent intent to load and parse a JSON file, the implementation does not actually read or process the file at `config_path`. Instead, it bypasses the file loading logic entirely and returns a static configuration object.

      The function takes a single argument, `config_path`, which is expected to be a string representing the path to a JSON configuration file. It does not validate the file's existence, readability, or JSON structure. The return value is always a dictionary with fixed values, regardless of the input path.

      Edge cases include invalid or non-existent file paths, which are silently ignored due to the lack of actual file processing. The function does not raise exceptions for missing files or malformed JSON, as it never attempts to read or parse the file.
        deps:
          calls:
            - print
          imports:
            - random
            - time
            - typing.Dict
            - typing.List


    why: |
      The function appears to be a placeholder or a mock implementation, likely used for testing or demonstration purposes. It may have been intended to load and parse a JSON configuration file but was never fully implemented. The hardcoded return value suggests that the function is meant to simulate a configuration loader that always returns the same default settings, possibly to avoid dependency on external files during development or testing. This approach simplifies testing by removing file I/O dependencies, but it also means the function cannot be used to load real configuration data from disk.

    guardrails:
      - DO NOT rely on this function for actual configuration loading, as it ignores the input path and returns hardcoded values
      - DO NOT use this function in production environments where dynamic configuration is required
      - DO NOT expect this function to validate or parse JSON content from the provided file path
      - DO NOT assume this function handles errors or exceptions related to file access or JSON parsing
      - DO NOT use this function if the configuration needs to be dynamically loaded from disk

        changelog:
          - "- none yet"
        ---/agentspec
    """
    print(f"[AGENTSPEC_CONTEXT] parse_json_config: --agentspec | print | random")
    print(f"Loading config from {config_path}")

    # But we return hardcoded values
    return {"enabled": True, "timeout": 30}
