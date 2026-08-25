"""SQLite storage for packages, orders, keys and redemption sessions."""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS packages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    duration_days INTEGER NOT NULL,
    price_vnd INTEGER NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    order_code INTEGER PRIMARY KEY AUTOINCREMENT,
    package_id INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING',
    access_token TEXT NOT NULL,
    payment_link_id TEXT,
    checkout_url TEXT,
    buyer_email TEXT,
    key_id INTEGER,
    created_at TEXT NOT NULL,
    paid_at TEXT
);

CREATE TABLE IF NOT EXISTS keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    package_id INTEGER NOT NULL,
    duration_days INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'unused',
    order_code INTEGER,
    activated_at TEXT,
    expires_at TEXT,
    created_at TEXT NOT NULL,
    note TEXT
);

CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY,
    key_id INTEGER NOT NULL,
    created_at TEXT NOT NULL
);
"""

DEFAULT_PACKAGES = [
    ("Dùng thử 7 ngày", 7, 49_000),
    ("Gói tháng - 30 ngày", 30, 149_000),
    ("Gói năm - 365 ngày", 365, 999_000),
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_iso(value: str) -> datetime:
    return datetime.fromisoformat(value)


@contextmanager
def get_db():
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_db() as conn:
        conn.executescript(SCHEMA)
        existing = conn.execute("SELECT COUNT(*) FROM packages").fetchone()[0]
        if existing == 0:
            for name, duration_days, price_vnd in DEFAULT_PACKAGES:
                conn.execute(
                    "INSERT INTO packages (name, duration_days, price_vnd, active, created_at) "
                    "VALUES (?, ?, ?, 1, ?)",
                    (name, duration_days, price_vnd, now_iso()),
                )


# --- Packages ---

def list_packages(active_only: bool = False) -> list[sqlite3.Row]:
    with get_db() as conn:
        query = "SELECT * FROM packages"
        if active_only:
            query += " WHERE active = 1"
        query += " ORDER BY price_vnd ASC"
        return conn.execute(query).fetchall()


def get_package(package_id: int) -> sqlite3.Row | None:
    with get_db() as conn:
        return conn.execute("SELECT * FROM packages WHERE id = ?", (package_id,)).fetchone()


def create_package(name: str, duration_days: int, price_vnd: int) -> int:
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO packages (name, duration_days, price_vnd, active, created_at) "
            "VALUES (?, ?, ?, 1, ?)",
            (name, duration_days, price_vnd, now_iso()),
        )
        return cur.lastrowid


def set_package_active(package_id: int, active: bool) -> None:
    with get_db() as conn:
        conn.execute("UPDATE packages SET active = ? WHERE id = ?", (1 if active else 0, package_id))


def update_package_price(package_id: int, price_vnd: int) -> None:
    with get_db() as conn:
        conn.execute("UPDATE packages SET price_vnd = ? WHERE id = ?", (price_vnd, package_id))


# --- Orders ---

def create_order(package_id: int, amount: int, access_token: str, buyer_email: str | None) -> int:
    with get_db() as conn:
        cur = conn.execute(
            "INSERT INTO orders (package_id, amount, status, access_token, buyer_email, created_at) "
            "VALUES (?, ?, 'PENDING', ?, ?, ?)",
            (package_id, amount, access_token, buyer_email, now_iso()),
        )
        return cur.lastrowid


def set_order_payment_link(order_code: int, payment_link_id: str, checkout_url: str) -> None:
    with get_db() as conn:
        conn.execute(
            "UPDATE orders SET payment_link_id = ?, checkout_url = ? WHERE order_code = ?",
            (payment_link_id, checkout_url, order_code),
        )


def get_order(order_code: int) -> sqlite3.Row | None:
    with get_db() as conn:
        return conn.execute("SELECT * FROM orders WHERE order_code = ?", (order_code,)).fetchone()


def list_orders(limit: int = 100) -> list[sqlite3.Row]:
    with get_db() as conn:
        return conn.execute(
            "SELECT * FROM orders ORDER BY order_code DESC LIMIT ?", (limit,)
        ).fetchall()


def mark_order_paid(order_code: int, key_id: int) -> None:
    with get_db() as conn:
        conn.execute(
            "UPDATE orders SET status = 'PAID', key_id = ?, paid_at = ? "
            "WHERE order_code = ? AND status = 'PENDING'",
            (key_id, now_iso(), order_code),
        )


# --- Keys ---

def _generate_key_code() -> str:
    import secrets
    import string

    alphabet = string.ascii_uppercase + string.digits
    groups = ["".join(secrets.choice(alphabet) for _ in range(4)) for _ in range(3)]
    return "KHV-" + "-".join(groups)


def create_key(package_id: int, duration_days: int, order_code: int | None, note: str | None = None) -> sqlite3.Row:
    with get_db() as conn:
        for _ in range(5):
            code = _generate_key_code()
            try:
                cur = conn.execute(
                    "INSERT INTO keys (code, package_id, duration_days, status, order_code, created_at, note) "
                    "VALUES (?, ?, ?, 'unused', ?, ?, ?)",
                    (code, package_id, duration_days, order_code, now_iso(), note),
                )
                return conn.execute("SELECT * FROM keys WHERE id = ?", (cur.lastrowid,)).fetchone()
            except sqlite3.IntegrityError:
                continue
        raise RuntimeError("Không thể tạo mã key duy nhất, vui lòng thử lại")


def get_key_by_code(code: str) -> sqlite3.Row | None:
    with get_db() as conn:
        return conn.execute("SELECT * FROM keys WHERE code = ?", (code,)).fetchone()


def get_key(key_id: int) -> sqlite3.Row | None:
    with get_db() as conn:
        return conn.execute("SELECT * FROM keys WHERE id = ?", (key_id,)).fetchone()


def activate_key(key_id: int, duration_days: int) -> sqlite3.Row:
    expires_at = (datetime.now(timezone.utc) + timedelta(days=duration_days)).isoformat()
    with get_db() as conn:
        conn.execute(
            "UPDATE keys SET status = 'active', activated_at = ?, expires_at = ? WHERE id = ?",
            (now_iso(), expires_at, key_id),
        )
        return conn.execute("SELECT * FROM keys WHERE id = ?", (key_id,)).fetchone()


def expire_key(key_id: int) -> None:
    with get_db() as conn:
        conn.execute("UPDATE keys SET status = 'expired' WHERE id = ?", (key_id,))


def revoke_key(key_id: int) -> None:
    with get_db() as conn:
        conn.execute("UPDATE keys SET status = 'revoked' WHERE id = ?", (key_id,))


def list_keys(limit: int = 200, search: str | None = None) -> list[sqlite3.Row]:
    with get_db() as conn:
        if search:
            return conn.execute(
                "SELECT * FROM keys WHERE code LIKE ? ORDER BY id DESC LIMIT ?",
                (f"%{search}%", limit),
            ).fetchall()
        return conn.execute("SELECT * FROM keys ORDER BY id DESC LIMIT ?", (limit,)).fetchall()


# --- Sessions ---

def create_session(token: str, key_id: int) -> None:
    with get_db() as conn:
        conn.execute(
            "INSERT INTO sessions (token, key_id, created_at) VALUES (?, ?, ?)",
            (token, key_id, now_iso()),
        )


def get_session(token: str) -> sqlite3.Row | None:
    with get_db() as conn:
        return conn.execute("SELECT * FROM sessions WHERE token = ?", (token,)).fetchone()
