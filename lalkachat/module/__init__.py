from abc import ABC

from base import Base


class Module(Base, ABC):
    def __init__(self, profiles, active_profile, queue):
        super().__init__(profiles, active_profile)

        self.queue = queue
        self.profiles = profiles
        self.active_profile = active_profile

    def process_message(self, message):
        return message
