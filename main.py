import uvicorn
import redis.asyncio as redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from src.routes import users, auth, profile
from src.conf.config import settings


origins = ["*"]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(profile.router, prefix='/api')

async def initialize_limiter():
    r = await redis.Redis(
        host=settings.redis_host, 
        port=settings.redis_port, 
        db=0, 
        encoding="utf-8", 
        decode_responses=True
    )
    await FastAPILimiter.init(r)

@app.on_event("startup")
async def startup_event():
    await initialize_limiter()

@app.on_event("shutdown")
async def shutdown_event():
    await FastAPILimiter.redis.close()

@app.get("/")
def read_root():
    """
    Root endpoint.

    :return: Message indicating the root of the API.
    :rtype: dict
    """
    return {"message": "USERS BOOK"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
