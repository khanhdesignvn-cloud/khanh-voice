"""Public storefront endpoints: list packages, create checkout, check order status."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field

from . import db, payments, security

router = APIRouter(prefix="/api")


@router.get("/packages")
def list_packages():
    rows = db.list_packages(active_only=True)
    return [
        {
            "id": r["id"],
            "name": r["name"],
            "duration_days": r["duration_days"],
            "price_vnd": r["price_vnd"],
        }
        for r in rows
    ]


class CheckoutRequest(BaseModel):
    package_id: int
    buyer_email: EmailStr | None = None


@router.post("/checkout")
async def create_checkout(req: CheckoutRequest):
    package = db.get_package(req.package_id)
    if not package or not package["active"]:
        raise HTTPException(status_code=400, detail="Gói không hợp lệ")

    access_token = security.new_access_token()
    order_code = db.create_order(
        package_id=package["id"],
        amount=package["price_vnd"],
        access_token=access_token,
        buyer_email=req.buyer_email,
    )

    try:
        result = await payments.create_checkout(
            order_code=order_code,
            amount=package["price_vnd"],
            package_name=package["name"],
            buyer_email=req.buyer_email,
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Không tạo được link thanh toán: {exc}") from exc

    db.set_order_payment_link(order_code, result.payment_link_id, result.checkout_url)

    return {
        "order_code": order_code,
        "access_token": access_token,
        "checkout_url": result.checkout_url,
        "qr_code": result.qr_code,
    }


@router.get("/order/{order_code}")
def get_order_status(order_code: int, t: str):
    order = db.get_order(order_code)
    if not order or order["access_token"] != t:
        raise HTTPException(status_code=404, detail="Không tìm thấy đơn hàng")

    payload = {"order_code": order_code, "status": order["status"]}
    if order["status"] == "PAID" and order["key_id"]:
        key = db.get_key(order["key_id"])
        if key:
            payload["key_code"] = key["code"]
    return payload
