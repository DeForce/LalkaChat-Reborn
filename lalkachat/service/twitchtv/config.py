import logging
from typing import Dict

from base import Config
from secret import TWITCH_CLIENT_ID

IRC_HOST = 'irc.twitch.tv'
IRC_PORT = 6667

HEADERS = {'Client-ID': TWITCH_CLIENT_ID,
           'Accept': 'application/vnd.twitchtv.v5+json'}

logger = logging.getLogger('twitch')


class ChannelConfig(Config):
    def __init__(self, config):
        self.nickname_color = config.get('nickname_color', True)

    def save(self):
        return {
            'nickname_color': self.nickname_color
        }


class ServiceConfig(Config):
    channels: Dict[str, ChannelConfig] = {}

    def __init__(self, config):
        self.enable_bttv = config.get('enable_bttv', True)
        self.enable_ffz = config.get('enable_ffz', True)
        channels = config.get('channels', {})
        for channel_name, channel_config in channels.items():
            self.channels[channel_name] = ChannelConfig(channel_config)

    def save(self):
        return {
            'enable_bttv': self.enable_bttv,
            'enable_ffz': self.enable_ffz,
            'channels': {
                channel_name: channel_config.save()
                for channel_name, channel_config in self.channels.items()
            }
        }
