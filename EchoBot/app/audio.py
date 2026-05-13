"""
Audio processing utilities.

All functions are pure (no I/O, no side effects) so they are trivially
testable and reusable.  The "processing" here is intentionally minimal —
the point is to show *where* DSP / ML inference would plug in.

In a real system you would replace `process_chunk` with:
  - A call to a speech-to-text model
  - An LLM turn
  - A text-to-speech synthesis step
  - Returning the synthesised audio bytes
"""

from __future__ import annotations

import base64
import logging

from .config import AudioConfig

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def process_chunk(raw_audio: bytes, cfg: AudioConfig) -> bytes:
    """
    Transform an inbound audio chunk into an outbound audio chunk.

    Current implementation: identity transform (echo).
    Replace the body of this function to swap in real processing.

    Args:
        raw_audio: Raw audio bytes decoded from the inbound media payload.
        cfg:       Audio configuration (encoding, sample rate, …).

    Returns:
        Processed audio bytes ready to be base64-encoded and sent back.
    """
    logger.debug(
        "process_chunk | encoding=%s sample_rate=%d bytes=%d",
        cfg.encoding,
        cfg.sample_rate,
        len(raw_audio),
    )
    # ── Future hook ────────────────────────────────────────────────────────
    # result = my_tts_pipeline(my_stt_pipeline(raw_audio, cfg), cfg)
    # return result
    # ───────────────────────────────────────────────────────────────────────
    return raw_audio  # echo


def encode_audio(raw_audio: bytes) -> str:
    """Base64-encode audio bytes for transmission over WebSocket JSON."""
    return base64.b64encode(raw_audio).decode("utf-8")


def validate_chunk_size(raw_audio: bytes, max_bytes: int) -> None:
    """
    Raise ValueError when a chunk exceeds the configured maximum.

    Keeping validation here (not in the model) lets us apply it after
    decoding, where we know the real byte count.
    """
    if len(raw_audio) > max_bytes:
        raise ValueError(
            f"Audio chunk {len(raw_audio)} B exceeds maximum {max_bytes} B"
        )