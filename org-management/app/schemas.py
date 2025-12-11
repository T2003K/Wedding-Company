# app/schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class OrgCreateRequest(BaseModel):
    organization_name: str = Field(..., min_length=2)
    email: EmailStr
    password: str = Field(..., min_length=6)

class OrgGetRequest(BaseModel):
    organization_name: str

class OrgUpdateRequest(BaseModel):
    old_organization_name: str
    new_organization_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class OrgDeleteRequest(BaseModel):
    organization_name: str

class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str

class OrgMetadataResponse(BaseModel):
    organization_name: str
    collection_name: str
    admin_user_id: str
