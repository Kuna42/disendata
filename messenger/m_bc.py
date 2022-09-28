
# import
import os

from messenger.m_abc import BaseAddClass
from messenger.variables import S, object_library, thread_objects


# classes
class Member(BaseAddClass):
    _identify_attr = {
        "id_": int,
        "name_self": str,
        "address": tuple,
        "name_generic": str,
        "name_given": str
    }
    _identify_attr_default = "id_"

    """
    def __new__(cls, *args, **kwargs):
        identify_attr = "id_"
        if "identification_attribute" in kwargs.keys():
            if kwargs["identification_attribute"] in ("id_", "name_self", "address", "name_generic", "name_given"):
                identify_attr = kwargs.pop("identification_attribute")

        if identify_attr not in kwargs.keys():
            kwargs[identify_attr] = len(object_library[cls]) + 100  # TODO could be better
        return super().__new__(cls, *args, identification_attribute=identify_attr, **kwargs)
    """  # TODO check if this is possible

    def __init__(self, *, address: tuple = ("", 0),
                 id_: int = 0, name_self: str = "", name_given: str = "",
                 name_generic: str = "", cryptic_hash: str = "",
                 identification_attribute: str = _identify_attr_default):
        """

        :param address: your internet address
        :param id_: the environment (db) specific id, type this only,
        when you know the id of a member
        :param name_self: how he calls himself
        :param name_given: the nane you give
        :param name_generic: an generic (mostly, identifiable) name
        :param cryptic_hash: (todo implement this)
        :param identification_attribute: this is only useful to change,
        when you want to catch a specific member with one attribute
        """
        if getattr(self, "_BaseAddClass__initialised", False):
            return
        super().__init__(self)

        #self.id_
        reserved_identify = set()
        for obj in object_library[Member]:
            reserved_identify.add(getattr(obj, identification_attribute, None))
        if id_ in reserved_identify:
            #raise ValueError(f"The identifier (id_) of '{name_generic}' have to be unique")
            id_ = (set(range(0, len(reserved_identify) + 1)) #todo is this right?
                   - reserved_identify).pop()
        self.id_ = id_
        self.name_self = name_self
        self.name_given = name_given
        self.name_generic = name_generic
        self.crypt_hash = cryptic_hash
        self.actual_ip = ""
        self.port = S.PORT
        self.address = address

    @property
    def address(self):
        return self.actual_ip, self.port

    @address.setter
    def address(self, value: tuple):
        if len(value) != 2:
            raise AttributeError("Wrong address, correct: (IPv4, Port)")
        if value[0] == "":
            self.actual_ip = "127.0.0.1"
        else:
            self.actual_ip = value[0]
        if value[1] == 0:
            self.port = S.PORT
        else:
            self.port = value[1]


class MemberGroup:
    def __init__(self, *members: Member, sort_key: str = "actual_ip"):
        """

        :param members: a list of members
        :param sort_key: how the group is sorted
        """
        self.name = ""  # name of the session
        self.group = {}
        if sort_key not in ("actual_ip", "address", "id_", "name_generic"):
            sort_key = "actual_ip"
        self.sort_key = sort_key
        for member in members:
            self.new_member(member)

    def __add__(self, other):
        """
        self + other

        the self will be overwritten with the attributes of other, if the attributes of other are "True"

        :param other: another member_group with the same class

        :return: this object, self
        """
        if type(self) is not type(other):
            raise NotImplementedError("This addition was not implemented")
        if self.sort_key != other.sort_key:
            raise ValueError("These two Member groups should have the same sort key.")
        self.name = other.name
        self.group.update(other.group)
        return self

    def has_member(self, name: Member or str) -> bool:
        if type(name) is str:
            return name in self.group.keys()
        return getattr(name, self.sort_key) in self.group.keys()

    def new_member(self, member: Member):
        self.group[getattr(member, self.sort_key)] = member

    def all_members(self) -> [Member]:
        member_list = []
        for member in self.group.values():
            member_list.append(member)
        return member_list


class Chat(BaseAddClass):
    _identify_attr = {
        "name": str,
        "display_name": str
    }
    _identify_attr_default = "name"

    def __init__(self, *, name, members: MemberGroup = None,
                 display_name: str = "", info: str = "",
                 identification_attribute: str = _identify_attr_default):
        """

        :param name: the identifying name
        :param members: class MemberGroup (a list of members)
        :param display_name: name that is shown
        :param info: what specific detailed information have the group
        :param identification_attribute: this is only useful to change,
        when you want to catch a specific chat with one attribute
        """
        if getattr(self, "_BaseAddClass__initialised", False):
            return
        super().__init__(self)
        if not members:
            members = MemberGroup()
        self.name = name
        self.members = members  # [Member]
        #if not hasattr(self, "display_name") and display_name != "":
        self.display_name = display_name
        self.info = info
        self.unread_msg = 0  # TODO this must be in the database too
        self.type_buffer = ""  # TODO this must be implemented


