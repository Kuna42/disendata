#

# import
from threading import Thread
import socket
import os

from messenger.m_bc import Member, MemberGroup, Message, Chat
from messenger.static_variables import S
from messenger.database import DB


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

        if not (db_name.startswith("/") or db_name.startswith("~")):
            raise SyntaxError("db_name should be a complete path like /tmp/test.db")
        if db_name.split("/")[1] not in ["tmp", "home", "etc", ".disendata"]:
            # if the db was in a global directory or in a local like ".didendata"
            raise PermissionError(f"You can't open this database {db_name}")
        if not os.path.exists(db_name):
            if not os.path.exists("/".join(db_name.split("/")[:-1])):##
                raise FileNotFoundError("This File does not exists.")

        self.db = DB(db_name=db_name)

        self.sockets = socket.socket(
            socket.AF_INET,
            # socket.SOCK_STREAM,
            socket.SOCK_DGRAM
        )
        self.sockets.bind(("", S.PORT))

    @property
    def address(self):
        return self.ip, self.open_port

    @address.setter
    def address(self, value):
        self.ip = value[0]
        self.open_port = value[1]

    def new_member(self, ipv4):
        # self.sockets.connect((ipv4, S_PORT))
        connect_message = S.MSG_START["cmd"] + S.CMD["connection"]
        self.sockets.sendto(connect_message, (ipv4, S.PORT))  # TODO hier
        if True:  # TODO here must be checked if it is accept
            member = Member(address=(ipv4, S.PORT), identification_attribute="address")
            self.db.new_member(member)
            self.online_members.new_member(member)

    def send(self, message: Message):
        if not self.online_members.has_member(message.receiver):
            self.new_member(message.receiver.actual_ip)
        message_parts = len(message.text) // S.MSG_SIZE + 1
        for i in range(0, message_parts):
            part_of_parts = f"{i + 1}/{message_parts}"
            msg_size = S.MSG_SIZE - len(part_of_parts)
            self.sockets.sendto(
                S.MSG_START[message.m_type] + bytes(part_of_parts, "ascii")
                + S.MSG_START["separator"] + message.text[i * msg_size:(i + 1) * msg_size],
                message.receiver.address
            )

    def reversiere(self) -> Message:
        message_txt, address = self.sockets.recvfrom(self.message_size)
        if message_txt[2] not in S.MSG_START.items():
            return self.reversiere()  # vllt nicht gut
        # TODO das zusammenbauen von Nachrichten

        if message_txt[2] == S.MSG_START["cmd"]:
            cmd = message_txt[message_txt.index(S.MSG_START["separator"]):]
            self.msg_command(cmd)
        elif message_txt[2] == S.MSG_START["tmp"]:
            pass
        elif message_txt[2] == S.MSG_START["data"]:
            pass
        elif message_txt[2] == S.MSG_START["msg"]:
            message_txt = message_txt[2:]
            return Message(self.msg_encrypt(message_txt), chat=Chat(name=""),
                           to_member=Member(address=address, identification_attribute="address"))

        # self.check_message(Message(message_txt, Member(address)))
        return Message(message_txt, Member(address=address, identification_attribute="address"),
                       chat=Chat(name=""))  # TODO

    def msg_command(self, command: bytes):
        if command not in S.CMD:
            raise ValueError(f"This command \"{command}\" does not exists")
        if command == S.CMD["connection"]:
            pass

    def msg_encrypt(self, msg: bytes) -> bytes:
        return msg

    def check_message(self, message: Message) -> bool:
        pass

    def save_message(self, message: Message):
        self.db.new_message(message=message)

    def load_message(self, chat: Chat, timestamp=None):
        pass

    def send_message(self, message: Message):
        self.save_message(message)
        self.send(message)

    def run(self) -> None:
        while True:
            msg = self.reversiere()
