
# import
from messenger.m_abc import Interface
from messenger.m_bc import Member, Message, Chat
from messenger.events import EventSend, EventMsgSend, EventNewChat, EventUpdateDB
from messenger.variables import S, connection, running, thread_objects, object_library


# classes
class Terminal(Interface):
    def __init__(self):
        super(Terminal, self).__init__()
        self.typing_start = ">"
        self.running = running  # is this needed?

    def input(self, text: str = "") -> str:
        if text:
            return input(text)
        return input(self.typing_start)

    @staticmethod
    def _show(string: str, end: str = "\n"):
        print(string, end=end)

    def decide(self, decide_txt: str, decide_options: dict, **kwargs) -> bool:
        self._show(decide_txt + "\t[" + ", ".join(decide_options.keys()) + "]")
        answer = self.input("Decide: ")
        if answer not in decide_options.keys():  # possible problems
            return self.decide(decide_txt=decide_txt, decide_options=decide_options)
        return decide_options[answer]()

    def get_db_name(self) -> str:
        answer = self.input(f"What port? (default: {S.PORT}): ")
        if answer:
            connection[0] = ("", int(answer)) # could be better

        answer = self.input(f"What database? (default: /tmp/test.db): ")
        if answer:
            return answer
        return "/tmp/test.db"

    def show_msg(self, message: Message):
        self._show(f"/chats/{str(message.chat.name, 'ascii')}>{message.sender.name_given}: {message.text.decode('utf-8')}")

    def show_chat(self, chat: Chat):
        pass

    def show_member(self, member: Member):
        pass

    def show_chat_list(self, chat_list: list):
        pass

    def show_member_list(self, member_list: list):
        pass

    def show_self(self):
        pass

    def commands(self, input_cmd: str):
        # todo this can be in 3.10 with match case
        if input_cmd == "help":
            self._show("\thelp\n"
                       "\texit\n"
                       "\tconnect\n"
                       "\tonline members\n"
                       "\tedit member\n"
                       "\tnew chat\n"
                       "\tlist chats\n"
                       "\topen chat\n")

        elif input_cmd == "exit":
            EventUpdateDB()
            self.running.stop()

        elif input_cmd == "connect": # TODO could be better, like at the first check if someone else is there
            self._show("Connect to ... (ip)")
            answer = [self.input()]
            self._show(f"Port...(default: {S.PORT})")
            answer_2 = self.input()
            if answer_2 == "":
                answer.append(S.PORT)
            else:
                answer.append(int(answer_2))
            self._show("(Given)Name of the Member")
            answer_2 = self.input()
            if answer_2:
                member = Member(address=tuple(answer), name_given=answer_2, identification_attribute="name_given")
            else:
                member = Member(address=tuple(answer), identification_attribute="address")
            EventSend(message=Message(to_member=member, sender=Member(id_=0),
                                      text=S.CMD["connection"], chat=Chat(name=""), m_type="cmd"))

        elif input_cmd == "online members":
            for member in thread_objects.network.online_members.group.values():
                self._show(f"\t{member.name_self}\t{member.name_given}\t{member.name_generic}"
                           f"\t{member.id_}\t{member.address[0]}:{member.address[1]}")

        elif input_cmd == "all members":
            for member in object_library[Member]:
                self._show(f"\t{member.name_self}\t{member.name_given}\t{member.name_generic}"
                           f"\t{member.id_}\t{member.address[0]}:{member.address[1]}")

        elif input_cmd == "edit member":
            self._show("If something was not filled, it will not replaced")
            m_dict = {}
            m_id_ = self.input("Id: ")
            if m_id_ != "":
                m_dict["id_"] = int(m_id_)
            m_name_given = self.input("Your name for the member: ")
            if m_name_given != "":
                m_dict["name_given"] = m_name_given
            m_name_self = self.input("Name of the Member: ")
            if m_name_self != "":
                m_dict["name_self"] = m_name_self
            m_name_generic = self.input("Generic name: ")
            if m_name_generic != "":
                m_dict["name_generic"] = m_name_generic
            m_address_0 = self.input("Ip-address: ")
            m_address_1 = self.input("Port: ")
            m_address = []
            if m_address_0 != "":
                m_address.append(m_address_0)
            if m_address_1 != "":
                if not m_address:
                    m_address.append("")
                m_address.append(int(m_address_1))
            if len(m_address) == 1:
                m_address.append(S.PORT)
            if m_address:
                m_dict["address"] = tuple(m_address)
            m_identification_attribute = self.input("Identification attribute (default 'id_'): ")
            if m_identification_attribute != "":
                m_dict["identification_attribute"] = m_identification_attribute
            Member(**m_dict)

        elif input_cmd == "new chat":
            chat = Chat(name=self.input("Chat-name: "))
            if not thread_objects.network.db.has_chat(chat=chat):
                return
            self._show(f"This chat({chat.name}) was not in the DB.")
            chat.display_name = self.input("Name of the chat: ")
            chat.info = self.input("Short information of the chat: ")
            members_str = "-"
            while members_str:
                members_str = self.input("Given-name of the Member, who is in this chat "
                                         "(press only Enter if no one else should be added): ")
                if not members_str:
                    break
                chat.members.new_member(Member(name_given=members_str,
                                               identification_attribute="name_given"))
            EventNewChat(chat=chat)

        elif input_cmd == "list chats":
            for chat in object_library[Chat]:
                self._show(f"{chat.name}\t{chat.display_name}\t{chat.info}", end="\t=\t")
                for member in chat.members.all_members():
                    self._show(f"{member.id_}", end="\t")
                self._show("")

        elif input_cmd == "open chat":
            chat = Chat(name=self.input("Chatname: "))
            if not thread_objects.network.db.has_chat(chat=chat):
                self._show(f"This chat({chat.name}) was not in the DB.")
                chat.display_name = self.input("Name of the chat: ")
                chat.info = self.input("Short information of the chat: ")
                members_str = "-"
                while members_str:
                    members_str = self.input("Given-name of the Member, who is in this chat "
                                             "(press only Enter if no one else should be added): ")
                    if not members_str:
                        break
                    chat.members.new_member(Member(name_given=members_str,
                                                   identification_attribute="name_given"))
                EventNewChat(chat=chat)
                # new chat

            self.chat_commands(chat=chat)

    def chat_commands(self, chat: Chat):
        cmd_char = "/"

        def chat_cmd(cmd: str, chat_: Chat):
            pass
        input_msg = ""
        while input_msg != (cmd_char + "exit"):
            input_msg = self.input(text=f"/chats/{chat.name}>self: ")
            if input_msg == "":
                continue
            if input_msg[0] == cmd_char:
                chat_cmd(cmd=input_msg[1:], chat_=chat)
                continue
            EventMsgSend(message=Message(text=bytes(input_msg, "utf-8"), sender=Member(id_=0), chat=chat))

    def run(self):
        while running:
            self.commands(self.input())
