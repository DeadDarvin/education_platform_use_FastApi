from datetime import timedelta
from typing import Optional

from fastapi import Depends
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

import settings
from .models import ShowUser
from .models import Token
from db.dals import UserDAL
from db.models import User
from db.session import get_db
from hashing import Hasher
from security import create_access_token


#########################
# BLOCK WITH API ROUTES #
#########################


async def _get_user_by_email_for_auth(email: str, db: AsyncSession) -> Optional[User]:
    """Открывает сессию с БД. Передает email для поиска юзера."""
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            return await user_dal.get_user_by_email(email=email)


async def authenticate_user(
    email: str, password: str, db: AsyncSession
) -> Optional[User]:
    """Проверка на наличие юзера и на правильность пароля."""
    user = await _get_user_by_email_for_auth(email=email, db=db)
    if user is None:
        return

    if not Hasher.verify_password(password, user.hashed_password):
        return

    return user


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")


async def get_current_user_from_token(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> Optional[ShowUser]:
    """Получение юзера из токена"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await _get_user_by_email_for_auth(email=email, db=db)
    if user is None:
        raise credentials_exception

    return ShowUser(
        user_id=user.user_id,
        name=user.name,
        surname=user.surname,
        email=user.email,
        is_active=user.is_active,
    )


#########################
# ROUTERS #
#########################

login_router = APIRouter()


@login_router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """
    Отвечает за аутентификацию юзера.
    Возвращает jwt-токен при успехе.
    """
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "other_custom_data": [1, 2, 3, 4]},
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}


@login_router.get("/test_auth_endpoint")
async def sample_endpoint_under_jwt(
    current_user: User = Depends(get_current_user_from_token),
):
    return {"Success": True, "current_user": current_user}
