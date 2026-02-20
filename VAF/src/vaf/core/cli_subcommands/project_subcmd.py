# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Source code for vaf project subcommands"""

from pathlib import Path
from typing import Any, Optional

import click

from vaf.core.cli_subcommands.make_subcmd import make_preset
from vaf.core.cli_subcommands.model_subcmd import model_generate
from vaf.core.common.click_extension import (
    DisableForProjectOption,
    choice_option,
    cli_verbose_option,
    filepath_option,
    get_project_type_for_project_dir,
    modifying_choice_fp_option,
    sanatized_str_option,
)
from vaf.core.common.utils import (
    ProjectType,
    _get_default_model_path,
    get_project_type,
    get_projects_in_path,
)
from vaf.core.objects.model_cmd import ModelCmd
from vaf.core.objects.project_cmd import ProjectCmd


# vaf project create group #
@click.group()
def project_create() -> None:
    """Create the specified project artifacts inside the given project."""


# vaf project create app-module #
@project_create.command(name="app-module")
@sanatized_str_option(
    "-n",
    "--name",
    type=str,
    required=True,
    help="App-module name.",
    prompt="Enter the name of the app-module",
)
@click.option(
    "--namespace",
    type=str,
    required=True,
    help="App-module namespace.",
    prompt="Enter the namespace of the app-module",
    callback=lambda ctx, param, value: value.strip() if value else "",
)
@filepath_option(
    "-p",
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, writable=True),
    required=True,
    help="Path to the project root directory.",
    default=".",
    prompt="Enter the path to the VAF integration project root directory",
)
@click.option(
    "--pre-path",
    type=click.Path(exists=False, file_okay=False, writable=True),
    help="Relative pre-path to the app module directory: <project_root_dir>/src/application_modules/<pre_path>/<app_module_dir>",  # pylint: disable=line-too-long
    default=".",
    required=False,
)
@click.option(
    "-m",
    "--model-dir",
    type=click.Path(exists=True, file_okay=False, writable=True),
    required=False,
    help="Relative path to VAF model directory from project dir.",
)
def project_create_app_module(  # pylint: disable=missing-param-doc, too-many-arguments, too-many-positional-arguments
    namespace: str, name: str, project_dir: str, pre_path: str, model_dir: Optional[str] = None
) -> None:
    """Create an application module project and add it to the given integration project."""
    # Look for project type in VAF_CFG_FILE in the project directory
    project_type = get_project_type(Path(project_dir))

    if project_type == ProjectType.INTEGRATION:
        if model_dir is None:
            model_dir = _get_default_model_path(get_project_type(Path(project_dir)))
        click.echo(
            f"Creating app-module {namespace}::{name} to {project_dir}/src/application_modules/{pre_path}/{name}."
        )
        click.echo(f"App-Module {namespace}::{name} will be stored in {model_dir}")
        cmd = ProjectCmd()
        cmd.create_appmodule(namespace, name, project_dir, pre_path, model_dir)
    elif project_type == ProjectType.UNKNOWN:
        click.echo("\nNo valid VAF project found!")
    else:
        click.echo("\nInvalid VAF project for project create app-module command.")


# --- Helper Function ---
def is_source_file(file_path: Path) -> bool:  # pylint: disable=missing-param-doc
    """Helper function to identify the c++ source files."""
    file_extensions = [".cpp", ".h", ".hpp", ".cc"]
    return file_path.suffix in file_extensions


