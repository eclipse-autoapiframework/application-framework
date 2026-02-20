# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Delta Model Module

This module defines the core data models for the stateless undo/redo system.
It includes the DeltaType enum, FileDelta class, OperationGroup class, and
StateHistory class, which collectively represent the delta-based data model.
"""

import time
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator
from typing_extensions import Self

from .data_handlers.dir_handlers import DirCreateHandler, DirDeleteHandler
from .data_handlers.file_handlers import FileCreateHandler, FileDeleteHandler, FileModifyHandler, FileMoveHandler
from .data_handlers.symlink_handlers import (
    SymlinkDirCreateHandler,
    SymlinkDirDeleteHandler,
    SymlinkFileCreateHandler,
    SymlinkFileDeleteHandler,
)
from .protocols.protocols import FileDeltaInterface


class DeltaType(Enum):
    """Types of file system deltas with dedicated handler classes."""

    FILE_CREATE = FileCreateHandler
    FILE_MODIFY = FileModifyHandler
    FILE_DELETE = FileDeleteHandler
    FILE_MOVE = FileMoveHandler
    DIR_CREATE = DirCreateHandler
    DIR_DELETE = DirDeleteHandler
    SYMLINK_FILE_CREATE = SymlinkFileCreateHandler
    SYMLINK_FILE_DELETE = SymlinkFileDeleteHandler
    SYMLINK_DIR_CREATE = SymlinkDirCreateHandler
    SYMLINK_DIR_DELETE = SymlinkDirDeleteHandler

    def apply_forward(self, delta: FileDeltaInterface) -> None:
        """
        Delegate to the handler class static method to apply the delta forward.

        Args:
            delta (FileDeltaInterface): The delta to apply.
        """
        self.value.apply_forward(delta)

    def apply_reverse(self, delta: FileDeltaInterface) -> None:
        """
        Delegate to the handler class static method to apply the delta in reverse.

        Args:
            delta (FileDeltaInterface): The delta to apply.
        """
        self.value.apply_reverse(delta)

    def __str__(self) -> str:
        """Return string representation for serialization."""
        return self.name.lower()

    @classmethod
    def from_string(cls, name: str) -> Self:
        """
        Create DeltaType from string representation.

        Args:
            name (str): The string representation of the DeltaType.

        Returns:
            DeltaType: The corresponding DeltaType enum value.
        """
        return cls[name.upper()]


class FileDelta(BaseModel):
    """
    Represents a single file system change that can be undone.

    This stores only the minimal information needed to reverse a change,
    without keeping full file copies.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        use_enum_values=False,  # Keep enum, not handler class
    )

    delta_type: DeltaType
    target_path: str = Field(..., description="Relative to project root")
    old_content: Optional[str] = Field(default=None, description="For modifications")
    new_content: Optional[str] = Field(default=None, description="For modifications")
    old_path: Optional[str] = Field(default=None, description="For moves")
    file_existed: bool = Field(default=False, description="For creates/deletes")
    timestamp: float = Field(default_factory=time.time)
    checksum: Optional[str] = Field(default=None, description="For integrity verification")
    symlink_target: Optional[str] = Field(default=None, description="Target path for symlinks")
    relative_to: Optional[str] = Field(default=None, description="Base directory for relative symlinks")
    processed: bool = Field(default=False, description="If delta is already processed e.g. via run_copy")

    @field_serializer("delta_type")
    def serialize_delta_type(self, value: DeltaType, field: Field) -> str:  # type:ignore[valid-type]  # pylint: disable=unused-argument
        """
        Serialize DeltaType to a lowercase string for JSON.

        Args:
            value (DeltaType): The DeltaType to serialize.
            field (Field): The field being serialized (unused).

        Returns:
            str: The serialized DeltaType as a lowercase string.
        """
        return value.name.lower()

    @field_validator("delta_type", mode="before")
    @classmethod
    def deserialize_delta_type(cls, value: str) -> DeltaType:
        """
        Deserialize DeltaType from a string.

        Args:
            value (str): The string representation of the DeltaType.

        Returns:
            DeltaType: The corresponding DeltaType enum value.

        Raises:
            ValueError: If the value is not a valid DeltaType.
        """
        if isinstance(value, DeltaType):
            return value
        if isinstance(value, str):
            try:
                return DeltaType[value.upper()]
            except KeyError as exc:
                raise ValueError(f"Invalid DeltaType: {value}") from exc
        raise ValueError(f"Invalid DeltaType type: {type(value)}")


class OperationGroup(BaseModel):
    """
    Groups related file deltas into atomic operations.

    This ensures that complex operations (like generating multiple files)
    can be undone/redone as a single unit.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, json_encoders={DeltaType: lambda v: v.name.lower()})

    operation_id: str
    description: str
    deltas: List[FileDelta]
    timestamp: float = Field(default_factory=time.time)
    completed: bool = Field(default=True)

    def get_summary(self) -> str:
        """Get a human-readable summary of this operation."""
        if len(self.deltas) == 1:
            delta = self.deltas[0]
            return f"{delta.delta_type.name.lower()}: {delta.target_path}"
        return f"{self.description} ({len(self.deltas)} files)"


class StateHistory(BaseModel):
    """
    Represents the undo/redo history state.

    This is stored in a JSON file within the project to maintain statelessness.
    """

    current_position: int = 0
    operations: Dict[int, OperationGroup] = Field(default_factory=dict)
    last_updated: float = Field(default_factory=time.time)
    total_operations: int = Field(default=0)
    can_undo: bool = Field(default=False)
    can_redo: bool = Field(default=False)
