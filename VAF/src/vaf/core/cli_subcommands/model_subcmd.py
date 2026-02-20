# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Source code for vaf model subcommands"""

from pathlib import Path

import click

from vaf.core.common.click_extension import (
    DisableForProjectOption,
    choice_option,
    filepath_option,
    get_project_type_for_project_dir,
    modifying_choice_fp_option,
)
from vaf.core.common.utils import (
    ProjectType,
    _get_default_model_path,
    get_project_type,
)
from vaf.core.objects.model_cmd import ModelCmd


# vaf model import group #
@click.group()
def model_import() -> None:
    """Import the VAF model from a specified model input file."""


# vaf model import vss #
@model_import.command(name="vss")
@click.option(
    "-p",
    "--project-dir",
    type=click.Path(exists=False, file_okay=False, writable=True),
    default=".",
    help="Path to the project root directory",
    show_default=True,
)
@filepath_option(
    "-i",
    "--input-file",
    help="JSON file to import.",
    required=True,
    type=click.Path(exists=True, dir_okay=False),
    prompt="Enter the path to the VSS catalogue file in JSON format",
)
def model_import_vss(project_dir: str, input_file: str) -> None:  # pylint: disable=missing-param-doc
    """Import the VAF model from a VSS input file."""
    # Look for project type in VAF_CFG_FILE in the project directory
    project_type = get_project_type(Path(project_dir))
    model_dir = project_dir  # Applies for interface project
    if project_type == ProjectType.APP_MODULE:
        model_dir = project_dir + "/model"
    if project_type == ProjectType.UNKNOWN:
        click.echo("\nNo valid VAF project found!")
    else:
        click.echo(f"Derive for model VSS from {input_file}.")
        cmd = ModelCmd()
        cmd.import_vss(input_file, model_dir)


# vaf model update #
# This option has to come before all options mentioned in the disable_param_for_project_type dictionary.
@click.command()
@click.option(
    "-p",
    "--project-dir",
    cls=DisableForProjectOption,
    disable_param_for_project_type={
        ProjectType.INTEGRATION: ["model-dir"],
        ProjectType.APP_MODULE: ["app-model-dir", "app-modules"],
    },
    type=click.Path(exists=True, file_okay=False, writable=True),
    required=True,
    help="Path to the project root directory.",
    default=".",
)
# This option has to come before the --app-modules option, because the app-modules are populated by it's callback
@filepath_option(
    "-m",
    "--model-dir",
    cls=modifying_choice_fp_option("--model-dir", choice_to_modify="app-modules"),
    type=click.Path(exists=True, file_okay=False, writable=True),
    help="Path to the model directory.",
    # lambda to ensure the callable is called every function call
    default=lambda: _get_default_model_path(get_project_type_for_project_dir()),
    prompt_required=False,
)
@choice_option(
    "--app-modules",
    prompt="Choose one ore more application modules",
    type=click.Choice([]),
    help="Absolute path to the application module directory to update. Specify multiple times for multiple modules.",
    multiple=True,
)
def model_update(project_dir: str, model_dir: str, app_modules: list[str]) -> None:  # pylint: disable=missing-param-doc
    "Update previously imported model or application module artifacts based on the project type."

    # Look for project type in VAF_CFG_FILE in the project directory
    project_type = get_project_type(Path(project_dir))
    if project_type == ProjectType.UNKNOWN:
        click.echo("\nNo valid VAF project found!")
    elif project_type == ProjectType.APP_MODULE:
        click.echo(f"Updating imported model artifacts in {model_dir} directory for an app-module project.")
        cmd = ModelCmd()
        cmd.update_imported_models(model_dir)
    elif project_type == ProjectType.INTEGRATION:
        # This workaround is necessary, because of the hacky solution to support only one choice in
        # ModifyingChoiceFpOption.callback_handler()
        if isinstance(app_modules, str):
            app_modules = [app_modules]

        paths = set()
        for app_module in app_modules:
            click.echo(f"Updating app-module model artifacts in {model_dir} directory for an integration project.")
            paths.add(Path(app_module))
        cmd = ModelCmd()
        cmd.update_app_modules(model_dir=Path(model_dir), app_modules=list(paths))
    else:
        click.echo("\nInvalid VAF project type for model update command.")


# vaf model generate #
@click.command()
@click.option(
    "-p",
    "--project-dir",
    cls=DisableForProjectOption,
    disable_param_for_project_type={
        ProjectType.INTERFACE: ["mode"],
        ProjectType.INTEGRATION: [""],
        ProjectType.APP_MODULE: [""],
    },
    type=click.Path(exists=False, file_okay=False, writable=True),
    default=".",
    help="Path to the project root directory",
    show_default=True,
)
@click.option(
    "-t",
    "--project-type",
    help="Project type.",
    required=False,
    type=ProjectType,
    # lambda to ensure the callable is called every function call
    default=lambda: get_project_type_for_project_dir(),  # pylint:disable=unnecessary-lambda
    show_default=True,
)
@filepath_option(
    "-m",
    "--model-dir",
    type=click.Path(exists=True, file_okay=False, writable=True),
    help="Path to the VAF model configuration directory.",
    # lambda to ensure the callable is called every function call
    default=lambda: _get_default_model_path(get_project_type_for_project_dir()),
    prompt_required=False,
)
@click.option(
    "--mode",
    help="Generation mode, either 'prj' or 'all'.",
    required=True,
    envvar="TYPE_VARIANT",
    type=click.Choice(["prj", "all"], case_sensitive=False),
    default="all",
    show_default=True,
)
@click.option(
    "--skip-validation",
    help="Flag to skip the model validation before generating the model.",
    is_flag=True,
)
def model_generate(  # pylint: disable=missing-param-doc
    project_dir: str,
    project_type: ProjectType,
    model_dir: str,
    mode: str,
    skip_validation: bool = False,
) -> None:
    """Process the VAF configuration to JSON model exchange format."""
    if project_type == ProjectType.UNKNOWN:
        click.echo(f"\nNo valid VAF project found in {project_dir}!")
    else:
        cmd = ModelCmd()
        cmd.generate(project_type, model_dir, mode, skip_validation)
