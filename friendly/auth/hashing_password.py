from logger_config import log
from passlib.context import CryptContext
from passlib.exc import UnknownHashError

context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Хэширование паролей"""
    return context.hash(password)


def verify_password(simple_password: str, hashing_password: str) -> bool:
    """Верификация пароля с хэшем"""
    try:
        return context.verify(simple_password, hashing_password)
    except UnknownHashError as ex:
        log.error(ex)
        return False
