from fastapi import FastAPI
from .routers import users

app = FastAPI()

app.include_router(users.router, prefix="/users", tags=["users"])


@app.get("/")
def read_root():
    return {"status": "ok"}