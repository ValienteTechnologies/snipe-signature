"""Internationalisation helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Lang = Literal["en", "tr"]


@dataclass(frozen=True)
class Labels:
    # UI
    page_title: str
    tab_asset: str
    tab_user: str
    search_placeholder_tag: str
    search_placeholder_user: str
    btn_lookup_asset: str
    btn_lookup_user: str
    btn_checkout_form: str
    btn_return_form: str
    col_asset_tag: str
    col_name: str
    col_manufacturer: str
    col_model: str
    col_category: str
    col_serial: str
    col_checkout_date: str
    col_return_date: str
    error_not_found: str
    error_generic: str
    no_assets: str
    no_returned_assets: str
    select_all: str

    # Document — shared
    doc_condition_note: str

    # Document — checkout
    doc_checkout_title: str
    doc_issued_by: str
    doc_received_by: str
    doc_date: str
    doc_signature: str
    doc_name_surname: str

    # Document — return
    doc_return_title: str
    doc_returned_by: str
    doc_received_by_admin: str


def get_labels(lang: Lang = "en") -> Labels:
    if lang == "tr":
        from app.i18n.tr import TR_LABELS

        return TR_LABELS
    from app.i18n.en import EN_LABELS

    return EN_LABELS
