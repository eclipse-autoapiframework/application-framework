# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Source code for vaf project init subcommand"""

import click

from vaf.core.common.click_extension import filepath_option, sanatized_str_option
from vaf.core.objects.project_init_cmd import ProjectInitCmd


# vaf project init group #
@click.group()
def project_init() -> None:
    """Initiate a project of chosen VAF project type and template."""


# vaf project init integration #
@project_init.command(name="integration")
@sanatized_str_option(
    "-n",
    "--name",
    type=str,
    required=True,
    help="Name of the project.",
    prompt="Enter your project name",
)
@filepath_option(
    "-p",
    "--project-dir",
    type=click.Path(exists=False, writable=True, file_okay=False),
    default=".",
    required=True,
    help="Path to output directory.",
    prompt="Enter the directory to store your project in",
)
@click.option(
    "-t",
    "--template",
    type=click.Path(file_okay=False),
    default="",
    help="Path to template directory.",
)
@click.option(
    "--skip-git-init",
    is_flag=True,
    help="Skip initialization of an empty git repository and introduction of a .gitignore file",
)
def integration_project_init(name: str, project_dir: str, template: str, skip_git_init: bool) -> None:  # pylint: disable=missing-param-doc
    """Creates a VAF integration project from the given template."""
    cmd = ProjectInitCmd()
    cmd.integration_project_init(name, project_dir, template, not skip_git_init)


# vaf interface project init #
@project_init.command(name="interface")
@sanatized_str_option(
    "-n",
    "--name",
    type=str,
    required=True,
    help="Name of the project.",
    prompt="Enter your project name",
)
@filepath_option(
    "-p",
    "--project-dir",
    type=click.Path(exists=False, writable=True, file_okay=False),
    required=True,
    help="Path to output directory.",
    default=".",
    prompt="Enter the directory to store your project in",
)
@click.option(
    "--skip-git-init",
    is_flag=True,
    help="Skip initialization of an empty git repository and introduction of a .gitignore file",
)
def interface_project_init(name: str, project_dir: str, skip_git_init: bool) -> None:  # pylint: disable=missing-param-doc
    """Creates a VAF interface project from the given template."""
    cmd = ProjectInitCmd()
    cmd.interface_project_init(name, project_dir, not skip_git_init)


# vaf app module project init  #
@project_init.command(name="app-module")
@sanatized_str_option(
    "-n",
    "--name",
    type=str,
    required=True,
    help="App-module name",
    prompt="Enter the name of the app-module",
)
@click.option(
    "--namespace",
    type=str,
    required=True,
    help="App-module namespace.",
    prompt="Enter the namespace of the app-module",
)
@filepath_option(
    "-p",
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, writable=True),
    required=True,
    help="Path to the output directory.",
    default=".",
    prompt="Enter the path to the output root directory",
)
@click.option(
    "--skip-git-init",
    is_flag=True,
    help="Skip initialization of an empty git repository and introduction of a .gitignore file",
)
def app_module_project_init(namespace: str, name: str, project_dir: str, skip_git_init: bool) -> None:  # pylint: disable=missing-param-doc
    """Creates a VAF app-module project from the given template."""
    click.echo(f"Init app-module {namespace}::{name} project.")
    cmd = ProjectInitCmd()
    cmd.app_module_project_init(namespace, name, project_dir, not skip_git_init)
