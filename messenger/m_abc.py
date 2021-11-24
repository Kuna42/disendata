#!/usr/bin/env python3

# import
from messenger.variables import object_library

from abc import ABC, abstractmethod
from threading import Thread

# variables


# classes
class BaseAddClass(ABC):
    @abstractmethod
    def __new__(cls, *args, identification_attribute: str, **kwargs):
        for obj in object_library[cls]:
            if getattr(obj, identification_attribute) == kwargs[identification_attribute]:
                # set attributes
                for attribute in kwargs:
                    setattr(obj, attribute, kwargs[attribute])
                return obj
        obj = super().__new__(cls)
        object_library[cls].append(obj)
        return obj

    def __add__(self, other):  # TODO probably remove able
        """
        self + other

        the self will be overwritten with the attributes of other, if the attributes of other are "True"

        :param other: an other object with the same class

        :return: this object, self
        """
        if type(self) is not type(other):
            raise NotImplementedError("This addition was not implemented")
        attr_ = vars(other)
        for attr_name in attr_:
            attr_value = attr_[attr_name]
            if attr_value:
                setattr(self, attr_name, attr_value)
        return self


class Interface(ABC, Thread):
    @abstractmethod
    def __init__(self):
        super(Interface, self).__init__()

    @abstractmethod
    def input(self) -> str:
        pass

    @abstractmethod
    def decide(self, event) -> bool:
        pass

    @abstractmethod
    def get_db_name(self) -> str:
        pass

    @abstractmethod
    def show_msg(self, message):
        pass

    @abstractmethod
    def show_chat(self, chat):
        pass

    @abstractmethod
    def show_member(self, member):
        pass

    @abstractmethod
    def show_chat_list(self, chat_list: list):
        pass

    @abstractmethod
    def show_member_list(self, member_list: list):
        pass

    @abstractmethod
    def show_self(self):
        pass

    @abstractmethod
    def commands(self, input_cmd: str):
        pass

    @abstractmethod
    def run(self):
        pass
