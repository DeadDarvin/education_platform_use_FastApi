from .models import User
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy import update, and_, select

from typing import Optional

###########################################################
# BLOCK FOR INTERACTION WITH DATABASE IN BUSINESS CONTEXT #
###########################################################


class UserDAL:
    """Data Access Layer for operating user info"""
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(
        self, name: str, surname: str, email: str
    ) -> User:
        new_user = User(
            name=name,
            surname=surname,
            email=email,
        )
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        query = select(User).where(User.user_id == user_id)
        result = await self.db_session.execute(query)
        user_row = result.fetchone()
        if user_row is not None:
            return user_row[0]

    async def delete_user_by_id(self, user_id: UUID) -> Optional[UUID]:
        query = update(User).where(and_(User.user_id == user_id, User.is_active == True)).\
            values(is_active=False).returning(User.user_id)

        result = await self.db_session.execute(query)
        deleted_user_id_row = result.fetchone()
        if deleted_user_id_row is not None:
            return deleted_user_id_row[0]

    async def update_user_by_id(self, user_id: UUID, **kwargs) -> Optional[UUID]:
        query = update(User).where(User.user_id == user_id, User.is_active == True).\
            values(kwargs).returning(User.user_id)

        result = await self.db_session.execute(query)
        updated_user_id_row = result.fetchone()
        if updated_user_id_row is not None:
            return updated_user_id_row[0]
