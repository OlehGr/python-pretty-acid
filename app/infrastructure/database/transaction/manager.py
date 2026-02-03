from app.application.interfaces.transaction import ITransactionManager
from app.infrastructure.database.transaction.session import TransactionalSessionFactory

from .context import SessionContext, TransactionContext


class TransactionManager(ITransactionManager):
    _session_factory: TransactionalSessionFactory

    def __init__(self, session_factory: TransactionalSessionFactory) -> None:
        self._session_factory = session_factory

    def transaction(self) -> TransactionContext:
        return TransactionContext(self._session_factory)

    def session(self) -> SessionContext:
        return SessionContext(self._session_factory)
