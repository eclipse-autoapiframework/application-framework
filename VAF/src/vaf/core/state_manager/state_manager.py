# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
State Manager Module

This module provides the main orchestrator for the stateless undo/redo system.
It includes the StatusQuoOrdinator class, which manages file system deltas
and maintains a lightweight metadata-based history.
"""

import json
import warnings
from itertools import islice
from pathlib import Path
from typing import Any, Dict, Tuple

from vaf.core.state_manager.data_model import OperationGroup, StateHistory
from vaf.core.state_manager.protocols import FileDeltaInterface


class StatusQuoOrdinator:
    """
    Stateless undo/redo manager that operates purely on file system deltas.

    This manager:
    - Stores no state between CLI commands
    - Reconstructs its state from metadata on each operation
    - Applies deltas directly to the file system
    - Maintains minimal, lightweight metadata
    """

    def __init__(self, project_dir: Path) -> None:
        """
        Initialize the stateless undo manager.

        Args:
            project_dir: VAF project root directory
        """
        self.project_dir = project_dir.resolve()
        self.metadata_dir = self.project_dir / ".quoordinator"
        self.metadata_file = self.metadata_dir / "deltas.json"

        # Ensure metadata directory exists
        self.metadata_dir.mkdir(exist_ok=True)

    def record_operation(self, operation: OperationGroup, append_position: bool = True) -> None:
        """
        Record a new operation for future undo/redo.

        Args:
            operation: The operation group to record
            append_position: If True, append as a new operation; if False, overwrite the last operation
        """
        # Load existing history
        history = self._load_history()

        # if there are operations for redo recorded, but user changes something
        # then we need to ensure that the redo history (old path) is deleted
        # and we build a new path
        if len(history.operations) > history.current_position + 1:
            history.operations = dict(islice(history.operations.items(), history.current_position))

        if append_position:
            # Add new operation
            history.operations[history.current_position] = operation
            # Update position
            history.current_position += 1
        else:
            history.operations[history.current_position - 1] = operation

        # Apply history limit (keep last 50 operations)
        max_history = 7
        if len(history.operations) > max_history:
            history.operations = dict(islice(history.operations.items(), max_history))
        history.total_operations = len(history.operations)

        try:
            # process the deltas
            self._apply_forward_deltas(operation)

            history.can_undo = history.current_position > 0
            self._save_history(history)
        except PermissionError as e:
            print(f"Failed to record operation due to permission error: {e}")

    def undo(self, steps: int = 1) -> Tuple[bool, str]:
        """
        Undo the specified number of operations.

        Args:
            steps: Number of operations to undo

        Returns:
            (success, message) tuple
        """
        history = self._load_history()

        if history.current_position == 0:
            return False, "Nothing to undo"

        # Calculate how many operations we can actually undo
        actual_steps = min(steps, history.current_position)
        success_count = 0

        try:
            # Undo operations in reverse order
            for i in range(actual_steps):
                operation_index = history.current_position - 1 - i
                operation = history.operations[operation_index]

                # Apply reverse deltas
                self._apply_reverse_deltas(operation)
                success_count += 1

            # Update position
            history.current_position -= success_count
            self._save_history(history)

            return True, f"Successfully undid {success_count} operation(s)"

        except (IOError, ValueError, KeyError) as e:
            return False, f"Undo failed after {success_count} operations: {str(e)}"

    def redo(self, steps: int = 1) -> Tuple[bool, str]:
        """
        Redo the specified number of operations.

        Args:
            steps: Number of operations to redo

        Returns:
            (success, message) tuple
        """
        history = self._load_history()

        available_redos = history.total_operations - history.current_position
        if available_redos == 0:
            return False, "Nothing to redo"

        # Calculate how many operations we can actually redo
        actual_steps = min(steps, available_redos)
        success_count = 0

        try:
            # Redo operations in forward order
            for i in range(actual_steps):
                operation_index = (
                    history.current_position + i
                )  # if current_position = x, then do operation belongs to x to go to x+1
                operation = history.operations[operation_index]

                # Apply forward deltas
                self._apply_forward_deltas(operation)
                success_count += 1

            # Update position
            history.current_position += success_count
            self._save_history(history)

            return True, f"Successfully redid {success_count} operation(s)"

        except (IOError, ValueError, KeyError) as e:
            return False, f"Redo failed after {success_count} operations: {str(e)}"

    def get_history(self) -> Dict[str, Any]:
        """
        Get current undo/redo history information.

        Returns:
            Dictionary containing history state and operations
        """
        history = self._load_history()

        # Convert operations to summaries for display
        operation_summaries = []
        for i, op_data in history.operations.items():
            operation = OperationGroup.model_validate(op_data)
            summary = {
                "position": i + 1,
                "description": operation.get_summary(),
                "timestamp": operation.timestamp,
                "completed": operation.completed,
                "is_current": i == (history.current_position - 1),
            }
            operation_summaries.append(summary)

        return {
            "current_position": history.current_position,
            "total_operations": len(history.operations),
            "can_undo": history.current_position > 0,
            "can_redo": history.current_position < len(history.operations),
            "operations": operation_summaries,
        }

    def clear_history(self) -> bool:
        """
        Clear all undo/redo history.

        Returns:
            True if successful
        """
        try:
            self._save_history(StateHistory())
            return True
        except (FileNotFoundError, PermissionError, OSError, AttributeError, OverflowError, TypeError) as e:
            print(f"Failed to remove history due to {e}")
            return False

    def _apply_reverse_deltas(self, operation: OperationGroup) -> None:
        """Apply deltas in reverse to undo an operation."""
        # Process deltas in reverse order
        for delta_data in reversed(operation.deltas):
            self._apply_reverse_delta(delta_data)

    def _apply_forward_deltas(self, operation: OperationGroup) -> None:
        """Apply deltas forward to redo an operation."""
        # Process deltas in forward order
        for delta_data in operation.deltas:
            self._apply_forward_delta(delta_data)

    def _apply_reverse_delta(self, delta: FileDeltaInterface) -> None:
        """Apply a single delta in reverse by delegating to the handler."""
        delta.delta_type.apply_reverse(delta)
        delta.processed = False

    def _apply_forward_delta(self, delta: FileDeltaInterface) -> None:
        """Apply a single delta forward by delegating to the handler."""
        if not delta.processed:
            delta.delta_type.apply_forward(delta)
            delta.processed = True

    def _load_history(self) -> StateHistory:
        """Load history from metadata file."""
        default_value = StateHistory()

        if not self.metadata_file.is_file():
            return default_value

        try:
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return StateHistory.model_validate(data)
        except (FileNotFoundError, PermissionError, OSError, AttributeError, TypeError, json.JSONDecodeError) as e:
            # If loading fails, return empty history
            warnings.warn(f"Failed to load corrupted history due to {e}, returning empty history.")
            return default_value

    def _save_history(self, history: StateHistory) -> None:
        """Save history to metadata file.

        Args:
            history (StateHistory): The state history to save.

        """
        try:
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                f.write(history.model_dump_json(indent=2))
        except (FileNotFoundError, PermissionError, OSError, AttributeError, OverflowError, TypeError) as e:
            raise e
