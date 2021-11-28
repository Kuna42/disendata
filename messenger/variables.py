
# import

#from messenger.m_bc import ThreadObjectLibrary
class ThreadObjectLibrary:
    def __init__(self):
        self.network = None
        self.events = None
        self.interface = None

    def start(self):
        self.network.name = "network-Thread"
        self.events.name = "event-Thread"
        self.interface.name = "interface-Thread"
        self.network.start()
        self.events.start()
        self.interface.start()


# imported

class Running:
    def __init__(self, __running: bool = True):
        self.running = __running

    def __bool__(self):
        return self.running

    def stop(self):
        self.running = False
        # TODO add stopping all threads

# global variable
global object_library
object_library = {}

global thread_objects
thread_objects = ThreadObjectLibrary()

global running
running = Running()  # could be different


# variables
event_actions = {}


def fill_event_actions():  # TODO could be better
    from messenger.events import (EventVersion, EventUpdateDB, EventSelfUpdate,
                                  EventInterfaceDecide, EventSend, EventNewMember,
                                  EventMsgCmd, EventMsgShow, EventMsgSend, EventMsgLoad)

    event_actions.clear()
    event_actions.update({
        EventMsgCmd: thread_objects.network.msg_command,
        EventMsgShow: thread_objects.interface.show_msg,
        EventMsgSend: thread_objects.network.send_message,
        EventMsgLoad: thread_objects.network.load_message,
        "chat_load": None,
        "chat_new": None,
        "member_new": None,
        "member_load": None,
        EventInterfaceDecide: thread_objects.interface.decide,  # decide_options: dict of str: method
        "self_stuff": None,
        EventSelfUpdate: None,
        EventVersion: information,
        EventNewMember: thread_objects.network.new_member,
        EventUpdateDB: None,
        EventSend: thread_objects.network.send,
    })


connection = [("", 36000)]


# private variables
__name = "disendata_messenger"
__version = "0.0.1"
__author = "Kuna42"
__www = "kuna42@web.de"
__copyright = "(C) 2021"
__licence = "MIT"


def information() -> str:
    """
    Returns all static information in a string

    :return: str
    """
    return (__name + "-" + __version + " written by " + __author +
            " under the licence " + __licence + " " + __copyright +
            ". Can be contacted on " + __www + ".")


# class
class S:
    """
    Class for static standard variables
    """
    PORT = 36000
    SEND_SIZE = 1024
    MSG_SIZE = 1021  # S_SEND_SIZE - len(S_MSG_START["anything"]) - len(S_MSG_START["separator"]
    MSG_START = {  # every option should have the same length of 2
        "msg": b"m\t",  # is used to tell, this was a simple message
        "cmd": b"c\t",  # is used for commands (includes new connections)
        "tmp": b"t\t",  # tells that this are temporary Data
        "data": b"d\t",  # is used for data packs
        "separator": b";",  # is used to separate the indicator from the message
    }
    CMD = {  # commands as a part of every message
        "connection": b"c",
        "connection accept": b"a",
        "information": b"i",
        "close": b"\n",
    }


if __name__ == "__main__":
    print("Variables: ...")
