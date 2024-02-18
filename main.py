import uvicorn
from fastapi import FastAPI
from src.routes import users

app = FastAPI()

app.include_router(users.router, prefix="/api")


@app.get("/")
def read_root():
    return {"message": "USERS BOOK"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
