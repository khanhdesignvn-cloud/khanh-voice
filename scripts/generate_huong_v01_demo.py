#!/usr/bin/env python3
"""Tạo bản thử giọng Hương v.01 từ mẫu đã chuẩn hóa."""
from pathlib import Path
import subprocess
from vieneu import Vieneu

ROOT = Path('/root/projects/khanh-voice')
REF = ROOT / 'voice-references/huong-v01/huong-v01-clean.wav'
OUT = ROOT / 'voice-demos/huong-v01'
OUT.mkdir(parents=True, exist_ok=True)
TEXT = (
    'Xin chào, đây là bản thử nghiệm giọng nói Hương phiên bản một. '
    'Mỗi ngày là một cơ hội mới để chúng ta học hỏi, sáng tạo và chia sẻ những điều tốt đẹp. '
    'Cảm ơn bạn đã lắng nghe.'
)

tts = Vieneu(mode='v3turbo')
audio = tts.infer(text=TEXT, ref_audio=REF, denoise=True,
                  temperature=0.72, top_p=0.90, repetition_penalty=1.25)
raw = OUT / 'huong-v01-demo-raw.wav'
tts.save(audio, raw)
master = OUT / 'huong-v01-demo.mp3'
filters = (
    'highpass=f=60,equalizer=f=120:t=q:w=1.0:g=1.4,'
    'equalizer=f=350:t=q:w=1.5:g=-0.8,equalizer=f=3200:t=q:w=1.1:g=1.6,'
    'acompressor=threshold=-20dB:ratio=2.2:attack=10:release=100:makeup=2dB,'
    'loudnorm=I=-16:TP=-1.5:LRA=8'
)
subprocess.run(['ffmpeg','-y','-loglevel','error','-i',str(raw),'-af',filters,
                '-codec:a','libmp3lame','-b:a','256k',str(master)],check=True)
print(master)
