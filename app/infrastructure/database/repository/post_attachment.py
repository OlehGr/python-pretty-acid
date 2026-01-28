from dataclasses import dataclass

from app.application.interfaces.repository import IPostAttachmentRepository
from app.application.transaction.manager import TransactionManager
from app.models import PostAttachment


@dataclass
class PostAttachmentRepository(IPostAttachmentRepository):
    _tm: TransactionManager

    async def save_list(self, post_attachments: list[PostAttachment]) -> None:
        async with self._tm.transaction() as tx:
            for post_attachment in post_attachments:
                await tx.merge(post_attachment)

    async def save(self, user: PostAttachment) -> None:
        async with self._tm.transaction() as tx:
            await tx.merge(user)
