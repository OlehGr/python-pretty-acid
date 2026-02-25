from collections.abc import Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.interfaces.transaction import ITransactionalSession


class TransactionalSession(AsyncSession, ITransactionalSession):
    _callbacks_set_after_commit: set[Callable[[], Awaitable[None]]]
    _callbacks_after_commit: list[Callable[[], Awaitable[None]]]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._callbacks_set_after_commit = set()
        self._callbacks_after_commit = []

    def add_async_after_commit(self, cb: Callable[[], Awaitable[None]]) -> None:
        if cb in self._callbacks_set_after_commit:
            return

        self._callbacks_set_after_commit.add(cb)
        self._callbacks_after_commit.append(cb)

    def remove_async_after_commit(self, cb: Callable[[], Awaitable[None]]) -> None:
        if cb not in self._callbacks_set_after_commit:
            return

        self._callbacks_set_after_commit.discard(cb)
        self._callbacks_after_commit.remove(cb)

    def clear_after_commit_callbacks(self) -> None:
        self._callbacks_set_after_commit.clear()
        self._callbacks_after_commit.clear()

    async def execute_after_commit_callbacks(self) -> None:
        for cb in self._callbacks_after_commit:
            await cb()


TransactionalSessionFactory = async_sessionmaker[TransactionalSession]
