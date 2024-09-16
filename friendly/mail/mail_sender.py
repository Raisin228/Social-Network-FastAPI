from pathlib import Path
from typing import Dict

from config import settings
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr
from starlette.responses import JSONResponse

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_USERNAME,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME="Friendly-Mail service",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_mail(email: EmailStr, body: Dict, sub: str, temp_name: str) -> JSONResponse:
    """Отправить письмо на почту"""
    body["support_email"] = settings.MAIL_USERNAME
    message = MessageSchema(subject=sub, recipients=[email], template_body=body, subtype=MessageType.html)
    fm = FastMail(conf)
    await fm.send_message(message, template_name=temp_name)
    return JSONResponse(status_code=200, content={"message": "email has been sent"})
