from abc import abstractmethod
from typing import Coroutine, Protocol


class IBackgroundExecutor(Protocol):
    @abstractmethod
    def submit(self, coroutine: Coroutine) -> None: ...
