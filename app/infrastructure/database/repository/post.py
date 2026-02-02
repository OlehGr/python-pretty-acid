import uuid
from dataclasses import dataclass

from sqlalchemy import select

from app.application.interfaces.repository import IPostRepository
from app.infrastructure.database.transaction import TransactionManager
from app.models import Post


@dataclass
class PostRepository(IPostRepository):
    _tm: TransactionManager

    async def get_by_id(self, post_id: uuid.UUID) -> Post:
        query = select(Post).where(Post.id == post_id).limit(1)

        async with self._tm.session() as session:
            post = await session.scalar(query)

            if post is None:
                raise ValueError("Post not found")

            return post

    async def save(self, post: Post) -> None:
        async with self._tm.transaction() as tx:
            await tx.merge(post)
