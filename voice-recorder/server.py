#!/usr/bin/env python3
"""Khanh Voice Recorder: thu âm trên web, lưu và chuẩn hóa audio tại Hermes."""
from __future__ import annotations

import datetime as dt
import json
import os
import re
import shutil
import subprocess
import tempfile
import unicodedata
import urllib.parse
import uuid
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = APP_DIR / 'public'
RECORDINGS_ROOT = Path(os.getenv('VOICE_RECORDINGS_DIR', '/root/projects/khanh-voice/voice-references/recordings')).resolve()
MAX_BYTES = 25 * 1024 * 1024
ALLOWED_TYPES = {
    'audio/webm': '.webm', 'audio/ogg': '.ogg', 'audio/mp4': '.m4a',
    'audio/mpeg': '.mp3', 'audio/wav': '.wav', 'audio/x-wav': '.wav'
}


def safe_slug(value: str) -> str:
    value = re.sub(r'<[^>]*>', '', str(value or ''))
    value = unicodedata.normalize('NFD', value).encode('ascii', 'ignore').decode().lower()
    value = re.sub(r'[^a-z0-9]+', '-', value).strip('-')
    return (value[:48] or 'giong-moi')


def clean_text(value: str, limit: int = 160) -> str:
    value = re.sub(r'<[^>]*>', '', str(value or ''))
    return re.sub(r'\s+', ' ', value).strip()[:limit]


def extension_for(content_type: str) -> str:
    mime = (content_type or '').split(';', 1)[0].strip().lower()
    if mime not in ALLOWED_TYPES:
        raise ValueError('Định dạng âm thanh không được hỗ trợ')
    return ALLOWED_TYPES[mime]


def make_recording_dir(root: Path, voice_name: str) -> Path:
    root = root.resolve()
    voice_dir = (root / safe_slug(voice_name)).resolve()
    if not voice_dir.is_relative_to(root):
        raise ValueError('Đường dẫn không hợp lệ')
    rec_id = dt.datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + uuid.uuid4().hex[:8]
    target = (voice_dir / rec_id).resolve()
    if not target.is_relative_to(root):
        raise ValueError('Đường dẫn không hợp lệ')
    target.mkdir(parents=True, exist_ok=False)
    return target


def atomic_json(path: Path, data: dict) -> None:
    fd, tmp_name = tempfile.mkstemp(prefix='.meta-', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.flush(); os.fsync(f.fileno())
        os.replace(tmp_name, path)
    except Exception:
        try: os.unlink(tmp_name)
        except OSError: pass
        raise


def probe_duration(path: Path) -> float:
    r = subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(path)],
                       capture_output=True, text=True, timeout=20, check=True)
    duration = float(r.stdout.strip())
    if not 1 <= duration <= 1800:
        raise ValueError('Thời lượng phải từ 1 giây đến 30 phút')
    return round(duration, 2)


def normalize_audio(source: Path, destination: Path) -> None:
    fd, tmp_name = tempfile.mkstemp(prefix='.clean-', suffix='.wav', dir=destination.parent)
    os.close(fd)
    try:
        subprocess.run([
            'ffmpeg','-y','-loglevel','error','-i',str(source),
            '-af','highpass=f=70,lowpass=f=11500,afftdn=nf=-28,loudnorm=I=-19:TP=-2:LRA=7',
            '-ar','24000','-ac','1','-c:a','pcm_s16le',tmp_name
        ], capture_output=True, timeout=120, check=True)
        if Path(tmp_name).stat().st_size < 1000:
            raise ValueError('Audio đầu ra không hợp lệ')
        os.replace(tmp_name, destination)
    finally:
        try: os.unlink(tmp_name)
        except OSError: pass


