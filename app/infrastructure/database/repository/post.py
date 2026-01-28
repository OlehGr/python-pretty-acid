from dataclasses import dataclass

from app.application.interfaces.repository import IPostRepository
from app.application.transaction.manager import TransactionManager
from app.models import Post


@dataclass
class PostRepository(IPostRepository):
    _tm: TransactionManager

    async def save(self, post: Post) -> None:
        async with self._tm.transaction() as tx:
            await tx.merge(post)
