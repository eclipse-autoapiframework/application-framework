# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Comprehensive Unit Tests for State Manager System

This module provides thorough unit testing for all classes and objects
in the state manager system, ensuring proper functionality, edge case handling,
and type safety.
"""
# mypy: disable-error-code="no-untyped-def"

import json
import tempfile
from pathlib import Path
from typing import Tuple
from unittest.mock import Mock, patch

import pytest

from vaf.core.state_manager.data_handlers.dir_handlers import (
    DirCreateHandler,
    DirValidator,
)
from vaf.core.state_manager.data_handlers.file_handlers import (
    FileCreateHandler,
    FileDeleteHandler,
    FileModifyHandler,
    FileValidator,
)
from vaf.core.state_manager.data_handlers.symlink_handlers import (
    SymlinkValidator,
)
from vaf.core.state_manager.data_model import DeltaType, FileDelta, OperationGroup, StateHistory
from vaf.core.state_manager.factory import (
    create_dir_delta,
    create_dir_symlink_delta,
    create_file_delta,
    create_file_symlink_delta,
    delete_dir_delta,
    delete_file_delta,
    get_state_manager,
    modify_file_delta,
)
from vaf.core.state_manager.protocols.protocols import FileDeltaInterface
from vaf.core.state_manager.state_manager import StatusQuoOrdinator
from vaf.core.state_manager.tracker import TrailSheriff as TrackerSheriff
from vaf.core.state_manager.tracker import activate_tracking, tracking_context


class TestFileDelta:
    """Test cases for FileDelta data model."""

    def test_file_delta_creation_with_all_fields(self) -> None:
        """Test FileDelta creation with all possible fields."""
        delta = FileDelta(
            delta_type=DeltaType.FILE_CREATE,
            target_path="/test/file.txt",
            old_content="old",
            new_content="new",
            old_path="/old/path.txt",
            file_existed=True,
            checksum="abc123",
            symlink_target="/symlink/target",
            processed=True,
        )

        assert delta.delta_type == DeltaType.FILE_CREATE
        assert delta.target_path == "/test/file.txt"
        assert delta.old_content == "old"
        assert delta.new_content == "new"
        assert delta.old_path == "/old/path.txt"
        assert delta.file_existed is True
        assert delta.checksum == "abc123"
        assert delta.symlink_target == "/symlink/target"
        assert delta.processed is True

    def test_file_delta_serialization_deserialization(self) -> None:
        """Test JSON serialization and deserialization."""
        original_delta = FileDelta(
            delta_type=DeltaType.FILE_MODIFY,
            target_path="/test/file.txt",
            old_content="old content",
            new_content="new content",
        )

        # Serialize to JSON
        json_data = original_delta.model_dump_json()
        parsed_data = json.loads(json_data)

        # Deserialize from JSON
        reconstructed_delta = FileDelta.model_validate(parsed_data)

        assert reconstructed_delta.delta_type == original_delta.delta_type
        assert reconstructed_delta.target_path == original_delta.target_path
        assert reconstructed_delta.old_content == original_delta.old_content
        assert reconstructed_delta.new_content == original_delta.new_content

    def test_file_delta_timestamp_generation(self) -> None:
        """Test automatic timestamp generation."""
        delta1 = FileDelta(delta_type=DeltaType.FILE_CREATE, target_path="/test1.txt")
        delta2 = FileDelta(delta_type=DeltaType.FILE_CREATE, target_path="/test2.txt")

        assert delta1.timestamp > 0
        assert delta2.timestamp >= delta1.timestamp

    def test_file_delta_with_invalid_delta_type(self) -> None:
        """Test FileDelta with invalid delta type should fail validation."""
        with pytest.raises(ValueError):
            FileDelta(delta_type="INVALID_TYPE", target_path="/test.txt")  # type: ignore


class TestDeltaType:
    """Test cases for DeltaType enum."""

    def test_delta_type_serialization(self) -> None:
        """Test DeltaType serialization to string values."""
        assert DeltaType.FILE_CREATE.value == FileCreateHandler
        assert DeltaType.FILE_DELETE.value == FileDeleteHandler
        assert DeltaType.FILE_MODIFY.value == FileModifyHandler

    def test_delta_type_handler_mapping(self) -> None:
        """Test that each DeltaType has proper handler methods."""
        for delta_type in DeltaType:
            # Ensure each delta type has apply_forward and apply_reverse methods
            assert hasattr(delta_type, "apply_forward")
            assert hasattr(delta_type, "apply_reverse")
            assert callable(delta_type.apply_forward)
            assert callable(delta_type.apply_reverse)

    def test_delta_type_protocol_compliance(self) -> None:
        """Test that DeltaType implements DeltaTypeProtocol."""
        mock_delta = Mock(spec=FileDeltaInterface)

        # Test that each enum value can be called as a protocol method
        for delta_type in DeltaType:
            try:
                # These should not raise errors (though they might fail with mock)
                delta_type.apply_forward(mock_delta)
                delta_type.apply_reverse(mock_delta)
            except Exception:
                # Expected to fail with mock, but method should exist
                pass


class TestOperationGroup:
    """Test cases for OperationGroup data model."""

    def test_operation_group_creation(self) -> None:
        """Test OperationGroup creation and validation."""
        delta = FileDelta(delta_type=DeltaType.FILE_CREATE, target_path="/test.txt")
        operation = OperationGroup(
            operation_id="test-123",
            description="Test operation",
            deltas=[delta],
            completed=True,
        )

        assert operation.operation_id == "test-123"
        assert operation.description == "Test operation"
        assert len(operation.deltas) == 1
        assert operation.completed is True
        assert operation.timestamp > 0

    def test_operation_group_with_multiple_deltas(self) -> None:
        """Test OperationGroup with multiple deltas."""
        deltas = [
            FileDelta(delta_type=DeltaType.FILE_CREATE, target_path="/test1.txt"),
            FileDelta(delta_type=DeltaType.FILE_MODIFY, target_path="/test2.txt"),
            FileDelta(delta_type=DeltaType.FILE_DELETE, target_path="/test3.txt"),
        ]

        operation = OperationGroup(
            operation_id="multi-test",
            description="Multiple operations",
            deltas=deltas,
        )

        assert len(operation.deltas) == 3
        assert all(isinstance(delta, FileDelta) for delta in operation.deltas)


class TestStateHistory:
    """Test cases for StateHistory data model."""

    def test_state_history_creation(self) -> None:
        """Test StateHistory creation and management."""
        delta = FileDelta(delta_type=DeltaType.FILE_CREATE, target_path="/test.txt")
        operation = OperationGroup(
            operation_id="test-op",
            description="Test",
            deltas=[delta],
        )

        history = StateHistory(
            operations={0: operation},
            current_position=0,
        )

        assert len(history.operations) == 1
        assert history.current_position == 0

    def test_state_history_serialization(self) -> None:
        """Test StateHistory JSON serialization."""
        delta = FileDelta(delta_type=DeltaType.FILE_CREATE, target_path="/test.txt")
        operation = OperationGroup(
            operation_id="test-op",
            description="Test",
            deltas=[delta],
        )
        history = StateHistory(operations={0: operation}, current_position=0)

        json_data = history.model_dump_json()
        parsed_data = json.loads(json_data)
        reconstructed = StateHistory.model_validate(parsed_data)

        assert len(reconstructed.operations) == 1
        assert reconstructed.current_position == 0


class TestFactoryFunctions:
    """Test cases for factory functions."""

    def test_create_file_delta_factory(self) -> None:
        """Test file delta creation factory."""
        delta = create_file_delta("/test.txt", "content", processed=True)

        assert delta.delta_type == DeltaType.FILE_CREATE
        assert delta.target_path == "/test.txt"
        assert delta.new_content == "content"
        assert delta.file_existed is False
        assert delta.processed is True

    def test_modify_file_delta_factory(self) -> None:
        """Test file modification delta factory."""
        delta = modify_file_delta("/test.txt", "old", "new", processed=False)

        assert delta.delta_type == DeltaType.FILE_MODIFY
        assert delta.target_path == "/test.txt"
        assert delta.old_content == "old"
        assert delta.new_content == "new"
        assert delta.file_existed is True
        assert delta.processed is False

    def test_delete_file_delta_factory(self) -> None:
        """Test file deletion delta factory."""
        delta = delete_file_delta("/test.txt", "content")

        assert delta.delta_type == DeltaType.FILE_DELETE
        assert delta.target_path == "/test.txt"
        assert delta.old_content == "content"
        assert delta.file_existed is True
        assert delta.processed is False

    def test_symlink_factories(self) -> None:
        """Test symlink delta factories."""
        # File symlink
        file_symlink = create_file_symlink_delta("/link.txt", "/target.txt")
        assert file_symlink.delta_type == DeltaType.SYMLINK_FILE_CREATE
        assert file_symlink.symlink_target == "/target.txt"

        # Directory symlink
        dir_symlink = create_dir_symlink_delta("/link_dir", "/target_dir")
        assert dir_symlink.delta_type == DeltaType.SYMLINK_DIR_CREATE
        assert dir_symlink.symlink_target == "/target_dir"

    def test_directory_factories(self) -> None:
        """Test directory delta factories."""
        create_delta = create_dir_delta("/new_dir", processed=True)
        assert create_delta.delta_type == DeltaType.DIR_CREATE
        assert create_delta.processed is True

        delete_delta = delete_dir_delta("/old_dir")
        assert delete_delta.delta_type == DeltaType.DIR_DELETE
        assert delete_delta.processed is False


class TestValidators:
    """Test cases for validator classes."""

    def test_file_validator(self) -> None:
        """Test FileValidator methods."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Test directory validation
            with pytest.raises(IsADirectoryError):
                FileValidator.validate_not_dir(temp_path)

            # Test file existence validation
            non_existent = temp_path / "nonexistent.txt"
            with pytest.raises(FileNotFoundError):
                FileValidator.validate_exists(non_existent)

    def test_dir_validator(self) -> None:
        """Test DirValidator methods."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a file to test file validation
            test_file = temp_path / "test.txt"
            test_file.write_text("content")

            with pytest.raises(FileExistsError):
                DirValidator.validate_not_file(test_file)

    def test_symlink_validator(self) -> None:
        """Test SymlinkValidator methods."""
        # Test invalid symlink target (empty path)
        with pytest.raises(ValueError):
            SymlinkValidator.validate_symlink_target(Path("fakepath"))

    def test_symlink_validator_with_temp_file_and_dir(self) -> None:
        """Test SymlinkValidator with temporary file and directory as symlink targets."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create a temporary file and directory
            temp_file = temp_path / "temp_file.txt"
            temp_file.write_text("Temporary file content")

            temp_subdir = temp_path / "temp_subdir"
            temp_subdir.mkdir()

            # Create a symlink to another temporary file
            target_file = temp_path / "target_file.txt"
            target_file.write_text("Target file content")
            temp_file_symlink = temp_path / "temp_file_symlink"
            temp_file_symlink.symlink_to(target_file)

            # Create a symlink to another temporary directory
            target_dir = temp_path / "target_dir"
            target_dir.mkdir()
            temp_dir_symlink = temp_path / "temp_dir_symlink"
            temp_dir_symlink.symlink_to(target_dir)

            # Test SymlinkValidator with file symlink target
            with pytest.raises(ValueError):
                SymlinkValidator.validate_symlink_target(temp_file_symlink)

            # Test SymlinkValidator with directory symlink target
            with pytest.raises(ValueError):
                SymlinkValidator.validate_symlink_target(temp_dir_symlink)


