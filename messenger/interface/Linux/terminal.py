
# useful thinks for linux
# https://askubuntu.com/questions/158305/python-libnotify-showing-weird-behaviour-with-xfce4-notifyd-and-notify-osd
# https://stackoverflow.com/questions/51910946/using-backspace-with-getch-in-python-curses
# https://docs.python.org/3/library/curses.html


# import
import os
import time

from messenger.m_abc import Interface
from messenger.m_bc import Chat, Message, Member
from messenger.variables import LinuxS, running
from messenger.interface.Linux.configuration import Configuration, LanguageText
from messenger.events import EventMsgSend, EventNewChat, EventNewMember, EventUpdateDB

import curses

# strange but it worked
curses.KEY_ENTER = 10


# classes

class TextCurses:
    def __init__(self, text: str, y_loc: int = None, x_loc: int = None):
        """
        This is a class for adding text blocks to a curses window in the class CursesWindow
        :param text: any Text (string), as long as this doesn't go over the window size
        :param y_loc: in what line of the window should the text be, default None. If None, it will append at the end
        :param x_loc: in what column of the window should the text be, default None. If None, append to the end
        """
        self.text = text
        self.y = y_loc
        self.x = x_loc

    def __str__(self):
        return self.text

    def __getitem__(self, item):
        raise ValueError(f"'{item}' is not a valid Value of this class. Only 'y' and 'x' are valid.")


class ChatHistory(TextCurses):
    def __init__(self, chat: Chat = None):
        super(ChatHistory, self).__init__()


