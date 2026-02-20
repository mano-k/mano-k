from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from config import settings
from transcriber import StreamingTranscriber

BASE_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(title="Realtime Speech-to-Text")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.websocket("/ws/transcribe")
async def transcribe_socket(websocket: WebSocket) -> None:
    await websocket.accept()
    transcriber = StreamingTranscriber(
        sample_rate=settings.sample_rate,
        chunk_seconds=settings.chunk_seconds,
        vad_threshold=settings.vad_threshold,
        whisper_model=settings.whisper_model,
        whisper_device=settings.whisper_device,
        whisper_compute_type=settings.whisper_compute_type,
    )

    await websocket.send_text(
        json.dumps(
            {
                "type": "status",
                "message": "Connected. Speak into your mic...",
                "sample_rate": settings.sample_rate,
            }
        )
    )

    try:
        while True:
            audio_bytes = await websocket.receive_bytes()
            chunk = np.frombuffer(audio_bytes, dtype=np.int16)
            result = transcriber.push_audio(chunk)
            if result:
                await websocket.send_text(json.dumps(result))

    except WebSocketDisconnect:
        return
