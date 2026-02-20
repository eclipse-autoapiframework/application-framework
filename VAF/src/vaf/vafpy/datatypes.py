# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Abstraction layer for the datatypes in Config as Code."""

from typing import Any, List, Optional, Tuple

from vaf import vafmodel

from .core import BaseTypes, BaseTypesWrapper, ModelError, VafpyAbstractBase
from .factory import VafpyFactory
from .model_runtime import ModelRuntime

# pylint: disable = too-few-public-methods
# pylint: disable = unused-private-member # Used via decorators
# pylint: disable = super-init-not-called # DUE to decorators' use
# pylint: disable = unused-argument # DUE to overload in decorator
# pylint: disable = protected-access
# pylint:disable=too-many-ancestors
# mypy: disable-error-code="misc"


class Enum(vafmodel.VafEnum, VafpyAbstractBase):
    """The VAF::Enum datatype"""

    __last_value: int

    def __init__(
        self,
        name: str,
        namespace: str,
        literals: Optional[List[vafmodel.EnumLiteral | Tuple[str, int] | str]] = None,
    ) -> None:
        VafpyFactory.create(constructor=vafmodel.VafEnum, obj=self, Name=name, Namespace=namespace, Literals=[])
        # -1 because first next value will start with 0
        self.__last_value = -1
        if literals is not None:
            self.add_literal_list(self.__list_to_vafmodel_literal(literals))  # type:ignore[arg-type]  # pylint:disable=no-member,line-too-long # false positive due to inheritance

    def add_literal(self, item: str, value: Optional[int] = None) -> None:
        """Add a literal to the enum definition.

        Args:
            item (str): The label of the enum entry
            value (int): The value of the enum entry

        Raises:
            ModelError: If entry labels are invalid or duplicated
        """
        self.Literals.append(self.__to_vafmodel_literal((item, value) if value is not None else item))  # pylint:disable=no-member,line-too-long # false positive due to inheritance

    def add_literal_list(self, literals: List[vafmodel.EnumLiteral | Tuple[str, int] | str]) -> None:
        """Add list of literals to the enum definition.

        Args:
            literals: list of literals to be added

        Raises:
            ModelError: If entry labels are invalid or duplicated
        """
        self.Literals += self.__list_to_vafmodel_literal(literals)  # pylint:disable=no-member # false positive due to inheritance

    def __validate_label(self, label: str) -> None:
        """Validate label for no spaces.

        Args:
            label (str): The label of the enum entry

        Raises:
            ModelError: If entry label is invalid
        """
        if " " in label:
            raise ModelError(f"Enum - Label cannot contain spaces: '{label}'")

    def __validate_entry(self, label: str, value: int) -> None:
        """Validate the enum entries.

        Args:
            label (str): The label of the enum entry
            value (int): The value of the enum entry

        Raises:
            ModelError: If entry labels or values are invalid or duplicated
        """
        self.__validate_label(label)

        if not isinstance(value, int):
            raise ModelError(f"Enum - Invalid value of label '{label}', value {value} is not int!")

        if self.Literals:  # pylint:disable=no-member # false positive due to inheritance
            current_labels, current_values = zip(*[(literal.Item, literal.Value) for literal in self.Literals])  # pylint:disable=no-member, line-too-long # false positive due to inheritance
            if current_labels.count(label) > 0:
                raise ModelError(f"Enum - Duplicate label not allowed: '{label}'")
            if current_values.count(value) > 0:
                raise ModelError(f"Enum - Duplicate value not allowed: '{value}' from label '{label}'")

    def __list_to_vafmodel_literal(
        self, input_list: List[vafmodel.EnumLiteral | Tuple[str, int] | str]
    ) -> List[vafmodel.EnumLiteral]:
        """Convert possible list of literals to list of vafmodel.EnumLiteral.

        Args:
            input_list: List that contains possible enum literals' entry

        Returns:
            converted enum literals to list of vafmodel.EnumLiteral

        Raises:
            ModelError: If duplicates found in labels or values
        """

        def __split_literal(
            lit: vafmodel.EnumLiteral,
        ) -> Tuple[vafmodel.EnumLiteral, str, int]:
            return (
                lit,
                lit.Item,
                lit.Value,
            )

        literals, labels, values = zip(
            *[
                __split_literal(val if isinstance(val, vafmodel.EnumLiteral) else self.__to_vafmodel_literal(val))
                for val in input_list
            ]
        )

        # validate labels and values
        if len(labels) != len(set(labels)):
            raise ModelError(
                f"Enum - Duplicate label in constructor: '{[label for label in labels if labels.count(label) > 1]}'"
            )
        if len(values) != len(set(values)):
            raise ModelError(
                "".join(
                    [
                        "Enum - Duplicate value in constructor: ",
                        f"'{[(labels[idx], value) for idx, value in enumerate(values) if values.count(value) > 1]}'",
                    ]
                )
            )

        return list(literals)

    def __to_vafmodel_literal(self, input_value: Tuple[str, int] | str) -> vafmodel.EnumLiteral:
        """Convert a possible enum literal's entry to vafmodel.EnumLiteral

        Args:
            input_value: string for label or tuple of label and value pair

        Returns:
            converted entry to vafmodel.EnumLiteral
        """
        if isinstance(input_value, tuple):
            key, value = input_value
            new_last_value = max(self.__last_value, value)
        else:
            key = input_value
            new_last_value = self.__last_value + 1
            value = new_last_value

        self.__validate_entry(key, value)
        # overwrite __last_value only if validation passes
        self.__last_value = new_last_value
        return vafmodel.EnumLiteral(Item=key, Value=value)


