
# useful thinks for linux
# https://askubuntu.com/questions/158305/python-libnotify-showing-weird-behaviour-with-xfce4-notifyd-and-notify-osd
# https://stackoverflow.com/questions/51910946/using-backspace-with-getch-in-python-curses
# https://docs.python.org/3/library/curses.html


# import
import os
import time
import re
import bisect
import logging

from messenger.m_abc import Interface, Event
from messenger.m_bc import Chat, Message, Member, MemberGroup, auto_linebreak, auto_linebreak_with_linebreak_info
from messenger.variables import LinuxS, S, running, object_library, thread_objects, information  # todo the thread_objects could be replaced with better Events
from messenger.interface.Linux.configuration import Configuration, LanguageText, DataText
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
        logging.error(f"(terminal:45) - ValueError('{item}' is not a valid Value of TextCurses. Only 'y' and 'x' are valid.)")
        raise ValueError(f"'{item}' is not a valid Value of this class. Only 'y' and 'x' are valid.")


# event for resize the terminal
class TerminalResized(Event):
    def __init__(self):
        super(TerminalResized, self).__init__(False)

    def command(self) -> None:

        thread_objects.interface.curses.terminal_size()

    def done(self) -> bool:
        return False


class CursesWindow:

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
            self.history_line_written = 0
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

            self.field = None
            self.field_d = (  # pad
                0,  # n lines (visible)
                0,  # n cols (visible)
                0,  # begin_y
                0,  # begin_x
                0,  # y of the right bottom corner from the window
                0,  # x of the right bottom corner from the window
                0,  # max n lines
                0,  # max n cols
            )
            self.field_act_loc = [
                0,  # y active location in the pad
                0,  # x active location in the pad
            ]
            self.field_act_lines = 0
            self.field_string = ""
            self.field_input = [
                # (name: str,
                # y_actual_place: int,
                # x_actual_place: int,
                # regex: str,
                # placeholder_chars: int,
                # actual_data: str,
                # y_real_place: int,
                # x_real_place: int),
            ]
            self.field_act_input = -1
            self.field_finally = None

            self.keybinding = None
            self.keybinding_d = (  # window
                0,  # n lines
                0,  # n cols
                0,  # begin_y
                0,  # begin_x
            )

    def __init__(self):

        # load config
        self.config = Configuration()
        self.config.file()

        # screen setup
        self.screen = curses.initscr()
        # save current screen
        curses.savetty()
        # initialisations of the screen / change some options
        curses.curs_set(0)
        curses.noecho()
        curses.cbreak(True)
        curses.setupterm(information(dict)["name"] + "_" + information(dict)["version"])
        self.screen.nodelay(True)
        self.screen.keypad(True)
        self.screen.leaveok(True)

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

        self.window = CursesWindow.Window()
        self._window_init()

        self.update_screen()

        self._terminal_resized = True
        # todo here must be written on

        # what chat is selected by the left chat list
        self.chat_selected = Chat(name="self", display_name="Self")

        # chat what is shown in the history
        self.__chat_visible = Chat(name="self")

        self.chat_message_cache = [
            # old messages first
        ]

        self.language = LanguageText(self.config)
        logging.info("Created CursesInterface..")

    def __del__(self):
        """
        Redo all options
        :return:
        """
        logging.info("Closing CursesInterface..")
        curses.curs_set(1)
        curses.nocbreak()
        self.screen.nodelay(False)
        self.screen.keypad(False)
        curses.echo()
        curses.endwin()
        curses.resetty()  # todo check if above is necessary

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

    @property
    def chat_visible(self):
        """
        chat what is shown in the history
        :return:
        """
        return self.__chat_visible

    @chat_visible.setter
    def chat_visible(self, chat: Chat):
        self.__chat_visible.type_buffer = self.window.type_buffer
        self.window.type_buffer = chat.type_buffer
        self.__chat_visible = chat
        self.window.type.clear()
        self.update_history(chat=chat)
        self.update_type()

    def _screen_init(self):
        # check screen size
        max_y, max_x = self.screen.getmaxyx()
        if max_y < self.config.min_y or max_x < self.config.min_x:
            logging.error("(terminal:268) - The size of the window is too small.")
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

        tmp_type_d_0 = (self.screen_size[0] - 3) * (100 - self.config.w_line_message_type) // 100
        if self.config.w_line_type_new_message > tmp_type_d_0:
            tmp_type_d_0 = self.config.w_line_type_new_message

        self.window.type_d = (
            tmp_type_d_0,
            (self.screen_size[1] - 3) - self.window.debug_d[1],
            self.screen_size[0] - tmp_type_d_0 - 1,
            self.window.chat_d[1] + 2,
        )

        self.window.history_d = (
            (self.screen_size[0] - 3) - self.window.type_d[0],
            self.window.type_d[1],
            1,
            self.window.debug_d[1] + 2,
            self.window.type_d[2] - 2,
            self.screen_size[1] - 1,
            1000,  # TODO here is recode needed (y size of the message history)
            self.window.type_d[1],
        )

        self.window.field_d = (
            self.screen_size[0] - 2,
            self.window.history_d[1],
            1,
            self.window.history_d[3],
            self.screen_size[0] - 2,
            self.screen_size[1] - 1,
            1000,
            self.window.history_d[7],
        )

        self.window.keybinding_d = (
            *self.window.chat_d[0:4],
        )

        # the windows are init
        self.window.debug = curses.newwin(*self.window.debug_d)
        #self.window.debug.idlok(True)
        self.window.chat = curses.newpad(*self.window.chat_d[6:8])
        self.window.history = curses.newpad(*self.window.history_d[6:8])
        self.window.type = curses.newwin(*self.window.type_d)

        self.window.field = curses.newpad(*self.window.field_d[6:8])
        self.window.keybinding = curses.newwin(*self.window.keybinding_d)

    def input(self) -> int:
        ##
        _input = self.screen.getch()
        if _input == -1:
            return -1  # could be None
        # change selected window
        elif _input == self._ord(self.config.k_switch_window):
            tab_rotating = {"type": "chat", "chat": "history", "history": "type"}
            self.focus = tab_rotating.get(self.focus, self.focus)  # TODO this should be separate
        # help page
        elif _input == self._ord(self.config.k_help):
            additional_data = DataText()
            additional_data.keybinding = self.language.translate("keybinding")
            additional_data.config_path = LinuxS.CONFIG_FILE_PATH
            all_information = information(dict)
            additional_data.name = all_information["name"]
            additional_data.version = all_information["version"]
            additional_data.author = all_information["author"]
            additional_data.www = all_information["www"]
            additional_data.copyright = all_information["copyright"]
            additional_data.licence = all_information["licence"]
            self.update_screen_field()
            self.update_keybinding()
            self.update_field(
                visible=True,
                text=TextCurses(
                    text=self.language.translate("information", additional_data),
                ),
                finally_do=None
            )
        # configuration page
        elif _input == self._ord(self.config.k_config):
            def finally_input(*args, **configs):
                for name, value in configs.items():
                    setattr(
                        self.config,
                        name,
                        value
                    )
                self.config.update()
            self.update_screen_field()
            self.update_keybinding()
            self.update_field(
                visible=True,
                text=TextCurses(
                    text=self.language.translate("configuration"),
                ),
                finally_do=finally_input
            )
        elif _input == self._ord(self.config.k_new_member):
            def finally_input(*args, **member_data): # TODO write this
                new_member = Member(
                    address=(member_data["member_ip"], int(member_data["member_port"])),
                    name_self=member_data["name_self"],
                    name_given=member_data["name_given"],
                    name_generic=member_data["name_generic"],
                    cryptic_hash="",#todo this have to be implemented
                )
                EventNewMember(new_member)
                new_chat = Chat(
                    name="memberChatII" + member_data["name_generic"],
                    members=MemberGroup(
                        Member(id_=0),
                        new_member
                    ),
                    display_name=member_data["name_given"],
                    info="Chat with the member",
                )
                EventNewChat(new_chat)
                self.update_chat(chat=new_chat)
            self.update_screen_field()
            self.update_keybinding()
            self.update_field(
                visible=True,
                text=TextCurses(
                    text=self.language.translate("member_add"),
                ),
                finally_do=finally_input
            )
        elif _input == self._ord(self.config.k_new_chat):
            def finally_input(*args, **chat_data): # TODO write this
                EventNewChat(Chat(
                    name="",
                    members=MemberGroup(
                        Member(id_=0),
                    ),
                    display_name="",
                    info="",
                ))
            self.update_screen_field()
            self.update_keybinding()
            self.update_field(
                visible=True,
                text=TextCurses(
                    text=self.language.translate("chat_add"),
                ),
                finally_do=finally_input
            )
        elif _input == self._ord(self.config.k_edit_chat):
            def finally_input(*args, **chat_data):
                pass
            self.update_screen_field()
            self.update_keybinding()
            self.update_field(
                visible=True,
                text=TextCurses(
                    text=self.language.translate("chat_edit"),
                ),
                finally_do=finally_input
            )
        elif _input == self._ord(self.config.k_debug):
            pass
        elif _input == self._ord(self.config.k_escape):
            self.focus = "chat"
            self.update_screen()
            self.refresh_all()
        elif _input == self._ord(self.config.k_exit):
            running.stop()
        else:
            return _input
        # it returns -1 if nothing is pressed
        return -1

    #@staticmethod
    def _is_printable_char(self, ch: int or str):  # TODO this need to be better
        if type(ch) is int:
            pass
        elif type(ch) is str:
            if len(ch) - 1:
                logging.error(f"(terminal:472) - This Value '{ch}' must be exactly one single character, not more or less.")
                raise ValueError(f"This Value '{ch}' must be exactly one single character, not more or less.")
            ch = ord(ch)

        return 31 < ch < 127  # or 160 < ch < 255

    #@staticmethod
    def _ord(self, string: str) -> int:
        """
        This is for transferring the values from self.config
        :param string: like TAB, F[..], PAGE_UP, PAGE_DOWN, ENTER, DEL, INS, BACKSPACE,
        LEFT, UP, RIGHT, DOWN, HOME, END, PRINT
        :return: integer of this string with ord()
        """
        if string == "TAB":
            return ord("\t")  # maybe back TAB should be added
        elif string.startswith("F"):
            return getattr(curses, f"KEY_{string}")
        elif string in {"UP", "DOWN", "RIGHT", "LEFT", "HOME", "END", "BACKSPACE", "ENTER", "PRINT"}:
            return getattr(curses, f"KEY_{string}")
        logging.error(f"(terminal:492) - this is not a valid key option: {string}")
        raise ValueError(f"this is not a valid key option: {string}")

    def terminal_resized(self):
        self._terminal_resized = False
        # update all windows
        # update actual selected window todo
        if self.focus in {"chat", "history", "type"}:
            self.update_screen()
            self.update_history(refresh=True)
            self.update_chat(refresh=True)
            self.update_type()
        elif self.focus == "field":
            self.update_screen_field()
            self.update_field(refresh=True)
            self.update_keybinding()

    def terminal_size(self):
        # terminal resized ?
        if not curses.is_term_resized(*self.screen_size):
            return
        self._screen_init()
        self._window_init()
        self._terminal_resized = True

    def update_screen(self):
        """
        Refresh the screen layout
        :return:
        """
        # background
        self.screen.clear()
        self.screen.bkgd(curses.color_pair(1))

        c_chat = self.window.debug_d[1]  # column size of the chat and debug window
        c_history = self.window.history_d[1]  # column size of the history and type window
        self.screen.insstr(
            0, 0,
            ('┌' + '─' * c_chat + '┬' + '─' * c_history + '┐\n') +
            ('│' + ' ' * c_chat + '│' + ' ' * c_history + '│\n') * self.window.debug_d[0] +
            ('├' + '─' * c_chat + '┤' + ' ' * c_history + '│\n') +
            ('│' + ' ' * c_chat + '│' + ' ' * c_history + '│\n') * (self.window.chat_d[0] - self.window.type_d[0] - 1) +
            ('│' + ' ' * c_chat + '├' + '─' * c_history + '┤\n') +
            ('│' + ' ' * c_chat + '│' + ' ' * c_history + '│\n') * self.window.type_d[0] +
            ('└' + '─' * c_chat + '┴' + '─' * c_history + '┘')
        )
        self.screen.refresh()

    def update_screen_field(self):
        """
        Refresh the screen layout
        :return:
        """
        # background
        self.screen.clear()
        self.screen.bkgd(curses.color_pair(1))

        c_chat = self.window.debug_d[1]  # column size of the chat and debug window
        c_history = self.window.history_d[1]  # column size of the history and type window
        self.screen.insstr(
            0, 0,
            ('┌' + '─' * c_chat + '┬' + '─' * c_history + '┐\n') +
            ('│' + ' ' * c_chat + '│' + ' ' * c_history + '│\n') * self.window.debug_d[0] +
            ('├' + '─' * c_chat + '┤' + ' ' * c_history + '│\n') +
            ('│' + ' ' * c_chat + '│' + ' ' * c_history + '│\n') * self.window.chat_d[0] +
            ('└' + '─' * c_chat + '┴' + '─' * c_history + '┘')
        )
        self.screen.refresh()

    def update_debug(self, text: TextCurses = None):
        if text:
            self.window.debug.insstr(text.y, 0, text.text[:self.window.debug_d[1] - text.x]
                                     .ljust(self.window.debug_d[1] - text.x, " ")
                                     .rjust(self.window.debug_d[1], " "))
        self.window.debug.refresh()

    def update_chat(self, _input: int = None, chat: Chat = None, refresh: bool = False):
        def seperator(chat_numb):
            self.window.chat.insstr(chat_numb * 2 - 1, 0, "-" * self.window.chat_d[7])

        def chat_entry(chat_numb, chat_):
            self.window.chat.insstr(chat_numb * 2, 0,
                                    chat_.display_name[:self.window.chat_d[7] - 3]
                                    .ljust(self.window.chat_d[7] - 3, " ")
                                    + "|" + str(chat_.unread_msg)[:3].rjust(2, " "))

        if refresh:
            self.window.chat.clear()
            for chat_line, chat_chat in enumerate(self.window.chat_chat_ord):
                if 0 < chat_line < len(self.window.chat_chat_ord):
                    seperator(chat_line)
                chat_entry(chat_line, chat_chat)

        if chat:
            if chat in self.window.chat_chat_ord:
                return
            tmp_how_many_chats = len(self.window.chat_chat_ord)
            if tmp_how_many_chats:
                seperator(tmp_how_many_chats)
            chat_entry(tmp_how_many_chats, chat)
            self.window.chat_chat_ord.append(chat)
            return self.window.chat.refresh(0, 0, *self.window.chat_d[2:6])  # todo this needs to be better

        self.window.chat.insstr(*self.window.chat_act_loc,
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
            self.chat_visible = self.chat_selected

        self.chat_selected = self.window.chat_chat_ord[self.window.chat_act_loc[0] // 2]

        self.window.chat.insstr(*self.window.chat_act_loc,
                                self.chat_selected.display_name[:self.window.chat_d[7] - 3]
                                .ljust(self.window.chat_d[7] - 3, " ")
                                + "|" + str(self.chat_selected.unread_msg)[:3].rjust(2, " "),
                                curses.color_pair(2))

        self.window.chat.refresh(0, 0, *self.window.chat_d[2:6])  # todo this needs to be better, replace the (0, ...

    def update_history(self, _input: int = None, chat: Chat = None, message: Message = None, refresh: bool = False):
        # todo update_history() might be changed that only a few messages would shown
        def show_line_sized_message(message_: Message):
            history_message = f"[{message_.timestamp}]_{message_.sender.name_given}: " \
                              f"{' ' * 5}{str(message_.text, 'utf-8')}"  # todo replace the 5 with a variable
            for text_line in auto_linebreak(text=history_message, max_char_in_line=self.window.history_d[1],
                                            split_char=" ").split("\n"):
                self.window.history_line_written += 1
                self.window.history.insstr(
                    self.window.history_line_written, 0,
                    text_line
                )
        if refresh:
            chat = self.chat_visible

        if chat:
            self.chat_message_cache = thread_objects.network.db.read_chat(chat=chat, count=100)
            self.window.history_line_written = 0
            self.window.history.clear()
            self.window.history.insstr(0, 0, f"{chat.display_name}: {' ' * 5}{chat.info}"[:self.window.history_d[1]])
            for message_in_cache in self.chat_message_cache:
                show_line_sized_message(message_in_cache)

        if message:
            if message.chat is not self.chat_visible:
                return
            self.chat_message_cache.append(message)
            show_line_sized_message(message)

        # todo python3.10 match case

        if _input is None or _input == -1:
            pass
        elif _input == curses.KEY_UP:
            if self.window.history_act_loc[0] != 0:
                self.window.history_act_loc[0] -= 1
        elif _input == curses.KEY_DOWN:
            if self.window.history_act_loc[0] != self.window.history_line_written:
                self.window.history_act_loc[0] += 1
        elif _input == curses.KEY_LEFT:
            pass
        elif _input == curses.KEY_RIGHT:
            pass
        elif _input == curses.KEY_PPAGE:
            if self.window.history_act_loc[0] != 0:
                self.window.history_act_loc[0] -= self.window.history_d[0]
                if self.window.history_act_loc[0] < 0:
                    self.window.history_act_loc[0] = 0
        elif _input == curses.KEY_NPAGE:
            if self.window.history_act_loc[0] != self.window.history_line_written:
                self.window.history_act_loc[0] += self.window.history_d[0]
                if self.window.history_act_loc[0] > self.window.history_line_written:
                    self.window.history_act_loc[0] = self.window.history_line_written

        #
        self.window.history.refresh(*self.window.history_act_loc, *self.window.history_d[2:6])

    def update_type(self, _input: int = None, text: TextCurses = None):
        # todo python3.10 match case
        if _input is None:
            pass
        elif _input == -1:
            return
        elif _input == curses.KEY_UP:
            pass
        elif _input == curses.KEY_DOWN:
            pass
        elif _input == curses.KEY_LEFT:
            pass
        elif _input == curses.KEY_RIGHT:
            pass
        elif _input == curses.KEY_ENTER:
            if self.window.type_buffer == "":
                return
            message = Message(
                text=bytes(self.window.type_buffer, "utf-8"),
                sender=Member(id_=0),
                chat=self.chat_visible,
                _timestamp=time.strftime(S.TIMESTAMP_FORMAT)
            )
            EventMsgSend(message)
            self.update_history(message=message)
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

    def update_keybinding(self):
        self.window.keybinding.clear()
        self.window.keybinding.insstr(
            0, 0,
            auto_linebreak(
                text=self.language.translate("keybinding"),
                max_lines=self.window.keybinding_d[0],
                max_char_in_line=self.window.keybinding_d[1],
                split_char=" ",
            )
        )
        self.window.keybinding.refresh()

    def update_field(self, visible: bool = True, _input: int = None,
                     text: TextCurses = None, finally_do: callable = None, refresh: bool = False):
        """

        :param visible: is this window visible, default True
        :param _input: the input char
        :param text: The text what is shown up, formatted:
        an insert place: <"name"|number how many chars|"regex"|"predefined value">

        :param finally_do: what should be done with the input? Your method here
        it must be like: def finally_method(*args, field_name = field_value, ..): ...
        :param refresh: if the update field should be refreshed
        :return:
        """
        def to_main():
            self.window.field_finally(**dict(
                (field_input[0], field_input[5]) for field_input in self.window.field_input
            ))
            self.window.field_finally = None
            self.window.field_string = ""
            self.window.field_input = []
            self.window.field_act_input = -1
            self.window.field_act_lines = 0
            self.window.field_act_loc = [0, 0]
            self.focus = "chat"
            self.update_screen()
            self.refresh_all()

        def refresh_field():  # todo what if a linebreak is in the input field
            shown_string, field_linebreaks = auto_linebreak_with_linebreak_info(
                self.window.field_string,
                max_char_in_line=self.window.field_d[7],
                split_char=" "
            )
            self.window.field_act_lines = shown_string.count("\n") + 1
            for insert_field in self.window.field_input:
                linebreaks = bisect.bisect_left(field_linebreaks, (insert_field[6], insert_field[7] + 1))
                insert_field[1] = linebreaks + insert_field[6]
                insert_field[2] = insert_field[7]
                if linebreaks and field_linebreaks[linebreaks-1][0] == insert_field[6]:
                    insert_field[2] -= field_linebreaks[linebreaks-1][1]
            self.window.field.clear()
            self.window.field.insstr(
                0,
                0,
                shown_string,
            )
            for insert_field in self.window.field_input:
                self.window.field.addstr(
                    insert_field[1],
                    insert_field[2],
                    insert_field[5][-insert_field[4]:].rjust(insert_field[4], "_"),
                    curses.color_pair(2),
                )
            self.window.field.refresh(*self.window.field_act_loc, *self.window.field_d[2:6])

        if not visible:
            return to_main()

        if refresh:
            return refresh_field()

        if text is not None:
            self.focus = "field"
            #
            if finally_do is None:
                def finally_method(*args, **kwargs):
                    """
                    do something with the input
                    :param kwargs: dict with name and value
                    :return:
                    """
                    pass
                finally_do = finally_method

            self.window.field_finally = finally_do
            self.window.field_input = []
            pure_text = ""
            raw_text = text.text
            while raw_text.count("<"):
                insert_field = ["", 0, 0, "", 0, "", 0, 0]
                # (name: str,
                # y_actual_place: int,
                # x_actual_place: int,
                # regex: str,
                # placeholder_chars: int,
                # actual_data: str,
                # y_real_place: int,
                # x_real_place: int),
                part_pure_text, raw_text = raw_text.split("<\"", 1)
                pure_text += part_pure_text
                insert_field[0], raw_text = raw_text.split("\"|", 1)
                insert_field[4], raw_text = raw_text.split("|\"", 1)
                insert_field[3], raw_text = raw_text.split("\"|\"", 1)
                insert_field[5], raw_text = raw_text.split("\">", 1)
                pure_text_lines = pure_text.split("\n")
                insert_field[6] = len(pure_text_lines) - 1
                insert_field[7] = len(pure_text_lines[-1])
                # str to int
                insert_field[6] = int(insert_field[6])
                insert_field[7] = int(insert_field[7])
                insert_field[4] = int(insert_field[4])
                self.window.field_input.append(insert_field)
                pure_text += insert_field[5][-insert_field[4]:].rjust(insert_field[4], "_")
            if not text.text.count("<"):
                pure_text = text.text
            self.window.field_string = pure_text
            self.window.field_act_input = int(len(self.window.field_input) > 0) - 1
            return refresh_field()

        if _input == -1:
            return
        elif _input is None:
            return
        elif _input == curses.KEY_ENTER:
            if self.window.field_act_input == -1:
                return to_main()
            if re.search(
                    self.window.field_input[self.window.field_act_input][3],
                    self.window.field_input[self.window.field_act_input][5]
            ):
                self.window.field_act_input += 1
                # the regex is found in this input field, go to the next input field
            if self.window.field_act_input == len(self.window.field_input):
                self.window.field_act_input = 0  # todo is this necessary?
                return to_main()
            # go to the input field in the pad
            self.window.field_act_loc[0] = self.window.field_input[self.window.field_act_input][1]

        elif _input == curses.KEY_UP:
            if self.window.field_act_loc[0] != 0:
                self.window.field_act_loc[0] -= 1
        elif _input == curses.KEY_DOWN:
            if self.window.field_act_loc[0] != self.window.field_act_lines - 1:
                self.window.field_act_loc[0] += 1
        elif _input == curses.KEY_BACKSPACE:
            act_field = self.window.field_input[self.window.field_act_input]
            act_field[5] = act_field[5][:-1]
            self.window.field.addstr(
                act_field[1],
                act_field[2],
                act_field[5][-act_field[4]:].rjust(act_field[4], "_"),
                curses.color_pair(2),
            )
        elif self._is_printable_char(_input):
            act_field = self.window.field_input[self.window.field_act_input]
            act_field[5] += chr(_input)
            self.window.field.addstr(
                act_field[1],
                act_field[2],
                act_field[5][-act_field[4]:].rjust(act_field[4], "_"),
                curses.color_pair(2),
            )
        self.window.field.refresh(*self.window.field_act_loc, *self.window.field_d[2:6])

    def refresh_all(self):
        """
        You have to call this, to see all changes in the terminal
        :return:
        """
        self.window.debug.refresh()
        self.window.chat.refresh(0, 0, *self.window.chat_d[2:6])  # todo this have to be better, without the 0, 0
        self.window.history.refresh(*self.window.history_act_loc, *self.window.history_d[2:6])
        self.window.type.refresh()

    def run(self):
        focus_def = {
            "chat": self.update_chat,
            "history": self.update_history,
            "type": self.update_type,
            "field": self.update_field,
        }

        TerminalResized()

        while running:
            # input
            char_input = self.input()
            if self.focus in focus_def.keys():
                focus_def[self.focus](_input=char_input)

            # terminal resized ?
            self.terminal_resized() if self._terminal_resized else None

            # debug window
            self.update_debug(text=TextCurses(f"Focus: {self.focus}", 1, 0))
            self.update_debug(text=TextCurses(f"Chat:  {self.chat_visible.display_name}", 2, 0))
            self.update_debug(text=TextCurses(f"Time: {time.strftime(S.TIMESTAMP_FORMAT)}", 3, 0))
            self.update_debug(text=TextCurses(f"help: {self.config.k_help}", 4, 0))
            # TODO tmp
            self.update_debug(text=TextCurses(f"TMP: events {len(thread_objects.events.events)}", 0, 0))
        print(information(_type=str))

    def stop(self):
        """
        Stopped the terminal interface
        :return:
        """
        self.__del__()


class Terminal(Interface):
    def __init__(self):
        self.curses = CursesWindow()
        super(Terminal, self).__init__()

    def __del__(self):
        del self.curses

    def input(self, text: str = "") -> str:
        self.curses.update_field(visible=True, text=TextCurses(text))
        # todo wait for output
        return ""

    def decide(self, decide_txt: str, decide_options: dict) -> bool:
        #self.curses.update_field(visible=True, text=TextCurses(decide_txt)) # TODO display error
        # todo wait for output
        return True  # todo should be rewritten, it should send back, what was to decide

    def get_db_name(self) -> str:
        if self.curses.config.path_database[0] == "~":
            self.curses.config.path_database = os.path.expanduser("~") + self.curses.config.path_database[1:]
        return self.curses.config.path_database

    def show_msg(self, message: Member):
        pass

    def show_chat(self, chat: Chat):
        self.curses.focus = "history"
        self.curses.chat_visible = chat

    def show_member(self, member):
        pass

    def show_chat_list(self, chat_list: list):
        self.curses.focus = "chat"

    def show_member_list(self, member_list: list):
        pass

    def show_self(self):
        pass

    def commands(self, input_cmd: str):  # needed ?
        pass

    def run(self):
        for chat in object_library[Chat]:
            self.curses.update_chat(chat=chat)
        # self.curses.update_chat(chat=Chat(name="self", display_name="command line 1"))  # todo
        # self.curses.update_chat(chat=Chat(name="self2", display_name="command line 2 - super long name without text"))
        EventUpdateDB()
        self.curses.run()

    def stop(self):
        self.curses.stop()
