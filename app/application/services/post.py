import uuid
from dataclasses import dataclass

from app.application.interfaces.repository import IPostRepository, IUserRepository
from app.application.interfaces.transaction import ITransactionManager
from app.application.services.post_attachment import PostattachmentService
from app.models import Post


@dataclass
class PostService:
    _tm: ITransactionManager
    _post_repository: IPostRepository
    _user_repository: IUserRepository

    _post_attachment_servie: PostattachmentService

    async def create_post(
        self, *, text: str, user_id: uuid.UUID, attachments_url: list[str]
    ) -> uuid.UUID:
        async with self._tm.transaction():
            post = Post.create(text=text, user_id=user_id)
            await self._post_repository.save(post)
            await self._post_attachment_servie.create_attachments(
                post_id=post.id, file_urls=attachments_url
            )

            user = await self._user_repository.get_by_id(post.user_id)
            user.increament_posts_count()
            await self._user_repository.save(user)

            return post.id
