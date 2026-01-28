from contextvars import ContextVar, Token

from .interfaces import (
    TransactionalSession,
    TransactionalSessionFactory,
)

_current_session: ContextVar[TransactionalSession | None] = ContextVar(
    "current_session", default=None
)


class _BaseSessionContext:
    _session_factory: TransactionalSessionFactory
    _session: TransactionalSession | None
    _ctx_token: Token[TransactionalSession | None] | None

    def __init__(self, session_factory: TransactionalSessionFactory) -> None:
        self._session_factory = session_factory
        self._session = None
        self._ctx_token = None

    @property
    def _is_root(self) -> bool:
        return self._session is not None

    async def _get_or_create_session(self) -> TransactionalSession:
        existing = _current_session.get()
        if existing is not None:
            return existing

        self._session = self._session_factory()
        self._ctx_token = _current_session.set(self._session)
        return self._session

    async def _flush_if_not_root(self) -> None:
        if self._is_root:
            return
        session = _current_session.get()
        if session is None:
            return
        await session.flush()

    async def _close_session_if_root(self) -> None:
        if not self._is_root:
            return

        assert self._session is not None
        assert self._ctx_token is not None

        await self._session.close()
        _current_session.reset(self._ctx_token)


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
