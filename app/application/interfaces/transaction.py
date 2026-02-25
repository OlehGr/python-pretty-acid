from abc import abstractmethod
from collections.abc import Awaitable, Callable
from typing import Protocol


class ITransactionalSession(Protocol):
    @abstractmethod
    async def flush(self) -> None: ...

    @abstractmethod
    def add_async_after_commit(self, cb: Callable[[], Awaitable[None]]) -> None: ...

    @abstractmethod
    def remove_async_after_commit(self, cb: Callable[[], Awaitable[None]]) -> None: ...


class ITransactionContext(Protocol):
    @abstractmethod
    async def __aenter__(self) -> ITransactionalSession: ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback) -> None: ...


class ITransactionManager(Protocol):
    @abstractmethod
    def transaction(self) -> ITransactionContext: ...
