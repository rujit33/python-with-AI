"""
EchoBot — one instance per WebSocket connection.

Responsibilities
----------------
- Track per-session state (stream SID, chunk counter, …).
- Dispatch inbound messages to the correct handler method.
- Delegate audio processing to `audio.py` (no DSP logic here).
- Build and return outbound messages; never send directly (that stays
  in the route layer so the bot remains unit-testable without a live socket).
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Optional

from .audio import encode_audio, process_chunk, validate_chunk_size
from .config import AppConfig
from .models import (
    EchoPayload,
    ErrorPayload,
    EventType,
    InboundMessage,
    OutboundMessage,
    StartPayload,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Session state — plain dataclass, no framework magic
# ---------------------------------------------------------------------------

@dataclass
class SessionState:
    stream_sid:   Optional[str] = None
    call_sid:     Optional[str] = None
    account_sid:  Optional[str] = None
    chunks_received: int = 0
    bytes_received:  int = 0
    is_active:    bool = True

    def record_chunk(self, byte_count: int) -> None:
        self.chunks_received += 1
        self.bytes_received  += byte_count

    def summary(self) -> dict:
        return {
            "stream_sid":      self.stream_sid,
            "chunks_received": self.chunks_received,
            "bytes_received":  self.bytes_received,
        }


# ---------------------------------------------------------------------------
# Bot
# ---------------------------------------------------------------------------

class EchoBot:
    """
    Processes one WebSocket session end-to-end.

    Usage
    -----
        bot = EchoBot(config)
        async for message in ws_receive():
            response = await bot.handle(message)
            if response:
                await ws_send(response.to_json())
    """

    def __init__(self, cfg: AppConfig) -> None:
        self._cfg   = cfg
        self._state = SessionState()
        logger.info("[%s] Session created", cfg.bot.name)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @property
    def state(self) -> SessionState:
        return self._state

    async def handle(self, message: InboundMessage) -> Optional[OutboundMessage]:
        """
        Dispatch an inbound message and return an outbound response, or
        None when no response is required (e.g. for `connected` / `stop`).
        """
        handlers = {
            EventType.CONNECTED: self._on_connected,
            EventType.START:     self._on_start,
            EventType.MEDIA:     self._on_media,
            EventType.STOP:      self._on_stop,
        }
        handler = handlers.get(message.event)
        if handler is None:
            logger.warning("Unhandled event type: %s", message.event)
            return None
        return await handler(message)

    # ------------------------------------------------------------------
    # Private event handlers
    # ------------------------------------------------------------------

    async def _on_connected(self, message: InboundMessage) -> None:
        payload = message.connected
        logger.info(
            "[%s] Connected | protocol=%s version=%s",
            self._cfg.bot.name,
            payload.protocol if payload else "?",
            payload.version  if payload else "?",
        )
        return None

    async def _on_start(self, message: InboundMessage) -> None:
        payload: StartPayload = message.start
        self._state.stream_sid  = payload.stream_sid
        self._state.call_sid    = payload.call_sid
        self._state.account_sid = payload.account_sid
        logger.info(
            "[%s] Stream started | sid=%s call=%s tracks=%s",
            self._cfg.bot.name,
            payload.stream_sid,
            payload.call_sid,
            payload.tracks,
        )
        return None

    async def _on_media(self, message: InboundMessage) -> OutboundMessage:
        media = message.media

        # 1. Decode raw bytes from base64 payload
        raw_audio = media.decode_audio()

        # 2. Validate size before any processing
        try:
            validate_chunk_size(raw_audio, self._cfg.audio.max_chunk_bytes)
        except ValueError as exc:
            logger.error("Chunk rejected: %s", exc)
            return OutboundMessage(
                event=EventType.ERROR,
                error=ErrorPayload(code="CHUNK_TOO_LARGE", message=str(exc)),
            )

        # 3. Update session counters
        self._state.record_chunk(len(raw_audio))

        # 4. Simulate processing latency (remove in production)
        await asyncio.sleep(self._cfg.bot.echo_delay_seconds)

        # 5. Process audio (echo in this implementation)
        processed = process_chunk(raw_audio, self._cfg.audio)

        logger.debug(
            "[%s] Media chunk | seq=%s ts=%s bytes=%d",
            self._cfg.bot.name,
            media.chunk,
            media.timestamp,
            len(raw_audio),
        )

        # 6. Build and return response — caller is responsible for sending
        return OutboundMessage(
            event=EventType.ECHO,
            echo=EchoPayload(
                original_chunk=media.chunk,
                original_timestamp=media.timestamp,
                payload=encode_audio(processed),
                byte_count=len(processed),
            ),
        )

    async def _on_stop(self, message: InboundMessage) -> None:
        self._state.is_active = False
        logger.info(
            "[%s] Stream stopped | summary=%s",
            self._cfg.bot.name,
            self._state.summary(),
        )
        return None