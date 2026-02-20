# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Unit tests for the state manager factory module.

This module tests all factory functions for creating delta objects
and the state manager getter function.
"""
# mypy: disable-error-code="no-untyped-def,arg-type,operator"

from pathlib import Path
from unittest.mock import MagicMock, patch

from vaf.core.state_manager.data_model import DeltaType, FileDelta
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
from vaf.core.state_manager.state_manager import StatusQuoOrdinator


class TestFileOperationFactories:
    """Test suite for file operation factory functions."""

    def test_create_file_delta_minimal(self) -> None:
        """Test create_file_delta with minimal parameters."""
        delta = create_file_delta("test.txt", "content")

        assert isinstance(delta, FileDelta)
        assert delta.delta_type == DeltaType.FILE_CREATE
        assert delta.target_path == "test.txt"
        assert delta.new_content == "content"
        assert delta.file_existed is False
        assert delta.processed is False
        assert delta.old_content is None

    def test_create_file_delta_with_processed(self) -> None:
        """Test create_file_delta with processed flag."""
        delta = create_file_delta("test.txt", "content", processed=True)

        assert delta.processed is True
        assert delta.delta_type == DeltaType.FILE_CREATE
        assert delta.target_path == "test.txt"
        assert delta.new_content == "content"

    def test_modify_file_delta_minimal(self) -> None:
        """Test modify_file_delta with minimal parameters."""
        delta = modify_file_delta("test.txt", "old", "new")

        assert isinstance(delta, FileDelta)
        assert delta.delta_type == DeltaType.FILE_MODIFY
        assert delta.target_path == "test.txt"
        assert delta.old_content == "old"
        assert delta.new_content == "new"
        assert delta.file_existed is True
        assert delta.processed is False

    def test_modify_file_delta_with_processed(self) -> None:
        """Test modify_file_delta with processed flag."""
        delta = modify_file_delta("test.txt", "old", "new", processed=True)

        assert delta.processed is True
        assert delta.delta_type == DeltaType.FILE_MODIFY
        assert delta.old_content == "old"
        assert delta.new_content == "new"

    def test_delete_file_delta_minimal(self):
        """Test delete_file_delta with minimal parameters."""
        delta = delete_file_delta("test.txt", "content")

        assert isinstance(delta, FileDelta)
        assert delta.delta_type == DeltaType.FILE_DELETE
        assert delta.target_path == "test.txt"
        assert delta.old_content == "content"
        assert delta.file_existed is True
        assert delta.processed is False
        assert delta.new_content is None

    def test_delete_file_delta_with_processed(self) -> None:
        """Test delete_file_delta with processed flag."""
        delta = delete_file_delta("test.txt", "content", processed=True)

        assert delta.processed is True
        assert delta.delta_type == DeltaType.FILE_DELETE
        assert delta.old_content == "content"


class TestSymlinkOperationFactories:
    """Test suite for symlink operation factory functions."""

    def test_create_file_symlink_delta_minimal(self):
        """Test create_file_symlink_delta with minimal parameters."""
        delta = create_file_symlink_delta("link.txt", "/target/file.txt")

        assert isinstance(delta, FileDelta)
        assert delta.delta_type == DeltaType.SYMLINK_FILE_CREATE
        assert delta.target_path == "link.txt"
        assert delta.symlink_target == "/target/file.txt"
        assert delta.file_existed is False
        assert delta.processed is False

    def test_create_file_symlink_delta_with_processed(self):
        """Test create_file_symlink_delta with processed flag."""
        delta = create_file_symlink_delta("link.txt", "/target/file.txt", processed=True)

        assert delta.processed is True
        assert delta.delta_type == DeltaType.SYMLINK_FILE_CREATE
        assert delta.symlink_target == "/target/file.txt"

    def test_delete_file_symlink_delta_minimal(self):
        """Test delete_file_symlink_delta with minimal parameters."""
        delta = delete_file_symlink_delta("link.txt", "/target/file.txt")

        assert isinstance(delta, FileDelta)
        assert delta.delta_type == DeltaType.SYMLINK_FILE_DELETE
        assert delta.target_path == "link.txt"
        assert delta.symlink_target == "/target/file.txt"
        assert delta.file_existed is False
        assert delta.processed is False

    def test_delete_file_symlink_delta_with_processed(self):
        """Test delete_file_symlink_delta with processed flag."""
        delta = delete_file_symlink_delta("link.txt", "/target/file.txt", processed=True)

        assert delta.processed is True
        assert delta.delta_type == DeltaType.SYMLINK_FILE_DELETE

    def test_create_dir_symlink_delta_minimal(self):
        """Test create_dir_symlink_delta with minimal parameters."""
        delta = create_dir_symlink_delta("link_dir", "/target/dir")

        assert isinstance(delta, FileDelta)
        assert delta.delta_type == DeltaType.SYMLINK_DIR_CREATE
        assert delta.target_path == "link_dir"
        assert delta.symlink_target == "/target/dir"
        assert delta.file_existed is False
        assert delta.processed is False

    def test_create_dir_symlink_delta_with_processed(self):
        """Test create_dir_symlink_delta with processed flag."""
        delta = create_dir_symlink_delta("link_dir", "/target/dir", processed=True)

        assert delta.processed is True
        assert delta.delta_type == DeltaType.SYMLINK_DIR_CREATE

    def test_delete_dir_symlink_delta_minimal(self):
        """Test delete_dir_symlink_delta with minimal parameters."""
        delta = delete_dir_symlink_delta("link_dir", "/target/dir")

        assert isinstance(delta, FileDelta)
        assert delta.delta_type == DeltaType.SYMLINK_DIR_DELETE
        assert delta.target_path == "link_dir"
        assert delta.symlink_target == "/target/dir"
        assert delta.file_existed is False
        assert delta.processed is False

    def test_delete_dir_symlink_delta_with_processed(self):
        """Test delete_dir_symlink_delta with processed flag."""
        delta = delete_dir_symlink_delta("link_dir", "/target/dir", processed=True)

        assert delta.processed is True
        assert delta.delta_type == DeltaType.SYMLINK_DIR_DELETE


class TestDirectoryOperationFactories:
    """Test suite for directory operation factory functions."""

    def test_create_dir_delta_minimal(self):
        """Test create_dir_delta with minimal parameters."""
        delta = create_dir_delta("test_dir")

        assert isinstance(delta, FileDelta)
        assert delta.delta_type == DeltaType.DIR_CREATE
        assert delta.target_path == "test_dir"
        assert delta.file_existed is False
        assert delta.processed is False
        assert delta.old_content is None
        assert delta.new_content is None

    def test_create_dir_delta_with_processed(self):
        """Test create_dir_delta with processed flag."""
        delta = create_dir_delta("test_dir", processed=True)

        assert delta.processed is True
        assert delta.delta_type == DeltaType.DIR_CREATE
        assert delta.target_path == "test_dir"

    def test_delete_dir_delta_minimal(self):
        """Test delete_dir_delta with minimal parameters."""
        delta = delete_dir_delta("test_dir")

        assert isinstance(delta, FileDelta)
        assert delta.delta_type == DeltaType.DIR_DELETE
        assert delta.target_path == "test_dir"
        assert delta.file_existed is True
        assert delta.processed is False
        assert delta.old_content is None
        assert delta.new_content is None

    def test_delete_dir_delta_with_processed(self):
        """Test delete_dir_delta with processed flag."""
        delta = delete_dir_delta("test_dir", processed=True)

        assert delta.processed is True
        assert delta.delta_type == DeltaType.DIR_DELETE
        assert delta.target_path == "test_dir"


class TestGetStateManager:
    """Test suite for get_state_manager function."""

    @patch("vaf.core.state_manager.factory.StatusQuoOrdinator")
    def test_get_state_manager_with_path_string(self, mock_status_quo):
        """Test get_state_manager with string path."""
        mock_instance = MagicMock()
        mock_status_quo.return_value = mock_instance

        result = get_state_manager("/path/to/project")

        mock_status_quo.assert_called_once_with(Path("/path/to/project"))
        assert result == mock_instance

    @patch("vaf.core.state_manager.factory.StatusQuoOrdinator")
    def test_get_state_manager_with_path_object(self, mock_status_quo):
        """Test get_state_manager with Path object."""
        mock_instance = MagicMock()
        mock_status_quo.return_value = mock_instance

        path_obj = Path("/path/to/project")
        result = get_state_manager(str(path_obj))

        mock_status_quo.assert_called_once_with(path_obj)
        assert result == mock_instance

    @patch("vaf.core.state_manager.factory.StatusQuoOrdinator")
    def test_get_state_manager_with_default_path(self, mock_status_quo):
        """Test get_state_manager with default (current) path."""
        mock_instance = MagicMock()
        mock_status_quo.return_value = mock_instance

        # Call get_state_manager without arguments
        result = get_state_manager()

        # Assert that StatusQuoOrdinator was called with Path(".")
        mock_status_quo.assert_called_once_with(Path())
        assert result == mock_instance

    def test_get_state_manager_returns_status_quo_ordinator(self):
        """Test that get_state_manager returns StatusQuoOrdinator instance."""
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            result = get_state_manager(temp_dir)

            assert isinstance(result, StatusQuoOrdinator)
            assert result.project_dir == Path(temp_dir).resolve()


class TestFactoryFunctionTypes:
    """Test suite for verifying factory function return types and consistency."""

    def test_all_factories_return_file_delta(self):
        """Test that all factory functions return FileDelta instances."""
        factories_and_args = [
            (create_file_delta, ("test.txt", "content")),
            (modify_file_delta, ("test.txt", "old", "new")),
            (delete_file_delta, ("test.txt", "content")),
            (create_dir_delta, ("test_dir",)),
            (delete_dir_delta, ("test_dir",)),
            (create_file_symlink_delta, ("link.txt", "/target")),
            (delete_file_symlink_delta, ("link.txt", "/target")),
            (create_dir_symlink_delta, ("link_dir", "/target")),
            (delete_dir_symlink_delta, ("link_dir", "/target")),
        ]

        for factory_func, args in factories_and_args:
            result = factory_func(*args)
            assert isinstance(result, FileDelta), f"{factory_func.__name__} should return FileDelta"

    def test_all_factories_accept_processed_parameter(self):
        """Test that all factory functions accept processed parameter."""
        factories_and_args = [
            (create_file_delta, ("test.txt", "content")),
            (modify_file_delta, ("test.txt", "old", "new")),
            (delete_file_delta, ("test.txt", "content")),
            (create_dir_delta, ("test_dir",)),
            (delete_dir_delta, ("test_dir",)),
            (create_file_symlink_delta, ("link.txt", "/target")),
            (delete_file_symlink_delta, ("link.txt", "/target")),
            (create_dir_symlink_delta, ("link_dir", "/target")),
            (delete_dir_symlink_delta, ("link_dir", "/target")),
        ]

        for factory_func, args in factories_and_args:
            # Test with processed=True
            result = factory_func(*args, processed=True)
            assert result.processed is True, f"{factory_func.__name__} should accept processed=True"

            # Test with processed=False (default)
            result = factory_func(*args, processed=False)
            assert result.processed is False, f"{factory_func.__name__} should accept processed=False"

    def test_factory_function_docstrings(self):
        """Test that all factory functions have proper docstrings."""
        factories = [
            create_file_delta,
            modify_file_delta,
            delete_file_delta,
            create_dir_delta,
            delete_dir_delta,
            create_file_symlink_delta,
            delete_file_symlink_delta,
            create_dir_symlink_delta,
            delete_dir_symlink_delta,
        ]

        for factory_func in factories:
            assert factory_func.__doc__ is not None, f"{factory_func.__name__} should have docstring"
            assert "processed" in factory_func.__doc__, (
                f"{factory_func.__name__} docstring should mention processed parameter"
            )

    def test_delta_type_assignments(self):
        """Test that factory functions assign correct DeltaType values."""
        test_cases = [
            (create_file_delta, ("test.txt", "content"), DeltaType.FILE_CREATE),
            (modify_file_delta, ("test.txt", "old", "new"), DeltaType.FILE_MODIFY),
            (delete_file_delta, ("test.txt", "content"), DeltaType.FILE_DELETE),
            (create_dir_delta, ("test_dir",), DeltaType.DIR_CREATE),
            (delete_dir_delta, ("test_dir",), DeltaType.DIR_DELETE),
            (create_file_symlink_delta, ("link.txt", "/target"), DeltaType.SYMLINK_FILE_CREATE),
            (delete_file_symlink_delta, ("link.txt", "/target"), DeltaType.SYMLINK_FILE_DELETE),
            (create_dir_symlink_delta, ("link_dir", "/target"), DeltaType.SYMLINK_DIR_CREATE),
            (delete_dir_symlink_delta, ("link_dir", "/target"), DeltaType.SYMLINK_DIR_DELETE),
        ]

        for factory_func, args, expected_type in test_cases:
            result = factory_func(*args)
            assert result.delta_type == expected_type, f"{factory_func.__name__} should create {expected_type}"


class TestFactoryFunctionEdgeCases:
    """Test suite for edge cases and error conditions."""

    def test_empty_strings_allowed(self):
        """Test that factory functions handle empty strings appropriately."""
        # Empty target path
        delta = create_file_delta("", "content")
        assert delta.target_path == ""

        # Empty content
        delta = create_file_delta("test.txt", "")
        assert delta.new_content == ""

        # Empty symlink target
        delta = create_file_symlink_delta("link.txt", "")
        assert delta.symlink_target == ""

    def test_unicode_strings_supported(self):
        """Test that factory functions support unicode strings."""
        unicode_content = "Hello 世界 🌍"
        unicode_path = "test_文件.txt"

        delta = create_file_delta(unicode_path, unicode_content)
        assert delta.target_path == unicode_path
        assert delta.new_content == unicode_content

    def test_long_strings_supported(self):
        """Test that factory functions support long strings."""
        long_content = "x" * 10000
        long_path = "a" * 255  # Typical filesystem limit

        delta = create_file_delta(long_path, long_content)
        assert delta.target_path == long_path
        assert delta.new_content == long_content

    def test_special_characters_in_paths(self):
        """Test that factory functions handle special characters in paths."""
        special_chars_path = "test/path with spaces & symbols!@#$%^&*()_+-={}[]|\\:;\"'<>,.?/~`"

        delta = create_file_delta(special_chars_path, "content")
        assert delta.target_path == special_chars_path
