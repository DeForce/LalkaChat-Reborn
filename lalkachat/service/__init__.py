import asyncio
from abc import ABC
from queue import Queue

from base import Base


class Service(Base, ABC):
    def __init__(self, profiles, active_profile, queue: Queue):
        super().__init__(profiles, active_profile)

        self.queue = queue
        self.loop = asyncio.get_event_loop()

    def send_message(self, message):
        asyncio.run_coroutine_threadsafe(self._send_message(message), self.loop)

    async def _send_message(self, message):
        await self.queue.put(message)
