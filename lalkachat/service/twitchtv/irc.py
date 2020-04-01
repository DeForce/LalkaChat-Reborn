import asyncio
import random

import irc.client_aio
import requests

from base import Channel
from .config import HEADERS, logger
from .message import TwitchMessage


class TwitchIRC(irc.client_aio.AioSimpleIRCClient):
    def __init__(self, channel_name, channel: Channel, event_loop):
        asyncio.set_event_loop(event_loop)

        super().__init__()

        self.channel_name = channel_name
        self.channel = channel
        self.nickname = f'justinfan{"".join([str(random.randint(0, 9)) for index in range(15)])}'

    def connect(self):
        logger.info('Twitch Connecting')
        request = requests.get(f"http://tmi.twitch.tv/servers?channel={self.channel_name}", headers=HEADERS)
        if request.ok:
            host, port = random.choice(request.json()['servers']).split(':')
            asyncio.run_coroutine_threadsafe(
                self.connection.connect(host, port, self.nickname), asyncio.get_event_loop())
        else:
            raise ConnectionError(f'Unable to get irc host from twitch api: {request.status_code}')

    def on_welcome(self, connection, _):
        logger.info('IRC Connected, joining %s', self.channel_name)

        connection.join(f'#{self.channel_name}')
        connection.cap('REQ', ':twitch.tv/tags')
        connection.cap('REQ', ':twitch.tv/commands')

    def on_join(self, _, __):
        logger.info('Joined channel %s', self.channel_name)

    def on_pubmsg(self, _, event):
        message = TwitchMessage(event, self.channel_name, self.channel)
        self.channel.send_message(message)

    def on_action(self, _, event):
        message = TwitchMessage(event, self.channel_name, self.channel, action=True)
        self.channel.send_message(message)

    def on_usernotice(self, _, event):
        logger.debug(event)
