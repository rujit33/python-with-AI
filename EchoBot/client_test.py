"""
Simulated Twilio Media Streams client.

Run this in a separate terminal while the server is running:

    python client_test.py

What it does
------------
1. Opens a WebSocket to ws://localhost:8000/ws/audio
2. Sends the Twilio `connected` handshake
3. Sends a `start` envelope with fake SIDs
4. Sends N `media` frames of synthetic audio (sine wave encoded as µ-law)
5. Sends `stop`
6. Prints each echoed response
7. Prints a final summary
"""

from __future__ import annotations

import asyncio
import base64
import json
import math
import struct
import time
import uuid

import websockets

SERVER_URL    = "ws://localhost:8000/ws/audio"
NUM_CHUNKS    = 10          # Number of audio frames to send
CHUNK_MS      = 20          # Milliseconds of audio per frame
SAMPLE_RATE   = 8_000       # Hz
SINE_FREQ     = 440.0       # Hz — A4 note


# ---------------------------------------------------------------------------
# Audio helpers
# ---------------------------------------------------------------------------

def _linear_to_ulaw(sample: int) -> int:
    """Convert a 16-bit linear PCM sample to 8-bit µ-law."""
    BIAS    = 0x84
    MAX     = 32767
    sample  = max(-MAX, min(MAX, sample))
    sign    = (sample >> 8) & 0x80
    if sign:
        sample = -sample
    sample += BIAS
    exp = 7
    for exp_mask in (0x4000, 0x2000, 0x1000, 0x0800, 0x0400, 0x0200, 0x0100):
        if sample & exp_mask:
            break
        exp -= 1
    mantissa = (sample >> (exp + 3)) & 0x0F
    return ~(sign | (exp << 4) | mantissa) & 0xFF


def generate_ulaw_chunk(chunk_index: int) -> bytes:
    """Generate one chunk of sine-wave audio in µ-law encoding."""
    num_samples = int(SAMPLE_RATE * CHUNK_MS / 1000)
    offset      = chunk_index * num_samples
    raw = bytearray(num_samples)
    for i in range(num_samples):
        t      = (offset + i) / SAMPLE_RATE
        pcm16  = int(32767 * 0.5 * math.sin(2 * math.pi * SINE_FREQ * t))
        raw[i] = _linear_to_ulaw(pcm16)
    return bytes(raw)


# ---------------------------------------------------------------------------
# Message builders
# ---------------------------------------------------------------------------

def _make_connected() -> str:
    return json.dumps({
        "event":     "connected",
        "connected": {"protocol": "Call", "version": "1.0.0"},
    })


def _make_start(stream_sid: str, account_sid: str, call_sid: str) -> str:
    return json.dumps({
        "event":          "start",
        "sequenceNumber": "1",
        "start": {
            "streamSid":  stream_sid,
            "accountSid": account_sid,
            "callSid":    call_sid,
            "tracks":     ["inbound"],
            "mediaFormat": {
                "encoding":   "audio/x-mulaw",
                "sampleRate": SAMPLE_RATE,
                "channels":   1,
            },
        },
    })


def _make_media(chunk_index: int, timestamp_ms: int, audio: bytes) -> str:
    return json.dumps({
        "event":          "media",
        "sequenceNumber": str(chunk_index + 2),   # +2 because connected + start used 1-2
        "media": {
            "track":     "inbound",
            "chunk":     str(chunk_index),
            "timestamp": str(timestamp_ms),
            "payload":   base64.b64encode(audio).decode(),
        },
    })


def _make_stop(stream_sid: str, account_sid: str, call_sid: str) -> str:
    return json.dumps({
        "event": "stop",
        "stop": {
            "streamSid":  stream_sid,
            "accountSid": account_sid,
            "callSid":    call_sid,
        },
    })


# ---------------------------------------------------------------------------
# Main client coroutine
# ---------------------------------------------------------------------------

async def run_client() -> None:
    stream_sid  = f"MZ{uuid.uuid4().hex[:32]}"
    account_sid = f"AC{uuid.uuid4().hex[:32]}"
    call_sid    = f"CA{uuid.uuid4().hex[:32]}"

    print(f"\n{'─'*60}")
    print(f"  Echo Bot Test Client")
    print(f"  Server  : {SERVER_URL}")
    print(f"  Stream  : {stream_sid[:20]}…")
    print(f"  Chunks  : {NUM_CHUNKS} × {CHUNK_MS} ms  ({CHUNK_MS*NUM_CHUNKS} ms total)")
    print(f"{'─'*60}\n")

    async with websockets.connect(SERVER_URL) as ws:
        # ── Handshake ───────────────────────────────────────────────────
        print("[→] Sending: connected")
        await ws.send(_make_connected())

        print("[→] Sending: start")
        await ws.send(_make_start(stream_sid, account_sid, call_sid))

        # ── Media stream ─────────────────────────────────────────────────
        echoes_received = 0
        t0 = time.perf_counter()

        for i in range(NUM_CHUNKS):
            timestamp_ms = i * CHUNK_MS
            audio        = generate_ulaw_chunk(i)
            msg          = _make_media(i, timestamp_ms, audio)

            print(f"[→] Sending: media  chunk={i:>3}  bytes={len(audio)}")
            await ws.send(msg)

            # Read the echoed response
            try:
                raw_resp = await asyncio.wait_for(ws.recv(), timeout=5.0)
                resp     = json.loads(raw_resp)
                echoes_received += 1
                echo = resp.get("echo", {})
                print(
                    f"[←] Echo:          chunk={echo.get('original_chunk','?'):>3}"
                    f"  bytes={echo.get('byte_count','?')}"
                    f"  ts={echo.get('original_timestamp','?')} ms"
                )
            except asyncio.TimeoutError:
                print(f"[!] Timeout waiting for echo on chunk {i}")

        elapsed = time.perf_counter() - t0

        # ── Teardown ──────────────────────────────────────────────────────
        print(f"\n[→] Sending: stop")
        await ws.send(_make_stop(stream_sid, account_sid, call_sid))

        # ── Summary ───────────────────────────────────────────────────────
        print(f"\n{'─'*60}")
        print(f"  Summary")
        print(f"  Chunks sent    : {NUM_CHUNKS}")
        print(f"  Echoes received: {echoes_received}")
        print(f"  Round-trip time: {elapsed:.3f} s")
        print(f"  Success        : {'✓' if echoes_received == NUM_CHUNKS else '✗'}")
        print(f"{'─'*60}\n")


if __name__ == "__main__":
    asyncio.run(run_client())