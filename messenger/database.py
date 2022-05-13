#!/usr/bin/env python3

# import
from sqlite3 import connect as sql_connect
from messenger.m_bc import Member, Chat, Message, MemberGroup
from messenger.variables import object_library

import os.path


# class
class DB:
    def __init__(self, db_name: str):
        """
        This Class is to store Chat, Member, Message in a database.

        :param db_name: The name of the database what will be used
        """
        self.__db_name = db_name
        if not os.path.exists(self.__db_name):  # TODO test if path is valid (should be in an upper class [actual is it in networkmessenger])
            self.create()

    def __execute(self, sql_instruction: str, param: tuple = None): # needed?
        with sql_connect(self.__db_name) as db:
            db_cursor = db.cursor()
            if param is not None:
                db_cursor.execute(sql_instruction, param)
            else:
                db_cursor.execute(sql_instruction)
            db.commit()

    def create(self):
        """
        Creates tables:

        m_member(id, name_self, name_given, name_generic, cryptic_hash)

        m_chats(table_name, display_name, info)

        m_chat_member(chat_table_name, member_id)

        :return:
        """
        sql_instructions = """
        CREATE TABLE IF NOT EXISTS m_member (
    
        id                         INTEGER PRIMARY KEY AUTOINCREMENT,
        name_self                  VARCHAR(15),
        name_given                 VARCHAR(15),
        name_generic               VARCHAR(15),
        cryptic_hash               VARCHAR(10)
        );
        
        CREATE TABLE IF NOT EXISTS m_chats (
        
        table_name                 VARCHAR(15) PRIMARY KEY,
        display_name               VARCHAR(15),
        info                       VARCHAR(30)
        
        );
        
        CREATE TABLE IF NOT EXISTS m_chat_member (
        
        chat_table_name            VARCHAR(15),
        member_id                  INTEGER
        
        );"""
        with sql_connect(self.__db_name) as db:
            db_cursor = db.cursor()
            db_cursor.executescript(sql_instructions)
            db.commit()

    def new_chat(self, chat: Chat):
        """
        Add a new table to the db with the name of the chat

        chat-name(msg_id, member_sender, member_receiver, timestamp, text)

        :param chat: Chat what should be added to the db
        :return:
        """
        if type(chat.name) is not str:
            raise ValueError("the table name should be a String")
        if not chat.name.isalnum():
            raise ValueError("the table name must be alpha numeric")
        sql_instructions = f"CREATE TABLE IF NOT EXISTS chat_{chat.name} (" \
                           f"msg_id                    INTEGER PRIMARY KEY AUTOINCREMENT," \
                           f"member_sender             INTEGER," \
                           f"member_receiver           INTEGER," \
                           f"timestamp                 DATE," \
                           f"text                      TEXT" \
                           f");"

        with sql_connect(self.__db_name) as db:
            db_cursor = db.cursor()
            db_cursor.execute(sql_instructions)

            sql_instructions = "INSERT INTO m_chats VALUES(?, ?, ?);"

            db_cursor.execute(sql_instructions, (chat.name, chat.display_name, chat.info))

            sql_instructions = "INSERT INTO m_chat_member VALUES(?, ?);"
            for member in chat.members.all_members():
                db_cursor.execute(sql_instructions, (chat.name, member.id_,))

            db.commit()

    def new_member(self, member: Member):
        """
        Add a new member to the db

        :param member: a Member as an object
        :return:
        """
        if member.name_generic == "":
            pass
        elif not member.name_generic.isalnum():
            raise ValueError("the member name must be alpha numeric")

        sql_instructions = "INSERT INTO m_member (name_self, name_given, name_generic, cryptic_hash) " \
                           "VALUES(?, ?, ?, ?);"

        with sql_connect(self.__db_name) as db:
            db_cursor = db.cursor()
            db_cursor.execute(sql_instructions,
                              (member.name_self, member.name_given, member.name_generic, member.crypt_hash))

            db.commit()

    def new_message(self, message: Message):
        """
        Add a Message to the table of the related chat

        :param message: a Message object
        :return:
        """
        if type(message.chat.name) is not str:
            raise ValueError("the message target table-name should be a String")
        if not message.chat.name.isalnum():
            raise ValueError("the target table-name must be alpha numeric")

        sql_instructions = f"INSERT INTO chat_{message.chat.name} " \
                           f"(member_sender, member_receiver, timestamp, text) VALUES(?, ?, ?, ?);"##

        with sql_connect(self.__db_name) as db:
            db_cursor = db.cursor()
            db_cursor.execute(sql_instructions,
                              (message.sender.id_, message.receiver.id_, message.timestamp, message.text))

            db.commit()

    def new_self(self, member: Member):
        """
        Add a Member which contains self in the database

        :param member: the Member what represent self
        :return:
        """
        sql_instructions = "SELECT id FROM m_member WHERE id = 0;"

        with sql_connect(self.__db_name) as db:
            db_cursor = db.cursor()
            db_cursor.execute(sql_instructions)
            request = db_cursor.fetchall()
            if len(request) != 1:  # if the table has not self
                sql_instructions = "INSERT INTO m_member VALUES(?, ?, ?, ?, ?);"
                db_cursor.execute(sql_instructions, (member.id_, member.name_self, member.name_given,
                                                     member.name_generic, member.crypt_hash))
            else:
                sql_instructions = "UPDATE m_member SET name_self = ?, name_given = ?, " \
                                   "name_generic = ?, cryptic_hash = ?" \
                                   "WHERE id = 0;"
                db_cursor.execute(sql_instructions, (member.name_self, member.name_given,
                                                     member.name_generic, member.crypt_hash))

    def has_chat(self, chat: Chat) -> bool:
        """
        Check, if the Chat exists in the database

        :param chat: the .name is necessary for finding the right chat
        :return:
        """
        sql_instructions = "SELECT table_name FROM m_chats WHERE table_name = ?;"

        with sql_connect(self.__db_name) as db:
            db_cursor = db.cursor()
            db_cursor.execute(sql_instructions, (chat.name,))
            request = db_cursor.fetchall()
        return bool(request)

    def has_member(self, member: Member) -> bool:
        """
        Check, if the Member exists in the database

        :param member: the id_ is necessary to find the member
        :return:
        """
        sql_instructions = "SELECT * FROM m_chats WHERE name_self = ? OR name_given = ? OR name_generic = ?;"
        with sql_connect(self.__db_name) as db:
            db_cursor = db.cursor()
            db_cursor.execute(sql_instructions, (member.name_self, member.name_given, member.name_generic))
            request = db_cursor.fetchall()
            if request: # should be better
                return True
        return False

    def member_in_chats(self, member: Member) -> [Chat]:
        """
        Select every Chat, where the member is a part of

        :param member: member what is the search-key
        :return: return a list of Chats
        """
        sql_instructions = "SELECT * FROM (SELECT chat_table_name FROM m_chat_member WHERE member_id = ?) " \
                           "LEFT JOIN m_chats"

        with sql_connect(self.__db_name) as db:
            db_cursor = db.cursor()
            db_cursor.execute(sql_instructions, (member.id_,))
            request = db_cursor.fetchall()

        chat_list = []
        for chat in request:
            chat_list.append(Chat(name=chat[0]))
        return chat_list

    def read_message(self, chat: Chat, _timestamp) -> Message or None:
        """
        Give a Message or None based on a timestamp
        :param chat: in what Chat should be the message
        :param _timestamp: the date of the receiving
        :return: a Message or None if none message with the timestamp was found
        """
        if not chat.name.isalnum():
            raise ValueError("The name of the Chat should be Alpha Numeric")
        sql_instructions = f"SELECT * FROM chat_{chat.name} WHERE timestamp = ?;"

        with sql_connect(self.__db_name) as db:
            db_cursor = db.cursor()
            db_cursor.execute(sql_instructions, (_timestamp,))
            request = db_cursor.fetchall()
        if not request:
            return None
        request = request[0]  # only the first message with this timestamp
        return Message(text=request[4], sender=Member(id_=request[1]), to_member=Member(id_=request[2]),
                       chat=chat, _timestamp=request[3])

    def read_chat(self, chat: Chat, count: int = 20) -> [Message]:
        """
        Read a Chat and returns all (counted) Messages, the newest is the last

        :param chat: the Chat what are read
        :param count: how many Messages should be returned
        :return: returned a list of Messages
        """
        if not chat.name.isalnum():
            raise ValueError("The name of the Chat should be Alpha Numeric")
        sql_instructions = f"SELECT * FROM chat_{chat.name} ORDER BY timestamp DESC LIMIT {count};"

        with sql_connect(self.__db_name) as db:
            db_cursor = db.cursor()
            db_cursor.execute(sql_instructions)
            request = db_cursor.fetchall()
        if not request:
            return []
        message_list = []
        for message in request:
            message_list.append(Message(text=message[4], sender=Member(id_=message[1]),
                                        to_member=Member(id_=message[2]), chat=chat, _timestamp=message[3]))
        message_list.reverse()
        return message_list

    def open_chats(self) -> [Chat]:
        """
        Gives a list of all existing Chats, this is at the beginning useful

        :return: a list of all Chats
        """
        sql_instructions = "SELECT table_name, display_name, info FROM m_chats;"
        with sql_connect(self.__db_name) as db:
            db_cursor = db.cursor()
            db_cursor.execute(sql_instructions)
            request = db_cursor.fetchall()
            sql_instructions = "SELECT * FROM m_chat_member;"
            db_cursor.execute(sql_instructions)
            request_2 = db_cursor.fetchall()

        chat_list = []
        for chat in request:
            member_list = []
            for m_chat_member in request_2:
                if m_chat_member[0] == chat[0]:
                    member_list.append(Member(id_=m_chat_member[1]))
            chat_list.append(Chat(name=chat[0], display_name=chat[1], info=chat[2],
                                  members=MemberGroup(*member_list)))
        return chat_list

    def open_members(self) -> [Member]:
        """
        Gives a list of all registered members, this is at the beginning useful

        :return: a list of all members
        """
        sql_instructions = "SELECT * FROM m_member;"

        with sql_connect(self.__db_name) as db:
            db_cursor = db.cursor()
            db_cursor.execute(sql_instructions)
            request = db_cursor.fetchall()

        member_list = []
        for member in request:
            member_list.append(Member(id_=member[0], name_self=member[1], name_given=member[2],
                                      name_generic=member[3], cryptic_hash=member[4]))
        return member_list

    def update_chat(self): ...  # TODO
    def update_member(self): ...  # TODO

    def update(self):
        """
        append the members and chats,
        cut to the database to a smaller one if possible

        :return:
        """
        for member in object_library[Member]:
            if not self.has_member(member=member):
                self.new_member(member=member)

        for chat in object_library[Chat]:
            if not self.has_chat(chat=chat):
                self.new_chat(chat=chat)

        sql_instructions = "VACUUM;"
        with sql_connect(self.__db_name) as db:
            db_cursor = db.cursor()
            db_cursor.execute(sql_instructions)
            db.commit()
