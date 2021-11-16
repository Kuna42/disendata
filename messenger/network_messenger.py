#

# import
from threading import Thread
import socket
import os

from messenger.m_bc import Member, MemberGroup, Message
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

        if not db_name.startswith("/"):
            raise SyntaxError("db_name should be a complete path like /tmp/test.db")
        if db_name.split("/")[1] not in ["tmp", "home", "etc"]:
            raise PermissionError(f"You can't open this database {db_name}")
        if not os.path.exists(db_name):
            if not os.path.exists("/".join(db_name.split("/")[:-1])):
                raise FileNotFoundError("This File does not exists.")

        self.db_name = db_name
        self.db = sql_connect(self.db_name)

        self.chats = {
            # "Member_name": ""
        }
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
        member = Member((ipv4, S.PORT))
        # self.sockets.connect((ipv4, S_PORT))
        connect_message = S.MSG_START["cmd"] + S.CMD["connection"]
        self.sockets.sendto(connect_message, (ipv4, S.PORT))  # TODO hier
        self._db_new_member(member)
        member = self._db_load_member(member.name)
        if True:
            self.online_members.new_member(member)

    def send(self, message: Message):
        if not self.online_members.has_member(message.receiver.name):
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
            return Message(self.msg_encrypt(message_txt), Member(address))

        # self.check_message(Message(message_txt, Member(address)))
        return Message(message_txt, Member(address))

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
        pass

    def load_message(self):
        pass

    def send_message(self, message: Message):
        self.save_message(message)
        self.send(message)

    def _db_create(self):
        sql_instructions = """
        CREATE TABLE IF NOT EXISTS m_member (

        id                         INTEGER PRIMARY KEY,
        name_self                  VARCHAR(15),
        name_given                 VARCHAR(15),
        name_generic               VARCHAR(15),
        cryptic_hash               VARCHAR(10)
        );"""
        db = self.db.cursor()
        db.execute(sql_instructions)
        self.db.commit()

    def _db_new_table(self, table_name: str):  # TODO may be removed
        if type(table_name) is not str:
            raise ValueError("the table name should be a String")
        if not table_name.isalnum():
            raise ValueError("the table name must be alpha numeric")
        sql_instructions = f"CREATE TABLE IF NOT EXISTS {table_name} ("

    def _db_has_member(self, member: Member) -> bool:
        pass

    def _db_new_member(self, member: Member):
        if self._db_has_member(member):
            return

        db = self.db.cursor()

        sql_instructions = "INSERT OR IGNORE INTO m_member VALUES(?, ?, ?, ?, ?)"
        member_values = ()
        db.execute(sql_instructions, member_values)
        table_name = ""
        sql_instructions = f"CREATE TABLE IF NOT EXISTS {table_name} (" \
                           f"" \
                           f"message_id      INTEGER PRIMARY KEY," \
                           f"message         STRING," \
                           f"timestamp       DATE" \
                           f");"
        db.execute(sql_instructions)
        self.db.commit()

    def _db_load_member(self, name: str) -> Member:
        pass

    def run(self) -> None:
        while True:
            msg = self.reversiere()
