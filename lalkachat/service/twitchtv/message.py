import re

from base import Channel
from message import Message, EMOTE_FORMAT, Emote, MESSAGE_DEFAULT, MESSAGE_HIGHLIGHT
from service.twitchtv.base import EMOTE_URL, BITS_REGEXP

PLATFORM = {
    'icon': 'img/sources/twitchtv.png',
    'id': 'twitch'
}

TWITCH_MESSAGE_TYPES = {
    None: MESSAGE_DEFAULT,
    'highlighted-message': MESSAGE_HIGHLIGHT
}


class TwitchMessage(Message):
    def __init__(self, event, channel_name, channel: Channel, **kwargs):
        self.channel = channel
        self.tags = {item['key']: item['value'] for item in event.tags}

        text = event.arguments[0]
        user = self.tags.get('display-name', event.source.split('!')[0])

        message_type = TWITCH_MESSAGE_TYPES[self.tags.get('msg-id')]

        super().__init__(text, channel_name=channel_name, username=user, message_type=message_type, **kwargs)
        self._username_color = self.tags.get('color')

        self.process_emotes()
        self.process_badges()
        self.process_bttv_and_frankerz()

        self.process_bits()

    @staticmethod
    def get_emote_list(emotes):
        if emotes is None:
            return {}

        for emote in emotes.split('/'):
            emote_id, emote_pos_diap = emote.split(':')

            for position in emote_pos_diap.split(','):
                start, end = position.split('-')
                yield {'emote_id': emote_id, 'start': int(start), 'end': int(end)}

    def process_emotes(self):
        emotes = self.get_emote_list(self.tags.get('emotes'))
        sorted_emotes = sorted(emotes, key=lambda k: k['start'], reverse=True)

        for emote in sorted_emotes:
            self._text = '{start}{emote}{end}'.format(
                start=self._text[:emote['start']],
                end=self._text[emote['end'] + 1:],
                emote=EMOTE_FORMAT.format(emote['emote_id']))
            emote_id = emote['emote_id'].split('_')[0]
            self.add_emote(Emote(emote_id, EMOTE_URL.format(emote_id)))

    def process_badges(self):
        badge_list = self.tags.get('badges')
        if not badge_list:
            return

        badges = self.channel.badges
        for badge in badge_list.split(','):
            name, version = badge.split('/')

            if name in badges:
                self.add_badge(badges[name].version(version))

    @property
    def platform(self):
        return PLATFORM

    def process_bttv_and_frankerz(self):
        words = self._text.split()
        for index, word in enumerate(words):
            if word in self.channel.emotes:
                custom_smile = self.channel.emotes[word]
                self.add_emote(custom_smile)
                words[index] = EMOTE_FORMAT.format(custom_smile.name)
        self._text = ' '.join(words)

    def process_bits(self):
        if 'bits' not in self.tags:
            return

        for word in self._text.split():
            reg = re.match(BITS_REGEXP, word)
            if not reg:
                continue

            emote, amount = reg.groups()
            emote = emote.lower()
            if emote not in self.channel.bits:
                continue

            tier = min([tier for tier in self.channel.bits[emote]['tiers'].keys() if tier - int(amount) <= 0],
                       key=lambda x: (abs(x - int(amount)), x))

            emote_key = f'{emote}-{tier}'
            if emote_key in self.channel.bits:
                continue

            self._text.bits[emote_key] = self.channel.bits[emote]['tiers'][tier]
            self._text = self._text.replace(emote, EMOTE_FORMAT.format(emote))
