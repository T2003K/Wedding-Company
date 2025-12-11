# Organization Management Service

## Tech stack
- FastAPI (Python)
- Motor (async MongoDB driver)
- JWT via PyJWT
- bcrypt (passlib)

## Setup
1. copy .env.example -> .env and fill
2. `pip install -r requirements.txt`
3. `uvicorn app.main:app --reload`
4. DB: MongoDB running at MONGO_URI

## Endpoints
- POST /org/create
- GET /org/get?organization_name=...
- PUT /org/update
- DELETE /org/delete (requires bearer token)
- POST /admin/login

## Notes
See design and tradeoffs in the README body.
