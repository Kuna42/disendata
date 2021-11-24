
# import
from messenger.m_abc import Interface
from messenger.m_bc import Member, Message, Chat, Event
from messenger.variables import running


# classes
class Terminal(Interface):
    def __init__(self):
        super(Terminal, self).__init__()
        self.typing_start = ">"

    def input(self) -> str:
        return input(self.typing_start)

    @staticmethod
    def _show(string: str, end: str = "\n"):
        print(string, end=end)

    def decide(self, event: Event) -> bool:
        pass

    def get_db_name(self) -> str:
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
        if input_cmd == "exit":
            running = False

    def run(self):
        while running:
            self.commands(self.input())
