import threading
from queue import Queue

from service import Service
from service.twitchtv.channel import TwitchChannel
from service.twitchtv.config import ServiceConfig


class TwitchTV(Service):
    channels = {}

    def __init__(self, profiles, active_profile, queue: Queue):
        super().__init__(profiles, active_profile, queue)

        self.config = ServiceConfig(self.class_configuration)

        self.bits = {}
        self.emotes = {}
        self.badges = {}

        threading.Thread(target=self.init_twitch, daemon=True).run()

    def init_twitch(self):
        for channel, config in self.config.channels.items():
            self.channels[channel] = TwitchChannel(channel, config)

    def save(self):
        return self.config.save()
