# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Generator for vaf core library.
Generates
    Core library
"""

from pathlib import Path
from typing import Any

from .generation import FileHelper, Generator


def __generate_internal(
    templates_dir: str,
    output_dir: Path,
    file_type: str,
    namespace: str,
    verbose_mode: bool = False,
    **kwargs: Any,
) -> None:
    generator = Generator()
    generator.set_base_directory(output_dir)

    templates = Path(__file__).resolve().parent / "templates" / templates_dir

    for filename in templates.iterdir():
        base_file_name = filename.stem
        if base_file_name.endswith("_" + file_type):
            generator.generate_to_file(
                FileHelper(base_file_name.rstrip("_" + file_type), namespace, True),
                "." + file_type,
                templates_dir + filename.name,
                verbose_mode=verbose_mode,
                **kwargs,
            )


def generate(
    output_dir: Path,
    type_variant: str,
    verbose_mode: bool = False,
) -> None:
    """Generate files for VAF core support

    Args:
        output_dir (Path): Base output directory
        type_variant (str): Type variant of the generated data types
        verbose_mode: flag to enable verbose_mode mode
    """
    output_path = output_dir / "src-gen/libs/core_library"

    generator = Generator()
    generator.set_base_directory(output_path)

    __generate_internal("vaf_core_library/common/src/", output_path, "cpp", "", verbose_mode, lib_type=type_variant)
    __generate_internal(
        "vaf_core_library/common/include/", output_path, "h", "vaf", verbose_mode, lib_type=type_variant
    )
    __generate_internal(
        "vaf_core_library/common/include/internal/",
        output_path,
        "h",
        "vaf/internal",
        verbose_mode,
        lib_type=type_variant,
    )

    __generate_internal("vaf_core_library/std/src/", output_path, "cpp", "", verbose_mode)
    __generate_internal("vaf_core_library/std/include/", output_path, "h", "vaf", verbose_mode)
    __generate_internal("vaf_core_library/std/include/tl/", output_path, "h", "tl", verbose_mode)
    __generate_internal("vaf_core_library/std/include/internal/", output_path, "h", "vaf/internal", verbose_mode)

    generator.generate_to_file(
        FileHelper("CMakeLists", "", True),
        ".txt",
        "vaf_core_library/common/cmake.jinja",
        verbose_mode=verbose_mode,
        lib_type=type_variant,
    )
