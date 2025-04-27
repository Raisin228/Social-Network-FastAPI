import secrets
import uuid

from application.auth.constants import ACCESS_TOKEN_TYPE, RESET_PASSWORD_TOKEN_TYPE
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
    GetUser,
    RedirectUserAuth,
    ResetPasswordByEmail,
    TokensInfo,
    UserRegister,
    UserUpdatePassword,
)
from application.auth.utils import generate_tokens_pair
from application.core.responses import (
    BAD_REQUEST,
    CONFLICT,
    FORBIDDEN,
    NOT_FOUND,
    UNAUTHORIZED,
)
from auth.auth import create_jwt_token
from auth.google_oauth import get_data_from_authorize_token, oauth
from auth.hashing_password import hash_password
from auth.yandex_oauth import change_code_to_access_token, change_token_to_user_info
from config import settings
from database import Transaction, get_async_session
from fastapi import APIRouter, Depends, HTTPException, Request, status
from mail.mail_sender import send_mail
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse, RedirectResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/registration", summary="Register new user", responses=CONFLICT, response_model=UserRegister
)
async def register_user(user_data: UserRegistrationData):
    """
    Registers a new user in the system.

    ### Request body:
    - **email**: Email address of the user.
    - **password**: Password for the account (will be hashed before storing).

    ### Behavior:
    - Checks if a user with the same email already exists.
    - If not, creates a new user with a generated UUID and default nickname (`id_<uuid>`).
    - Sends a welcome email to the provided address.

    ### Responses:
    - **200**: Account successfully created (returns basic user info).
    - **409**: Conflict — user with the same email already exists.
    - **422**: Validation Error - error in validation of input data.
    """

    email = {"email": user_data.email}

    async with Transaction() as session:
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

    async with Transaction() as session:
        result = await UserDao.add(session, user_data)
        d_res = result.to_dict()
        response = UserRegister(msg="Account successfully created", detail=GetUser(**d_res))

    send_mail.delay(
        user_data["email"],
        {"user_email": d_res["email"], "user_nick": d_res["nickname"]},
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
async def login_user(
    user_data: UserRegistrationData, session: AsyncSession = Depends(get_async_session)
):
    """
    Authenticate the user with email and password.

    ### Request body:
    - **user_data** (UserRegistrationData): The user's login credentials (email/password).

    ### Behavior:
    - Checks the presence of such login in the system and checks passwords
    - In case of a mismatch, a 401 error is thrown.

    ### Responses:
    - **200**: authorization is successful (returns access and refresh tokens).
    - **401**: Unauthorized — incorrect login information or there is no such user.
    - **422**: Validation Error - error in validation of input data.
    """
    user = await UserDao.authenticate_user(**user_data.model_dump(), session=session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    return generate_tokens_pair({"user_id": str(user["id"])})


@router.post(
    "/refresh_access_token",
    summary="Issue a new access token using refresh",
    response_model=AccessTokenInfo,
    responses=UNAUTHORIZED | FORBIDDEN,
)
async def refresh_jwt(user: GetUser = Depends(get_current_user_refresh_token)):
    """
    Get a new access token using refresh token.

    ### Request body:
    - It's enough to call this method by passing the refresh token as an authorization.
    `Authorization: Bearer <your_refresh_token>`

    ### Behavior:
    - Checks the validity of the refresh token.
    - Creating a new access token.

    ### Responses:
    - **200**: Successful — new access token has been received.
    - **401**: Unauthorized — access tokens are incorrect or too old.
    - **403**: Forbidden — insufficient access rights. Authorization failed.
    - **422**: Validation Error - error in validation of input data.
    """
    data_for_payload = {"user_id": str(user.id)}
    access_token = create_jwt_token(data_for_payload, ACCESS_TOKEN_TYPE)
    return AccessTokenInfo(access_token=access_token, token_type="Bearer")


@router.post(
    "/change_password",
    summary="Change the account password using the current one",
    response_model=UserUpdatePassword,
    responses=FORBIDDEN | UNAUTHORIZED | BAD_REQUEST,
)
async def change_account_password(
    inform: ModifyPassword,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user_access_token),
):
    """
    Change the password from the user account.

    ### Request body:
    - **inform (ModifyPassword)**: the old password and the new one confirmed twice.

    ### Behavior:
    - The user must be logged in and the old password must be valid.
    - If successful, the password data is changed.
    - In case of failure, a 400 error is thrown.

    ### Responses:
    - **200**: Successful — new password has been successfully set.
    - **400**: Bad Request — the entered old password does not match the valid one.
    - **401**: Unauthorized — access tokens are incorrect or too old.
    - **403**: Forbidden — insufficient access rights. Authorization failed.
    - **422**: Validation Error - error in validation of input data.
    """

    """Сменить пароль от аккаунта. При условии что пользователь помнит текущий пароль"""
    is_valid = await UserDao.authenticate_user(user.email, inform.current_password, session)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="the password from the current_password field does"
            " not match your account password",
        )

    await UserDao.update_row(
        session, {"password": hash_password(inform.new_password)}, {"id": user.id}
    )
    return UserUpdatePassword(**{"id": user.id, "email": user.email})


