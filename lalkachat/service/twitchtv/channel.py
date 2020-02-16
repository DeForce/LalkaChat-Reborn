from service.twitchtv.config import ChannelConfig
from service.twitchtv.irc import TwitchIRC


class TwitchChannel:
    config: ChannelConfig
    irc: TwitchIRC

    def __init__(self, channel, config, service):
        self.config = config
        self.channel = channel
        self.service = service

        self.irc = TwitchIRC(channel, service, self.service.service_loop)
        self.irc.connect()
