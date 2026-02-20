# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Convenience Functions for CLI Integration

This module contains utility functions for creating delta objects and managing
the undo system in CLI applications.
"""

from pathlib import Path

from vaf.core.state_manager.data_model import DeltaType, FileDelta
from vaf.core.state_manager.state_manager import StatusQuoOrdinator


# Convenience functions for CLI integration
def create_file_delta(target_path: str, content: str, processed: bool = False) -> FileDelta:
    """Create a delta for file creation.

    Args:
        target_path (str): The path of the target file.
        content (str): The content to be written to the file.
        processed (bool): Whether the delta has already been processed. Defaults to False.

    Returns:
        FileDelta: The file delta object representing the creation operation.
    """
    return FileDelta(
        delta_type=DeltaType.FILE_CREATE,
        target_path=target_path,
        new_content=content,
        file_existed=False,
        processed=processed,
    )


def modify_file_delta(target_path: str, old_content: str, new_content: str, processed: bool = False) -> FileDelta:
    """Create a delta for file modification.

    Args:
        target_path (str): The path of the target file.
        old_content (str): The original content of the file.
        new_content (str): The new content to replace the old content.
        processed (bool): Whether the delta has already been processed. Defaults to False.

    Returns:
        FileDelta: The file delta object representing the modification operation.
    """
    return FileDelta(
        delta_type=DeltaType.FILE_MODIFY,
        target_path=target_path,
        old_content=old_content,
        new_content=new_content,
        file_existed=True,
        processed=processed,
    )


def delete_file_delta(target_path: str, content: str, processed: bool = False) -> FileDelta:
    """Create a delta for file deletion.

    Args:
        target_path (str): The path of the target file.
        content (str): The content of the file to be deleted.
        processed (bool): Whether the delta has already been processed. Defaults to False.

    Returns:
        FileDelta: The file delta object representing the deletion operation.
    """
    return FileDelta(
        delta_type=DeltaType.FILE_DELETE,
        target_path=target_path,
        old_content=content,
        file_existed=True,
        processed=processed,
    )


def create_file_symlink_delta(
    target_path: str, symlink_target: str, relative_to: str | None = None, processed: bool = False
) -> FileDelta:
    """
    Create a delta for symlink creation.

    Args:
        target_path (str): The path where the symlink will be created.
        symlink_target (str): The target path the symlink will point to.
        relative_to (str | None): Base path for relative symlink creation, or None for absolute.
        processed (bool): Whether the delta has already been processed. Defaults to False.

    Returns:
        FileDelta: The file delta object representing the symlink creation operation.

    Raises:
        ValueError: If the source path is a symlink or if the target and source paths
                   are not both files or both directories.
    """
    return FileDelta(
        delta_type=DeltaType.SYMLINK_FILE_CREATE,
        target_path=target_path,
        symlink_target=symlink_target,
        relative_to=relative_to,
        file_existed=False,
        processed=processed,
    )


def delete_file_symlink_delta(target_path: str, symlink_target: str, processed: bool = False) -> FileDelta:
    """
    Create a delta for symlink deletion.

    Args:
        target_path (str): The path of the symlink to be deleted.
        symlink_target (str): The target path the symlink points to.
        processed (bool): Whether the delta has already been processed. Defaults to False.

    Returns:
        FileDelta: The file delta object representing the symlink deletion operation.

    Raises:
        ValueError: If the source path is a symlink or if the target and source paths
                   are not both files or both directories.
    """
    return FileDelta(
        delta_type=DeltaType.SYMLINK_FILE_DELETE,
        target_path=target_path,
        symlink_target=symlink_target,
        file_existed=False,
        processed=processed,
    )


def create_dir_delta(target_path: str, processed: bool = False) -> FileDelta:
    """
    Create a delta for directory creation.

    Args:
        target_path (str): The path of the directory to be created.
        processed (bool): Whether the delta has already been processed. Defaults to False.

    Returns:
        FileDelta: The file delta object representing the directory creation operation.
    """
    return FileDelta(
        delta_type=DeltaType.DIR_CREATE,
        target_path=target_path,
        file_existed=False,
        processed=processed,
    )


def delete_dir_delta(target_path: str, processed: bool = False) -> FileDelta:
    """
    Create a delta for directory removal.

    Args:
        target_path (str): The path of the directory to be removed.
        processed (bool): Whether the delta has already been processed. Defaults to False.

    Returns:
        FileDelta: The file delta object representing the directory removal operation.
    """
    return FileDelta(
        delta_type=DeltaType.DIR_DELETE,
        target_path=target_path,
        file_existed=True,
        processed=processed,
    )


def create_dir_symlink_delta(
    target_path: str, symlink_target: str, relative_to: str | None = None, processed: bool = False
) -> FileDelta:
    """
    Create a delta for directory symlink creation.

    Args:
        target_path (str): The path where the symlink will be created.
        symlink_target (str): The target path the symlink will point to.
        relative_to (str | None): Base path for relative symlink creation, or None for absolute.
        processed (bool): Whether the delta has already been processed. Defaults to False.

    Returns:
        FileDelta: The file delta object representing the directory symlink creation operation.

    Raises:
        ValueError: If the source path is a symlink or if the target and source paths
                   are not both directories.
    """
    return FileDelta(
        delta_type=DeltaType.SYMLINK_DIR_CREATE,
        target_path=target_path,
        symlink_target=symlink_target,
        relative_to=relative_to,
        file_existed=False,
        processed=processed,
    )


def delete_dir_symlink_delta(target_path: str, symlink_target: str, processed: bool = False) -> FileDelta:
    """
    Create a delta for directory symlink deletion.

    Args:
        target_path (str): The path of the symlink to be deleted.
        symlink_target (str): The target path the symlink points to.
        processed (bool): Whether the delta has already been processed. Defaults to False.

    Returns:
        FileDelta: The file delta object representing the directory symlink deletion operation.

    Raises:
        ValueError: If the source path is a symlink or if the target and source paths
                   are not both directories.
    """
    return FileDelta(
        delta_type=DeltaType.SYMLINK_DIR_DELETE,
        target_path=target_path,
        symlink_target=symlink_target,
        file_existed=False,
        processed=processed,
    )


# Factory function for CLI integration
def get_state_manager(project_dir: str = ".") -> StatusQuoOrdinator:
    """
    Factory function to create a state manager instance.

    This function provides a `TrailSheriff` instance for managing file system
    deltas and enabling undo/redo functionality in CLI applications.

    Args:
        project_dir (str): Path to the VAF project directory. Defaults to the current directory.

    Returns:
        TrailSheriff: A new instance of the state manager.
    """
    return StatusQuoOrdinator(Path(project_dir))
