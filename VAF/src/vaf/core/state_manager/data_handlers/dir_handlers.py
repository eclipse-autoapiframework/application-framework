# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Directory Operations Handlers and Validators

This module contains all directory-related handlers and validators for the stateless undo system.
"""

from pathlib import Path

from vaf.core.state_manager.protocols.protocols import FileDeltaInterface


class DirValidator:
    """
    Utility class for validating directory paths.

    This class provides static methods to validate directory paths before performing
    file system operations. It ensures that operations are performed on valid
    paths and prevents unintended behavior.
    """

    @staticmethod
    def validate_exists(dir_path: Path) -> None:
        """
        Ensure the given directory exists and is not empty.

        Args:
            dir_path (Path): The directory path to validate.

        Raises:
            FileNotFoundError: If the given directory doesn't exist or is empty.

        Example:
            DirValidator.validate_exists(Path("example_dir"))
        """
        if not dir_path.is_dir() or not any(dir_path.iterdir()):
            raise FileNotFoundError(f"Directory does not exist or is empty: {dir_path}")

    @staticmethod
    def validate_not_file(dir_path: Path) -> None:
        """
        Ensure the given path is not a file.

        Args:
            dir_path (Path): The directory path to validate.

        Raises:
            FileExistsError: If the given path is a file.

        Example:
            DirValidator.validate_not_file(Path("example_dir"))
        """
        if dir_path.is_file():
            raise FileExistsError(f"Target path is a file: {dir_path}")


class DirCreateHandler:
    """Pure utility class for directory creation operations."""

    @staticmethod
    def apply_forward(delta: FileDeltaInterface) -> None:
        """
        Validate and apply the delta.

        Args:
            delta (FileDeltaInterface): The delta to apply.

        Raises:
            FileExistsError: If the directory already exists.
        """
        target_path = Path(delta.target_path)
        DirValidator.validate_not_file(target_path)

        if target_path.exists():
            raise FileExistsError(f"Directory already exists: {target_path}")

        target_path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def apply_reverse(delta: FileDeltaInterface) -> None:
        """
        Validate and reverse the delta.

        Args:
            delta (FileDeltaInterface): The delta to reverse.
        """
        target_path = Path(delta.target_path)

        if target_path.exists() and target_path.is_dir():
            target_path.rmdir()
            # Remove empty parent directories
            for parent in target_path.parents:
                try:
                    parent.rmdir()
                except OSError:
                    break


class DirDeleteHandler:
    """Pure utility class for directory deletion operations."""

    @staticmethod
    def apply_forward(delta: FileDeltaInterface) -> None:
        """
        Validate and apply the delta.

        Args:
            delta (FileDeltaInterface): The delta to apply.
        """
        DirCreateHandler.apply_reverse(delta)

    @staticmethod
    def apply_reverse(delta: FileDeltaInterface) -> None:
        """
        Validate and reverse the delta.

        Args:
            delta (FileDeltaInterface): The delta to reverse.
        """
        DirCreateHandler.apply_forward(delta)
