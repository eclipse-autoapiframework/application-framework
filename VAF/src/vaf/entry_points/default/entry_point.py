# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Initialize the module.
Could be used to define the public interface of the module.
CLI Function with the click module: e.g. "vaf version --help"
"""

# Python Standard Library imports
import warnings

# External imports
import click

from vaf.core.cli_subcommands.make_subcmd import (
    make_build,
    make_clean,
    make_install,
    make_preset,
)
from vaf.core.cli_subcommands.model_subcmd import (
    model_generate,
    model_import,
    model_update,
)
from vaf.core.cli_subcommands.platform_subcmd import (
    platform_derive,
    platform_export,
)
from vaf.core.cli_subcommands.project_init_subcmd import project_init
from vaf.core.cli_subcommands.project_subcmd import (
    project_create,
    project_generate,
    project_import,
    project_remove,
)

# Internal imports
from vaf.core.cli_subcommands.undo_subcmd import redo, undo
from vaf.core.cli_subcommands.workspace_subcmd import workspace_init
from vaf.core.common.click_help import (
    CLICK_CONTEXT_SETTINGS,
    CustomHelpGroup,
    simple_user_warning,
)
from vaf.core.common.constants import get_package_version

# Switch to simple user warning message without stack trace or file info.
warnings.formatwarning = simple_user_warning


@click.group(
    context_settings=CLICK_CONTEXT_SETTINGS,
    help=f"This is the Vehicle Application Framework command-line interface (vaf-cli) version {get_package_version()}",  # pylint: disable=line-too-long
    cls=CustomHelpGroup,
)
@click.version_option(get_package_version(), "-v", "--version", message="%(prog)s version %(version)s")
def cli() -> None:
    """This function is the entrypoint for the click arguments cli."""


# Command 'project'
@cli.group()
def project() -> None:
    """Project-related commands."""


# vaf project init #
project.add_command(name="init", cmd=project_init)
# vaf project create #
project.add_command(name="create", cmd=project_create)
# vaf project generate #
project.add_command(name="generate", cmd=project_generate)
# vaf project import #
project.add_command(name="import", cmd=project_import)
# vaf project remove #
project.add_command(name="remove", cmd=project_remove)
# vaf project undo #
project.add_command(name="undo", cmd=undo)
# vaf project redo #
project.add_command(name="redo", cmd=redo)


# Command 'platform'
@cli.group()
def platform() -> None:
    """Platform-related commands."""


# vaf platform derive #
platform.add_command(name="derive", cmd=platform_derive)

# vaf platform export #
platform.add_command(name="export", cmd=platform_export)


# Command 'model'
@cli.group()
def model() -> None:
    """Model-related commands."""


# vaf model import #
model.add_command(name="import", cmd=model_import)
# vaf model update #
model.add_command(name="update", cmd=model_update)
# vaf model generate #
model.add_command(name="generate", cmd=model_generate)


# Command 'make'
@cli.group()
def make() -> None:
    """Make-related commands."""


# vaf make preset #
make.add_command(name="preset", cmd=make_preset)
# vaf make build #
make.add_command(name="build", cmd=make_build)
# vaf make install #
make.add_command(name="install", cmd=make_install)
# vaf make clean #
make.add_command(name="clean", cmd=make_clean)


# Command 'workspace'
@cli.group()
def workspace() -> None:
    """Workspace-related commands."""


# vaf project init #
workspace.add_command(name="init", cmd=workspace_init)


if __name__ == "__main__":  # pragma: no cover
    cli()  # pylint: disable=no-value-for-parameter
