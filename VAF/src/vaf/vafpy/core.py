# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Module providing config as code for VAF projects."""

from abc import ABCMeta, abstractmethod
from collections import defaultdict
from threading import Lock
from typing import Dict, List

from vaf import vafmodel

# pylint: disable=too-few-public-methods


class ModelError(Exception):
    """Exception class for modeling errors"""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class BaseTypesWrapper:
    """Wrapper for std types"""

    @property
    def type_ref(self) -> vafmodel.DataTypeRef:
        """Method to get typeref from current instance
        Returns:
            Respective string typeref of current instance
        """
        return vafmodel.DataType(Name=self.Name, Namespace=self.Namespace)

    def __init__(self, name: str, namespace: str = "") -> None:
        self.Name = name
        self.Namespace = namespace
        self.TypeRef = self.type_ref


class BaseTypes:
    """All c++ std base types"""

    INT8_T = BaseTypesWrapper("int8_t")
    INT16_T = BaseTypesWrapper("int16_t")
    INT32_T = BaseTypesWrapper("int32_t")
    INT64_T = BaseTypesWrapper("int64_t")
    UINT8_T = BaseTypesWrapper("uint8_t")
    UINT16_T = BaseTypesWrapper("uint16_t")
    UINT32_T = BaseTypesWrapper("uint32_t")
    UINT64_T = BaseTypesWrapper("uint64_t")
    FLOAT = BaseTypesWrapper("float", "")
    DOUBLE = BaseTypesWrapper("double", "")
    BOOL = BaseTypesWrapper("bool", "")
    STRING = BaseTypesWrapper("String", "vaf")


# pylint: disable=too-few-public-methods
# pylint: disable=super-init-not-called
class VafpyAbstractBase(vafmodel.DataType, BaseTypesWrapper):
    """Base Abstract class for VafpyObject"""

    def __init__(self) -> None:
        """
        Raises:
            ModelError: if initialized
        """
        raise ModelError("Dude, who told you to construct this forbidden class?")


class _SingletonMeta(type):
    """
    This is a thread-safe implementation of Singleton.
    """

    _instances: Dict[type, type] = {}

    _lock: Lock = Lock()
    """
    We now have a lock object that will be used to synchronize threads during
    first access to the Singleton.
    """

    # no signature, since this signature will overshadow its users init signature
    # in pylance -> bad intellisense support
    def __call__(cls, *args, **kwargs):  # type:ignore[no-untyped-def]
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        # Now, imagine that the program has just been launched. Since there's no
        # Singleton instance yet, multiple threads can simultaneously pass the
        # previous conditional and reach this point almost at the same time. The
        # first of them will acquire lock and will proceed further, while the
        # rest will wait here.
        with cls._lock:
            # The first thread to acquire the lock, reaches this conditional,
            # goes inside and creates the Singleton instance. Once it leaves the
            # lock block, a thread that might have been waiting for the lock
            # release may then enter this section. But since the Singleton field
            # is already initialized, the thread won't create a new object.
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)  # pylint:disable=no-member
                cls._instances[cls] = instance
        return cls._instances[cls]


class _ABCSingletonMeta(_SingletonMeta, ABCMeta): ...


class VafpyAbstractModelRuntime(metaclass=_ABCSingletonMeta):
    """Abstract Class for ModelRuntime"""

    # Dict that stores namespace & name of used module interfaces
    # and their respectives data_elements & operations typerefs
    used_module_interfaces: Dict[str, List[str]] = {}
    # List that stores the name of internal interfaces
    internal_interfaces: List[str] = []
    # List that stores the name of all connected interfaces
    connected_interfaces: defaultdict[str, List[str]] = defaultdict(list)
    # dictionary that stores vafpy elements by namespace (for CaC)
    # Reason: getter function in runtime.py can get the vafpy elements
    # CaC and some generations are namespace-based: One can access the model
    # by calling <vafpy_element>.vafmodel
    element_by_namespace: Dict[str, Dict[str, Dict[str, VafpyAbstractBase]]] = {}
    main_model: vafmodel.MainModel = vafmodel.MainModel()

    @staticmethod
    def __init_allowed(child: object) -> bool:
        """check if child is allowed to call init
        Args:
            child: child object that calls the super
        Returns:
            boolean for the check result
        """
        return (child.__class__.__name__, child.__class__.__module__) == ("ModelRuntime", "vaf.vafpy.model_runtime")

    def __init__(self) -> None:
        """
        Raises:
            NotImplementedError: for unauthorized childrens
        """
        if self.__init_allowed(self):
            super().__init__()
        else:
            # tell intruders to think if no init is implemented
            raise NotImplementedError("__init__() is not implemented.")

    @classmethod
    def reset(cls) -> None:
        """Resets the model runtime"""
        cls.main_model = vafmodel.MainModel()
        cls.used_module_interfaces.clear()
        cls.internal_interfaces.clear()
        cls.connected_interfaces.clear()
        cls.element_by_namespace.clear()

    @abstractmethod
    def remove_element(self, element: VafpyAbstractBase) -> None:
        """Remove an element from the model
        Args:
            element: element to be removed from the model
        Raises:
            NotImplementedError
        """
        raise NotImplementedError("remove_element is not implemented.")

    @abstractmethod
    def replace_element(self, element: VafpyAbstractBase) -> None:
        """Replace an element with same name & namespace
        Args:
            element: element to be replaced in the model
        Raises:
            NotImplementedError
        """
        raise NotImplementedError("replace_element() is not implemented.")
