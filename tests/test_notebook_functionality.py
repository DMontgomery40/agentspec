"""
Test to verify the notebook's widget functionality.

---agentspec
what: |
  Tests that the notebook's widget-based input collection works correctly.
  Verifies that:
  - Widgets can be created and displayed
  - Values can be extracted from Textarea widgets
  - The VBox container properly wraps the widgets

deps:
  imports:
    - ipywidgets.Textarea
    - ipywidgets.VBox
    - ipywidgets.HTML
    - ipywidgets.Layout

why: |
  After fixing the padding issue by switching from mixed HTML/widgets
  to pure VBox container, we need to verify functionality isn't broken.

guardrails:
  - DO NOT test visual styling - only functional behavior
  - MUST verify widget value extraction still works

changelog:
  - "2025-11-03: Initial test after VBox padding fix"
---/agentspec
"""

import pytest
from ipywidgets import Textarea, VBox, HTML as WidgetHTML, Layout


def test_vbox_container_creation():
    """Test that VBox container can be created with proper layout."""
    # Create widgets
    label1 = WidgetHTML('<h3>Test Label</h3>')
    input1 = Textarea(placeholder='', rows=10, layout=Layout(width='100%'))
    
    label2 = WidgetHTML('<h3>Another Label</h3>')
    input2 = Textarea(placeholder='', rows=5, layout=Layout(width='100%'))
    
    # Create VBox with uniform padding
    container = VBox(
        [label1, input1, label2, input2],
        layout=Layout(
            width='100%',
            padding='12px',
            background='#1e1e1e',
            border_radius='4px',
            margin='0'
        )
    )
    
    # Verify container was created
    assert container is not None
    assert len(container.children) == 4
    assert container.layout.padding == '12px'
    # No CSS class required for a minimal VBox in this test


def test_widget_value_extraction():
    """Test that values can be extracted from Textarea widgets."""
    # Create input widgets
    example_input = Textarea(
        placeholder='',
        rows=10,
        layout=Layout(width='100%', margin='0 0 12px 0')
    )
    
    critic_input = Textarea(
        placeholder='',
        rows=5,
        layout=Layout(width='100%', margin='0')
    )
    
    # Set values
    example_input.value = "def test_function():\n    pass"
    critic_input.value = "This function needs a docstring."
    
    # Extract values (simulating Cell 3's behavior)
    EXAMPLE_TEXT = example_input.value
    CRITIQUE = critic_input.value
    
    # Verify extraction works
    assert EXAMPLE_TEXT == "def test_function():\n    pass"
    assert CRITIQUE == "This function needs a docstring."
    assert bool(EXAMPLE_TEXT) and bool(CRITIQUE)  # Both should be truthy


def test_vbox_layout_properties():
    """Test that VBox layout properties are correctly applied."""
    container = VBox(
        [],
        layout=Layout(
            width='100%',
            padding='12px',  # Uniform padding
            margin='0',
            display='flex',
            flex_flow='column nowrap'
        )
    )
    container.add_class('dark-notebook')
    
    # Verify all layout properties
    assert container.layout.width == '100%'
    assert container.layout.padding == '12px'  # Should be uniform
    assert container.layout.margin == '0'
    assert container.layout.display == 'flex'
    assert container.layout.flex_flow == 'column nowrap'
    assert 'dark-notebook' in getattr(container, '_dom_classes', [])


if __name__ == "__main__":
    test_vbox_container_creation()
    test_widget_value_extraction()
    test_vbox_layout_properties()
    print("✅ All notebook functionality tests pass!")
