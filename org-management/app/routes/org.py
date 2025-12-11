# app/routes/org.py
from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas import OrgCreateRequest, OrgGetRequest, OrgUpdateRequest, OrgDeleteRequest, OrgMetadataResponse
from app.models import org_exists, create_organization_metadata, create_admin, get_org_by_name
from app.db import db, organizations_coll, admins_coll
from app.utils import collection_name_for_org, copy_collection_data, sanitize_org_name
from bson.objectid import ObjectId
from app.auth import verify_token

router = APIRouter(prefix="/org", tags=["organization"])

@router.post("/create", response_model=OrgMetadataResponse)
async def create_org(payload: OrgCreateRequest):
    org_name = payload.organization_name.strip()
    if await org_exists(org_name):
        raise HTTPException(status_code=400, detail="Organization already exists")

    collection_name = collection_name_for_org(org_name)
    # create dynamic collection reference
    org_collection = db[collection_name]
    # optional: initialize collection with an index or sample doc
    await org_collection.insert_one({"_meta": "initialized"})

    # create admin
    admin_id = await create_admin(payload.email, payload.password, organization_name=org_name)

    # create metadata
    metadata_id = await create_organization_metadata(org_name, collection_name, admin_id)

    return {
        "organization_name": org_name,
        "collection_name": collection_name,
        "admin_user_id": str(admin_id)
    }

@router.get("/get")
async def get_org(organization_name: str):
    org = await get_org_by_name(organization_name)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    org["admin_user_id"] = str(org.get("admin_user_id"))
    return org

@router.put("/update")
async def update_org(payload: OrgUpdateRequest):
    old_name = payload.old_organization_name.strip()
    org = await get_org_by_name(old_name)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    update_fields = {}
    if payload.new_organization_name:
        new_name = payload.new_organization_name.strip()
        # ensure not colliding with existing org
        if new_name != old_name and await org_exists(new_name):
            raise HTTPException(status_code=400, detail="New organization name already exists")

        # create new collection and copy data
        old_coll_name = org["collection_name"]
        new_coll_name = collection_name_for_org(new_name)

        old_coll = db[old_coll_name]
        new_coll = db[new_coll_name]
        await new_coll.insert_one({"_meta": "initialized"})  # ensure exists
        await copy_collection_data(old_coll, new_coll)

        update_fields["organization_name"] = new_name
        update_fields["collection_name"] = new_coll_name

    # update admin credentials changes if provided
    if payload.email or payload.password:
        admin = await admins_coll.find_one({"_id": org["admin_user_id"]}) if "admin_user_id" in org else None
        if admin:
            update_admin = {}
            if payload.email:
                update_admin["email"] = payload.email
            if payload.password:
                from passlib.hash import bcrypt
                update_admin["password"] = bcrypt.hash(payload.password)
            if update_admin:
                await admins_coll.update_one({"_id": admin["_id"]}, {"$set": update_admin})

    # persist metadata updates
    if update_fields:
        await organizations_coll.update_one({"_id": org["_id"]}, {"$set": update_fields})

    return {"status": "success", "updated": update_fields}

@router.delete("/delete")
async def delete_org(payload: OrgDeleteRequest, token_payload=Depends(verify_token)):
    # Only allow if token belongs to admin of this org.
    org_name = payload.organization_name.strip()
    org = await get_org_by_name(org_name)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    # token_payload expected to contain admin_id and organization_name
    token_org = token_payload.get("organization_name")
    admin_id = token_payload.get("admin_id")
    if token_org != org_name:
        raise HTTPException(status_code=403, detail="Forbidden: token admin not authorized for this org")

    # remove dynamic collection
    coll_name = org["collection_name"]
    await db.drop_collection(coll_name)

    # remove admin and organization metadata
    await admins_coll.delete_one({"_id": org["admin_user_id"]})
    await organizations_coll.delete_one({"_id": org["_id"]})

    return {"status": "deleted", "organization_name": org_name}
