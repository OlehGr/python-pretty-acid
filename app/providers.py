from dishka import Provider, Scope, alias, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from app.application.interfaces.repository import (
    IPostAttachmentRepository,
    IPostRepository,
    IUserRepository,
)
from app.application.interfaces.transaction import ITransactionManager
from app.application.services.post import PostService
from app.application.services.post_attachment import PostattachmentService
from app.application.services.user import UserService
from app.config import DATABASE_URL
from app.infrastructure.database.repository.post import PostRepository
from app.infrastructure.database.repository.post_attachment import (
    PostAttachmentRepository,
)
from app.infrastructure.database.repository.user import UserRepository
from app.infrastructure.database.transaction import (
    TransactionalSession,
    TransactionalSessionFactory,
    TransactionManager,
)


class DatabaseProvider(Provider):
    scope = Scope.APP

    @provide
    def engine(self) -> AsyncEngine:
        engine = create_async_engine(
            DATABASE_URL,
        )
        return engine

    @provide
    def session_factory(self, engine: AsyncEngine) -> TransactionalSessionFactory:
        return async_sessionmaker(
            bind=engine,
            class_=TransactionalSession,
            expire_on_commit=True,
            autoflush=False,
        )


class InfrastructureProvider(Provider):
    scope = Scope.APP

    transaction_manager_impl = provide(TransactionManager)
    transaction_manager = alias(source=TransactionManager, provides=ITransactionManager)

    user_repository = provide(UserRepository, provides=IUserRepository)
    post_repository = provide(PostRepository, provides=IPostRepository)
    post_attachment_repository = provide(
        PostAttachmentRepository, provides=IPostAttachmentRepository
    )


class ApplicationProvider(Provider):
    scope = Scope.APP

    user_service = provide(UserService)
    post_service = provide(PostService)
    post_attachment_service = provide(PostattachmentService)
