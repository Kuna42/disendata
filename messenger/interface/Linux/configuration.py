
# import
import os

from messenger.m_bc import Chat
from messenger.variables import LinuxS


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

    def change(self, **kwargs):  # todo is this needed? no?
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
        if language in LinuxS.LANGUAGE_DICTIONARY_NAMES.keys():  # todo this could be better
            self.language = language
        else:
            self.language = "en_UK"

    def __str__(self):
        return self.language

    def translate(self, text: str) -> str:  # TODO this need to be included and be written
        """
        This translates the standard text into a specific language
        :param text:
        :return:
        """
        return text

    def spellcheck(self, *words: str, marker_start: str = "~~", marker_end: str = "~~") -> [str]:  # TODO actual a bad idea, maybe it could be better
        """
        checks if those words are all in the selected language
        :param words: all words are strings
        :param marker_start: how should the words be marked at the beginning
        :param marker_end: how the end of the word is marked
        :return: the same list, but the words are now marked
        """
        words = list(words)
        checked_words = ["" * len(words)]
        for dict_word in open(LinuxS.LANGUAGE_DICTIONARY_PATH + LinuxS.LANGUAGE_DICTIONARY_NAMES[self.language][0]):  # TODO the [0] is only tmp
            for index, word in enumerate(words):
                if word == "":
                    continue
                if word == dict_word[:-1]:
                    checked_words[index] = word
                    words[index] = ""
        for index, word in enumerate(words):
            if word == "":
                continue
            checked_words[index] = marker_start + word + marker_end
            words[index] = ""
        return checked_words
