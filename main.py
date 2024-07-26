from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from pydantic import BaseModel

app = FastAPI()


class User(BaseModel):
    id: int
    name: str
    last_name: str | None = None


users_db = [{'id': 1, 'name': 'Alice', 'last_name': 'Brown'},
            {'id': 2, 'name': 'Alex'}]


@app.get('/users/{user_id}', response_model=User)
def main_page(user_id: int):
    data = list(filter(lambda user: user['id'] == user_id, users_db))
    if data:
        return data[0]
    raise HTTPException(status_code=404)
