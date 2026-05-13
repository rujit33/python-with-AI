"""
Central configuration for the Echo Bot server.
All tuneable knobs live here — nothing is scattered across the codebase.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "info"


@dataclass(frozen=True)
class AudioConfig:
    # Twilio sends µ-law (mulaw) 8-bit 8 kHz audio by default.
    # We store that assumption here so handlers don't hard-code it.
    encoding: str = "mulaw"
    sample_rate: int = 8000
    channels: int = 1

    # Maximum chunk size (bytes) we accept in a single WebSocket message.
    max_chunk_bytes: int = 32_768  # 32 KB


@dataclass(frozen=True)
class BotConfig:
    # Echo delay in seconds — simulates processing latency.
    echo_delay_seconds: float = 0.05
    # Label shown in log lines.
    name: str = "EchoBot"


@dataclass(frozen=True)
class AppConfig:
    server: ServerConfig = field(default_factory=ServerConfig)
    audio: AudioConfig = field(default_factory=AudioConfig)
    bot: BotConfig = field(default_factory=BotConfig)


# Singleton used throughout the app — import and use directly.
config = AppConfig()