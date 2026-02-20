# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Generator library for protobuf serialization/deserialization."""

from pathlib import Path
from typing import Dict, List

from vaf import vafmodel
from vaf.vafpy.core import VafpyAbstractBase
from vaf.vafpy.model_runtime import ModelRuntime

from .generation import (
    FileHelper,
    Generator,
    data_type_to_str,
)


def data_type_to_proto_type(data_type: vafmodel.DataType) -> str:
    """Converts a DataType to string

    Args:
        data_type (vafmodel.DataType): The data type

    Returns:
        str: DataType as string
    """
    result = ""
    if data_type.is_cstdint_type:
        match data_type.Name:
            case "uint8_t":
                result = "uint32"
            case "uint16_t":
                result = "uint32"
            case "uint32_t":
                result = "uint32"
            case "uint64_t":
                result = "uint64"
            case "int8_t":
                result = "int32"
            case "int16_t":
                result = "int32"
            case "int32_t":
                result = "int32"
            case "int64_t":
                result = "int64"
            case _:
                result = "data_type.Name"
    else:
        result = (
            "protobuf." + data_type.Namespace.replace("::", ".") + "." + data_type.Name
            if data_type.Namespace != ""
            else data_type.Name
        )

    return result


def __add_datatype_double_colon(datatype: vafmodel.DataType) -> str:
    return "::" if not datatype.is_base_type else ""


def __add_double_colon(name: str, namespace: str) -> str:
    return __add_datatype_double_colon(vafmodel.DataType(Name=name, Namespace=namespace))


def _get_operation_parameter_list_with_in(operation: vafmodel.Operation) -> str:
    parameter_str = ""
    is_first = True
    for parameter in operation.Parameters:
        if not parameter.is_direction_out:
            if is_first:
                parameter_str = (
                    "const "
                    + __add_datatype_double_colon(parameter.TypeRef)
                    + data_type_to_str(parameter.TypeRef)
                    + "& in_"
                    + parameter.Name
                )
                is_first = False
            else:
                parameter_str = (
                    parameter_str
                    + ", const "
                    + __add_datatype_double_colon(parameter.TypeRef)
                    + data_type_to_str(parameter.TypeRef)
                    + "& in_"
                    + parameter.Name
                )
    return parameter_str


def _get_operation_parameter_list_with_out(operation: vafmodel.Operation) -> str:
    parameter_str = ""
    is_first = True
    for parameter in operation.Parameters:
        if not parameter.is_direction_out:
            if is_first:
                parameter_str = (
                    __add_datatype_double_colon(parameter.TypeRef)
                    + data_type_to_str(parameter.TypeRef)
                    + "& out_"
                    + parameter.Name
                )
                is_first = False
            else:
                parameter_str = (
                    parameter_str
                    + ", "
                    + __add_datatype_double_colon(parameter.TypeRef)
                    + data_type_to_str(parameter.TypeRef)
                    + "& out_"
                    + parameter.Name
                )
    return parameter_str


def _add_namespace_to_import(data_type: vafmodel.DataTypeRef, namespace: str, used_namespaces: List[str]) -> bool:
    return (
        not data_type.is_cpp_base_type
        and data_type.Namespace != namespace
        and data_type.Namespace not in used_namespaces
    )


