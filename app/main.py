"""Application factory and entry point."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings

_APP_DIR = Path(__file__).parent
from app.routers import forms, rfid, ui
from app.snipeit.client import AssetNotFound, SnipeITClient, SnipeITError, UserNotFound


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    client = SnipeITClient(
        base_url=settings.snipeit_base_url,
        token=settings.snipeit_token,
        verify_ssl=settings.snipeit_verify_ssl,
        cf_access_client_id=settings.cf_access_client_id,
        cf_access_client_secret=settings.cf_access_client_secret,
    )
    app.state.snipeit = client
    yield
    await client.aclose()


def create_app() -> FastAPI:
    get_settings()

    app = FastAPI(
        title="Snipe-IT Signature",
        description="Physical signature form generator for Snipe-IT assets.",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Static files
    app.mount("/static", StaticFiles(directory=str(_APP_DIR / "static")), name="static")

    # Routers
    app.include_router(ui.router)
    app.include_router(forms.router, tags=["forms"])
    app.include_router(rfid.router, tags=["rfid"])

    # Exception handlers
    @app.exception_handler(AssetNotFound)
    @app.exception_handler(UserNotFound)
    async def not_found_handler(request: Request, exc: SnipeITError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(SnipeITError)
    async def snipeit_error_handler(request: Request, exc: SnipeITError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code or 502,
            content={"detail": str(exc)},
        )

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run("app.main:app", host=settings.app_host, port=settings.app_port, reload=True)
