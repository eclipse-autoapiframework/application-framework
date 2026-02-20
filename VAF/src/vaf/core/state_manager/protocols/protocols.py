# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Protocol Interfaces for State Manager

This module defines all protocol interfaces used by the state manager system,
breaking circular dependencies and enabling structural typing.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Protocol, runtime_checkable


class DeltaTypeProtocol(Protocol):
    """Protocol for DeltaType enum values."""

    def apply_forward(self, delta: "FileDeltaInterface") -> None:
        """
        Apply the delta in the forward direction.

        Args:
            delta (FileDeltaInterface): The delta to apply.
        """

    def apply_reverse(self, delta: "FileDeltaInterface") -> None:
        """
        Apply the delta in the reverse direction.

        Args:
            delta (FileDeltaInterface): The delta to reverse.
        """


@runtime_checkable
class FileDeltaInterface(Protocol):
    """Protocol interface for delta data - breaks circular dependencies.

    Design Note:
    This class uses Python's `Protocol` to define a structural interface for file deltas.
    This approach ensures flexibility by allowing any class with matching attributes and methods
    to be considered a valid implementation, without requiring explicit inheritance.

    If runtime performance becomes critical, especially with frequent `isinstance` checks, consider
    switching to an Abstract Base Class (ABC). While ABCs require explicit inheritance, they
    provide faster `isinstance` checks.
    """

    @property
    def delta_type(self) -> DeltaTypeProtocol:
        """
        Get the type of the delta.

        Returns:
            DeltaTypeProtocol: The type of the delta (e.g., FILE_CREATE, FILE_DELETE).
        """

    @property
    def target_path(self) -> str:
        """
        Get the target path of the delta.

        Returns:
            str: The target path as a string.
        """

    @property
    def old_content(self) -> Optional[str]:
        """
        Get the old content of the delta (if applicable).

        Returns:
            Optional[str]: The old content of the file, or None if not applicable.
        """

    @property
    def new_content(self) -> Optional[str]:
        """
        Get the new content of the delta (if applicable).

        Returns:
            Optional[str]: The new content of the file, or None if not applicable.
        """

    @property
    def old_path(self) -> Optional[str]:
        """
        Get the old path of the delta (if applicable).

        Returns:
            Optional[str]: The old path as a string, or None if not applicable.
        """

    @property
    def file_existed(self) -> bool:
        """
        Check if the file existed before the delta operation.

        Returns:
            bool: True if the file existed, False otherwise.
        """

    @property
    def timestamp(self) -> float:
        """
        Get the timestamp of the delta operation.

        Returns:
            float: The timestamp as a Unix epoch time.
        """

    @property
    def checksum(self) -> Optional[str]:
        """
        Get the checksum of the file (if applicable).

        Returns:
            Optional[str]: The checksum as a string, or None if not applicable.
        """

    @property
    def symlink_target(self) -> Optional[str]:
        """
        Get the target path of the symlink (if applicable).

        Returns:
            Optional[str]: The symlink target path as a string, or None if not applicable.
        """

    @property
    def relative_to(self) -> Optional[str]:
        """
        Get the base path for relative symlink creation (if applicable).

        When provided, the symlink will be created as a relative path from this base directory.
        If None, an absolute symlink path will be used.

        Returns:
            Optional[str]: The base path for relative symlink creation, or None for absolute symlinks.
        """

    @property
    def processed(self) -> bool:
        """
        Check if the delta has been processed.

        Returns:
            bool: True if the delta has already been processed (e.g., via run copy), False otherwise.
        """

    @processed.setter
    def processed(self, value: bool) -> None:
        """
        Set the processed status of the delta.

        Args:
            value (bool): True to mark the delta as processed, False otherwise.
        """


class RunCopyCallableProtocol(Protocol):  # pylint: disable=too-few-public-methods
    """
    Protocol for the run_copy callable.

    This callable is responsible for copying templates and handling data during the generation process.
    """

    def __call__(self, template: str, destination: Path, data: Optional[Dict[str, Any]] = None, **kwargs: Any) -> None:
        """
        Execute the run_copy operation.

        Args:
            template (str): Path to the template to copy.
            destination (Path): Destination path for the copied template.
            data (Optional[Dict[str, Any]]): Data to be used for template rendering. Defaults to None.
        """
