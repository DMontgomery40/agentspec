#!/usr/bin/env python3
"""
Smoke tests for collectors architecture.

Demonstrates how collectors extract deterministic metadata from code.
"""

import ast
from pathlib import Path

# Collectors
from agentspec.collectors import CollectorOrchestrator
from agentspec.collectors.code_analysis import (
    SignatureCollector,
    ExceptionCollector,
    DecoratorCollector,
    ComplexityCollector,
    TypeAnalysisCollector,
)


def test_signature_collector():
    """Test signature collector extracts parameters correctly."""
    code = """
def process_data(x: int, y: str = "default", *args, **kwargs) -> bool:
    return True
"""

    tree = ast.parse(code)
    func_node = tree.body[0]

    collector = SignatureCollector()
    result = collector.collect(func_node, {})

    sig = result["signature"]
    params = sig["parameters"]

    # Check parameters extracted
    assert len(params) == 4
    assert params[0]["name"] == "x"
    assert params[0]["type"] == "int"
    assert params[1]["name"] == "y"
    assert params[1]["default"] == "'default'"
    assert params[2]["kind"] == "var_positional"
    assert params[3]["kind"] == "var_keyword"

    # Check return type
    assert sig["return_type"] == "bool"
    assert sig["is_async"] == False

    print("\n✅ Signature collector test passed")
    print(f"   Extracted {len(params)} parameters")
    print(f"   Return type: {sig['return_type']}")


def test_exception_collector():
    """Test exception collector finds all raise statements."""
    code = """
def validate_input(data):
    if not data:
        raise ValueError("Data cannot be empty")

    if not isinstance(data, dict):
        raise TypeError

    return data
"""

    tree = ast.parse(code)
    func_node = tree.body[0]

    collector = ExceptionCollector()
    result = collector.collect(func_node, {})

    exceptions = result["exceptions"]

    # Check exceptions extracted
    assert len(exceptions) == 2
    assert exceptions[0]["type"] == "ValueError"
    assert "empty" in exceptions[0]["message"]
    assert exceptions[1]["type"] == "TypeError"

    print("\n✅ Exception collector test passed")
    print(f"   Found {len(exceptions)} exceptions")
    for exc in exceptions:
        print(f"   - {exc['type']}: {exc['message']}")


def test_decorator_collector():
    """Test decorator collector extracts decorators."""
    code = """
@lru_cache(maxsize=128)
@timing
def expensive_computation(n):
    return n ** 2
"""

    tree = ast.parse(code)
    func_node = tree.body[0]

    collector = DecoratorCollector()
    result = collector.collect(func_node, {})

    decorators = result["decorators"]

    # Check decorators extracted
    assert len(decorators) == 2
    assert decorators[0]["name"] == "lru_cache"
    assert "maxsize=128" in decorators[0]["args"]
    assert decorators[1]["name"] == "timing"

    print("\n✅ Decorator collector test passed")
    print(f"   Found {len(decorators)} decorators")
    for dec in decorators:
        print(f"   - {dec['full']}")


def test_complexity_collector():
    """Test complexity collector calculates metrics."""
    code = """
def complex_function(x):
    if x > 0:
        if x > 10:
            return "high"
        else:
            return "medium"
    else:
        return "low"
"""

    tree = ast.parse(code)
    func_node = tree.body[0]

    collector = ComplexityCollector()
    result = collector.collect(func_node, {})

    complexity = result["complexity"]

    # Check metrics calculated
    assert complexity["cyclomatic_complexity"] > 1
    assert complexity["lines_of_code"] > 1

    print("\n✅ Complexity collector test passed")
    print(f"   Cyclomatic complexity: {complexity['cyclomatic_complexity']}")
    print(f"   Lines of code: {complexity['lines_of_code']}")


def test_type_analysis_collector():
    """Test type analysis collector measures type hint coverage."""
    code = """
def mixed_types(a: int, b, c: str = "default") -> int:
    return a + len(c)
"""

    tree = ast.parse(code)
    func_node = tree.body[0]

    collector = TypeAnalysisCollector()
    result = collector.collect(func_node, {})

    type_analysis = result["type_analysis"]

    # Check coverage calculated
    assert type_analysis["parameters_total"] == 3
    assert type_analysis["parameters_typed"] == 2  # a and c are typed, b is not
    assert type_analysis["parameter_coverage_percent"] == 66.7
    assert type_analysis["has_return_type"] == True

    print("\n✅ Type analysis collector test passed")
    print(f"   Type coverage: {type_analysis['parameter_coverage_percent']}%")
    print(f"   Has return type: {type_analysis['has_return_type']}")


def test_orchestrator():
    """Test orchestrator runs all collectors and aggregates results."""
    code = """
@lru_cache(maxsize=128)
def compute(x: int, y: int = 0) -> int:
    if x < 0:
        raise ValueError("x must be non-negative")
    return x + y
"""

    tree = ast.parse(code)
    func_node = tree.body[0]

    # Create orchestrator and register collectors
    orchestrator = CollectorOrchestrator()
    orchestrator.register(SignatureCollector())
    orchestrator.register(ExceptionCollector())
    orchestrator.register(DecoratorCollector())
    orchestrator.register(ComplexityCollector())
    orchestrator.register(TypeAnalysisCollector())

    # Collect metadata
    metadata = orchestrator.collect_all(
        func_node,
        context={
            "function_name": "compute",
            "file_path": Path("test.py")
        }
    )

    # Verify all categories populated
    assert "signature" in metadata.code_analysis
    assert "exceptions" in metadata.code_analysis
    assert "decorators" in metadata.code_analysis
    assert "complexity" in metadata.code_analysis
    assert "type_analysis" in metadata.code_analysis

    print("\n✅ Orchestrator test passed")
    print(f"   Function: {metadata.function_name}")
    print(f"   Collected categories: {list(metadata.code_analysis.keys())}")
    print(f"\n   Signature: {len(metadata.code_analysis['signature']['parameters'])} params")
    print(f"   Exceptions: {len(metadata.code_analysis['exceptions'])} found")
    print(f"   Decorators: {len(metadata.code_analysis['decorators'])} found")
    print(f"   Complexity: {metadata.code_analysis['complexity']['cyclomatic_complexity']}")
    print(f"   Type coverage: {metadata.code_analysis['type_analysis']['parameter_coverage_percent']}%")


if __name__ == "__main__":
    print("=" * 60)
    print("COLLECTORS SMOKE TESTS")
    print("=" * 60)

    test_signature_collector()
    test_exception_collector()
    test_decorator_collector()
    test_complexity_collector()
    test_type_analysis_collector()
    test_orchestrator()

    print("\n" + "=" * 60)
    print("ALL COLLECTOR TESTS PASSED ✅")
    print("=" * 60)
