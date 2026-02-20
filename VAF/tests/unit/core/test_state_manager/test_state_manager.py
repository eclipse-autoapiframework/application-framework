# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for the state manager StatusQuoOrdinator class.

This module tests the main state manager functionality including
operation recording, undo/redo operations, and history management.
"""
# mypy: disable-error-code="no-untyped-def"

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from vaf.core.state_manager.data_model import DeltaType, FileDelta, OperationGroup, StateHistory
from vaf.core.state_manager.state_manager import StatusQuoOrdinator


class TestStatusQuoOrdinatorInit:
    """Test suite for StatusQuoOrdinator initialization."""

    def test_init_creates_metadata_directory(self):
        """Test that initialization creates metadata directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            manager = StatusQuoOrdinator(project_dir)
            test_quoordinator = StatusQuoOrdinator(Path())

            assert manager.project_dir == project_dir.resolve()
            assert manager.metadata_dir == project_dir / test_quoordinator.metadata_dir.name
            assert manager.metadata_file == project_dir / test_quoordinator.metadata_dir.name / "deltas.json"
            assert manager.metadata_dir.exists()

    def test_init_with_existing_metadata_directory(self):
        """Test initialization when metadata directory already exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir)
            metadata_dir = project_dir / StatusQuoOrdinator(Path()).metadata_dir.name
            metadata_dir.mkdir()

            manager = StatusQuoOrdinator(project_dir)

            assert manager.metadata_dir.exists()
            assert manager.metadata_dir == metadata_dir

    def test_init_resolves_relative_paths(self):
        """Test that initialization resolves relative paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_dir = Path(temp_dir) / "subdir" / ".." / "project"
            project_dir.mkdir(parents=True)

            manager = StatusQuoOrdinator(project_dir)

            assert manager.project_dir.is_absolute()
            assert manager.project_dir == project_dir.resolve()


