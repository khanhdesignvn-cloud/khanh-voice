# Mentor Khánh AI - Voice Training Log

## 🎯 Định vị Persona: "Khánh Podcast v.01"
* **Tên chính thức:** Khánh Podcast v.01
* **Phong cách:** Giọng mentor/podcast thương hiệu — trong trẻo, ấm mượt, chuyên nghiệp.
* **Ứng dụng:** Đọc voice cho video podcast thương hiệu Nguyễn Quốc Khánh.

---

## ✅ QUYẾT ĐỊNH CHỐT (2026-08-16)

**Giọng chính thức:** **Khánh Podcast v.01** — kiểu **Neumann U87 Condenser**.

| Hạng mục | Giá trị |
| :--- | :--- |
| Reference | `mentor-khanh-ref-02.wav` (75s) |
| Engine | VieNeu v3 Turbo |
| Mastering | Neumann U87 (presence 3.2kHz, air 12kHz, -16 LUFS) |
| File chuẩn | `output/final/khanh-podcast-v01.mp3` |
| File clone thô | `output/final/khanh-podcast-v01-raw.wav` |
| Script tái tạo | `scripts/master_khanh_podcast.py` |

---

## 🧬 Lịch sử huấn luyện

### Vòng 1 (baseline):
- Mẫu ref-01 (36s) → 4 demo (01 raw, 02 warm, 03 rõ, 04 sâu lắng).
- Chọn bản 01 (clone mộc) làm nền.

### Vòng 2 (bản thu mới):
- Mẫu ref-02 (75s, chuyên nghiệp hơn) → 4 biến thể phòng thu v2.
- **CHỐT bản 02-v2-neumann-u87** (Neumann U87 condenser).

### Vòng 3 (chính thức):
- Đặt tên **Khánh Podcast v.01**, lưu file chuẩn + script mastering.
