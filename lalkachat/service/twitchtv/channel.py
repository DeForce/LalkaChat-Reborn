import threading

from service.twitchtv.config import ChannelConfig
from service.twitchtv.irc import TwitchIRC


class TwitchChannel:
    config: ChannelConfig
    irc: TwitchIRC

    def __init__(self, channel, config):
        self.config = config
        self.channel = channel

        self.irc = TwitchIRC(channel)
        self.irc.connect()
