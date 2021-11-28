#!/usr/bin/env python3

# import
from messenger.variables import thread_objects, information, fill_event_actions
from messenger.events import Eventmanager
from messenger.interface.universal_terminal import Terminal
from messenger.network_messenger import NetworkMessenger
from messenger.m_bc import Messenger

thread_objects.events = Eventmanager()
thread_objects.interface = Terminal()
thread_objects.network = NetworkMessenger(thread_objects.interface.get_db_name())


fill_event_actions()


# variables
__name = "messenger"
__version = "0.0.1"
__author = "Kuna42"
__www = "kuna42@web.de"
__copyright = "(C) 2021"
__licence = "MIT"


if __name__ == "__main__":
    print(information())
    messenger = Messenger()
    messenger.start()
