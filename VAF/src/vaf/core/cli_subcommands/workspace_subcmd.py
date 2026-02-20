# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Source code for vaf workspace subcommands"""

import click

from vaf.core.common.click_extension import filepath_option, sanatized_str_option
from vaf.core.objects.workspace_cmd import WorkspaceCmd


# vaf workspace init #
@click.command()
@sanatized_str_option(
    "-n",
    "--name",
    type=str,
    required=True,
    help="Name of the workspace.",
    prompt="Enter your workspace name",
)
@filepath_option(
    "-w",
    "--workspace-dir",
    type=click.Path(exists=False, writable=True, file_okay=False),
    default=".",
    required=True,
    help="Path to directory where the workspace is to be created.",
    prompt="Enter the directory to store your workspace in",
)
@click.option(
    "-m",
    "--mount",
    type=click.Path(exists=True, file_okay=False, readable=True),
    multiple=True,
    help="Mount a directory into the DevContainer. Can be specified multiple times.",
)
def workspace_init(name: str, workspace_dir: str, mount: tuple[str, ...]) -> None:  # pylint: disable=missing-param-doc
    """Initiate a VAF workspace with devcontainer and VS Code settings."""
    cmd = WorkspaceCmd()
    cmd.init(name, workspace_dir, mount)
