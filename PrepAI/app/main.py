from fastapi import FastAPI
from .routers import users, auth

app = FastAPI()

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])


@app.get("/")
def read_root():
    return {"status": "ok"}