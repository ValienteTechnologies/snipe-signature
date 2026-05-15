"""PDF generation via WeasyPrint (HTML → PDF)."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import jinja2
from weasyprint import HTML

from app.documents.registry import checkout_pdf_template, return_pdf_template

_DEFAULT_LOGO = Path(__file__).parent.parent / "static" / "logo_placeholder.png"


def resolve_logo(logo_path: Path | None) -> Path | None:
    if logo_path and logo_path.is_file():
        return logo_path
    if _DEFAULT_LOGO.is_file():
        return _DEFAULT_LOGO
    return None


def make_temp_file(suffix: str) -> Path:
    fd, tmp = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    return Path(tmp)
from app.i18n import Labels
from app.snipeit.models import AssetWithActivity, User

_TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "documents"
ITEMS_PER_PAGE = 10

_jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(_TEMPLATES_DIR)),
    autoescape=jinja2.select_autoescape(["html"]),
)


def _render_pdf(template_name: str, context: dict) -> Path:
    tmpl = _jinja_env.get_template(template_name)
    html_str = tmpl.render(**context)
    tmp = make_temp_file(".pdf")
    HTML(string=html_str, base_url=str(_TEMPLATES_DIR)).write_pdf(str(tmp))
    return tmp


def build_checkout_pdf(
    enriched: list[AssetWithActivity],
    user: User,
    labels: Labels,
    logo_path: Path | None = None,
    template: str = "default",
    footer_text: str = "",
) -> Path:
    from datetime import datetime

    resolved_logo = resolve_logo(logo_path)
    logo_uri = resolved_logo.resolve().as_uri() if resolved_logo else None

    return _render_pdf(
        checkout_pdf_template(template),
        {
            "labels": labels,
            "user": user,
            "enriched": enriched,
            "logo_uri": logo_uri,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "footer_text": footer_text,
            "page_size": ITEMS_PER_PAGE,
        },
    )


def build_return_pdf(
    enriched: list[AssetWithActivity],
    user: User,
    labels: Labels,
    logo_path: Path | None = None,
    template: str = "default",
    footer_text: str = "",
) -> Path:
    from datetime import datetime

    resolved_logo = resolve_logo(logo_path)
    logo_uri = resolved_logo.resolve().as_uri() if resolved_logo else None
    today_str = datetime.now().strftime("%Y-%m-%d")

    return _render_pdf(
        return_pdf_template(template),
        {
            "labels": labels,
            "user": user,
            "enriched": enriched,
            "logo_uri": logo_uri,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "today": today_str,
            "footer_text": footer_text,
            "page_size": ITEMS_PER_PAGE,
        },
    )
