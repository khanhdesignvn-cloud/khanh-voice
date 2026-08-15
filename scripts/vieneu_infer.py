#!/usr/bin/env python3
"""Generate Vietnamese podcast narration with an approved voice sample."""

import argparse
import os
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description="VieNeu voice synthesis")
    parser.add_argument("text_file", help="Path to text file")
    parser.add_argument("ref_audio", help="Path to reference WAV audio")
    parser.add_argument("output_wav", help="Path to output WAV file")
    args = parser.parse_args()

    with open(args.text_file, "r", encoding="utf-8") as handle:
        text = handle.read().strip()
    if not text:
        raise ValueError("Narration text is empty")

    from vieneu import Vieneu

    emotion = os.environ.get("VIENEU_EMOTION", "storytelling")
    print(f"[vieneu] Loading v3 Turbo; delivery={emotion}", file=sys.stderr)
    tts = Vieneu(mode="v3turbo")

    print(f"[vieneu] Synthesizing {len(text)} characters", file=sys.stderr)
    audio = tts.infer(
        text=text,
        ref_audio=args.ref_audio,
        style=emotion,
        denoise=True,
        temperature=0.72,
        top_p=0.9,
        repetition_penalty=1.25,
    )
    tts.save(audio, args.output_wav)
    print(f"[vieneu] Saved WAV output to {args.output_wav}", file=sys.stderr)


if __name__ == "__main__":
    main()
