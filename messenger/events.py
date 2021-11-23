#

# import
from threading import Thread

from messenger.m_bc import Event
from messenger.variables import running, event_actions


# classes
class Eventmanager(Thread):
    def __init__(self):
        super(Eventmanager, self).__init__()
        self.events = []

    def append(self, event: Event):
        self.events.append(event)

    def run(self) -> None:
        while running:
            for event in self.events[:]:
                event_actions[event.action_type](**event.content)
                if event.done():
                    self.events.remove(event)
