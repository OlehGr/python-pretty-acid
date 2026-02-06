from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.interfaces.transaction import ITransactionalSession


class TransactionalSession(AsyncSession, ITransactionalSession):
    set_callbacks_on_commit: set[Callable[[], None]]
    callbacks_on_commit: list[Callable[[], None]]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_callbacks_on_commit = set()
        self.callbacks_on_commit = []

    def add_on_commit(self, cb: Callable[[], None]) -> None:
        if cb in self.set_callbacks_on_commit:
            return

        self.set_callbacks_on_commit.add(cb)
        self.callbacks_on_commit.append(cb)

    def remove_on_commit(self, cb: Callable[[], None]) -> None:
        if cb not in self.set_callbacks_on_commit:
            return

        self.set_callbacks_on_commit.discard(cb)
        self.callbacks_on_commit.remove(cb)


TransactionalSessionFactory = async_sessionmaker[TransactionalSession]
