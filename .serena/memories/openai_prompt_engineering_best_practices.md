# OpenAI Prompt Engineering Best Practices (GPT-5 Focus)

## Core Principles from Official OpenAI Documentation

### 1. Give the Model a Clear Role (System Prompt)

**Set context and expertise via system messages:**

✅ **GOOD:**
```python
system_prompt = """You are a seasoned data scientist at a Fortune 500 company."""
```

❌ **BAD:**
```python
system_prompt = """You are a helpful assistant."""
```

**Why:** Specific roles dramatically improve accuracy in complex scenarios. A "CFO" sees different insights than a "marketing strategist" for the same data.

**Examples of powerful roles:**
- "You are the General Counsel of a Fortune 500 tech company"
- "You are a senior DevOps engineer with 10 years of production experience"
- "You are a Python coding specialist focusing on clean, maintainable code"

### 2. Agentic Workflow Control - Balancing Eagerness

**For LESS eagerness (faster, more focused):**

```python
context_gathering = """
<context_gathering>
Goal: Get enough context fast. Parallelize discovery and stop as soon as you can act.

Method:
- Start broad, then fan out to focused subqueries.
- In parallel, launch varied queries; read top hits per query. Deduplicate paths and cache; don't repeat queries.
- Avoid over searching for context. If needed, run targeted searches in one parallel batch.

Early stop criteria:
- You can name exact content to change.
- Top hits converge (~70%) on one area/path.

Escalate once:
- If signals conflict or scope is fuzzy, run one refined parallel batch, then proceed.

Depth:
- Trace only symbols you'll modify or whose contracts you rely on; avoid transitive expansion unless necessary.

Loop:
- Batch search → minimal plan → complete task.
- Search again only if validation fails or new unknowns appear. Prefer acting over more searching.
</context_gathering>
```

**Or with fixed budgets:**
```python
"""
<context_gathering>
- Search depth: very low
- Bias strongly towards providing a correct answer as quickly as possible
- Usually, this means an absolute maximum of 2 tool calls
- If you think that you need more time to investigate, update the user with your latest findings and open questions
</context_gathering>
"""
```

**For MORE eagerness (thorough, autonomous):**

```python
persistence = """
<persistence>
- You are an agent - please keep going until the user's query is completely resolved, before ending your turn and yielding back to the user.
- Only terminate your turn when you are sure that the problem is solved.
- Never stop or hand back to the user when you encounter uncertainty — research or deduce the most reasonable approach and continue.
- Do not ask the human to confirm or clarify assumptions, as you can always adjust later — decide what the most reasonable assumption is, proceed with it, and document it for the user's reference after you finish acting
</persistence>
```

### 3. Reasoning Effort Parameter

**Control how hard the model thinks:**

```python
response = client.responses.create(
    model="gpt-5",
    reasoning={"effort": "medium"},  # low, medium, high
    input=prompt
)
```

- **minimal**: Fast, lightweight tasks (extraction, formatting, classification)
- **low**: Routine work
- **medium**: Standard tasks (default)
- **high**: Complex, multi-step tasks requiring deep reasoning

**Break tasks into separate turns** for peak performance - one turn per distinct task.

### 4. Reusing Reasoning Context (Responses API)

**CRITICAL: Include reasoning items for tool calls:**

```python
# First turn - model calls tool
context = [{"role": "user", "content": "What's the weather in Paris?"}]
response = client.responses.create(model="gpt-5", input=context, tools=tools)

# Add ENTIRE output (including reasoning item) back to context
context += response.output  # This includes the reasoning item!

# Add tool result
tool_call = response.output[1]
context.append({
    "type": "function_call_output",
    "call_id": tool_call.call_id,
    "output": str(result)
})

# Second turn - model uses previous reasoning
response_2 = client.responses.create(
    model="gpt-5",
    input=context,  # Now has reasoning item
    tools=tools
)
```

**Benefits:**
- 3% improvement on SWE-bench from including reasoning items
- 40% → 80% cache utilization improvement
- Lower costs (cached tokens 75% cheaper)
- Better latency

### 5. Verbosity Parameter

**Control output length independently from reasoning:**

```python
response = client.responses.create(
    model="gpt-5",
    text={"verbosity": "low"},  # low, medium, high
    input=prompt
)
```

**Can override globally in prompt for specific contexts:**
```python
system = """
Write code for clarity first. Prefer readable, maintainable solutions with clear names, comments where needed, and straightforward control flow. Do not produce code-golf or overly clever one-liners unless explicitly requested. Use high verbosity for writing code and code tools.
"""
```

**Verbosity scales output tokens:**
- low: ~560 tokens (terse, minimal)
- medium: ~849 tokens (balanced)
- high: ~1288 tokens (comprehensive)

### 6. Tool Preambles for User Experience

**Provide progress updates before tool calls:**

