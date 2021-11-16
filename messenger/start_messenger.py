#!/usr/bin/env python3

# import
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
