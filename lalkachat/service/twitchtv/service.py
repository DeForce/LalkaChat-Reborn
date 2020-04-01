import threading
from queue import Queue

import requests

from base import Service
from message import Emote, BadgeSet, Badge
from .base import BTTV_URL
from .channel import TwitchChannel
from .config import ServiceConfig


class TwitchTV(Service):
    def __init__(self, profiles, active_profile, queue: Queue):
        super().__init__(profiles, active_profile, queue)

        self.config = ServiceConfig(self.class_configuration)
        self.bits = {}

        threading.Thread(target=self.init_twitch, daemon=True).start()

    def init_twitch(self):
        self.get_bttv_emotes()
        self.get_badges()

        for channel_name, config in self.config.channels.items():
            self.channels[channel_name] = TwitchChannel(channel_name, config, self)

    def get_badges(self):
        request = requests.get('https://badges.twitch.tv/v1/badges/global/display')
        if request.ok:
            badges = request.json()['badge_sets']
            for name, badge_info in badges.items():
                self.badges[name] = BadgeSet({
                    version: Badge(version,
                                   data.get('image_url_4x', data.get('image_url_2x', data.get('image_url_1x'))))
                    for version, data in badge_info['versions'].items()
                })

    def get_bttv_emotes(self):
        request = requests.get('https://api.betterttv.net/2/emotes')
        if request.ok:
            data = request.json()
            for emote in data['emotes']:
                self.emotes[emote['code']] = Emote(emote['code'], BTTV_URL.format(id=emote['id']))

    def save(self):
        return self.config.save()
