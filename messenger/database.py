#!/usr/bin/env python3

# import
from sqlite3 import connect as sql_connect
from messenger.m_bc import Member, Chat, Message

import os


# class
class DB:
    def __init__(self, db_name: str):
        self.__db_name = db_name
        if not os.path.exists(self.__db_name):  # TODO test if path is valid
            self.create()

    def __execute(self, sql_instruction: str, param: tuple = None):
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

        :param chat: Chat what should be added to the db
        :return:
        """
        if type(chat.name) is not str:
            raise ValueError("the table name should be a String")
        if not chat.name.isalnum():
            raise ValueError("the table name must be alpha numeric")
        sql_instructions = f"CREATE TABLE IF NOT EXISTS {chat.name} (" \
                           f"msg_id                    INTEGER PRIMARY KEY AUTOINCREMENT," \
                           f"member                    INTEGER," \
                           f"timestamp                 DATE," \
                           f"text                      TEXT" \
                           f");"

        with sql_connect(self.__db_name) as db:
            db_cursor = db.cursor()
            db_cursor.execute(sql_instructions)

            sql_instructions = "INSERT INTO m_chats VALUES(?, ?, ?);"

            db_cursor.execute(sql_instructions, (chat.name, chat.display_name, chat.info))

            sql_instructions = "INSERT INTO m_chat_member VALUES(?, ?);"
            for member in chat.member:  # TODO could be a MessageGroup from class Chat
                db_cursor.execute(sql_instructions, (chat.name, member.id,))

            db.commit()

    def new_member(self, member: Member):
        """
        Add a new member to the db

        :param member: a Member as a object
        :return:
        """
        if not member.name_given.isalnum():
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
        if type(message.chat) is not str:
            raise ValueError("the message target table-name should be a String")
        if not message.chat.name.isalnum():
            raise ValueError("the target table-name must be alpha numeric")

        sql_instructions = f"INSERT INTO {message.chat} VALUES(?, ?, ?);"

        with sql_connect(self.__db_name) as db:
            db_cursor = db.cursor()
            db_cursor.execute(sql_instructions,
                              (message.receiver, message.timestamp, message.text))

            db.commit()

    def new_self(self, member: Member):
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
        sql_instructions = "SELECT table_name FROM m_chats WHERE table_name = ?;"

        with sql_connect(self.__db_name) as db:
            db_cursor = db.cursor()
            db_cursor.execute(sql_instructions, (chat.name,))
            request = db_cursor.fetchall()
            if request:
                return True
        return False

    def has_member(self, member: Member) -> bool:
        sql_instructions = "SELECT * FROM m_chats WHERE name_self = ? OR name_given = ? OR name_generic = ?;"
        with sql_connect(self.__db_name) as db:
            db_cursor = db.cursor()
            db_cursor.execute(sql_instructions, (member.name_self, member.name_given, member.name_generic))
            request = db_cursor.fetchall()
            if request: # should be better
                return True
        return False

    def member_in_chats(self, member: Member) -> [Chat]:
        sql_instructions = "SELECT * FROM (SELECT chat_table_name FROM m_chat_member WHERE member_id = ?) " \
                           "LEFT JOIN m_chats"

        with sql_connect(self.__db_name) as db:
            db_cursor = db.cursor()
            db_cursor.execute(sql_instructions, (member.id_,))
            request = db_cursor.fetchall()

        chat_list = []
        for chat in request:
            chat_list.append(Chat(chat[0], members=[member]))

        return chat_list

    def read_message(self, chat, __timestamp) -> Message:
        sql_instructions = "SELECT * FROM ? WHERE timestamp = ?;"

        with sql_connect(self.__db_name) as db:
            db_cursor = db.cursor()
            db_cursor.execute(sql_instructions, (chat.name, __timestamp))
            request = db_cursor.fetchall()
            print(request)

    def read_chat(self, chat: Chat, count: int = 20) -> [Message]:
        pass

    def open_chats(self, count: int = 0) -> [Chat]:
        sql_instructions = "SELECT table_name, display_name, info FROM m_chats"
        if count != 0: # possible remove
            sql_instructions += f" ORDER BY id ASC LIMIT {count};"
        else:
            sql_instructions += ";"

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
                    member_list.append(Member(("", 0), id_=m_chat_member[1]))
            chat_list.append(Chat(name=chat[0], display_name=chat[1], info=chat[2], members=member_list))
        return chat_list

    def open_members(self, count: int = 0) -> [Member]:
        sql_instructions = "SELECT * FROM m_member"
        if count != 0: # possible remove
            sql_instructions += f" ORDER BY id ASC LIMIT {count};"
        else:
            sql_instructions += ";"

        with sql_connect(self.__db_name) as db:
            db_cursor = db.cursor()
            db_cursor.execute(sql_instructions)
            request = db_cursor.fetchall()

        member_list = []
        for member in request:
            member_list.append(Member(address=("", 0), id_=member[0], name_self=member[1], name_given=member[2],
                                      name_generic=member[3], cryptic_hash=member[4]))
        return member_list

    def update(self):
        sql_instructions = "VACUUM;"

        with sql_connect(self.__db_name) as db:
            db_cursor = db.cursor()
            db_cursor.execute(sql_instructions)

            db.commit()


# for testing the db
if __name__ == "__main__":
    database = DB(input("Database location: "))
    inp = "help"
    while inp != "exit":
        if inp == "help":
            print("Commands:\n\thelp\n\tread\n\tlist\n\tinsert\n\texit\n")
        elif inp == "read":
            inp = input("What type do you want to read? (m: member, t: message, c: chat)")
            if inp == "m":
                for _member in database.open_members():
                    print("id:  \t" + str(_member.id_) + "\nself:\t" +
                          _member.name_self + "\ngiven:\t" + _member.name_given)
            elif inp == "t":
                print(database.read_message(Chat(input("Chatname: "), members=[]), __timestamp=input("Timestamp: ")))
            elif inp == "c":
                print(database.read_chat(Chat(input("Chatname: "), members=[])))
        elif inp == "list":
            inp = input("What type do you want to list? (m: member, c: chat)")
            if inp == "m":
                for _member in database.open_members():
                    print("id:  \t" + str(_member.id_) + "\nself:\t" +
                          _member.name_self + "\ngiven:\t" + _member.name_given)
            elif inp == "c":
                for _chat in database.open_chats():
                    print("Chatname:\t\t" + _chat.name + "\nDisplayname:\t" + _chat.display_name + "\nInformation:\t" + _chat.info)
                print()
        elif inp == "insert":
            inp = input("What type do you want to insert? (m: member, t: message, c: chat)")
            if inp == "m":
                if input("self? (Y/N)") == "Y":
                    database.new_self(Member(("", 0), name_self=input("Your name: "),
                                             name_given=input("Your name for others: "),
                                             name_generic="self"))
                database.new_member(Member(("", 0), name_self=input("Members name: "),
                                           name_given=input("Members name for others: "),
                                           name_generic=input("Generic name: ")))
            elif inp == "t":
                database.new_message(Message(chat=Chat(name=input("Chatname: "), members=[]),
                                             to_member=Member(("", 0)), text=bytes(input("the Text of the Message: "))))
            elif inp == "c":
                database.new_chat(Chat(name=input("Chat name: "), members=[Member(("", 0))],
                                       display_name=input("Shown name: "), info=input("Information about the chat: ")))
        inp = input(">>>")
