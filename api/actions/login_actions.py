from typing import Optional

from fastapi import Depends
from fastapi import status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

import settings
from api.models import ShowUser
from db.dals import UserDAL
from db.models import User
from db.session import get_db
from hashing import Hasher


async def _get_user_by_email_for_auth(
    email: str, session: AsyncSession
) -> Optional[User]:
    """Открывает сессию с БД. Передает email для поиска юзера."""
    async with session.begin():
        user_dal = UserDAL(session)
        return await user_dal.get_user_by_email(email=email)


async def authenticate_user(
    email: str, password: str, session: AsyncSession
) -> Optional[User]:
    """Проверка на наличие юзера и на правильность пароля."""
    user = await _get_user_by_email_for_auth(email=email, session=session)
    if user is None:
        return

    if not Hasher.verify_password(password, user.hashed_password):
        return

    return user


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/token")


async def get_current_user_from_token(
    token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_db)
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

    user = await _get_user_by_email_for_auth(email=email, session=session)
    if user is None:
        raise credentials_exception

    return ShowUser(
        user_id=user.user_id,
        name=user.name,
        surname=user.surname,
        email=user.email,
        is_active=user.is_active,
    )
