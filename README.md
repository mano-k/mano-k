# Realtime Speech-to-Text (WebSocket + Backend Audio Processing)

A complete starter project for **live speech-to-text**:
- Browser captures mic audio
- Streams PCM audio chunks over WebSocket
- Backend processes audio (RMS/VAD + buffering)
- Backend returns realtime transcripts

---

## 1) Complete folder structure

```text
mano-k/
├── .env.example
├── .gitignore
├── README.md
├── scripts/
│   └── run_backend.sh
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   └── transcriber.py
└── frontend/
    ├── index.html
    └── main.js
```

---

## 2) How this works (end-to-end)

1. `frontend/main.js` gets microphone input (mono, 16kHz target).
2. Audio `Float32` samples are converted to `Int16 PCM`.
3. Audio chunks are sent to `ws://<host>/ws/transcribe`.
4. `backend/app.py` reads bytes and forwards PCM to `StreamingTranscriber`.
5. `backend/transcriber.py` computes RMS (simple speech activity hint), buffers speech chunks, and transcribes with `faster-whisper`.
6. Transcript/status/audio stats are pushed back to the browser in realtime JSON messages.

---

## 3) Step-by-step implementation guide

### Step A — Prerequisites
- Python 3.10+
- `ffmpeg` available on system (required by whisper stack)
- Microphone access in your browser

### Step B — Configure environment

```bash
cp .env.example .env
```

Optional tuning in `.env`:
- `APP_SAMPLE_RATE` (default `16000`)
- `APP_CHUNK_SECONDS` (default `2.5`)
- `APP_VAD_THRESHOLD` (default `0.01`)
- `APP_WHISPER_MODEL` (e.g. `base`, `small`)
- `APP_WHISPER_DEVICE` (`cpu` or `cuda`)
- `APP_WHISPER_COMPUTE_TYPE` (e.g. `int8`, `float16`)

### Step C — Start backend

```bash
./scripts/run_backend.sh
```

This script creates `backend/.venv` (if needed), installs dependencies, loads `.env`, and starts Uvicorn.

### Step D — Open app
- Go to `http://localhost:8000`
- Click **Start**
- Allow microphone
- Speak and watch status/audio stats/transcript update

---

## 4) WebSocket contract

### Client → Server
- Binary messages only: raw `Int16 PCM` mono samples

### Server → Client JSON messages
- `{"type":"status","message":"...","sample_rate":16000}`
- `{"type":"audio_stats","rms":0.0231,"speech":true,"buffered_ms":1800}`
- `{"type":"transcript","text":"hello world","rms":0.0312}`

---

## 5) Production recommendations

- Add auth on WebSocket endpoint
- Add per-connection rate limits and max payload checks
- Use GPU + larger whisper model for better quality
- Add structured logs and monitoring
- Add persistent transcript/session storage

---

## 6) Troubleshooting

- **No transcript**: verify mic permissions and check browser console/network WS frames.
- **Install failures**: check outbound network/proxy and Python package index access.
- **Slow transcription**: reduce model size or use GPU (`APP_WHISPER_DEVICE=cuda`).
