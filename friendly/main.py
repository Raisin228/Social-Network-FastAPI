import os
import sys
from contextlib import asynccontextmanager

import uvicorn
from admin import setup_admin
from application.auth.router import router as auth_router
from application.friends.router import router as friends_router
from application.notifications.router import router as notify_system_router
from application.profile.router import router as profile_router
from config import settings
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse
from logger_config import filter_traceback, log
from object_storage_service.s3 import YOSService
from redis_service.__init__ import RedisService
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles

sys.path.insert(1, os.path.join(sys.path[0], ".."))


@asynccontextmanager
async def lifespan(_application: FastAPI):
    """Код исполняемый до/после запуска приложения"""
    log.debug("[Lifespan] Connecting to external services/db/storage")
    await RedisService.connect_to()
    await YOSService.get_client()
    yield
    log.debug("[Lifespan] Disconnecting from external services/db/storage")
    await RedisService.disconnect()


app = FastAPI(
    contact={
        "name": "Bogdan Atroshenko",
        "url": "https://t.me/BogdanAtroshenko",
        "email": "bogdanatrosenko@gmail.com",
    },
    title="Friendly🫂",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="static"), name="static")

setup_admin(app)


@app.exception_handler(Exception)
async def unicorn_exception_handler(_request: Request, exc: Exception):
    """Базовый обработчик исключений"""
    log.error("".join(filter_traceback(exc)))
    return ORJSONResponse(status_code=500, content={"message": "Что-то пошло не так o_0, пожалуйста, попробуйте позже"})


app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET_KEY, max_age=3_600)

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(friends_router)
app.include_router(notify_system_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
