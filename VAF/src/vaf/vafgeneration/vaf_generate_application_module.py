# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Generator library for generating the complete VAF project."""

import shutil
from pathlib import Path
from typing import List

from vaf import vafmodel
from vaf.core.common.exceptions import VafProjectGenerationError
from vaf.vafpy import import_model
from vaf.vafpy.model_runtime import ModelRuntime

# Utils
from .vaf_application_module import generate_app_module_project_files

# Build system files generators
from .vaf_cmake_common import generate as generate_cmake_common
from .vaf_conan import generate as generate_conan_deps
from .vaf_core_library import generate as generate_core_library
from .vaf_generate_common import format_files, get_ancestor_model, is_source_file, merge_after_regeneration

# VAF generators
from .vaf_interface import generate_module_interfaces as generate_interface
from .vaf_persistency import generate as generate_persistency
from .vaf_protobuf_serdes import generate as generate_protobuf_serdes
from .vaf_std_data_types import generate as generate_vaf_std_data_types


def validate_application_module(app_module: vafmodel.ApplicationModule) -> None:
    """Function to validate a single application model
    Args:
        app_module: Application Module to be validated
    Raises:
        VafProjectGenerationError: If InstallationPath is not defined
    """
    if app_module.ImplementationProperties is None:
        raise VafProjectGenerationError(f"ImplementationProperties for application module {app_module.Name}  missing!")
    if app_module.ImplementationProperties.InstallationPath is None:
        raise VafProjectGenerationError(f"InstallationPath for application module {app_module.Name}  missing!")


def _print_info(header: str, content: str = "") -> None:
    columns = shutil.get_terminal_size().columns
    remaining_columns = columns - len(header) - 2  # Two spaces around the header
    if remaining_columns <= 0:
        prefix_cnt = postfix_cnt = 0
    else:
        prefix_cnt = remaining_columns // 2
        postfix_cnt = remaining_columns // 2 + (remaining_columns % 2 > 0)

    print(f"\n{prefix_cnt * '-'} {header} {postfix_cnt * '-'}")
    if content:
        print("\n".join([content, f"{columns * '-'}\n"]))


def generate_application_module(  # pylint: disable=too-many-arguments, too-many-positional-arguments, too-many-branches, too-many-statements
    model_file: str,
    project_dir: str,
    type_variant: str,
    execute_merge: bool = True,
    verbose_mode: bool = False,
) -> None:
    """Generates all app modules files & operations
    Args:
        model_file (str): Path to the VAF model JSON
        type_variant (str): Type variant of the generated data types
        project_dir (Path): The directory of the project. Defaults to output_dir.
        execute_merge (bool): Flag to enable/disable automatic merge changes after regeneration
        verbose_mode (bool): Flag to enable verbose mode
    Raises:
        SystemError: If there is a system-related error during cleanup.
        ValueError: If the given model contains more or less application modules than one.
    """
    list_merge_relevant_files: List[str] = []

    # clean model runtime before every run
    ModelRuntime().reset()
    # import json as ModelRuntime()
    import_model(model_file)
    main_model = ModelRuntime().main_model
    path_output_dir = Path(project_dir)
    if len(main_model.ApplicationModules) != 1:
        raise ValueError(
            "".join(
                [
                    "An application module model needs exactly one application module, ",
                    f"but found {len(main_model.ApplicationModules)}",
                ]
            )
        )
    print(f"Generate app-module in {path_output_dir}\n\n")

    # define flag for merge: execute merge == True and not first time
    # (first time: if src-gen folder only contains one file - conan_deps.list)
    execute_merge &= len(list((path_output_dir / "src-gen").glob("*"))) != 1

    for subdir_name in ["src-gen", "test"]:
        if (path_output_dir / subdir_name).is_dir():
            try:
                shutil.rmtree(path_output_dir / subdir_name)
            except OSError as e:
                raise SystemError(
                    f'Folder "{(path_output_dir / subdir_name).absolute().as_posix()}" could not be removed due to {e}!'
                ) from e

    generate_conan_deps(main_model, path_output_dir, verbose_mode)

    _print_info("VAF GENERATE APP-MODULE: STEP 1", "Generating module interfaces files")
    generate_interface(main_model, path_output_dir, verbose_mode)

    _print_info(
        "VAF GENERATE APP-MODULE: STEP 2",
        f"Generating source files based on: {model_file}",
    )
    list_merge_relevant_files = generate_app_module_project_files(
        main_model.ApplicationModules[0],
        path_output_dir,
        is_ancestor=False,
        verbose_mode=verbose_mode,
    )
    print("SUCCESS: Source files generated!")
    # check for "ancestor" model.json (model.json~)
    ancestor_model = get_ancestor_model(model_file) if execute_merge else None
    # generate ancestor files if this exists and merge will be performed
    if ancestor_model is not None:
        if verbose_mode:
            print("VERBOSE: Generating ancestor files for auto-merge")
        generate_app_module_project_files(
            ancestor_model.ApplicationModules[0],
            path_output_dir,
            is_ancestor=True,
            verbose_mode=verbose_mode,
        )

    _print_info("VAF GENERATE APP-MODULE: STEP 3", "Generating core support files")
    generate_core_library(path_output_dir, type_variant, verbose_mode=verbose_mode)

    _print_info(
        "VAF GENERATE APP-MODULE: STEP 4",
        f"Generating datatypes using {type_variant} generator",
    )
    generate_vaf_std_data_types(path_output_dir, verbose_mode)
    if main_model.is_silkit_used or main_model.is_persistency_used:
        generate_protobuf_serdes(path_output_dir, verbose_mode)
    if main_model.is_persistency_used:
        generate_persistency(main_model, path_output_dir, verbose_mode)

    # must run as last generator
    # No files to merge when generating for app-modules
    _ = generate_cmake_common(
        main_model,
        path_output_dir,
        generate_for_application_module=True,
        verbose_mode=verbose_mode,
    )
    print("SUCCESS: Datatypes generated!")

    format_files(
        project_dir=project_dir,
        list_files=[Path(project_dir) / f for f in list_merge_relevant_files if is_source_file(Path(project_dir) / f)],
        verbose_mode=verbose_mode,
    )

    # execute merge if list of user files are not empty
    if execute_merge and list_merge_relevant_files:
        _print_info(
            "VAF GENERATE APP-MODULE: STEP 5",
            "Merging existing source files with results from step 1",
        )
        # solve conflicts for user files
        merge_after_regeneration(path_output_dir, list_merge_relevant_files, verbose_mode)
        _print_info("SUCCESS: MERGE EXECUTED!")
