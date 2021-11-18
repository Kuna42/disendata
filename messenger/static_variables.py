
# import

# variables
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
    CMD = {
        "connection": b"c",
        "connection accept": b"a",
        "information": b"i",
        "close": b"\n",
    }
