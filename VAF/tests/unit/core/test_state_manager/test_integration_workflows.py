# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Integration Tests for State Manager System

This module provides integration testing that verifies the complete workflow
of the state manager system, testing interactions between components.
"""
# mypy: disable-error-code="no-untyped-def"

import json
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from vaf.core.state_manager.data_model import DeltaType, OperationGroup
from vaf.core.state_manager.tracker import tracking_context


class TestIntegrationWorkflows:
    """Integration tests for complete state manager workflows."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def teardown_method(self) -> None:
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_complete_file_lifecycle(self, tmp_path, monkeypatch) -> None:
        """Test complete file lifecycle: create -> modify -> delete."""
        monkeypatch.chdir(tmp_path)
        with tracking_context("File lifecycle test") as tracker:
            test_file = self.temp_path / "lifecycle_test.txt"

            # Create file
            tracker.create_modify_file(test_file, "initial content")
            tracker.finalize()
            assert test_file.exists()
            assert test_file.read_text(encoding="utf-8") == "initial content"

            # Modify file
            tracker.create_modify_file(test_file, "modified content")
            tracker.finalize()
            assert test_file.read_text(encoding="utf-8") == "modified content"

            # Delete file (track before deletion)
            tracker.delete_file(test_file)
            tracker.finalize()
            assert not test_file.exists()

        # Verify all operations were tracked
        assert len(tracker.deltas) == 3
        assert tracker.deltas[0].delta_type == DeltaType.FILE_CREATE
        assert tracker.deltas[1].delta_type == DeltaType.FILE_MODIFY
        assert tracker.deltas[2].delta_type == DeltaType.FILE_DELETE

    def test_directory_operations_with_files(self, tmp_path, monkeypatch) -> None:
        """Test directory operations containing files."""
        monkeypatch.chdir(tmp_path)
        with tracking_context("Directory with files test") as tracker:
            # Create directory structure
            test_dir = self.temp_path / "test_directory"
            test_file = test_dir / "test_file.txt"

            # Track directory creation
            tracker.create_dir(test_dir)

            # Track file creation in directory
            tracker.create_modify_file(test_file, "file in directory")
            tracker.finalize()

            assert test_dir.exists()
            assert test_file.exists()
            assert test_file.read_text(encoding="utf-8") == "file in directory"

        assert len(tracker.deltas) == 2
        assert tracker.deltas[0].delta_type == DeltaType.DIR_CREATE
        assert tracker.deltas[1].delta_type == DeltaType.FILE_CREATE

    def test_symlink_operations(self, tmp_path, monkeypatch) -> None:
        """Test symlink creation and deletion operations."""
        monkeypatch.chdir(tmp_path)
        with tracking_context("Symlink operations test") as tracker:
            # Create target file
            target_file = self.temp_path / "target.txt"
            target_file.write_text("target content", encoding="utf-8")

            # Create symlink
            symlink_path = self.temp_path / "link.txt"
            tracker.create_file_symlink(symlink_path, target_file)
            tracker.finalize()

            assert symlink_path.exists()
            assert symlink_path.is_symlink()
            assert symlink_path.read_text(encoding="utf-8") == "target content"

            # Delete symlink
            tracker.delete_file_symlink(symlink_path, target_file)

        assert len(tracker.deltas) == 2
        assert tracker.deltas[0].delta_type == DeltaType.SYMLINK_FILE_CREATE
        assert tracker.deltas[1].delta_type == DeltaType.SYMLINK_FILE_DELETE

    @patch("vaf.core.state_manager.tracker.run_copy")
    def test_template_processing_workflow(self, mock_run_copy, tmp_path, monkeypatch) -> None:
        """Test complete template processing workflow with run_copy."""
        monkeypatch.chdir(tmp_path)
        with tracking_context("Template processing test") as tracker:
            # Setup existing files that will be modified
            existing_file = self.temp_path / "existing.txt"
            existing_file.write_text("original content", encoding="utf-8")

            new_file = self.temp_path / "new.txt"

            # Mock run_copy to simulate template processing
            def mock_copy_side_effect(*args, **kwargs):
                # Simulate template processing: modify existing, create new
                existing_file.write_text("template modified content", encoding="utf-8")
                new_file.write_text("new template content", encoding="utf-8")

            mock_run_copy.side_effect = mock_copy_side_effect

            # Use run_copy with tracking
            tracker.run_copy("template_path", str(self.temp_path), {"template_var": "value"})

            # Verify files were processed
            assert existing_file.read_text(encoding="utf-8") == "template modified content"
            assert new_file.read_text(encoding="utf-8") == "new template content"

            # Verify tracking occurred
            assert len(tracker.deltas) >= 1  # At least one operation should be tracked

    def test_error_handling_workflow(self, tmp_path, monkeypatch) -> None:
        """Test error handling in integrated workflows."""
        monkeypatch.chdir(tmp_path)
        with tracking_context("Error handling test") as tracker:
            # Try to create file in non-existent directory (should handle gracefully)
            non_existent_dir = self.temp_path / "non_existent" / "deep" / "path"
            test_file = non_existent_dir / "test.txt"

            # This should create parent directories
            tracker.create_modify_file(test_file, "content")
            tracker.finalize()

            assert test_file.exists()
            assert test_file.read_text(encoding="utf-8") == "content"

        assert len(tracker.deltas) == 1

    def test_multiple_trackers_workflow(self, tmp_path, monkeypatch) -> None:
        """Test workflow with multiple independent trackers."""
        monkeypatch.chdir(tmp_path)
        tracker1_deltas = []
        tracker2_deltas = []

        with tracking_context("First operation") as tracker1:
            file1 = self.temp_path / "file1.txt"
            tracker1.create_modify_file(file1, "content 1")
            tracker1_deltas = tracker1.deltas.copy()

        with tracking_context("Second operation") as tracker2:
            file2 = self.temp_path / "file2.txt"
            tracker2.create_modify_file(file2, "content 2")
            tracker2_deltas = tracker2.deltas.copy()

        # Verify independent tracking
        assert len(tracker1_deltas) == 1
        assert len(tracker2_deltas) == 1
        assert tracker1_deltas[0].target_path != tracker2_deltas[0].target_path

    def test_nested_directory_operations(self, tmp_path, monkeypatch) -> None:
        """Test operations on nested directory structures."""
        monkeypatch.chdir(tmp_path)
        with tracking_context("Nested directory test") as tracker:
            # Create nested structure
            base_dir = self.temp_path / "level1"
            mid_dir = base_dir / "level2"
            deep_dir = mid_dir / "level3"
            deep_file = deep_dir / "deep_file.txt"

            # Track each level
            tracker.create_dir(base_dir)

            tracker.create_dir(mid_dir)

            tracker.create_dir(deep_dir)

            tracker.create_modify_file(deep_file, "deep content")
            tracker.finalize()

            # Verify structure
            assert deep_file.exists()
            assert deep_file.read_text(encoding="utf-8") == "deep content"

        assert len(tracker.deltas) == 4  # 3 dirs + 1 file

    def test_unicode_and_special_characters(self, tmp_path, monkeypatch) -> None:
        """Test operations with unicode and special characters."""
        monkeypatch.chdir(tmp_path)
        with tracking_context("Unicode test 🌍") as tracker:
            # Test with unicode filename and content
            unicode_file = self.temp_path / "tëst_üñíçødé_🌍.txt"
            unicode_content = "Hello 世界! Content with émojis 🚀 and spëcial çhars"

            tracker.create_modify_file(unicode_file, unicode_content)

            tracker.finalize()
            assert unicode_file.exists()
            assert unicode_file.read_text(encoding="utf-8") == unicode_content

        assert len(tracker.deltas) == 1
        assert tracker.deltas[0].new_content == unicode_content

    def test_performance_with_many_operations(self, tmp_path, monkeypatch) -> None:
        """Test performance with a large number of operations."""
        start_time = time.time()
        monkeypatch.chdir(tmp_path)
        with tracking_context("Performance test") as tracker:
            # Create many files
            for i in range(100):
                test_file = self.temp_path / f"perf_test_{i}.txt"
                tracker.create_modify_file(test_file, f"Content {i}")

        end_time = time.time()
        execution_time = end_time - start_time

        # Verify all operations were tracked
        assert len(tracker.deltas) == 100

        # Performance assertion (should complete within reasonable time)
        assert execution_time < 5.0  # Should complete within 5 seconds

    def test_serialization_round_trip(self, tmp_path, monkeypatch) -> None:
        """Test complete serialization and deserialization workflow."""
        monkeypatch.chdir(tmp_path)
        # Create operations with tracker
        with tracking_context("Serialization test") as tracker:
            test_file = self.temp_path / "serialize_test.txt"
            tracker.create_modify_file(test_file, "serialization content")

            # Manually create an operation group for testing
            operation = OperationGroup(
                operation_id=tracker.operation_id,
                description=tracker.description,
                deltas=tracker.deltas,
                completed=True,
            )

            # Serialize to JSON
            json_data = operation.model_dump_json()

            # Deserialize from JSON
            parsed_data = json.loads(json_data)
            reconstructed_operation = OperationGroup.model_validate(parsed_data)

            # Verify reconstruction
            assert reconstructed_operation.operation_id == operation.operation_id
            assert reconstructed_operation.description == operation.description
            assert len(reconstructed_operation.deltas) == len(operation.deltas)
            assert reconstructed_operation.deltas[0].target_path == operation.deltas[0].target_path


