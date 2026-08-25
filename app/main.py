#!/usr/bin/env python3
"""Khanh Voice — TTS key-selling site: storefront + PayOS checkout + key-gated TTS + admin."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import db
from .routes_admin import router as admin_router
from .routes_public import router as public_router
from .routes_tts import router as tts_router
from .routes_webhook import router as webhook_router

APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"

app = FastAPI(title="Khanh Voice")


@app.on_event("startup")
def on_startup() -> None:
    db.init_db()


app.include_router(public_router)
app.include_router(webhook_router)
app.include_router(tts_router)
app.include_router(admin_router)

app.mount("/assets", StaticFiles(directory=STATIC_DIR), name="assets")

PAGES = {
    "/": "landing.html",
    "/app": "app.html",
    "/thanks": "thanks.html",
    "/cancel": "cancel.html",
    "/admin": "admin.html",
}

for path, filename in PAGES.items():
    def make_handler(fname: str):
        async def handler():
            return FileResponse(STATIC_DIR / fname)

        return handler

    app.add_api_route(path, make_handler(filename), methods=["GET"], include_in_schema=False)
