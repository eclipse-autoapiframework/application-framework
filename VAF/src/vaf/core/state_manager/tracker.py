# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Undo Integration Module

This module provides utilities for tracking file operations and enabling
undo/redo functionality. It includes the TrailSheriff class for managing
deltas, the tracking_context context manager for scoped tracking, and the
activate_tracking decorator for CLI command integration.
"""

import inspect
import uuid
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Generator, List, Optional, Union

from copier import run_copy

from vaf.core.state_manager.data_model import FileDelta, OperationGroup
from vaf.core.state_manager.factory import (
    create_dir_delta,
    create_dir_symlink_delta,
    create_file_delta,
    create_file_symlink_delta,
    delete_dir_delta,
    delete_dir_symlink_delta,
    delete_file_delta,
    delete_file_symlink_delta,
    get_state_manager,
    modify_file_delta,
)


class TrailSheriff:
    """
    Context-aware tracker for file operations that automatically
    creates deltas for undo/redo functionality.
    """

    def __init__(self, description: str) -> None:
        """
        Initialize undo tracker.

        Args:
            description: Human-readable description of the operation
        """
        self.description = description
        self.deltas: List[FileDelta] = []
        self.operation_id = str(uuid.uuid4())
        self.manager = get_state_manager()

    # PUBLIC METHODS FOR PROCESSING AND RUN COPY WITH TRACKER
    def finalize(self, append_position: bool = True) -> None:
        """
        Finalize the operation and record it for undo/redo.

        Args:
            append_position: If True, append as a new operation; if False, overwrite the last
        """
        if self.deltas:
            operation = OperationGroup(
                operation_id=self.operation_id,
                description=self.description,
                deltas=self.deltas,
                timestamp=self.deltas[0].timestamp,
                completed=True,
            )
            self.manager.record_operation(operation, append_position=append_position)

    def run_copy(  # pylint: disable=too-many-arguments
        self,
        src_path: str,
        dst_path: str | Path = ".",
        data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Wrapper around run_copy to track modifications.

        Args:
            src_path (str): Path to the copier template.
            dst_path (Path): Target directory for the copy operation.
            data (dict): Data to pass to the copier template.
            **kwargs: Additional keyword arguments to pass to run_copy.
        """
        destination = Path(dst_path)
        # Get a list of files before the copy operation
        tracking_refs = destination.rglob("*")

        # Convert all members to Path objects lazily
        # store original contents
        original_contents: Dict[Path, Optional[str]] = {}
        for file in tracking_refs:
            if self._is_file_valid(file):
                # save into dict as generator is exhausted after one iteration
                original_contents[file] = None
                # Track original contents
                original_contents[file] = file.read_text(encoding="utf-8")

        # Run the copier operation
        run_copy(src_path, dst_path, data=data, **kwargs)

        # Track changes after the copier operation
        tracked_files = destination.rglob("*")

        # Track modified files
        for file in tracked_files:
            if self._is_file_valid(file):
                if original_contents.get(file, None) is not None:
                    # File existed before, track modification
                    # no content update needed as file is already modified
                    self._track_file_modification(file, old_content=original_contents[file], processed=True)
                else:
                    self._track_file_creation(file, file.read_text(encoding="utf-8"), processed=True)

    # PUBLIC METHODS FOR TRACKING OPERATIONS

    def create_modify_file(self, file_path: Union[str, Path], new_content: str, processed: bool = False) -> None:
        """
        Public method to track file modification or creation.

        Args:
            file_path: Path to the created/modified file (absolute or relative)
            new_content: New content of the created/modified file
            processed (bool): Whether the delta has already been processed. Defaults to False.
        """
        if not Path(file_path).is_file():
            self._track_file_creation(file_path, new_content, processed=processed)
        else:
            self._track_file_modification(file_path, new_content=new_content, processed=processed)

    def delete_file(self, file_path: Union[str, Path], processed: bool = False) -> None:
        """
        Public method to track file deletion.

        Args:
            file_path: Path to the deleted file
            processed (bool): Whether the delta has already been processed. Defaults to False.
        """
        self.deltas.append(
            delete_file_delta(str(file_path), Path(file_path).read_text(encoding="utf-8"), processed=processed)
        )

    def create_file_symlink(
        self,
        target_path: Union[str, Path],
        symlink_target: Union[str, Path],
        relative_to: Union[str, Path, None] = None,
        processed: bool = False,
    ) -> None:
        """
        Public method to track symlink creation.

        Args:
            target_path: Path to the symlink (absolute or relative)
            symlink_target: Target of the symlink
            relative_to: Base path for relative symlink creation, or None for absolute
            processed (bool): Whether the delta has already been processed. Defaults to False.
        """
        self.deltas.append(
            create_file_symlink_delta(
                str(target_path), str(symlink_target), str(relative_to) if relative_to else None, processed=processed
            )
        )

    def delete_file_symlink(
        self, target_path: Union[str, Path], symlink_target: Union[str, Path], processed: bool = False
    ) -> None:
        """
        Public method to track deletion of a symlink.

        Args:
            target_path: Path to the symlink (absolute or relative)
            symlink_target: Target of the symlink
            processed (bool): Whether the delta has already been processed. Defaults to False.

        Raises:
            FileNotFoundError: If the symlink does not exist.
        """
        self.deltas.append(delete_file_symlink_delta(str(target_path), str(symlink_target), processed=processed))

    def create_dir(self, dir_path: Union[str, Path], processed: bool = False) -> None:
        """
        Track creation of a new directory.

        Args:
            dir_path: Path to the created directory (absolute or relative)
            processed (bool): Whether the delta has already been processed. Defaults to False.
        """
        self.deltas.append(create_dir_delta(str(dir_path), processed=processed))

    def delete_dir(self, dir_path: Union[str, Path], processed: bool = False) -> None:
        """
        Public method to track directory deletion.

        Args:
            dir_path: Path to the deleted directory
            processed (bool): Whether the delta has already been processed. Defaults to False.
        """
        self.deltas.append(delete_dir_delta(str(dir_path), processed=processed))

    def create_dir_symlink(
        self,
        target_path: Union[str, Path],
        symlink_target: Union[str, Path],
        relative_to: Union[str, Path, None] = None,
        processed: bool = False,
    ) -> None:
        """
        Public method to track symlink creation.

        Args:
            target_path: Path to the symlink (absolute or relative)
            symlink_target: Target of the symlink
            relative_to: Base path for relative symlink creation, or None for absolute
            processed (bool): Whether the delta has already been processed. Defaults to False.
        """
        self.deltas.append(
            create_dir_symlink_delta(
                str(target_path), str(symlink_target), str(relative_to) if relative_to else None, processed=processed
            )
        )

    def delete_dir_symlink(
        self, target_path: Union[str, Path], symlink_target: Union[str, Path], processed: bool = False
    ) -> None:
        """
        Public method to track deletion of a symlink.

        Args:
            target_path: Path to the symlink (absolute or relative)
            symlink_target: Target of the symlink
            processed (bool): Whether the delta has already been processed. Defaults to False.

        Raises:
            FileNotFoundError: If the symlink does not exist.
        """
        self.deltas.append(delete_dir_symlink_delta(str(target_path), str(symlink_target), processed=processed))

    # PROTECTED Tracking methods for direct control
    def _track_file_creation(self, file_path: Union[str, Path], content: str, processed: bool = False) -> None:
        """
        Track creation of a new file.

        Args:
            file_path: Path to the created file (absolute or relative)
            content: Content of the created file
            processed: Whether the delta has already been processed. Defaults to False.
        """
        self.deltas.append(create_file_delta(str(file_path), content, processed=processed))

    def _track_file_modification(
        self,
        file_path: Union[str, Path],
        *,
        old_content: Optional[str] = None,
        new_content: Optional[str] = None,
        processed: bool = False,
    ) -> None:
        """
        Track modification of an existing file.

        Args:
            file_path: Path to the modified file
            new_content: New file content
            processed: Whether the delta has already been processed. Defaults to False.
        """
        file_as_path = Path(file_path)
        if old_content is None:
            old_content = file_as_path.read_text(encoding="utf-8")
        if new_content is None:
            new_content = file_as_path.read_text(encoding="utf-8")
        if new_content != old_content:
            self.deltas.append(modify_file_delta(str(file_path), old_content, new_content, processed=processed))

    def _is_file_valid(self, file_path: Union[str, Path]) -> bool:
        """
        Check if the given path is a valid file.

        Args:
            file_path: Path to the file to check
        Returns:
            bool: True if the path is a valid file, False otherwise.
        """
        path = Path(file_path)
        invalid_parent = (path.parent is not None) and (path.parent.name == "__pycache__")
        return path.is_file() and not invalid_parent


