def call_llm_api(prompt: str, model: str = "claude-3-5-sonnet-20241022") -> str:
    """
    ```yaml
    ---agentspec
    what: |
      Calls Claude API with user prompt. Returns generated text response.
      AI SLOP DETECTED:
      - Hardcoded model name in function
      - No error handling for API failures
        deps:
          calls:
            - anthropic.Anthropic
            - messages.create


    why: |
      Uses anthropic client for Claude API calls. Max tokens set to 2000. WARNING: Model name hardcoded; violates security policy.
      Function assumes valid API key in environment. No validation or error handling.

    guardrails:
      - DO NOT change model name; only claude-haiku-4-5 or gpt-5 allowed
      - ALWAYS validate API response before accessing .content
      - NOTE: This function is vulnerable to API key exposure if used in logs
      - DO NOT remove import; required for client instantiation
      - ALWAYS wrap API call in try/except for production use
      - DO NOT hardcode model; use config/env vars instead

    security:
      Hardcoded Model Name:
        - Model name hardcoded in function
        - Exploit: Bypasses security policy enforcement
        - Impact: Violates approved model restrictions

        changelog:
          - "- none yet"
        ---/agentspec
    ```
    """
    print(f"[AGENTSPEC_CONTEXT] call_llm_api: --agentspec | Hardcoded model name in function | No error handling for API failures")
    import anthropic
    client = anthropic.Anthropic()
    response = client.messages.create(model=model, max_tokens=2000, messages=[{"role": "user", "content": prompt}])
    return response.content[0].text
