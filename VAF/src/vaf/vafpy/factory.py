# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Factory to build."""

from typing import Any

from vaf import vafmodel

from .core import ModelError, VafpyAbstractBase
from .model_runtime import ModelRuntime

# pylint: disable=too-few-public-methods


class VafpyFactory:
    """Generic Abstract type for vafpy element"""

    @staticmethod
    def __ensure_name_ns(
        constructor: type[vafmodel.vafmodel.VafBaseModel], name: str | None, namespace: str | None
    ) -> None:
        """Method to ensure name & namespaces of the object
        Args:
            kwargs: attributes to be checked
        Raises:
            ModelError: if name and namespace is not valid
        """
        if name is None and namespace is None:
            type_str = constructor.__name__
            error_msg = "".join(
                [
                    f"Why do you want to initialize {type_str}",
                    "with name = None & namespace = None?",
                ]
            )
            raise ModelError(error_msg)

        assert isinstance(name, str) and isinstance(namespace, str)

        invalid_name_bs: bool = "::" in name

        if "::" in name:
            reason = "Name must not contain character '::'!"
        else:
            reason = "The first character of name and namespace must not be a number!"
            if namespace == "":
                invalid_name_bs |= name[0].isdigit()
            else:
                invalid_name_bs |= name[0].isdigit() or namespace[0].isdigit()

        if invalid_name_bs:
            raise ModelError(reason)

    @classmethod
    def create(cls, constructor: type[vafmodel.VafBaseModel], obj: VafpyAbstractBase, **kwargs: Any) -> None:
        """Method to build an instance of a vafpy element
        Args:
            constructor: parent of object whose constructor will be used
            obj: object if it's already built
            kwargs: attributes of the object
        """
        # ensure validity of attributes
        cls.__ensure_name_ns(
            constructor=constructor, name=kwargs.get("Name", None), namespace=kwargs.get("Namespace", None)
        )
        # construct via vafmodel constructor
        constructor.__init__(  # pylint:disable=unnecessary-dunder-call  # type:ignore[misc]
            obj,
            **{init_args: kwargs[init_args] for init_args in constructor.model_fields.keys() if init_args in kwargs},
        )
        # add to model runtime
        ModelRuntime().add_element(obj, imported=kwargs.get("imported", False))

    @classmethod
    def create_from_model(
        cls,
        vaf_model: vafmodel.VafBaseModel,
        vafpy_class: type[VafpyAbstractBase],
        **kwargs: Any,
    ) -> None:
        """Method to init vafpy object from a vafmodel object
        Args:
            vaf_model: vafmodel object as input
            vafpy_class: vafpy class of the goal object
            kwargs: Other variables
        """
        # append vaf_model attributes to kwargs
        kwargs |= {init_args: getattr(vaf_model, init_args) for init_args in vaf_model.model_fields_set}
        # construct empty instance if obj is none
        obj = vafpy_class.__new__(vafpy_class)
        # construct object from kwargs
        cls.create(constructor=type(vaf_model), obj=obj, **kwargs)
