#!/usr/bin/env python3
"""
Auto-generate verbose agentspec docstrings using Claude.
"""
import ast
import sys
import os
from pathlib import Path
from anthropic import Anthropic

# Initialize Claude client
client = Anthropic()  # Reads ANTHROPIC_API_KEY from env

GENERATION_PROMPT = """You are helping to document a Python codebase with extremely verbose docstrings designed for AI agent consumption.

Analyze this function and generate a comprehensive docstring following this EXACT format:

\"\"\"
Brief one-line description.

WHAT THIS DOES:
- Detailed explanation of what this function does (3-5 lines)
- Include edge cases, error handling, return values
- Be specific about types and data flow

DEPENDENCIES:
- Called by: [list files/functions that call this, if you can infer from context]
- Calls: [list functions this calls]
- Imports used: [key imports this relies on]
- External services: [APIs, databases, etc. if applicable]

WHY THIS APPROACH:
- Explain why this implementation was chosen
- Note any alternatives that were NOT used and why
- Document performance considerations
- Explain any "weird" or non-obvious code

CHANGELOG:
- [Current date]: Initial implementation (or describe what changed)

AGENT INSTRUCTIONS:
- DO NOT [list things agents should not change]
- ALWAYS [list things agents must preserve]
- NOTE: [any critical warnings about this code]
\"\"\"

Here's the function to document:

```python
{code}
```

File context: {filepath}

Generate ONLY the docstring content (without the triple quotes themselves). Be extremely verbose and thorough."""

def extract_function_info(filepath: Path) -> list[tuple[int, str, str]]:
    """
    Extract information about all functions in a file that need docstrings.
    Returns list of (lineno, name, source_code) tuples, sorted bottom-to-top.
    """
    with open(filepath, 'r') as f:
        source = f.read()
    
    tree = ast.parse(source)
    functions = []
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Check if needs docstring
            existing = ast.get_docstring(node)
            if not existing or len(existing.split('\n')) < 5:
                # Get source code
                lines = source.split('\n')
                func_lines = lines[node.lineno - 1:node.end_lineno]
                code = '\n'.join(func_lines)
                functions.append((node.lineno, node.name, code))
    
    # Sort by line number DESCENDING (bottom to top)
    # This way inserting docstrings doesn't invalidate later line numbers
    functions.sort(key=lambda x: x[0], reverse=True)
    
    return functions

def generate_docstring(code: str, filepath: str, model: str = "claude-sonnet-4-20250514") -> str:
    """Use Claude to generate a verbose docstring."""
    
    message = client.messages.create(
        model=model,
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": GENERATION_PROMPT.format(
                code=code,
                filepath=filepath
            )
        }]
    )
    
    return message.content[0].text

def insert_docstring_at_line(filepath: Path, lineno: int, func_name: str, docstring: str, force_context: bool = False):
    """
    Insert docstring at a specific line number in a file.
    This handles the actual file modification.
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Find the function definition line
    func_line_idx = lineno - 1
    
    # Find the first line after the function signature (where docstring goes)
    insert_idx = func_line_idx + 1
    
    # Skip any existing docstring if present
    if insert_idx < len(lines):
        line = lines[insert_idx].strip()
        if line.startswith('"""') or line.startswith("'''"):
            quote_type = '"""' if '"""' in line else "'''"
            # Skip existing docstring
            if line.count(quote_type) >= 2:
                # Single-line docstring
                insert_idx += 1
            else:
                # Multi-line docstring - find end
                insert_idx += 1
                while insert_idx < len(lines):
                    if quote_type in lines[insert_idx]:
                        insert_idx += 1
                        break
                    insert_idx += 1
            
            # Also skip any existing context print
            if insert_idx < len(lines) and '[AGENTSPEC_CONTEXT]' in lines[insert_idx]:
                insert_idx += 1
            
            # Delete the old docstring and print
            del lines[func_line_idx + 1:insert_idx]
            insert_idx = func_line_idx + 1
    
    # Determine indentation
    func_line = lines[func_line_idx]
    base_indent = len(func_line) - len(func_line.lstrip())
    indent = ' ' * (base_indent + 4)  # Function body indent
    
    # Format new docstring
    new_lines = []
    new_lines.append(f'{indent}"""\n')
    for line in docstring.split('\n'):
        if line.strip():
            new_lines.append(f'{indent}{line}\n')
        else:
            new_lines.append('\n')
    new_lines.append(f'{indent}"""\n')
    
    # Add context print if requested
    if force_context:
        # Extract key bullet points
        sections = []
        for line in docstring.split('\n'):
            line = line.strip()
            if line.startswith('-') and len(sections) < 3:
                sections.append(line[1:].strip())
        
        # Properly escape the content for the print statement
        print_content = ' | '.join(sections)
        # Escape quotes and backslashes
        print_content = print_content.replace('\\', '\\\\').replace('"', '\\"')
        
        new_lines.append(f'{indent}print(f"[AGENTSPEC_CONTEXT] {func_name}: {print_content}")\n')
    
    # Insert the new docstring
    for line in reversed(new_lines):
        lines.insert(insert_idx, line)
    
    # Write back
    with open(filepath, 'w') as f:
        f.writelines(lines)

