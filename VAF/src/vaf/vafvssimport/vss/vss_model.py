# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Module containing the VSS model."""

from collections import defaultdict
from typing import Any

from vaf import vafmodel

from . import vss_types


class VSS:  # pylint: disable=too-few-public-methods
    """Class representing the VSS model"""

    def __init__(self, vss_json: dict[str, Any]) -> None:
        """Instanciates a VSS Model

        Args:
            vss_json (dict[str, Any]): The complete VSS input as JSON dict
        """

        self.datatypes_per_namespace: defaultdict[str, set[vss_types.BaseType]] = defaultdict(set)

        self._import_vss(vss_json)

    def export(self) -> vafmodel.MainModel:
        """Exports the VSS model to a VAF model

        Returns:
            vafmodel.MainModel: complete model containing VSS data
        """

        model = vafmodel.MainModel()

        data_type_definitions = vafmodel.DataTypeDefinition()
        for _, datatypes in self.datatypes_per_namespace.items():
            data_type_definitions.Structs += [dt.export() for dt in datatypes if isinstance(dt, vss_types.StructType)]
            data_type_definitions.Enums += [dt.export() for dt in datatypes if isinstance(dt, vss_types.EnumType)]
            data_type_definitions.Arrays += [dt.export() for dt in datatypes if isinstance(dt, vss_types.ArrayType)]
            data_type_definitions.Vectors += [dt.export() for dt in datatypes if isinstance(dt, vss_types.VectorType)]
            data_type_definitions.TypeRefs += [
                dt.export() for dt in datatypes if isinstance(dt, vss_types.PrimitiveType)
            ]

        # Add vaf::String
        data_type_definitions.Strings = [vafmodel.String(Name="String", Namespace="vaf")]

        model.DataTypeDefinitions = data_type_definitions

        return model

    def _import_vss(self, vss_json: dict[str, Any]) -> None:
        self.datatypes_per_namespace.clear()

        for vss_key, vss_value in vss_json.items():
            self._create_struct(vss_value=vss_value, namespace_with_name="vss::" + vss_key)

    def _create_struct(self, vss_value: dict[str, Any], namespace_with_name: str) -> vss_types.StructType:
        """
        Creates a struct for a VSS (Vehicle Signal Specification) branch.

        Raises:
            ValueError: If the 'type' in the vss_branch is not 'branch', or if required keys are missing or invalid.
        """
        namespace, name = namespace_with_name.rsplit("::", 1)

        if vss_value["type"] != "branch":
            raise ValueError("JSON does not contain a 'branch' type.")
        struct_type = vss_types.StructType(name=name, namespace=namespace.lower())

        for subelement_key, subelement_value in vss_value["children"].items():
            if subelement_value["type"] == "branch":
                struct_type.subelements.append(
                    self._create_struct(
                        vss_value=subelement_value, namespace_with_name=f"{namespace}::{name}::{subelement_key}"
                    )
                )
                continue
            if "allowed" in subelement_value and subelement_value["datatype"] == "string":
                struct_type.subelements.append(
                    self._create_enum(
                        vss_value=subelement_value, namespace_with_name=f"{namespace}::{name}::{subelement_key}"
                    )
                )
                continue
            if "[]" in subelement_value["datatype"] and "arraysize" in subelement_value:
                struct_type.subelements.append(
                    self._create_array(
                        vss_value=subelement_value, namespace_with_name=f"{namespace}::{name}::{subelement_key}"
                    )
                )
                continue
            if "[]" in subelement_value["datatype"]:
                struct_type.subelements.append(
                    self._create_vector(
                        vss_value=subelement_value, namespace_with_name=f"{namespace}::{name}::{subelement_key}"
                    )
                )
                continue
            struct_type.subelements.append(
                self._create_primitive_type(
                    vss_value=subelement_value, namespace_with_name=f"{namespace}::{name}::{subelement_key}"
                )
            )

        self.datatypes_per_namespace[namespace.lower()].add(struct_type)
        return struct_type

    def _create_enum(self, vss_value: dict[str, Any], namespace_with_name: str) -> vss_types.EnumType:
        """Handles enum creation."""

        namespace, name = namespace_with_name.rsplit("::", 1)

        enum_type = vss_types.EnumType(name=name, namespace=namespace.lower())
        allowed_values = vss_value["allowed"]

        for idx, literal in enumerate(allowed_values, start=1):
            enum_type.add_literal(item=literal, value=idx)

        self.datatypes_per_namespace[namespace_with_name.lower()].add(enum_type)
        return enum_type

    def _create_array(self, vss_value: dict[str, Any], namespace_with_name: str) -> vss_types.ArrayType:
        """Handles array creation."""

        namespace, name = namespace_with_name.rsplit("::", 1)

        primitive_type_name = vss_value["datatype"][:-2]  # Remove "[]"
        array_type = vss_types.ArrayType(
            name=name,
            namespace=namespace,
            type_name=primitive_type_name,
            array_size=vss_value["arraysize"],
        )

        self.datatypes_per_namespace[namespace.lower()].add(array_type)
        return array_type

    def _create_vector(self, vss_value: dict[str, Any], namespace_with_name: str) -> vss_types.VectorType:
        """Handles vector creation."""

        namespace, name = namespace_with_name.rsplit("::", 1)

        primitive_type_name = vss_value["datatype"][:-2]  # Remove "[]"
        vector_type = vss_types.VectorType(name=name, namespace=namespace, type_name=primitive_type_name)

        self.datatypes_per_namespace[namespace.lower()].add(vector_type)
        return vector_type

    def _create_primitive_type(self, vss_value: dict[str, Any], namespace_with_name: str) -> vss_types.PrimitiveType:
        """Handles primitive type creation."""

        namespace, name = namespace_with_name.rsplit("::", 1)

        min_value = vss_value.get("min")
        max_value = vss_value.get("max")

        primitive_type: vss_types.PrimitiveType

        if vss_types.is_numeric(datatype=vss_value["datatype"]):
            primitive_type = vss_types.PrimitiveType(
                name=name,
                namespace=namespace.lower(),
                type_name=vss_value["datatype"],
                min_value=min_value,
                max_value=max_value,
            )
        else:
            primitive_type = vss_types.PrimitiveType(name=name, namespace=namespace, type_name=vss_value["datatype"])

        self.datatypes_per_namespace[namespace.lower()].add(primitive_type)
        return primitive_type


# pylint: enable=too-few-public-methods
