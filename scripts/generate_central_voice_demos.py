#!/usr/bin/env python3
"""Generate easy-listening Central Vietnamese VieNeu voice comparisons."""

from pathlib import Path
import subprocess

try:
    from vieneu import Vieneu
except ImportError:
    Vieneu = None


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "voice-demos"
TEXT = (
    "Một thương hiệu mạnh không cần nói quá nhiều. "
    "Điều quan trọng là mỗi điểm chạm đều rõ ràng, nhất quán, "
    "và tạo được niềm tin."
)


def encode(source: Path, target: Path, audio_filter: str) -> None:
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error", "-i", str(source),
        "-af", f"{audio_filter},loudnorm=I=-16:TP=-1.5:LRA=9",
        "-codec:a", "libmp3lame", "-q:a", "2", str(target),
    ], check=True)


def main() -> None:
    if Vieneu is None:
        print("Lỗi: Thư viện 'vieneu' chưa được cài đặt. Vui lòng chạy: pip install vieneu torch torchaudio")
        return

    OUTPUT.mkdir(parents=True, exist_ok=True)
    tts = Vieneu(mode="v3turbo")

    quang_son = tts.get_preset_voice("Quang Sơn")
    male_audio = tts.infer(
        text=TEXT,
        voice=quang_son,
        temperature=0.68,
        top_p=0.88,
        repetition_penalty=1.25,
    )
    male_wav = OUTPUT / "central-quang-son-source.wav"
    tts.save(male_audio, male_wav)

    male_variants = [
        (
            "05-quang-son-tu-nhien-am.mp3",
            "atempo=0.93,highpass=f=62,lowpass=f=14500,"
            "equalizer=f=145:t=q:w=1.1:g=1.8,equalizer=f=320:t=q:w=1.2:g=.8",
        ),
        (
            "06-quang-son-tram-podcast.mp3",
            "rubberband=tempo=0.89:pitch=0.965,highpass=f=55,lowpass=f=13800,"
            "equalizer=f=125:t=q:w=1.05:g=2.8,equalizer=f=260:t=q:w=1.2:g=1.4",
        ),
        (
            "07-quang-son-ro-cham-vua.mp3",
            "atempo=0.96,highpass=f=68,lowpass=f=15000,"
            "equalizer=f=170:t=q:w=1.1:g=1.2,equalizer=f=2500:t=q:w=1.3:g=1.0",
        ),
    ]
    for filename, audio_filter in male_variants:
        target = OUTPUT / filename
        encode(male_wav, target, audio_filter)
        print(f"Đã tạo: {target}")

    ngoc_tran = tts.get_preset_voice("Ngọc Trân")
    female_audio = tts.infer(
        text=TEXT,
        voice=ngoc_tran,
        temperature=0.68,
        top_p=0.88,
        repetition_penalty=1.25,
    )
    female_wav = OUTPUT / "central-ngoc-tran-source.wav"
    tts.save(female_audio, female_wav)
    female_target = OUTPUT / "08-ngoc-tran-mien-trung.mp3"
    encode(
        female_wav,
        female_target,
        "atempo=0.94,highpass=f=75,lowpass=f=15000,equalizer=f=190:t=q:w=1.1:g=1.0",
    )
    print(f"Đã tạo: {female_target}")


if __name__ == "__main__":
    main()