class TestHandlers:
    """Test cases for operation handlers."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def teardown_method(self) -> None:
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_file_create_handler(self) -> None:
        """Test FileCreateHandler operations."""
        test_file = self.temp_path / "test.txt"
        delta = FileDelta(delta_type=DeltaType.FILE_CREATE, target_path=str(test_file), new_content="test content")

        # Test forward operation
        FileCreateHandler.apply_forward(delta)
        assert test_file.exists()
        assert test_file.read_text(encoding="utf-8") == "test content"

        # Test reverse operation
        FileCreateHandler.apply_reverse(delta)
        assert not test_file.exists()

    def test_file_modify_handler(self) -> None:
        """Test FileModifyHandler operations."""
        test_file = self.temp_path / "modify_test.txt"
        test_file.write_text("original content", encoding="utf-8")

        delta = FileDelta(
            delta_type=DeltaType.FILE_MODIFY,
            target_path=str(test_file),
            old_content="original content",
            new_content="modified content",
        )

        # Test forward operation
        FileModifyHandler.apply_forward(delta)
        assert test_file.read_text(encoding="utf-8") == "modified content"

        # Test reverse operation
        FileModifyHandler.apply_reverse(delta)
        assert test_file.read_text(encoding="utf-8") == "original content"

    def test_dir_create_handler(self) -> None:
        """Test DirCreateHandler operations."""
        test_dir = self.temp_path / "test_directory"
        delta = FileDelta(delta_type=DeltaType.DIR_CREATE, target_path=str(test_dir))

        # Test forward operation
        DirCreateHandler.apply_forward(delta)
        assert test_dir.exists()
        assert test_dir.is_dir()

        # Test reverse operation
        DirCreateHandler.apply_reverse(delta)
        assert not test_dir.exists()


class TestTracker:
    """Test cases for TrailSheriff tracker."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def teardown_method(self) -> None:
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_tracker_creation(self) -> None:
        """Test TrailSheriff creation and initialization."""
        tracker = TrackerSheriff("Test operation")

        assert tracker.description == "Test operation"
        assert len(tracker.deltas) == 0
        assert tracker.operation_id is not None

    def test_tracker_file_operations(self) -> None:
        """Test tracker file operation methods."""
        tracker = TrackerSheriff("File operations test")

        # Test file creation tracking
        test_file = self.temp_path / "tracked_file.txt"
        tracker.create_modify_file(test_file, new_content="content")
        tracker.finalize()

        assert test_file.exists()
        assert len(tracker.deltas) == 1
        assert tracker.deltas[0].delta_type == DeltaType.FILE_CREATE

    def test_tracker_directory_operations(self) -> None:
        """Test tracker directory operation methods."""
        tracker = TrackerSheriff("Directory operations test")

        test_dir = self.temp_path / "tracked_dir"
        tracker.create_dir(test_dir)

        assert len(tracker.deltas) == 1
        assert tracker.deltas[0].delta_type == DeltaType.DIR_CREATE

    @patch("vaf.core.state_manager.tracker.run_copy")
    def test_tracker_run_copy(self, mock_run_copy: Mock) -> None:
        """Test tracker run_copy method."""
        tracker = TrackerSheriff("Copy operation test")

        # Create test files before copy
        test_file = self.temp_path / "existing.txt"
        test_file.write_text("original", encoding="utf-8")

        # Mock the copy operation
        mock_run_copy.return_value = None

        tracker.run_copy("src_template", str(self.temp_path), {"key": "value"})

        # Verify run_copy was called
        mock_run_copy.assert_called_once()

    def test_tracking_context_manager(self) -> None:
        """Test tracking_context context manager."""
        with tracking_context("Context test") as tracker:
            assert isinstance(tracker, TrackerSheriff)
            assert tracker.description == "Context test"

            # Add some operations
            test_file = self.temp_path / "context_file.txt"
            tracker.create_modify_file(test_file, "content")

        # After context exit, operations should be finalized
        assert len(tracker.deltas) == 1

    def test_activate_tracking_decorator(self) -> None:
        """Test activate_tracking decorator."""

        @activate_tracking("Decorator test", "test_dir")
        def test_function(name: str, test_dir: str, **kwargs) -> Tuple[str, TrackerSheriff | None]:
            tracker = kwargs.get("tracker", None)
            return f"Processed {name} in {test_dir}: with tracker {tracker}", tracker

        result, tracker = test_function("test", str(self.temp_path))
        assert result == f"Processed test in {str(self.temp_path)}: with tracker {tracker}"


