from uuid import UUID

from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/friend/add/{user_id}")
async def send_friend_request(user_id: UUID):
    print(user_id)
