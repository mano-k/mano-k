from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from faster_whisper import WhisperModel


@dataclass
class StreamingTranscriber:
    sample_rate: int
    whisper_model: str = "base"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"
    chunk_seconds: float = 2.5
    vad_threshold: float = 0.01
    _buffer: list[np.ndarray] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.samples_per_chunk = int(self.sample_rate * self.chunk_seconds)
        self.model = WhisperModel(
            self.whisper_model,
            device=self.whisper_device,
            compute_type=self.whisper_compute_type,
        )

    def push_audio(self, pcm_chunk: np.ndarray) -> dict | None:
        if pcm_chunk.size == 0:
            return None

        float_audio = pcm_chunk.astype(np.float32) / 32768.0
        rms = float(np.sqrt(np.mean(np.square(float_audio))))

        if rms < self.vad_threshold:
            return {"type": "audio_stats", "rms": round(rms, 5), "speech": False}

        self._buffer.append(float_audio)
        current = np.concatenate(self._buffer)

        if current.shape[0] < self.samples_per_chunk:
            return {
                "type": "audio_stats",
                "rms": round(rms, 5),
                "speech": True,
                "buffered_ms": int((current.shape[0] / self.sample_rate) * 1000),
            }

        segments, _ = self.model.transcribe(
            current,
            language="en",
            vad_filter=True,
            beam_size=1,
            condition_on_previous_text=False,
        )

        transcript = " ".join(seg.text.strip() for seg in segments).strip()
        self._buffer.clear()

        return {"type": "transcript", "text": transcript, "rms": round(rms, 5)}
