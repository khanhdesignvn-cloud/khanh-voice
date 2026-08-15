# Mentor Khánh AI - Voice Training Log & Profiles

Tài liệu lưu trữ các thông số, mẫu giọng và đánh giá phản hồi để chất giọng **Mentor Khánh AI** thông minh và hoàn thiện dần theo thời gian.

---

## 🎯 Định vị Persona: "Mentor Khánh AI"
* **Phong cách:** Chuyên gia, chia sẻ kiến thức, trầm ấm, rõ ràng, truyền cảm hứng và tự tin.
* **Mục tiêu ứng dụng:** Đọc voice cho Podcast, video thương hiệu, video chia sẻ chuyên môn, hướng dẫn kỹ thuật.

---

## 🧬 Các vòng đào tạo & Tinh chỉnh (Training Iterations)

### Vòng 1: Khởi tạo Project & Baseline
* **Trạng thái:** Sẵn sàng nạp mẫu giọng thật đầu tiên.
* **Pipeline kỹ thuật:**
  - Tiền xử lý âm thanh: Denoise, Trim silence, Bandpass 58Hz - 14kHz.
  - Clone: VieNeu v3 Turbo / Fine-tuning profile.
  - Hậu kỳ: Equalizer làm dày giọng nam (135Hz +2.4dB, 280Hz +1.2dB), Loudnorm -16 LUFS.
