#!/usr/bin/env python3
"""Mentor Khanh AI - Studio Mastering Pipeline
Phát triển từ bản gốc 01 thành các phiên bản Phòng Thu Chuyên Nghiệp (Studio Pro / Broadcast).
"""

from pathlib import Path
import subprocess

ROOT = Path("/root/projects/khanh-voice")
OUTPUT_DIR = ROOT / "output" / "mentor-khanh-studio"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
RAW_WAV = ROOT / "output" / "mentor-khanh-demo" / "mentor-khanh-v1-raw.wav"

STUDIO_VARIANTS = [
    (
        "01-studio-shure-sm7b-warm.mp3",
        (
            # Giữ nguyên nhịp độ 1.0 của bản 01
            # Highpass lọc rumble dưới 50Hz
            # Boost dải ấm ngực 120-150Hz (+2.2dB) tạo chất mic Shure SM7B
            # Dip nhẹ vùng đục 450Hz (-1.2dB) để tiếng thoáng
            # Air boost dải cao 9kHz-12kHz (+1.8dB) tạo độ mướt, thở
            # De-esser nhẹ qua notch filter 6.5kHz
            # Compressor nhẹ giúp giọng đều lực, dày dặn
            # Chuẩn hóa EBU R128 (-16 LUFS)
            "highpass=f=48,"
            "equalizer=f=130:t=q:w=1.2:g=2.2,"
            "equalizer=f=450:t=q:w=1.4:g=-1.2,"
            "equalizer=f=2800:t=q:w=1.2:g=1.4,"
            "equalizer=f=10500:t=q:w=0.8:g=1.8,"
            "acompressor=threshold=-18dB:ratio=2.5:attack=15:release=120:makeup=2dB,"
            "loudnorm=I=-16:TP=-1.5:LRA=7"
        ),
        "Studio Mic Shure SM7B (Dày ấm, lực trầm tự nhiên, phong thái Podcast Pro)"
    ),
    (
        "02-studio-neumann-u87-condenser.mp3",
        (
            # Mô phỏng chất mic Condenser phòng thu Neumann U87: trong trẻo, mượt mà, siêu chi tiết
            "highpass=f=52,"
            "equalizer=f=110:t=q:w=1.0:g=1.8,"
            "equalizer=f=350:t=q:w=1.5:g=-1.0,"
            "equalizer=f=3200:t=q:w=1.1:g=2.0,"
            "equalizer=f=12000:t=q:w=0.7:g=2.4,"
            "acompressor=threshold=-20dB:ratio=2.2:attack=10:release=100:makeup=2.5dB,"
            "loudnorm=I=-16:TP=-1.5:LRA=8"
        ),
        "Studio Condenser U87 (Trong trẻo, ấm mượt, bắt trọn từng chi tiết hơi thở)"
    ),
    (
        "03-studio-acoustic-treated-warmth.mp3",
        (
            # Không gian phòng thu tiêu âm hoàn hảo + Tube Preamp ấm áp
            "highpass=f=45,"
            "equalizer=f=140:t=q:w=1.0:g=2.8,"
            "equalizer=f=250:t=q:w=1.2:g=1.2,"
            "equalizer=f=600:t=q:w=1.6:g=-1.5,"
            "equalizer=f=4000:t=q:w=1.2:g=1.2,"
            "equalizer=f=9500:t=q:w=0.9:g=1.5,"
            "acompressor=threshold=-16dB:ratio=3.0:attack=20:release=150:makeup=2dB,"
            "loudnorm=I=-15.5:TP=-1.2:LRA=6"
        ),
        "Studio Tube Warmth (Âm thanh ấm áp qua đèn tiền khuếch đại, phòng tiêu âm chuẩn)"
    ),
    (
        "04-studio-broadcast-executive.mp3",
        (
            # Chuẩn đài phát thanh / Mentor khóa học cao cấp (Rõ từng từ, kiểm soát âm lượng tuyệt đối)
            "highpass=f=55,"
            "equalizer=f=125:t=q:w=1.1:g=2.0,"
            "equalizer=f=2400:t=q:w=1.3:g=2.2,"
            "equalizer=f=8000:t=q:w=1.0:g=1.6,"
            "acompressor=threshold=-22dB:ratio=3.2:attack=8:release=80:makeup=3dB,"
            "loudnorm=I=-15:TP=-1.0:LRA=6"
        ),
        "Broadcast Executive (Quyền uy, sang trọng, rõ nét từng âm tiết, dứt khoát)"
    )
]

for filename, audio_filter, desc in STUDIO_VARIANTS:
    out_path = OUTPUT_DIR / filename
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error", "-i", str(RAW_WAV),
        "-af", audio_filter,
        "-codec:a", "libmp3lame", "-b:a", "256k", str(out_path)
    ]
    subprocess.run(cmd, check=True)
    print(f"Generated: {out_path} ({desc})")
