from .context import SessionContext, TransactionContext
from .interfaces import TransactionalSessionFactory


class TransactionManager:
    _session_factory: TransactionalSessionFactory

    def __init__(self, session_factory: TransactionalSessionFactory) -> None:
        self._session_factory = session_factory

    def transaction(self) -> TransactionContext:
        return TransactionContext(self._session_factory)

    def session(self) -> SessionContext:
        return SessionContext(self._session_factory)
