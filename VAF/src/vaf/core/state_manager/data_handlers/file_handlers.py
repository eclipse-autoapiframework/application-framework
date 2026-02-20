# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
File Operations Handlers and Validators

This module contains all file-related handlers and validators for the stateless undo system.
"""

from pathlib import Path

from vaf.core.state_manager.protocols.protocols import FileDeltaInterface


class FileValidator:
    """
    Utility class for validating file system paths.

    This class provides static methods to validate file paths before performing
    file system operations. It ensures that operations are performed on valid
    paths and prevents unintended behavior.
    """

    @staticmethod
    def validate_not_dir(file_path: Path) -> None:
        """
        Ensure the given path is not a directory.

        Args:
            file_path (Path): The file path to validate.

        Raises:
            IsADirectoryError: If the given path is a directory.

        Example:
            FileValidator.validate_not_dir(Path("example.txt"))
        """
        if file_path.is_dir():
            raise IsADirectoryError(f"Target path is a directory: {file_path}")

    @staticmethod
    def validate_exists(file_path: Path) -> None:
        """
        Ensure the given path exists.

        Args:
            file_path (Path): The file path to validate.

        Raises:
            FileNotFoundError: If the given path does not exist.

        Example:
            FileValidator.validate_exists("example.txt")
        """
        if not file_path.is_file():
            raise FileNotFoundError(f"Target path does not exist: {file_path}")


class FileCreateHandler:
    """Pure utility class for file creation operations."""

    @staticmethod
    def apply_forward(delta: FileDeltaInterface) -> None:
        """
        Validate and apply the delta.

        Args:
            delta (FileDeltaInterface): The delta to apply.

        Raises:
            ValueError: If new content is not provided for file creation.
            FileExistsError: If the file already exists.
        """
        if delta.new_content is None:
            raise ValueError("New content must be provided for file creation.")

        target_path = Path(delta.target_path)
        FileValidator.validate_not_dir(target_path)

        if target_path.is_file():
            raise FileExistsError(f"File already exists: {target_path}")

        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(delta.new_content, encoding="utf-8")

    @staticmethod
    def apply_reverse(delta: FileDeltaInterface) -> None:
        """
        Validate and reverse the delta.

        Args:
            delta (FileDeltaInterface): The delta to reverse.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        target_path = Path(delta.target_path)
        FileValidator.validate_not_dir(target_path)
        try:
            FileValidator.validate_exists(target_path)
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"Cannot delete non-existing file: {target_path}") from exc
        target_path.unlink()


class FileDeleteHandler:
    """Pure utility class for file deletion operations."""

    @staticmethod
    def apply_forward(delta: FileDeltaInterface) -> None:
        """
        Validate and apply the delta.

        Args:
            delta (FileDeltaInterface): The delta to apply.
        """
        FileCreateHandler.apply_reverse(delta)

    @staticmethod
    def apply_reverse(delta: FileDeltaInterface) -> None:
        """
        Validate and reverse the delta.

        Args:
            delta (FileDeltaInterface): The delta to reverse.
        """
        FileCreateHandler.apply_forward(delta)


class FileModifyHandler:
    """Pure utility class for file modification operations."""

    @staticmethod
    def validate(target_path: Path) -> None:
        """
        Validate the delta before applying it.

        Args:
            target_path (Path): The path to validate.
        """
        FileValidator.validate_not_dir(target_path)
        FileValidator.validate_exists(target_path)

    @classmethod
    def apply_forward(cls, delta: FileDeltaInterface) -> None:
        """
        Validate and apply the delta.

        Args:
            delta (FileDeltaInterface): The delta to apply.
        """
        target_path = Path(delta.target_path)
        cls.validate(target_path)
        if delta.new_content is not None:
            target_path.write_text(delta.new_content, encoding="utf-8")

    @classmethod
    def apply_reverse(cls, delta: FileDeltaInterface) -> None:
        """
        Validate and reverse the delta.

        Args:
            delta (FileDeltaInterface): The delta to reverse.
        """
        target_path = Path(delta.target_path)
        cls.validate(target_path)
        if delta.old_content is not None:
            target_path.write_text(delta.old_content, encoding="utf-8")
        elif not delta.file_existed:
            target_path.unlink(missing_ok=True)


class FileMoveHandler:
    """Pure utility class for file move operations."""

    @staticmethod
    def validate(target_path: Path, old_path: Path) -> None:
        """
        Validate the delta before applying it.

        Args:
            target_path (Path): The new path for the file.
            old_path (Path): The old path of the file.

        Raises:
            FileNotFoundError: If the old file does not exist.
        """
        FileValidator.validate_not_dir(old_path)
        FileValidator.validate_not_dir(target_path)
        FileValidator.validate_exists(target_path)
        if not old_path.is_file():
            raise FileNotFoundError(f"Cannot move non-existing file: {old_path}")

    @classmethod
    def apply_forward(cls, delta: FileDeltaInterface) -> None:
        """
        Validate and apply the delta.

        Args:
            delta (FileDeltaInterface): The delta to apply.
        """
        target_path = Path(delta.target_path)
        old_path = Path(delta.old_path) if delta.old_path else target_path
        cls.validate(target_path, old_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        old_path.rename(target_path)

    @classmethod
    def apply_reverse(cls, delta: FileDeltaInterface) -> None:
        """
        Validate and reverse the delta.

        Args:
            delta (FileDeltaInterface): The delta to reverse.

        Raises:
            ValueError: If the old content is not provided and the file did not exist before.
        """
        target_path = Path(delta.target_path)
        if delta.old_path is None:
            raise ValueError("Old path must be specified for reversing a move operation.")
        old_path = Path(delta.old_path)
        cls.validate(target_path, old_path)

        old_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.rename(old_path)
