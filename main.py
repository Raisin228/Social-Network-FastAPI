from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing_extensions import Optional

app = FastAPI(
    title='Social Network',
    version='1.0'
)

fake_db = []


class User(BaseModel):
    """Модель для валидации пользователя"""
    login: str
    password: str


class ResponseUser(BaseModel):
    """Валидация ответа при регистрации/поиску по username"""
    status: int = Field(ge=0)
    data: Optional[User] = None


@app.get('/get_userinfo/{u_login}', response_model=ResponseUser)
def get_user(u_login: str) -> dict:
    """Поиск пользователя по логину"""
    filtered_user = tuple(filter(lambda user: user.get('login') == u_login, fake_db))
    if filtered_user:
        return {'status': 200, 'data': filtered_user[0]}
    return {'status': 404}


@app.post('/register', response_model=ResponseUser)
def register_user(send_d: User) -> dict:
    """Регистрация пользователя в системе"""
    new_user = {'login': send_d.login, 'password': send_d.password}
    fake_db.append(new_user)
    return {'status': -200, 'data': new_user}

# import uvicorn
# if __name__ == '__main__':
#     uvicorn.run('main:app')
