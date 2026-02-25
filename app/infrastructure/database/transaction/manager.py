import asyncio
from weakref import WeakKeyDictionary

from app.application.interfaces.transaction import ITransactionManager
from .context import SessionContext, TransactionContext
from .session import TransactionalSession, TransactionalSessionFactory


class TransactionManager(ITransactionManager):
    _session_factory: TransactionalSessionFactory
    _task_sessions: WeakKeyDictionary[asyncio.Task, TransactionalSession]

    def __init__(self, session_factory: TransactionalSessionFactory) -> None:
        self._session_factory = session_factory
        self._task_sessions: WeakKeyDictionary[asyncio.Task, TransactionalSession] = (
            WeakKeyDictionary()
        )

    def transaction(self) -> TransactionContext:
        return TransactionContext(self._session_factory, self._task_sessions)

    def session(self) -> SessionContext:
        return SessionContext(self._session_factory, self._task_sessions)
