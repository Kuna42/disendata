
# import
from messenger.m_abc import Interface
from messenger.m_bc import Member, Message, Chat
from messenger.events import EventSend
from messenger.variables import S, connection, running, thread_objects


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
        # return self._ainput()

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
        self._show(f"What port? (default: {S.PORT})")
        answer = self.input()
        if answer:
            connection[0] = ("", int(answer)) # could be better

        self._show(f"What database? (default: /tmp/test.db)")
        answer = self.input()
        if answer:
            return answer
        return "/tmp/test.db"

    def show_msg(self, message: Message):
        pass

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
                       "\tonline members\n")

        elif input_cmd == "exit":
            self.running.stop()

        elif input_cmd == "connect": # TODO could be better, like at the first check if someone else is there
            text = S.MSG_START["cmd"] + S.CMD["connection"]

            self._show("Connect to ... (ip)")
            answer = [self.input()]
            self._show(f"Port...(default: {S.PORT})")
            answer.append(self.input())
            EventSend(message=Message(to_member=Member(address=tuple(answer), identification_attribute="address"),
                                      sender=Member(id_=0), text=text, chat=Chat(name=""), m_type="cmd"))
        elif input_cmd == "online members":
            for member in thread_objects.network.online_members.group.values():
                self._show(f"\t{member.name_self}\t+\t{member.name_generic}\t{member.address[0]}:{member.address[1]}")

    def run(self):
        while running:
            self.commands(self.input())
