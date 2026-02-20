# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Generator for VAF data types.
Generates
    - data_type.h
    - CMakeLists.txt
"""

from pathlib import Path

from vaf import vafmodel
from vaf.vafpy.model_runtime import ModelRuntime

from .generation import FileHelper, Generator, get_data_type_include


def _get_file_helper(data_type: vafmodel.DataType) -> FileHelper:
    return FileHelper(data_type.Name, data_type.Namespace)


# pylint: disable-next=too-many-locals,too-many-branches
def generate(output_dir: Path, verbose_mode: bool = False) -> None:
    """Generate VAF data types

    Args:
        output_dir (Path): The output directory
        verbose_mode: flag to enable verbose_mode mode
    """
    generator = Generator()

    generator.set_base_directory(output_dir / "src-gen/libs/data_types")

    for namespace, data in ModelRuntime().element_by_namespace.items():
        for array in data.get("Arrays", {}).values():
            generator.generate_to_file(
                FileHelper("impl_type_" + array.Name.lower(), namespace),
                ".h",
                "vaf_std_data_types/array_h.jinja",
                array=array,
                get_file_helper=_get_file_helper,
                get_data_type_include=get_data_type_include,
                verbose_mode=verbose_mode,
            )

        for vaf_enum in data.get("Enums", {}).values():
            generator.generate_to_file(
                FileHelper("impl_type_" + vaf_enum.Name.lower(), namespace),
                ".h",
                "vaf_std_data_types/enum_h.jinja",
                vaf_enum=vaf_enum,
                get_data_type_include=get_data_type_include,
                verbose_mode=verbose_mode,
            )

        for vaf_map in data.get("Maps", {}).values():
            generator.generate_to_file(
                FileHelper("impl_type_" + vaf_map.Name.lower(), namespace),
                ".h",
                "vaf_std_data_types/map_h.jinja",
                vaf_map=vaf_map,
                get_file_helper=_get_file_helper,
                get_data_type_include=get_data_type_include,
                verbose_mode=verbose_mode,
            )

        for vaf_string in data.get("Strings", {}).values():
            generator.generate_to_file(
                FileHelper("impl_type_" + vaf_string.Name.lower(), namespace),
                ".h",
                "vaf_std_data_types/string_h.jinja",
                vaf_string=vaf_string,
                get_data_type_include=get_data_type_include,
                verbose_mode=verbose_mode,
            )

        for vaf_struct in data.get("Structs", {}).values():
            assert isinstance(vaf_struct, vafmodel.Struct)
            includes: list[str] = []
            for sub in vaf_struct.SubElements:
                includes.append(get_data_type_include(sub.TypeRef))
            includes = list(set(includes))
            if "" in includes:
                includes.remove("")
            generator.generate_to_file(
                FileHelper("impl_type_" + vaf_struct.Name.lower(), namespace),
                ".h",
                "vaf_std_data_types/struct_h.jinja",
                vaf_struct=vaf_struct,
                get_file_helper=_get_file_helper,
                includes=includes,
                get_data_type_include=get_data_type_include,
                verbose_mode=verbose_mode,
            )

        for vaf_type_ref in data.get("TypeRefs", {}).values():
            generator.generate_to_file(
                FileHelper("impl_type_" + vaf_type_ref.Name.lower(), namespace),
                ".h",
                "vaf_std_data_types/type_ref_h.jinja",
                vaf_type_ref=vaf_type_ref,
                get_file_helper=_get_file_helper,
                get_data_type_include=get_data_type_include,
                verbose_mode=verbose_mode,
            )

        for vaf_vector in data.get("Vectors", {}).values():
            generator.generate_to_file(
                FileHelper("impl_type_" + vaf_vector.Name.lower(), namespace),
                ".h",
                "vaf_std_data_types/vector_h.jinja",
                vaf_vector=vaf_vector,
                get_file_helper=_get_file_helper,
                get_data_type_include=get_data_type_include,
                verbose_mode=verbose_mode,
            )
