import logging
import random

import irc.client_aio

from service.twitchtv.config import IRC_PORT, IRC_HOST


class TwitchIRC(irc.client_aio.AioSimpleIRCClient):
    def __init__(self, channel):
        super().__init__()
        self.channel = f'#{channel}'
        self.nickname = f'justinfan{"".join([str(random.randint(0, 9)) for index in range(15)])}'

    def connect(self):
        super().connect(IRC_HOST, IRC_PORT, self.nickname)

    def on_welcome(self, connection, event):
        logging.info('IRC Connected')

        connection.join(self.channel)
        connection.cap('REQ', ':twitch.tv/tags')
        connection.cap('REQ', ':twitch.tv/commands')

    def on_pubmsg(self, connection, event):
        pass