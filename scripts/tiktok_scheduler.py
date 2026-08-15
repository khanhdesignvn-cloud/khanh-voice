#!/usr/bin/env python3
"""
TikTok Auto Scheduler Module - Khanh TTS & Thuyet TTS
Hỗ trợ 2 phương thức:
1. TikTok Content Posting API (Official OAuth2)
2. Session Cookie / Webhook Scheduler
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

CONFIG_DIR = Path.home() / ".hermes" / "tiktok"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
CREDENTIALS_FILE = CONFIG_DIR / "credentials.json"
SCHEDULE_QUEUE_FILE = CONFIG_DIR / "schedule_queue.json"


def init_queue():
    if not SCHEDULE_QUEUE_FILE.exists():
        SCHEDULE_QUEUE_FILE.write_text("[]", encoding="utf-8")


def add_to_schedule(video_path: str, cover_path: str, title: str, caption: str, hashtags: list, schedule_time_iso: str):
    init_queue()
    queue = json.loads(SCHEDULE_QUEUE_FILE.read_text(encoding="utf-8"))
    
    item = {
        "id": f"tiktok_task_{int(datetime.now().timestamp())}",
        "video_path": str(video_path),
        "cover_path": str(cover_path),
        "title": title,
        "caption": caption,
        "hashtags": hashtags,
        "schedule_time": schedule_time_iso,
        "status": "pending_auth" if not CREDENTIALS_FILE.exists() else "scheduled",
        "created_at": datetime.now().isoformat()
    }
    
    queue.append(item)
    SCHEDULE_QUEUE_FILE.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
    return item


if __name__ == "__main__":
    # Demo tạo lịch cho video 12
    video_12_demo = add_to_schedule(
        video_path="/root/projects/khanh-tts/videos/12-nhan-dien-thuong-hieu-thieu-quy-chuan.mp4",
        cover_path="/root/projects/khanh-tts/videos/12-nhan-dien-thuong-hieu-thieu-quy-chuan.png",
        title="Nhận diện thương hiệu thiếu quy chuẩn | Mentor Nguyễn Quốc Khánh",
        caption="Bộ nhận diện của bạn có đang bị sử dụng sai cách? Xem ngay giải pháp quy chuẩn hóa thương hiệu!",
        hashtags=["#nguyenquockhanh", "#khanhtts", "#nhandienthuonghieu", "#brandguidelines", "#marketing", "#kinhdoanh", "#xuhuong"],
        schedule_time_iso="2026-08-16T19:30:00+07:00"
    )
    print(json.dumps(video_12_demo, ensure_ascii=False, indent=2))