class Handler(SimpleHTTPRequestHandler):
    server_version = 'KhanhVoiceRecorder/1.0'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def end_headers(self):
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'same-origin')
        self.send_header('Permissions-Policy', 'microphone=(self)')
        self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def json_response(self, status: int, payload: dict | list):
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/health':
            return self.json_response(200, {'ok': True, 'storage': str(RECORDINGS_ROOT)})
        if parsed.path == '/api/recordings':
            items = []
            if RECORDINGS_ROOT.exists():
                for meta_path in RECORDINGS_ROOT.glob('*/*/meta.json'):
                    try: items.append(json.loads(meta_path.read_text(encoding='utf-8')))
                    except Exception: continue
            items.sort(key=lambda x: x.get('created_at',''), reverse=True)
            return self.json_response(200, items[:200])
        if parsed.path.startswith('/recordings/'):
            rel = urllib.parse.unquote(parsed.path.removeprefix('/recordings/'))
            if not re.fullmatch(r'[a-z0-9-]+/[0-9]{8}-[0-9]{6}-[a-f0-9]{8}/clean\.wav', rel):
                return self.send_error(HTTPStatus.NOT_FOUND)
            target = (RECORDINGS_ROOT / rel).resolve()
            if not target.is_relative_to(RECORDINGS_ROOT) or not target.is_file():
                return self.send_error(HTTPStatus.NOT_FOUND)
            data = target.read_bytes()
            self.send_response(200); self.send_header('Content-Type','audio/wav')
            self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data); return
        return super().do_GET()

    def do_POST(self):
        if urllib.parse.urlparse(self.path).path != '/api/recordings':
            return self.json_response(404, {'ok': False, 'error': 'Không tìm thấy endpoint'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length < 1000 or length > MAX_BYTES:
                raise ValueError('File phải lớn hơn 1 KB và không quá 25 MB')
            ext = extension_for(self.headers.get('Content-Type', ''))
            voice_name = clean_text(urllib.parse.unquote(self.headers.get('X-Voice-Name', 'Giọng mới')), 80)
            notes = clean_text(urllib.parse.unquote(self.headers.get('X-Notes', '')), 300)
            rec_dir = make_recording_dir(RECORDINGS_ROOT, voice_name)
            source = rec_dir / ('original' + ext)
            fd, tmp_name = tempfile.mkstemp(prefix='.upload-', suffix=ext, dir=rec_dir)
            try:
                remaining = length
                with os.fdopen(fd, 'wb') as f:
                    while remaining:
                        chunk = self.rfile.read(min(65536, remaining))
                        if not chunk: raise ValueError('Upload bị gián đoạn')
                        f.write(chunk); remaining -= len(chunk)
                    f.flush(); os.fsync(f.fileno())
                os.replace(tmp_name, source)
                duration = probe_duration(source)
                clean = rec_dir / 'clean.wav'
                normalize_audio(source, clean)
                rel_clean = clean.relative_to(RECORDINGS_ROOT).as_posix()
                metadata = {
                    'id': rec_dir.name, 'voice_name': voice_name, 'slug': rec_dir.parent.name,
                    'notes': notes, 'duration': duration, 'size': source.stat().st_size,
                    'created_at': dt.datetime.now(dt.timezone.utc).astimezone().isoformat(),
                    'audio_url': '/recordings/' + rel_clean, 'status': 'ready'
                }
                atomic_json(rec_dir / 'meta.json', metadata)
                return self.json_response(201, {'ok': True, 'recording': metadata})
            finally:
                try: os.unlink(tmp_name)
                except OSError: pass
        except (ValueError, subprocess.SubprocessError) as e:
            if 'rec_dir' in locals(): shutil.rmtree(rec_dir, ignore_errors=True)
            return self.json_response(400, {'ok': False, 'error': str(e)[:240]})
        except Exception:
            if 'rec_dir' in locals(): shutil.rmtree(rec_dir, ignore_errors=True)
            return self.json_response(500, {'ok': False, 'error': 'Không thể lưu bản thu'})


def main():
    RECORDINGS_ROOT.mkdir(parents=True, exist_ok=True)
    host = os.getenv('VOICE_RECORDER_HOST', '127.0.0.1')
    port = int(os.getenv('VOICE_RECORDER_PORT', '4010'))
    print(f'Khanh Voice Recorder listening on http://{host}:{port}', flush=True)
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == '__main__':
    main()
