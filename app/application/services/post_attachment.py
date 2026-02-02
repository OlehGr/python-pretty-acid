import uuid
from dataclasses import dataclass

from app.application.interfaces.repository import (
    IPostAttachmentRepository,
    IPostRepository,
)
from app.application.interfaces.transaction import ITransactionManager
from app.models import PostAttachment


@dataclass
class PostattachmentService:
    _tm: ITransactionManager
    _post_attachment_repository: IPostAttachmentRepository
    _post_repository: IPostRepository

    async def create_attachments(
        self, file_urls: list[str], post_id: uuid.UUID
    ) -> list[uuid.UUID]:
        async with self._tm.transaction():
            post_attachments = [
                PostAttachment.create(post_id=post_id, file_url=file_url)
                for file_url in file_urls
            ]
            await self._post_attachment_repository.save_list(post_attachments)

            post = await self._post_repository.get_by_id(post_id)
            post.update_attachments_count(len(post_attachments))
            await self._post_repository.save(post)

            return [post_attachment.id for post_attachment in post_attachments]
