# app/models.py
from app.db import organizations_coll, admins_coll, db
from passlib.hash import bcrypt
from bson.objectid import ObjectId

async def org_exists(org_name: str) -> bool:
    return await organizations_coll.find_one({"organization_name": org_name}) is not None

async def create_organization_metadata(org_name: str, collection_name: str, admin_id: ObjectId):
    doc = {
        "organization_name": org_name,
        "collection_name": collection_name,
        "admin_user_id": admin_id,
        "created_at": None
    }
    res = await organizations_coll.insert_one(doc)
    return res.inserted_id

async def create_admin(email: str, password: str, organization_name: str):
    hashed = bcrypt.hash(password)
    doc = {
        "email": email,
        "password": hashed,
        "organization_name": organization_name
    }
    res = await admins_coll.insert_one(doc)
    return res.inserted_id

async def get_admin_by_email(email: str):
    return await admins_coll.find_one({"email": email})

async def get_org_by_name(org_name: str):
    return await organizations_coll.find_one({"organization_name": org_name})
