import asyncio
from typing import Coroutine

from app.application.interfaces.common import IBackgroundExecutor


class BackgroundExecutor(IBackgroundExecutor):
    _tasks: set[asyncio.Task]

    def __init__(self) -> None:
        self._tasks = set()

    def submit(self, coroutine: Coroutine) -> None:
        loop = asyncio.get_event_loop()
        task = loop.create_task(coroutine)
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
