"""FastAPI dependency providers."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request

from app.config import Settings, get_settings
from app.i18n import Labels, get_labels
from app.snipeit.client import SnipeITClient


def get_snipeit_client(request: Request) -> SnipeITClient:
    """Return the shared SnipeITClient stored on app state."""
    return request.app.state.snipeit


def get_labels_dep(settings: Annotated[Settings, Depends(get_settings)]) -> Labels:
    return get_labels(settings.app_lang)


SnipeITDep = Annotated[SnipeITClient, Depends(get_snipeit_client)]
LabelsDep = Annotated[Labels, Depends(get_labels_dep)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