@router.post(
    "/single_link_to_password_reset",
    summary="Change your password via email",
    response_model=ResetPasswordByEmail,
    responses=NOT_FOUND,
)
async def request_token_to_reset_password(
    reset_mail: Email, request: Request, session: AsyncSession = Depends(get_async_session)
):
    """
    Forgot your password? Get a short-lived link (to the mail) with a token [to reset the password]

    ### Request body:
    - **reset_mail (Email)**: mail for receiving mailing lists.

    ### Behavior:
    - We check that the user with this login is in the system.
    - Creating and sending a password reset token to the mail.

    ### Responses:
    - **200**: Successful — new password has been successfully set.
    - **404**: Not Found — there is no user with this login.
    - **422**: Validation Error - error in validation of input data.
    """
    user = await UserDao.find_by_filter(session, {"email": reset_mail.email})

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with '{reset_mail.email}' email address doesn't exist",
        )

    reset_token = create_jwt_token(
        {"user_id": str(user["id"])}, token_type=RESET_PASSWORD_TOKEN_TYPE
    )
    single_link = f"{settings.FRONTEND_URL}reset_password?reset_token={reset_token}"

    send_mail.delay(
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


@router.get(
    "/login/via_google",
    summary="Log in via google",
    response_model=RedirectUserAuth,
    status_code=302,
)
async def redirect_google_auth_server(request: Request):
    """
    Redirection to the Google authorization server for [login or registration] Friendly

    ### Note:
    - **redirect_uri=**http://127.0.0.1:8000/auth/callback/google
    """
    request_from_swagger = request.headers.get("referer", "")
    if request_from_swagger and request_from_swagger.endswith("/docs"):
        return JSONResponse(
            status_code=302,
            content=RedirectUserAuth(
                **{"msg": "Redirects the user to Google OAuth for authentication"}
            ).dict(),
        )

    # Генерация безопасного nonce (одноразовый криптографический ключ)
    nonce = secrets.token_urlsafe(16)
    request.session["nonce"] = nonce
    redirect_uri = request.url_for("callback")
    return await oauth.google.authorize_redirect(
        request, redirect_uri, nonce=nonce, prompt="consent"
    )


@router.get(
    "/callback/google",
    name="callback",
    response_model=TokensInfo,
    responses=BAD_REQUEST,
    include_in_schema=False,
)
async def auth(request: Request):
    """Google OAuth Callback. Замечание: не требуется вызывать напрямую"""
    user_data = await get_data_from_authorize_token(request)
    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Authorization failed or was canceled."
        )

    async with Transaction() as session:
        is_user_exist = await UserDao.find_by_filter(session, {"email": user_data.get("email")})
        if is_user_exist is None:
            temp = uuid.uuid4()
            new_user = {
                "id": temp,
                "nickname": f"id_{temp}",
                "email": user_data.get("email"),
                "first_name": user_data.get("given_name"),
                "last_name": user_data.get("family_name"),
                "password": "",
            }
            result = await UserDao.add(session, new_user)

            return generate_tokens_pair({"user_id": str(result.id)})
    return generate_tokens_pair({"user_id": str(is_user_exist["id"])})


@router.get(
    "/login/via_yandex",
    summary="Login via Yandex ID",
    response_model=RedirectUserAuth,
    status_code=302,
)
async def redirect_yandex_auth_server(request: Request):
    """
    Redirection to the Yandex ID authorization server for [login | registration] Friendly

    ### Note:
    - **redirect_uri=**http://127.0.0.1:8000/auth/callback/yandex
    """
    request_from_swagger = request.headers.get("referer", "")
    if request_from_swagger and request_from_swagger.endswith("/docs"):
        return JSONResponse(
            status_code=302,
            content=RedirectUserAuth(
                **{"msg": "Redirects the user to Yandex OAuth for authentication"}
            ).dict(),
        )

    redirect_uri = request.url_for("callback_yandex")
    yandex_auth_url = (
        f"https://oauth.yandex.ru/authorize?response_type=code&client_id={settings.YDEX_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&force_confirm=true"
    )
    return RedirectResponse(yandex_auth_url)


@router.get(
    "/callback/yandex",
    name="callback_yandex",
    include_in_schema=False,
    response_model=TokensInfo,
    responses=BAD_REQUEST,
)
async def ydex_auth(request: Request):
    """Yandex OAuth Callback. !Не требуется вызывать напрямую!"""
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="The confirmation code is missing."
        )
    access_token = await change_code_to_access_token(code)
    user_data = await change_token_to_user_info(access_token)
    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Authorization failed or was canceled."
        )

    async with Transaction() as session:
        is_user_exist = await UserDao.find_by_filter(
            session, {"email": user_data.get("default_email")}
        )
        if is_user_exist is None:
            temp = uuid.uuid4()
            new_user = {
                "id": temp,
                "nickname": f"id_{temp}",
                "email": user_data.get("default_email"),
                "first_name": user_data.get("first_name"),
                "last_name": user_data.get("last_name"),
                "password": "",
            }
            result = await UserDao.add(session, new_user)

            return generate_tokens_pair({"user_id": str(result.id)})
    return generate_tokens_pair({"user_id": str(is_user_exist["id"])})


@router.patch(
    "/replace_existent_password",
    summary="Reset the password using the link from the email",
    response_model=UserUpdatePassword,
    responses=UNAUTHORIZED | FORBIDDEN,
)
async def change_password_by_provided_token(
    data: NewPassword,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(get_current_user_reset_password_token),
):
    """
    Save the new password using the reset password link from the email.

    ### Request body:
    - **data (NewPassword)**: new pass confirmed twice.

    ### Behavior:
    - The user is being verified.
    - Saving a new password.

    ### Responses:
    - **200**: Successful — new password has been successfully set.
    - **401**: Unauthorized — access tokens are incorrect or too old.
    - **403**: Forbidden — insufficient access rights. Authorization failed.
    - **422**: Validation Error - error in validation of input data.
    """
    updated_profile = await UserDao.update_row(
        session, {"password": hash_password(data.new_password)}, {"id": str(user.id)}
    )
    return UserUpdatePassword(**{"id": str(updated_profile[0][0]), "email": updated_profile[0][6]})
