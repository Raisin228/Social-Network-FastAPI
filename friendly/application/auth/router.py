import uuid

from application.auth.constants import (
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    RESET_PASSWORD_TOKEN_TYPE,
)
from application.auth.dao import UserDao
from application.auth.dependensies import (
    get_current_user_access_token,
    get_current_user_refresh_token,
    get_current_user_reset_password_token,
)
from application.auth.models import User
from application.auth.request_body import (
    Email,
    ModifyPassword,
    NewPassword,
    UserRegistrationData,
)
from application.auth.schemas import (
    AccessTokenInfo,
    BasicUserFields,
    GetUser,
    ResetPasswordByEmail,
    TokensInfo,
    UserRegister,
    UserUpdatePassword,
)
from application.core.responses import CONFLICT, FORBIDDEN, NOT_FOUND, UNAUTHORIZED
from auth.auth import create_jwt_token
from auth.hashing_password import hash_password
from config import settings
from database import get_async_session
from fastapi import APIRouter, Depends, HTTPException, Request, status
from mail.mail_sender import send_mail
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/registration", summary="Register new user", responses=CONFLICT, response_model=UserRegister)
async def register_user(user_data: UserRegistrationData, session: AsyncSession = Depends(get_async_session)):
    """Регистрация пользователя по логину и паролю"""
    email = {"email": user_data.email}
    if await UserDao.find_by_filter(session, email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with that email already exist",
        )

    user_data = dict(user_data)
    temp = uuid.uuid4()
    user_data["id"] = temp
    user_data["nickname"] = f"id_{temp}"
    user_data["password"] = hash_password(user_data["password"])
    result = await UserDao.add_one(session, user_data)
    response = UserRegister(msg="Account successfully created", detail=GetUser(**result.to_dict()))

    # TODO
    # сделать отправку почты либо через background task либо через celery

    await send_mail(
        user_data["email"],
        {"user_email": result.email, "user_nick": result.nickname},
        "Registration was successful",
        "welcome.html",
    )
    return response


@router.post(
    "/login",
    summary="Log in to system",
    response_model=TokensInfo,
    responses=UNAUTHORIZED,
)
async def login_user(user_data: UserRegistrationData, session: AsyncSession = Depends(get_async_session)):
    """Вход в систему, получение JWT токена и запись его в cookies"""
    user = await UserDao.authenticate_user(**user_data.model_dump(), session=session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    data_for_payload = {"user_id": str(user["id"])}
    access_token = create_jwt_token(data_for_payload, ACCESS_TOKEN_TYPE)
    refresh_token = create_jwt_token(data_for_payload, REFRESH_TOKEN_TYPE)
    return TokensInfo(access_token=access_token, refresh_token=refresh_token, token_type="Bearer")


@router.post(
    "/refresh_access_token",
    response_model=AccessTokenInfo,
    responses=UNAUTHORIZED | FORBIDDEN,
)
async def refresh_jwt(user: GetUser = Depends(get_current_user_refresh_token)):
    """Получить новый токен доступа"""
    data_for_payload = {"user_id": str(user.id)}
    access_token = create_jwt_token(data_for_payload, ACCESS_TOKEN_TYPE)
    return AccessTokenInfo(access_token=access_token, token_type="Bearer")


@router.post("/change_password", response_model=UserUpdatePassword, responses=FORBIDDEN | UNAUTHORIZED)
async def change_account_password(
    inform: ModifyPassword,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user_access_token),
):
    """Сменить пароль от аккаунта. При условии что пользователь помнит текущий пароль"""
    is_valid = await UserDao.authenticate_user(user.email, inform.current_password, session)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="the password from the current_password field does not match your account password",
        )

    await UserDao.update_row(session, {"password": hash_password(inform.new_password)}, {"id": user.id})
    return UserUpdatePassword(detail=BasicUserFields(**{"id": user.id, "email": user.email}))


@router.post("/single_link_to_password_reset", response_model=ResetPasswordByEmail, responses=NOT_FOUND)
async def request_token_to_reset_password(
    reset_mail: Email, request: Request, session: AsyncSession = Depends(get_async_session)
):
    """Забыл пароль? Получить короткоживущую ссылку (на почту) с токеном [для сброса пароля]"""
    user = await UserDao.find_by_filter(session, {"email": reset_mail.email})

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User with '{reset_mail.email}' email address doesn't exist"
        )

    reset_token = create_jwt_token({"user_id": str(user["id"])}, token_type=RESET_PASSWORD_TOKEN_TYPE)
    single_link = f"{settings.FRONTEND_URL}reset_password?reset_token={reset_token}"

    # TODO
    # сделать отправку почты либо через background task либо через celery

    await send_mail(
        reset_mail.email,
        {
            "user_nick": user["nickname"],
            "user_email": reset_mail.email,
            "browser_name": request.headers.get("user-agent"),
            "action_url": single_link,
        },
        "Password reset request",
        "reset_password.html",
    )
    return ResetPasswordByEmail(**{"email": reset_mail.email})


@router.patch("/replace_existent_password", response_model=UserUpdatePassword, responses=UNAUTHORIZED | FORBIDDEN)
async def change_password_by_provided_token(
    data: NewPassword,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user_reset_password_token),
):
    """Изменить пароль пользователя через токен из ссылки"""
    updated_profile = await UserDao.update_row(
        session, {"password": hash_password(data.new_password)}, {"id": str(user.id)}
    )
    return UserUpdatePassword(**{"id": str(updated_profile[0].id), "email": updated_profile[0].email})
