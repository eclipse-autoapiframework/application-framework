# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Module containing the VSS model."""

from collections import defaultdict
from typing import Any

from vaf import vafmodel

from . import vss_types


class VSS:
    """Class representing the VSS model"""

    # pylint: disable=too-few-public-methods
    class ModuleInterface:
        """Class representing a ModuleInterface in the VSS model"""

        def __init__(self, full_name: str, vss_branch: dict[str, Any]) -> None:
            """Instanciates a VSS ModuleInterface

            Args:
                full_name (str): The name of the module interface including the namespace
                vss_branch (dict[str, Any]): The VSS branch containing the details as JSON dict

            Raises:
                ValueError: If the type of a DataElement is not supported and cannot be resolved.
            """
            self.namespace, self.name = full_name.rsplit("::", 1)
            self.namespace = self.namespace.lower()
            self.data_elements: list[vafmodel.DataElement] = []
            self.operations: list[vafmodel.Operation] = []

            # Add DataElements for the child elements
            # The temporary DataElements are only used to create the TypeRef in the resulting json.
            # Therefore not all fields have to be set for these instances (e.g. min_value is not required).
            for element_name, element in vss_branch["children"].items():
                if "branch" == element["type"]:
                    # Complex types
                    type_ref = vafmodel.DataType(
                        Name=element_name,
                        Namespace=f"{self.namespace}::{self.name}".lower(),
                    )
                    self.data_elements.append(vafmodel.DataElement(Name=element_name, TypeRef=type_ref))
                    continue

                datatype = element["datatype"]
                if "allowed" in element and "string" == datatype:
                    # Enums
                    type_ref = vafmodel.DataType(Name=element_name, Namespace=full_name.lower())
                    self.data_elements.append(vafmodel.DataElement(Name=element_name, TypeRef=type_ref))

                elif "[]" in datatype:
                    primitive_type_name = datatype[:-2]
                    tmp: vss_types.VectorType | vss_types.ArrayType
                    if "arraysize" in element:
                        # Arrays
                        tmp = vss_types.ArrayType("_", primitive_type_name, element["arraysize"])
                    else:
                        # Vectors
                        tmp = vss_types.VectorType("_", primitive_type_name)
                    type_ref = vafmodel.DataType(Name=tmp.getTypeRefStr(), Namespace=tmp.namespace)
                    self.data_elements.append(vafmodel.DataElement(Name=element_name, TypeRef=type_ref))

                else:
                    # Generic primitive types
                    if element["datatype"] not in vss_types.type_translation:
                        raise ValueError(f"Unsupported type '{element['datatype']}' for DataElement '{element_name}'")
                    type_ref = vss_types.type_translation[element["datatype"]]

                    if vss_types.is_numeric(datatype):
                        # Add VSS ranges
                        self.data_elements.append(
                            vafmodel.DataElement(
                                Name=element_name,
                                TypeRef=type_ref,
                                Min=element.get("min"),
                                Max=element.get("max"),
                            )
                        )
                    else:
                        self.data_elements.append(vafmodel.DataElement(Name=element_name, TypeRef=type_ref))

                # VSS actuators shall have a setter callback
                if "actuator" == element["type"]:
                    self.operations.append(
                        vafmodel.Operation(
                            Name=element_name + "_Setter_Callback",
                            Parameters=[
                                vafmodel.Parameter(
                                    Name="new_data",
                                    TypeRef=type_ref,
                                    Direction=vafmodel.ParameterDirection.IN,
                                )
                            ],
                        )
                    )

        def export(self) -> vafmodel.ModuleInterface:
            """Exports VSS ModuleInterface to VAF model ModuleInterface

            Returns:
                vafmodel.ModuleInterface: ModuleInterface containing the VSS data
            """
            return vafmodel.ModuleInterface(
                Name=self.name + "_If",
                Namespace=self.namespace,
                DataElements=self.data_elements,
                Operations=self.operations,
            )

    def __init__(self, vss_json: dict[str, Any]) -> None:
        """Instanciates a VSS Model

        Args:
            vss_json (dict[str, Any]): The complete VSS input as JSON dict
        """

        self.datatypes_per_namespace: defaultdict[str, set[vss_types.BaseType]] = defaultdict(set)
        self.module_interfaces: list[VSS.ModuleInterface] = []

        self._import_vss(vss_json)

    def export(self) -> vafmodel.MainModel:
        """Exports the VSS model to a VAF model

        Returns:
            vafmodel.MainModel: complete model containing VSS data
        """

        model = vafmodel.MainModel()

        model.ModuleInterfaces = [if_.export() for if_ in self.module_interfaces]

        data_type_definitions = vafmodel.DataTypeDefinition()
        for _, datatypes in self.datatypes_per_namespace.items():
            structs = [dt.export() for dt in datatypes if isinstance(dt, vss_types.StructType)]
            enums = [dt.export() for dt in datatypes if isinstance(dt, vss_types.EnumType)]
            data_type_definitions.Arrays += [dt.export() for dt in datatypes if isinstance(dt, vss_types.ArrayType)]
            data_type_definitions.Vectors += [dt.export() for dt in datatypes if isinstance(dt, vss_types.VectorType)]

            data_type_definitions.Structs += structs
            data_type_definitions.Enums += enums

        # Add vaf::String
        data_type_definitions.Strings = [vafmodel.String(Name="String", Namespace="vaf")]

        model.DataTypeDefinitions = data_type_definitions

        return model

    def _import_vss(self, vss_json: dict[str, Any]) -> None:
        self.module_interfaces.clear()
        self.datatypes_per_namespace.clear()

        for name, branch in vss_json.items():
            self._process_branch(branch, "vss::" + name)

    def _process_branch(self, branch: dict[str, Any], full_name: str) -> None:
        # check for existence before
        if branch["type"] == "branch":
            self.module_interfaces.append(self.ModuleInterface(full_name=full_name, vss_branch=branch))
            # Create DataType for specific branch
            self._create_datatype_for_branch(vss_branch=branch, namespace_with_name=full_name)

            # Recursion for deeper branches
            for name, child in branch["children"].items():
                self._process_branch(child, f"{full_name}::{name}")

    def _create_datatype_for_branch(self, vss_branch: dict[str, Any], namespace_with_name: str) -> None:
        """
        Creates a data type for a VSS (Vehicle Signal Specification) branch.

        Raises:
            ValueError: If the 'type' in the vss_branch is not 'branch', or if required keys are missing or invalid.
        """
        ns, dt_name = namespace_with_name.rsplit("::", 1)

        if "branch" != vss_branch["type"]:
            raise ValueError("JSON does not contain a 'branch' type.")
        result_type = vss_types.StructType(name=dt_name, namespace=ns)

        for subelement_name, data_type in vss_branch["children"].items():
            subelement = self._create_subelement(subelement_name, data_type, namespace_with_name)
            result_type.subelements.append(subelement)

        self.datatypes_per_namespace[ns.lower()].add(result_type)

    def _create_subelement(
        self, subelement_name: str, data_type: dict[str, Any], namespace_with_name: str
    ) -> vss_types.BaseType:
        """
        Creates a subelement based on its type and the associated data type.
        """
        if "branch" == data_type["type"]:
            return self._create_struct(subelement_name, namespace_with_name)

        if "allowed" in data_type and "string" == data_type["datatype"]:
            return self._create_enum(subelement_name, data_type, namespace_with_name)

        if "[]" in data_type["datatype"]:
            if "arraysize" in data_type:
                return self._create_array(subelement_name, data_type)
            return self._create_vector(subelement_name, data_type)

        return self._create_primitive_type(subelement_name, data_type)

    def _create_struct(self, subelement_name: str, namespace_with_name: str) -> vss_types.StructType:
        """Handles struct creation."""
        return vss_types.StructType(name=subelement_name, namespace=namespace_with_name)

    def _create_enum(
        self, subelement_name: str, data_type: dict[str, Any], namespace_with_name: str
    ) -> vss_types.EnumType:
        """Handles enum creation."""

        enum_type = vss_types.EnumType(name=subelement_name, namespace=namespace_with_name.lower())
        allowed_values = data_type["allowed"]

        for idx, literal in enumerate(allowed_values, start=1):
            enum_type.add_literal(item=literal, value=idx)

        self.datatypes_per_namespace[namespace_with_name.lower()].add(enum_type)
        return enum_type

    def _create_array(self, subelement_name: str, data_type: dict[str, Any]) -> vss_types.ArrayType:
        """Handles array creation."""
        primitive_type_name = data_type["datatype"][:-2]  # Remove "[]"
        subelement = vss_types.ArrayType(
            name=subelement_name,
            type_name=primitive_type_name,
            array_size=data_type["arraysize"],
        )

        self.datatypes_per_namespace["vss"].add(subelement)
        return subelement

    def _create_vector(self, subelement_name: str, data_type: dict[str, Any]) -> vss_types.VectorType:
        """Handles vector creation."""
        primitive_type_name = data_type["datatype"][:-2]  # Remove "[]"
        subelement = vss_types.VectorType(name=subelement_name, type_name=primitive_type_name)

        self.datatypes_per_namespace["vss"].add(subelement)
        return subelement

    def _create_primitive_type(self, subelement_name: str, data_type: dict[str, Any]) -> vss_types.PrimitiveType:
        """Handles primitive type creation."""
        min_value = data_type.get("min")
        max_value = data_type.get("max")

        if vss_types.is_numeric(datatype=data_type["datatype"]):
            return vss_types.PrimitiveType(
                name=subelement_name,
                type_name=data_type["datatype"],
                min_value=min_value,
                max_value=max_value,
            )

        return vss_types.PrimitiveType(name=subelement_name, type_name=data_type["datatype"])


# pylint: enable=too-few-public-methods
