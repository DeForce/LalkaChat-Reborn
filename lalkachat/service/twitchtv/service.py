import asyncio
import logging
import threading
from queue import Queue

import requests

from service import Service
from .channel import TwitchChannel
from .config import ServiceConfig, HEADERS, logger


class TwitchTV(Service):
    channels = {}

    def __init__(self, profiles, active_profile, queue: Queue):
        super().__init__(profiles, active_profile, queue)

        self.config = ServiceConfig(self.class_configuration)

        self.bits = {}
        self.emotes = {}
        self.badges = {}

        self.service_loop = asyncio.get_event_loop()

        threading.Thread(target=self.init_twitch, daemon=True).start()

    def init_twitch(self):
        self.get_all_emotes()

        for channel, config in self.config.channels.items():
            self.channels[channel] = TwitchChannel(channel, config, self)

    def get_all_emotes(self):
        logger.info('Getting Twitch Emotes')

        request = requests.get('https://api.twitch.tv/kraken/chat/emoticons', headers=HEADERS)
        if request.ok:
            logger.info('Emotes received')
            data = request.json()['emoticons']
            for emote in data:
                self.emotes[emote['id']] = emote
            logger.info('Emotes processed')

    def save(self):
        return self.config.save()
