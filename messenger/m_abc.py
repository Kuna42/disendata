#!/usr/bin/env python3

# import
from abc import ABC, abstractmethod

# variables
# globals
global object_library
object_library = {}


# classes
class BaseAddClass(ABC):
    @abstractmethod
    def __new__(cls, identification_attribute: str, *args, **kwargs):
        for obj in object_library[cls]:
            if getattr(obj, identification_attribute) == kwargs[identification_attribute]:
                # set attributes
                return obj
        obj = super().__new__(cls)
        object_library[cls].append(obj)
        return obj

    def __add__(self, other):
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


class Interface(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def show_msg(self):
        pass

    @abstractmethod
    def run(self):
        pass
