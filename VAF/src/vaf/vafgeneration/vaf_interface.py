# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Generator library for module interface generation."""

# pylint: disable=duplicate-code
from pathlib import Path

from vaf import vafmodel

from .generation import FileHelper, Generator, get_data_type_include, get_include


def _get_file_helper(data_type: vafmodel.DataType) -> FileHelper:
    return FileHelper(data_type.Name, data_type.Namespace)


def generate_interfaces(
    interface: vafmodel.ModuleInterface,
    generator: Generator,
    verbose_mode: bool = False,
) -> None:
    """Generates the module interfaces

    Args:
        interface (ModuleInterface): The model
        generator (Generator): The generator
        verbose_mode: flag to enable verbose_mode mode
    """
    include_files: list[str] = []
    for d in interface.DataElements:
        include_files.append(get_data_type_include(d.TypeRef))

    out_parameter_type_namespace: str = interface.Namespace

    for o in interface.Operations:
        out_paramter_includes: list[str] = []
        out_parameters: list[vafmodel.Parameter] = []
        for p in o.Parameters:
            if p.Direction is not vafmodel.ParameterDirection.OUT:
                include_files.append(get_data_type_include(p.TypeRef))
            if p.Direction is not vafmodel.ParameterDirection.IN:
                out_paramter_includes.append(get_data_type_include(p.TypeRef))
                out_parameters.append(p)

        if len(out_parameters) > 0:
            include_files.append(FileHelper(o.Name, out_parameter_type_namespace).get_include())
            generator.generate_to_file(
                FileHelper(o.Name, out_parameter_type_namespace),
                ".h",
                "vaf_interface/operation_output.jinja",
                includes=set(out_paramter_includes),
                parameters=out_parameters,
                operation_name=o.Name,
                get_file_helper=_get_file_helper,
                verbose_mode=verbose_mode,
            )

    include_files = list(set(include_files))

    consumer_file = FileHelper(interface.Name + "Consumer", interface.Namespace)
    generator.generate_to_file(
        consumer_file,
        ".h",
        "vaf_interface/module_interface_consumer_h.jinja",
        name=interface.Name,
        module_interface=interface,
        data_elements=interface.DataElements,
        operations=interface.Operations,
        include_files=include_files,
        verbose_mode=verbose_mode,
    )

    provided_file = FileHelper(interface.Name + "Provider", interface.Namespace)
    generator.generate_to_file(
        provided_file,
        ".h",
        "vaf_interface/module_interface_provider_h.jinja",
        name=interface.Name,
        module_interface=interface,
        data_elements=interface.DataElements,
        operations=interface.Operations,
        include_files=include_files,
        verbose_mode=verbose_mode,
    )


def generate_interfaces_mocks(
    interface: vafmodel.ModuleInterface,
    generator: Generator,
    verbose_mode: bool = False,
) -> None:
    """Generates the module interfaces

    Args:
        interface (ModuleInterface): The model
        generator (Generator): The generator
        verbose_mode: flag to enable verbose_mode mode
    """
    out_parameter_type_namespace: str = interface.Namespace

    include_files: list[str] = []
    for d in interface.DataElements:
        include_files.append(get_data_type_include(d.TypeRef))

    for o in interface.Operations:
        out_parameters: list[vafmodel.Parameter] = []
        for p in o.Parameters:
            if p.Direction is not vafmodel.ParameterDirection.OUT:
                include_files.append(get_data_type_include(p.TypeRef))
            if p.Direction is not vafmodel.ParameterDirection.IN:
                out_parameters.append(p)

        if len(out_parameters) > 0:
            include_files.append(FileHelper(o.Name, out_parameter_type_namespace).get_include())

    include_files.append(get_include(interface.Name + "_consumer", interface.Namespace))
    include_files = list(set(include_files))

    consumer_file = FileHelper(interface.Name + "ConsumerMock", interface.Namespace)
    generator.generate_to_file(
        consumer_file,
        ".h",
        "vaf_interface/module_interface_consumer_mock_h.jinja",
        name=interface.Name,
        module_interface=interface,
        data_elements=interface.DataElements,
        operations=interface.Operations,
        include_files=include_files,
        verbose_mode=verbose_mode,
    )

    include_files.remove(get_include(interface.Name + "_consumer", interface.Namespace))
    include_files.append(get_include(interface.Name + "_provider", interface.Namespace))
    provided_file = FileHelper(interface.Name + "ProviderMock", interface.Namespace)
    generator.generate_to_file(
        provided_file,
        ".h",
        "vaf_interface/module_interface_provider_mock_h.jinja",
        name=interface.Name,
        module_interface=interface,
        data_elements=interface.DataElements,
        operations=interface.Operations,
        include_files=include_files,
        verbose_mode=verbose_mode,
    )


def generate_module_interfaces(model: vafmodel.MainModel, output_dir: Path, verbose_mode: bool = False) -> None:
    """Generates the module interfaces

    Args:
        model (vafmodel.MainModel): The model
        output_dir (str): The output directory
        verbose_mode: flag to enable verbose_mode mode
    """

    generator = Generator()
    generator.set_base_directory(output_dir / "src-gen/libs/interfaces")

    cmake_file = FileHelper("CMakeLists", "", True)

    data_type_definition_not_empty: bool = any(
        bool(getattr(model.DataTypeDefinitions, data_type)) for data_type in vafmodel.data_types
    )

    libraries: list[str] = ["vaf_data_types"] if data_type_definition_not_empty else []
    libraries.append("vaf_core")

    generator.generate_to_file(
        cmake_file,
        ".txt",
        "common/cmake_interface_library.jinja",
        target_name="vaf_module_interfaces",
        libraries=libraries,
        verbose_mode=verbose_mode,
    )

    if not model.ModuleInterfaces:
        include_path: Path = output_dir / "src-gen/libs/interfaces/include"
        include_path.mkdir(parents=False, exist_ok=True)

    if model.has_module_interfaces or model.is_persistency_used:
        generator.set_base_directory(output_dir / "test-gen/mocks/interfaces")
        generator.generate_to_file(
            cmake_file,
            ".txt",
            "common/cmake_interface_library.jinja",
            target_name="vaf_module_interface_mocks",
            libraries=libraries,
            verbose_mode=verbose_mode,
        )

    for interface in model.ModuleInterfaces:
        generator.set_base_directory(output_dir / "src-gen/libs/interfaces")
        generate_interfaces(interface, generator, verbose_mode)
        generator.set_base_directory(output_dir / "test-gen/mocks/interfaces")
        generate_interfaces_mocks(interface, generator, verbose_mode)


# pylint: enable=duplicate-code
