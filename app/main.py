#!/usr/bin/env python3
"""Free TTS web app backend, powered by Microsoft Edge Neural TTS (no API key required)."""

import io
from pathlib import Path

import edge_tts
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"

app = FastAPI(title="Khanh Voice - Free TTS")

VOICES = [
    {"id": "vi-VN-HoaiMyNeural", "label": "Hoài My (Nữ, miền Bắc)"},
    {"id": "vi-VN-NamMinhNeural", "label": "Nam Minh (Nam, miền Bắc)"},
    {"id": "en-US-AriaNeural", "label": "Aria (English, US, Female)"},
    {"id": "en-US-GuyNeural", "label": "Guy (English, US, Male)"},
    {"id": "en-GB-SoniaNeural", "label": "Sonia (English, UK, Female)"},
    {"id": "ja-JP-NanamiNeural", "label": "Nanami (Japanese, Female)"},
    {"id": "ko-KR-SunHiNeural", "label": "SunHi (Korean, Female)"},
    {"id": "zh-CN-XiaoxiaoNeural", "label": "Xiaoxiao (Chinese, Female)"},
    {"id": "fr-FR-DeniseNeural", "label": "Denise (French, Female)"},
]
VOICE_IDS = {v["id"] for v in VOICES}


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    voice: str = "vi-VN-HoaiMyNeural"
    rate: int = Field(0, ge=-50, le=50)
    pitch: int = Field(0, ge=-50, le=50)


@app.get("/api/voices")
def list_voices():
    return VOICES


@app.post("/api/tts")
async def synthesize(req: TTSRequest):
    if req.voice not in VOICE_IDS:
        raise HTTPException(status_code=400, detail="Giọng không hợp lệ")

    communicate = edge_tts.Communicate(
        req.text,
        req.voice,
        rate=f"{req.rate:+d}%",
        pitch=f"{req.pitch:+d}Hz",
    )

    audio_chunks = []
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_chunks.append(chunk["data"])

    if not audio_chunks:
        raise HTTPException(status_code=502, detail="Không tạo được âm thanh, vui lòng thử lại")

    audio_bytes = b"".join(audio_chunks)
    return StreamingResponse(
        io.BytesIO(audio_bytes),
        media_type="audio/mpeg",
        headers={"Content-Disposition": 'attachment; filename="giong-noi.mp3"'},
    )


app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
