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

## 💳 Website bán key TTS (Web App)

Website hoàn chỉnh: trang bán hàng → thanh toán tự động qua **PayOS** → phát key tự động → công cụ tạo giọng nói (Microsoft Edge Neural TTS) khoá bằng key → trang quản trị.

**Chạy thử cục bộ (không cần tài khoản PayOS thật để xem giao diện):**

```bash
pip install -r requirements.txt
cp .env.example .env   # rồi điền ADMIN_PASSWORD, SECRET_KEY tối thiểu
uvicorn app.main:app --reload
```

| Trang | Đường dẫn | Mô tả |
|---|---|---|
| Bán hàng | `/` | Khách chọn gói, thanh toán qua PayOS |
| Công cụ TTS | `/app` | Nhập key để kích hoạt và tạo giọng nói |
| Sau thanh toán | `/thanks` | Hiện key vừa mua |
| Quản trị | `/admin` | Đăng nhập bằng `ADMIN_PASSWORD`: quản lý gói giá, cấp key thủ công, xem đơn hàng |

**Thiết lập PayOS (bắt buộc để bán hàng tự động):**
1. Tạo tài khoản merchant tại [payos.vn](https://payos.vn), lấy `Client ID`, `API Key`, `Checksum Key`.
2. Điền 3 giá trị này cùng `PUBLIC_BASE_URL` (domain thật, có `https://`) vào `.env`.
3. Sau khi deploy lên domain thật, vào `/admin` → bấm **"Đăng ký Webhook với PayOS"** một lần duy nhất để PayOS biết gửi thông báo thanh toán về đâu.

**Mô hình key:** mỗi key có thời hạn (7/30/365 ngày...) tính từ **lần đầu kích hoạt** (nhập key tại `/app`), không tính từ lúc mua — khách không bị mất thời gian nếu chưa dùng ngay. Key = tài khoản, không cần đăng ký username/password riêng.

⚠️ **Lưu ý:** `edge-tts` dùng ngược tính năng "Đọc to" miễn phí của Microsoft Edge, không phải API thương mại chính thức — không có SLA, có thể thay đổi/chặn bất kỳ lúc nào. Nếu kinh doanh lâu dài, nên chuyển gói trả phí sang giọng VieNeu (chạy local, xem mục bên dưới) và chỉ dùng Edge TTS cho gói dùng thử.

**Triển khai lên VPS thật:** xem `deploy/` (Dockerfile, docker-compose, cấu hình Nginx + script `deploy.sh`). Chạy `deploy/deploy.sh` **trên VPS** (không phải từ máy khác) sau khi đã tạo `.env` với thông tin thật.

## 📁 Cấu trúc thư mục

```text
khanh-voice/
├── app/
│   ├── main.py                      # Khởi tạo FastAPI, gắn router, phục vụ trang HTML
│   ├── config.py                    # Đọc cấu hình từ biến môi trường
│   ├── db.py                        # SQLite: packages / orders / keys / sessions
│   ├── security.py                  # Xác thực admin + phiên đăng nhập bằng key
│   ├── payments.py                  # Tích hợp PayOS (SDK chính thức)
│   ├── routes_public.py             # API bán hàng: /api/packages, /api/checkout, /api/order
│   ├── routes_webhook.py            # /api/payos/webhook — xác thực chữ ký & phát key
│   ├── routes_tts.py                # /api/redeem, /api/voices, /api/tts (yêu cầu key)
│   ├── routes_admin.py              # /api/admin/* — quản lý gói/key/đơn hàng
│   └── static/                      # landing.html, app.html, thanks.html, cancel.html, admin.html
├── deploy/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── nginx.conf.example
│   └── deploy.sh                    # Script deploy chạy trên VPS
├── data/                            # File SQLite khanhvoice.db (không commit)
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
