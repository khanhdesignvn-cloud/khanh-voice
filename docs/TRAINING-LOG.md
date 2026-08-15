# Mentor Khánh AI - Voice Training Log & Profiles

Tài liệu lưu trữ các thông số, mẫu giọng và đánh giá phản hồi để chất giọng **Mentor Khánh AI** thông minh và hoàn thiện dần theo thời gian.

---

## 🎯 Định vị Persona: "Mentor Khánh AI"
* **Phong cách:** Chuyên gia, chia sẻ kiến thức, trầm ấm, rõ ràng, truyền cảm hứng và tự tin.
* **Mục tiêu ứng dụng:** Đọc voice cho Podcast, video thương hiệu, video chia sẻ chuyên môn, hướng dẫn kỹ thuật.

---

## 🧬 Dữ liệu mẫu (Training Dataset)

### Mẫu 1: `voice-references/mentor-khanh-ref-01.wav`
* **Nguồn gốc:** File ghi âm trực tiếp qua Telegram (`1JVVPMQLT_3NTNH2.aac`)
* **Thời lượng:** ~36.15 giây
* **Định dạng gốc:** AAC mono 44.1kHz -> Chuẩn hóa WAV 24kHz / Bandpass filter 60Hz-12kHz / Loudnorm -16 LUFS
* **Đặc trưng âm học sơ bộ:**
  - Giọng nam, tự nhiên, nhịp điệu đĩnh đạc, rõ ràng.
  - Phù hợp làm mẫu tham chiếu gốc (Reference Voice Anchor) cho việc clone và tuning.

---

## 🛠️ Lộ trình huấn luyện (Training Pipeline)

1. **Local CPU Engine (VieNeu-TTS):**
   - Phù hợp chạy trực tiếp trên server với CPU Intel Xeon.
   - Sử dụng `vieneu` v3 Turbo kết hợp mẫu `mentor-khanh-ref-01.wav`.
2. **Cloud AI Voice Cloning (ElevenLabs / OpenRouter / Custom Engine):**
   - Đăng ký Instant Voice Clone với mẫu chất lượng cao.
3. **Bộ lọc hậu kỳ Mentor Podcast Filter:**
   - EQ đặc trưng: Nâng dải trầm ấm (135Hz +2.2dB), làm rõ dải trung thoại (2.5kHz +1.0dB), Loudnorm -16 LUFS.
