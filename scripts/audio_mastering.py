#!/usr/bin/env python3
"""Podcast mastering filter using FFmpeg for warm, crisp voice output."""

import argparse
from pathlib import Path
import subprocess


def master_audio(
    input_file: Path,
    output_file: Path,
    tempo: float = 0.90,
    target_lufs: float = -16.0,
    profile: str = "podcast_warm",
) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)

    if profile == "podcast_warm":
        audio_filter = (
            f"atempo={tempo},"
            "highpass=f=58,lowpass=f=14000,"
            "equalizer=f=135:t=q:w=1.1:g=2.4,"
            "equalizer=f=280:t=q:w=1.2:g=1.2,"
            f"loudnorm=I={target_lufs}:TP=-1.5:LRA=9"
        )
    elif profile == "central_smooth":
        audio_filter = (
            f"atempo={tempo},"
            "highpass=f=62,lowpass=f=14500,"
            "equalizer=f=145:t=q:w=1.1:g=1.8,"
            "equalizer=f=320:t=q:w=1.2:g=0.8,"
            f"loudnorm=I={target_lufs}:TP=-1.5:LRA=9"
        )
    elif profile == "clean_video":
        audio_filter = (
            f"atempo={tempo},"
            "highpass=f=65,lowpass=f=15000,"
            "equalizer=f=160:t=q:w=1.1:g=1.2,"
            f"loudnorm=I={target_lufs}:TP=-1.5:LRA=9"
        )
    else:
        audio_filter = f"atempo={tempo},loudnorm=I={target_lufs}:TP=-1.5:LRA=9"

    cmd = [
        "ffmpeg", "-y", "-loglevel", "error", "-i", str(input_file),
        "-af", audio_filter,
        "-codec:a", "libmp3lame", "-q:a", "2", str(output_file),
    ]
    subprocess.run(cmd, check=True)
    print(f"[mastering] Filtered '{profile}' output saved to {output_file}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Master audio for Podcast/Video")
    parser.add_argument("--input", required=True, help="Input audio file (WAV/MP3)")
    parser.add_argument("--output", required=True, help="Output MP3 file")
    parser.add_argument("--tempo", type=float, default=0.90, help="Tempo factor (e.g. 0.90)")
    parser.add_argument("--lufs", type=float, default=-16.0, help="Integrated loudness in LUFS (-16 for podcast, -18.5 for video)")
    parser.add_argument("--profile", choices=["podcast_warm", "central_smooth", "clean_video", "flat"], default="podcast_warm", help="Audio EQ profile")

    args = parser.parse_args()
    master_audio(
        input_file=Path(args.input),
        output_file=Path(args.output),
        tempo=args.tempo,
        target_lufs=args.lufs,
        profile=args.profile,
    )


if __name__ == "__main__":
    main()
