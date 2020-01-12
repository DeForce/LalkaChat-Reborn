

class Module:
    def __init__(self, profiles, active_profile, queue):
        self.queue = queue
        self.profiles = profiles
        self.active_profile = active_profile

    def process_message(self, message):
        return message
