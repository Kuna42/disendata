#

# import
from threading import Thread

from messenger.m_abc import Event
from messenger.m_bc import Message, Chat, Member
from messenger.variables import running, event_actions, thread_objects


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
                event_actions[type(event)](**event.content)
                if event.done() or True:#TODO recode
                    self.events.remove(event)


# events

class EventUpdateDB(Event):
    def __init__(self):
        super(EventUpdateDB, self).__init__()

    @property
    def content(self):
        return {}


class EventVersion(Event):
    def __init__(self):
        super(EventVersion, self).__init__()

    @property
    def content(self):
        return {}


class EventInterfaceDecide(Event):
    def __init__(self, decide_txt: str, decide_options: dict):
        super(EventInterfaceDecide, self).__init__()
        self.decide_txt = decide_txt
        self.decide_options = decide_options

    @property
    def content(self):
        return {
            "decide_options": self.decide_options,
            "decide_txt": self.decide_txt,
        }


class _EventMember(Event):
    def __init__(self, member: Member):
        super(_EventMember, self).__init__()
        self.member = member

    @property
    def content(self):
        return {
            "member": self.member,
        }


class _EventMessage(Event):
    def __init__(self, message: Message):
        super(_EventMessage, self).__init__()
        self.message = message

    @property
    def content(self):
        return {
            "message": self.message,
        }


class EventSelfUpdate(_EventMember):
    pass


class EventSend(_EventMessage):
    pass


class EventMsgCmd(_EventMessage):
    pass


class EventMsgShow(_EventMessage):
    pass


class EventMsgSend(_EventMessage):
    pass


class EventMsgLoad(Event):
    def __init__(self, chat: Chat, _timestamp: str):
        super(EventMsgLoad, self).__init__()
        self.chat = chat
        self._timestamp = _timestamp

    @property
    def content(self):
        return {
            "chat": self.chat,
            "_timestamp": self._timestamp,
        }


class EventNewMember(Event):
    def __init__(self, ipv4: str):
        super(EventNewMember, self).__init__()
        self.ipv4 = ipv4

    @property
    def content(self):
        return {
            "ipv4": self.ipv4,
        }
