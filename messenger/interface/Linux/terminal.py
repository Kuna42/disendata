
# useful thinks for linux
# https://askubuntu.com/questions/158305/python-libnotify-showing-weird-behaviour-with-xfce4-notifyd-and-notify-osd
# https://stackoverflow.com/questions/51910946/using-backspace-with-getch-in-python-curses
# https://docs.python.org/3/library/curses.html


# import
import os

from messenger.m_abc import Interface
from messenger.m_bc import Chat
from messenger.variables import LinuxS, running

import curses


# classes
class Configuration:
    def __init__(self):
        """
        This is a class for all configurations of the visual user terminal
        """
        # this could be in another file, to load configs for both, terminal and window

        #  Database:

        self.path_database = ""

        #  Language:
        self.language = ""

        #  Minimum size:
        self.min_y = 0
        self.min_x = 0

        #  Keys reserved for options:
        self.k_switch_window = ""
        self.k_help = ""
        self.k_config = ""
        self.k_new_member = ""
        self.k_new_chat = ""
        self.k_edit_chat = ""
        self.k_debug = ""
        self.k_exit = ""

        #  Values of the windows in the terminal:

        # in percent of the display size,
        # if it is 0, the optional parameters are used

        self.w_line_chat_message = 20
        self.w_line_debug_chat = 10
        self.w_line_message_type = 80

        # optional parameters
        # in lines or spaces

        self.i_line_chat_chat = 2
        self.w_line_type_new_message = 3
        self.w_line_debug_lines = 5

    def file(self):
        """
        Check if the config.-file exists and create it if not
        :return:
        """
        if not os.path.exists(LinuxS.CONFIG_FILE_PATH):  # if folder not exists
            os.mkdir(LinuxS.CONFIG_FILE_PATH)

        if not os.path.exists(LinuxS.CONFIG_FILE_NAME):  # if file not exists
            with open(LinuxS.CONFIG_FILE_NAME, "w") as config_file:  # todo could be better
                with open(LinuxS.TEMPLATE_CONFIG_FILE_PATH, "r") as template_file:
                    config_file.write(template_file.read())

        self.read()

    def change(self, **kwargs):  # todo is this needed?
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def read(self):
        """
        Read the configurations and load them into the values of these object
        :return:
        """
        with open(LinuxS.CONFIG_FILE_NAME, "r") as config_file:
            for line in config_file:
                if line.startswith("# ") or line == "\n":
                    continue
                line = line[:-1].split(" = ", 1)
                if line[1].isnumeric():
                    line[1] = int(line[1])
                setattr(self, line[0], line[1])

    def update(self):
        """
        Writes all configurations in the config file
        :return:
        """
        config_text = ""
        with open(LinuxS.CONFIG_FILE_NAME, "r") as config_file:
            for line in config_file:
                if not line.startswith("# ") or line != "\n":
                    line = line.split(" = ", 1)
                    line[1] = getattr(self, line[0])
                    line = " = ".join(line) + "\n"
                config_text += line
        with open(LinuxS.CONFIG_FILE_NAME, "w") as config_file:
            config_file.write(config_text)


class LanguageText:
    def __init__(self, language="en_UK"):
        # this could be in another file, to load configs for both, terminal and window
        self.language = language

    def __str__(self):
        return self.language

    def translate(self, text: str) -> str:  # TODO this need to be included and be written
        """
        This translates the standard text into a specific language
        :param text:
        :return:
        """
        return text


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
        self.focus = "chat"  # sone focus random set to chat
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
                self.type_buffer = ""

        self.window = Window()
        self._window_init()

        self.update_screen()
        # todo here must be written on

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
            self.screen_size[0] - 1,
            self.window.debug_d[1] + 1,
            1000,  # TODO here is recode needed (y size of the chats)  # this must be a number with the divider 2
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
            self.focus = tab_rotating.get(self.focus, self.focus)
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

    def update_debug(self, _input: int = None, text: TextCurses = None):
        pass

    def update_chat(self, _input: int = None, chat: Chat = None):  # todo idk if the chat is necessary
        # todo python3.10 match case
        if _input is None or _input == -1:
            pass
        elif _input == curses.KEY_UP:
            if self.window.chat_act_loc[0] == 0:
                return
            self.window.chat_act_loc[0] -= 2
        elif _input == curses.KEY_DOWN:
            if self.window.chat_act_loc[0] == self.window.chat_d[6] - 1:
                return
            self.window.chat_act_loc[0] += 2
        elif _input == curses.KEY_LEFT:
            pass
        elif _input == curses.KEY_RIGHT:
            pass
        elif _input == curses.KEY_ENTER:
            self.update_history(chat=self.window.chat_chat_ord[self.window.chat_act_loc[0]])

        if chat:
            self.window.chat_chat_ord.append(chat)

        """
            self.update_history(text=TextCurses("")) # TODO work here for enter the chat history
            # TODO work here
        if text:
            if text.y is None:
                self.window.chat.addstr(*self.window.chat_act_loc, str(text))
            else:
                self.window.chat.addstr(text.y, text.x, str(text))
        """

    def update_history(self, _input: int = None, text: TextCurses = None):
        pass

    def update_type(self, _input: int = None, text: TextCurses = None):
        pass

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
            if char_input == -1:
                continue
            if self.focus in focus_def.keys():
                focus_def[self.focus](_input=char_input)


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
        self.curses.run()
