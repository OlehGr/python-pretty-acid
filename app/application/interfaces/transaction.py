from abc import abstractmethod
from typing import Protocol


class ITransactionalSession(Protocol):
    @abstractmethod
    async def flush(self) -> None: ...


class ITransactionContext(Protocol):
    @abstractmethod
    async def __aenter__(self) -> ITransactionalSession: ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback) -> None: ...


class ITransactionManager(Protocol):
    @abstractmethod
    def transaction(self) -> ITransactionContext: ...
