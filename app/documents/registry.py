"""Template registry — central definition of available document templates.

To add a new template:
1. Add its name → label entry to TEMPLATES.
2. Create the HTML files: doc_checkout_{name}.html and doc_return_{name}.html
   (they extend doc_base.html just like the default ones).
3. If the DOCX layout should differ, add a branch in checkout.py / return_form.py.
"""

from __future__ import annotations

# name → display label (order preserved — first entry is the default)
TEMPLATES: dict[str, str] = {
    "uwagi": "Uwagi",
    "eve": "Eve",
}

DEFAULT_TEMPLATE = "uwagi"


def available_templates() -> list[tuple[str, str]]:
    """Return list of (id, label) pairs for all registered templates."""
    return list(TEMPLATES.items())


def checkout_pdf_template(template: str) -> str:
    """Return the Jinja2 HTML template filename for checkout PDF."""
    if template == "uwagi" or template not in TEMPLATES:
        return "doc_checkout.html"
    return f"doc_checkout_{template}.html"


def return_pdf_template(template: str) -> str:
    """Return the Jinja2 HTML template filename for return PDF."""
    if template == "uwagi" or template not in TEMPLATES:
        return "doc_return.html"
    return f"doc_return_{template}.html"
