# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Symlink Operations Handlers and Validators

This module contains all symlink-related handlers and validators for the stateless undo system.
"""

import os
from pathlib import Path

from vaf.core.state_manager.protocols.protocols import FileDeltaInterface


def _compute_symlink_target(symlink_target: Path, relative_to: Path | None) -> str:
    """
    Compute the symlink target path (absolute or relative).

    Args:
        symlink_target (Path): The target path the symlink will point to.
        relative_to (Path | None): Base path for relative symlink creation, or None for absolute.

    Returns:
        str: The path to use for creating the symlink (absolute or relative).

    Raises:
        ValueError: If relative_to is provided but doesn't exist or isn't a directory.
    """
    if relative_to is None:
        # Absolute path mode (backward compatibility)
        return str(symlink_target)

    # Validate relative_to parameter
    if not relative_to.exists():
        raise ValueError(f"relative_to path does not exist: {relative_to}")
    if not relative_to.is_dir():
        raise ValueError(f"relative_to must be a directory: {relative_to}")

    # Compute relative path
    return os.path.relpath(symlink_target, relative_to)


class SymlinkValidator:  # pylint: disable=too-few-public-methods
    """
    Utility class for validating symlink paths.

    This class provides static methods to validate symlink paths before performing
    file system operations. It ensures that operations are performed on valid
    paths and prevents unintended behavior.
    """

    @staticmethod
    def validate_symlink_target(symlink_target: Path) -> None:
        """
        Validate that the symlink target is valid.

        Args:
            symlink_target (Path): The symlink target path to validate.

        Raises:
            ValueError: If the symlink target is invalid.

        Example:
            SymlinkValidator.validate_symlink_target(Path("target_file.txt"))
        """
        if not symlink_target.exists():
            raise ValueError(f"Invalid symlink target: {symlink_target}")
        if symlink_target.is_symlink():
            raise ValueError(f"Symlink target {symlink_target} cannot be a symlink")


class SymlinkFileCreateHandler:
    """Pure utility class for file symlink creation operations."""

    @staticmethod
    def validate(symlink_target: Path, target_path: Path) -> None:
        """
        Validate the delta before applying it.

        Args:
            symlink_target (Path): The target path the symlink will point to.
            target_path (Path): The path where the symlink will be created.

        Raises:
            FileExistsError: If the target path already exists.
        """
        SymlinkValidator.validate_symlink_target(symlink_target)
        if target_path.exists():
            raise FileExistsError(f"Target path already exists: {target_path}")

    @classmethod
    def apply_forward(cls, delta: FileDeltaInterface) -> None:
        """
        Validate and apply the delta.

        Args:
            delta (FileDeltaInterface): The delta to apply.

        Raises:
            ValueError: If the symlink target is not specified.
        """
        if not delta.symlink_target:
            raise ValueError("Symlink target must be specified")

        target_path = Path(delta.target_path)
        symlink_target = Path(delta.symlink_target)
        relative_to = Path(delta.relative_to) if delta.relative_to else None

        cls.validate(symlink_target, target_path)

        # Compute the actual path to use for symlink (absolute or relative)
        link_target = _compute_symlink_target(symlink_target, relative_to)

        target_path.symlink_to(link_target)

    @classmethod
    def apply_reverse(cls, delta: FileDeltaInterface) -> None:
        """
        Validate and reverse the delta.

        Args:
            delta (FileDeltaInterface): The delta to reverse.
        """
        target_path = Path(delta.target_path)
        if target_path.is_symlink():
            target_path.unlink()


class SymlinkFileDeleteHandler:
    """Pure utility class for file symlink deletion operations."""

    @staticmethod
    def apply_forward(delta: FileDeltaInterface) -> None:
        """
        Validate and apply the delta.

        Args:
            delta (FileDeltaInterface): The delta to apply.
        """
        SymlinkFileCreateHandler.apply_reverse(delta)

    @staticmethod
    def apply_reverse(delta: FileDeltaInterface) -> None:
        """
        Validate and reverse the delta.

        Args:
            delta (FileDeltaInterface): The delta to reverse.
        """
        SymlinkFileCreateHandler.apply_forward(delta)


class SymlinkDirCreateHandler:
    """Pure utility class for directory symlink creation operations."""

    @staticmethod
    def validate(symlink_target: Path, target_path: Path) -> None:
        """
        Validate the delta before applying it.

        Args:
            symlink_target (Path): The target path the symlink will point to.
            target_path (Path): The path where the symlink will be created.

        Raises:
            FileExistsError: If the target path already exists.
        """
        SymlinkValidator.validate_symlink_target(symlink_target)
        if target_path.exists():
            raise FileExistsError(f"Target path already exists: {target_path}")

    @classmethod
    def apply_forward(cls, delta: FileDeltaInterface) -> None:
        """
        Validate and apply the delta.

        Args:
            delta (FileDeltaInterface): The delta to apply.

        Raises:
            ValueError: If the symlink target is not specified.
        """
        if not delta.symlink_target:
            raise ValueError("Symlink target must be specified")

        target_path = Path(delta.target_path)
        symlink_target = Path(delta.symlink_target)
        relative_to = Path(delta.relative_to) if delta.relative_to else None

        cls.validate(symlink_target, target_path)

        # Compute the actual path to use for symlink (absolute or relative)
        link_target = _compute_symlink_target(symlink_target, relative_to)

        target_path.symlink_to(link_target)

    @classmethod
    def apply_reverse(cls, delta: FileDeltaInterface) -> None:
        """
        Validate and reverse the delta.

        Args:
            delta (FileDeltaInterface): The delta to reverse.
        """
        target_path = Path(delta.target_path)
        if target_path.is_symlink():
            target_path.unlink()


class SymlinkDirDeleteHandler:
    """Pure utility class for directory symlink deletion operations."""

    @staticmethod
    def apply_forward(delta: FileDeltaInterface) -> None:
        """
        Validate and apply the delta.

        Args:
            delta (FileDeltaInterface): The delta to apply.
        """
        SymlinkDirCreateHandler.apply_reverse(delta)

    @staticmethod
    def apply_reverse(delta: FileDeltaInterface) -> None:
        """
        Validate and reverse the delta.

        Args:
            delta (FileDeltaInterface): The delta to reverse.
        """
        SymlinkDirCreateHandler.apply_forward(delta)
