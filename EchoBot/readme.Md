## Steps to run the server and simulate communication 

Install the required libraries using the requirements.txt

change working directory to EchoBot

```powershell

cd "EchoBot"

```

# Terminal 1 — server
```powershell
python main.py
```
# Terminal 2 — simulated Twilio client
```powershell
python client_test.py
```
# Tests (no server needed)
```powershell
pytest -v  
```

# Async WebSocket Echo Bot

A real-time bi-directional WebSocket audio streaming server built using:

- FastAPI
- WebSockets
- Async Python
- Pydantic
- µ-law audio simulation

This project mimics how telephony systems like Twilio Media Streams send live audio during a phone call.

---

# What This Project Actually Does

This project simulates a live phone-call audio pipeline.

The system contains:

1. A WebSocket server
2. A fake client that streams audio
3. An Echo Bot that processes audio
4. A response pipeline that sends audio back

The current implementation simply echoes audio back to the client.

---

# Real-World Analogy

This project behaves like a simplified version of:

- Twilio Media Streams
- AI call center systems
- Voice assistants
- Real-time speech AI
- Discord voice bots

Real systems work like this:

```text
Microphone Audio
       ↓
Audio Stream over WebSocket
       ↓
Server receives chunks
       ↓
AI processes audio
       ↓
Audio response sent back
```

This project recreates that architecture locally.

---

# WebSocket?

Normal HTTP:

```text
Client → Request
Server → Response
Connection closes
```

WebSocket:

```text
Client ↔ Server
Connection stays open
Continuous two-way communication
```

WebSockets are required for:

- Live calls
- Streaming audio
- Multiplayer games
- Live chat
- Voice AI systems

---

# Overall Architecture

```text
client_test.py
      │
      │  Sends audio chunks
      ▼
server.py
      │
      ▼
bot.py
      │
      ▼
audio.py
      │
      ▼
bot.py
      │
      ▼
server.py
      │
      ▼
client_test.py
```

---

# Project Structure

```text
echo_bot/
├── main.py
├── client_test.py
├── requirements.txt
│
├── app/
│   ├── config.py
│   ├── models.py
│   ├── audio.py
│   ├── bot.py
│   └── server.py
│
└── tests/
    └── test_bot.py
```

---

# File-by-File Explanation

# 1. main.py

Purpose:
Starts the FastAPI server using Uvicorn.

Code:

```python
uvicorn.run(
    "app.server:app",
    host=config.server.host,
    port=config.server.port,
)
```

What happens:

- Uvicorn launches the ASGI server
- FastAPI app starts
- WebSocket endpoint becomes available

Server URL:

```text
ws://localhost:8000/ws/audio
```

---

# 2. config.py

Purpose:
Stores all configuration values in one place.

Example:

```python
sample_rate = 8000
encoding = "mulaw"
max_chunk_bytes = 32768
```



Without centralized config:

- values become scattered everywhere
- harder to modify
- harder to test

This file uses frozen dataclasses:

```python
@dataclass(frozen=True)
```

Meaning:

- configuration becomes immutable
- safer for production systems

---

# 3. models.py

Purpose:
Defines structured WebSocket message formats using Pydantic.

This acts like a schema validator.

Instead of accepting random JSON:

```json
{
  "event": "media",
  "payload": "abc"
}
```

Pydantic validates:

- required fields
- data types
- structure
- base64 correctness

---

# Event Types

```python
class EventType(str, Enum):
    CONNECTED = "connected"
    START     = "start"
    MEDIA     = "media"
    STOP      = "stop"
    ECHO      = "echo"
    ERROR     = "error"
```

These represent different message categories.

---

# Message Flow

The client sends messages in this order:

```text
connected
start
media
media
media
...
stop
```

---

# MediaPayload

Most important model:

```python
class MediaPayload(BaseModel):
```

Contains:

| Field | Purpose |
|---|---|
| track | inbound/outbound |
| chunk | chunk sequence number |
| timestamp | stream timestamp |
| payload | base64 audio |

---

# Base64 Validation

```python
base64.b64decode(v, validate=True)
```

Ensures corrupted audio payloads are rejected.

---

# 4. audio.py

Purpose:
Contains all audio-processing functions.

Very important design decision:

These functions are PURE FUNCTIONS.

Meaning:

- no networking
- no file I/O
- no side effects

This makes them:

- easy to test
- reusable
- predictable

---

# process_chunk()

Current implementation:

```python
return raw_audio
```

This is why it is called an Echo Bot.

The server sends back the exact same audio.

---

# Real Future AI Pipeline

This section:

```python
# result = my_tts_pipeline(my_stt_pipeline(raw_audio, cfg), cfg)
```

shows where real AI would go.

In real systems:

```text
Audio
  ↓
Speech-to-Text
  ↓
LLM
  ↓
Text-to-Speech
  ↓
Audio Response
```

