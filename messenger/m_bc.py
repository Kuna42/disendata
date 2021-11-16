
# import
from messenger.m_abc import BaseAddClass, object_library
from messenger.static_variables import S


# classes
class Member(BaseAddClass):
    def __new__(cls, *args, **kwargs):
        print("a")
        if "id_" not in kwargs.keys():
            print("b")
            kwargs["id_"] = len(object_library[cls]) + 100  # TODO could be better
            print(kwargs["id_"])
        print("c")
        return super().__new__(cls, identification_attribute="id_", args=args, kwargs=kwargs)

    def __init__(self, address: tuple,
                 id_: int = 0, name_self: str = "", name_given: str = "",
                 name_generic: str = "", cryptic_hash: str = ""):
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
    def __init__(self, *members):
        self.name = ""  # name of the session
        self.self_ip = ""
        self.group = {}

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

    def has_member(self, name: str) -> bool:
        return name in self.group.keys()

    def new_member(self, member: Member):
        self.group[member.actual_ip] = member


class Chat(BaseAddClass):
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, identification_attribute="name", args=args, kwargs=kwargs)

    def __init__(self, name, members: [Member],
                 display_name: str = "", info: str = ""):
        self.name = name
        self.member = members  # [Member]
        self.display_name = display_name
        self.info = info


class Message:
    def __init__(self, text: bytes, to_member: Member, chat: Chat, m_type="msg"):
        self.text = text
        self.receiver = to_member
        self.chat = chat
        self.__timestamp = 0  # TODO timestamp muss eingefügt werden

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


class Tunnel: # probably not necessary
    def __init__(self):
        self.__dict = dict()

    def get(self, obj: object, standard_sort_key="id") -> object:
        for element in self.__dict[type(obj)]:
            if getattr(element, standard_sort_key) == getattr(obj, standard_sort_key):
                obj = self.__dict[type(obj)] + obj  # the object overwrites the object in the list

    def add_object_list(self, _class) -> bool:
        if _class in self.__dict.keys():
            return False
        self.__dict[_class] = []
        return True


class Messenger:
    pass


object_library[Member] = []
object_library[Chat] = []
