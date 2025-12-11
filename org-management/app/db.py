# app/db.py
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MASTER_DB = os.getenv("MASTER_DB", "master_db")

client = AsyncIOMotorClient(MONGO_URI)
db = client[MASTER_DB]

# Collections for master metadata
organizations_coll = db["organizations"]    # stores org metadata
admins_coll = db["admins"]                  # stores admin users (hashed password, org ref)
