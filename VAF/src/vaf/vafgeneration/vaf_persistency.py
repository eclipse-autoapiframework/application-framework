# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Generator library for persistency."""

from pathlib import Path
from typing import Any

from vaf import vafmodel

from ..core.common.utils import create_name_namespace_full_name
from .generation import FileHelper, Generator


def _get_used_namespaces_and_name(
    model: vafmodel.MainModel,
) -> tuple[list[str], list[str]]:
    used_namespaces: list[str] = []
    used_names: list[str] = []

    # add vaf::String
    used_namespaces.append("vaf")
    used_names.append(create_name_namespace_full_name("String", "vaf"))

    for am in model.ApplicationModules:
        if am.DataTypesForSerialization is not None:
            for dts in am.DataTypesForSerialization:
                data = dts.TypeRef
                if data.Namespace not in used_namespaces:
                    used_namespaces.append(data.Namespace)

                full_name = create_name_namespace_full_name(data.Name, data.Namespace)
                if full_name not in used_names:
                    used_names.append(full_name)

    return used_names, used_namespaces


def _get_includes(model: vafmodel.MainModel) -> list[str]:
    includes: list[str] = []
    for array in model.DataTypeDefinitions.Arrays:
        includes.append('#include "' + array.Namespace.replace("::", "/") + "/impl_type_" + array.Name.lower() + '.h"')
    for vector in model.DataTypeDefinitions.Vectors:
        includes.append(
            '#include "' + vector.Namespace.replace("::", "/") + "/impl_type_" + vector.Name.lower() + '.h"'
        )
    for map_entry in model.DataTypeDefinitions.Maps:
        includes.append(
            '#include "' + map_entry.Namespace.replace("::", "/") + "/impl_type_" + map_entry.Name.lower() + '.h"'
        )
    for string in model.DataTypeDefinitions.Strings:
        includes.append(
            '#include "' + string.Namespace.replace("::", "/") + "/impl_type_" + string.Name.lower() + '.h"'
        )
    for enum in model.DataTypeDefinitions.Enums:
        includes.append('#include "' + enum.Namespace.replace("::", "/") + "/impl_type_" + enum.Name.lower() + '.h"')
    for struct in model.DataTypeDefinitions.Structs:
        includes.append(
            '#include "' + struct.Namespace.replace("::", "/") + "/impl_type_" + struct.Name.lower() + '.h"'
        )
    for type_ref in model.DataTypeDefinitions.TypeRefs:
        includes.append(
            '#include "' + type_ref.Namespace.replace("::", "/") + "/impl_type_" + type_ref.Name.lower() + '.h"'
        )
    includes = list(set(includes))
    return includes


# pylint: disable=too-many-locals, too-many-statements
def _generate_interface(
    model: vafmodel.MainModel,
    output_dir: Path,
    generator: Generator,
    verbose_mode: bool = False,
) -> None:
    interface_name = "PersistencyInterface"
    interface_file = FileHelper(interface_name, "persistency")
    module_name = "Persistency"
    module_file = FileHelper(module_name, "persistency")
    kvs_interface_name = "KvsInterface"
    kvs_interface_file = FileHelper(kvs_interface_name, "persistency")
    module_mock_name = "PersistencyMock"
    module_mock_file = FileHelper(module_mock_name, "persistency")

    import_datatype_namespaces: list[str] = []
    import_datatype_names: list[str] = []
    includes: list[str] = []

    import_datatype_names, import_datatype_namespaces = _get_used_namespaces_and_name(model)
    includes = sorted(_get_includes(model))

    proto_basetype_dict = {}
    proto_basetype_dict["UInt64"] = "std::uint64_t"
    proto_basetype_dict["UInt32"] = "std::uint32_t"
    proto_basetype_dict["UInt16"] = "std::uint16_t"
    proto_basetype_dict["UInt8"] = "std::uint8_t"
    proto_basetype_dict["Int64"] = "std::int64_t"
    proto_basetype_dict["Int32"] = "std::int32_t"
    proto_basetype_dict["Int16"] = "std::int16_t"
    proto_basetype_dict["Int8"] = "std::int8_t"
    proto_basetype_dict["Bool"] = "bool"
    proto_basetype_dict["Float"] = "float"
    proto_basetype_dict["Double"] = "double"

    generator.set_base_directory(output_dir / "test-gen/mocks/interfaces")
    generator.generate_to_file(
        module_mock_file,
        ".h",
        "vaf_persistency/persistency_module_mock_h.jinja",
        module_name=module_mock_name,
        namespaces=import_datatype_namespaces,
        datatype_names=import_datatype_names,
        proto_basetype_dict=proto_basetype_dict,
        includes=includes,
        interface_file=interface_file,
        verbose_mode=verbose_mode,
    )

    generator.set_base_directory(output_dir / "src-gen/libs/interfaces")

    generator.generate_to_file(
        interface_file,
        ".h",
        "vaf_persistency/persistency_interface_h.jinja",
        module_name=interface_name,
        namespaces=import_datatype_namespaces,
        datatype_names=import_datatype_names,
        proto_basetype_dict=proto_basetype_dict,
        includes=includes,
        verbose_mode=verbose_mode,
    )

    generator.set_base_directory(output_dir / "src-gen/libs/persistency")

    # Depending on the used persistency library, add wrapper and cmake dependencies
    cmake_libraries = []
    cmake_find_packages = []
    jinja_per_h_file = ""
    jinja_per_cpp_file = ""
    extra_includes: list[Any] = []
    cmake_find_packages.append("leveldb")
    cmake_libraries.append("leveldb::leveldb")
    jinja_per_h_file = "vaf_persistency/persistency_module_h_leveldb.jinja"
    jinja_per_cpp_file = "vaf_persistency/persistency_module_cpp_leveldb.jinja"

    generator.generate_to_file(
        module_file,
        ".h",
        jinja_per_h_file,
        module_name=module_name,
        namespaces=import_datatype_namespaces,
        datatype_names=import_datatype_names,
        proto_basetype_dict=proto_basetype_dict,
        interface_file=interface_file,
        kvs_interface_file=kvs_interface_file,
        verbose_mode=verbose_mode,
    )

    generator.generate_to_file(
        module_file,
        ".cpp",
        jinja_per_cpp_file,
        module_name=module_name,
        namespaces=import_datatype_namespaces,
        datatype_names=import_datatype_names,
        proto_basetype_dict=proto_basetype_dict,
        kvs_interface_file=kvs_interface_file,
        verbose_mode=verbose_mode,
    )

    generator.generate_to_file(
        FileHelper("CMakeLists", "", True),
        ".txt",
        "vaf_persistency/module_cmake.jinja",
        target_name="vaf_persistency",
        files=[module_file],
        packages=cmake_find_packages,
        libraries=[
            "vaf_core",
            "vaf_protobuf",
            "vaf_protobuf_transformer",
        ]
        + cmake_libraries,
        verbose_mode=verbose_mode,
        extra_includes=extra_includes,
    )


# pylint: enable=too-many-locals


def generate(model: vafmodel.MainModel, output_dir: Path, verbose_mode: bool = False) -> None:
    """Generates the middleware wrappers for persistency

    Args:
        model (vafmodel.MainModel): The main model
        output_dir (Path): The output path
        verbose_mode: flag to enable verbose_mode mode
    """
    generator = Generator()
    _generate_interface(model, output_dir, generator, verbose_mode=verbose_mode)
