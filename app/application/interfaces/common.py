from abc import abstractmethod
from collections.abc import Coroutine
from typing import Protocol


class IBackgroundExecutor(Protocol):
    @abstractmethod
    def submit(self, coroutine: Coroutine) -> None: ...
