import datetime
import time
import uuid
from abc import ABC
from typing import List, Dict

DEFAULT_ICON = 'img/sources/lalkachat.png'
DEFAULT_PLATFORM_ID = 'lalkachat'
DEFAULT_CHANNEL = 'system'
DEFAULT_USERNAME = 'LalkaChat'

EMOTE_FORMAT = ':emote;{}:'

PLATFORM = {
    'icon': DEFAULT_ICON,
    'id': DEFAULT_PLATFORM_ID
}


MESSAGE_DEFAULT = 'default'
MESSAGE_HIGHLIGHT = 'highlight'


class Emote:
    def __init__(self, name, url):
        self.name = name
        self.url = url

    def to_json(self):
        return {
            'id': self.name,
            'url': self.url
        }


class Badge(Emote):
    pass


class BadgeSet:
    def __init__(self, badge_set: Dict[str, Badge]):
        self.set = badge_set

    def version(self, version) -> Badge:
        return self.set[version]


class Message:
    def __init__(self, text, channel_name=DEFAULT_CHANNEL, username=DEFAULT_USERNAME,
                 mid=None, pm=False, action=False, message_type=MESSAGE_DEFAULT):
        self._timestamp = datetime.datetime.now()
        self._id = mid if mid else str(uuid.uuid1())

        self._channel_name = channel_name
        self._username = username
        self._username_color = None

        self._text = text

        self._show_channel_name = False

        self._pm = pm
        self._action = action

        self._badges: List[Badge] = []
        self._emotes: List[Emote] = []

        self._type = message_type

    @property
    def type(self):
        return self._type

    @property
    def message_type(self):
        return 'message'

    @property
    def platform(self):
        return PLATFORM

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def unixtime(self):
        return time.mktime(self._timestamp.timetuple())

    def is_pm(self):
        return self._pm

    def is_mention(self):
        return False

    def add_emote(self, emote: Emote):
        self._emotes.append(emote)

    def add_badge(self, badge: Badge):
        self._badges.append(badge)

    def process_emotes(self, *args, **kwargs):
        raise NotImplementedError(f'Emotes are missing from the class {self.__class__.__name__}')

    def process_badges(self, *args, **kwargs):
        raise NotImplementedError(f'Badges are missing from the class {self.__class__.__name__}')

    def to_web(self):
        return {
            'type': self.message_type,
            'unixtime': self.unixtime,
            'payload': self.payload
        }

    @property
    def payload(self):
        return {
            'id': self._id,
            'type': self.type,
            'platform': self.platform,
            'channel': self._channel_name,

            'badges': [badge.to_json() for badge in self._badges],
            'emotes': [emote.to_json() for emote in self._emotes],

            'username': self._username,
            'username_color': self._username_color,

            'action': self.is_action(),
            'pm': self.is_pm(),
            'mention': self.is_mention(),
            'show_channel_name': self._show_channel_name,

            'text': self._text,
        }

    def is_action(self):
        return self._action
