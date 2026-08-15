# Mentor Khánh AI - Voice Training Log & Profiles

Tài liệu lưu trữ các thông số, mẫu giọng và đánh giá phản hồi để chất giọng **Mentor Khánh AI** thông minh và hoàn thiện dần theo thời gian.

---

## 🎯 Định vị Persona: "Mentor Khánh AI"
* **Phong cách:** Chuyên gia, chia sẻ kiến thức, trầm ấm, rõ ràng, truyền cảm hứng và tự tin.
* **Mục tiêu ứng dụng:** Đọc voice cho Podcast, video thương hiệu, video chia sẻ chuyên môn, hướng dẫn kỹ thuật.
* **Quyết định nền tảng (Baseline Selection):** Chọn **Bản Clone Mộc 01** làm gốc để phát triển chuỗi xử lý âm thanh chuẩn phòng thu cao cấp.

---

## 🧬 Dữ liệu mẫu (Training Dataset)

### Mẫu 1: `voice-references/mentor-khanh-ref-01.wav`
* **Nguồn gốc:** File ghi âm trực tiếp qua Telegram (`1JVVPMQLT_3NTNH2.aac`)
* **Thời lượng:** ~36.15 giây
* **Định dạng gốc:** AAC mono 44.1kHz -> Chuẩn hóa WAV 24kHz / Bandpass filter 60Hz-12kHz / Loudnorm -16 LUFS

---

## 🎙️ Các cấu hình Mastering Phòng Thu Đang Thử Nghiệm (Studio Master Profiles)

1. **Studio Profile A — Dynamic Shure SM7B:**
   - EQ: Boost ấm ngực 130Hz (+2.2dB), giảm đục 450Hz (-1.2dB), Presence 2.8kHz (+1.4dB), Air 10.5kHz (+1.8dB).
   - Dynamic: Compressor nhẹ (Ratio 2.5:1, Attack 15ms, Release 120ms), Loudnorm -16 LUFS.
2. **Studio Profile B — Condenser Neumann U87:**
   - EQ: Sub-warmth 110Hz (+1.8dB), Presence 3.2kHz (+2.0dB), High Air 12kHz (+2.4dB).
   - Dynamic: Compressor mềm mại (Ratio 2.2:1), độ nhạy hơi thở cao.
3. **Studio Profile C — Tube Warmth (Đèn tiền khuếch đại):**
   - EQ: Boost 140Hz (+2.8dB) + 250Hz (+1.2dB), cắt nhẹ 600Hz, tạo độ ấm dày sâu lắng.
4. **Studio Profile D — Broadcast Executive:**
   - EQ: 125Hz (+2.0dB), 2.4kHz (+2.2dB), 8kHz (+1.6dB), kiểm soát động lực dứt khoát.
