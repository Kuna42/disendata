#!/usr/bin/env python3

# import
import os
import logging
import time

from messenger.variables import thread_objects, information, LinuxS
from messenger.events import Eventmanager
from messenger.network_messenger import NetworkMessenger
from messenger.m_bc import Messenger

# for logging set variables
logging.basicConfig(
    filename=LinuxS.DATA_LOG_PATH + time.strftime("%Y-%m-%d-%H-%M-%S") + ".log",
    filemode="w",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG
)

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


if __name__ == "__main__":
    logging.info("Starting Messenger ...")
    messenger = Messenger()
    try:
        messenger.start()
    except Exception as error:
        del thread_objects.interface
        print(error)
    #print(information())