def process_file(filepath: Path, dry_run: bool = False, force_context: bool = False, model: str = "claude-sonnet-4-20250514"):
    """Process a single file and generate docstrings."""
    print(f"\n📄 Processing {filepath}")
    
    try:
        functions = extract_function_info(filepath)
    except SyntaxError as e:
        print(f"  ❌ Syntax error in file: {e}")
        return
    
    if not functions:
        print("  ✅ All functions already have verbose docstrings")
        return
    
    print(f"  Found {len(functions)} functions needing docstrings:")
    for lineno, name, _ in functions:
        print(f"    - {name} (line {lineno})")
    
    if force_context:
        print("  🔊 Context-forcing print() statements will be added")
    
    print(f"  🤖 Using model: {model}")
    
    if dry_run:
        return
    
    # Process bottom-to-top (already sorted that way)
    for lineno, name, code in functions:
        print(f"\n  🤖 Generating docstring for {name}...")
        
        try:
            docstring = generate_docstring(code, str(filepath), model=model)
            insert_docstring_at_line(filepath, lineno, name, docstring, force_context=force_context)
            
            if force_context:
                print(f"  ✅ Added docstring + context print to {name}")
            else:
                print(f"  ✅ Added docstring to {name}")
        except Exception as e:
            print(f"  ❌ Error processing {name}: {e}")

def run(target: str, dry_run: bool = False, force_context: bool = False, model: str = "claude-sonnet-4-20250514") -> int:
    """
    CLI entry point for generating docstrings.
    
    Args:
        target: File or directory path
        dry_run: If True, preview only without modifying files
        force_context: If True, add print() statements to force context loading
        model: Claude model to use for generation
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ Error: ANTHROPIC_API_KEY environment variable not set")
        print("Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        return 1
    
    path = Path(target)
    
    if not path.exists():
        print(f"❌ Error: Path does not exist: {target}")
        return 1
    
    if dry_run:
        print("🔍 DRY RUN MODE - no files will be modified\n")
    
    try:
        if path.is_file():
            process_file(path, dry_run, force_context, model)
        else:
            for filepath in path.rglob("*.py"):
                try:
                    process_file(filepath, dry_run, force_context, model)
                except Exception as e:
                    print(f"❌ Error processing {filepath}: {e}")
        
        print("\n✅ Done!")
        return 0
    
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        return 1

def main():
    """Standalone script entry point."""
    if len(sys.argv) < 2:
        print("Usage: python generate.py <file_or_dir> [--dry-run] [--force-context] [--model MODEL]")
        print("\nRequires ANTHROPIC_API_KEY environment variable")
        print("\nOptions:")
        print("  --dry-run           Preview without modifying files")
        print("  --force-context     Add print() statements to force LLMs to load context")
        print("  --model MODEL       Claude model to use (default: claude-sonnet-4-20250514)")
        print("                      Options: claude-haiku-4-5, claude-3-5-sonnet-20241022, claude-3-5-haiku-20241022")
        sys.exit(1)
    
    path = sys.argv[1]
    dry_run = '--dry-run' in sys.argv
    force_context = '--force-context' in sys.argv
    
    # Parse model flag
    model = "claude-sonnet-4-20250514"
    if '--model' in sys.argv:
        model_index = sys.argv.index('--model')
        if model_index + 1 < len(sys.argv):
            model = sys.argv[model_index + 1]
    
    exit_code = run(path, dry_run, force_context, model)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