# vaf project generate #
@click.command()
@click.pass_context
@cli_verbose_option
@click.option(
    "-p",
    "--project-dir",
    type=click.Path(exists=False, file_okay=False, writable=False),
    required=False,
    help="Path to the project directory.",
    default=".",
)
@click.option(
    "-i",
    "--input-file",
    "user_input_file",
    type=click.Path(exists=False, dir_okay=False, writable=True),
    required=False,
    help="Path to the project model JSON file.",
)
@click.option(
    "-b",
    "--build-dir",
    type=click.Path(exists=False, file_okay=False, writable=False),
    default="build",
    help="Build directory",
    show_default=True,
)
@click.option(
    "-t",
    "--type-variant",
    help="Type variant of the generated data types.",
    required=False,
    envvar="TYPE_VARIANT",
    type=click.Choice(["std"], case_sensitive=False),
    default="std",
    show_default=True,
)
@click.option(
    "--no-merge",
    "no_merge",
    help="Flag to disable the automatic 3-way merge mechanism on re-generation of user-editable source files.",
    is_flag=True,
)
@click.option(
    "--skip-model-update",
    "skip_model_update",
    help="Flag to not update model.json before generating the project.",
    is_flag=True,
)
@click.option(
    "--skip-make-preset",
    "skip_make_preset",
    help="Flag to skip the make preset call after generating the project.",
    is_flag=True,
)
@click.option(
    "--mode",
    help="Generation mode only relevant for integration project, either 'prj' or 'all'",
    required=False,
    envvar="GEN_MODE",
    type=click.Choice(["prj", "all"], case_sensitive=False),
    default="prj",
    show_default=True,
)
# pylint: disable=missing-param-doc, missing-raises-doc, line-too-long, too-many-arguments, too-many-positional-arguments, too-many-locals, too-many-branches, too-many-statements
def project_generate(
    ctx: click.Context,
    project_dir: str,
    build_dir: str,
    type_variant: str,
    mode: str,
    user_input_file: Optional[str] = None,
    no_merge: bool = False,
    verbose: bool = False,
    skip_model_update: bool = False,
    skip_make_preset: bool = False,
) -> None:
    """Generate the source code of the VAF project based on the configuration and generation mode."""
    # Look for project type in VAF_CFG_FILE in the project directory
    project_type = get_project_type(Path(project_dir))

    input_file = (
        (Path(project_dir) / _get_default_model_path(project_type) / "model.json").as_posix()
        if user_input_file is None
        else user_input_file
    )

    if project_type == ProjectType.UNKNOWN:
        click.echo("\nNo valid VAF project found!")
    else:
        # Check if the user provided `--input-file` or if it's using the default value
        if (user_input_file is not None) and not skip_model_update:
            click.echo("Disabling the model update for a user provided model JSON file.")
            skip_model_update = True

        def __run_make_preset(project_dir: str = project_dir, **kwargs: Any) -> None:
            ctx.invoke(
                make_preset,
                project_dir=project_dir,
                build_dir=build_dir,
                verbose=verbose,
                **kwargs,
            )

        def __run_make_preset_release(**kwargs: Any) -> None:
            __run_make_preset(build_type="Release", **kwargs)

        def __update_vaf_model(
            project_type: ProjectType,
            project_dir: str,
            input_file: str,
            mode: str,
        ) -> None:
            """Function to also update vaf model by calling vaf model generate
            Args:
                input_file: Path to the model.json as string
                mode: type of generation mode used
            """
            model_dir = Path(input_file).parent.as_posix()
            click.echo(f"\nTriggering vaf model generate in {model_dir}...")
            ctx.invoke(
                model_generate,
                project_dir=project_dir,
                project_type=project_type,
                model_dir=model_dir,
                mode=mode,
            )
            click.echo(f"\nSUCCESS: VAF model generated and stored in {model_dir}")

        cmd = ProjectCmd(verbose)
        match project_type:
            case ProjectType.INTEGRATION:
                if ctx.get_parameter_source("mode") == click.core.ParameterSource.DEFAULT:
                    mode = click.prompt(
                        text="Choose the project generation mode",
                        default="prj",
                        type=click.Choice(["prj", "all"], case_sensitive=False),
                        show_default=True,
                        show_choices=True,
                    )
                if not skip_model_update:
                    click.echo("Updating integration project model before generation.")
                    __update_vaf_model(project_type, project_dir, input_file, mode)
                click.echo(f"Generating integration project for {mode} based on model in {input_file}")
                cmd.generate_integration(
                    input_file,
                    project_dir,
                    mode,
                    type_variant,
                    disable_auto_merge=no_merge,
                )

                if not skip_make_preset:
                    click.echo("Running vaf make preset.")
                    if mode == "all":
                        # Execute cmake preset for all included app-module projects
                        for pr_path, _ in get_projects_in_path(Path(project_dir)):
                            __run_make_preset_release(project_dir=pr_path)
                    __run_make_preset_release()

            case ProjectType.APP_MODULE:
                click.echo("\nSkipping generation mode selection as the project is not an integration project.")

                if not skip_model_update:
                    click.echo("Updating integration project model before generation.")
                    __update_vaf_model(project_type, project_dir, input_file, "prj")
                click.echo(f"\nGenerating application module based on model in {input_file}")
                cmd.generate_app_module(
                    input_file,
                    project_dir,
                    type_variant,
                    disable_auto_merge=no_merge,
                )

                if not skip_make_preset:
                    click.echo("Running vaf make preset.")
                    __run_make_preset_release()
            case _:
                click.echo("\nInvalid VAF project for project generate command.")


