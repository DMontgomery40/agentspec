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

def generate_docstring(code: str, filepath: str) -> str:
    """Use Claude to generate a verbose docstring."""
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
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

def insert_docstring(filepath: Path, node: ast.FunctionDef, docstring: str):
    """Insert or replace docstring in function."""
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Find where to insert docstring (right after function definition)
    func_line = node.lineno - 1
    
    # Check if there's already a docstring
    existing_docstring = ast.get_docstring(node)
    
    if existing_docstring:
        # Find and replace existing docstring
        # This is tricky - we need to find the docstring location
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
        
        # Remove old docstring
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
    
    # Insert new docstring
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

def process_file(filepath: Path, dry_run: bool = False):
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
    
    if dry_run:
        return
    
    for lineno, name in finder.functions:
        print(f"\n  🤖 Generating docstring for {name}...")
        
        try:
            code, node = extract_function_code(filepath, lineno)
            docstring = generate_docstring(code, str(filepath))
            insert_docstring(filepath, node, docstring)
            print(f"  ✅ Added docstring to {name}")
        except Exception as e:
            print(f"  ❌ Error processing {name}: {e}")

def run(target: str, dry_run: bool = False) -> int:
    """
    CLI entry point for generating docstrings.
    
    Args:
        target: File or directory path
        dry_run: If True, preview only without modifying files
    
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
            process_file(path, dry_run)
        else:
            for filepath in path.rglob("*.py"):
                try:
                    process_file(filepath, dry_run)
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
        print("Usage: python generate.py <file_or_dir> [--dry-run]")
        print("\nRequires ANTHROPIC_API_KEY environment variable")
        sys.exit(1)
    
    path = sys.argv[1]
    dry_run = '--dry-run' in sys.argv
    
    exit_code = run(path, dry_run)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