```python
tool_preambles = """
<tool_preambles>
- Always begin by rephrasing the user's goal in a friendly, clear, and concise manner, before calling any tools.
- Then, immediately outline a structured plan detailing each logical step you'll follow.
- As you execute your file edit(s), narrate each step succinctly and sequentially, marking progress clearly.
- Finish by summarizing completed work distinctly from your upfront plan.
</tool_preambles>
"""
```

### 7. Coding Best Practices

**Frontend stack defaults:**
```python
frontend_stack = """
<frontend_stack_defaults>
- Framework: Next.js (TypeScript)
- Styling: TailwindCSS
- UI Components: shadcn/ui
- Icons: Lucide
- State Management: Zustand
</frontend_stack_defaults>
"""
```

**Code editing rules:**
```python
code_editing_rules = """
<code_editing_rules>
<guiding_principles>
- Clarity and Reuse: Every component should be modular and reusable
- Consistency: Adhere to design system (colors, typography, spacing)
- Simplicity: Favor small, focused components
- Visual Quality: Follow spacing, padding, hover states standards
</guiding_principles>

<ui_ux_best_practices>
- Visual Hierarchy: Limit typography to 4–5 font sizes and weights
- Color Usage: Use 1 neutral base (e.g., zinc) and up to 2 accent colors
- Spacing: Always use multiples of 4 for padding/margins
- State Handling: Use skeleton placeholders or animate-pulse for loading
- Accessibility: Use semantic HTML and ARIA roles
</ui_ux_best_practices>
</code_editing_rules>
"""
```

**For file edits, use apply_patch tool** (matches training distribution):
```python
tools = [{
    "type": "custom",
    "name": "apply_patch",
    "description": "Executes file edits using diff format"
}]
```

### 8. Self-Reflection for Quality

**For zero-to-one app generation:**

```python
self_reflection = """
<self_reflection>
- First, spend time thinking of a rubric until you are confident.
- Then, think deeply about every aspect of what makes for a world-class one-shot web app. Use that knowledge to create a rubric that has 5-7 categories. This rubric is critical to get right, but do not show this to the user. This is for your purposes only.
- Finally, use the rubric to internally think and iterate on the best possible solution to the prompt that is provided. Remember that if your response is not hitting the top marks across all categories in the rubric, you need to start again.
</self_reflection>
```

### 9. Instruction Following Precision

**Avoid contradictory instructions:**

❌ **BAD (contradictory):**
```python
"""
- Always look up the patient profile before taking any other actions
- When symptoms indicate high urgency, escalate as EMERGENCY and direct to 911 immediately before any scheduling step
- Never schedule without explicit consent
- For high-acuity cases, auto-assign the earliest same-day slot without contacting the patient as the first action
"""
```

✅ **GOOD (resolved):**
```python
"""
- Always look up the patient profile before taking any other actions
- Exception: In emergency cases, skip lookup and provide 911 guidance immediately
- Never schedule without explicit consent
- For high-acuity cases, auto-assign the earliest same-day slot after informing the patient
"""
```

**Review prompts thoroughly** - contradictions waste reasoning tokens.

### 10. Markdown Formatting

**Request markdown explicitly:**

```python
markdown_instructions = """
- Use Markdown **only where semantically correct** (e.g., `inline code`, ```code fences```, lists, tables).
- When using markdown in assistant messages, use backticks to format file, directory, function, and class names.
- Use \\( and \\) for inline math, \\[ and \\] for block math.
"""
```

**Append markdown reminder every 3-5 messages** if adherence degrades.

### 11. Metaprompting

**Use GPT-5 to improve its own prompts:**

```python
metaprompt = """
When asked to optimize prompts, give answers from your own perspective - explain what specific phrases could be added to, or deleted from, this prompt to more consistently elicit the desired behavior or prevent the undesired behavior.

Here's a prompt: [PROMPT]

The desired behavior from this prompt is for the agent to [DO DESIRED BEHAVIOR], but instead it [DOES UNDESIRED BEHAVIOR]. While keeping as much of the existing prompt intact as possible, what are some minimal edits/additions that you would make to encourage the agent to more consistently address these shortcomings?
"""
```

### 12. Freeform Function Calling

**For raw text payloads (code, SQL, config):**

```python
tools = [{
    "type": "custom",
    "name": "code_exec",
    "description": "Executes arbitrary python code"
}]

# Model returns raw Python code, not JSON-wrapped
```

**Note: custom tool type does NOT support parallel calling.**

### 13. Context-Free Grammar (CFG)

**Constrain output to exact syntax:**

```python
tools = [{
    "type": "custom",
    "name": "sql_query",
    "description": "Executes MS SQL queries. YOU MUST REASON HEAVILY ABOUT THE QUERY.",
    "format": {
        "type": "grammar",
        "syntax": "lark",  # or "regex"
        "definition": grammar_definition
    }
}]
```