# vaf project import #
@click.command()
# This option has to come before all options mentioned in the disable_param_for_project_type dictionary.
@click.option(
    "-p",
    "--project-dir",
    cls=DisableForProjectOption,
    disable_param_for_project_type={
        ProjectType.INTEGRATION: ["input-file"],
        ProjectType.APP_MODULE: ["input-dir"],
    },
    type=click.Path(exists=True, file_okay=False, writable=True),
    required=False,
    help="Path to the project root directory.",
    default=".",
)
@filepath_option(
    "--input-dir",
    type=click.Path(exists=True, file_okay=False, writable=False),
    required=True,
    help="Path to the application module project to be imported. "
    "Applicable only for the app-module import into an integration project.",
    prompt="Enter the path to the application module project to be imported:",
)
@click.option(
    "--pre-path",
    type=click.Path(exists=False, file_okay=False, writable=False),
    help="Relative pre-path to the app-module directory: <project_root_dir>/src/application_modules/<pre_path>/<app_module_dir>",  # pylint: disable=line-too-long
    default=".",
    required=False,
)
@click.option(
    "-m",
    "--model-dir",
    type=click.Path(exists=True, file_okay=False, writable=True),
    required=False,
    help="Path to the VAF model directory.",
)
@filepath_option(
    "--input-file",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to the exported VAF model JSON file(from the interface project). "
    "Applicable only for the interface import into an application module project.",
    required=True,
    prompt="Please provide the path to the exported VAF model JSON file",
)
@click.option(
    "--force-import",
    is_flag=True,
    help="Carry out import in any case. Will overwrite existing files.",
)
@click.option(
    "--skip-import",
    is_flag=True,
    help="Cancel operation directly in case of a re-import.",
)
@click.argument(
    "import-mode",
    default="copy",
    type=click.Choice(["copy", "reference"], case_sensitive=False),
)
def project_import(  # pylint: disable=missing-param-doc, too-many-positional-arguments, too-many-arguments
    project_dir: str,
    input_dir: str,
    pre_path: str,
    input_file: str,
    force_import: bool,
    skip_import: bool,
    import_mode: str,
    model_dir: Optional[str] = None,
) -> None:
    """Import an interface/app-module project to the given project based on the project type."""
    # Look for project type in VAF_CFG_FILE in the project directory
    project_type = get_project_type(Path(project_dir))

    if model_dir is None:
        model_dir = _get_default_model_path(project_type)

    if project_type == ProjectType.UNKNOWN:
        click.echo("\nNo valid VAF project found!")
    elif project_type == ProjectType.INTEGRATION:
        click.echo(f"Importing an app-module from {input_dir} to the integration project {model_dir}.")
        project_cmd = ProjectCmd()
        project_cmd.import_appmodule(input_dir, project_dir, pre_path, model_dir)
    elif project_type == ProjectType.APP_MODULE:
        click.echo(f"Importing an interface from {input_file} to the app-module project {model_dir}.")
        model_cmd = ModelCmd()
        model_cmd.import_model(input_file, model_dir, import_mode, force_import, skip_import)
    else:
        click.echo("\nInvalid VAF project type for project import command.")


# vaf project remove group #
@click.group()
def project_remove() -> None:
    """Remove the specified project artifacts from the given project."""


def __validate_integration_project_dir(ctx: click.Context, option: click.Option, value: str) -> str:  # pylint: disable = unused-argument
    """Validates that the given project directory is an integration project."""
    if get_project_type(Path(value)) != ProjectType.INTEGRATION:
        raise click.BadParameter("This command is only supported for integration projects.")
    return value


# vaf project remove app_module #
@project_remove.command(name="app-module")
@sanatized_str_option(
    "-n",
    "--name",
    type=str,
    required=True,
    help="App-module name.",
    prompt="Enter the name of the app-module",
)
@filepath_option(
    "-p",
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, writable=True),
    required=True,
    help="Path to the project root directory.",
    default=".",
    prompt="Enter the path to the project root directory",
    callback=__validate_integration_project_dir,
)
# This option has to come before the --app-modules option, because the app-modules are populated by it's callback
@filepath_option(
    cls=modifying_choice_fp_option("-m", "--model-dir", choice_to_modify="app-modules"),
    type=click.Path(exists=True, file_okay=False, writable=True),
    help="Path to the model directory.",
    default=lambda: _get_default_model_path(get_project_type_for_project_dir()),
    prompt="Enter the path to the model directory",
)
@choice_option(
    "--app-modules",
    prompt="Choose one ore more application modules",
    type=click.Choice([]),
    help="Absolute path to the application module project to remove. Specify multiple times for multiple modules.",
    multiple=True,
)
def project_remove_app_module(  # pylint: disable=missing-param-doc,unused-argument
    name: str,
    project_dir: Path | str,
    model_dir: Path | str,
    app_modules: list[str],
) -> None:
    """Remove an app-module from an integration project."""
    # This workaround is necessary, because of the hacky solution to support only one choice in
    # ModifyingChoiceFpOption.callback_handler()
    if isinstance(app_modules, str):
        app_modules = [app_modules]

    cmd = ProjectCmd()
    cmd.remove_appmodule(Path(project_dir), Path(model_dir), app_modules)
