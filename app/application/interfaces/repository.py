from abc import abstractmethod
from typing import Protocol

from app.models import Post, PostAttachment, User


class IUserRepository(Protocol):
    @abstractmethod
    async def save(self, user: User) -> None: ...


class IPostRepository(Protocol):
    @abstractmethod
    async def save(self, post: Post) -> None: ...


class IPostAttachmentRepository(Protocol):
    @abstractmethod
    async def save_list(self, post_attachments: list[PostAttachment]) -> None: ...
