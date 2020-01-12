import asyncio
from queue import Queue


class Service:
    def __init__(self, profiles, active_profile, queue: Queue):
        self.queue = queue
        self.profiles = profiles
        self.active_profile = active_profile
        self.loop = asyncio.get_event_loop()

    def send_message(self, message):
        asyncio.run_coroutine_threadsafe(self._send_message(message), self.loop)

    async def _send_message(self, message):
        await self.queue.put(message)
