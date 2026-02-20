# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Source code for vaf undo subcommands"""

from enum import Enum

import click

from vaf.core.state_manager.factory import get_state_manager
from vaf.core.state_manager.state_manager import StatusQuoOrdinator


class _ProcessType(Enum):
    LIST = "list"
    CLEAR = "clear"
    NADA = "no thing"


def _process_history_info(
    manager: StatusQuoOrdinator,
    list_history: bool,
    clear_history: bool,
) -> None:
    """
    Handle common logic to read or clear history info.

    Args:
        manager: The state manager instance.
        steps (int): Number of commands to undo/redo.
        list_history (bool): Flag to list recent commands.
        clear_history (bool): Flag to clear undo/redo history.
        is_undo (bool): True for undo, False for redo.
    """
    if list_history:
        process = _ProcessType.LIST
    elif clear_history:
        process = _ProcessType.CLEAR
    else:
        process = _ProcessType.NADA

    match process:
        case _ProcessType.CLEAR:
            if manager.clear_history():
                click.echo("History cleared successfully.")
            else:
                click.echo("Failed to clear history.")
            return

        case _ProcessType.LIST:
            history_info = manager.get_history()
            operations = history_info.get("operations", [])

            current_position = history_info.get("current_position", 0)

            if not operations:
                click.echo("No operations in history.")
                return

            click.echo(
                f"Operation history (Position: {history_info['current_position']}/{history_info['total_operations']}):"
            )
            click.echo(f"Can undo: {history_info['can_undo']}, Can redo: {history_info['can_redo']}")
            click.echo()

            # Show last 10 operations
            for op in reversed(operations):
                position = op.get("position", "Unknown")
                description = op.get("description", "Unknown operation")
                is_current = op.get("is_current", False)

                marker = "→" if is_current else " "
                box = "☑" if position <= current_position else "☐"
                click.echo(f"  {marker} {box} [Position {position}] {description}")
            return


# CLI command for undo functionality
@click.command()
@click.option("--steps", "-n", default=1, help="Number of commands to undo (default: 1)")
@click.option("--list", "list_history", is_flag=True, help="List recent commands")
@click.option("--clear", "clear_history", is_flag=True, help="Clear undo history")
@click.option("--project-dir", "-p", default=".", help="Project directory (default: current directory)")
def undo(steps: int, list_history: bool, clear_history: bool, project_dir: str) -> None:
    """
    Undo recent VAF commands using stateless delta-based undo system.

    Args:
        steps (int): Number of commands to undo.
        list_history (bool): Flag to list recent commands.
        clear_history (bool): Flag to clear undo history.
        project_dir (str): Path to the project directory.
    """
    manager = get_state_manager(project_dir)
    _process_history_info(manager, list_history, clear_history)
    if not list_history and not clear_history:
        _, message = manager.undo(steps)
        click.echo(message)


# CLI command for redo functionality
@click.command()
@click.option("--steps", "-n", default=1, help="Number of commands to redo (default: 1)")
@click.option("--list", "list_history", is_flag=True, help="List recent commands")
@click.option("--clear", "clear_history", is_flag=True, help="Clear redo history")
@click.option("--project-dir", "-p", default=".", help="Project directory (default: current directory)")
def redo(steps: int, list_history: bool, clear_history: bool, project_dir: str) -> None:
    """
    Redo recent VAF commands using stateless delta-based undo system.

    Args:
        steps (int): Number of commands to redo.
        list_history (bool): Flag to list recent commands.
        clear_history (bool): Flag to clear redo history.
        project_dir (str): Path to the project directory.
    """
    manager = get_state_manager(project_dir)
    _process_history_info(manager, list_history, clear_history)
    if not list_history and not clear_history:
        _, message = manager.redo(steps)
        click.echo(message)
