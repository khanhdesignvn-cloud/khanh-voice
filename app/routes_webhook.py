"""PayOS webhook: verifies the signed payload and issues a key on successful payment."""

import logging

from fastapi import APIRouter, Request

from . import db, payments

logger = logging.getLogger("khanhvoice.webhook")

router = APIRouter(prefix="/api")


@router.post("/payos/webhook")
async def payos_webhook(request: Request):
    body = await request.json()

    try:
        data = await payments.verify_webhook(body)
    except Exception as exc:
        logger.warning("Webhook signature verification failed: %s", exc)
        return {"success": False}

    order_code = getattr(data, "order_code", None)
    if order_code is None:
        # PayOS's own reachability test ping — nothing to reconcile, just acknowledge.
        return {"success": True}

    order = db.get_order(order_code)
    if not order:
        logger.warning("Webhook for unknown order_code=%s", order_code)
        return {"success": True}

    if order["status"] != "PENDING":
        return {"success": True}  # already handled — idempotent

    key = db.create_key(
        package_id=order["package_id"],
        duration_days=db.get_package(order["package_id"])["duration_days"],
        order_code=order_code,
    )
    db.mark_order_paid(order_code, key["id"])
    logger.info("Order %s paid, issued key %s", order_code, key["code"])

    return {"success": True}
