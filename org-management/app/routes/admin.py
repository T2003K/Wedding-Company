# app/routes/admin.py
from fastapi import APIRouter, HTTPException
from app.schemas import AdminLoginRequest
from app.models import get_admin_by_email, get_org_by_name
from passlib.hash import bcrypt
from app.auth import create_access_token

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/login")
async def admin_login(payload: AdminLoginRequest):
    admin = await get_admin_by_email(payload.email)
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not bcrypt.verify(payload.password, admin["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # fetch org metadata
    org = await get_org_by_name(admin["organization_name"])
    if not org:
        raise HTTPException(status_code=500, detail="Organization metadata missing")

    token_payload = {
        "admin_id": str(admin["_id"]),
        "organization_name": admin["organization_name"]
    }
    token = create_access_token(token_payload)
    return {"access_token": token, "token_type": "bearer"}
