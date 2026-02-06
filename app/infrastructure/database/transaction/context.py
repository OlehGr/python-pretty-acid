import asyncio
from weakref import WeakKeyDictionary

from app.infrastructure.database.transaction.session import (
    TransactionalSession,
    TransactionalSessionFactory,
)

_task_sessions: WeakKeyDictionary[asyncio.Task, TransactionalSession] = (
    WeakKeyDictionary()
)


def _get_task() -> asyncio.Task:
    task = asyncio.current_task()
    if task is None:
        raise RuntimeError("No current asyncio task; cannot bind session")
    return task


def _on_task_done(task: asyncio.Task) -> None:
    try:
        _task_sessions.pop(task)
    except RuntimeError:
        pass


class _BaseSessionContext:
    _session_factory: TransactionalSessionFactory
    _session: TransactionalSession | None

    def __init__(self, session_factory: TransactionalSessionFactory) -> None:
        self._session_factory = session_factory
        self._session = None

    @property
    def _is_root(self) -> bool:
        return self._session is not None

    async def _get_or_create_session(self) -> TransactionalSession:
        task = _get_task()

        existing = _task_sessions.get(task)
        if existing is not None:
            return existing

        self._session = self._session_factory()
        _task_sessions[task] = self._session
        task.add_done_callback(_on_task_done)

        return self._session

    async def _flush_if_not_root(self) -> None:
        if self._is_root:
            return
        task = _get_task()
        session = _task_sessions.get(task)
        if session is not None:
            await session.flush()

    async def _close_session_if_root(self) -> None:
        if not self._is_root:
            return

        task = _get_task()

        try:
            if self._session:
                await self._session.close()
        finally:
            _task_sessions.pop(task, None)


class TransactionContext(_BaseSessionContext):
    async def __aenter__(self) -> TransactionalSession:
        session = await self._get_or_create_session()
        if self._is_root:
            await session.begin()
        return session

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        if self._session is None:
            if exc_value is None:
                await self._flush_if_not_root()
            return

        try:
            if exc_value is not None:
                await self._session.rollback()
            else:
                await self._session.commit()
        finally:
            await self._close_session_if_root()


class SessionContext(_BaseSessionContext):
    async def __aenter__(self) -> TransactionalSession:
        return await self._get_or_create_session()

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self._close_session_if_root()
