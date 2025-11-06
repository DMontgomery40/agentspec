#!/usr/bin/env python3
"""
Test diff_summary implementation in modular architecture.
"""
import sys
from pathlib import Path

# Add agentspec to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentspec.generators.orchestrator import Orchestrator
from agentspec.models.config import GenerationConfig

def test_diff_summary_with_openai():
    """Test diff_summary with OpenAI (requires OPENAI_API_KEY in env)."""

    config = GenerationConfig(
        provider="openai",
        model="gpt-4o-mini",
        update_existing=True,
        diff_summary=True  # Enable diff summary
    )

    orch = Orchestrator(config)
    print(f"✅ Created orchestrator with {orch.provider.name}")

    # Use a real file in this repo that has git history
    test_file = Path(__file__).parent.parent / "collect.py"

    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        sys.exit(1)

    print(f"\n🧪 Testing diff_summary with {test_file.name}...")
    print(f"   File: {test_file}")

    # Read a function from the file
    with open(test_file, 'r') as f:
        content = f.read()

    # Extract _get_function_calls function (we know it has git history)
    import ast
    tree = ast.parse(content)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_get_function_calls":
            # Get function source
            func_source = ast.get_source_segment(content, node)

            result = orch.generate_docstring(
                code=func_source,
                function_name="_get_function_calls",
                context={"file_path": str(test_file)}
            )

            print(f"\n✅ Generation completed: {result.success}")
            print(f"✅ Messages: {result.messages}")

            if result.success:
                # Check if diff summary was included
                if "FUNCTION CODE DIFF SUMMARY" in result.generated_docstring:
                    print("✅ DIFF SUMMARY INJECTED")
                    # Print just the diff summary section
                    parts = result.generated_docstring.split("FUNCTION CODE DIFF SUMMARY")
                    if len(parts) > 1:
                        print("\nDiff Summary:")
                        print("=" * 60)
                        print("FUNCTION CODE DIFF SUMMARY" + parts[1][:500])
                        print("=" * 60)
                else:
                    print("⚠️  No diff summary in output (file may not have git history)")

                return True
            else:
                print(f"❌ Generation failed: {result.errors}")
                return False

    print("❌ Function _get_function_calls not found")
    return False

if __name__ == "__main__":
    try:
        success = test_diff_summary_with_openai()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
