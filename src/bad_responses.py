from pydantic import BaseModel


class Error400(BaseModel):
    """Для ошибок 400-499 (нужно чтобы регистр. в Responses)"""
    detail: str
