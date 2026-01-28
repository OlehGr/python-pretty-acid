from dataclasses import dataclass

from app.application.interfaces.repository import IUserRepository
from app.application.transaction.manager import TransactionManager
from app.models import User


@dataclass
class UserRepository(IUserRepository):
    _tm: TransactionManager

    async def save(self, user: User) -> None:
        async with self._tm.transaction() as tx:
            await tx.merge(user)