class TestStatusQuoOrdinatorRecordOperation:
    """Test suite for operation recording functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_dir = Path(self.temp_dir)
        self.manager = StatusQuoOrdinator(self.project_dir)

        # Create test operation
        self.test_delta = FileDelta(
            delta_type=DeltaType.FILE_CREATE, target_path="test.txt", new_content="test content"
        )
        self.test_operation = OperationGroup(
            operation_id="test-op-123", description="Test operation", deltas=[self.test_delta], timestamp=1234567890.0
        )

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_record_operation_creates_new_history(self, tmp_path, monkeypatch):
        """Test recording operation when no history exists."""
        monkeypatch.chdir(tmp_path)
        self.manager.record_operation(self.test_operation)

        assert self.manager.metadata_file.exists()

        # Read and verify the created history
        with open(self.manager.metadata_file, "r") as f:
            data = json.load(f)

        history = StateHistory.model_validate(data)
        assert history.current_position == 1
        assert history.total_operations == 1
        assert history.can_undo is True
        assert history.can_redo is False
        assert len(history.operations) == 1

    def test_record_operation_appends_to_existing_history(self, tmp_path, monkeypatch):
        """Test recording operation when history already exists."""
        monkeypatch.chdir(tmp_path)
        # Create initial history
        initial_operation = OperationGroup(
            operation_id="initial-op", description="Initial operation", deltas=[self.test_delta], timestamp=1234567800.0
        )
        self.manager.record_operation(initial_operation)

        # Record second operation
        self.manager.record_operation(self.test_operation)

        # Verify both operations are recorded
        with open(self.manager.metadata_file, "r") as f:
            data = json.load(f)

        history = StateHistory.model_validate(data)
        assert history.current_position == 2
        assert history.total_operations == 2
        assert len(history.operations) == 2

    def test_record_operation_truncates_redo_history(self, tmp_path, monkeypatch):
        """Test that recording new operation truncates any redo history."""
        monkeypatch.chdir(tmp_path)
        # Create operations 1, 2, 3
        ops = []
        for i in range(3):
            op = OperationGroup(
                operation_id=f"op-{i + 1}",
                description=f"Operation {i + 1}",
                deltas=[self.test_delta],
                timestamp=1234567800.0 + i,
            )
            ops.append(op)
            self.manager.record_operation(op)

        # Undo once (should be at position 2)
        self.manager.undo(1)

        # Record new operation (should truncate operation 3 and add new one)
        new_operation = OperationGroup(
            operation_id="new-op", description="New operation", deltas=[self.test_delta], timestamp=1234567900.0
        )
        self.manager.record_operation(new_operation)

        # Verify history
        with open(self.manager.metadata_file, "r") as f:
            data = json.load(f)

        history = StateHistory.model_validate(data)
        assert history.current_position == 3
        assert history.total_operations == 3
        assert history.can_redo is False


class TestStatusQuoOrdinatorUndo:
    """Test suite for undo functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_dir = Path(self.temp_dir)
        self.manager = StatusQuoOrdinator(self.project_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_undo_no_history(self):
        """Test undo when no history exists."""
        success, message = self.manager.undo(1)

        assert success is False
        assert "Nothing to undo" in message

    def test_undo_no_operations_to_undo(self, tmp_path, monkeypatch):
        """Test undo when at beginning of history."""
        monkeypatch.chdir(tmp_path)
        # Create history but undo everything
        delta = FileDelta(delta_type=DeltaType.FILE_CREATE, new_content="Wuluwulu", target_path="test.txt")
        operation = OperationGroup(operation_id="test-op", description="Test", deltas=[delta], timestamp=1234567890.0)
        self.manager.record_operation(operation)

        # Undo once
        self.manager.undo(1)

        # Try to undo again
        success, message = self.manager.undo(1)

        assert success is False
        assert "Nothing to undo" in message

    @patch("vaf.core.state_manager.state_manager.StatusQuoOrdinator._load_history")
    def test_undo_single_operation(self, mock_load, tmp_path, monkeypatch):
        """Test undoing a single operation."""
        monkeypatch.chdir(tmp_path)
        # Mock history with one operation
        delta = FileDelta(delta_type=DeltaType.FILE_CREATE, new_content="Wuluwulu", target_path="test.txt")
        operation = OperationGroup(
            operation_id="test-op", description="Create file", deltas=[delta], timestamp=1234567890.0
        )
        history = StateHistory(
            current_position=1, operations={0: operation}, total_operations=1, can_undo=True, can_redo=False
        )
        mock_load.return_value = history

        with patch.object(delta.delta_type, "apply_reverse") as mock_apply:
            success, message = self.manager.undo(1)

            assert success is True
            assert "Successfully undid 1 operation" in message
            mock_apply.assert_called_once_with(delta)

    @patch("vaf.core.state_manager.state_manager.StatusQuoOrdinator._load_history")
    def test_undo_multiple_steps(self, mock_load, tmp_path, monkeypatch):
        """Test undoing multiple operations."""
        monkeypatch.chdir(tmp_path)
        # Mock history with three operations
        operations = {}
        for i in range(0, 3):
            delta = FileDelta(delta_type=DeltaType.FILE_CREATE, new_content=f"Wuluwulu {i}", target_path=f"test{i}.txt")
            operation = OperationGroup(
                operation_id=f"test-op-{i}", description=f"Create file {i}", deltas=[delta], timestamp=1234567890.0 + i
            )
            operations[i] = operation

        history = StateHistory(
            current_position=2, operations=operations, total_operations=3, can_undo=True, can_redo=False
        )
        mock_load.return_value = history

        with patch.object(DeltaType.FILE_CREATE, "apply_reverse") as mock_apply:
            success, message = self.manager.undo(2)

            assert success is True
            assert "Successfully undid 2 operation" in message
            assert mock_apply.call_count == 2

    @patch("vaf.core.state_manager.state_manager.StatusQuoOrdinator._load_history")
    def test_undo_more_than_available(self, mock_load, tmp_path, monkeypatch):
        """Test undoing more operations than available."""
        monkeypatch.chdir(tmp_path)
        delta = FileDelta(delta_type=DeltaType.FILE_CREATE, new_content="Wuluwulu", target_path="test.txt")
        operation = OperationGroup(
            operation_id="test-op", description="Create file", deltas=[delta], timestamp=1234567890.0
        )
        history = StateHistory(
            current_position=1, operations={0: operation}, total_operations=1, can_undo=True, can_redo=False
        )
        mock_load.return_value = history

        with patch.object(delta.delta_type, "apply_reverse"):
            success, message = self.manager.undo(5)

            assert success is True
            assert "Successfully undid 1 operation" in message


class TestStatusQuoOrdinatorRedo:
    """Test suite for redo functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_dir = Path(self.temp_dir)
        self.manager = StatusQuoOrdinator(self.project_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_redo_no_history(self):
        """Test redo when no history exists."""
        success, message = self.manager.redo(1)

        assert success is False
        assert "Nothing to redo" in message

    @patch("vaf.core.state_manager.state_manager.StatusQuoOrdinator._load_history")
    def test_redo_no_operations_to_redo(self, mock_load):
        """Test redo when at end of history."""
        delta = FileDelta(delta_type=DeltaType.FILE_CREATE, target_path="test.txt")
        operation = OperationGroup(operation_id="test-op", description="Test", deltas=[delta], timestamp=1234567890.0)
        history = StateHistory(
            current_position=1, operations={1: operation}, total_operations=1, can_undo=True, can_redo=False
        )
        mock_load.return_value = history

        success, message = self.manager.redo(1)

        assert success is False
        assert "Nothing to redo" in message

    @patch("vaf.core.state_manager.state_manager.StatusQuoOrdinator._load_history")
    def test_redo_single_operation(self, mock_load, tmp_path, monkeypatch):
        """Test redoing a single operation."""
        monkeypatch.chdir(tmp_path)
        delta = FileDelta(delta_type=DeltaType.FILE_CREATE, target_path="test.txt")
        operation = OperationGroup(
            operation_id="test-op", description="Create file", deltas=[delta], timestamp=1234567890.0
        )
        # History after undo (can redo)
        history = StateHistory(
            current_position=0, operations={0: operation}, total_operations=1, can_undo=False, can_redo=True
        )
        mock_load.return_value = history

        with patch.object(delta.delta_type, "apply_forward") as mock_apply:
            success, message = self.manager.redo(1)

            assert success is True
            assert "Successfully redid 1 operation" in message
            mock_apply.assert_called_once_with(delta)


class TestStatusQuoOrdinatorHistory:
    """Test suite for history management functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_dir = Path(self.temp_dir)
        self.manager = StatusQuoOrdinator(self.project_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_get_history_no_file(self):
        """Test get_history when no history file exists."""
        history_info = self.manager.get_history()

        expected = {
            "current_position": 0,
            "total_operations": 0,
            "can_undo": False,
            "can_redo": False,
            "operations": [],
        }

        assert history_info == expected

    def test_get_history_with_operations(self, tmp_path, monkeypatch):
        """Test get_history with existing operations."""
        monkeypatch.chdir(tmp_path)
        # Create test operations
        operations = []
        for i in range(3):
            delta = FileDelta(
                delta_type=DeltaType.FILE_CREATE, new_content=f"Content for test{i}.txt", target_path=f"test{i}.txt"
            )
            operation = OperationGroup(
                operation_id=f"op-{i + 1}", description=f"Operation {i + 1}", deltas=[delta], timestamp=1234567890.0 + i
            )
            operations.append(operation)
            self.manager.record_operation(operation)

        history_info = self.manager.get_history()

        assert history_info["current_position"] == 3
        assert history_info["total_operations"] == 3
        assert history_info["can_undo"] is True
        assert history_info["can_redo"] is False
        assert len(history_info["operations"]) == 3

        # Check operation details
        op_info = history_info["operations"][0]
        assert op_info["position"] == 1
        assert operations[0].description == "Operation 1"
        # from get summary
        assert op_info["description"] == "file_create: test0.txt"
        assert op_info["is_current"] is False

    def test_clear_history_no_file(self):
        """Test clear_history when no history file exists."""
        success = self.manager.clear_history()
        assert success is True

    def test_clear_history_with_file(self, tmp_path, monkeypatch):
        """Test clear_history when history file exists."""
        monkeypatch.chdir(tmp_path)
        # Create some history
        delta = FileDelta(delta_type=DeltaType.FILE_CREATE, new_content="test content", target_path="test.txt")
        operation = OperationGroup(operation_id="test-op", description="Test", deltas=[delta], timestamp=1234567890.0)
        self.manager.record_operation(operation)

        # Clear history
        success = self.manager.clear_history()
        assert success is True
        history = self.manager._load_history()
        assert history.current_position == 0
        assert history.total_operations == 0
        assert not history.operations
        assert not history.can_redo
        assert not history.can_undo


class TestStatusQuoOrdinatorPrivateMethods:
    """Test suite for private helper methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_dir = Path(self.temp_dir)
        self.manager = StatusQuoOrdinator(self.project_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_load_history_no_file(self):
        """Test _load_history when no file exists."""
        history = self.manager._load_history()

        assert isinstance(history, StateHistory)
        assert history.current_position == 0
        assert history.total_operations == 0
        assert history.operations == {}

    def test_load_history_invalid_json(self):
        """Test _load_history with invalid JSON."""
        # Create invalid JSON file
        with open(self.manager.metadata_file, "w") as f:
            f.write("invalid json content")

        history = self.manager._load_history()

        # Should return default history
        assert isinstance(history, StateHistory)
        assert history.current_position == 0

    def test_save_history(self, tmp_path, monkeypatch):
        """Test _save_history functionality."""
        monkeypatch.chdir(tmp_path)
        # Create a sample history
        delta = FileDelta(delta_type=DeltaType.FILE_CREATE, new_content="test content", target_path="test.txt")
        operation = OperationGroup(operation_id="test-op", description="Test", deltas=[delta], timestamp=1234567890.0)
        history = StateHistory(current_position=1, operations={1: operation}, total_operations=1, can_undo=True)

        self.manager._save_history(history)

        assert self.manager.metadata_file.exists()

        # Verify saved content
        with open(self.manager.metadata_file, "r") as f:
            data = json.load(f)

        loaded_history = StateHistory.model_validate(data)
        assert loaded_history.current_position == 1
        assert loaded_history.total_operations == 1


class TestStatusQuoOrdinatorErrorHandling:
    """Test suite for error handling scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_dir = Path(self.temp_dir)
        self.manager = StatusQuoOrdinator(self.project_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_record_operation_permission_error(self, tmp_path, monkeypatch):
        """Test record_operation with permission error."""
        monkeypatch.chdir(tmp_path)
        delta = FileDelta(delta_type=DeltaType.FILE_CREATE, new_content="test content", target_path="test.txt")
        operation = OperationGroup(operation_id="test-op", description="Test", deltas=[delta], timestamp=1234567890.0)

        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            # Should not raise exception
            self.manager.record_operation(operation)

    def test_undo_with_delta_application_error(self):
        """Test undo when delta application fails."""
        delta = FileDelta(delta_type=DeltaType.FILE_CREATE, target_path="test.txt")
        operation = OperationGroup(operation_id="test-op", description="Test", deltas=[delta], timestamp=1234567890.0)

        history = StateHistory(current_position=1, operations={1: operation}, total_operations=1, can_undo=True)

        with patch.object(self.manager, "_load_history", return_value=history):
            with patch.object(delta.delta_type, "apply_reverse", side_effect=Exception("Apply failed")):
                success, message = self.manager.undo(1)

                # Should handle error gracefully
                assert success is False
                assert "Undo failed after" in message

    def test_redo_with_delta_application_error(self):
        """Test redo when delta application fails."""
        delta = FileDelta(delta_type=DeltaType.FILE_CREATE, target_path="test.txt")
        operation = OperationGroup(operation_id="test-op", description="Test", deltas=[delta], timestamp=1234567890.0)

        history = StateHistory(current_position=0, operations={1: operation}, total_operations=1, can_undo=True)

        with patch.object(self.manager, "_load_history", return_value=history):
            with patch.object(delta.delta_type, "apply_reverse", side_effect=Exception("Apply failed")):
                success, message = self.manager.redo(1)

                # Should handle error gracefully
                assert success is False
                assert "Redo failed after" in message
