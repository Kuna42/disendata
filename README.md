## This is outdatet, visit https://codeberg.org/disendata
Now the future goal is to build an interface for many information services and implement a self designed connector.

----
----
# disendata
It is developed in [Python3.10](https://www.python.org/downloads/release/python-3104/)
(libraries: os, sockets, curses, sqlite, time, threading)
with the environment [PyCharm Community Edition](https://www.jetbrains.com/pycharm/download)
by [Kuna42](https://github.com/Kuna42)
under the licence [GNU GPLv3](https://opensource.org/licenses/GPL-3.0)
but the licence could be changed in later versions.
## Messenger
This Messenger is coded for local Networks without a server.
The idea behind this messenger is that nobody has to set up a 
server and everybody has only their own messenger programm on 
their local device.

### Issues

#### Goals for version 0.2

- [x] Database, which store messages
  - [ ] `~/.disendata` add and manage it
- [ ] Database for Chat and Member information
- [x] Eventhandler
- [ ] Network
  - [x] connect in LAN
  - [ ] connect in WAN
  - [x] IPv4
  - [ ] IPv6
  - [x] send messages
  - [ ] send files
  - [ ] VoIP
- [ ] Configuration file
  - [ ] Linux
  - [ ] Windows
  - [ ] Android
- [ ] TUI (Terminal User Interface) for all platforms (generic)
- [ ] TUI Linux
- [ ] TUI Windows
- [ ] GUI (Graphical User Interface) for all platforms (generic)
- [ ] GUI Linux
- [ ] GUI Android
- [ ] GUI Windows
- [ ] API
- [ ] Documentation
  - [ ] Why use disendata?
  - [ ] What is disendata?
  - [ ] Installation
  - [ ] How to compile it for yourself
  - [ ] How to use the API (with little examples)
- [ ] README.md consumer friendly
- [ ] Binaries
  - [ ] `.deb`
  - [ ] `.AppImage`
  - [ ] `.apk`
  - [ ] `.exe`
  - [ ] Repository to add on different Linux package manager
  - [ ] In F-Droid or some else Store for mobile devices (Android, Ubuntu Touch)

---

#### Goals for version 0.1:
- [ ] TUI Linux
  - [x] load messages
  - [x] save messages
  - [ ] add/edit member
  - [ ] add/edit chat
  - [ ] edit self
  - [x] type shown
  - [ ] copy and paste
  - [ ] start screen
  - [x] information field
  - [ ] decide field
  - [ ] write field
  - [x] configuration file
  - [x] resize terminal window
- [x] Database store messages
- [ ] Database store members and chats
  - [x] add chat
  - [ ] edit chat
  - [x] add member
  - [ ] edit member
- [x] Linux config file
- [ ] lite documentation
  - [ ] installation instruction 
- [ ] reread the code
- [ ] check issues


---
### Note:
This branch is not usable for testing the program. 
Later, after version 0.1 a develop branch will be used.
At the moment, there is no usable version of the programm.
