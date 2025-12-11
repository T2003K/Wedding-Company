# app/main.py
from fastapi import FastAPI
from app.routes import org, admin
import uvicorn

app = FastAPI(title="Organization Management Service")

app.include_router(org.router)
app.include_router(admin.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
