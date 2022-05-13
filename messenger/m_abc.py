#!/usr/bin/env python3

# import
from messenger.variables import object_library, thread_objects

from abc import ABC, abstractmethod
from threading import Thread

# variables


# classes
class BaseAddClass(ABC):
    _identify_attr = {
        # a dict of all identification attributes with type
        # "id": int,
    }
    _identify_attr_default = ""

    def __new__(cls, *args, identification_attribute: str = None, **kwargs):
        """
        Checks if an object already with this identification.

        :param args:
        :param identification_attribute: the attribute, what is the one to check if it exists None = default
        :param kwargs:
        """
        if identification_attribute not in cls._identify_attr:
            identification_attribute = cls._identify_attr_default
        if identification_attribute in kwargs:
            for obj in object_library[cls]:
                if getattr(obj, identification_attribute) == kwargs[identification_attribute]:
                    # set attributes
                    for attribute in kwargs:
                        setattr(obj, attribute, kwargs[attribute])
                    return obj
        else:
            # create a new identification attribute, what is generic
            reserved_identify = set()
            for obj in object_library[cls]:
                reserved_identify.add(getattr(obj, identification_attribute))
            if cls._identify_attr[identification_attribute] is int:
                kwargs[identification_attribute] = (set(range(0, len(reserved_identify) + 1))
                                                    - reserved_identify).pop()
            elif cls._identify_attr[identification_attribute] is str:
                attribute_string = "generic0x"
                for alphanum in "0123456789abcdef":
                    if attribute_string + alphanum not in reserved_identify:
                        kwargs[identification_attribute] = attribute_string + alphanum
                        break
            else:
                raise ValueError(f"Unsupported value of the identification attribute,"
                                 f"to generate one. "
                                 f"'{cls._identify_attr[identification_attribute]}' "
                                 f"is not supported.")

        obj = super().__new__(cls)
        object_library[cls].append(obj)
        obj.__initialised = False
        return obj

    def __add__(self, other):  # TODO probably remove able
        """
        self + other

        the self will be overwritten with the attributes of other, if the attributes of other are "True"

        :param other: another object with the same class

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

    def __init__(self, *args, **kwargs):
        """
        The _BaseAddClass_initialised attribute should be asked,
        when in the subclass __init__ is called, like so:
        (write this at the top of your __init__)


        if getattr(self, "_BaseAddClass__initialised", False):
            return
        super().__init__(self)
        """
        self.__initialised = True

        """
        write this at the top of your __init__  method:
        
        if getattr(self, "_BaseAddClass__initialised", False):
            return
        super().__init__(self)
        """


class Event:
    @abstractmethod
    def __init__(self, _is_done: bool = False):
        """
        Created an Event obj witch will be added to the Eventmanager, that this will execute this event.

        :param _is_done: default(False)
        """
        self._is_done = _is_done
        thread_objects.events.append(self)

    @property
    @abstractmethod
    def content(self):
        """
        Returned a dict with all content of the event

        :return: dict
        """
        return {}

    def done(self) -> bool:
        return self._is_done


class Interface(ABC, Thread):
    @abstractmethod
    def __init__(self):
        """
        This should be called the subclass, because the Tread should be init.
        """
        super(Interface, self).__init__()

    @abstractmethod
    def input(self) -> str:
        pass

    @abstractmethod
    def decide(self, decide_txt: str, decide_options: dict) -> bool:
        """
        Is used for pop up some choices.

        :param decide_txt: What text should be shown (what choice is it)
        :param decide_options: All decides in one dictionary, they are like: str: method,
        the method will only be executed, if it was chosen.
        :return:
        """
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
        """
        Is used for the threading module, witch run the whole time

        :return:
        """
        pass

    @abstractmethod
    def stop(self):
        """
        Stopped the Interface, for a clean exit
        :return:
        """
        pass
