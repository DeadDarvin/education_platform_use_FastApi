from logging import getLogger
from typing import Optional
from uuid import UUID

from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .models import DeleteUserResponse
from .models import ShowUser
from .models import UpdateUserRequest
from .models import UpdateUserResponse
from .models import UserCreate
from db.dals import UserDAL
from db.session import get_db

logger = getLogger(__name__)

#########################
# BLOCK WITH API ROUTES #
#########################

user_router = APIRouter()


async def _create_new_user(body: UserCreate, db) -> ShowUser:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user = await user_dal.create_user(
                name=body.name,
                surname=body.surname,
                email=body.email,
            )
            return ShowUser(
                user_id=user.user_id,
                name=user.name,
                surname=user.surname,
                email=user.email,
                is_active=user.is_active,
            )


async def _get_user_by_id(user_id: UUID, db: AsyncSession) -> Optional[ShowUser]:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            user = await user_dal.get_user_by_id(user_id=user_id)
            if user is not None:
                return ShowUser(
                    user_id=user.user_id,
                    name=user.name,
                    surname=user.surname,
                    email=user.email,
                    is_active=user.is_active,
                )


async def _delete_user_by_id(user_id: UUID, db: AsyncSession) -> Optional[UUID]:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            deleted_user_id = await user_dal.delete_user_by_id(user_id=user_id)

            return deleted_user_id


async def _update_user_by_id(
    user_id: UUID, updated_user_params: dict, db: AsyncSession
) -> Optional[UUID]:
    async with db as session:
        async with session.begin():
            user_dal = UserDAL(session)
            updated_user_id = await user_dal.update_user_by_id(
                user_id=user_id, **updated_user_params
            )

            return updated_user_id


#########################
# ROUTERS #
#########################


@user_router.post("/", response_model=ShowUser)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)) -> ShowUser:
    try:
        return await _create_new_user(body, db)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")


@user_router.get("/", response_model=ShowUser)
async def get_user_by_id(user_id: UUID, db: AsyncSession = Depends(get_db)) -> ShowUser:
    user = await _get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")

    return user


@user_router.delete("/", response_model=DeleteUserResponse)
async def delete_user_by_id(
    user_id: UUID, db: AsyncSession = Depends(get_db)
) -> DeleteUserResponse:
    deleted_user_id = await _delete_user_by_id(user_id, db)
    if deleted_user_id is None:
        raise HTTPException(status_code=404, detail=f"user with id {user_id} not found")

    return DeleteUserResponse(deleted_user_id=deleted_user_id)


@user_router.patch("/", response_model=UpdateUserResponse)
async def update_user_by_id(
    user_id: UUID, body: UpdateUserRequest, db: AsyncSession = Depends(get_db)
) -> UpdateUserResponse:

    updated_user_params = body.dict(
        exclude_none=True
    )  # Pydantic method: clean all unsupported params
    if updated_user_params == {}:
        raise HTTPException(
            status_code=422,
            detail="At least one parameter for user update info should be provided",
        )

    user = await _get_user_by_id(user_id, db)
    if user is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found")

    try:
        updated_user_id = await _update_user_by_id(user_id, updated_user_params, db)
    except IntegrityError as err:
        logger.error(err)
        raise HTTPException(status_code=503, detail=f"Database error: {err}")

    return UpdateUserResponse(updated_user_id=updated_user_id)
