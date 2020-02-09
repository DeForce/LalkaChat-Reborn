import threading
import time

from message import Message
from service import Service


class SampleService(Service):
    def __init__(self, profiles, active_profile, queue):
        super().__init__(profiles, active_profile, queue)

        thread = threading.Thread(target=self.send_loop, daemon=True)
        thread.start()

    def save(self):
        return {}

    def send_loop(self):
        loop = 0
        while True:
            message = Message(text=f'Please Ignore {loop}', channel='SampleChannel', username='LalkaNet')
            self.send_message(message)
            loop += 1
            time.sleep(1)
