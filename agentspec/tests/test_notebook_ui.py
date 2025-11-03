"""
Tests for the reusable UI-only toggle used in the notebook.

---agentspec
what: |
  Verifies that create_ui_only_toggle returns a Button, registers a click
  handler, and when clicked emits an IPython Javascript object that toggles
  the 'ui-only' CSS class. This proves the exact behavior used by the
  notebook's Cell 2 without needing a browser DOM.

deps:
  imports:
    - agentspec.notebook_ui.create_ui_only_toggle
    - IPython.display.Javascript
    - ipywidgets.Button

why: |
  The notebook relies on this helper to manage UI-only mode. Testing it in a
  small unit test ensures regressions are caught without executing a full UI.

guardrails:
  - DO NOT depend on a live Jupyter frontend; we only assert Python-side facts
  - KEEP the toggle string 'document.body.classList.toggle(\'ui-only\')'

changelog:
  - "2025-11-03: Initial tests for UI-only toggle"
---/agentspec
"""

from IPython.display import Javascript
from agentspec.notebook_ui import create_ui_only_toggle


def test_create_ui_only_toggle_button_and_click(monkeypatch):
    displayed = {}

    def fake_display(obj):
        # Capture the last displayed object
        displayed["obj"] = obj

    # Patch the display function inside the module under test
    import agentspec.notebook_ui as ui

    monkeypatch.setattr(ui, "display", fake_display)

    btn = create_ui_only_toggle("UI only")

    # Ensure a handler was registered (ipywidgets stores callbacks internally)
    assert hasattr(btn, "_click_handlers")
    assert len(btn._click_handlers.callbacks) >= 1

    # Simulate a click; this should call our fake display with Javascript
    btn.click()
    assert isinstance(displayed.get("obj"), Javascript)
    js_src = displayed["obj"].data
    # Should contain overlay logic and .dark-notebook handling
    assert "agentspec-overlay" in js_src
    assert "agentspec-placeholder" in js_src
    assert ".dark-notebook" in js_src
    assert "appendChild" in js_src


