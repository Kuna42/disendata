
# import
from messenger.m_abc import BaseAddClass
from messenger.variables import S, object_library, thread_objects


# classes
class Member(BaseAddClass):
    def __new__(cls, *args, **kwargs):
        identify_attr = "id_"
        if "identification_attribute" in kwargs.keys():
            if kwargs["identification_attribute"] in ("id_", "name_self", "address", "name_generic"):
                identify_attr = kwargs.pop("identification_attribute")

        if identify_attr not in kwargs.keys():
            kwargs[identify_attr] = len(object_library[cls]) + 100  # TODO could be better
        return super().__new__(cls, *args, identification_attribute=identify_attr, **kwargs)

    def __init__(self, *, address: tuple = ("", 0),
                 id_: int = 0, name_self: str = "", name_given: str = "",
                 name_generic: str = "", cryptic_hash: str = "",
                 identification_attribute: str = "id_"):
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
        self.actual_ip = value[0]
        if value[1] == 0:
            self.port = S.PORT
        else:
            self.port = value[1]


class MemberGroup:
    def __init__(self, *members: Member, sort_key: str = "actual_ip"):
        self.name = ""  # name of the session
        self.self_ip = ""
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

        :param other: an other member_group with the same class

        :return: this object, self
        """
        if type(self) is not type(other):
            raise NotImplementedError("This addition was not implemented")
        new_group = MemberGroup()
        new_group.name = other.name
        new_group = self.group#
        new_group.update(other.group)#
        self.group = new_group
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
    def __new__(cls, *args, **kwargs):
        identify_attr = "name"
        if "identification_attribute" in kwargs.keys():
            if kwargs["identification_attribute"] in ("name", "display_name"):
                identify_attr = kwargs["identification_attribute"]

        if identify_attr not in kwargs.keys():
            kwargs[identify_attr] = len(object_library[cls]) + 100  # TODO could be better
        return super().__new__(cls, *args, identification_attribute=identify_attr, **kwargs)

    def __init__(self, *, name, members: MemberGroup = None,
                 display_name: str = "", info: str = "",
                 identification_attribute: str = "name"):
        if members is None:
            members = MemberGroup()
        self.name = name
        self.member = members  # [Member]
        self.display_name = display_name
        self.info = info


class Message:
    def __init__(self, text: bytes, sender: Member, chat: Chat,
                 to_member: Member = None, m_type="msg", _timestamp: str = ""):
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
        return str(self.text)

    @property
    def timestamp(self):
        return self.__timestamp


class Messenger:
    def start(self):
        self.run()
        thread_objects.network.db.open_chats()
        thread_objects.network.db.open_members()

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
