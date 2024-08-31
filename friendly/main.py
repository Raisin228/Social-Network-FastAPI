import os
import sys
import uvicorn

from fastapi import FastAPI
from application.auth.router import router as auth_router

sys.path.insert(1, os.path.join(sys.path[0], '..'))

app = FastAPI(
    contact={'name': 'Bogdan Atroshenko', 'url': 'https://t.me/BogdanAtroshenko', 'email': 'bogdanatrosenko@gmail.com'},
    title='Friendly🫂')

app.include_router(auth_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
