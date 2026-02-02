import uuid
from dataclasses import dataclass

from sqlalchemy import select

from app.application.interfaces.repository import IUserRepository
from app.infrastructure.database.transaction import TransactionManager
from app.models import User


@dataclass
class UserRepository(IUserRepository):
    _tm: TransactionManager

    async def get_by_id(self, user_id: uuid.UUID) -> User:
        query = select(User).where(User.id == user_id).limit(1)

        async with self._tm.session() as session:
            user = await session.scalar(query)

            if user is None:
                raise ValueError("User not found")

            return user

    async def save(self, user: User) -> None:
        async with self._tm.transaction() as tx:
            await tx.merge(user)