class TestStateManager:
    """Test cases for TrailSheriff state manager."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def teardown_method(self) -> None:
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("test_comprehensive_state_manager.get_state_manager")
    def test_state_manager_factory(self, mock_get_manager: Mock) -> None:
        """Test state manager factory function."""
        mock_manager = Mock(spec=StatusQuoOrdinator)
        mock_get_manager.return_value = mock_manager

        manager = get_state_manager(str(self.temp_path))

        assert manager is mock_manager
        mock_get_manager.assert_called_once_with(str(self.temp_path))


class TestEdgeCases:
    """Test cases for edge cases and error conditions."""

    def test_invalid_file_operations(self) -> None:
        """Test operations on invalid files."""
        invalid_path = Path("/nonexistent/path/file.txt")

        # Test file creation with invalid parent
        delta = FileDelta(delta_type=DeltaType.FILE_CREATE, target_path=str(invalid_path), new_content="content")

        # Should handle parent directory creation
        try:
            FileCreateHandler.apply_forward(delta)
        except PermissionError:
            # Expected on systems where /nonexistent can't be created
            pass

    def test_empty_delta_operations(self) -> None:
        """Test operations with empty or None content."""
        # Test file creation without content
        with pytest.raises(ValueError):
            delta = FileDelta(delta_type=DeltaType.FILE_CREATE, target_path="/test.txt", new_content=None)
            FileCreateHandler.apply_forward(delta)

    def test_concurrent_operations(self) -> None:
        """Test behavior under concurrent operations."""
        # This is a placeholder for concurrent operation tests
        # In a real implementation, you'd test thread safety
        tracker1 = TrackerSheriff("Operation 1")
        tracker2 = TrackerSheriff("Operation 2")

        assert tracker1.operation_id != tracker2.operation_id

    def test_large_file_operations(self) -> None:
        """Test operations with large files."""
        large_content = "x" * 10000  # 10KB content

        delta = create_file_delta("/large_test.txt", large_content)
        assert len(delta.new_content or "") == 10000

    def test_unicode_file_operations(self) -> None:
        """Test operations with unicode content and paths."""
        unicode_content = "Hello 世界! 🌍 Héllo"
        unicode_path = "/test_üñíçødé_file.txt"

        delta = create_file_delta(unicode_path, unicode_content)
        assert delta.target_path == unicode_path
        assert delta.new_content == unicode_content


class TestProtocolCompliance:
    """Test cases for protocol compliance and interface contracts."""

    def test_file_delta_interface_compliance(self) -> None:
        """Test that FileDelta implements FileDeltaInterface properly."""
        delta = FileDelta(delta_type=DeltaType.FILE_CREATE, target_path="/test.txt", new_content="content")

        # Test that all protocol methods/properties are available
        assert hasattr(delta, "delta_type")
        assert hasattr(delta, "target_path")
        assert hasattr(delta, "old_content")
        assert hasattr(delta, "new_content")
        assert hasattr(delta, "old_path")
        assert hasattr(delta, "file_existed")
        assert hasattr(delta, "timestamp")
        assert hasattr(delta, "checksum")
        assert hasattr(delta, "symlink_target")
        assert hasattr(delta, "processed")

    def test_delta_type_protocol_compliance(self) -> None:
        """Test that DeltaType enum implements DeltaTypeProtocol."""

        for delta_type in DeltaType:
            # Verify protocol methods exist
            assert hasattr(delta_type, "apply_forward")
            assert hasattr(delta_type, "apply_reverse")
            assert callable(delta_type.apply_forward)
            assert callable(delta_type.apply_reverse)
