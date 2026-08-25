"""PayOS payment integration (official `payos` SDK — do not hand-roll signatures)."""

from functools import lru_cache

from fastapi import HTTPException

from . import config

try:
    from payos import AsyncPayOS
    from payos.types.v2 import CreatePaymentLinkRequest
except ImportError:  # pragma: no cover - surfaced as a clear runtime error instead
    AsyncPayOS = None
    CreatePaymentLinkRequest = None


@lru_cache
def get_client():
    if AsyncPayOS is None:
        raise HTTPException(status_code=503, detail="Thiếu thư viện payos, chạy: pip install payos")
    if not config.PAYOS_CONFIGURED:
        raise HTTPException(
            status_code=503,
            detail="Chưa cấu hình PAYOS_CLIENT_ID / PAYOS_API_KEY / PAYOS_CHECKSUM_KEY",
        )
    return AsyncPayOS(
        client_id=config.PAYOS_CLIENT_ID,
        api_key=config.PAYOS_API_KEY,
        checksum_key=config.PAYOS_CHECKSUM_KEY,
    )


async def create_checkout(order_code: int, amount: int, package_name: str, buyer_email: str | None):
    client = get_client()
    description = f"KhanhVoice {order_code}"[:25]
    request = CreatePaymentLinkRequest(
        order_code=order_code,
        amount=amount,
        description=description,
        items=[{"name": package_name, "quantity": 1, "price": amount}],
        buyer_email=buyer_email or None,
        return_url=f"{config.PUBLIC_BASE_URL}/thanks?order={order_code}",
        cancel_url=f"{config.PUBLIC_BASE_URL}/cancel?order={order_code}",
    )
    response = await client.payment_requests.create(request)
    return response


async def verify_webhook(payload):
    client = get_client()
    return await client.webhooks.verify(payload)


async def confirm_webhook(webhook_url: str):
    client = get_client()
    return await client.webhooks.confirm(webhook_url)
