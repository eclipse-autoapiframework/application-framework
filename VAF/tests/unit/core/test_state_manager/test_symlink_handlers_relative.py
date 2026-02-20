# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Test Suite for Relative Symlink Support in Symlink Handlers

This test suite follows TDD principles to ensure that both SymlinkFileCreateHandler
and SymlinkDirCreateHandler can handle relative symlinks correctly.
"""
# mypy: disable-error-code="no-untyped-def"

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import pytest

from vaf.core.state_manager.data_handlers.symlink_handlers import (
    SymlinkDirCreateHandler,
    SymlinkFileCreateHandler,
)
from vaf.core.state_manager.protocols.protocols import DeltaTypeProtocol, FileDeltaInterface


class MockDeltaType:
    """Mock DeltaType for testing."""

    def apply_forward(self, delta: FileDeltaInterface) -> None:
        """Mock apply_forward."""
        pass

    def apply_reverse(self, delta: FileDeltaInterface) -> None:
        """Mock apply_reverse."""
        pass


@dataclass
class MockDelta:
    """Mock delta for testing symlink operations."""

    target_path: str
    symlink_target: str
    relative_to: Optional[str] = None
    delta_type: DeltaTypeProtocol = field(default_factory=MockDeltaType)
    old_content: Optional[str] = None
    new_content: Optional[str] = None
    old_path: Optional[str] = None
    file_existed: bool = False
    timestamp: float = 0.0
    checksum: Optional[str] = None
    processed: bool = False


class TestSymlinkFileCreateHandlerRelative:
    """Test cases for SymlinkFileCreateHandler with relative paths."""

    def test_absolute_symlink_backward_compatibility(self, tmp_path):
        """Test that absolute symlinks still work (backward compatibility)."""
        # Arrange
        source_file = tmp_path / "source.txt"
        source_file.write_text("test content")
        target_symlink = tmp_path / "link.txt"

        delta = MockDelta(
            target_path=str(target_symlink),
            symlink_target=str(source_file),
            relative_to=None,  # Absolute path mode
        )

        # Act
        SymlinkFileCreateHandler.apply_forward(delta)

        # Assert
        assert target_symlink.is_symlink()
        assert target_symlink.resolve() == source_file.resolve()
        assert target_symlink.read_text() == "test content"

    def test_relative_symlink_creation(self, tmp_path):
        """Test creating a relative symlink."""
        # Arrange
        base_dir = tmp_path / "base"
        base_dir.mkdir()
        source_file = tmp_path / "source" / "file.txt"
        source_file.parent.mkdir()
        source_file.write_text("relative test")

        target_symlink = base_dir / "link.txt"

        delta = MockDelta(
            target_path=str(target_symlink),
            symlink_target=str(source_file),
            relative_to=str(base_dir),
        )

        # Act
        SymlinkFileCreateHandler.apply_forward(delta)

        # Assert
        assert target_symlink.is_symlink()
        # Check that the symlink target is relative, not absolute
        link_target = Path.readlink(target_symlink)
        assert not Path(link_target).is_absolute()
        # But it should still resolve to the correct file
        assert target_symlink.resolve() == source_file.resolve()
        assert target_symlink.read_text() == "relative test"

    def test_relative_symlink_with_nested_structure(self, tmp_path):
        """Test relative symlink with nested directory structure."""
        # Arrange
        # Structure: tmp/project/src/module/link -> tmp/project/lib/file.txt
        project_dir = tmp_path / "project"
        src_dir = project_dir / "src" / "module"
        lib_dir = project_dir / "lib"
        src_dir.mkdir(parents=True)
        lib_dir.mkdir(parents=True)

        source_file = lib_dir / "library.txt"
        source_file.write_text("library content")

        target_symlink = src_dir / "lib_link.txt"

        delta = MockDelta(
            target_path=str(target_symlink),
            symlink_target=str(source_file),
            relative_to=str(src_dir),
        )

        # Act
        SymlinkFileCreateHandler.apply_forward(delta)

        # Assert
        assert target_symlink.is_symlink()
        link_target = Path.readlink(target_symlink)
        assert not Path(link_target).is_absolute()
        assert target_symlink.resolve() == source_file.resolve()
        assert target_symlink.read_text() == "library content"

    def test_relative_symlink_reverse_operation(self, tmp_path):
        """Test that reverse operation works for relative symlinks."""
        # Arrange
        base_dir = tmp_path / "base"
        base_dir.mkdir()
        source_file = tmp_path / "source.txt"
        source_file.write_text("test")
        target_symlink = base_dir / "link.txt"

        delta = MockDelta(
            target_path=str(target_symlink),
            symlink_target=str(source_file),
            relative_to=str(base_dir),
        )

        # Create the symlink
        SymlinkFileCreateHandler.apply_forward(delta)
        assert target_symlink.is_symlink()

        # Act - Reverse the operation
        SymlinkFileCreateHandler.apply_reverse(delta)

        # Assert
        assert not target_symlink.exists()

    def test_relative_symlink_with_parent_traversal(self, tmp_path):
        """Test relative symlink that traverses parent directories."""
        # Arrange
        # Structure: tmp/a/b/link -> tmp/c/file.txt (link uses ../../c/file.txt)
        dir_a_b = tmp_path / "a" / "b"
        dir_c = tmp_path / "c"
        dir_a_b.mkdir(parents=True)
        dir_c.mkdir()

        source_file = dir_c / "file.txt"
        source_file.write_text("parent traversal test")

        target_symlink = dir_a_b / "link.txt"

        delta = MockDelta(
            target_path=str(target_symlink),
            symlink_target=str(source_file),
            relative_to=str(dir_a_b),
        )

        # Act
        SymlinkFileCreateHandler.apply_forward(delta)

        # Assert
        assert target_symlink.is_symlink()
        link_target = Path.readlink(target_symlink)
        assert not Path(link_target).is_absolute()
        assert ".." in str(link_target)  # Should contain parent directory references
        assert target_symlink.resolve() == source_file.resolve()

    def test_relative_to_with_nonexistent_base_raises_error(self, tmp_path):
        """Test that relative_to pointing to non-existent directory raises error."""
        # Arrange
        source_file = tmp_path / "source.txt"
        source_file.write_text("test")
        target_symlink = tmp_path / "link.txt"
        nonexistent_base = tmp_path / "nonexistent"

        delta = MockDelta(
            target_path=str(target_symlink),
            symlink_target=str(source_file),
            relative_to=str(nonexistent_base),
        )

        # Act & Assert
        with pytest.raises(ValueError, match="relative_to path does not exist"):
            SymlinkFileCreateHandler.apply_forward(delta)

    def test_relative_symlink_source_not_exist_raises_error(self, tmp_path):
        """Test that creating symlink to non-existent file raises error."""
        # Arrange
        base_dir = tmp_path / "base"
        base_dir.mkdir()
        nonexistent_file = tmp_path / "nonexistent.txt"
        target_symlink = base_dir / "link.txt"

        delta = MockDelta(
            target_path=str(target_symlink),
            symlink_target=str(nonexistent_file),
            relative_to=str(base_dir),
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid symlink target"):
            SymlinkFileCreateHandler.apply_forward(delta)


class TestSymlinkDirCreateHandlerRelative:
    """Test cases for SymlinkDirCreateHandler with relative paths."""

    def test_absolute_dir_symlink_backward_compatibility(self, tmp_path):
        """Test that absolute directory symlinks still work."""
        # Arrange
        source_dir = tmp_path / "source_dir"
        source_dir.mkdir()
        (source_dir / "file.txt").write_text("content")

        target_symlink = tmp_path / "link_dir"

        delta = MockDelta(
            target_path=str(target_symlink),
            symlink_target=str(source_dir),
            relative_to=None,
        )

        # Act
        SymlinkDirCreateHandler.apply_forward(delta)

        # Assert
        assert target_symlink.is_symlink()
        assert target_symlink.is_dir()
        assert (target_symlink / "file.txt").read_text() == "content"

    def test_relative_dir_symlink_creation(self, tmp_path):
        """Test creating a relative directory symlink."""
        # Arrange
        base_dir = tmp_path / "base"
        base_dir.mkdir()
        source_dir = tmp_path / "modules" / "my_module"
        source_dir.mkdir(parents=True)
        (source_dir / "code.py").write_text("print('hello')")

        target_symlink = base_dir / "module_link"

        delta = MockDelta(
            target_path=str(target_symlink),
            symlink_target=str(source_dir),
            relative_to=str(base_dir),
        )

        # Act
        SymlinkDirCreateHandler.apply_forward(delta)

        # Assert
        assert target_symlink.is_symlink()
        assert target_symlink.is_dir()
        link_target = Path.readlink(target_symlink)
        assert not Path(link_target).is_absolute()
        assert (target_symlink / "code.py").read_text() == "print('hello')"

    def test_relative_dir_symlink_nested_structure(self, tmp_path):
        """Test relative directory symlink with complex nested structure."""
        # Arrange
        # Structure: tmp/app/imports/lib -> tmp/shared/libraries/lib
        app_dir = tmp_path / "app" / "imports"
        lib_dir = tmp_path / "shared" / "libraries" / "lib"
        app_dir.mkdir(parents=True)
        lib_dir.mkdir(parents=True)

        (lib_dir / "module.py").write_text("# library module")

        target_symlink = app_dir / "lib_link"

        delta = MockDelta(
            target_path=str(target_symlink),
            symlink_target=str(lib_dir),
            relative_to=str(app_dir),
        )

        # Act
        SymlinkDirCreateHandler.apply_forward(delta)

        # Assert
        assert target_symlink.is_symlink()
        assert target_symlink.is_dir()
        link_target = Path.readlink(target_symlink)
        assert not Path(link_target).is_absolute()
        assert (target_symlink / "module.py").exists()

    def test_relative_dir_symlink_reverse_operation(self, tmp_path):
        """Test reverse operation for relative directory symlinks."""
        # Arrange
        base_dir = tmp_path / "base"
        base_dir.mkdir()
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        target_symlink = base_dir / "link"

        delta = MockDelta(
            target_path=str(target_symlink),
            symlink_target=str(source_dir),
            relative_to=str(base_dir),
        )

        # Create the symlink
        SymlinkDirCreateHandler.apply_forward(delta)
        assert target_symlink.is_symlink()

        # Act
        SymlinkDirCreateHandler.apply_reverse(delta)

        # Assert
        assert not target_symlink.exists()


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_relative_to_is_file_not_directory(self, tmp_path):
        """Test that relative_to must be a directory."""
        # Arrange
        base_file = tmp_path / "base.txt"
        base_file.write_text("not a directory")
        source_file = tmp_path / "source.txt"
        source_file.write_text("test")
        target_symlink = tmp_path / "link.txt"

        delta = MockDelta(
            target_path=str(target_symlink),
            symlink_target=str(source_file),
            relative_to=str(base_file),
        )

        # Act & Assert
        with pytest.raises(ValueError, match="relative_to must be a directory"):
            SymlinkFileCreateHandler.apply_forward(delta)

    def test_symlink_target_already_exists(self, tmp_path):
        """Test that creating symlink when target exists raises error."""
        # Arrange
        base_dir = tmp_path / "base"
        base_dir.mkdir()
        source_file = tmp_path / "source.txt"
        source_file.write_text("test")
        target_symlink = base_dir / "link.txt"
        target_symlink.write_text("existing file")

        delta = MockDelta(
            target_path=str(target_symlink),
            symlink_target=str(source_file),
            relative_to=str(base_dir),
        )

        # Act & Assert
        with pytest.raises(FileExistsError, match="Target path already exists"):
            SymlinkFileCreateHandler.apply_forward(delta)

    def test_symlink_target_cannot_be_symlink(self, tmp_path):
        """Test that symlink target cannot itself be a symlink."""
        # Arrange
        base_dir = tmp_path / "base"
        base_dir.mkdir()
        real_file = tmp_path / "real.txt"
        real_file.write_text("real")
        intermediate_link = tmp_path / "intermediate_link.txt"
        intermediate_link.symlink_to(real_file)
        target_symlink = base_dir / "link.txt"

        delta = MockDelta(
            target_path=str(target_symlink),
            symlink_target=str(intermediate_link),
            relative_to=str(base_dir),
        )

        # Act & Assert
        with pytest.raises(ValueError, match="cannot be a symlink"):
            SymlinkFileCreateHandler.apply_forward(delta)


class TestIntegrationScenarios:
    """Integration tests for real-world scenarios."""

    def test_app_module_import_scenario(self, tmp_path):
        """
        Test the exact scenario mentioned in the user request:
        full_app_module_dir.symlink_to(os.path.relpath(import_module_dir, full_app_module_dir.parent))
        """
        # Arrange - Simulate the VAF application module structure
        project_root = tmp_path / "vaf_project"
        app_modules_dir = project_root / "app_modules"
        import_modules_dir = project_root / "import_modules"

        app_modules_dir.mkdir(parents=True)
        import_modules_dir.mkdir(parents=True)

        # Create an import module
        my_import_module = import_modules_dir / "my_library"
        my_import_module.mkdir()
        (my_import_module / "__init__.py").write_text("# library init")

        # Create app module symlink location
        full_app_module_dir = app_modules_dir / "imported_lib"

        delta = MockDelta(
            target_path=str(full_app_module_dir),
            symlink_target=str(my_import_module),
            relative_to=str(app_modules_dir),  # This is full_app_module_dir.parent
        )

        # Act
        SymlinkDirCreateHandler.apply_forward(delta)

        # Assert
        assert full_app_module_dir.is_symlink()
        link_target = Path.readlink(full_app_module_dir)
        assert not Path(link_target).is_absolute()
        assert (full_app_module_dir / "__init__.py").exists()

        # Verify the relative path is correct
        expected_relpath = os.path.relpath(my_import_module, app_modules_dir)
        assert str(link_target) == expected_relpath
