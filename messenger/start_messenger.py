#!/usr/bin/env python3

# import
import os

from messenger.variables import thread_objects, information, fill_event_actions
from messenger.events import Eventmanager
from messenger.network_messenger import NetworkMessenger
from messenger.m_bc import Messenger

thread_objects.events = Eventmanager()

os_name = os.uname().sysname
if os_name == "Linux":
    from messenger.interface.Linux.terminal import Terminal as Interface
elif os_name == "Windows":
    from messenger.interface.Windows.terminal import Terminal as Interface
else:
    from messenger.interface.universal_terminal import Terminal as Interface
thread_objects.interface = Interface()

thread_objects.network = NetworkMessenger(thread_objects.interface.get_db_name())


fill_event_actions()


# variables
__name = "messenger"
__version = "0.0.2"
__author = "Kuna42"
__www = "kuna42@web.de"
__copyright = "(C) 2021"
__licence = "MIT"


if __name__ == "__main__":
    messenger = Messenger()
    try:
        messenger.start()
    except Exception as error:
        del thread_objects.interface
        print(error)
    #print(information())
