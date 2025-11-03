from IPython.display import Javascript, display
from ipywidgets import Button, Layout


def create_ui_only_toggle(button_text: str = "UI only") -> Button:
    """
    Create a small button that toggles a UI-only mode in Jupyter frontends.

    ---agentspec
    what: |
      Returns an ipywidgets Button configured with an on-click handler that
      toggles the CSS class 'ui-only' on document.body using a Javascript
      snippet. When the class is present, notebook CSS can hide everything
      except the primary UI container. The function does not alter global
      state until the button is clicked, making it safe to import.

    deps:
      imports:
        - IPython.display.Javascript
        - IPython.display.display
        - ipywidgets.Button
        - ipywidgets.Layout

    why: |
      Encapsulating the toggle logic in a reusable function allows unit
      testing outside of the notebook runtime and avoids repeatedly embedding
      anonymous JS strings. It centralizes the 'ui-only' behavior so that
      future changes (e.g., class name or script) occur in one place.

    guardrails:
      - DO NOT execute Javascript on import; only when button is clicked.
      - KEEP the CSS class name 'ui-only' stable; CSS relies on it.
      - USE IPython.display.Javascript and display(); avoid other side effects.

    changelog:
      - "2025-11-03: Added create_ui_only_toggle for UI-only notebook mode"
    ---/agentspec
    """

    button = Button(
        description=button_text,
        tooltip="Toggle UI-only view",
        layout=Layout(width="auto"),
    )

    def _on_click(_):
        # Overlay approach: move the UI container into a fullscreen overlay
        js = (
            "(function(){\n"
            "  const OVERLAY_ID='agentspec-overlay';\n"
            "  const PLACEHOLDER_ID='agentspec-placeholder';\n"
            "  const overlay = document.getElementById(OVERLAY_ID);\n"
            "  if (overlay) {\n"
            "    // Disable UI-only: move back and remove overlay\n"
            "    const container = overlay.querySelector('.dark-notebook');\n"
            "    const ph = document.getElementById(PLACEHOLDER_ID);\n"
            "    if (container && ph && ph.parentNode) { ph.parentNode.insertBefore(container, ph); }\n"
            "    if (ph && ph.parentNode) { ph.parentNode.removeChild(ph); }\n"
            "    overlay.remove();\n"
            "    document.body.classList.remove('agentspec-ui-only');\n"
            "    return;\n"
            "  }\n"
            "  // Enable UI-only\n"
            "  const containers = document.querySelectorAll('.dark-notebook');\n"
            "  const container = containers.length ? containers[containers.length - 1] : null;\n"
            "  if (!container) { console.warn('agentspec: no .dark-notebook found'); return; }\n"
            "  const ph = document.createElement('div'); ph.id = PLACEHOLDER_ID;\n"
            "  container.parentNode.insertBefore(ph, container);\n"
            "  const ov = document.createElement('div');\n"
            "  ov.id = OVERLAY_ID;\n"
            "  ov.style.position='fixed'; ov.style.inset='0'; ov.style.background='#0f0f0f';\n"
            "  ov.style.overflow='auto'; ov.style.padding='16px'; ov.style.zIndex='99999';\n"
            "  document.body.appendChild(ov);\n"
            "  ov.appendChild(container);\n"
            "  container.style.margin='0';\n"
            "  document.body.classList.add('agentspec-ui-only');\n"
            "})();"
        )
        display(Javascript(js))

    button.on_click(_on_click)
    return button