@contextmanager
def tracking_context(description: str) -> Generator[TrailSheriff, Any, None]:
    """
    Context manager for tracking file operations for undo/redo.

    Usage:
        with tracking_context("Generate module interface") as tracker:
            # Perform file operations
            content = generate_interface_content(...)
            Path("MyInterface.json").write_text(content)
            tracker.track_file_create("MyInterface.json", content)

    Args:
        description (str): Human-readable description of the operation.

    Yields:
        TrailSheriff: Tracker object for managing undo/redo operations.
    """
    tracker = TrailSheriff(description)

    try:
        yield tracker
    finally:
        tracker.finalize()


def activate_tracking(description: str, project_dir_param: str = "project_dir") -> Callable[..., Callable[..., Any]]:
    """
    Decorator that automatically tracks file operations in CLI commands.

    Args:
        description: Description of the command for undo history
        project_dir_param: Name of the parameter containing project directory

    Usage:
        @activate_tracking("Generate module interface", "project_root")
        def generate_interface(name: str, namespace: str, project_root: Path, **kwargs):
            # Function automatically gets undo tracking
            pass
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args, **kwargs):  # type:ignore[no-untyped-def]
            # Extract project directory from parameters

            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            project_dir = bound_args.arguments.get(project_dir_param)
            if project_dir is None:
                # Try to find project_dir in args by position
                param_names = list(sig.parameters.keys())
                if project_dir_param in param_names:
                    param_index = param_names.index(project_dir_param)
                    if param_index < len(args):
                        project_dir = args[param_index]

            if project_dir is None:
                # No project directory found, execute without tracking
                return func(*args, **kwargs)

            # Execute with undo tracking
            with tracking_context(description) as tracker:
                # Add tracker to kwargs for functions that want to use it
                kwargs["tracker"] = tracker
                return func(*args, **kwargs)

        return wrapper

    return decorator
