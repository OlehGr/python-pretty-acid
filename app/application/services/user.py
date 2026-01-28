import uuid
from dataclasses import dataclass

from app.application.interfaces.repository import IUserRepository
from app.models import User


@dataclass
class UserService:
    _user_repository: IUserRepository

    async def create_user(self, *, name: str) -> uuid.UUID:
        user = User.create(name=name)

        await self._user_repository.save(user)

        return user.id
