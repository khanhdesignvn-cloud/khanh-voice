#!/usr/bin/env python3
"""Generate comparable VieNeu voice samples for podcast voice selection."""

from pathlib import Path
import subprocess

try:
    from vieneu import Vieneu
except ImportError:
    Vieneu = None


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "voice-demos"
REFERENCE = ROOT / "voice-references" / "khanh-podcast-reference.wav"
TEXT = (
    "Một thương hiệu mạnh không cần nói quá nhiều. "
    "Điều quan trọng là mỗi điểm chạm đều rõ ràng, nhất quán, "
    "và tạo được niềm tin."
)

VOICES = [
    ("01-khanh-giong-mau", None),
    ("02-quang-son-mien-trung", "Quang Sơn"),
    ("03-thanh-binh-ke-chuyen", "Thanh Bình"),
    ("04-thai-son-ke-chuyen", "Thái Sơn"),
]


def main() -> None:
    if Vieneu is None:
        print("Lỗi: Thư viện 'vieneu' chưa được cài đặt. Vui lòng chạy: pip install vieneu torch torchaudio")
        return

    OUTPUT.mkdir(parents=True, exist_ok=True)
    tts = Vieneu(mode="v3turbo")

    for filename, preset_name in VOICES:
        wav_path = OUTPUT / f"{filename}.wav"
        mp3_path = OUTPUT / f"{filename}.mp3"
        if preset_name:
            voice = tts.get_preset_voice(preset_name)
            audio = tts.infer(
                text=TEXT,
                voice=voice,
                temperature=0.72,
                top_p=0.9,
                repetition_penalty=1.25,
            )
        else:
            if not REFERENCE.exists():
                print(f"Bỏ qua clone: Không tìm thấy file mẫu tại {REFERENCE}")
                continue
            audio = tts.infer(
                text=TEXT,
                ref_audio=REFERENCE,
                denoise=True,
                temperature=0.72,
                top_p=0.9,
                repetition_penalty=1.25,
            )
        tts.save(audio, wav_path)
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error", "-i", str(wav_path),
            "-af", (
                "atempo=0.90,highpass=f=58,lowpass=f=14000,"
                "equalizer=f=135:t=q:w=1.1:g=2.4,"
                "equalizer=f=280:t=q:w=1.2:g=1.2,"
                "loudnorm=I=-16:TP=-1.5:LRA=9"
            ),
            "-codec:a", "libmp3lame", "-q:a", "2", str(mp3_path),
        ], check=True)
        print(f"Đã tạo: {mp3_path}")


if __name__ == "__main__":
    main()
