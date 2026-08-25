"""Key redemption and the key-gated text-to-speech endpoint."""

import io
import time

import edge_tts
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from . import db, security

router = APIRouter(prefix="/api")

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


class RedeemRequest(BaseModel):
    code: str = Field(..., min_length=4, max_length=64)


@router.post("/redeem")
def redeem_key(req: RedeemRequest):
    code = req.code.strip().upper()
    key = db.get_key_by_code(code)
    if not key:
        raise HTTPException(status_code=404, detail="Key không tồn tại")

    if key["status"] == "unused":
        key = db.activate_key(key["id"], key["duration_days"])
    elif key["status"] == "active":
        if key["expires_at"] and db.parse_iso(key["expires_at"]).timestamp() < time.time():
            db.expire_key(key["id"])
            raise HTTPException(status_code=403, detail="Key đã hết hạn")
    else:
        raise HTTPException(status_code=403, detail="Key đã bị thu hồi hoặc hết hạn")

    token = security.new_session_token()
    db.create_session(token, key["id"])

    return {"session_token": token, "expires_at": key["expires_at"]}


@router.get("/voices")
def list_voices(key=Depends(security.require_key_session)):
    return VOICES


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    voice: str = "vi-VN-HoaiMyNeural"
    rate: int = Field(0, ge=-50, le=50)
    pitch: int = Field(0, ge=-50, le=50)


@router.post("/tts")
async def synthesize(req: TTSRequest, key=Depends(security.require_key_session)):
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
