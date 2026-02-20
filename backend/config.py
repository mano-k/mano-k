from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    sample_rate: int = int(os.getenv("APP_SAMPLE_RATE", "16000"))
    chunk_seconds: float = float(os.getenv("APP_CHUNK_SECONDS", "2.5"))
    vad_threshold: float = float(os.getenv("APP_VAD_THRESHOLD", "0.01"))
    whisper_model: str = os.getenv("APP_WHISPER_MODEL", "base")
    whisper_device: str = os.getenv("APP_WHISPER_DEVICE", "cpu")
    whisper_compute_type: str = os.getenv("APP_WHISPER_COMPUTE_TYPE", "int8")


settings = Settings()
