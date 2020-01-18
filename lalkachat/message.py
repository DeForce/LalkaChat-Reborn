import datetime
import time
import uuid

DEFAULT_ICON = 'img/sources/lalkachat.png'
DEFAULT_PLATFORM_ID = 'lalkachat'
DEFAULT_CHANNEL = 'system'
DEFAULT_USERNAME = 'LalkaChat'


class Message:
    def __init__(self, text, channel=DEFAULT_CHANNEL, username=DEFAULT_USERNAME, mid=None):
        self._timestamp = datetime.datetime.now()
        self._id = mid if mid else str(uuid.uuid1())

        self._channel = channel
        self._username = username
        self._username_color = None

        self._text = text

        self._show_channel_name = False

        self._badges = []
        self._emotes = []

    @property
    def type(self):
        return 'message'

    @property
    def platform(self):
        return {
            'icon': DEFAULT_ICON,
            'id': DEFAULT_PLATFORM_ID
        }

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def unixtime(self):
        return time.mktime(self._timestamp.timetuple())

    def to_web(self):
        return {
            'type': self.type,
            'unixtime': self.unixtime,
            'payload': self.payload
        }

    def is_pm(self):
        return False

    def is_mention(self):
        return False

    @property
    def payload(self):
        return {
            'id': self._id,
            'type': self.type,
            'platform': self.platform,
            'channel': self._channel,
            'badges': self._badges,

            'emotes': self._emotes,

            'username': self._username,
            'username_color': self._username_color,

            'pm': self.is_pm(),
            'mention': self.is_mention(),
            'show_channel_name': self._show_channel_name,

            'text': self._text,
        }
