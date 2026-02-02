from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.interfaces.transaction import ITransactionManager

from .context import SessionContext, TransactionContext


class TransactionManager(ITransactionManager):
    _session_factory: async_sessionmaker[AsyncSession]

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    def transaction(self) -> TransactionContext:
        return TransactionContext(self._session_factory)

    def session(self) -> SessionContext:
        return SessionContext(self._session_factory)
