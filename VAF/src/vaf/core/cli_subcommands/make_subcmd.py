# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Source code for vaf project subcommands"""

from pathlib import Path
from typing import Optional

import click

from vaf.core.common.utils import ProjectType, get_project_type
from vaf.core.objects.make_cmd import MakeCmd


# vaf make preset #
@click.command()
@click.option(
    "-p",
    "--project-dir",
    type=click.Path(exists=False, file_okay=False, writable=True),
    default=".",
    help="Path to the project root directory",
    show_default=True,
)
@click.option(
    "-b",
    "--build-dir",
    type=click.Path(exists=False, file_okay=False, writable=True),
    help="Build directory",
    show_default=True,
)
@click.option(
    "-t",
    "--build-type",
    help="Type variant of build, either 'Debug' or 'Release'",
    type=click.Choice(["Debug", "Release"], case_sensitive=True),
    default="Release",
    show_default=True,
)
@click.option(
    "-c",
    "--compiler",
    help="Compiler version",
    type=str,
    default="gcc12__x86_64-pc-linux-elf",
    show_default=True,
)
@click.option(
    "-d",
    "--defines",
    type=str,
    default="",
    help="Additional defines, -d -DVAF_BUILD_TESTS=OFF",
    show_default=True,
)
# pylint: disable=too-many-arguments, too-many-positional-arguments
def make_preset(
    project_dir: str,
    compiler: str,
    build_type: str,
    defines: str,
    build_dir: Optional[str] = None,
    verbose: bool = True,
) -> None:
    """
    Preset the project build dependencies.
    :param project_dir: Project directory.
    :param build_dir: Build directory.
    :param compiler: Compiler version.
    :param build_type: Debug or release build.
    :param defines: Set defines.
    :param verbose: enable verbose mode (show full CMake output)
    """
    path_project = Path(project_dir)
    # Look for project type in VAF_CFG_FILE in the project directory
    project_type = get_project_type(path_project)
    if build_dir is None:
        build_dir = (path_project / "build").as_posix()
    if project_type == ProjectType.UNKNOWN:
        click.echo("\nNo valid VAF project found!")
    elif project_type in {ProjectType.INTEGRATION, ProjectType.APP_MODULE}:
        cmd = MakeCmd(verbose)
        cmd.preset(build_dir, compiler, build_type, defines, path_project.as_posix())
    else:
        click.echo("\nInvalid VAF project type for make preset command.")


# vaf make build #
@click.command()
@click.option(
    "-p",
    "--project-dir",
    type=click.Path(exists=False, file_okay=False, writable=True),
    default=".",
    help="Path to the project root directory",
    show_default=True,
)
@click.option(
    "--preset",
    required=True,
    type=click.Choice(["conan-debug", "conan-release"], case_sensitive=True),
    default="conan-release",
    show_default=True,
)
def make_build(project_dir: str, preset: str) -> None:
    """
    Build the project artifacts.
    :param project_dir: Project directory.
    :param preset: CMake preset.

    """
    # Look for project type in VAF_CFG_FILE in the project directory
    project_type = get_project_type(Path(project_dir))
    if project_type == ProjectType.UNKNOWN:
        click.echo("\nNo valid VAF project found!")
    elif project_type in {ProjectType.INTEGRATION, ProjectType.APP_MODULE}:
        cmd = MakeCmd()
        cmd.build(preset)
    else:
        click.echo("\nInvalid VAF project type for make build command.")


# vaf make clean #
@click.command()
@click.argument("mode", type=click.Choice(["all", "not_all"], case_sensitive=False), default="not_all", nargs=1)
@click.option(
    "-p",
    "--project-dir",
    type=click.Path(exists=False, file_okay=False, writable=True),
    default=".",
    help="Path to the project root directory",
    show_default=True,
)
@click.option(
    "--preset",
    type=click.Choice(["conan-debug", "conan-release"], case_sensitive=True),
    default="conan-release",
    show_default=True,
)
def make_clean(mode: str, project_dir: str, preset: str) -> None:
    """
    Clean up the project build directory.
    :param mode: Mode of the clean all or not all.
    :param project_dir: Project directory.
    :param preset: CMake preset.

    """
    # Look for project type in VAF_CFG_FILE in the project directory
    project_type = get_project_type(Path(project_dir))
    if project_type == ProjectType.UNKNOWN:
        click.echo("\nNo valid VAF project found!")
    elif project_type in {ProjectType.INTEGRATION, ProjectType.APP_MODULE}:
        cmd = MakeCmd()
        if mode == "all":
            cmd.clean_all()
        elif mode == "not_all":
            cmd.clean(preset)
    else:
        click.echo("\nInvalid VAF project type for make clean command.")


# vaf make install #
@click.command()
@click.option(
    "-p",
    "--project-dir",
    type=click.Path(exists=False, file_okay=False, writable=True),
    default=".",
    help="Path to the project root directory",
    show_default=True,
)
@click.option(
    "--preset",
    required=True,
    type=click.Choice(["conan-debug", "conan-release"], case_sensitive=True),
    default="conan-release",
    show_default=True,
)
def make_install(project_dir: str, preset: str) -> None:
    """
    Install the built artifacts to build/<build-type>/install directory.
    :param project_dir: Project directory.
    :param preset: CMake preset.

    """
    # Look for project type in VAF_CFG_FILE in the project directory
    project_type = get_project_type(Path(project_dir))
    if project_type == ProjectType.UNKNOWN:
        click.echo("\nNo valid VAF project found!")
    elif project_type in {ProjectType.INTEGRATION, ProjectType.APP_MODULE}:
        cmd = MakeCmd()
        cmd.install(preset)
    else:
        click.echo("\nInvalid VAF project type for make install command.")
