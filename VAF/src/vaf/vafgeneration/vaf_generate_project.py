# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Generator library for generating the complete VAF project."""

import shutil
from pathlib import Path
from typing import Any, Callable, Dict, List

from vaf import vafmodel
from vaf.vafpy import import_model
from vaf.vafpy.model_runtime import ModelRuntime

from .vaf_application_communication import (
    generate as generate_application_communication,
)
from .vaf_application_module import generate_app_module_files_for_integration_project

# Build system files generators
from .vaf_cmake_common import generate as generate_cmake_common
from .vaf_conan import generate as generate_conan_deps
from .vaf_controller import generate as generate_controller
from .vaf_core_library import generate as generate_core_library

# Platform Generators
# VAF generators
from .vaf_generate_common import format_files, get_ancestor_model, is_source_file, merge_after_regeneration
from .vaf_interface import generate_module_interfaces as generate_interface
from .vaf_persistency import generate as generate_persistency
from .vaf_protobuf_serdes import generate as generate_protobuf_serdes
from .vaf_silkit import generate as generate_silkit
from .vaf_std_data_types import generate as generate_vaf_std_data_types

# pylint: disable=duplicate-code


def get_ecosystems(model: vafmodel.MainModel) -> List[str]:
    """Get All Ecosystems in the model
    Args:
        model: VAF MainModel
    Returns:
        List of all found Ecosystems in the platform
    """
    list_of_relevant_attrs = [
        "PlatformConsumerModules",
        "PlatformProviderModules",
        "ServiceConsumerModules",
        "ServiceProviderModules",
    ]
    return list(
        {
            module.OriginalEcoSystem.value
            for modules in [getattr(model, attr, "") for attr in list_of_relevant_attrs]
            for module in modules
            if hasattr(module, "OriginalEcoSystem")
        }
    )


ECOSYSTEM_FUNCTION_DICT: Dict[str, Callable[[vafmodel.MainModel, Path, bool], Any]] = {
    "SILKIT": generate_silkit,
}


# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
def generate_integration_project(
    model_file: str,
    project_dir: str,
    type_variant: str,
    execute_merge: bool = True,
    verbose_mode: bool = False,
) -> None:
    """
        Generate the code for the project.

    Args:
        model_file (str): The path to the input file.
        project_dir (str): The path to project root directory.
        type_variant (str): The type variant for the data type generation process.
        project_dir (Path): The directory of the project. Defaults to output_dir.
        execute_merge (bool): Flag to enable/disable automatic merge changes after regeneration
        verbose_mode (bool): Flag to enable verbose mode
    Raises:
        ValueError: If the path to the project root directory is invalid.
        SystemError: If there is a system-related error during cleanup.

    """
    # clean model runtime before every run
    ModelRuntime().reset()

    if project_dir is None:
        raise ValueError("Path to project directory cannot be None!")

    path_project_dir = Path(project_dir)
    import_model(model_file)
    main_model = ModelRuntime().main_model

    delete_folder_src_gen: Path = path_project_dir / "src-gen"
    if delete_folder_src_gen.exists():
        try:
            shutil.rmtree(delete_folder_src_gen)
        except OSError as e:
            raise SystemError(
                f'Folder "{delete_folder_src_gen.absolute().as_posix()}" could not be removed because of {e}!'
            ) from e

    delete_folder_test_gen: Path = path_project_dir / "test-gen"
    if delete_folder_test_gen.exists():
        try:
            shutil.rmtree(delete_folder_test_gen)
        except OSError as e:
            raise SystemError(
                f'Folder "{delete_folder_test_gen.absolute().as_posix()}" could not be removed because of {e}!'
            ) from e

    # This generator needs to run before calling get_paths()
    generate_conan_deps(main_model, path_project_dir, verbose_mode)

    generate_interface(main_model, path_project_dir, verbose_mode)

    # Load "ancestor" model.json if available and 3-way-merge is enabled
    ancestor_model = get_ancestor_model(model_file) if execute_merge else None
    # collect list of merge relevant files
    list_merge_relevant_files: List[str] = []

    # only generate platform_vaf in case of application module is modelled
    if getattr(main_model, "ApplicationModules"):
        # generate files for app modules + ancestor
        list_merge_relevant_files += generate_app_module_files_for_integration_project(
            application_modules=main_model.ApplicationModules,
            output_dir=path_project_dir,
            verbose_mode=verbose_mode,
        )
        if ancestor_model is not None:
            generate_app_module_files_for_integration_project(
                application_modules=ancestor_model.ApplicationModules,
                output_dir=path_project_dir,
                is_ancestor=True,
                verbose_mode=verbose_mode,
            )

        generate_application_communication(main_model, path_project_dir, verbose_mode)

    list_merge_relevant_files += generate_controller(main_model, path_project_dir, verbose_mode=verbose_mode)
    if ancestor_model is not None:
        generate_controller(
            ancestor_model,
            path_project_dir,
            is_ancestor=True,
            verbose_mode=verbose_mode,
        )

    # only generate platform dir for used ecosystems
    for ecosystem in get_ecosystems(main_model):
        ECOSYSTEM_FUNCTION_DICT[ecosystem](main_model, path_project_dir, verbose_mode)

    generate_core_library(path_project_dir, type_variant, verbose_mode=verbose_mode)
    generate_vaf_std_data_types(path_project_dir, verbose_mode)
    if main_model.is_silkit_used or main_model.is_persistency_used:
        generate_protobuf_serdes(path_project_dir, verbose_mode)
    if main_model.is_persistency_used:
        generate_persistency(main_model, path_project_dir, verbose_mode)

    # must run as last generator
    list_merge_relevant_files += generate_cmake_common(
        main_model,
        path_project_dir,
        generate_for_application_module=False,
        verbose_mode=verbose_mode,
    )
    if ancestor_model is not None:
        generate_cmake_common(
            ancestor_model,
            path_project_dir,
            is_ancestor=True,
            generate_for_application_module=False,
            verbose_mode=verbose_mode,
        )

    format_files(
        project_dir=project_dir,
        list_files=[Path(project_dir) / f for f in list_merge_relevant_files if is_source_file(Path(project_dir) / f)],
        verbose_mode=verbose_mode,
    )

    if execute_merge and list_merge_relevant_files:
        # solve conflicts for user files
        merge_after_regeneration(path_project_dir, list_merge_relevant_files, verbose_mode)
