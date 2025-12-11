# app/utils.py
import re
from typing import Any, List

def sanitize_org_name(name: str) -> str:
    # produce safe collection name portion: lowercase, alnum and underscores
    s = name.strip().lower()
    s = re.sub(r'\s+', '_', s)
    s = re.sub(r'[^a-z0-9_]', '', s)
    return s

def collection_name_for_org(name: str) -> str:
    clean = sanitize_org_name(name)
    return f"org_{clean}"

async def copy_collection_data(src_coll, dst_coll):
    # src_coll and dst_coll are Motor collection objects
    cursor = src_coll.find({})
    docs = []
    async for doc in cursor:
        # remove _id so Mongo creates a new one in destination
        doc.pop("_id", None)
        docs.append(doc)
    if docs:
        await dst_coll.insert_many(docs)
