import asyncio
import copy
from abc import ABC
from queue import Queue
from typing import Dict

from message import BadgeSet, Emote


class Base:
    def __init__(self, profiles, active_profile, config_prefix=None):
        self.prefix = config_prefix if config_prefix else self.__class__.__name__.lower()

        self.profiles = profiles
        self.active_profile_name = active_profile

    @property
    def class_configuration(self):
        return self.profiles.get(self.active_profile_name, {}).get(self.prefix, {})

    def save(self):
        raise NotImplementedError(f"Save should be implemented in {self.__class__.__name__}")


class Config:
    def save(self):
        raise NotImplementedError(f"Save should be implemented in {self.__class__.__name__}")


class Service(Base, ABC):
    def __init__(self, profiles, active_profile, queue: Queue):
        super().__init__(profiles, active_profile)

        self.queue = queue
        self.loop = asyncio.get_event_loop()

        self.badges: Dict[str, BadgeSet] = {}
        self.emotes: Dict[str, Emote] = {}
        self.channels: Dict[str, Channel] = {}

    def send_message(self, message):
        asyncio.run_coroutine_threadsafe(self._send_message(message), self.loop)

    async def _send_message(self, message):
        await self.queue.put(message)


class Channel:
    def __init__(self, channel_name, config, service: Service):
        self.config = config
        self.channel = channel_name
        self.service = service

        self.badges: Dict[str, BadgeSet] = copy.deepcopy(service.badges)
        self.emotes: Dict[str, Emote] = copy.deepcopy(service.emotes)

    def send_message(self, message):
        self.service.send_message(message)
