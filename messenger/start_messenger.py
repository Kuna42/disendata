#!/usr/bin/env python3

# import
from messenger.variables import thread_objects, information
from messenger.events import Eventmanager
from messenger.interface.universal_terminal import Terminal
from messenger.network_messenger import NetworkMessenger


thread_objects.events = Eventmanager()
thread_objects.interface = Terminal()
thread_objects.network = NetworkMessenger(thread_objects.interface.get_db_name())


def fill_event_actions():  # TODO could be better
    from messenger.variables import event_actions

    event_actions["msg_cmd"] = thread_objects.network.msg_command
    event_actions["msg_show"] = thread_objects.interface.show_msg
    event_actions["msg_send"] = thread_objects.network.send_message
    event_actions["msg_load"] = thread_objects.network.load_message
    event_actions["chat_load"] = None
    event_actions["chat_new"] = None
    event_actions["member_new"] = None
    event_actions["member_load"] = None
    event_actions["if_decide"] = thread_objects.interface.decide
    event_actions["self_stuff"] = None
    event_actions["self_new"] = None
    event_actions["version"] = information
    event_actions["new_online"] = thread_objects.network.new_member
    event_actions["update_db"] = None
    event_actions["send_cmd"] = thread_objects.network.send


fill_event_actions()

if __name__ == "__main__":
    from messenger.m_bc import Messenger

# variables
__name = "messenger"
__version = "0.0.1"
__author = "Kuna42"
__www = "kuna42@web.de"
__copyright = "(C) 2021"
__licence = "MIT"


def information():
    return __name + "-" + __version + " written by " + __author + \
           " under the licence " + __licence + " " + __copyright + \
           ". Can be contacted on " + __www + "."


if __name__ == "__main__":
    print(information())
    messenger = Messenger()
    messenger.start()
