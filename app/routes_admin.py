"""Admin dashboard API: login, packages, orders, keys, webhook registration."""

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field

from . import config, db, payments, security

router = APIRouter(prefix="/api/admin")


class LoginRequest(BaseModel):
    password: str


@router.post("/login")
def login(req: LoginRequest, response: Response):
    if not config.ADMIN_PASSWORD:
        raise HTTPException(status_code=503, detail="Chưa cấu hình ADMIN_PASSWORD trên server")
    if req.password != config.ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Sai mật khẩu")

    cookie = security.issue_admin_cookie()
    response.set_cookie(
        "khv_admin",
        cookie,
        httponly=True,
        samesite="lax",
        secure=config.PUBLIC_BASE_URL.startswith("https://"),
        max_age=config.ADMIN_SESSION_HOURS * 3600,
    )
    return {"ok": True}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("khv_admin")
    return {"ok": True}


@router.get("/packages", dependencies=[Depends(security.require_admin)])
def admin_list_packages():
    return [dict(r) for r in db.list_packages()]


class NewPackage(BaseModel):
    name: str
    duration_days: int = Field(..., gt=0)
    price_vnd: int = Field(..., gt=0)


@router.post("/packages", dependencies=[Depends(security.require_admin)])
def admin_create_package(req: NewPackage):
    package_id = db.create_package(req.name, req.duration_days, req.price_vnd)
    return {"id": package_id}


class UpdatePackagePrice(BaseModel):
    price_vnd: int = Field(..., gt=0)


@router.patch("/packages/{package_id}/price", dependencies=[Depends(security.require_admin)])
def admin_update_price(package_id: int, req: UpdatePackagePrice):
    db.update_package_price(package_id, req.price_vnd)
    return {"ok": True}


@router.patch("/packages/{package_id}/active", dependencies=[Depends(security.require_admin)])
def admin_toggle_active(package_id: int, active: bool):
    db.set_package_active(package_id, active)
    return {"ok": True}


@router.get("/orders", dependencies=[Depends(security.require_admin)])
def admin_list_orders():
    return [dict(r) for r in db.list_orders()]


@router.get("/keys", dependencies=[Depends(security.require_admin)])
def admin_list_keys(search: str | None = None):
    return [dict(r) for r in db.list_keys(search=search)]


class IssueKey(BaseModel):
    package_id: int
    note: str | None = None


@router.post("/keys/issue", dependencies=[Depends(security.require_admin)])
def admin_issue_key(req: IssueKey):
    package = db.get_package(req.package_id)
    if not package:
        raise HTTPException(status_code=400, detail="Gói không hợp lệ")
    key = db.create_key(package["id"], package["duration_days"], order_code=None, note=req.note)
    return dict(key)


@router.post("/keys/{key_id}/revoke", dependencies=[Depends(security.require_admin)])
def admin_revoke_key(key_id: int):
    db.revoke_key(key_id)
    return {"ok": True}


@router.post("/webhook/confirm", dependencies=[Depends(security.require_admin)])
async def admin_confirm_webhook():
    webhook_url = f"{config.PUBLIC_BASE_URL}/api/payos/webhook"
    try:
        await payments.confirm_webhook(webhook_url)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Đăng ký webhook thất bại: {exc}") from exc
    return {"ok": True, "webhook_url": webhook_url}


@router.get("/status", dependencies=[Depends(security.require_admin)])
def admin_status():
    return {
        "payos_configured": config.PAYOS_CONFIGURED,
        "public_base_url": config.PUBLIC_BASE_URL,
    }