def _get_namespace_imports(
    namespace_object_Dict: Dict[str, Dict[str, Dict[str, VafpyAbstractBase]]],
) -> Dict[str, List[str]]:
    namespace_imports: Dict[str, List[str]] = {}

    for namespace, data in namespace_object_Dict.items():
        if namespace not in namespace_imports:
            namespace_imports[namespace] = []
        for data_type in vafmodel.data_types:
            for dt in data.get(data_type, {}).values():
                if isinstance(dt, vafmodel.Struct):
                    namespace_imports[namespace] += [
                        x.TypeRef.Namespace
                        for x in dt.SubElements
                        if _add_namespace_to_import(x.TypeRef, namespace, namespace_imports[namespace])
                    ]
                elif isinstance(dt, vafmodel.Map):
                    namespace_imports[namespace] += [
                        *(
                            [dt.MapKeyTypeRef.Namespace]
                            if _add_namespace_to_import(
                                dt.MapKeyTypeRef,
                                namespace,
                                namespace_imports[namespace],
                            )
                            else []
                        ),
                        *(
                            [dt.MapValueTypeRef.Namespace]
                            if _add_namespace_to_import(
                                dt.MapValueTypeRef,
                                namespace,
                                namespace_imports[namespace],
                            )
                            else []
                        ),
                    ]
                elif isinstance(dt, (vafmodel.Array, vafmodel.TypeRef, vafmodel.Vector)):
                    namespace_imports[namespace] += (
                        [dt.TypeRef.Namespace]
                        if _add_namespace_to_import(dt.TypeRef, namespace, namespace_imports[namespace])
                        else []
                    )
        # make imports List unique
        namespace_imports[namespace] = list(set(namespace_imports[namespace]))

    return namespace_imports


def _get_used_namespaces_by_interface(interface: vafmodel.ModuleInterface) -> List[str]:
    used_namespaces: List[str] = []
    for x in interface.DataElements:
        if _add_namespace_to_import(x.TypeRef, "", used_namespaces):
            used_namespaces.append(x.TypeRef.Namespace)
    for op in interface.Operations:
        for x in op.Parameters:  # type: ignore[assignment]
            if _add_namespace_to_import(x.TypeRef, "", used_namespaces):
                used_namespaces.append(x.TypeRef.Namespace)
    return used_namespaces


def _generate_proto_files(
    output_path: Path,
    generator: Generator,
    verbose_mode: bool = False,
) -> None:
    generator.set_base_directory(output_path)

    proto_translate_dict = {}
    proto_translate_dict["UInt64"] = "uint64"
    proto_translate_dict["UInt32"] = "uint32"
    proto_translate_dict["UInt16"] = "uint32"
    proto_translate_dict["UInt8"] = "uint32"
    proto_translate_dict["Int64"] = "int64"
    proto_translate_dict["Int32"] = "int32"
    proto_translate_dict["Int16"] = "int32"
    proto_translate_dict["Int8"] = "int32"
    proto_translate_dict["Bool"] = "bool"
    proto_translate_dict["Float"] = "float"
    proto_translate_dict["Double"] = "double"

    generator.generate_to_file(
        FileHelper("protobuf_basetypes", "", True),
        ".proto",
        "vaf_protobuf/basetypes_proto.jinja",
        proto_translate_dict=proto_translate_dict,
        verbose_mode=verbose_mode,
    )

    namespace_imports = _get_namespace_imports(ModelRuntime().element_by_namespace)

    for namespace, data in ModelRuntime().element_by_namespace.items():
        generator.generate_to_file(
            FileHelper("protobuf_" + namespace.replace("::", "_"), "", True),
            ".proto",
            "vaf_protobuf/data_type_proto.jinja",
            str=str,
            package=namespace.replace("::", "."),
            namespace_data=data,
            len=len,
            data_type_to_proto_type=data_type_to_proto_type,
            imports=namespace_imports[namespace],
            verbose_mode=verbose_mode,
        )

    for interface in ModelRuntime().main_model.ModuleInterfaces:
        import_datatype_namespaces = _get_used_namespaces_by_interface(interface)

        generator.generate_to_file(
            FileHelper(
                "protobuf_interface_" + interface.Namespace.replace("::", "_") + "_" + interface.Name,
                "",
                True,
            ),
            ".proto",
            "vaf_protobuf/interface_proto.jinja",
            str=str,
            interface=interface,
            package="interface." + interface.Namespace.replace("::", ".") + "." + interface.Name,
            len=len,
            data_type_to_proto_type=data_type_to_proto_type,
            imports=import_datatype_namespaces,
            verbose_mode=verbose_mode,
        )

    generator.generate_to_file(
        FileHelper("CMakeLists", "", True),
        ".txt",
        "vaf_protobuf/protobuf_cmake.jinja",
        target_name="vaf_protobuf",
        libraries=[
            "protobuf::protobuf",
        ],
        verbose_mode=verbose_mode,
    )


