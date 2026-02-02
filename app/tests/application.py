import pytest
from dishka import Container, make_container
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.services.post import PostService
from app.application.services.user import UserService
from app.config import DB_NAME
from app.infrastructure.database.transaction import TransactionManager
from app.models import Post, PostAttachment, User
from app.providers import ApplicationProvider, DatabaseProvider, InfrastructureProvider

pytestmark = pytest.mark.asyncio


@pytest.fixture
def di():
    di = make_container(
        DatabaseProvider(), InfrastructureProvider(), ApplicationProvider()
    )
    yield di
    di.close()


class TestApplication:
    async def test_create_post_integration_on_sucess(self, di: Container):
        """
        Сервисы корректно работают, используя TransactionManager.
        Все данные сохраняються в БД
        """

        tm = di.get(TransactionManager)
        user_service = di.get(UserService)
        post_service = di.get(PostService)

        async with tm.transaction():
            user_id = await user_service.create_user(name="Bob")
            post_id = await post_service.create_post(
                text="Hello world",
                user_id=user_id,
                attachments_url=[
                    "https://examle.com/image1.jpg",
                    "https://examle.com/image2.jpg",
                    "https://examle.com/image3.jpg",
                ],
            )

        async with tm.session() as s:
            created_user = await s.get(User, user_id)
            created_post = await s.get(Post, post_id)

            assert created_user is not None
            assert created_post is not None

            assert created_user.posts_count == 1
            assert created_post.attachments_count == 3

            query_attachments_count = (
                select(func.count())
                .select_from(PostAttachment)
                .where(PostAttachment.post_id == post_id)
            )
            attachments_count = await s.scalar(query_attachments_count)
            assert attachments_count == 3

        await self._assert_no_stuck_transactions(di)

    async def test_create_post_integration_on_fail(self, di: Container):
        """
        При возникновении ошибки все данные не сохраняються
        """

        tm = di.get(TransactionManager)
        user_service = di.get(UserService)
        post_service = di.get(PostService)

        user_id = None
        post_id = None

        with pytest.raises(ValueError):
            async with tm.transaction():
                user_id = await user_service.create_user(name="Bob")
                post_id = await post_service.create_post(
                    text="Hello world",
                    user_id=user_id,
                    attachments_url=[
                        "https://examle.com/image1.jpg",
                        "https://examle.com/image2.jpg",
                        "Какой-то не валтжный URL",
                    ],
                )

        async with tm.session() as s:
            created_user = await s.get(User, user_id)

            assert created_user is None
            assert post_id is None

            query_attachments_count = (
                select(func.count())
                .select_from(PostAttachment)
                .where(PostAttachment.post_id == post_id)
            )
            attachments_count = await s.scalar(query_attachments_count)
            assert attachments_count == 0

        await self._assert_no_stuck_transactions(di)

    async def _assert_no_stuck_transactions(self, di: Container):
        session_maker = di.get(async_sessionmaker[AsyncSession])
        async with session_maker() as s:
            stuck_tx_count = await s.scalar(
                text(f"""
                        SELECT COUNT(*)
                        FROM pg_stat_activity
                        WHERE datname = '{DB_NAME}'
                            AND pid <> pg_backend_pid()
                            AND state IN ('idle in transaction', 'idle in transaction (aborted)')
                    """)
            )
            assert stuck_tx_count == 0
