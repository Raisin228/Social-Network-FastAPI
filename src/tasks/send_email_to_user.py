import smtplib
from email.message import EmailMessage

from fastapi import HTTPException

from auth.models import user
from config import MAIL_HOST, MAIL_PORT, MAIL_USER, MAIL_PASSWORD

SMTP_HOST = MAIL_HOST
SMTP_PORT = MAIL_PORT
SMTP_USER = MAIL_USER
SMTP_PASSWORD = MAIL_PASSWORD


def get_template_email_forgot_pass(person: user, token: str):
    """Создаётся шаблон почтового сообщения (забыл пароль)"""
    email = EmailMessage()
    email['Subject'] = 'Social Network. Reset password.'
    email['From'] = SMTP_USER
    email['To'] = person.email

    email.set_content(
        '<div>'
        f'<p>Hi {person.username},<br>'
        'You recently requested to reset the password for your Social Network account.<br><br>'

        f'<b>Password reset token - {token}</b><br></p>'

        '<p>If you did not request a password reset, please ignore this email or reply to let us know.<br>'
        'This password reset link is only valid for the next 60 minutes.<br><br></p>'

        'Thanks, the Social Network team'
        '</div>',
        subtype='html'
    )
    return email


def after_registered_mail(person: user):
    """Шаблон почтового сообщения (благодарность после регистрации)"""
    email = EmailMessage()
    email['Subject'] = 'Social Network. Welcome to the team.'
    email['From'] = SMTP_USER
    email['To'] = person.email

    email.set_content(
        '<div>'
        '<img src="https://fanibani.ru/wp-content/uploads/2021/07/top3000c.jpg" alt="A tired cat eats a cake)">'
        f'Hi {person.username},<br>'
        'Thank you for registering on the Social Network. Now you are also part of our big family.🎉🎉🎉<br><br>'

        'We hope you will be satisfied with our application.<br>'
        'For all questions and suggestions, you can write to this email.<br>'
        'Regards, the Social Network team'
        '</div>',
        subtype='html'
    )
    return email


def send_mail(email: EmailMessage):
    """Подключение к почтовому серверу и отправка письма"""
    # Преобразовать EmailMessage в строку MIME
    message_data = email.as_string()

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(SMTP_USER, SMTP_PASSWORD)

    # Отправить сообщение
    server.sendmail(SMTP_USER, [email['To']], message_data)
    if email['Subject'] == 'Social Network. Reset password.':
        raise HTTPException(status_code=202, detail='Письмо отправлено на почту')

