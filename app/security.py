"""Admin cookie signing and customer session/key token helpers."""

import base64
import hmac
import secrets
import time
from hashlib import sha256

from fastapi import Cookie, Header, HTTPException

from . import config, db


def _sign(payload: str) -> str:
    mac = hmac.new(config.SECRET_KEY.encode(), payload.encode(), sha256).hexdigest()
    return mac


def issue_admin_cookie() -> str:
    expires_at = int(time.time()) + config.ADMIN_SESSION_HOURS * 3600
    payload = f"admin:{expires_at}"
    signature = _sign(payload)
    token = f"{payload}:{signature}"
    return base64.urlsafe_b64encode(token.encode()).decode()


def verify_admin_cookie(cookie_value: str) -> bool:
    try:
        decoded = base64.urlsafe_b64decode(cookie_value.encode()).decode()
        payload, signature = decoded.rsplit(":", 1)
        _, expires_at = payload.split(":", 1)
    except (ValueError, TypeError):
        return False

    expected = _sign(payload)
    if not hmac.compare_digest(expected, signature):
        return False
    return int(expires_at) > int(time.time())


def require_admin(khv_admin: str | None = Cookie(default=None)) -> None:
    if not config.ADMIN_PASSWORD:
        raise HTTPException(status_code=503, detail="Chưa cấu hình ADMIN_PASSWORD trên server")
    if not khv_admin or not verify_admin_cookie(khv_admin):
        raise HTTPException(status_code=401, detail="Chưa đăng nhập quản trị")


def new_access_token() -> str:
    return secrets.token_urlsafe(24)


def new_session_token() -> str:
    return secrets.token_urlsafe(32)


def require_key_session(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Thiếu phiên đăng nhập, vui lòng nhập key")

    token = authorization.removeprefix("Bearer ").strip()
    session = db.get_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="Phiên không hợp lệ, vui lòng nhập lại key")

    key = db.get_key(session["key_id"])
    if not key or key["status"] not in ("active", "unused"):
        raise HTTPException(status_code=403, detail="Key đã bị thu hồi hoặc không còn hiệu lực")

    if key["status"] == "active" and key["expires_at"]:
        if db.parse_iso(key["expires_at"]).timestamp() < time.time():
            db.expire_key(key["id"])
            raise HTTPException(status_code=403, detail="Key đã hết hạn")

    return key