class CursesWindow:
    def __init__(self):

        # load config
        self.config = Configuration()
        self.config.file()

        # screen setup
        self.screen = curses.initscr()
        # initialisations of the screen / change some options
        curses.curs_set(0)
        curses.noecho()
        curses.cbreak()#
        self.screen.nodelay(True)
        self.screen.keypad(True)

        # set colours
        curses.start_color()  # colours
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # normal text
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)  # highlight text
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)  # error text
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_RED)  # unread messages
        curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)  # something useful to read

        # screen create
        self.screen_size = (0, 0)
        self._screen_init()

        # cursor location and focus location
        self.__focus = "chat"  # sone focus random set to chat
        self._cursor_location = [0, 0]

        # create values for the windows
        class Window:
            def __init__(self):
                self.debug = None
                self.debug_d = (  # window
                    0,  # n lines
                    0,  # n cols
                    0,  # begin_y
                    0,  # begin_x
                )
                self.chat = None
                self.chat_d = (  # pad
                    0,  # n lines (visible)
                    0,  # n cols (visible)
                    0,  # begin_y
                    0,  # begin_x
                    0,  # y of the right corner from the window
                    0,  # x of the right corner from the window
                    0,  # max n lines
                    0,  # max n cols
                )
                self.chat_act_loc = [
                    0,  # y active location in the pad
                    0,  # x active location in the pad
                ]
                self.chat_chat_ord = [
                    # here are all chats in order
                ]
                self.history = None
                self.history_d = (  # pad
                    0,  # n lines (visible)
                    0,  # n cols (visible)
                    0,  # begin_y
                    0,  # begin_x
                    0,  # y of the right bottom corner from the window
                    0,  # x of the right bottom corner from the window
                    0,  # max n lines
                    0,  # max n cols
                )
                self.history_act_loc = [
                    0,  # y active location in the pad
                    0,  # x active location in the pad
                ]
                self.type = None
                self.type_d = (  # window
                    0,  # n lines
                    0,  # n cols
                    0,  # begin_y
                    0,  # begin_x
                )
                self.type_act_loc = [
                    0,  # y active location in the window
                    0,  # x active location in the window
                ]
                self.type_buffer = ""

        self.window = Window()
        self._window_init()

        self.update_screen()
        # todo here must be written on

        self.chat_selected = None
        self.chat_visible = None

        self.language = LanguageText(self.config.language)

    def __del__(self):
        """
        Redo all options
        :return:
        """
        curses.curs_set(1)
        curses.nocbreak()
        self.screen.nodelay(False)
        self.screen.keypad(False)
        curses.echo()
        curses.endwin()

    @property
    def focus(self):
        return self.__focus

    @focus.setter
    def focus(self, new_focus: str):
        if self.focus == "type":
            self.chat_visible.type_buffer = self.window.type_buffer
        elif self.focus == "chat":
            pass
        elif self.focus == "history":
            pass

        if new_focus == "type":
            pass

        self.__focus = new_focus

    def _screen_init(self):
        # check screen size
        max_y, max_x = self.screen.getmaxyx()
        if max_y < self.config.min_y or max_x < self.config.min_x:
            raise BlockingIOError("The size of the window is too small.")  # TODO this should be a better error
        self.screen_size = (max_y, max_x)

    def _window_init(self):
        self.window.debug_d = (
            #  (available screen) * percent how much is used
            (self.screen_size[0] - 3) * self.config.w_line_debug_chat // 100,
            (self.screen_size[1] - 3) * self.config.w_line_chat_message // 100,
            1,
            1,
        )
        if self.config.w_line_debug_lines > self.window.debug_d[0]:
            self.window.debug_d = (
                self.config.w_line_debug_lines,
                *self.window.debug_d[1:]
            )
        self.window.chat_d = (
            (self.screen_size[0] - 3) - self.window.debug_d[0],
            self.window.debug_d[1],
            self.window.debug_d[0] + 2,
            1,
            self.screen_size[0] - 2,
            self.window.debug_d[1] + 1,
            1000,  # TODO here is recode needed (y = size of the chats * 2 - 1)
            self.window.debug_d[1]
        )
        self.window.type_d = [
            (self.screen_size[0] - 3) * (100 - self.config.w_line_message_type) // 100,
            (self.screen_size[1] - 3) - self.window.debug_d[1],
            None,
            self.window.chat_d[1] + 2,
        ]
        if self.config.w_line_type_new_message > self.window.type_d[0]:
            self.window.type_d[0] = self.config.w_line_type_new_message
        self.window.type_d[2] = self.screen_size[0] - self.window.type_d[0] - 1
        self.window.type_d = tuple(self.window.type_d)

        self.window.history_d = (
            (self.screen_size[0] - 3) - self.window.type_d[0],
            self.window.type_d[1],
            1,
            self.window.debug_d[1] + 2,
            self.window.type_d[2] - 1,
            self.screen_size[1] - 1,
            1000,  # TODO here is recode needed (y size of the message history)
            self.window.type_d[1],
        )

        # the windows are init
        self.window.debug = curses.newwin(*self.window.debug_d)
        self.window.chat = curses.newpad(*self.window.chat_d[6:8])
        self.window.history = curses.newpad(*self.window.history_d[6:8])
        self.window.type = curses.newwin(*self.window.type_d)

    def input(self) -> int:
        ##
        _input = self.screen.getch()
        if _input == -1:
            return -1  # could be None
        elif _input == self._ord(self.config.k_switch_window):
            tab_rotating = {"type": "chat", "chat": "history", "history": "type"}
            self.focus = tab_rotating.get(self.focus, self.focus)  # TODO this should be separate
        elif _input == self._ord(self.config.k_help):
            self.update_info_field(visible=True, text=TextCurses(self.language.translate("help_text")))
        elif _input == self._ord(self.config.k_config):
            pass
        elif _input == self._ord(self.config.k_new_member):
            pass
        elif _input == self._ord(self.config.k_new_chat):
            pass
        elif _input == self._ord(self.config.k_edit_chat):
            pass
        elif _input == self._ord(self.config.k_debug):
            pass
        elif _input == self._ord(self.config.k_exit):
            running.stop()
        else:
            return _input
        # it returns -1 if nothing is pressed
        return -1

    def _is_printable_char(self, ch: int or str):  # TODO this need to be better
        if type(ch) is int:
            pass
        elif type(ch) is str:
            if len(ch) - 1:
                raise ValueError(f"This Value '{ch}' must be exactly one single character, not more or less.")
            ch = ord(ch)

        return 31 < ch < 127  # or 160 < ch < 255

    def _ord(self, string: str) -> int:
        """
        This is for transferring the values from self.config
        :param string: like TAB, F[], PAGE_UP, PAGE_DOWN, ENTER, DEL, INS, BACKSPACE,
        LEFT, UP, RIGHT, DOWN, HOME, END, PRINT
        :return: integer of this string with ord()
        """
        if string == "TAB":
            return ord("\t")  # maybe back TAB should be added
        elif string.startswith("F"):
            return getattr(curses, f"KEY_{string}")
        elif string in {"UP", "DOWN", "RIGHT", "LEFT", "HOME", "END", "BACKSPACE", "ENTER", "PRINT"}:
            return getattr(curses, f"KEY_{string}")
        raise ValueError(f"this is not a valid key option: {string}")

    def update_screen(self):
        """
        Refresh the screen layout
        :return:
        """
        # background
        self.screen.bkgd(curses.color_pair(1))
        self.screen.box()
        self.screen.addstr('┌' + '─' * self.window.debug_d[1] + '┬' + '─' * self.window.history_d[1] + '┐')
        for i in range(self.window.debug_d[0]):
            self.screen.addstr('│' + ' ' * self.window.debug_d[1] + '│' + ' ' * self.window.history_d[1] + '│')
        self.screen.addstr('├' + '─' * self.window.debug_d[1] + '┤' + ' ' * self.window.history_d[1] + '│')
        for i in range(self.window.chat_d[0] - self.window.type_d[0] - 1):
            self.screen.addstr('│' + ' ' * self.window.chat_d[1] + '│' + ' ' * self.window.history_d[1] + '│')
        self.screen.addstr('│' + ' ' * self.window.chat_d[1] + '├' + '─' * self.window.history_d[1] + '┤')
        for i in range(self.window.type_d[0]):
            self.screen.addstr('│' + ' ' * self.window.chat_d[1] + '│' + ' ' * self.window.type_d[1] + '│')
        self.screen.addstr('└' + '─'*self.window.chat_d[1] + '┴')
        self.screen.refresh()

    def update_debug(self, text: TextCurses = None):
        if text:
            self.window.debug.addstr(text.y, 0, text.text[:self.window.debug_d[1] - text.x]
                                     .ljust(self.window.debug_d[1] - text.x, " ")
                                     .rjust(self.window.debug_d[1], " "))
        self.window.debug.refresh()

    def update_chat(self, _input: int = None, chat: Chat = None):
        if chat:
            tmp_how_many_chats = len(self.window.chat_chat_ord)
            if tmp_how_many_chats:
                self.window.chat.addstr(tmp_how_many_chats * 2 - 1, 0, "-" * self.window.chat_d[7])
            self.window.chat.addstr(tmp_how_many_chats * 2, 0,
                                    chat.display_name[:self.window.chat_d[7] - 3]
                                    .ljust(self.window.chat_d[7] - 3, " ")
                                    + "|" + str(chat.unread_msg)[:3].rjust(2, " "))
            self.window.chat_chat_ord.append(chat)
            return self.window.chat.refresh(0, 0, *self.window.chat_d[2:6])  # todo this needs to be better

        self.chat_selected = self.window.chat_chat_ord[self.window.chat_act_loc[0] // 2]
        self.window.chat.addstr(*self.window.chat_act_loc,
                                self.chat_selected.display_name[:self.window.chat_d[7] - 3]
                                .ljust(self.window.chat_d[7] - 3, " ")
                                + "|" + str(self.chat_selected.unread_msg)[:3].rjust(2, " "),
                                curses.color_pair(1))

        # todo python3.10 match case
        if _input is None or _input == -1:
            pass
        elif _input == curses.KEY_UP:
            if self.window.chat_act_loc[0] != 0:
                # return self.window.chat.refresh(0, 0, *self.window.chat_d[2:6])
                self.window.chat_act_loc[0] -= 2
        elif _input == curses.KEY_DOWN:
            if self.window.chat_act_loc[0] != len(self.window.chat_chat_ord) * 2 - 2:
                # return self.window.chat.refresh(0, 0, *self.window.chat_d[2:6])
                self.window.chat_act_loc[0] += 2
        elif _input == curses.KEY_LEFT:
            pass
        elif _input == curses.KEY_RIGHT:
            pass
        elif _input == curses.KEY_ENTER:
            self.chat_visible.type_buffer = self.window.type_buffer
            self.chat_visible = self.chat_selected
            self.window.type.clear()
            self.window.type_buffer = self.chat_visible.type_buffer
            self.update_type()
            self.update_history(chat=self.chat_selected) # hm

        self.chat_selected = self.window.chat_chat_ord[self.window.chat_act_loc[0] // 2]

        self.window.chat.addstr(*self.window.chat_act_loc,
                                self.chat_selected.display_name[:self.window.chat_d[7] - 3]
                                .ljust(self.window.chat_d[7] - 3, " ")
                                + "|" + str(self.chat_selected.unread_msg)[:3].rjust(2, " "),
                                curses.color_pair(2))

        self.window.chat.refresh(0, 0, *self.window.chat_d[2:6])  # todo this needs to be better, replace the (0, ...

    def update_history(self, _input: int = None, chat: Chat = None):
        # todo update_history() might be changed that only a few messages would shown
        pass

    def update_type(self, _input: int = None, text: TextCurses = None):
        # todo python3.10 match case
        if _input is None or _input == -1:
            pass
        elif _input == curses.KEY_UP:
            pass
        elif _input == curses.KEY_DOWN:
            pass
        elif _input == curses.KEY_LEFT:
            pass
        elif _input == curses.KEY_RIGHT:
            pass
        elif _input == curses.KEY_ENTER:
            EventMsgSend(Message(
                text=bytes(self.window.type_buffer, "utf-8"),
                sender=Member(id_=0),
                chat=self.chat_visible,
                _timestamp=time.strftime('%H:%M:%S - %d.%m.%Y')
            ))
            self.window.type_buffer = ""
            self.chat_visible.type_buffer = ""
            self.window.type.clear()
        elif _input == curses.KEY_BACKSPACE:
            self.window.type.addstr(*self.window.type_act_loc, " ")
            self.window.type_buffer = self.window.type_buffer[:-1]
        elif self._is_printable_char(_input):
            self.window.type_buffer += chr(_input)
        buffer_size = len(self.window.type_buffer)

        self.window.type_act_loc = [
            buffer_size // self.window.type_d[1],
            buffer_size % self.window.type_d[1]
        ]

        def get_type_line_text():  # todo maybe this could be better without yield
            for buffer_index in range(0, buffer_size, self.window.type_d[1]):
                # todo here might be an auto corrector
                yield self.window.type_buffer[buffer_index:buffer_size+buffer_index]
        for line_index, line_text in enumerate(get_type_line_text()):
            # line_text = " ".join(self.language.spellcheck(*line_text.split(" "),  # TODO bad idea
            #                                               marker_start="",
            #                                               marker_end=""))
            self.window.type.addstr(line_index, 0, line_text)
        # cursor
        self.window.type.addstr(*self.window.type_act_loc, "_", curses.A_BLINK)
        self.window.type.refresh()

    def update_write_field(self, visible: bool = True, _input: int = None,
                           text: TextCurses = None, get_buffer: bool = False):
        if not visible:
            return self.update_screen()
        self.focus = "write_field"

    def update_decide_field(self, visible: bool = True, _input: int = None,
                            text: TextCurses = None, decide_options: dict = None):
        if not visible:
            return self.update_screen()
        self.focus = "decide_field"

    def update_info_field(self, visible: bool = True, _input: int = None,
                          text: TextCurses = None):
        if not visible:
            return self.update_screen()
        self.focus = "info_field"

    def run(self):
        focus_def = {
            "chat": self.update_chat,
            "history": self.update_history,
            "type": self.update_type,
            "write_field": self.update_write_field,
            "decide_field": self.update_decide_field,
            "info_field": self.update_info_field,
        }
        while running:
            char_input = self.input()
            # if char_input == -1:
            #     continue
            if self.focus in focus_def.keys():
                focus_def[self.focus](_input=char_input)

            self.update_debug(text=TextCurses(f"Focus: {self.focus}", 1, 0))
            self.update_debug(text=TextCurses(f"Chat:  {self.chat_visible.display_name}", 2, 0))
            self.update_debug(text=TextCurses(f"Time: {time.strftime('%H:%M:%S - %d.%m.%Y')}", 3, 0))

            # TODO tmp
            self.update_debug(text=TextCurses(f"TMP:   {self.chat_visible.display_name}", 0, 0))


class Terminal(Interface):
    def __init__(self):
        self.curses = CursesWindow()
        super(Terminal, self).__init__()

    def __del__(self):
        pass

    def input(self, text: str = "") -> str:
        self.curses.update_write_field(visible=True, text=TextCurses(text))
        # todo wait for output
        return ""

    def decide(self, decide_txt: str, decide_options: dict) -> bool:
        self.curses.update_decide_field(visible=True, text=TextCurses(decide_txt),
                                        decide_options=decide_options)
        # todo wait for output
        return True  # todo should be rewritten, it should send back, what was the decide

    def get_db_name(self) -> str:
        if self.curses.config.path_database[0] == "~":
            self.curses.config.path_database = os.path.expanduser("~") + self.curses.config.path_database[1:]
        return self.curses.config.path_database

    def show_msg(self, message):
        pass

    def show_chat(self, chat):
        pass

    def show_member(self, member):
        pass

    def show_chat_list(self, chat_list: list):
        pass

    def show_member_list(self, member_list: list):
        pass

    def show_self(self):
        pass

    def commands(self, input_cmd: str):  # needed ?
        pass

    def run(self):
        # TODO this is only tmp
        self.curses.update_chat(chat=Chat(name="self", display_name="command line 1"))  # todo
        self.curses.update_chat(chat=Chat(name="self2", display_name="command line 2 - super long name without text"))  # todo
        self.curses.chat_selected = Chat(name="self")
        self.curses.chat_visible = Chat(name="self")
        EventUpdateDB()
        self.curses.run()
