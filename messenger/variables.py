
# import

# from messenger.m_bc import ThreadObjectLibrary
import os.path


class ThreadObjectLibrary:  # todo redundanz in m_bc.py
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

    def stop(self):
        self.network.stop()
        self.events.stop()
        self.interface.stop()


# imported

class Running:
    def __init__(self, __running: bool = True):
        self.running = __running

    def __del__(self):
        print(information()) # this is possible not necessary

    def __bool__(self):
        return self.running

    def stop(self):
        self.running = False
        thread_objects.stop()
        print(information())
        #raise KeyboardInterrupt("Finished, but this Code need to rewritten")
        # TODO add stopping all threads


# global variable
global object_library
object_library = {}

global thread_objects
thread_objects = ThreadObjectLibrary()

global running
running = Running()  # could be different


# variables
# event_actions = {}  # TODO change this, this have to be in the events.execute..


# def fill_event_actions():  # TODO could be better
#     from messenger.events import (EventVersion, EventUpdateDB, EventSelfUpdate,
#                                   EventInterfaceDecide, EventSend, EventNewMember,
#                                   EventMsgCmd, EventMsgShow, EventMsgSend, EventMsgLoad,
#                                   EventNewChat)
#
#     # event_actions.clear() not needed anymore
#     event_actions.update({
#         #EventMsgCmd: thread_objects.network.msg_command,
#         #EventMsgShow: thread_objects.interface.show_msg,
#         #EventMsgSend: thread_objects.network.send_message,
#         #EventMsgLoad: thread_objects.network.load_message,
#         #"chat_load": thread_objects.network.db.read_chat,
#         #EventNewChat: thread_objects.network.db.new_chat,
#         "member_new": None,
#         "member_load": None,
#         #EventInterfaceDecide: thread_objects.interface.decide,  # decide_options: dict of str: method
#         "self_stuff": None,
#         #EventSelfUpdate: None,
#         #EventVersion: information,
#         #EventNewMember: thread_objects.network.new_member,
#         #EventUpdateDB: thread_objects.network.db.update,
#         #EventSend: thread_objects.network.send,
#     })


connection = [("", 36000)]


# private variables
__name = "disendata_messenger"
__version = "0.0.2"
__author = "Kuna42"
__www = "kuna42@web.de"
__copyright = "(C) 2022"
__licence = "GNU GPLv3"


def information(_type=str) -> str or tuple or dict:
    """
    Returns all static information
    :param _type  decide if it returned
    as a string or as a tuple or as a dict

    :return: string or tuple or dictionary
    """
    if _type is str:
        return (__name + "-" + __version +
                " written by " + __author +
                " under the licence " + __licence +
                " " + __copyright +
                ". Can be contacted on <" + __www + ">.")
    elif _type is tuple:
        return __name, __version, __author, __www, __copyright, __licence
    elif _type is dict:
        return {
            "name": __name,
            "version": __version,
            "author": __author,
            "www": __www,
            "copyright": __copyright,
            "licence": __licence
        }


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
    MSG_INTERNAL_SEPERATOR = b";"  # todo replace this with the "old" seperator
    CMD = {  # commands as a part of every message
        "connection": b"c",
        "connection accept": b"a",
        "information": b"i",
        "close": b"\n",
        "stop": b"S",
    }
    TIMESTAMP_FORMAT = "%Y-%m-%d_%H:%M:%S"
    TIMESTAMP_FORMAT_2 = "%H:%M:%S - %d.%m.%Y"


class LinuxS:
    """
    Class for standard variables what are only in Linux
    """
    CONFIG_FILE_PATH = os.path.expanduser("~") + "/.config/disendata/"
    CONFIG_FILE_NAME = CONFIG_FILE_PATH + "terminal.config"
    LANGUAGE_FILE_PATH = CONFIG_FILE_PATH + "/language/"
    LANGUAGE_FILE_NAMES = {
        "de_DE",
        "en_UK",
        "en_US",
    }
    DISENDATA_PATH = "../"  # TODO this must be correct

    TEMPLATE_CONFIG_FILE_PATH = DISENDATA_PATH + "messenger/interface/Linux/template/configuration/terminal.config"

    DATA_PATH = os.path.expanduser("~") + "/.disendata/"
    DATA_LOG_FILE = DATA_PATH + "log/"

    LANGUAGE_DICTIONARY_PATH = "/usr/share/dict/"
    LANGUAGE_DICTIONARY_NAMES = {
        "de_DE": ("ngerman", "ogerman"),
        "en_UK": ("british-english",),
        "en_US": ("american-english",),
        None: ("words",)
    }


if __name__ == "__main__":
    print("Variables: ...")
