# Khánh Podcast v.01 — Bộ lọc Mastering chính thức (reusable)

"""Script tạo giọng Khánh Podcast v.01 từ clone thô.

Cách dùng:
    python scripts/master_khanh_podcast.py <input_wav> <output_mp3>
"""

import subprocess
import sys
from pathlib import Path

NEUMANN_U87_FILTER = (
    "highpass=f=52,"
    "equalizer=f=110:t=q:w=1.0:g=1.8,"
    "equalizer=f=350:t=q:w=1.5:g=-1.0,"
    "equalizer=f=3200:t=q:w=1.1:g=2.0,"
    "equalizer=f=12000:t=q:w=0.7:g=2.4,"
    "acompressor=threshold=-20dB:ratio=2.2:attack=10:release=100:makeup=2.5dB,"
    "loudnorm=I=-16:TP=-1.5:LRA=8"
)


def master(input_wav: Path, output_mp3: Path) -> None:
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-i", str(input_wav),
        "-af", NEUMANN_U87_FILTER,
        "-codec:a", "libmp3lame", "-b:a", "256k", str(output_mp3),
    ], check=True)
    print(f"✅ Khánh Podcast v.01: {output_mp3}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Dùng: python scripts/master_khanh_podcast.py <input.wav> <output.mp3>")
        sys.exit(1)
    master(Path(sys.argv[1]), Path(sys.argv[2]))
