# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Generator for controller.
Generates
    - executable_controller.h
    - executable_controller.cpp
    - user_controller.h
    - user_controller.cpp
    - CMakeLists.txt
"""

# pylint: disable=too-many-locals
# mypy: disable-error-code="union-attr"

from pathlib import Path
from typing import Any, List, Tuple

from vaf import vafmodel
from vaf.core.common.utils import create_name_namespace_full_name, to_snake_case
from vaf.vafgeneration.vaf_generate_common import get_ancestor_file_suffix

from .generation import (
    FileHelper,
    Generator,
    implicit_data_type_to_str,
    time_str_to_nanoseconds,
)


def _is_vsf_platform_module(executable: vafmodel.Executable, module: vafmodel.PlatformModule) -> bool:
    for m in executable.InternalCommunicationModules:
        if m == module:
            return True
    return False


def get_full_type_of_application_module(
    am: vafmodel.ExecutableApplicationModuleMapping,
) -> str:
    """Get the full type of an application module from its mapping

    Args:
        am (vafmodel.ExecutableApplicationModuleMapping): The application module mapping

    Returns:
        str: The full type of the application module
    """
    return FileHelper(am.ApplicationModuleRef.Name, am.ApplicationModuleRef.Namespace).get_full_type_name()


def get_include_of_application_module(
    am: vafmodel.ExecutableApplicationModuleMapping,
) -> str:
    """Get the include of an application module from its mapping

    Args:
        am (vafmodel.ExecutableApplicationModuleMapping): The application module mapping

    Returns:
        str: The include of the application module
    """
    return FileHelper(am.ApplicationModuleRef.Name, am.ApplicationModuleRef.Namespace).get_include()


def get_full_type_of_platform_module(sm: vafmodel.PlatformModule) -> str:
    """Get the full type of a platform module

    Args:
        sm (vafmodel.PlatformModule): The platform module

    Returns:
        str: The full type of the platform module
    """
    return FileHelper(sm.Name, sm.Namespace).get_full_type_name()


def get_includes_of_platform_modules(
    platform_modules: list[vafmodel.PlatformModule],
) -> list[str]:
    """Gets the list of unique platform module includes

    Args:
        platform_modules (list[vafmodel.PlatformModule]): List of platform modules.

    Returns:
        list[str]: The unique includes for the platform modules
    """
    includes: list[str] = []
    for sm in platform_modules:
        includes.append(FileHelper(sm.Name, sm.Namespace).get_include())
    includes = list(set(includes))
    includes.sort()
    return includes


def _get_provided_modules_of_application_module(
    eamm: vafmodel.ExecutableApplicationModuleMapping,
) -> list[vafmodel.PlatformModule]:
    modules: list[vafmodel.PlatformModule] = []
    am = eamm.ApplicationModuleRef
    for ami in am.ProvidedInterfaces:
        found_iitmm = [iitm for iitm in eamm.InterfaceInstanceToModuleMappings if iitm.InstanceName == ami.InstanceName]
        if len(found_iitmm) == 1:
            modules.append(found_iitmm[0].ModuleRef)
        else:
            raise ValueError(
                f"Error: The application module interface instance: {ami.InstanceName}"
                f" defined for application module: {am.Namespace}::{am.Name} is not mapped/connected."
                "Consider using the 'connect_interfaces()' method to connect the interfaces internally."
            )
    return modules


def _get_consumed_modules_of_application_module(
    eamm: vafmodel.ExecutableApplicationModuleMapping,
) -> list[vafmodel.PlatformModule]:
    modules: list[vafmodel.PlatformModule] = []
    am = eamm.ApplicationModuleRef
    for ami in am.ConsumedInterfaces:
        found_iitmm = [iitm for iitm in eamm.InterfaceInstanceToModuleMappings if iitm.InstanceName == ami.InstanceName]
        if len(found_iitmm) == 1:
            modules.append(found_iitmm[0].ModuleRef)
        else:
            raise ValueError(
                f"Error: The application module interface instance: {ami.InstanceName}"
                f" defined for application module: {am.Namespace}::{am.Name} is not mapped/connected."
                "Consider using the 'connect_interfaces()' method to connect the interfaces internally."
            )
    return modules


def _get_consumed_interface(
    am: vafmodel.ExecutableApplicationModuleMapping, m: vafmodel.PlatformModule
) -> vafmodel.ApplicationModuleConsumedInterface:
    for iitmm in am.InterfaceInstanceToModuleMappings:
        if iitmm.ModuleRef == m:
            for ci in am.ApplicationModuleRef.ConsumedInterfaces:
                if ci.InstanceName == iitmm.InstanceName:
                    return ci
    raise ValueError(f"Error: could not find consumed interface of platform module {m.Namespace}::{m.Name}")


def _derive_value_str_from_value(x: Any) -> str:
    value: str
    if type(x) is bool:  # pylint: disable=unidiomatic-typecheck
        value = "true" if x is True else "false"
    elif type(x) is str:  # pylint: disable=unidiomatic-typecheck
        value = '"' + str(x) + '"'
    else:
        value = str(x)
    return value


def derive_persistency_set_function(file_name: str, iv: vafmodel.PersistencyInitValue) -> str:
    """Derive how to call the persistency Set function

    Args:
        file_name (str): The persistency file name
        iv (vafmodel.PersistencyInitValue): PersistencyInitValue

    Returns:
        str: The persistency Set call string
    """
    output: str = ""
    name = iv.TypeRef.Name
    namespace = iv.TypeRef.Namespace

    basetype_dict = {}
    basetype_dict["uint64_t"] = "UInt64"
    basetype_dict["uint32_t"] = "UInt32"
    basetype_dict["uint16_t"] = "UInt16"
    basetype_dict["uint8_t"] = "UInt8"
    basetype_dict["int64_t"] = "Int64"
    basetype_dict["int32_t"] = "Int32"
    basetype_dict["int16_t"] = "Int16"
    basetype_dict["int8_t"] = "Int8"
    basetype_dict["bool"] = "Bool"
    basetype_dict["float"] = "Float"
    basetype_dict["double"] = "Double"

    if iv.TypeRef.is_cpp_base_type:
        output = f"""auto {file_name}_{iv.Key}_result = {file_name}->Get_{basetype_dict[name]}Value("{iv.Key}");
  if (!{file_name}_{iv.Key}_result.HasValue()) {{
    vaf::OutputSyncStream{{}} << "{file_name}: Key-Value {iv.Key} NOT initialized, set init value." << std::endl;
    ReportErrorOfModule({file_name}_{iv.Key}_result.Error(), "ExecutableController::DoInitialize", false);
    {file_name}->Set_{basetype_dict[name]}Value("{iv.Key}", {_derive_value_str_from_value(iv.Value.InitValue)});
  }}"""
    else:
        fullname = create_name_namespace_full_name(name, namespace)
        if isinstance(iv.Value.InitValue, str):
            init_value = '"' + str(iv.Value.InitValue) + '"'
            fullname = "String"
        else:
            init_list = []
            for x in iv.Value.InitValue:
                init_list.append(_derive_value_str_from_value(x))
            init_value = ",".join(init_list)
        # pylint: disable=line-too-long
        output = f"""auto {file_name}_{iv.Key}_result = {file_name}->Get_{fullname.rsplit("::", maxsplit=1)[-1]}Value("{iv.Key}");
  if (!{file_name}_{iv.Key}_result.HasValue()) {{
    vaf::OutputSyncStream{{}} << "{file_name}: Key-Value {iv.Key} NOT initialized, set init value." << std::endl;
    ReportErrorOfModule({file_name}_{iv.Key}_result.Error(), "ExecutableController::DoInitialize", false);
    {implicit_data_type_to_str(name, namespace)} {file_name}_{iv.Key}_value = {{ {init_value} }};
    {file_name}->Set_{fullname.rsplit("::", maxsplit=1)[-1]}Value("{iv.Key}", {file_name}_{iv.Key}_value);
  }}"""

    return output


def get_persistency_dependencies(
    exe: vafmodel.Executable,
    am: vafmodel.ExecutableApplicationModuleMapping,
    shared_per_path: dict[str, str],
) -> list[str]:
    """Gets persistency dependencies of a application module by its mapping

    Args:
        exe (vafmodel.Executable): The executable the application module is mapped to
        am (vafmodel.ExecutableApplicationModuleMapping): The application module mapping
        shared_per_path (dict[str, str]): Shared persistency paths and sync option

    Raises:
        ValueError: If application module have persistency files but persistency library wasn't connected

    Returns:
        list[str]: The persistency dependencies
    """
    persistency_dependencies: list[str] = []
    if exe.PersistencyModule is not None:
        # Need to be added in same order as declared in app module constructor token
        for app_per_file in am.ApplicationModuleRef.PersistencyFiles:
            for per_file in exe.PersistencyModule.PersistencyFiles:
                if per_file.AppModuleName == am.ApplicationModuleRef.Name and app_per_file == per_file.FileName:
                    shared_path_keys = list(shared_per_path)
                    if per_file.FilePath not in shared_path_keys:
                        persistency_dependencies.append(
                            "Persistency_" + per_file.AppModuleName + "_" + per_file.FileName
                        )
                    else:
                        persistency_dependencies.append(
                            "Persistency_" + "SharedFile" + str(1 + shared_path_keys.index(per_file.FilePath))
                        )

                    if not exe.PersistencyModule.PersistencyLibrary:
                        raise ValueError(
                            f"AppModule {am.ApplicationModuleRef.Namespace}::{am.ApplicationModuleRef.Name} has a"
                            " persistency file but no key-value store is connected."
                        )
    return persistency_dependencies


# pylint: disable=too-many-branches
def get_dependencies_of_application_module(
    exe: vafmodel.Executable,
    am: vafmodel.ExecutableApplicationModuleMapping,
    shared_per_path: dict[str, str],
) -> tuple[list[str], list[str]]:
    """Gets the execution and module dependencies of a application module by its mapping

    Args:
        exe (vafmodel.Executable): The executable the application module is mapped to
        am (vafmodel.ExecutableApplicationModuleMapping): The application module mapping
        shared_per_path (dict[str, str]): Shared persistency paths and sync option

    Raises:
        ValueError: If application module have persistency files but persistency library wasn't connected

    Returns:
        tuple[list[str], list[str]]: The execution and module dependencies
    """
    execution_dependencies: list[str] = []
    module_dependencies_c: list[str] = []
    module_dependencies_p: list[str] = []
    persistency_dependencies: list[str] = []

    persistency_dependencies = get_persistency_dependencies(exe, am, shared_per_path)
    provided_modules = _get_provided_modules_of_application_module(am)
    for m in provided_modules:
        module_dependencies_p.append(m.Name)
        execution_dependencies.append(m.Name)

    consumed_modules = _get_consumed_modules_of_application_module(am)
    for m in consumed_modules:
        module_dependencies_c.append(m.Name)

        if not _get_consumed_interface(am, m).IsOptional:
            execution_dependencies.append(m.Name)

    return (
        execution_dependencies,
        module_dependencies_c + module_dependencies_p + persistency_dependencies,
    )


# pylint: enable=too-many-branches


def get_task_mapping(
    mapping: vafmodel.ExecutableTaskMapping,
    am: vafmodel.ExecutableApplicationModuleMapping,
) -> tuple[int, int]:
    """Gets the offset and budget of a task by its mapping

    Args:
        mapping (vafmodel.ExecutableTaskMapping): The task mapping
        am (vafmodel.ExecutableApplicationModuleMapping): The application module the task is mapped to

    Raises:
        ValueError: If the mapped task is not found in the application module

    Returns:
        tuple[int, int]: The offset and budget of the task
    """
    offset = mapping.Offset if mapping.Offset is not None else 0
    budget = time_str_to_nanoseconds(mapping.Budget) if mapping.Budget is not None else 0

    task = [r for r in am.ApplicationModuleRef.Tasks if r.Name == mapping.TaskName]
    if len(task) == 0:
        raise ValueError(
            f"Error: could not find mapped task {mapping.TaskName} in application module"
            f"{am.ApplicationModuleRef.Namespace}::{am.ApplicationModuleRef.Name}"
        )

    preferred_offset = task[0].PreferredOffset
    if preferred_offset is not None:
        if mapping.Offset is None:
            offset = preferred_offset
        elif mapping.Offset != preferred_offset:
            print(f"Warning: offset for task {mapping.TaskName} is different then its preferred offset")

    return (offset, budget)


# Locals use seems reasonable. Generator could become an argument but not really a benefit there
def generate(  # pylint: disable=too-many-locals, too-many-branches, too-many-statements
    model: vafmodel.MainModel,
    output_dir: Path,
    is_ancestor: bool = False,
    verbose_mode: bool = False,
) -> List[str]:
    """Generate the VAF controller

    Args:
        model (vafmodel.MainModel): The main model
        output_dir (Path): The output directory
        is_ancestor (bool): Flag to trigger generation for ancestor
        verbose_mode: flag to enable verbose_mode mode

    Raises:
        ValueError: If there is a interface mapping problem
    """
    generator = Generator()

    # collect list of merge relevant files
    list_merge_relevant_files: List[str] = []

    for e in model.Executables:  # pylint: disable=too-many-branches, too-many-nested-blocks
        output_path = output_dir / "src-gen/executables"
        provided_modules: list[vafmodel.PlatformModule] = []
        consumed_modules: list[vafmodel.PlatformModule] = []

        unique_per_path: list[str] = []
        shared_per_path: dict[str, str] = {}
        if e.PersistencyModule is not None:
            for per_map in e.PersistencyModule.PersistencyFiles:
                if per_map.FilePath not in unique_per_path:
                    unique_per_path.append(per_map.FilePath)
                else:
                    if per_map.FilePath not in shared_per_path:
                        shared_per_path.update({per_map.FilePath: per_map.Sync})

        for am in e.ApplicationModules:
            for mapping in am.InterfaceInstanceToModuleMappings:
                if (
                    len(
                        [
                            ci
                            for ci in am.ApplicationModuleRef.ConsumedInterfaces
                            if ci.InstanceName == mapping.InstanceName
                        ]
                    )
                    > 0
                ):
                    if not _is_vsf_platform_module(e, mapping.ModuleRef):
                        consumed_modules.append(mapping.ModuleRef)
                elif (
                    len(
                        [
                            ci
                            for ci in am.ApplicationModuleRef.ProvidedInterfaces
                            if ci.InstanceName == mapping.InstanceName
                        ]
                    )
                    > 0
                ):
                    provided_modules.append(mapping.ModuleRef)
                else:
                    raise ValueError(
                        f"Mapped interface instance {mapping.InstanceName} not found in application module: "
                    )

        folder_name = to_snake_case(e.Name)
        generator.set_base_directory(output_path / folder_name)

        exe_controller_file = None
        if not is_ancestor:
            exe_controller_file = FileHelper("ExecutableController", "executable_controller")
            generator.generate_to_file(
                exe_controller_file,
                ".h",
                "vaf_controller/executable_controller_h.jinja",
            )
            generator.generate_to_file(
                exe_controller_file,
                ".cpp",
                "vaf_controller/executable_controller_cpp.jinja",
                get_full_type_of_application_module=get_full_type_of_application_module,
                get_dependencies_of_application_module=get_dependencies_of_application_module,
                get_persistency_dependencies=get_persistency_dependencies,
                derive_persistency_set_function=derive_persistency_set_function,
                get_includes_of_platform_modules=get_includes_of_platform_modules,
                get_full_type_of_platform_module=get_full_type_of_platform_module,
                get_include_of_application_module=get_include_of_application_module,
                get_task_mapping=get_task_mapping,
                executable=e,
                communication_modules=consumed_modules + provided_modules,
                vafmodel=vafmodel,
                isinstance=isinstance,
                shared_per_path=shared_per_path,
                verbose_mode=verbose_mode,
            )

        output_path = output_dir / "src/executables"
        generator.set_base_directory(output_path / folder_name)

        user_controller_file = FileHelper("UserController", "")
        generator.generate_to_file(
            user_controller_file,
            f".h{get_ancestor_file_suffix(is_ancestor)}",
            "vaf_controller/user_controller_h.jinja",
            check_to_overwrite=True,
            verbose_mode=verbose_mode,
        )
        list_merge_relevant_files.append(f"src/executables/{folder_name}/UserController.h")
        generator.generate_to_file(
            user_controller_file,
            f".cpp{get_ancestor_file_suffix(is_ancestor)}",
            "vaf_controller/user_controller_cpp.jinja",
            check_to_overwrite=True,
            verbose_mode=verbose_mode,
        )
        list_merge_relevant_files.append(f"src/executables/{folder_name}/UserController.cpp")

        output_path = output_dir / "src-gen/executables"
        generator.set_base_directory(output_path / folder_name)

        main_file = FileHelper("Main", "")
        if not is_ancestor:
            generator.generate_to_file(
                main_file,
                ".cpp",
                "vaf_controller/main_cpp.jinja",
                controller_file=exe_controller_file,
                verbose_mode=verbose_mode,
            )

        def __generate_platform_modules_library_list(
            modules: List[vafmodel.PlatformModule],
        ) -> Tuple[List[str], List[str]]:
            result = []
            deployment_types: list[Any] = []
            for module in modules:
                target_name_list = [
                    "vaf",
                    to_snake_case(module.Name),
                ]

                result.append("_".join(target_name_list))

            return result, deployment_types

        lib1, dep1 = __generate_platform_modules_library_list(consumed_modules)
        lib2, dep2 = __generate_platform_modules_library_list(provided_modules)
        libraries = lib1 + lib2
        deployment_types = dep1 + dep2

        for a in e.ApplicationModules:
            libraries.append(to_snake_case(a.ApplicationModuleRef.Name))
        if e.PersistencyModule is not None:
            if e.PersistencyModule.PersistencyLibrary:
                libraries.append("vaf_persistency")
        if not is_ancestor:
            generator.generate_to_file(
                FileHelper("CMakeLists", "", True),
                ".txt",
                "vaf_controller/CMakeLists_txt.jinja",
                model=model,
                target_name=e.Name,
                files=[exe_controller_file],
                libraries=libraries,
                unique_deployment_types=list(set(deployment_types)),
                verbose_mode=verbose_mode,
            )
        output_path = output_dir / "src/executables"
        generator.set_base_directory(output_path / folder_name)
        generator.generate_to_file(
            FileHelper("CMakeLists", "", True),
            f".txt{get_ancestor_file_suffix(is_ancestor)}",
            "vaf_controller/user_controller_CMakeLists_txt.jinja",
            target_name=e.Name,
            check_to_overwrite=True,
            verbose_mode=verbose_mode,
        )
        list_merge_relevant_files.append(f"src/executables/{folder_name}/CMakeLists.txt")

    return list_merge_relevant_files


# pylint: enable=too-many-locals
