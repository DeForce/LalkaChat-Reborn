from message import Message, EMOTE_FORMAT

PLATFORM = {
    'icon': 'img/sources/twitchtv.png',
    'id': 'twitch'
}


class TwitchMessage(Message):
    def __init__(self, event, channel, service):
        self.service = service
        self.tags = {item['key']: item['value'] for item in event.tags}

        text = event.arguments[0]
        user = self.tags.get('display-name', event.source.split('!')[0])

        super().__init__(text, channel=channel, username=user)
        self._username_color = self.tags.get('color')

        self.process_emotes()

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
            self.add_emote(emote['emote_id'], )

    def add_emote(self, emote_id, **kwargs):
        emote_data = self.service.emotes[int(emote_id)]
        super().add_emote(emote_id, emote_data)
        pass

    @property
    def platform(self):
        return PLATFORM
