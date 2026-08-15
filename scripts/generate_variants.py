#!/usr/bin/env python3
"""Generate multiple audio variants for Mentor Khanh AI comparison."""

from pathlib import Path
import subprocess

ROOT = Path("/root/projects/khanh-voice")
OUTPUT_DIR = ROOT / "output" / "mentor-khanh-demo"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
RAW_WAV = OUTPUT_DIR / "mentor-khanh-v1-raw.wav"

VARIANTS = [
    (
        "01-mentor-khanh-raw-clone.mp3",
        "atempo=1.0,loudnorm=I=-16:TP=-1.5:LRA=9",
        "Bản clone mộc thuần túy (nguyên bản nhịp độ và âm sắc sinh ra từ mẫu gốc)."
    ),
    (
        "02-mentor-khanh-podcast-warm.mp3",
        "atempo=0.92,highpass=f=55,lowpass=f=14000,equalizer=f=135:t=q:w=1.1:g=2.6,equalizer=f=280:t=q:w=1.2:g=1.4,loudnorm=I=-16:TP=-1.5:LRA=9",
        "Bản Podcast Trầm Ấm (giảm tốc 8%, tăng âm trầm dải 135Hz, dày dặn, thư thái)."
    ),
    (
        "03-mentor-khanh-dinhtac-ro-rang.mp3",
        "atempo=0.95,highpass=f=65,lowpass=f=15000,equalizer=f=160:t=q:w=1.1:g=1.2,equalizer=f=2600:t=q:w=1.3:g=1.5,loudnorm=I=-16:TP=-1.5:LRA=9",
        "Bản Đĩnh Đạc - Rõ Ràng (tốc độ vừa phải, tăng độ nét dải trung cao 2.6kHz, phong thái mentor dứt khoát)."
    ),
    (
        "04-mentor-khanh-chuyen-gia-sau-lang.mp3",
        "rubberband=tempo=0.88:pitch=0.97,highpass=f=50,lowpass=f=13500,equalizer=f=120:t=q:w=1.0:g=3.0,equalizer=f=250:t=q:w=1.2:g=1.5,loudnorm=I=-16:TP=-1.5:LRA=9",
        "Bản Chuyên Gia Sâu Lắng (hạ nhẹ tone giọng, nhịp chậm rãi, chiều sâu suy ngẫm)."
    )
]

for filename, audio_filter, desc in VARIANTS:
    out_path = OUTPUT_DIR / filename
    # Check if rubberband filter is supported, else fallback to standard filter
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error", "-i", str(RAW_WAV),
        "-af", audio_filter,
        "-codec:a", "libmp3lame", "-q:a", "2", str(out_path)
    ]
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        # Fallback if rubberband not compiled
        fallback_filter = audio_filter.replace("rubberband=tempo=0.88:pitch=0.97", "atempo=0.88")
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-i", str(RAW_WAV),
            "-af", fallback_filter,
            "-codec:a", "libmp3lame", "-q:a", "2", str(out_path)
        ], check=True)
    print(f"Generated: {out_path} ({desc})")
