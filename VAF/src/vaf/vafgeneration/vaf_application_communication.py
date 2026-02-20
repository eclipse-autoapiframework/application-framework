# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Generator for application communication modules.
Generates
    - module.h
    - module.cpp
    - CMakeLists.txt
    - Top level CMakeLists.txt
"""

from pathlib import Path

from vaf import vafmodel
from vaf.core.common.utils import to_snake_case

from .generation import FileHelper, Generator


def generate(model: vafmodel.MainModel, output_dir: Path, verbose_mode: bool = False) -> None:
    """Generate files for application communication modules

    Args:
        model (vafmodel.MainModel): The model
        output_dir (Path): Base output directory
        verbose_mode: flag to enable verbose_mode mode
    """
    output_path = output_dir / "src-gen/libs/platform_vaf"

    generator = Generator()

    module_dir_names: list[str] = []
    for executable in model.Executables:
        for sm in executable.InternalCommunicationModules:
            module_dir_name = to_snake_case(sm.Name)
            module_dir_names.append(module_dir_name)
            generator.set_base_directory(output_path / module_dir_name)

            provider_interface_file = FileHelper(
                sm.ModuleInterfaceRef.Name + "Provider", sm.ModuleInterfaceRef.Namespace
            )
            consumer_interface_file = FileHelper(
                sm.ModuleInterfaceRef.Name + "Consumer", sm.ModuleInterfaceRef.Namespace
            )

            file = FileHelper(sm.Name, sm.Namespace)
            generator.generate_to_file(
                file,
                ".h",
                "vaf_application_communication/application_communication_module_h.jinja",
                module=sm,
                provider_interface_file=provider_interface_file,
                consumer_interface_file=consumer_interface_file,
                verbose_mode=verbose_mode,
            )

            generator.generate_to_file(
                file,
                ".cpp",
                "vaf_application_communication/application_communication_module_cpp.jinja",
                module=sm,
                verbose_mode=verbose_mode,
            )

            cmake = FileHelper("CMakeLists", "", True)
            cmake_target_name = to_snake_case("vaf_" + sm.Name)
            generator.generate_to_file(
                cmake,
                ".txt",
                "common/cmake_library.jinja",
                target_name=cmake_target_name,
                files=[file],
                libraries=[
                    "vaf_core",
                    "vaf_module_interfaces",
                ],
                verbose_mode=verbose_mode,
            )

    generator.set_base_directory(output_path)
    subdir_cmake = FileHelper("CMakeLists", "", True)
    module_dir_names = list(set(module_dir_names))
    generator.generate_to_file(
        subdir_cmake,
        ".txt",
        "common/cmake_subdirs.jinja",
        subdirs=module_dir_names,
        verbose_mode=verbose_mode,
    )
