# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Setup click options to configure the help output of the CLI commands."""

import click

# Per default, click only displays help for --help option
# In our tools, we usually display help for both -h and --help
CLICK_CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


# Custom warning format to display warnings without stack trace or file info
def simple_user_warning(
    message: str | Warning,
    category: type[Warning],
    filename: str,
    lineno: int,
    line: str | None = None,
) -> str:
    # pylint: disable=unused-argument
    """Generates a simple user warning message without stack trace or file info.
    Args:
        message (str | Warning): The warning message to display.
        category (type[Warning]): The type of warning.
        filename (str): The filename related to the warning.
        lineno (int): The line number related to the warning.
        line (str | None): The line of code related to the warning.
    Returns:
        str: A formatted warning message.
    """
    return f"{category.__name__}: {message}\n"


class CustomHelpGroup(click.Group):
    """Custom click group to modify the CLI help output."""

    def _format_subcommands(self, cmd: click.Group, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        with formatter.indentation():
            sub_commands = cmd.list_commands(ctx)
            for index, sub_cmd_name in enumerate(sub_commands):
                sub_cmd = cmd.get_command(ctx, sub_cmd_name)
                if sub_cmd is not None:
                    formatter.write_text(f"{sub_cmd_name}: {sub_cmd.get_short_help_str(100)}")
                    if index == len(sub_commands) - 1:
                        # Add newline after last subcommand
                        formatter.write_paragraph()

    def format_commands(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        with formatter.section("Commands"):
            for cmd_name in self.list_commands(ctx):
                cmd = self.get_command(ctx, cmd_name)
                if cmd is not None:
                    formatter.write_text(f"{cmd_name}: {cmd.get_short_help_str(100)}")
                    if isinstance(cmd, click.Group):
                        self._format_subcommands(cmd, ctx, formatter)
