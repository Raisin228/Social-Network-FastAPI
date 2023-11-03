from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from auth.base_config import fastapi_users
from auth.models import user
from bad_responses import Error400
from database import get_async_session

current_user = fastapi_users.current_user()
# создаём новый роутер
profile_router = APIRouter(
    prefix='/profile',
    tags=['Profile']
)


@profile_router.patch('/update_name_surname',
                      responses={
                          200: {'model': Error400, 'description': 'OK'},
                          400: {'model': Error400, 'description': 'Bad request.'}})
async def update_user_information(new_name: str, new_surname: str, person: user = Depends(current_user),
                                  session: AsyncSession = Depends(get_async_session)):
    """Добавление доп.информации (имя, фамилия)"""
    if not (len(new_name) <= 50 and len(new_surname) <= 50):
        raise HTTPException(status_code=400, detail='Поля имя и фамилия не должны превышать 50 символов!')

    stmt = update(user).where(user.id == person.id).values(first_name=new_name, last_name=new_surname)
    await session.execute(stmt)
    await session.commit()
    return {'detail': 'Данные сохранены.'}
