import random

import irc.client_aio
import requests

from .config import HEADERS, logger
from .message import TwitchMessage


class TwitchIRC(irc.client_aio.AioSimpleIRCClient):
    def __init__(self, channel, service, event_loop):
        self.reactor = self.reactor_class(loop=event_loop)
        self.connection = self.reactor.server()
        self.dcc_connections = []
        self.reactor.add_global_handler("all_events", self._dispatcher, -10)
        self.reactor.add_global_handler("dcc_disconnect", self._dcc_disconnect, -10)

        self.service = service
        self.channel = channel
        self.nickname = f'justinfan{"".join([str(random.randint(0, 9)) for index in range(15)])}'

    def connect(self):
        request = requests.get(f"http://tmi.twitch.tv/servers?channel={self.channel}", headers=HEADERS)
        if request.ok:
            host, port = random.choice(request.json()['servers']).split(':')
            self.reactor.loop.create_task(self.connection.connect(host, port, self.nickname))
        else:
            raise ConnectionError(f'Unable to get irc host from twitch api: {request.status_code}')

    def on_welcome(self, connection, _):
        logger.info('IRC Connected, joining %s', self.channel)

        connection.join(f'#{self.channel}')
        connection.cap('REQ', ':twitch.tv/tags')
        connection.cap('REQ', ':twitch.tv/commands')

    def on_join(self, _, __):
        logger.info('Joined channel %s', self.channel)

    def on_pubmsg(self, _, event):
        message = TwitchMessage(event, self.channel, self.service)
        self.service.send_message(message)
