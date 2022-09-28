#

# import
import abc
from threading import Thread

from messenger.m_abc import Event
from messenger.m_bc import Message, Chat, Member
from messenger.variables import running, thread_objects, information


# classes
class Eventmanager(Thread):
    def __init__(self):
        """
        Create an Eventmanager, there you can add an event, see Event class
        """
        super(Eventmanager, self).__init__()
        self.events = []

    def append(self, event: Event):
        """
        append an Event to an event list
        :param event:
        :return:
        """
        self.events.append(event)

    def run(self) -> None:
        """
        cycle through all events and execute them
        :return:
        """
        while running:
            for event in self.events[:]:
                event.execute()
                if event.done():
                    self.events.remove(event)

    def stop(self):
        """
        stopped the program
        :return:
        """
        pass


# events
class EventUpdateDB(Event):
    def __init__(self):
        super(EventUpdateDB, self).__init__()

    def command(self) -> None:
        thread_objects.network.db.update()


class EventVersion(Event):  # todo could be removed
    def __init__(self):
        super(EventVersion, self).__init__()

    def command(self) -> None:
        information()


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

    def command(self) -> None:
        thread_objects.interface.decide(decide_options=self.decide_options, decide_txt=self.decide_txt)


class _EventMember(Event, abc.ABC):
    def __init__(self, member: Member):
        super(_EventMember, self).__init__()
        self.member = member

    @property
    def content(self):
        return {
            "member": self.member,
        }


class _EventMessage(Event, abc.ABC):
    def __init__(self, message: Message):
        super(_EventMessage, self).__init__()
        self.message = message

    @property
    def content(self):
        return {
            "message": self.message,
        }


class EventSelfUpdate(_EventMember):
    def command(self) -> None:
        # todo add selfupdate
        pass


class EventSend(_EventMessage):
    def command(self) -> None:
        thread_objects.network.send(message=self.message)


class EventMsgCmd(_EventMessage):
    def command(self) -> None:
        thread_objects.network.msg_command(message=self.message)


class EventMsgShow(_EventMessage):
    def command(self) -> None:
        thread_objects.interface.show_msg(message=self.message)


class EventMsgSend(_EventMessage):
    def command(self) -> None:
        thread_objects.network.send_message(message=self.message)


class EventMsgLoad(Event):  # todo check if this is obsolete
    def __init__(self, chat: Chat, timestamp: str):
        super(EventMsgLoad, self).__init__()
        self.chat = chat
        self.timestamp = timestamp

    @property
    def content(self):
        return {
            "chat": self.chat,
            "_timestamp": self.timestamp,
        }

    def command(self) -> None:
        thread_objects.network.load_message(chat=self.chat, timestamp=self.timestamp)


class EventNewMember(_EventMember):
    def command(self) -> None:
        thread_objects.network.new_member(member=self.member)
        thread_objects.network.db.new_member(member=self.member)


class EventNewChat(Event):
    def __init__(self, chat: Chat):
        super(EventNewChat, self).__init__()
        self.chat = chat

    @property
    def content(self):
        return {
            "chat": self.chat
        }

    def command(self) -> None:
        thread_objects.network.db.new_chat(chat=self.chat)


class EvenLoadChat(Event):  # too check if this is valid or obsolete
    def command(self) -> None:
        thread_objects.network.db.read_chat()

