import uuid
from abc import abstractmethod
from typing import Protocol

from app.models import Post, PostAttachment, User


class IUserRepository(Protocol):
    @abstractmethod
    async def save(self, user: User) -> None: ...

    @abstractmethod
    async def get_by_id(self, user_id: uuid.UUID) -> User: ...


class IPostRepository(Protocol):
    @abstractmethod
    async def save(self, post: Post) -> None: ...

    @abstractmethod
    async def get_by_id(self, post_id: uuid.UUID) -> Post: ...


class IPostAttachmentRepository(Protocol):
    @abstractmethod
    async def save_list(self, post_attachments: list[PostAttachment]) -> None: ...