class Message:
    def __init__(self, text: bytes, sender: Member, chat: Chat,
                 to_member: Member = None, m_type="msg", _timestamp: str = ""):
        """

        :param text: the content of the message
        :param sender: the autor of the message
        :param chat: for what chat is this message for
        :param to_member: the receiver
        :param m_type: msg = Text, cmd = Commands, tmp = Temporary,
        data = Data like pictures,
        :param _timestamp:
        """
        if to_member is None:
            to_member = Member(id_=0)
        self.text = text
        self.receiver = to_member
        self.sender = sender
        self.chat = chat
        if not _timestamp:
            pass  # TODO timestamp muss eingefügt werden
        self.__timestamp = _timestamp

        if m_type in S.MSG_START.keys():
            self.m_type = m_type
        else:
            raise AttributeError(f"This Message can not be a {m_type}, "
                                 f"it must be some of the set [{S.MSG_START.keys()}]")

    def __str__(self):
        return str(self.text, "utf-8")

    @property
    def timestamp(self):
        return self.__timestamp


class Filecheck:
    @staticmethod
    def file(filepath: str) -> bool:
        os_name = os.uname().sysname
        if os_name == "Linux":
            return Filecheck.linux(filepath)
        elif os_name == "Windows":
            return Filecheck.windows(filepath)
        raise OSError("Not known OS. Please check if you run a Linux Distro or Windows.")

    @staticmethod
    def linux(filepath: str) -> bool:
        if filepath.startswith("/") is (filepath[0] == "~"):
            raise SyntaxError("filename should be a complete path like /tmp/test.db")
        if filepath[0] == "~":
            filepath = os.path.expanduser("~") + filepath[1:]
        if filepath.split("/")[1] not in {"tmp", "home", "etc", ".disendata"}:
            # if the db was in a global directory or in a local directory like ".disendata"
            raise PermissionError(f"You can't open this database")
        if not os.path.exists("/".join(filepath.split("/")[:-1])):
            raise FileNotFoundError("This file/path does not exists. File can't be created.")
        return True

    @staticmethod
    def windows(filepath: str) -> bool:
        return True


def auto_linebreak_with_linebreak_info(text: str, max_char_in_line: int, max_lines: int = None,
                                       split_char: str = None) -> (str, list):
    """
    add linebreaks into a sting after a specific length of a line
    :param text: the raw text
    :param max_char_in_line: how many chars fit maximum in the line
    :param max_lines: if a line maximum is there, it would be marked with ...
    :param split_char: to split words that are separated with a special char like space
    :return: the text with linebreaks, and a list with: (line, char_of_linebreak)
    """
    linebreak_points = []
    simple_text = text.split("\n")
    for text_line_count, text_line in enumerate(simple_text):
        new_text_line = ""
        text_char = 0
        while text_char < len(text_line):
            text_part = text_line[text_char:(text_char + max_char_in_line)]
            if (split_char is None) or (len(text_part) < max_char_in_line - 1):
                new_text_line += text_part + "\n"
                text_char += max_char_in_line
                continue
            if split_char is None:
                new_text_line += text_part + "\n"
                text_char += max_char_in_line
                linebreak_points.append((text_line_count, text_char))
                continue
            text_part = text_part.rsplit(split_char, 1)
            if len(text_part) == 1:
                new_text_line += text_part[0] + "\n"
                text_char += max_char_in_line
                linebreak_points.append((text_line_count, text_char))
                continue
            new_text_line += text_part[0] + "\n"
            text_char += len(text_part[0]) + 1
            linebreak_points.append((text_line_count, text_char))

        if text_line != "":
            new_text_line = new_text_line[:-1]
        simple_text[text_line_count] = new_text_line

    if max_lines is None:
        return "\n".join(simple_text), linebreak_points

    text = "\n".join(simple_text).split("\n")
    if len(text) > max_lines:
        text = text[0:max_lines]
        text[max_lines - 1] = "..."
    return "\n".join(text), linebreak_points


def auto_linebreak(text: str, max_char_in_line: int, max_lines: int = None, split_char: str = None) -> str:
    """
    add linebreaks into a sting after a specific length of a line
    :param text: the raw text
    :param max_char_in_line: how many chars fit maximum in the line
    :param max_lines: if a line maximum is there, it would be marked with ...
    :param split_char: to split words that are separated with a special char like space
    :return: the text with linebreaks
    """
    return auto_linebreak_with_linebreak_info(
        text=text,
        max_char_in_line=max_char_in_line,
        max_lines=max_lines,
        split_char=split_char
    )[0]


class Messenger:
    def start(self):
        thread_objects.network.db.open_chats()
        thread_objects.network.db.open_members()
        self.run()

    def run(self):
        thread_objects.start()


class ThreadObjectLibrary:
    def __init__(self):
        self.network = None
        self.events = None
        self.interface = None

    def start(self):
        self.network.name = "network-Thread"
        self.events.name = "event-Thread"
        self.interface.name = "interface-Thread"
        self.network.start()
        self.events.start()
        self.interface.start()


object_library[Member] = []
object_library[Chat] = []