class TestErrorScenarios:
    """Integration tests for error scenarios and edge cases."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def teardown_method(self) -> None:
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_permission_denied_scenarios(self, tmp_path, monkeypatch) -> None:
        """Test handling of permission denied scenarios."""
        monkeypatch.chdir(tmp_path)
        with tracking_context("Permission test") as tracker:
            # Try to create file in system directory (might fail with permission)
            system_file = Path("/root/test_permission.txt")

            # This should handle permission errors gracefully
            try:
                tracker.create_modify_file(system_file, "content")
            except PermissionError:
                # Expected behavior - tracker should handle this
                pass

    def test_disk_space_simulation(self, tmp_path, monkeypatch) -> None:
        """Test behavior when simulating disk space issues."""
        monkeypatch.chdir(tmp_path)
        with tracking_context("Disk space test") as tracker:
            # Create a very large content string (simulating space issue)
            large_content = "x" * 1000000  # 1MB content
            large_file = self.temp_path / "large_test.txt"

            # This should work in most test environments
            tracker.create_modify_file(large_file, large_content)

            if large_file.exists():
                assert len(large_file.read_text(encoding="utf-8")) == 1000000

    def test_concurrent_file_access(self, tmp_path, monkeypatch) -> None:
        """Test concurrent access to the same file."""
        monkeypatch.chdir(tmp_path)
        test_file = self.temp_path / "concurrent_test.txt"
        test_file.write_text("initial", encoding="utf-8")

        with tracking_context("Concurrent test 1") as tracker1:
            tracker1.create_modify_file(test_file, "modified by tracker1")

        with tracking_context("Concurrent test 2") as tracker2:
            # Second tracker operates on the same file
            current_content = test_file.read_text(encoding="utf-8")
            tracker2.create_modify_file(test_file, current_content + " + tracker2")

        # Verify final state
        final_content = test_file.read_text(encoding="utf-8")
        assert "tracker2" in final_content

    def test_malformed_symlink_handling(self, tmp_path, monkeypatch) -> None:
        """Test handling of malformed or broken symlinks."""
        monkeypatch.chdir(tmp_path)
        with pytest.raises(ValueError, match="Invalid symlink target:"):
            with tracking_context("Malformed symlink test") as tracker:
                # Create symlink to non-existent target
                symlink_path = self.temp_path / "broken_link.txt"
                non_existent_target = self.temp_path / "does_not_exist.txt"

                # Track creation of broken symlink
                tracker.create_file_symlink(symlink_path, non_existent_target)

                # Create the actual broken symlink
                try:
                    symlink_path.symlink_to(non_existent_target)

                    # Verify symlink exists but target doesn't
                    assert symlink_path.is_symlink()
                    assert not symlink_path.exists()  # Broken symlink

                except OSError:
                    # Some systems might not allow broken symlinks
                    pass

    def test_circular_symlink_detection(self, tmp_path, monkeypatch) -> None:
        """Test detection and handling of circular symlinks."""
        monkeypatch.chdir(tmp_path)
        with pytest.raises(ValueError, match="Invalid symlink target:"):
            with tracking_context("Circular symlink test") as tracker:
                link1 = self.temp_path / "link1.txt"
                link2 = self.temp_path / "link2.txt"

                # This would create circular symlinks in a real scenario
                tracker.create_file_symlink(link1, link2)
                tracker.create_file_symlink(link2, link1)

                # The tracking should work regardless of the circular nature
                assert len(tracker.deltas) == 2
