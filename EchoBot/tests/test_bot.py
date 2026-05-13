"""
Unit tests for EchoBot and audio utilities.

Run with:  pytest -v
"""
from __future__ import annotations
import asyncio
import base64
import pytest
from app.audio import encode_audio, process_chunk, validate_chunk_size
from app.bot import EchoBot, SessionState
from app.config import AppConfig, AudioConfig, BotConfig, ServerConfig
from app.models import (
    ConnectedPayload,
    EventType,
    InboundMessage,
    MediaPayload,
    OutboundMessage,
    StartPayload,
    StopPayload,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def cfg() -> AppConfig:
    return AppConfig(
        server=ServerConfig(),
        audio=AudioConfig(max_chunk_bytes=1024),
        bot=BotConfig(echo_delay_seconds=0.0),  # no delay in tests
    )


@pytest.fixture
def bot(cfg) -> EchoBot:
    return EchoBot(cfg)


def _make_media_message(chunk: str = "0", payload_bytes: bytes = b"\x00" * 160) -> InboundMessage:
    payload_b64 = base64.b64encode(payload_bytes).decode()
    return InboundMessage(
        event=EventType.MEDIA,
        sequenceNumber="2",
        media=MediaPayload(
            track="inbound",
            chunk=chunk,
            timestamp="20",
            payload=payload_b64,
        ),
    )


# ---------------------------------------------------------------------------
# Audio utility tests
# ---------------------------------------------------------------------------

class TestAudioUtils:
    def test_process_chunk_returns_same_bytes(self, cfg):
        raw = b"\xAB\xCD" * 80
        result = process_chunk(raw, cfg.audio)
        assert result == raw

    def test_encode_audio_is_valid_base64(self):
        raw = b"hello audio"
        encoded = encode_audio(raw)
        assert base64.b64decode(encoded) == raw

    def test_validate_chunk_size_passes(self):
        validate_chunk_size(b"\x00" * 100, max_bytes=200)   # should not raise

    def test_validate_chunk_size_raises(self):
        with pytest.raises(ValueError, match="exceeds maximum"):
            validate_chunk_size(b"\x00" * 300, max_bytes=200)


# ---------------------------------------------------------------------------
# SessionState tests
# ---------------------------------------------------------------------------

class TestSessionState:
    def test_initial_state(self):
        s = SessionState()
        assert s.chunks_received == 0
        assert s.bytes_received  == 0
        assert s.is_active is True

    def test_record_chunk_accumulates(self):
        s = SessionState()
        s.record_chunk(160)
        s.record_chunk(320)
        assert s.chunks_received == 2
        assert s.bytes_received  == 480

    def test_summary_keys(self):
        s = SessionState(stream_sid="MZ123")
        assert "stream_sid"      in s.summary()
        assert "chunks_received" in s.summary()
        assert "bytes_received"  in s.summary()


# ---------------------------------------------------------------------------
# EchoBot dispatch tests
# ---------------------------------------------------------------------------

class TestEchoBotDispatch:

    def test_handle_connected_returns_none(self, bot):
        msg = InboundMessage(
            event=EventType.CONNECTED,
            connected=ConnectedPayload(protocol="Call", version="1.0.0"),
        )
        result = asyncio.get_event_loop().run_until_complete(bot.handle(msg))
        assert result is None

    def test_handle_start_updates_state(self, bot):
        msg = InboundMessage(
            event=EventType.START,
            start=StartPayload(
                streamSid="MZ_stream",
                accountSid="AC_account",
                callSid="CA_call",
                tracks=["inbound"],
            ),
        )
        asyncio.get_event_loop().run_until_complete(bot.handle(msg))
        assert bot.state.stream_sid  == "MZ_stream"
        assert bot.state.call_sid    == "CA_call"
        assert bot.state.account_sid == "AC_account"

    def test_handle_media_returns_echo(self, bot):
        msg = _make_media_message(chunk="7", payload_bytes=b"\xFF" * 160)
        result: OutboundMessage = asyncio.get_event_loop().run_until_complete(
            bot.handle(msg)
        )
        assert result is not None
        assert result.event == EventType.ECHO
        assert result.echo.original_chunk == "7"
        assert result.echo.byte_count == 160
        # Verify echoed payload decodes back to the original bytes
        assert base64.b64decode(result.echo.payload) == b"\xFF" * 160

    def test_handle_media_increments_counters(self, bot):
        msg = _make_media_message(payload_bytes=b"\x00" * 160)
        asyncio.get_event_loop().run_until_complete(bot.handle(msg))
        assert bot.state.chunks_received == 1
        assert bot.state.bytes_received  == 160

    def test_handle_media_oversized_chunk_returns_error(self, bot):
        big_payload = b"\x00" * 2048  # exceeds 1024-byte limit in test config
        msg = _make_media_message(payload_bytes=big_payload)
        result = asyncio.get_event_loop().run_until_complete(bot.handle(msg))
        assert result.event == EventType.ERROR
        assert result.error.code == "CHUNK_TOO_LARGE"

    def test_handle_stop_deactivates_session(self, bot):
        msg = InboundMessage(
            event=EventType.STOP,
            stop=StopPayload(
                streamSid="MZ_stream",
                accountSid="AC_account",
                callSid="CA_call",
            ),
        )
        asyncio.get_event_loop().run_until_complete(bot.handle(msg))
        assert bot.state.is_active is False

    def test_handle_unknown_event_returns_none(self, bot):
        # Inject a raw dict to bypass the Enum — simulates future event types
        msg = InboundMessage.model_construct(event="unknown_future_event")
        result = asyncio.get_event_loop().run_until_complete(bot.handle(msg))
        assert result is None

    def test_multiple_media_chunks_accumulate(self, bot):
        for i in range(5):
            msg = _make_media_message(chunk=str(i), payload_bytes=b"\xAB" * 160)
            asyncio.get_event_loop().run_until_complete(bot.handle(msg))
        assert bot.state.chunks_received == 5
        assert bot.state.bytes_received  == 800