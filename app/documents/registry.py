"""Template registry — central definition of available document templates.

To add a new template:
1. Add its name → label entry to TEMPLATES.
2. Create the HTML files: doc_checkout_{name}.html and doc_return_{name}.html
   (they extend doc_base.html just like the default ones).
3. If the DOCX layout should differ, add a branch in checkout.py / return_form.py.
"""

from __future__ import annotations

from pathlib import Path

_TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "documents"

# name → display label (order preserved — first entry is the default)
TEMPLATES: dict[str, str] = {
    "unagi": "Unagi",
    "eve": "Eve",
}

DEFAULT_TEMPLATE = "unagi"


def available_templates() -> list[tuple[str, str]]:
    """Return list of (id, label) pairs for templates whose directories exist on disk."""
    return [(name, label) for name, label in TEMPLATES.items() if (_TEMPLATES_DIR / name).is_dir()]


def checkout_pdf_template(template: str) -> str:
    """Return the Jinja2 template path for checkout PDF (relative to documents/ loader root)."""
    name = template if template in TEMPLATES else DEFAULT_TEMPLATE
    return f"{name}/checkout.html"


def return_pdf_template(template: str) -> str:
    """Return the Jinja2 template path for return PDF (relative to documents/ loader root)."""
    name = template if template in TEMPLATES else DEFAULT_TEMPLATE
    return f"{name}/return.html"