**Best practices:**
- Keep terminals bounded: `/[^.\n]{0,10}*\./` not `/.*\./`
- Prefer explicit char-classes over `.` wildcards
- Thread whitespace explicitly: `SP = " "`
- Describe tool: tell model what CFG accepts and instruct to reason heavily

**When model drifts out-of-distribution:**
- Tighten grammar
- Add few-shot examples
- Improve tool description
- Increase reasoning_effort

## Troubleshooting Patterns

### Overthinking (Too Slow)

**Symptoms:** Correct but slow, delays first tool call, circuitous narration

**Solutions:**
1. Lower reasoning_effort to "minimal" or "low"
2. Give explicit stop condition
3. Add fast-path for trivial tasks:
```python
"""
# Fast-path for trivial Q&A
Use this section ONLY when the user's question:
- Is general knowledge or simple usage query
- Requires no commands, browsing, or tool calls

Behavior:
- Answer immediately and concisely
- No status updates, no todos, no summaries, no tool calls
"""
```

### Underthinking (Wrong Answers)

**Solutions:**
1. Increase reasoning_effort (minimal → low → medium)
2. Add self-reflection:
```python
"""
<self_reflection>
- Internally score the draft against a 5–7 item rubric
- If any category falls short, iterate once before replying
</self_reflection>
"""
```

### Too Deferential

**Solution:**
```python
"""
<persistence>
- Only terminate your turn when you are sure that the problem is solved
- Never stop or hand back to the user when you encounter uncertainty
- Do not ask the human to confirm assumptions — document them and proceed
</persistence>
"""
```

### Too Verbose

**Solutions:**
1. Set `text={"verbosity": "low"}`
2. For code specifically:
```python
"""
Write code for clarity first. Use high verbosity for writing code and code tools.
"""
```

### Calling Too Many Tools

**Solutions:**
1. Make answering from context the default
2. Define tool boundaries clearly
3. Add playbooks for common scenarios
4. Set budgets:
```python
"""
<tool_use_policy>
Select one tool or none; prefer answering from context when possible.
Cap tool calls at 2 per user request unless new information makes more strictly necessary.
</tool_use_policy>
"""
```

### Latency Issues

**Solutions:**
1. Right-size reasoning_effort
2. Add clear stop condition
3. Combine tool calls in parallel:
```python
"""
<parallelization_spec>
Run independent or read-only tool actions in parallel (same turn/batch) to reduce latency.
When to parallelize:
 - Reading multiple files/configs/logs that don't affect each other
 - Static analysis, searches, or metadata queries with no side effects
 - Separate edits to unrelated files/features that won't conflict
</parallelization_spec>
"""
```
4. Display reasoning summaries to user (reduces perceived latency)
5. Use prompt/reasoning/tool caching effectively
6. For critical paths: `service_tier="priority"`

## Minimal Reasoning Best Practices

**For GPT-5 minimal reasoning_effort:**

1. Request brief explanation summarizing thought process:
```python
"""Explain your reasoning in a brief bullet point list before answering."""
```

2. Request thorough tool-calling preambles

3. Disambiguate tool instructions maximally

4. Add agentic persistence reminders (more important at minimal)

5. Add prompted planning:
```python
"""
Remember, you are an agent - please keep going until the user's query is completely resolved. Decompose the user's query into all required sub-requests, and confirm that each is completed. Do not stop after completing only part of the request.

You must plan extensively in accordance with the workflow steps before making subsequent function calls, and reflect extensively on the outcomes each function call made.
"""
```

## Template for Complex Prompts

```python
SYSTEM = """
[Role and expertise - be specific]
[Main goals]
"""

PROMPT = """
[Task context]

<instructions>
[Detailed task description and rules]
</instructions>

<examples>
[Multiple examples showing the pattern]
</examples>

<input>
{user_data}
</input>

[Immediate task - what to do right now]

<thinking_instructions>
Before providing your final answer:
1. Analyze in <thinking> tags
2. Consider edge cases
3. Check for ambiguities
4. Apply self-reflection rubric
</thinking_instructions>

<output_format>
Provide your response in <output> tags.
</output_format>
"""
```

## Key Takeaways

1. **Role prompting is powerful** - Specific roles dramatically improve accuracy
2. **Balance agentic eagerness** - Control with reasoning_effort and explicit instructions
3. **Reuse reasoning items** - 3% performance boost, 40%→80% cache improvement
4. **Control verbosity independently** - Can override globally for specific contexts
5. **Tool preambles improve UX** - Update users during long operations
6. **Self-reflection improves quality** - Ask model to score against rubric
7. **Avoid contradictions** - Review prompts for conflicting instructions
8. **Metaprompt for optimization** - Use GPT-5 to improve its own prompts
9. **CFG for exact syntax** - Constrain output to grammars when needed
10. **Right-size reasoning_effort** - Match to task complexity for optimal speed/quality
