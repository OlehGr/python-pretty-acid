from abc import abstractmethod
from typing import Callable, Protocol


class ITransactionalSession(Protocol):
    @abstractmethod
    async def flush(self) -> None: ...

    @abstractmethod
    def add_on_commit(self, cb: Callable[[], None]) -> None: ...

    @abstractmethod
    def remove_on_commit(self, cb: Callable[[], None]) -> None: ...


class ITransactionContext(Protocol):
    @abstractmethod
    async def __aenter__(self) -> ITransactionalSession: ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback) -> None: ...


class ITransactionManager(Protocol):
    @abstractmethod
    def transaction(self) -> ITransactionContext: ...
