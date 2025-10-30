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

def extract_function_code(filepath: Path, lineno: int) -> tuple[str, ast.FunctionDef]:
    """Extract the source code for a specific function."""
    with open(filepath, 'r') as f:
        source = f.read()
    
    tree = ast.parse(source)
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.lineno == lineno:
                # Get the function's source code
                lines = source.split('\n')
                func_lines = lines[node.lineno - 1:node.end_lineno]
                return '\n'.join(func_lines), node
    
    raise ValueError(f"No function found at line {lineno}")

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

def insert_docstring(filepath: Path, node: ast.FunctionDef, docstring: str, force_context: bool = False):
    """Insert or replace docstring in function, optionally adding context print."""
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Find where to insert docstring (right after function definition)
    func_line = node.lineno - 1
    
    # Check if there's already a docstring
    existing_docstring = ast.get_docstring(node)
    
    if existing_docstring:
        # Find and replace existing docstring
        start_line = func_line + 1
        
        # Skip decorators and find the actual def line
        for i in range(func_line, len(lines)):
            if 'def ' in lines[i]:
                start_line = i + 1
                break
        
        # Find end of existing docstring
        in_docstring = False
        quote_type = None
        end_line = start_line
        
        for i in range(start_line, len(lines)):
            line = lines[i].strip()
            
            if not in_docstring:
                if line.startswith('"""') or line.startswith("'''"):
                    in_docstring = True
                    quote_type = '"""' if '"""' in line else "'''"
                    if line.count(quote_type) >= 2:
                        # Single line docstring
                        end_line = i + 1
                        break
            else:
                if quote_type in line:
                    end_line = i + 1
                    break
        
        # Check if there's already a context print statement after docstring
        has_context_print = False
        if end_line < len(lines):
            next_line = lines[end_line].strip()
            if 'print(f"[AGENTSPEC_CONTEXT]' in next_line or 'print("[AGENTSPEC_CONTEXT]' in next_line:
                has_context_print = True
                end_line += 1  # Include the print line in deletion
        
        # Remove old docstring (and old print if exists)
        del lines[start_line:end_line]
        insert_line = start_line
    else:
        # Find insertion point (after function definition line)
        for i in range(func_line, len(lines)):
            if 'def ' in lines[i] or 'async def' in lines[i]:
                insert_line = i + 1
                break
    
    # Format new docstring
    indent = '    '  # Assuming 4-space indent
    formatted = f'{indent}"""\n'
    for line in docstring.split('\n'):
        formatted += f'{indent}{line}\n'
    formatted += f'{indent}"""\n'
    
    # Add context-forcing print if requested
    if force_context:
        # Extract key sections for print
        sections_to_print = []
        current_section = None
        
        for line in docstring.split('\n'):
            line = line.strip()
            if line.startswith('WHAT THIS DOES:'):
                current_section = 'WHAT_THIS_DOES'
            elif line.startswith('DEPENDENCIES:'):
                current_section = 'DEPENDENCIES'
            elif line.startswith('WHY THIS APPROACH:'):
                current_section = 'WHY_APPROACH'
            elif line.startswith('AGENT INSTRUCTIONS:'):
                current_section = 'AGENT_INSTRUCTIONS'
            elif line.startswith('CHANGELOG:'):
                current_section = None  # Skip changelog in prints
            elif current_section and line.startswith('-'):
                sections_to_print.append(line)
        
        # Add print statement that forces context
        func_name = node.name
        print_content = ' | '.join(sections_to_print[:3])  # First 3 bullet points
        formatted += f'{indent}print(f"[AGENTSPEC_CONTEXT] {func_name}: {print_content}")\n'
    
    # Insert new docstring (and print if applicable)
    lines.insert(insert_line, formatted)
    
    # Write back
    with open(filepath, 'w') as f:
        f.writelines(lines)

class FunctionFinder(ast.NodeVisitor):
    """Find all functions that need docstrings."""
    def __init__(self):
        self.functions = []
    
    def visit_FunctionDef(self, node):
        if not ast.get_docstring(node) or len(ast.get_docstring(node).split('\n')) < 5:
            self.functions.append((node.lineno, node.name))
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        if not ast.get_docstring(node) or len(ast.get_docstring(node).split('\n')) < 5:
            self.functions.append((node.lineno, node.name))
        self.generic_visit(node)

def process_file(filepath: Path, dry_run: bool = False, force_context: bool = False, model: str = "claude-sonnet-4-20250514"):
    """Process a single file and generate docstrings."""
    print(f"\n📄 Processing {filepath}")
    
    with open(filepath, 'r') as f:
        tree = ast.parse(f.read())
    
    finder = FunctionFinder()
    finder.visit(tree)
    
    if not finder.functions:
        print("  ✅ All functions already have verbose docstrings")
        return
    
    print(f"  Found {len(finder.functions)} functions needing docstrings:")
    for lineno, name in finder.functions:
        print(f"    - {name} (line {lineno})")
    
    if force_context:
        print("  🔊 Context-forcing print() statements will be added")
    
    print(f"  🤖 Using model: {model}")
    
    if dry_run:
        return
    
    for lineno, name in finder.functions:
        print(f"\n  🤖 Generating docstring for {name}...")
        
        try:
            code, node = extract_function_code(filepath, lineno)
            docstring = generate_docstring(code, str(filepath), model=model)
            insert_docstring(filepath, node, docstring, force_context=force_context)
            
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
        print("                      Options: claude-haiku-4-5-20250929, claude-sonnet-4-5-20250929")
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
