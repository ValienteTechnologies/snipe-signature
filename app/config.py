from pathlib import Path
from typing import Literal

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Snipe-IT connection
    snipeit_url: AnyHttpUrl
    snipeit_token: str
    snipeit_verify_ssl: bool = True
    # Cloudflare Access service token (optional — required when Snipe-IT is behind CF Access)
    cf_access_client_id: str | None = None
    cf_access_client_secret: str | None = None

    # Application
    app_lang: Literal["en", "tr"] = "en"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # Branding — path to a logo image used in generated documents
    logo_path: Path | None = None
    # Footer text printed at the bottom of every generated document (PDF and DOCX)
    doc_footer_text: str = ""

    # SATO RFID label printer — leave SATO_PRINTER_IP blank to disable the Print Tag button
    sato_printer_ip: str | None = None
    sato_printer_port: int = 9100
    # Base URL for QR codes printed on labels (asset ID appended); e.g. https://snipeit.example.com/hardware/
    sato_qr_base_url: str = ""

    @field_validator("logo_path", "sato_printer_ip", mode="before")
    @classmethod
    def _empty_str_to_none(cls, v: object) -> object:
        if isinstance(v, str) and not v.strip():
            return None
        return v

    @property
    def snipeit_base_url(self) -> str:
        return str(self.snipeit_url).rstrip("/")

    @property
    def sato_qr_base(self) -> str:
        return self.sato_qr_base_url.rstrip("/")


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()  # type: ignore[call-arg]
    return _settings
