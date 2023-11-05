from typing import Type

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi_users import exceptions, models, schemas
from fastapi_users.manager import BaseUserManager, UserManagerDependency
from fastapi_users.router.common import ErrorCode, ErrorModel
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import user
from database import get_async_session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, user)


# слегка изменённая библиотечная функция (добавил потому что хочу обрабатывать ситуацию
# когда пользователь с таки username уже существует в бд)
def get_register_router(
        get_user_manager: UserManagerDependency[models.UP, models.ID],
        user_schema: Type[schemas.U],
        user_create_schema: Type[schemas.UC],
) -> APIRouter:
    """Generate a router with the register route."""
    router = APIRouter()

    @router.post(
        "/register",
        response_model=user_schema,
        status_code=status.HTTP_201_CREATED,
        name="register:register",
        responses={
            status.HTTP_400_BAD_REQUEST: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.REGISTER_USER_ALREADY_EXISTS: {
                                "summary": "A user with this email already exists.",
                                "value": {
                                    "detail": ErrorCode.REGISTER_USER_ALREADY_EXISTS
                                },
                            },
                            ErrorCode.REGISTER_INVALID_PASSWORD: {
                                "summary": "Password validation failed.",
                                "value": {
                                    "detail": {
                                        "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                                        "reason": "Password should be"
                                                  "at least 3 characters",
                                    }
                                },
                            },
                        }
                    }
                },
            },
        },
    )
    async def register(
            request: Request,
            user_create: user_create_schema,  # type: ignore
            user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
    ):

        try:
            created_user = await user_manager.create(
                user_create, safe=True, request=request
            )
        except exceptions.UserAlreadyExists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
            )
        except exceptions.InvalidPasswordException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                    "reason": e.reason,
                },
            )
        # добавил обработку ошибки internal server error в случае если username уже есть в бд
        except:
            raise HTTPException(status_code=400, detail='REGISTER_USER_ALREADY_EXISTS')

        return schemas.model_validate(user_schema, created_user)

    return router