class Map(vafmodel.Map, VafpyAbstractBase):
    """The VAF::Map datatype"""

    def __init__(
        self,
        name: str,
        namespace: str,
        key_type: VafpyAbstractBase | BaseTypesWrapper,
        value_type: VafpyAbstractBase | BaseTypesWrapper,
    ) -> None:
        VafpyFactory.create(
            constructor=vafmodel.Map,
            obj=self,
            Name=name,
            Namespace=namespace,
            MapKeyTypeRef=key_type.type_ref,
            MapValueTypeRef=value_type.type_ref,
        )


class String(vafmodel.String, VafpyAbstractBase):
    """The VAF::String datatype"""

    def __init__(self, name: str, namespace: str) -> None:
        VafpyFactory.create(constructor=vafmodel.String, obj=self, Name=name, Namespace=namespace)


class VafpyFactoryWithTypeRef(VafpyFactory, VafpyAbstractBase):
    """Generic Abstract type for Vafpy datatypes that have typeref"""

    @staticmethod
    def __typeref_exists_in_model(typeref: VafpyAbstractBase | BaseTypesWrapper, object_class: type) -> bool:
        """Method to construct typeref object
        Args:
            typeref: typeref as cac object
            object_class: class of the typeref
        """
        # True if not exists (is None)
        return (
            ModelRuntime()
            .element_by_namespace.get(typeref.Namespace, {})
            .get(object_class.__name__ + "s", {})
            .get(typeref.Name, None)
            is None
        )

    @classmethod
    def check_typeref(cls, typeref: VafpyAbstractBase | BaseTypesWrapper) -> None:
        """Method to checkf if typeref needs construction
        Args:
            typeref: typeref as cac object
        """
        obj_cls: Optional[type[VafpyAbstractBase]]
        match typeref:
            case BaseTypes.STRING:
                obj_cls = String
            case _:
                obj_cls = None

        if obj_cls is not None and cls.__typeref_exists_in_model(typeref, obj_cls):
            # construct the typeref as vafpy object
            obj_cls(typeref.Name, typeref.Namespace)

    @classmethod
    def create(cls, constructor: type[vafmodel.VafBaseModel], obj: VafpyAbstractBase, **kwargs: Any) -> None:
        """Method to build an vafpy module interfaces
        Args:
            constructor: parent of object whose constructor will be used
            obj: object to be built
            kwargs: attributes of the object
        """
        # only for CaC: process given typeref
        if not kwargs.get("imported", False):
            assert isinstance(kwargs["TypeRef"], VafpyAbstractBase | BaseTypesWrapper)
            # store CaC typeref
            cac_typeref = kwargs["TypeRef"]
            # convert typeref in kwargs to vafmodel typeref
            kwargs["TypeRef"] = kwargs["TypeRef"].type_ref
            # construct typeref if needed
            cls.check_typeref(cac_typeref)

        # call parent build instance m
        super().create(constructor=constructor, obj=obj, **kwargs)


class Struct(vafmodel.Struct, VafpyAbstractBase):
    """The VAF::Struct datatype"""

    def __init__(
        self,
        name: str,
        namespace: str,
        sub_elements: Optional[List[vafmodel.SubElement]] = None,
    ) -> None:
        VafpyFactory.create(
            constructor=vafmodel.Struct,
            obj=self,
            Name=name,
            Namespace=namespace,
            SubElements=sub_elements if sub_elements is not None else [],
        )

    def add_subelement(
        self, name: str, datatype: VafpyAbstractBase | BaseTypesWrapper, is_optional: bool = False
    ) -> None:
        """Add a subelement to the struct definition

        Args:
            name (str): The name of the subelement
            datatype (VafpyAbstractBase | BaseTypesWrapper): The type of the subelement
            is_optional (bool): Whether the element is optional (default: False)

        Raises:
            ModelError: If subelement names are duplicated
        """
        if any(element.Name == name for element in self.SubElements):
            raise ModelError(f"Struct - Duplicated subelement: {name}")
        # borrow check typeref from VafpyFactoryWithTypeRef
        VafpyFactoryWithTypeRef.check_typeref(datatype)
        self.SubElements.append(vafmodel.SubElement(Name=name, TypeRef=datatype.type_ref, IsOptional=is_optional))


# pylint: disable = too-many-ancestors
class TypeRef(vafmodel.TypeRef, VafpyAbstractBase):
    """The VAF::TypeRef datatype"""

    def __init__(self, name: str, namespace: str, datatype: VafpyAbstractBase | BaseTypesWrapper) -> None:
        VafpyFactoryWithTypeRef.create(
            constructor=vafmodel.TypeRef, obj=self, Name=name, Namespace=namespace, TypeRef=datatype
        )


class Vector(vafmodel.Vector, VafpyAbstractBase):
    """The VAF::Vector datatype"""

    def __init__(
        self,
        name: str,
        namespace: str,
        datatype: VafpyAbstractBase | BaseTypesWrapper,
    ) -> None:
        VafpyFactoryWithTypeRef.create(
            constructor=vafmodel.Vector, obj=self, Name=name, Namespace=namespace, TypeRef=datatype
        )


class Array(vafmodel.Array, VafpyAbstractBase):
    """The VAF::Array datatype"""

    # Array must have size compared to Vector
    def __init__(self, name: str, namespace: str, datatype: VafpyAbstractBase | BaseTypesWrapper, size: int) -> None:
        VafpyFactoryWithTypeRef.create(
            constructor=vafmodel.Array, obj=self, Name=name, Namespace=namespace, TypeRef=datatype, Size=size
        )
