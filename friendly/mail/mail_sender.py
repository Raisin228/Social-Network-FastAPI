from typing import Dict

from config import settings
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from starlette.responses import JSONResponse

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_USERNAME,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME="Friendly",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    TEMPLATE_FOLDER="templates",
)


async def send_welcome_mail(email: str, body: Dict) -> JSONResponse:
    message = MessageSchema(subject="Fastapi-Mail service", recipients=[email], subtype=MessageType.html)

    fm = FastMail(conf)
    await fm.send_message(message, template_name="welcome.html")
    return JSONResponse(status_code=200, content={"message": "email has been sent"})
