# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Generator for application modules.
Generates
    - framework/AppModuleBase.h
    - framework/AppModuleBase.cpp
    - framework/CMakeLists.txt
    - AppModule.h
    - AppModule.cpp
    - CMakeLists.txt
    - unittest/*
"""

import collections
from pathlib import Path
from typing import Any, Dict, List

from vaf import vafmodel
from vaf.core.common.utils import to_snake_case
from vaf.vafgeneration.vaf_cmake_common import data_type_definitions_exist
from vaf.vafmodel import ApplicationModule
from vaf.vafpy.model_runtime import ModelRuntime

from .generation import FileHelper, Generator
from .vaf_generate_common import get_ancestor_file_suffix

# pylint: disable=duplicate-code


# dir name for user files
user_files_dir_name = "implementation"
test_files_dir_name = "test"


def _get_interface_type_by_instance(interfaces: list[Any], instance_name: str) -> str:
    for i in interfaces:
        if i["instance"] == instance_name:
            assert isinstance(i["type"], str)
            return i["type"]
    raise ValueError(f"Could not find interfaces on module: ${instance_name}")


# pylint:disable=too-many-locals
def generate_app_module_base(
    am: ApplicationModule,
    app_module_path_base: Path,
    generator: Generator,
    verbose_mode: bool = False,
) -> None:
    """Generate base files for application modules

    Args:
        am (ApplicationModule): The model
        app_module_path_base (Path): Output directory for base modules
        generator (Generator): The generator
        verbose_mode: flag to enable verbose_mode mode
    """
    base_output_directory: Path = app_module_path_base / to_snake_case(am.Name)
    if am.ImplementationProperties is not None:
        if am.ImplementationProperties.InstallationPath is not None:
            base_output_directory = app_module_path_base / am.ImplementationProperties.InstallationPath

    generator.set_base_directory(base_output_directory)

    interfaces_c = []
    interfaces_p = []
    for consumed_interface in am.ConsumedInterfaces:
        interface_file = FileHelper(
            consumed_interface.ModuleInterfaceRef.Name + "Consumer",
            consumed_interface.ModuleInterfaceRef.Namespace,
        )
        interfaces_c.append(
            {
                "include": interface_file.get_include(),
                "instance": consumed_interface.InstanceName,
                "type": interface_file.get_full_type_name(),
            }
        )
    for provided_interface in am.ProvidedInterfaces:
        interface_file = FileHelper(
            provided_interface.ModuleInterfaceRef.Name + "Provider",
            provided_interface.ModuleInterfaceRef.Namespace,
        )
        interfaces_p.append(
            {
                "include": interface_file.get_include(),
                "instance": provided_interface.InstanceName,
                "type": interface_file.get_full_type_name(),
            }
        )

    interfaces = interfaces_c + interfaces_p

    persistency_files = []
    persistency_includes = []
    if am.has_persistency:
        persistency_includes.append('#include "persistency/persistency_interface.h"')
    for per_file in am.PersistencyFiles:
        persistency_files.append(
            {
                "instance": to_snake_case(per_file),
                "type": "persistency::PersistencyInterface",
            }
        )

    base_file = FileHelper(am.Name + "Base", am.Namespace)
    generator.generate_to_file(
        base_file,
        ".h",
        "vaf_application_module/base_h.jinja",
        app_module=am,
        interfaces=interfaces,
        persistency_files=persistency_files,
        persistency_includes=persistency_includes,
        verbose_mode=verbose_mode,
    )

    generator.generate_to_file(
        base_file,
        ".cpp",
        "vaf_application_module/base_cpp.jinja",
        app_module=am,
        interfaces=interfaces,
        persistency_files=persistency_files,
        persistency_includes=persistency_includes,
        verbose_mode=verbose_mode,
    )

    base_cmake_target_name = to_snake_case("Vaf" + am.Name + "Base")
    generator.generate_to_file(
        FileHelper("CMakeLists", "", True),
        ".txt",
        "common/cmake_library.jinja",
        target_name=base_cmake_target_name,
        files=[base_file],
        libraries=[
            "vaf_core",
            "vaf_module_interfaces",
        ],
        verbose_mode=verbose_mode,
    )


def __read_interfaces_cplusplus_refs(
    am: vafmodel.ApplicationModule,
) -> List[Dict[str, str]]:
    """Method to collect interfaces reference in c++
    Args:
        am: ApplicationModule object
    Returns:
        List of dictionary that contains interface reference in c++
    """

    consumed_interfaces: List[Dict[str, str]] = []
    provided_interfaces: List[Dict[str, str]] = []
    for interface_type_attr in ["ConsumedInterfaces", "ProvidedInterfaces"]:
        for interface in getattr(am, interface_type_attr):
            # get a string for "Consumer"/"Provider"
            interface_type_string = interface_type_attr.replace("dInterfaces", "r")
            # build data for include & type for both mock & non mock
            interface_cplusplus_ref_data: Dict[str, str] = {
                to_snake_case(f"{key}{mock_type}"): getattr(
                    FileHelper(
                        interface.ModuleInterfaceRef.Name + f"{interface_type_string}{mock_type}",
                        interface.ModuleInterfaceRef.Namespace,
                    ),
                    method_name,
                )()
                # include calls get_include() method from FileHelper
                # type calls get_full_type_name() method from FileHelper
                for key, method_name in [
                    ("include", "get_include"),
                    ("type", "get_full_type_name"),
                ]
                for mock_type in [
                    "",
                    "Mock",
                ]  # Mock only needed by unittest but no harm for include & src
            }
            # append to the respective interfaces
            locals()[to_snake_case(interface_type_attr)].append(
                interface_cplusplus_ref_data
                | {
                    "instance": interface.InstanceName,
                    "name": interface.ModuleInterfaceRef.Name + interface_type_string,
                }
            )

    return consumed_interfaces + provided_interfaces


def generate_app_module_user(
    am: ApplicationModule,
    app_module_path: Path,
    generator: Generator,
    is_ancestor: bool,
    verbose_mode: bool = False,
) -> List[str]:
    """Generate user files for application modules

    Args:
        am (ApplicationModule): The model
        app_module_path (Path): Output directory
        generator (Generator): The generator
        is_ancestor: Flag to trigger generation for ancestor
        verbose_mode (bool): Flag to enable verbose mode
    Returns
        List of all strings of relative path to user files
    """
    # collect interfaces c++ references for jinja files
    interfaces = __read_interfaces_cplusplus_refs(am)

    persistency_files = []
    for per_file in am.PersistencyFiles:
        persistency_files.append(
            {
                "instance": to_snake_case(per_file),
                "type": "persistency::PersistencyInterface",
            }
        )

    base_file = FileHelper(am.Name + "Base", am.Namespace)
    generator.set_base_directory(app_module_path)
    app_file = FileHelper(am.Name, am.Namespace)
    generator.generate_to_file(
        app_file,
        f".h{get_ancestor_file_suffix(is_ancestor)}",
        "vaf_application_module/module_h.jinja",
        check_to_overwrite=True,
        app_module=am,
        base_include=base_file.get_include(),
        verbose_mode=(verbose_mode and not is_ancestor),
    )
    generator.generate_to_simple_file(
        FileHelper(am.Name, am.Namespace),
        f".cpp{get_ancestor_file_suffix(is_ancestor)}",
        "vaf_application_module/module_cpp.jinja",
        check_to_overwrite=True,
        app_module=am,
        interfaces=interfaces,
        persistency_files=persistency_files,
        get_interface_type_by_instance=_get_interface_type_by_instance,
        dummy_data_element=vafmodel.DataElement(
            Name="MyDataElement",
            TypeRef=vafmodel.DataTypeRef(Name="uint64_t", Namespace="std"),
        ),
        verbose_mode=(verbose_mode and not is_ancestor),
    )
    base_cmake_target_name = to_snake_case("Vaf" + am.Name + "Base")
    generator.generate_to_file(
        FileHelper("CMakeLists", "", True),
        f".txt{get_ancestor_file_suffix(is_ancestor)}",
        "vaf_application_module/cmake_implementation.jinja",
        target_name=to_snake_case(am.Name),
        files=[app_file],
        libraries=[base_cmake_target_name],
        check_to_overwrite=True,
        verbose_mode=(verbose_mode and not is_ancestor),
    )

    return_list = [
        user_files_dir_name
        + str(getattr(app_file, method_str)(generator.base_directory, file_ext)).removeprefix(str(app_module_path))
        for method_str, file_ext in [
            ("get_file_path", ".h"),
            ("get_simple_file_path", ".cpp"),
        ]
    ] + [f"{user_files_dir_name}/CMakeLists.txt"]

    generator.set_base_directory(app_module_path / "cmake")
    generator.generate_to_simple_file(
        FileHelper(to_snake_case(am.Name) + "Config.cmake", "", True),
        "",
        "vaf_application_module/cmake_config.jinja",
        target_name=to_snake_case(am.Name),
        data_type_definitions_exist=data_type_definitions_exist(ModelRuntime().main_model),
    )

    # return list of user files' relative path to app_module
    return return_list


def generate_app_unittest(
    am: ApplicationModule,
    app_module_path_test: Path,
    generator: Generator,
    is_ancestor: bool,
    verbose_mode: bool = False,
) -> List[str]:
    """Generate files for application modules

    Args:
        am (vafmodel.MainModel.ApplicationModules): The model
        app_module_path_test (Path): Output directory for unit tests
        generator (Generator): The generator
        is_ancestor: Flag to trigger generation for ancestor
        verbose_mode (bool): Flag to enable verbose mode
    Returns:
        List of strings that represent relative path to app_module's unit test
    """
    generator.set_base_directory(app_module_path_test)
    generator.generate_to_file(
        FileHelper("CMakeLists", "", True),
        f".txt{get_ancestor_file_suffix(is_ancestor)}",
        "common/cmake_subdirs.jinja",
        subdirs=["unittest"],
        check_to_overwrite=True,
        verbose_mode=(verbose_mode and not is_ancestor),
    )
    generator.set_base_directory(app_module_path_test / "unittest")
    app_file = FileHelper(am.Name, am.Namespace)
    base_file = FileHelper(am.Name + "Base", am.Namespace)

    # collect interfaces c++ references for jinja files
    interfaces = __read_interfaces_cplusplus_refs(am)

    persistency_files = []
    persistency_includes = []
    if am.has_persistency:
        persistency_includes.append('#include "persistency/persistency_interface.h"')
    for per_file in am.PersistencyFiles:
        persistency_files.append(
            {
                "instance": to_snake_case(per_file),
                "type": "persistency::PersistencyInterface",
            }
        )

    generator.generate_to_file(
        base_file,
        f".h{get_ancestor_file_suffix(is_ancestor)}",
        "vaf_application_module/test_base_h.jinja",
        app_module=am,
        interfaces=interfaces,
        check_to_overwrite=True,
        persistency_files=persistency_files,
        persistency_includes=persistency_includes,
        verbose_mode=(verbose_mode and not is_ancestor),
    )

    generator.generate_to_file(
        base_file,
        f".cpp{get_ancestor_file_suffix(is_ancestor)}",
        "vaf_application_module/test_base_cpp.jinja",
        app_module=am,
        interfaces=interfaces,
        len=len,
        check_to_overwrite=True,
        persistency_files=persistency_files,
        persistency_includes=persistency_includes,
        verbose_mode=(verbose_mode and not is_ancestor),
    )

    generator.generate_to_file(
        FileHelper("CMakeLists", "", True),
        f".txt{get_ancestor_file_suffix(is_ancestor)}",
        "vaf_application_module/test_cmake.jinja",
        application_module_name=to_snake_case(am.Name),
        target_name=to_snake_case(am.Name) + "_unittest",
        app_files=[app_file],
        base_files=[base_file],
        check_to_overwrite=True,
        verbose_mode=(verbose_mode and not is_ancestor),
    )

    base_file = FileHelper("main", "", True)
    generator.generate_to_file(
        base_file,
        f".cpp{get_ancestor_file_suffix(is_ancestor)}",
        "vaf_application_module/test_main_cpp.jinja",
        app_module=am,
        interfaces=interfaces,
        check_to_overwrite=True,
        verbose_mode=(verbose_mode and not is_ancestor),
    )

    base_file = FileHelper("tests", "", True)
    generator.generate_to_file(
        base_file,
        f".cpp{get_ancestor_file_suffix(is_ancestor)}",
        "vaf_application_module/test_module_cpp.jinja",
        app_module=am,
        interfaces=interfaces,
        app_include=FileHelper(am.Name, am.Namespace).get_include(),
        check_to_overwrite=True,
        persistency_files=persistency_files,
        persistency_includes=persistency_includes,
        verbose_mode=(verbose_mode and not is_ancestor),
    )

    # return List of strings that represent relative path to app_module's unit test
    return [
        f"{user_files_dir_name}/{test_files_dir_name}"
        + str(base_file.get_file_path(generator.base_directory, file_ext)).removeprefix(str(app_module_path_test))
        for base_file, file_exts in [
            (FileHelper(am.Name + "Base", am.Namespace), [".cpp", ".h"]),
            (FileHelper("main", "", True), [".cpp"]),
            (FileHelper("tests", "", True), [".cpp"]),
            (FileHelper("CMakeLists", "", True), [".txt"]),
        ]
        for file_ext in file_exts
    ] + [f"{user_files_dir_name}/{test_files_dir_name}/CMakeLists.txt"]


def generate_app_module_project_files(
    app_module: vafmodel.ApplicationModule,
    output_dir: Path,
    is_ancestor: bool = False,
    verbose_mode: bool = False,
) -> List[str]:
    """Generate files for application modules

    Args:
        app_module (vafmodel.ApplicationModule): The application model
        output_dir (Path): Base output directory
        is_ancestor (bool): Flag to trigger generation for ancestor
        verbose_mode (bool): Flag to enable verbose mode
    Returns:
        List of paths for user-editable files
    """
    # collect list of merge relevant files
    list_merge_relevant_files: List[str] = []

    app_modules_path_base = "src-gen/libs/application_modules_base"

    generator = Generator()

    # don't generate app module base for ancestors
    if not is_ancestor:
        generate_app_module_base(
            app_module,
            output_dir / app_modules_path_base,
            generator,
            verbose_mode=verbose_mode,
        )

    list_merge_relevant_files += generate_app_module_user(
        app_module,
        output_dir / user_files_dir_name,
        generator,
        is_ancestor=is_ancestor,
        verbose_mode=verbose_mode,
    )
    list_merge_relevant_files += generate_app_unittest(
        app_module,
        output_dir / user_files_dir_name / test_files_dir_name,
        generator,
        is_ancestor=is_ancestor,
        verbose_mode=verbose_mode,
    )

    # generate CMakeLists in src-gen/libs/application_modules_base
    generator.set_base_directory(output_dir / app_modules_path_base)
    if not is_ancestor:
        generator.generate_to_file(
            FileHelper("CMakeLists", "", True),
            ".txt",
            "common/cmake_subdirs.jinja",
            subdirs=[
                app_module.ImplementationProperties.InstallationPath
                if app_module.ImplementationProperties is not None
                and app_module.ImplementationProperties.InstallationPath is not None
                else to_snake_case(app_module.Name)
            ],
            verbose_mode=(verbose_mode and not is_ancestor),
        )

    # return list of str for relative paths of user files
    return list_merge_relevant_files


def generate_app_module_files_for_integration_project(
    application_modules: List[vafmodel.ApplicationModule],
    output_dir: Path,
    is_ancestor: bool = False,
    verbose_mode: bool = False,
) -> List[str]:
    """Generate files for application modules

    Args:
        application_modules: List of all app modules in integration project
        output_dir (Path): Base output directory
        is_ancestor (bool): Flag to trigger generation for ancestor
        verbose_mode: flag to enable verbose_mode mode
    Returns:
        List of paths for user-editable files
    """
    app_modules_path_base = "src-gen/libs/application_modules_base"
    list_merge_relevant_files: List[str] = []

    generator = Generator()
    app_modules_for_base: list[str] = []
    app_modules_for_src: list[str] = []
    for am in application_modules:
        inserted_base: bool = False
        if am.ImplementationProperties is not None:
            if am.ImplementationProperties.InstallationPath is not None:
                inserted_base = True
                app_modules_for_base.append(am.ImplementationProperties.InstallationPath)
                app_modules_for_src.append(am.ImplementationProperties.InstallationPath)
        if not inserted_base:
            app_modules_for_base.append(to_snake_case(am.Name))
        if not is_ancestor:
            generate_app_module_base(am, output_dir / app_modules_path_base, generator, verbose_mode)

    # generate CMakeLists in src/application_modules
    generator.set_base_directory(output_dir / "src" / "application_modules")
    generator.generate_to_file(
        FileHelper("CMakeLists", "", True),
        f".txt{get_ancestor_file_suffix(is_ancestor)}",
        "common/cmake_subdirs.jinja",
        subdirs=app_modules_for_src,
        check_to_overwrite=True,
        verbose_mode=verbose_mode,
    )
    list_merge_relevant_files.append("src/application_modules/CMakeLists.txt")

    # generate CMakeLists in src-gen/libs/application_modules_base
    generator.set_base_directory(output_dir / app_modules_path_base)
    if not is_ancestor:
        generator.generate_to_file(
            FileHelper("CMakeLists", "", True),
            ".txt",
            "common/cmake_subdirs.jinja",
            subdirs=app_modules_for_base,
            verbose_mode=verbose_mode,
        )

    return list_merge_relevant_files


def validate_model_app_modules(model: vafmodel.MainModel) -> None:
    """Function to validate a model's app modules
    Args:
        model (vafmodel.MainModel): Current VAF Model
    Raises:
        RuntimeError: Duplicate app modules name install path pairs
    """
    # get tuples of name, install_path
    app_module_names_with_install_path = [
        (
            am.Name,
            am.ImplementationProperties.InstallationPath
            if am.ImplementationProperties is not None and am.ImplementationProperties.InstallationPath is not None
            else "",
        )
        for am in model.ApplicationModules
    ]
    # placeholder for error msgs
    error_msg = []

    for item, count in collections.Counter(app_module_names_with_install_path).items():
        if count > 1:
            error_msg.append(
                " ".join(
                    [
                        f"ERROR: There are {count} application modules",
                        f"with name {item[0]} and install path '{item[1]}'. Application Module must have a unique pair of name and install path!",  # pylint: disable = line-too-long
                    ]
                )
            )

    if error_msg:
        error_msg.insert(
            0,
            f"{len(error_msg)} Errors are found in the Application Modules' modelling:",
        )
        raise RuntimeError("\n".join(error_msg))
