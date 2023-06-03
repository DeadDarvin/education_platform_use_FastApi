import datetime
from datetime import timedelta
from typing import Optional

from jose import jwt

import settings


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Универсальная функция для создания jwt-токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)

    return encoded_jwt
