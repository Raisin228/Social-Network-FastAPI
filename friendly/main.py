import os
import sys

import uvicorn
from application.auth.router import router as auth_router
from application.friends.router import router as friends_router
from application.profile.router import router as profile_router
from config import settings
from fastapi import FastAPI
from firebase.notification import send_fcm_notification
from starlette.middleware.sessions import SessionMiddleware

sys.path.insert(1, os.path.join(sys.path[0], ".."))

app = FastAPI(
    contact={
        "name": "Bogdan Atroshenko",
        "url": "https://t.me/BogdanAtroshenko",
        "email": "bogdanatrosenko@gmail.com",
    },
    title="Friendly🫂",
)

app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET_KEY)

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(friends_router)


send_fcm_notification(device_token="YOUR_DEVICE_TOKEN", title="Hello!", body="You have a new notification.")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
