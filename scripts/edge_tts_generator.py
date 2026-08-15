#!/usr/bin/env python3
"""Edge TTS synthesis module with word timing metadata for synchronization."""

import argparse
import asyncio
import json
from pathlib import Path
from typing import Optional

import edge_tts


async def run_edge_tts(
    text: str,
    voice: str,
    rate: str,
    pitch: str,
    output_mp3: Path,
    timing_json: Optional[Path] = None,
) -> None:
    output_mp3.parent.mkdir(parents=True, exist_ok=True)
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, boundary="WordBoundary")

    words = []
    with open(output_mp3, "wb") as f_out:
        async for chunk in communicate.stream():
            chunk_type = chunk.get("type")
            if chunk_type == "audio" and "data" in chunk:
                f_out.write(chunk["data"])
            elif chunk_type == "WordBoundary" and "text" in chunk:
                words.append({
                    "text": chunk["text"],
                    "offset": chunk.get("offset", 0) / 10_000_000,
                    "duration": chunk.get("duration", 0) / 10_000_000,
                })

    if timing_json and words:
        timing_json.parent.mkdir(parents=True, exist_ok=True)
        timing_json.write_text(json.dumps(words, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[edge-tts] Saved {len(words)} word timings to {timing_json}")

    print(f"[edge-tts] Synthesized audio to {output_mp3}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate speech using Microsoft Edge Neural TTS")
    parser.add_argument("--text", required=True, help="Text to speak")
    parser.add_argument("--voice", default="vi-VN-NamMinhNeural", help="Voice model (e.g. vi-VN-NamMinhNeural, vi-VN-HoaiMyNeural)")
    parser.add_argument("--rate", default="+0%", help="Speed adjustment (e.g. -10%, +0%)")
    parser.add_argument("--pitch", default="+0Hz", help="Pitch adjustment (e.g. +2Hz, +0Hz)")
    parser.add_argument("--output", default="output/voice.mp3", help="Output MP3 path")
    parser.add_argument("--timing", default=None, help="Optional output JSON path for word timing metadata")

    args = parser.parse_args()
    asyncio.run(run_edge_tts(
        text=args.text,
        voice=args.voice,
        rate=args.rate,
        pitch=args.pitch,
        output_mp3=Path(args.output),
        timing_json=Path(args.timing) if args.timing else None,
    ))


if __name__ == "__main__":
    main()
