
# import

#from messenger.m_bc import ThreadObjectLibrary
class ThreadObjectLibrary:
    def __init__(self):
        self.network = None
        self.events = None
        self.interface = None
# imported


# global variable
global object_library
object_library = {}

global thread_objects
thread_objects = ThreadObjectLibrary()

global running
running = True


# variables
event_actions = {  # TODO could be better
    "msg_cmd": None,
    "msg_show": None,
    "msg_send": None,
    "msg_load": None,
    "chat_load": None,
    "chat_new": None,
    "member_new": None,
    "member_load": None,
    "if_decide": None,
    "self_stuff": None,
    "self_new": None,
    "version": None,
    "new_online": None,
    "update_db": None,
    "send_cmd": None,
}


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