---

# encode_audio()

Purpose:

Converts raw bytes into base64 text.



JSON cannot send raw binary safely.

So audio is converted:

```text
Raw Bytes → Base64 String
```

---

# validate_chunk_size()

Purpose:

Protects server from oversized payloads.

Without this:

- malicious users could crash server
- memory attacks become possible

---

# 5. bot.py

Purpose:
Core session logic.

This is the brain of the system.

Each WebSocket connection gets its own:

```python
EchoBot()
```

instance.

---

# SessionState

Stores connection-specific data.

Example:

```python
stream_sid
call_sid
chunks_received
bytes_received
```

Why?

Every caller needs isolated state.

Without session state:

multiple users would mix together.

---

# handle()

Main dispatcher function:

```python
async def handle(self, message):
```

Routes messages based on event type.

Example:

```python
connected → _on_connected()
media → _on_media()
stop → _on_stop()
```

---

# _on_media()

Most important function in project.

Pipeline:

## Step 1

Decode base64:

```python
raw_audio = media.decode_audio()
```

---

## Step 2

Validate size:

```python
validate_chunk_size()
```

---

## Step 3

Update counters:

```python
self._state.record_chunk()
```

---

## Step 4

Simulate AI latency:

```python
await asyncio.sleep()
```

---

## Step 5

Process audio:

```python
processed = process_chunk()
```

---

## Step 6

Send response:

```python
OutboundMessage(...)
```

---

# Why async is used

Audio streaming is real-time.

Without async:

- one client blocks others
- server becomes slow

Async allows:

```text
Client A waiting
Client B processing
Client C sending
```

all simultaneously.

---

# 6. server.py

Purpose:
Networking layer.

Contains:

- FastAPI app
- WebSocket endpoint
- connection manager
- session loop

---

# ConnectionManager

Tracks active clients.

```python
self._active: set[WebSocket]
```

Useful for:

- monitoring
- broadcasting
- analytics

---

# create_app()

Factory pattern.

Allows tests to inject custom configs.

Better architecture than global app creation.

---

# Health Endpoint

```python
GET /health
```

Returns:

```json
{
  "status": "ok",
  "active_connections": 2
}
```

Used for:

- monitoring
- uptime checks
- deployment systems

---

# WebSocket Endpoint

```python
@app.websocket("/ws/audio")
```

Main streaming endpoint.

This is where live audio flows.

---

# _run_session()

Main receive/send loop.

Continuously:

```text
Receive message
Parse JSON
Validate
Process
Send response
```

---

# _parse_message()

Safely parses incoming JSON.

Prevents server crashes from malformed data.

Bad input becomes:

```text
logged warning
```

instead of:

```text
server crash
```

---

# 7. client_test.py

Purpose:
Fake Twilio client simulator.

Without this:

you would need:

- real phone calls
- Twilio account
- SIP integration

This file simulates all of that locally.

---

# What client_test.py Does

## Step 1

Connects to:

```text
ws://localhost:8000/ws/audio
```

---

## Step 2

Sends handshake:

```text
connected
start
```

---

## Step 3

Generates fake audio.

Uses:

```python
math.sin()
```

to create a sine wave.

---

# Why µ-law?

Telephony systems commonly use:

```text
8kHz
mono
µ-law
```

because it is lightweight and bandwidth efficient.

Twilio also uses µ-law.

---

# generate_ulaw_chunk()

Creates synthetic phone-call audio.

Pipeline:

```text
Sine Wave
  ↓
16-bit PCM
  ↓
µ-law encoding
  ↓
WebSocket transmission
```

---

# Media Streaming

The client sends:

```text
chunk 0
chunk 1
chunk 2
...
```

instead of one huge audio file.

This mimics live speaking.

---

# Echo Responses

For each chunk:

```text
Client sends audio
Server echoes audio
Client prints response
```

---

# Final Summary

At the end:

```text
Chunks sent
Echoes received
Round-trip time
Success status
```

are displayed.

---

# 8. test_bot.py

Purpose:
Unit testing.

Tests logic without running a live server.



---

# What Gets Tested

## Audio Utilities

Tests:

- base64 encoding
- chunk validation
- audio processing

---

# SessionState

Tests:

- chunk counters
- byte counters
- summaries

---

# EchoBot

Tests:

- connected event
- media event
- oversized chunks
- stop event
- unknown events

---



# Full Runtime Flow

# Terminal 1

Run server:

```bash
python main.py
```

---

# Terminal 2

Run client:

```bash
python client_test.py
```

---

# What Happens Internally

```text
Client connects
↓
Server accepts WebSocket
↓
Client sends connected
↓
Client sends start
↓
Client streams audio chunks
↓
Server validates chunks
↓
Server processes audio
↓
Server sends echo responses
↓
Client receives echoes
↓
Client sends stop
↓
Connection closes
```

---

