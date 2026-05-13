"""
FastAPI application — HTTP health check + WebSocket endpoint.

The WebSocket route is intentionally thin:
  - Accept / reject the connection
  - Drive the receive/send loop
  - Delegate all business logic to EchoBot

This separation means EchoBot is fully testable without a live HTTP server.
"""

from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from .bot import EchoBot
from .config import AppConfig, config as default_config
from .models import InboundMessage

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Connection manager — tracks all live sockets (useful for monitoring / broadcast)
# ---------------------------------------------------------------------------

class ConnectionManager:
    """Thread-safe registry of active WebSocket connections."""

    def __init__(self) -> None:
        self._active: set[WebSocket] = set()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._active.add(ws)
        logger.info("WS connected | total=%d remote=%s", len(self._active), ws.client)

    def disconnect(self, ws: WebSocket) -> None:
        self._active.discard(ws)
        logger.info("WS disconnected | total=%d", len(self._active))

    @property
    def active_count(self) -> int:
        return len(self._active)


# ---------------------------------------------------------------------------
# Factory — allows tests to inject a custom config
# ---------------------------------------------------------------------------

def create_app(cfg: AppConfig = default_config) -> FastAPI:

    manager = ConnectionManager()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator:
        logger.info(
            "Echo Bot starting | host=%s port=%d",
            cfg.server.host,
            cfg.server.port,
        )
        yield
        logger.info("Echo Bot shutting down")

    app = FastAPI(
        title="Async WebSocket Echo Bot",
        description=(
            "Bi-directional WebSocket server that mimics a Twilio Media Streams "
            "telephony integration.  Receives simulated audio chunks and echoes "
            "them back with metadata."
        ),
        version="1.0.0",
        lifespan=lifespan,
    )

    # ── HTTP endpoints ──────────────────────────────────────────────────────

    @app.get("/health", summary="Health check")
    async def health() -> JSONResponse:
        return JSONResponse({
            "status": "ok",
            "active_connections": manager.active_count,
        })

    @app.get("/", summary="API info")
    async def root() -> JSONResponse:
        return JSONResponse({
            "service": "echo-bot",
            "websocket_endpoint": "/ws/audio",
            "docs": "/docs",
        })

    # ── WebSocket endpoint ──────────────────────────────────────────────────

    @app.websocket("/ws/audio")
    async def websocket_audio(ws: WebSocket) -> None:
        """
        Main WebSocket endpoint.

        Expected message flow (mirrors Twilio Media Streams):
          1. Client sends  `connected`
          2. Client sends  `start`
          3. Client sends  N × `media`
          4. Client sends  `stop`
        """
        await manager.connect(ws)
        bot = EchoBot(cfg)

        try:
            await _run_session(ws, bot)
        except WebSocketDisconnect as exc:
            logger.info("Client disconnected | code=%s", exc.code)
        except Exception as exc:
            logger.exception("Unexpected error in WS session: %s", exc)
            await _safe_close(ws, code=status.WS_1011_INTERNAL_ERROR)
        finally:
            manager.disconnect(ws)

    return app


# ---------------------------------------------------------------------------
# Session loop — extracted so it can be unit-tested without a real socket
# ---------------------------------------------------------------------------

async def _run_session(ws: WebSocket, bot: EchoBot) -> None:
    """Receive messages in a loop, hand to bot, send responses."""
    async for raw in _iter_messages(ws):
        message = _parse_message(raw)
        if message is None:
            continue                    # malformed — already logged

        response = await bot.handle(message)

        if response is not None:
            await ws.send_text(response.to_json())


async def _iter_messages(ws: WebSocket):
    """Yield raw text/bytes from the WebSocket until it closes."""
    while True:
        data = await ws.receive()
        if "text" in data:
            yield data["text"]
        elif "bytes" in data:
            # Accept raw binary frames too — decode as UTF-8 JSON
            yield data["bytes"].decode("utf-8")
        elif data.get("type") == "websocket.disconnect":
            break


def _parse_message(raw: str) -> InboundMessage | None:
    """
    Parse + validate a raw JSON string into an InboundMessage.
    Returns None (and logs the error) on any parse failure so the session
    continues rather than crashing.
    """
    try:
        return InboundMessage.model_validate(json.loads(raw))
    except json.JSONDecodeError as exc:
        logger.warning("Invalid JSON received: %s | raw=%r", exc, raw[:120])
        return None
    except ValidationError as exc:
        logger.warning("Message validation failed: %s", exc)
        return None


async def _safe_close(ws: WebSocket, code: int) -> None:
    try:
        await ws.close(code=code)
    except Exception:
        pass  # already closed


# ---------------------------------------------------------------------------
# Module-level app instance for `uvicorn app.server:app`
# ---------------------------------------------------------------------------

app = create_app()