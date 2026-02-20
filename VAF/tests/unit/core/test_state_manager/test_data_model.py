# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for the state manager data model module.

This module tests DeltaType, FileDelta, OperationGroup, and StateHistory classes.
"""
# mypy: disable-error-code="no-untyped-def"

import json
import time
from unittest.mock import MagicMock, patch

import pytest

from vaf.core.state_manager.data_model import DeltaType, FileDelta, OperationGroup, StateHistory


class TestDeltaType:
    """Test suite for DeltaType enum."""

    def test_enum_values_exist(self):
        """Test that all expected enum values exist."""
        expected_types = [
            "FILE_CREATE",
            "FILE_MODIFY",
            "FILE_DELETE",
            "FILE_MOVE",
            "DIR_CREATE",
            "DIR_DELETE",
            "SYMLINK_FILE_CREATE",
            "SYMLINK_FILE_DELETE",
            "SYMLINK_DIR_CREATE",
            "SYMLINK_DIR_DELETE",
        ]

        for type_name in expected_types:
            assert hasattr(DeltaType, type_name)
            assert isinstance(getattr(DeltaType, type_name), DeltaType)

    def test_apply_forward_delegates_to_handler(self):
        """Test that apply_forward delegates to handler class."""
        mock_delta = MagicMock()
        mock_handler = MagicMock()

        with patch.object(DeltaType.FILE_CREATE, "apply_forward", mock_handler):
            DeltaType.FILE_CREATE.apply_forward(mock_delta)
            mock_handler.assert_called_once_with(mock_delta)

    def test_apply_reverse_delegates_to_handler(self):
        """Test that apply_reverse delegates to handler class."""
        mock_delta = MagicMock()
        mock_handler = MagicMock()

        with patch.object(DeltaType.FILE_CREATE, "apply_reverse", mock_handler):
            DeltaType.FILE_CREATE.apply_reverse(mock_delta)
            mock_handler.assert_called_once_with(mock_delta)

    def test_str_representation(self):
        """Test string representation for serialization."""
        assert str(DeltaType.FILE_CREATE) == "file_create"
        assert str(DeltaType.DIR_DELETE) == "dir_delete"
        assert str(DeltaType.SYMLINK_FILE_CREATE) == "symlink_file_create"

    def test_from_string_valid_names(self):
        """Test creating DeltaType from valid string representations."""
        assert DeltaType.from_string("file_create") == DeltaType.FILE_CREATE
        assert DeltaType.from_string("FILE_CREATE") == DeltaType.FILE_CREATE
        assert DeltaType.from_string("dir_delete") == DeltaType.DIR_DELETE

    def test_from_string_invalid_name(self):
        """Test creating DeltaType from invalid string raises KeyError."""
        with pytest.raises(KeyError):
            DeltaType.from_string("invalid_type")


class TestFileDelta:
    """Test suite for FileDelta model."""

    def test_minimal_file_delta_creation(self):
        """Test creating FileDelta with minimal required fields."""
        delta = FileDelta(delta_type=DeltaType.FILE_CREATE, target_path="test.txt")

        assert delta.delta_type == DeltaType.FILE_CREATE
        assert delta.target_path == "test.txt"
        assert delta.old_content is None
        assert delta.new_content is None
        assert delta.old_path is None
        assert delta.file_existed is False
        assert isinstance(delta.timestamp, float)
        assert delta.checksum is None
        assert delta.symlink_target is None
        assert delta.processed is False

    def test_complete_file_delta_creation(self):
        """Test creating FileDelta with all fields."""
        timestamp = time.time()
        delta = FileDelta(
            delta_type=DeltaType.FILE_MODIFY,
            target_path="test.txt",
            old_content="old content",
            new_content="new content",
            old_path="old_test.txt",
            file_existed=True,
            timestamp=timestamp,
            checksum="abc123",
            symlink_target="/path/to/target",
            processed=True,
        )

        assert delta.delta_type == DeltaType.FILE_MODIFY
        assert delta.target_path == "test.txt"
        assert delta.old_content == "old content"
        assert delta.new_content == "new content"
        assert delta.old_path == "old_test.txt"
        assert delta.file_existed is True
        assert delta.timestamp == timestamp
        assert delta.checksum == "abc123"
        assert delta.symlink_target == "/path/to/target"
        assert delta.processed is True

    def test_delta_type_serialization(self):
        """Test DeltaType serialization to JSON."""
        delta = FileDelta(delta_type=DeltaType.FILE_CREATE, target_path="test.txt")

        # Test direct serialization method
        serialized = delta.serialize_delta_type(DeltaType.FILE_CREATE, None)
        assert serialized == "file_create"

        # Test JSON serialization
        json_data = delta.model_dump_json()
        parsed = json.loads(json_data)
        assert parsed["delta_type"] == "file_create"

    def test_delta_type_deserialization(self):
        """Test DeltaType deserialization from JSON."""
        # Test string deserialization
        assert FileDelta.deserialize_delta_type("file_create") == DeltaType.FILE_CREATE
        assert FileDelta.deserialize_delta_type("FILE_CREATE") == DeltaType.FILE_CREATE

        # Test DeltaType passthrough
        assert FileDelta.deserialize_delta_type(DeltaType.FILE_CREATE.name.lower()) == DeltaType.FILE_CREATE

    def test_delta_type_deserialization_invalid(self):
        """Test DeltaType deserialization with invalid input."""
        with pytest.raises(ValueError, match="Invalid DeltaType: invalid_type"):
            FileDelta.deserialize_delta_type("invalid_type")

        with pytest.raises(ValueError, match="Invalid DeltaType"):
            FileDelta.deserialize_delta_type(str(123))

    def test_json_roundtrip(self):
        """Test complete JSON serialization and deserialization."""
        original = FileDelta(
            delta_type=DeltaType.FILE_MODIFY,
            target_path="test.txt",
            old_content="old",
            new_content="new",
            file_existed=True,
            processed=True,
        )

        # Serialize to JSON
        json_str = original.model_dump_json()

        # Deserialize from JSON
        reconstructed = FileDelta.model_validate_json(json_str)

        assert reconstructed.delta_type == original.delta_type
        assert reconstructed.target_path == original.target_path
        assert reconstructed.old_content == original.old_content
        assert reconstructed.new_content == original.new_content
        assert reconstructed.file_existed == original.file_existed
        assert reconstructed.processed == original.processed


class TestOperationGroup:
    """Test suite for OperationGroup model."""

    def test_operation_group_creation(self):
        """Test creating OperationGroup."""
        deltas = [
            FileDelta(delta_type=DeltaType.FILE_CREATE, target_path="file1.txt"),
            FileDelta(delta_type=DeltaType.FILE_CREATE, target_path="file2.txt"),
        ]

        timestamp = time.time()
        operation = OperationGroup(
            operation_id="test-123", description="Test operation", deltas=deltas, timestamp=timestamp, completed=True
        )

        assert operation.operation_id == "test-123"
        assert operation.description == "Test operation"
        assert len(operation.deltas) == 2
        assert operation.timestamp == timestamp
        assert operation.completed is True

    def test_operation_group_defaults(self):
        """Test OperationGroup default values."""
        operation = OperationGroup(
            operation_id="test-123", description="Test operation", deltas=[], timestamp=time.time()
        )

        assert operation.completed is True  # Default value

    def test_get_summary_single_delta(self):
        """Test get_summary with single delta."""
        delta = FileDelta(delta_type=DeltaType.FILE_CREATE, target_path="test.txt")
        operation = OperationGroup(
            operation_id="test-123", description="Create file", deltas=[delta], timestamp=time.time()
        )

        summary = operation.get_summary()
        assert summary == "file_create: test.txt"

    def test_get_summary_multiple_deltas(self):
        """Test get_summary with multiple deltas."""
        deltas = [
            FileDelta(delta_type=DeltaType.FILE_CREATE, target_path="file1.txt"),
            FileDelta(delta_type=DeltaType.FILE_CREATE, target_path="file2.txt"),
            FileDelta(delta_type=DeltaType.DIR_CREATE, target_path="dir1"),
        ]

        operation = OperationGroup(
            operation_id="test-123", description="Create project structure", deltas=deltas, timestamp=time.time()
        )

        summary = operation.get_summary()
        assert summary == "Create project structure (3 files)"

    def test_json_serialization(self):
        """Test OperationGroup JSON serialization."""
        delta = FileDelta(delta_type=DeltaType.FILE_CREATE, target_path="test.txt")
        operation = OperationGroup(
            operation_id="test-123", description="Test operation", deltas=[delta], timestamp=time.time()
        )

        json_str = operation.model_dump_json()
        reconstructed = OperationGroup.model_validate_json(json_str)

        assert reconstructed.operation_id == operation.operation_id
        assert reconstructed.description == operation.description
        assert len(reconstructed.deltas) == len(operation.deltas)
        assert reconstructed.timestamp == operation.timestamp


class TestStateHistory:
    """Test suite for StateHistory model."""

    def test_state_history_creation_defaults(self):
        """Test creating StateHistory with default values."""
        history = StateHistory()

        assert history.current_position == 0
        assert history.operations == {}
        assert isinstance(history.last_updated, float)
        assert history.total_operations == 0
        assert history.can_undo is False
        assert history.can_redo is False

    def test_state_history_creation_with_values(self):
        """Test creating StateHistory with explicit values."""
        operations = {
            1: OperationGroup(operation_id="op1", description="First operation", deltas=[], timestamp=time.time())
        }

        timestamp = time.time()
        history = StateHistory(
            current_position=1,
            operations=operations,
            last_updated=timestamp,
            total_operations=1,
            can_undo=True,
            can_redo=False,
        )

        assert history.current_position == 1
        assert len(history.operations) == 1
        assert history.last_updated == timestamp
        assert history.total_operations == 1
        assert history.can_undo is True
        assert history.can_redo is False

    def test_json_serialization(self):
        """Test StateHistory JSON serialization."""
        operation = OperationGroup(
            operation_id="test-123",
            description="Test operation",
            deltas=[FileDelta(delta_type=DeltaType.FILE_CREATE, target_path="test.txt")],
            timestamp=time.time(),
        )

        history = StateHistory(current_position=1, operations={1: operation}, total_operations=1, can_undo=True)

        json_str = history.model_dump_json()
        reconstructed = StateHistory.model_validate_json(json_str)

        assert reconstructed.current_position == history.current_position
        assert len(reconstructed.operations) == len(history.operations)
        assert reconstructed.total_operations == history.total_operations
        assert reconstructed.can_undo == history.can_undo

    def test_field_validation(self):
        """Test field validation constraints."""
        # Test that negative positions are allowed (for flexibility)
        history = StateHistory(current_position=-1)
        assert history.current_position == -1

        # Test that empty operations dict is valid
        history = StateHistory(operations={})
        assert history.operations == {}


class TestModelIntegration:
    """Integration tests for model interactions."""

    def test_complete_workflow_serialization(self):
        """Test complete workflow from delta creation to history serialization."""
        # Create deltas
        deltas = [
            FileDelta(
                delta_type=DeltaType.FILE_CREATE,
                target_path="src/main.py",
                new_content="print('Hello World')",
                file_existed=False,
            ),
            FileDelta(delta_type=DeltaType.DIR_CREATE, target_path="src", file_existed=False),
        ]

        # Create operation
        operation = OperationGroup(
            operation_id="create-project",
            description="Create initial project structure",
            deltas=deltas,
            timestamp=time.time(),
        )

        # Create history
        history = StateHistory(current_position=1, operations={1: operation}, total_operations=1, can_undo=True)

        # Test full serialization/deserialization
        json_str = history.model_dump_json()
        reconstructed = StateHistory.model_validate_json(json_str)

        # Verify structure is preserved
        assert len(reconstructed.operations) == 1
        assert 1 in reconstructed.operations

        # Get the operation (handle both string and int keys)
        reconstructed_op = reconstructed.operations[1]

        assert reconstructed_op.operation_id == "create-project"
        assert len(reconstructed_op.deltas) == 2
        assert reconstructed_op.deltas[0].delta_type == DeltaType.FILE_CREATE
        assert reconstructed_op.deltas[1].delta_type == DeltaType.DIR_CREATE

    def test_delta_type_enum_handler_integration(self):
        """Test that DeltaType enum properly integrates with handler classes."""
        delta = FileDelta(delta_type=DeltaType.FILE_CREATE, target_path="test.txt", new_content="content")

        # Test that the enum value has a handler
        assert hasattr(delta.delta_type.value, "apply_forward")
        assert hasattr(delta.delta_type.value, "apply_reverse")

        # Test that handler methods are callable
        assert callable(delta.delta_type.value.apply_forward)
        assert callable(delta.delta_type.value.apply_reverse)
