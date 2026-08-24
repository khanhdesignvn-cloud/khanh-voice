# Khanh Voice TTS & Voice Training Engine

Hệ thống xử lý âm thanh, sinh giọng đọc TTS chất lượng cao (Podcast / Storytelling) và đào tạo/nhân bản giọng nói phục vụ chuỗi video & podcast của **Nguyễn Quốc Khánh**.

---

## 🌟 Tính năng chính

1. **VieNeu-TTS (Local AI Voice Cloning):**
   - Chạy trực tiếp mô hình v3 Turbo cục bộ.
   - Nhân bản chất giọng podcast thương hiệu từ mẫu giọng mẫu (`voice-references/`).
   - Cung cấp các preset giọng vùng miền Việt Nam (Quang Sơn - Miền Trung, Ngọc Trân, Thanh Bình, Thái Sơn...).

2. **Edge TTS High-Definition (Keyless & Fast):**
   - Hỗ trợ giọng chuẩn đa vùng miền qua Microsoft Neural Network.
   - Tự động trích xuất `WordBoundary` phục vụ đồng bộ phụ đề chính xác từng mili-giây.

3. **Bộ lọc hậu kỳ Podcast Master Filter (FFmpeg):**
   - Chuẩn hóa âm lượng theo chuẩn quốc tế: `-16 LUFS` (Podcast) hoặc `-18.5 LUFS` (Video).
   - Bộ lọc dải tần (Highpass, Lowpass, Equalizer làm ấm và dày chất giọng nam/nữ).

4. **Multi-provider Cloud Fallback:**
   - Tích hợp linh hoạt ElevenLabs và Google Gemini TTS khi cần mở rộng.

---

## 🆓 Phần mềm tạo giọng nói miễn phí (Web App)

Ứng dụng web đơn giản chạy cục bộ, dùng Microsoft Edge Neural TTS — **hoàn toàn miễn phí, không cần API key**. Gõ văn bản, chọn giọng, nghe thử và tải file MP3.

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Mở trình duyệt tại `http://localhost:8000`.

## 📁 Cấu trúc thư mục

```text
khanh-voice/
├── app/
│   ├── main.py                      # Backend FastAPI cho web app TTS miễn phí (Edge TTS)
│   └── static/index.html            # Giao diện web
├── scripts/
│   ├── vieneu_infer.py              # Script sinh giọng VieNeu qua reference audio
│   ├── generate_voice_demos.py       # Tạo so sánh 4 bản demo phong cách podcast
│   ├── generate_central_voice_demos.py # Tạo so sánh các giọng miền Trung
│   ├── edge_tts_generator.py        # Sinh giọng Edge TTS kèm word timing
│   └── audio_mastering.py           # Bộ lọc âm chuẩn podcast bằng FFmpeg
├── voice-references/                # Thư mục chứa audio mẫu huấn luyện/clone
├── docs/
│   └── TTS-VIENEU.md                # Hướng dẫn chi tiết thiết lập & đào tạo VieNeu
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Cài đặt & Sử dụng

### 1. Cài đặt môi trường Python (Khuyến nghị Python 3.10 - 3.12)

```bash
python -m venv .venv
source .venv/bin/activate  # Trên Linux/macOS
# Hoặc trên Windows: .\.venv\Scripts\activate

pip install edge-tts vieneu torch torchaudio
```

### 2. Chạy tạo mẫu so sánh giọng Podcast

```bash
python scripts/generate_voice_demos.py
```

### 3. Chạy tạo mẫu giọng miền Trung

```bash
python scripts/generate_central_voice_demos.py
```

### 4. Sinh giọng đọc Edge TTS kèm timing

```bash
python scripts/edge_tts_generator.py --text "Một thương hiệu mạnh không cần nói quá nhiều." --voice "vi-VN-NamMinhNeural" --output "output/sample.mp3"
```
