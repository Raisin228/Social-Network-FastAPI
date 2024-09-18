from pathlib import Path
from typing import Dict

from config import settings
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from jinja2 import Environment, FileSystemLoader
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
    template = get_html_template(body, temp_name)
    message = MessageSchema(subject=sub, recipients=[email], body=template, subtype=MessageType.html)
    fm = FastMail(conf)
    await fm.send_message(message)
    return JSONResponse(status_code=200, content={"message": "email has been sent"})


def get_html_template(data: dict, template_name: str) -> str:
    """Сгенерировать html шаблон для отправки на почту"""
    file_loader = FileSystemLoader(Path(__file__).parent / "templates")
    env = Environment(loader=file_loader)

    template = env.get_template(template_name)
    return template.render(data)
