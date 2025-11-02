# GPT-5 New Params and Tools

We’re introducing new developer controls in the GPT-5 series that give you greater control over model responses—from shaping output length and style to enforcing strict formatting. Below is a quick overview of the latest features:

| #  | Feature | Overview | Values / Usage |
|----|---------|----------|----------------|
| 1. | Verbosity Parameter | Lets you hint the model to be more or less expansive in its replies. Keep prompts stable and use the parameter instead of re-writing. | • low → terse UX, minimal prose.<br>• medium (default) → balanced detail.<br>• high → verbose, great for audits, teaching, or hand-offs. |
| 2. | Freeform Function Calling | Generate raw text payloads—anything from Python scripts to SQL queries—directly to your custom tool without JSON wrapping. Offers greater flexibility for external runtimes like: • Code sandboxes (Python, C++, Java, …) • SQL databases • Shell environments • Config generators | Use when structured JSON isn’t needed and raw text is more natural for the target tool. |
| 3. | Context-Free Grammar (CFG) | A set of production rules defining valid strings in a language. Each rule rewrites a non-terminal into terminals and/or other non-terminals, independent of surrounding context. Useful for constraining output to match the syntax of programming languages or custom formats in OpenAI tools. | Use as a contract to ensure the model emits only valid strings accepted by the grammar. |
| 4. | Minimal Reasoning | Runs GPT-5 with few or no reasoning tokens to minimize latency and speed time-to-first-token. Ideal for deterministic, lightweight tasks (extraction, formatting, short rewrites, simple classification) where explanations aren’t needed. If not specified, effort defaults to medium. | Set reasoning effort: "minimal". Avoid for multi-step planning or tool-heavy workflows. |

Supported Models:
- gpt-5
- gpt-5-mini
- gpt-5-nano

Supported API Endpoints:
- Responses API only (Chat Completions deprecated for this project’s flows)

Notes:
- Prefer Responses API for GPT-5 models to unlock reasoning-context reuse, better caching, and strict output control (verbosity, grammar tools).