def _get_impl_type_include(data: vafmodel.ModelDataType) -> str:
    return '#include "' + data.Namespace.replace("::", "/") + "/impl_type_" + data.Name.lower() + '.h"'


def _get_array_vector_type_ref_includes(
    data: vafmodel.Array | vafmodel.Vector | vafmodel.TypeRef,
) -> List[str]:
    includes: List[str] = [_get_impl_type_include(data)]
    if not data.TypeRef.is_cpp_base_type:
        includes.append(
            '#include "' + data.TypeRef.Namespace.replace("::", "/") + "/impl_type_" + data.TypeRef.Name.lower() + '.h"'
        )
        if not data.Namespace == data.TypeRef.Namespace:
            includes.append(
                '#include "protobuf/' + data.TypeRef.Namespace.replace("::", "/") + '/protobuf_transformer.h"'
            )
        includes.append('#include "protobuf_' + data.TypeRef.Namespace.replace("::", "_") + '.pb.h"')

    return includes


def _get_struct_includes(data: vafmodel.Struct) -> List[str]:
    includes: List[str] = [_get_impl_type_include(data)]
    for sub_element in data.SubElements:
        if not sub_element.TypeRef.is_cpp_base_type:
            includes.append(
                '#include "'
                + sub_element.TypeRef.Namespace.replace("::", "/")
                + "/impl_type_"
                + sub_element.TypeRef.Name.lower()
                + '.h"'
            )
            if not data.Namespace == sub_element.TypeRef.Namespace:
                includes.append(
                    '#include "protobuf/'
                    + sub_element.TypeRef.Namespace.replace("::", "/")
                    + '/protobuf_transformer.h"'
                )
            includes.append('#include "protobuf_' + sub_element.TypeRef.Namespace.replace("::", "_") + '.pb.h"')

    return includes


def _get_map_includes(data: vafmodel.Map) -> List[str]:
    includes: List[str] = [_get_impl_type_include(data)]

    for map_attr in ["MapKeyTypeRef", "MapValueTypeRef"]:
        map_type_ref = getattr(data, map_attr)
        assert isinstance(map_type_ref, vafmodel.DataType)
        if not map_type_ref.is_cpp_base_type:
            includes.append(
                '#include "'
                + map_type_ref.Namespace.replace("::", "/")
                + "/impl_type_"
                + map_type_ref.Name.lower()
                + '.h"'
            )
            if not data.Namespace == map_type_ref.Namespace:
                includes.append(
                    '#include "protobuf/' + map_type_ref.Namespace.replace("::", "/") + '/protobuf_transformer.h"'
                )
            includes.append('#include "protobuf_' + map_type_ref.Namespace.replace("::", "_") + '.pb.h"')

    return includes


