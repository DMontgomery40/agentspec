# Anthropic Prompt Engineering Best Practices

## Key Principles from Anthropic's Official Docs

### 1. Use XML Tags to Separate Data from Instructions

**CRITICAL: Always use XML tags to clearly delineate input data from instructions.**

✅ **GOOD:**
```python
PROMPT = f"<email>{EMAIL}</email> Make this email more polite."
```

❌ **BAD:**
```python
PROMPT = f"{EMAIL} <----- Make this email more polite."
```

**Why:** Without tags, Claude may interpret data as part of instructions. Tags provide clear boundaries.

**Common tags:**
- `<email>...</email>` for emails
- `<code>...</code>` for code
- `<document>...</document>` for documents
- `<context>...</context>` for background information
- `<question>...</question>` for user questions
- `<thinking>...</thinking>` for internal reasoning
- `<final_answer>...</final_answer>` for outputs

### 2. Structure Complex Prompts in Order

**Recommended ordering:**
1. Task context (role, goals)
2. Tone context (if needed)
3. Detailed task description and rules
4. Examples (multiple if needed)
5. Input data (in XML tags)
6. Immediate task
7. Precognition/thinking instructions
8. Output formatting

**Example structure:**
```python
PROMPT = ""

if TASK_CONTEXT:
    PROMPT += f"{TASK_CONTEXT}"

if TONE_CONTEXT:
    PROMPT += f"\n\n{TONE_CONTEXT}"

if TASK_DESCRIPTION:
    PROMPT += f"\n\n{TASK_DESCRIPTION}"

if EXAMPLES:
    PROMPT += f"\n\n{EXAMPLES}"

if INPUT_DATA:
    PROMPT += f"\n\n{INPUT_DATA}"

if IMMEDIATE_TASK:
    PROMPT += f"\n\n{IMMEDIATE_TASK}"

if PRECOGNITION:
    PROMPT += f"\n\n{PRECOGNITION}"

if OUTPUT_FORMATTING:
    PROMPT += f"\n\n{OUTPUT_FORMATTING}"
```

### 3. Few-Shot Prompting with Examples

**Use examples instead of complex instructions:**

✅ **GOOD (show, don't tell):**
```python
PROMPT = """
Extract names and professions as JSON.

Text: "Alice is a software engineer and Bob is a doctor."
Output: [{"name": "Alice", "profession": "software engineer"}, {"name": "Bob", "profession": "doctor"}]

Text: "Charlie is a teacher."
Output: """
```

❌ **BAD (complex rules):**
```python
PROMPT = """
Extract names and professions. Format as JSON array with objects containing 'name' and 'profession' keys.
Ensure proper JSON syntax. Handle multiple people. Use lowercase for professions.
"""
```

**Key points:**
- Examples are the MOST EFFECTIVE tool for knowledge work
- Use `<example>...</example>` tags for multiple examples
- Provide context about what each example demonstrates

### 4. Prefilling to Control Output Format

**Use prefill to start Claude's response:**

```python
PROMPT = "Write a haiku about cats in <haiku> tags."
PREFILL = "<haiku>"

# Claude will complete: "<haiku>\nWhiskers twitch and turn..."
```

**Benefits:**
- Guarantees output starts with desired tag
- Forces specific format
- Skips preamble

### 5. Step-by-Step Thinking

**Ask Claude to think before answering:**

✅ **GOOD:**
```python
PROMPT = """
<question>{question}</question>

Before answering, analyze in <thinking> tags:
- What is the main issue?
- What information is relevant?
- What are potential ambiguities?

Then provide your answer in <answer> tags.
"""
```

**Why:** Improves accuracy and reasoning quality, especially for complex tasks.

### 6. Clear and Direct Instructions

**Be specific about what you want:**

❌ **VAGUE:**
```python
PROMPT = "What do you think about basketball?"
```

✅ **DIRECT:**
```python
PROMPT = "Who is the best basketball player of all time? Yes, there are differing opinions, but if you absolutely had to pick one player, who would it be?"
```

### 7. System Prompts for Context

**Use system prompts for role/persona:**

```python
SYSTEM = """
You are a highly experienced medical professional specializing in patient record summarization.
Your summaries help busy doctors prepare for appointments.
"""

PROMPT = """
<patient_record>{record}</patient_record>

Summarize this record including:
- Name and age
- Key diagnoses (chronological)
- Current medications
- Recent concerns
"""
```

### 8. Handle Ambiguity Explicitly

**Tell Claude what to do when it doesn't know:**

```python
PROMPT = """
Answer the question using only the provided context.

<context>{context}</context>
<question>{question}</question>

If the context doesn't contain enough information to answer, respond with:
"I don't have enough information to answer this question based on the provided context."
"""
```

### 9. Output Formatting with Tags

**Wrap outputs in consistent tags for parsing:**

```python
SYSTEM = """
Always wrap your final response in <reply></reply> tags.
Put your thinking in <thinking></thinking> tags first.
"""

# Then parse with regex:
pattern = r'<reply>(.*?)</reply>'
match = re.search(pattern, response, re.DOTALL)
```

### 10. Multiple Examples for Complex Tasks

**For data extraction, show the pattern multiple times:**

```python
PROMPT = """
Extract individuals and professions:

<passage>
Dr. Liam Patel is a neurosurgeon. Olivia Chen is an architect.
</passage>

<individuals>
1. Dr. Liam Patel [NEUROSURGEON]
2. Olivia Chen [ARCHITECT]
</individuals>

<passage>
Chef Oliver Hamilton runs a restaurant. Elizabeth Chen is a librarian.
</passage>

<individuals>
1. Oliver Hamilton [CHEF]
2. Elizabeth Chen [LIBRARIAN]
</individuals>

<passage>
{new_passage}
</passage>

<individuals>
"""
```

## Common Pitfalls to Avoid

1. **Mixing instructions with data** - Always use XML tags
2. **Vague instructions** - Be specific and direct
3. **No examples** - Show, don't just tell
4. **Inconsistent formatting** - Use same tags throughout
5. **Asking for impossible tasks** - Give Claude an "out" when it doesn't know
6. **No thinking space** - Allow Claude to reason in `<thinking>` tags
7. **Assuming knowledge** - Provide context explicitly

## Template for Complex Prompts

```python
SYSTEM = """
[Role and expertise]
[Main goals]
"""

PROMPT = """
[Task context - what you're doing and why]

[Detailed instructions with specific rules]

<examples>
<example>
[Input example 1]
[Output example 1]
</example>
<example>
[Input example 2]
[Output example 2]
</example>
</examples>

<input>
{user_data}
</input>

[Immediate task - what to do right now]

Before providing your final answer:
1. Analyze in <thinking> tags
2. Consider edge cases
3. Check for ambiguities

Provide your response in <output> tags.
"""
```

## Key Takeaways

1. **XML tags are mandatory** for separating data from instructions
2. **Examples > Rules** - Few-shot prompting is most effective
3. **Think before answering** - Use `<thinking>` tags for complex tasks
4. **Be direct and specific** - Don't assume Claude knows what you want
5. **Structure matters** - Order prompt elements logically
6. **Prefill for format** - Start Claude's response to control output
7. **Handle uncertainty** - Give Claude permission to say "I don't know"
