#!/usr/bin/env python3
"""
Simple test for diff_summary implementation.
"""
import sys
from pathlib import Path

# Add agentspec to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentspec.generators.orchestrator import Orchestrator
from agentspec.models.config import GenerationConfig

def test_diff_summary():
    """Test diff_summary with a simple function."""

    config = GenerationConfig(
        provider="openai",
        model="gpt-4o-mini",
        update_existing=True,
        diff_summary=True  # Enable diff summary
    )

    orch = Orchestrator(config)
    print(f"✅ Created orchestrator with {orch.provider.name}")

    # Simple test function
    test_code = """def add_numbers(a, b):
    return a + b"""

    # Use a real file path that has git history
    test_file = Path(__file__).parent.parent / "collect.py"

    print(f"\n🧪 Testing diff_summary...")
    print(f"   Note: Using {test_file.name} for git context")

    result = orch.generate_docstring(
        code=test_code,
        function_name="_get_function_calls",  # Use function that exists in collect.py
        context={"file_path": str(test_file)}
    )

    print(f"\n✅ Generation completed: {result.success}")
    print(f"   Messages: {len(result.messages)} messages")
    for msg in result.messages:
        print(f"   - {msg}")

    if result.success:
        print(f"\n✅ Generated {len(result.generated_docstring)} chars")

        # Check if diff summary was included
        if "FUNCTION CODE DIFF SUMMARY" in result.generated_docstring:
            print("✅ DIFF SUMMARY FOUND IN OUTPUT")

            # Print just the diff summary section
            parts = result.generated_docstring.split("FUNCTION CODE DIFF SUMMARY")
            if len(parts) > 1:
                print("\n" + "=" * 60)
                print("FUNCTION CODE DIFF SUMMARY" + parts[1][:300])
                print("=" * 60)
        else:
            print("⚠️  No diff summary in output")
            print("\nFull docstring preview:")
            print(result.generated_docstring[:500])

        return True
    else:
        print(f"❌ Generation failed: {result.errors}")
        return False

if __name__ == "__main__":
    try:
        success = test_diff_summary()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