# pylint:disable=too-many-locals
# pylint:disable=too-many-branches
# pylint:disable=too-many-statements
def _generate_transformer_files(
    output_path: Path,
    generator: Generator,
    verbose_mode: bool = False,
) -> None:
    generator.set_base_directory(output_path)

    for namespace, data in ModelRuntime().element_by_namespace.items():
        if not namespace:
            raise ValueError("Input json contains 'DataTypeDefinition' with empty namespace ")

        includes: List[str] = [
            '#include "protobuf_' + namespace.replace("::", "_") + '.pb.h"',
            "#include <cstdlib>",
            '#include "vaf/output_sync_stream.h"',
        ]
        for vector_array_typeref in (
            list(data.get("Arrays", {}).values())
            + list(data.get("Vectors", {}).values())
            + list(data.get("TypeRefs", {}).values())
        ):
            if isinstance(
                vector_array_typeref,
                (vafmodel.Array, vafmodel.Vector, vafmodel.TypeRef),
            ):
                includes += _get_array_vector_type_ref_includes(vector_array_typeref)
        for map_entry in data.get("Maps", {}).values():
            if isinstance(map_entry, vafmodel.Map):
                includes += _get_map_includes(map_entry)
        for string in data.get("Strings", {}).values():
            if isinstance(string, vafmodel.String):
                includes.append(_get_impl_type_include(string))
        for enum in data.get("Enums:", {}).values():
            if isinstance(enum, vafmodel.VafEnum):
                includes.append(_get_impl_type_include(enum))
        for struct in data.get("Structs", {}).values():
            if isinstance(struct, vafmodel.Struct):
                includes += _get_struct_includes(struct)

        includes = list(set(includes))
        includes.sort()

        generator.generate_to_file(
            FileHelper("protobuf_transformer", "protobuf::" + namespace, False),
            ".h",
            "vaf_protobuf/data_type_transformer.jinja",
            includes=includes,
            namespace=namespace,
            proto_namespace=namespace.replace("::", "_"),
            include_namespace=namespace.replace("::", "/"),
            namespace_data=data,
            data_type_to_proto_type=data_type_to_proto_type,
            verbose_mode=verbose_mode,
        )

    for interface in ModelRuntime().main_model.ModuleInterfaces:
        includes = []
        import_datatype_namespaces = _get_used_namespaces_by_interface(interface)

        operation_with_out_parameters: List[vafmodel.Operation] = []
        for o in interface.Operations:
            out_parameters: List[vafmodel.Parameter] = []
            for p in o.Parameters:
                if p.Direction is not vafmodel.ParameterDirection.IN:
                    out_parameters.append(p)

            if len(out_parameters) > 0:
                operation_with_out_parameters.append(o)

        out_parameter_type_namespace: str = interface.Namespace

        generator.generate_to_file(
            FileHelper(
                "protobuf_transformer",
                "protobuf::interface::" + interface.Namespace + "::" + interface.Name,
                False,
            ),
            ".h",
            "vaf_protobuf/interface_transformer.jinja",
            interface=interface,
            out_parameter_type_namespace=out_parameter_type_namespace,
            operation_with_out_parameters=operation_with_out_parameters,
            data_type_to_proto_type=data_type_to_proto_type,
            generate_types=False,
            imports=import_datatype_namespaces,
            get_operation_parameter_list_with_in=_get_operation_parameter_list_with_in,
            get_operation_parameter_list_with_out=_get_operation_parameter_list_with_out,
            add_double_colon=__add_double_colon,
            add_datatype_double_colon=__add_datatype_double_colon,
            verbose_mode=verbose_mode,
        )

    generator.generate_to_file(
        FileHelper("CMakeLists", "", True),
        ".txt",
        "common/cmake_interface_library.jinja",
        target_name="vaf_protobuf_transformer",
        libraries=["vaf_module_interfaces"],
        verbose_mode=verbose_mode,
    )


# pylint: disable=duplicate-code
def generate(output_dir: Path, verbose_mode: bool = False) -> None:
    """Generates the middleware wrappers for protobuf

    Args:
        output_dir (Path): The output path
        verbose_mode: flag to enable verbose_mode mode
    """
    output_path = output_dir / "src-gen/libs/protobuf_serdes"

    generator = Generator()

    subdirs: List[str] = []
    subdirs.append("proto")
    subdirs.append("transformer")
    generator.set_base_directory(output_path)
    generator.generate_to_file(
        FileHelper("CMakeLists", "", True),
        ".txt",
        "common/cmake_subdirs.jinja",
        subdirs=subdirs,
        verbose_mode=verbose_mode,
    )

    output_path = output_dir / "src-gen/libs/protobuf_serdes/proto"
    _generate_proto_files(output_path, generator, verbose_mode=verbose_mode)
    output_path = output_dir / "src-gen/libs/protobuf_serdes/transformer"
    _generate_transformer_files(output_path, generator, verbose_mode=verbose_mode)
