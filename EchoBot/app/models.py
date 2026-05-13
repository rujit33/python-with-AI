"""
Typed message models for the WebSocket protocol.

Mirrors the Twilio Media Streams message format so the server can be
swapped in front of a real Twilio integration with minimal changes.

Twilio docs reference:
  https://www.twilio.com/docs/voice/media-streams/websocket-messages
"""

from __future__ import annotations

import base64
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class EventType(str, Enum):
    """All event types that can appear in the `event` field of a message."""
    CONNECTED = "connected"
    START     = "start"
    MEDIA     = "media"
    STOP      = "stop"
    # Server → client only
    ECHO      = "echo"
    ERROR     = "error"


# ---------------------------------------------------------------------------
# Inbound (client → server) message payloads
# ---------------------------------------------------------------------------

class ConnectedPayload(BaseModel):
    protocol: str
    version: str


class StartPayload(BaseModel):
    stream_sid: str = Field(..., alias="streamSid")
    account_sid: str = Field(..., alias="accountSid")
    call_sid: str    = Field(..., alias="callSid")
    tracks: list[str]
    media_format: dict = Field(default_factory=dict, alias="mediaFormat")

    model_config = {"populate_by_name": True}


class MediaPayload(BaseModel):
    track: str
    chunk: str           # Sequence number as string (Twilio convention)
    timestamp: str       # Milliseconds since stream start, as string
    payload: str         # Base64-encoded raw audio bytes

    @field_validator("payload")
    @classmethod
    def must_be_valid_base64(cls, v: str) -> str:
        try:
            base64.b64decode(v, validate=True)
        except Exception as exc:
            raise ValueError("payload must be valid base64") from exc
        return v

    def decode_audio(self) -> bytes:
        """Return raw audio bytes from the base64 payload."""
        return base64.b64decode(self.payload)


class StopPayload(BaseModel):
    stream_sid: str = Field(..., alias="streamSid")
    account_sid: str = Field(..., alias="accountSid")
    call_sid: str    = Field(..., alias="callSid")

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Top-level inbound envelope
# ---------------------------------------------------------------------------

class InboundMessage(BaseModel):
    """
    Generic envelope — parse the `event` first, then dispatch to the
    appropriate typed payload.
    """
    event: EventType
    sequence_number: Optional[str] = Field(None, alias="sequenceNumber")

    # Only one of these will be present depending on `event`.
    connected: Optional[ConnectedPayload] = None
    start:     Optional[StartPayload]     = None
    media:     Optional[MediaPayload]     = None
    stop:      Optional[StopPayload]      = None

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Outbound (server → client) message payloads
# ---------------------------------------------------------------------------

class EchoPayload(BaseModel):
    """Echo payload the bot sends back for each received media chunk."""
    original_chunk: str     # Chunk sequence number echoed back
    original_timestamp: str
    payload: str            # Base64 audio (the echo)
    byte_count: int


class ErrorPayload(BaseModel):
    code: str
    message: str


class OutboundMessage(BaseModel):
    """Envelope for all server-initiated messages."""
    event: EventType
    echo:  Optional[EchoPayload]  = None
    error: Optional[ErrorPayload] = None

    def to_json(self) -> str:
        return self.model_dump_json(exclude_none=True)