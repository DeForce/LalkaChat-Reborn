from queue import Queue

from dotmap import DotMap

from service import Service


def config():
    return DotMap({

    })


class TwitchTV(Service):
    def __init__(self, profiles, active_profile, queue: Queue):
        super().__init__(profiles, active_profile, queue)

    def get_default_configuration(self):
        pass
