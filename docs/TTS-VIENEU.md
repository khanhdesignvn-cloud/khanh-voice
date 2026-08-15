# VieNeu-TTS Engine & Voice Training Guide

Luồng TTS ưu tiên VieNeu v3 Turbo chạy cục bộ, clone giọng từ mẫu audio `voice-references/khanh-podcast-reference.wav`. Audio sau khi sinh được lọc dải tần và chuẩn hóa ở -16 LUFS cho chất giọng podcast.

Nhịp đọc chuẩn dùng `VIENEU_TEMPO=0.88`; các ý trong kịch bản được ngăn bằng khoảng nghỉ để giọng có nhịp nhấn rõ hơn.

## Cài đặt trên Linux / WSL

```bash
python -m venv .venv
source .venv/bin/activate
pip install vieneu torch torchaudio
```

## Cài đặt trên Windows

Yêu cầu Python 3.10 - 3.12, eSpeak NG và FFmpeg:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install vieneu --extra-index-url https://pnnbao97.github.io/llama-cpp-python-v0.3.16/cpu/
.\.venv\Scripts\python.exe -m pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu
Copy-Item .env.example .env
```

`.env` và `.venv` chỉ nằm trên máy cục bộ, không được commit. Mô hình sẽ được tải vào cache trong lần chạy đầu tiên.

## Các Preset Giọng có sẵn trong VieNeu:
1. **Quang Sơn:** Giọng nam miền Trung ấm, tự nhiên.
2. **Ngọc Trân:** Giọng nữ miền Trung nhẹ nhàng, biểu cảm.
3. **Thanh Bình:** Giọng nam kể chuyện sâu lắng, trầm ấm.
4. **Thái Sơn:** Giọng nam chính luận, dứt khoát.
