#!/usr/bin/env python3
"""Mentor Khanh AI - Voice Training & Synthesis Iteration Script"""

import os
import sys
from pathlib import Path
import subprocess

ROOT = Path("/root/projects/khanh-voice")
OUTPUT_DIR = ROOT / "output" / "mentor-khanh-demo"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

REF_AUDIO = ROOT / "voice-references" / "mentor-khanh-ref-01.wav"

TEST_TEXT = (
    "Xin chào các bạn, tôi là Mentor Khánh. "
    "Chào mừng bạn đến với chuỗi chia sẻ về xây dựng thương hiệu và tối ưu quy trình tự động hóa. "
    "Một thương hiệu mạnh không cần nói quá nhiều, mà nằm ở sự nhất quán và trải nghiệm thực tế."
)

print(f"Loading VieNeu v3turbo...")
from vieneu import Vieneu
tts = Vieneu(mode="v3turbo")

print(f"Synthesizing test audio with reference: {REF_AUDIO}...")
audio = tts.infer(
    text=TEST_TEXT,
    ref_audio=REF_AUDIO,
    denoise=True,
    temperature=0.72,
    top_p=0.90,
    repetition_penalty=1.25,
)

raw_wav = OUTPUT_DIR / "mentor-khanh-v1-raw.wav"
tts.save(audio, raw_wav)
print(f"Saved raw synthesis to {raw_wav}")

# Variant 1: Podcast Warm Master
mp3_warm = OUTPUT_DIR / "mentor-khanh-v1-podcast-warm.mp3"
subprocess.run([
    "ffmpeg", "-y", "-loglevel", "error", "-i", str(raw_wav),
    "-af", (
        "atempo=0.92,highpass=f=55,lowpass=f=14000,"
        "equalizer=f=135:t=q:w=1.1:g=2.2,"
        "equalizer=f=280:t=q:w=1.2:g=1.2,"
        "loudnorm=I=-16:TP=-1.5:LRA=9"
    ),
    "-codec:a", "libmp3lame", "-q:a", "2", str(mp3_warm)
], check=True)
print(f"Generated Warm Master: {mp3_warm}")

# Variant 2: Crisp & Clear Broadcast
mp3_crisp = OUTPUT_DIR / "mentor-khanh-v1-crisp.mp3"
subprocess.run([
    "ffmpeg", "-y", "-loglevel", "error", "-i", str(raw_wav),
    "-af", (
        "atempo=0.95,highpass=f=65,lowpass=f=15000,"
        "equalizer=f=160:t=q:w=1.1:g=1.2,"
        "equalizer=f=2600:t=q:w=1.3:g=1.4,"
        "loudnorm=I=-16:TP=-1.5:LRA=9"
    ),
    "-codec:a", "libmp3lame", "-q:a", "2", str(mp3_crisp)
], check=True)
print(f"Generated Crisp Master: {mp3_crisp}")
