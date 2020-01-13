import asyncio
import collections
import logging
import os

import yaml
from aiohttp import web
from dotmap import DotMap

from __init__ import HTTP_FOLDER
from message import Message
from module.blacklist import Blacklist
from service.sample import SampleService

DEFAULT_THEME_NAME = 'default'
DEFAULT_WINDOW_NAME = 'default'


def get_available_themes():
    for folder in os.listdir(HTTP_FOLDER):
        theme_folder = os.path.join(HTTP_FOLDER, folder)
        if not os.path.isdir(theme_folder):
            continue

        yield {folder: get_theme_settings_default(folder)}


def theme_settings_folder(style):
    return os.path.join(HTTP_FOLDER, style)


def get_theme_settings_default(style):
    style_file = os.path.join(theme_settings_folder(style), 'settings.json')
    with open(style_file, 'r') as f:
        json_data = yaml.safe_load(f.read())
    if json_data:
        return json_data


class ServerAPI:
    def __init__(self, profile, server):
        self.profile = profile
        self.server = server

    def get_handlers(self):
        return ('get_window_settings', self.get_window_settings),

    async def get_window_settings(self, request: web.Request):
        path = request.path.split('/')
        profile = self.server.active_profile_name
        window = self.server.active_window

        if len(path) > 4:
            _, _, profile, _, window, _, _ = path

        return web.json_response(self.server.profiles[profile].windows[window]['keys'].toDict())


def create_default_profile():
    return DotMap({
        'active_window': DEFAULT_WINDOW_NAME,
        'windows': {
            DEFAULT_WINDOW_NAME: {
                'theme': DEFAULT_THEME_NAME,
                'keys': get_theme_settings_default(DEFAULT_THEME_NAME)
            }
        }
    })


class Server:
    def __init__(self, profiles, profile, base_configuration):
        self.queue = asyncio.Queue()
        self.active_websockets = []  # type: [web.WebSocketResponse]

        self.base_configuration = base_configuration

        self.profiles = profiles
        self.themes = collections.ChainMap(*get_available_themes())

        self.modules = [
            Blacklist(profiles, profile, self.queue)
        ]
        self.services = [
            SampleService(profiles, profile, self.queue)
        ]

        self.active_profile_name = profile
        self.active_profile = self.profiles.get(profile, {}).get('server')
        if not self.active_profile:
            self.active_profile = create_default_profile()
            self.profiles[profile] = self.active_profile

        self.active_window = self.active_profile.active_window
        self.active_theme = self.active_profile.windows[self.active_window].theme

        self.server = web.Application()

    def active_theme_folder(self):
        return theme_settings_folder(self.active_theme)

    async def active_window_view(self, _):
        return web.FileResponse(os.path.join(self.active_theme_folder(), 'index.html'))

    async def active_websockets_view(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self.active_websockets.append(ws)

        async for msg in ws:
            logging.info(f'Received message {msg}')

        self.active_websockets.remove(ws)
        return ws

    async def send_messages(self):
        while True:
            message: Message = await self.queue.get()
            for socket in self.active_websockets:
                await socket.send_json(message.to_web())
            self.queue.task_done()

    async def start_background_tasks(self, app):
        app['sender'] = asyncio.create_task(self.send_messages())

    async def stop_background_tasks(self, app):
        app['sender'].cancel()
        await app['sender']

    def run_server(self):
        self.server.router.add_get('/', self.active_window_view)
        self.server.router.add_get('/ws', self.active_websockets_view)

        api = ServerAPI(self.active_profile, self)
        api_routes = api.get_handlers()
        for route, func in api_routes:
            self.server.router.add_get(f'/api/{route}', func)
        self.server.router.add_static('/', self.active_theme_folder(), append_version=True)

        self.server.on_startup.append(self.start_background_tasks)
        self.server.on_cleanup.append(self.stop_background_tasks)
        web.run_app(self.server, host=self.base_configuration.host, port=self.base_configuration.port)
