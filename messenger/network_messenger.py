#

# import
from threading import Thread
import socket
import os

from messenger.m_bc import Member, MemberGroup, Message, Chat, Filecheck
from messenger.variables import S, running, connection
from messenger.events import EventInterfaceDecide, EventMsgCmd, EventMsgShow
from messenger.database import DB


# variables

# classes
class NetworkMessenger(Thread):
    def __init__(self, db_name: str):
        Thread.__init__(self)
        super(Thread, self).__init__()
        self.ip = ""
        self.open_port = S.PORT
        self.network_name = ""
        self.online_members = MemberGroup()
        self.message_size = S.SEND_SIZE
        self.tmp_message_storage = {
            # here should be Messages, where was not complete or was a request
        }

        if not Filecheck.file(db_name):
            raise FileNotFoundError("An unknown Error occurred in \'disendata/messenger/network_messenger\'.")

        self.db = DB(db_name=db_name)
        self.db.open_members()
        self.db.open_chats()

        self.address = connection[0]

        self.sockets = socket.socket(
            socket.AF_INET,
            # socket.SOCK_STREAM,
            socket.SOCK_DGRAM
        )
        self.sockets.bind(self.address)

    @property
    def address(self):
        return self.ip, self.open_port

    @address.setter
    def address(self, value):
        self.ip = value[0]
        self.open_port = value[1]

    def new_member(self, member: Member):
        connect_message = S.MSG_START["cmd"] + S.CMD["connection"]
        self.sockets.sendto(connect_message, member.address)  # TODO hier
        if True:  # TODO here must be checked if it is accept
            self.online_members.new_member(member)

    def send(self, message: Message):
        if not self.online_members.has_member(message.receiver):
            self.new_member(message.receiver)
        if message.m_type == "cmd":
            self.sockets.sendto(
                S.MSG_START["cmd"] + message.text,
                message.receiver.address
            )
            return
        message_parts = len(message.text) // S.MSG_SIZE + 1
        for i in range(0, message_parts):
            message_text = (S.MSG_START[message.m_type] + bytes(f"{i + 1}/{message_parts}", "ascii")
                            + S.MSG_START["separator"] + bytes(message.chat.name, "ascii")
                            + S.MSG_START["separator"])
            msg_size = S.MSG_SIZE - len(message_text)
            self.sockets.sendto(
                message_text + message.text[i * msg_size:(i + 1) * msg_size],
                message.receiver.address
            )

    def receive(self) -> Message:
        message_txt, address = self.sockets.recvfrom(self.message_size)
        #print(message_txt)
        if message_txt[:2] not in S.MSG_START.values():
            #print("+++")
            #print(message_txt)
            #print(message_txt[:2])##
            #print(S.MSG_START.values())
            #print(message_txt[:2] in S.MSG_START.values())
            return
            #return self.reversiere()  # vllt nicht gut
        # TODO das zusammenbauen von Nachrichten

        if message_txt[:2] == S.MSG_START["cmd"]:

            cmd = message_txt[message_txt.find(S.MSG_START["separator"]):]
            self.msg_command(Message(text=message_txt[2:],
                                     sender=Member(address=address, identification_attribute="address"),##
                                     chat=Chat(name="")))
            return
        elif message_txt[:2] == S.MSG_START["tmp"]:  # TODO
            pass
        elif message_txt[:2] == S.MSG_START["data"]:  # TODO
            pass
        elif message_txt[:2] == S.MSG_START["msg"]:
            message_txt = message_txt.split(S.MSG_START["separator"])
            message = Message(text=self.msg_encrypt(message_txt[2]), chat=Chat(name=message_txt[1]),
                              sender=Member(address=address, identification_attribute="address"))##
            self.save_message(message=message)
            EventMsgShow(message=message)
            return message

        # self.check_message(Message(message_txt, Member(address)))
        message = Message
        def nix(): # TODO this is only tmp
            print("nix")
            return
        EventInterfaceDecide(decide_txt=f"{message_txt}", decide_options={"nix": nix}) # tmp should be removed
        return Message(message_txt, Member(address=address, identification_attribute="address"),
                       chat=Chat(name=""))  # TODO

    def msg_command(self, message: Message):
        command = message.text
        if command[0:1] not in S.CMD.values():
            raise ValueError(f"This command \"{command}\" does not exists")
        # check, what command it is, todo can be in 3.10 with match case
        if command == S.CMD["connection"]:

            def yes():
                EventMsgCmd(message=Message(text=S.CMD["connection accept"], chat=message.chat, m_type="cmd",
                                            sender=message.receiver, to_member=message.sender))

            def no():
                return

            EventInterfaceDecide(decide_txt=f"Connect to {message.sender.address[0]}? (yes/no)",
                                 decide_options={"yes": yes, "no": no},)  # TODO

        elif command == S.CMD["connection accept"]:
            self.online_members.new_member(member=message.sender)

        elif command == S.CMD["information"]:
            self.send(message=Message(sender=Member(id_=0), to_member=message.sender, chat=message.chat,
                                      m_type="data", text=b""))

        elif command == S.CMD["close"]:
            self.online_members.group.remove(message.receiver)

        elif command == S.CMD["stop"]:
            if message.sender is Member(id_=0):
                return

    def msg_encrypt(self, msg: bytes) -> bytes:
        return msg

    def check_message(self, message: Message) -> bool:
        pass

    def save_message(self, message: Message):
        self.db.new_message(message=message)

    def load_message(self, chat: Chat, timestamp=None):
        self.db.read_chat(chat=chat, count=10)  # todo this have to be recoded

    def send_message(self, message: Message):
        self.save_message(message)
        for member in message.chat.members.all_members():
            message.receiver = member
            self.send(message)

    def run(self) -> None:
        while running:
            msg = self.receive()
        self.db.update()

    def stop(self) -> None:
        self.send(Message(text=S.CMD["stop"],
                          sender=Member(id_=0),
                          chat=Chat(name="cmd"),
                          to_member=Member(id_=0),
                          m_type="cmd"))
