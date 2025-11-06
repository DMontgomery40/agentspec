#!/usr/bin/env python3
"""
End-to-end smoke test for modular architecture.

Tests ACTUAL LLM generation (not dry run).
"""
import sys
from pathlib import Path

# Add agentspec to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentspec.generators.orchestrator import Orchestrator
from agentspec.models.config import GenerationConfig

def test_with_openai():
    """Test end-to-end with OpenAI (requires OPENAI_API_KEY in env)."""
    
    config = GenerationConfig(
        provider="openai",
        model="gpt-4o-mini",
        update_existing=True
    )
    
    orch = Orchestrator(config)
    print(f"✅ Created orchestrator with {orch.provider.name}")
    
    # Test code with dependencies
    test_code = """def process_data(data):
    import json
    from pathlib import Path
    
    result = json.loads(data)
    path = Path('/tmp/output.json')
    path.write_text(data)
    return len(result)"""
    
    print("\n🧪 Running end-to-end test...")
    
    result = orch.generate_docstring(
        code=test_code,
        function_name="process_data",
        context={"file_path": "/tmp/test.py"}
    )
    
    assert result.success, f"Generation failed: {result.errors}"
    assert result.generated_docstring, "No docstring generated"
    assert "DEPENDENCIES" in result.generated_docstring, "No dependencies section"
    assert "Path" in result.generated_docstring, "Dependencies not extracted"
    
    print("✅ END-TO-END TEST PASSED")
    print(f"✅ Generated {len(result.generated_docstring)} chars")
    print("✅ Metadata injection works")
    return True

if __name__ == "__main__":
    try:
        test_with_openai()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
