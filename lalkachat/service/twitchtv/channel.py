import requests

from base import Channel, Service
from message import BadgeSet, Badge, Emote
from service.twitchtv.base import BTTV_URL
from service.twitchtv.config import ChannelConfig, HEADERS
from service.twitchtv.irc import TwitchIRC


class TwitchChannel(Channel):
    config: ChannelConfig
    irc: TwitchIRC

    def __init__(self, channel_name, config, service: Service):
        super().__init__(channel_name, config, service)

        self.id = self.get_channel_id()

        self.update_badges()
        self.update_bttv_smiles()
        self.get_frankerz_smiles()

        self.bits = self.get_bits()

        self.irc = TwitchIRC(channel_name, self, service.loop)
        self.irc.connect()

    def get_channel_id(self):
        req = requests.get('https://api.twitch.tv/kraken/users', params={'login': self.channel}, headers=HEADERS)
        if not req.ok:
            return

        return req.json()['users'][0]['_id']

    def update_badges(self):
        request = requests.get(f'https://badges.twitch.tv/v1/badges/channels/{self.id}/display')
        if request.ok:
            badges = request.json()
            for name, badge_info in badges['badge_sets'].items():
                self.badges[name] = BadgeSet({
                    version: Badge(version,
                                   data.get('image_url_4x', data.get('image_url_2x', data.get('image_url_1x'))))
                    for version, data in badge_info['versions'].items()
                })

    def update_bttv_smiles(self):
        request = requests.get(f'https://api.betterttv.net/2/channels/{self.channel}')
        if request.ok:
            data = request.json()
            for emote in data['emotes']:
                self.emotes[emote['code']] = Emote(emote['code'], BTTV_URL.format(id=emote['id']))

    def get_frankerz_smiles(self):
        request = requests.get(f'https://api.frankerfacez.com/v1/room/id/{self.id}')
        if request.ok:
            data = request.json()
            for s_id, set_data in data['sets'].items():
                for emote in set_data['emoticons']:
                    emote_url = emote['urls'].get('4', emote['urls'].get('2', emote['urls'].get('1')))
                    self.emotes[emote['name']] = Emote(emote['name'], f'https:{emote_url}')

    def get_bits(self):
        request = requests.get(f"https://api.twitch.tv/kraken/bits/actions/?channel_id={self.id}", headers=HEADERS)
        if request.ok:
            data = request.json()['actions']
            return {
                bit_data['prefix'].lower(): {
                    'tiers': {int(tier['id']): tier for tier in bit_data['tiers']},
                    'states': bit_data['states'],
                    'scales': bit_data['scales']
                } for bit_data in data
            }
