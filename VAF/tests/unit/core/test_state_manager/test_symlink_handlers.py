# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Tests for Symlink Handlers

This module contains comprehensive tests for symlink creation and deletion handlers,
including support for both absolute and relative symlinks.
"""
# mypy: disable-error-code="no-untyped-def"

from pathlib import Path
from typing import Optional

import pytest

from vaf.core.state_manager.data_handlers.symlink_handlers import (
    SymlinkDirCreateHandler,
    SymlinkDirDeleteHandler,
    SymlinkFileCreateHandler,
    SymlinkFileDeleteHandler,
    SymlinkValidator,
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


class MockDelta:
    """Mock implementation of FileDeltaInterface for testing."""

    def __init__(
        self,
        target_path: str,
        symlink_target: Optional[str] = None,
        relative_to: Optional[str] = None,
    ):
        self._target_path = target_path
        self._symlink_target = symlink_target
        self._relative_to = relative_to
        self._delta_type = MockDeltaType()
        self._processed = False

    @property
    def target_path(self) -> str:
        return self._target_path

    @property
    def symlink_target(self) -> Optional[str]:
        return self._symlink_target

    @property
    def relative_to(self) -> Optional[str]:
        return self._relative_to

    @property
    def delta_type(self) -> DeltaTypeProtocol:
        return self._delta_type

    @property
    def old_content(self) -> Optional[str]:
        return None

    @property
    def new_content(self) -> Optional[str]:
        return None

    @property
    def old_path(self) -> Optional[str]:
        return None

    @property
    def file_existed(self) -> bool:
        return False

    @property
    def timestamp(self) -> float:
        return 0.0

    @property
    def checksum(self) -> Optional[str]:
        return None

    @property
    def processed(self) -> bool:
        return self._processed

    @processed.setter
    def processed(self, value: bool) -> None:
        self._processed = value


class TestSymlinkValidator:
    """Test suite for SymlinkValidator."""

    def test_validate_symlink_target_exists(self, tmp_path: Path):
        """Test validation passes when symlink target exists."""
        target = tmp_path / "target.txt"
        target.write_text("content")

        # Should not raise
        SymlinkValidator.validate_symlink_target(target)

    def test_validate_symlink_target_not_exists(self, tmp_path: Path):
        """Test validation fails when symlink target doesn't exist."""
        target = tmp_path / "nonexistent.txt"

        with pytest.raises(ValueError, match="Invalid symlink target"):
            SymlinkValidator.validate_symlink_target(target)

    def test_validate_symlink_target_is_symlink(self, tmp_path: Path):
        """Test validation fails when symlink target is itself a symlink."""
        actual_target = tmp_path / "actual.txt"
        actual_target.write_text("content")
        symlink_target = tmp_path / "symlink.txt"
        symlink_target.symlink_to(actual_target)

        with pytest.raises(ValueError, match="cannot be a symlink"):
            SymlinkValidator.validate_symlink_target(symlink_target)


class TestSymlinkFileCreateHandler:
    """Test suite for SymlinkFileCreateHandler with absolute and relative paths."""

    def test_create_absolute_file_symlink(self, tmp_path: Path):
        """Test creating an absolute file symlink."""
        target_file = tmp_path / "target.txt"
        target_file.write_text("content")
        symlink_path = tmp_path / "link.txt"

        delta = MockDelta(
            target_path=str(symlink_path),
            symlink_target=str(target_file),
            relative_to=None,
        )

        SymlinkFileCreateHandler.apply_forward(delta)

        assert symlink_path.is_symlink()
        assert symlink_path.resolve() == target_file.resolve()
        assert symlink_path.read_text() == "content"

    def test_create_relative_file_symlink(self, tmp_path: Path):
        """Test creating a relative file symlink."""
        # Create structure: tmp_path/dir1/target.txt and tmp_path/dir2/link.txt
        dir1 = tmp_path / "dir1"
        dir2 = tmp_path / "dir2"
        dir1.mkdir()
        dir2.mkdir()

        target_file = dir1 / "target.txt"
        target_file.write_text("content")
        symlink_path = dir2 / "link.txt"

        delta = MockDelta(
            target_path=str(symlink_path),
            symlink_target=str(target_file),
            relative_to=str(dir2),
        )

        SymlinkFileCreateHandler.apply_forward(delta)

        assert symlink_path.is_symlink()
        assert symlink_path.resolve() == target_file.resolve()
        assert symlink_path.read_text() == "content"

        # Verify it's a relative symlink
        link_target = Path.readlink(symlink_path)
        assert not Path(link_target).is_absolute()
        link_target_str = str(link_target)
        assert "../dir1/target.txt" in link_target_str or "..\\dir1\\target.txt" in link_target_str

    def test_create_symlink_target_already_exists(self, tmp_path: Path):
        """Test error when target path already exists."""
        target_file = tmp_path / "target.txt"
        target_file.write_text("content")
        existing_file = tmp_path / "existing.txt"
        existing_file.write_text("exists")

        delta = MockDelta(
            target_path=str(existing_file),
            symlink_target=str(target_file),
        )

        with pytest.raises(FileExistsError, match="Target path already exists"):
            SymlinkFileCreateHandler.apply_forward(delta)

    def test_create_symlink_without_symlink_target(self, tmp_path: Path):
        """Test error when symlink_target is not specified."""
        symlink_path = tmp_path / "link.txt"

        delta = MockDelta(target_path=str(symlink_path), symlink_target=None)

        with pytest.raises(ValueError, match="Symlink target must be specified"):
            SymlinkFileCreateHandler.apply_forward(delta)

    def test_reverse_file_symlink(self, tmp_path: Path):
        """Test reversing (deleting) a file symlink."""
        target_file = tmp_path / "target.txt"
        target_file.write_text("content")
        symlink_path = tmp_path / "link.txt"
        symlink_path.symlink_to(target_file)

        delta = MockDelta(target_path=str(symlink_path))

        SymlinkFileCreateHandler.apply_reverse(delta)

        assert not symlink_path.exists()
        assert target_file.exists()  # Original file should remain


class TestSymlinkDirCreateHandler:
    """Test suite for SymlinkDirCreateHandler with absolute and relative paths."""

    def test_create_absolute_dir_symlink(self, tmp_path: Path):
        """Test creating an absolute directory symlink."""
        target_dir = tmp_path / "target_dir"
        target_dir.mkdir()
        (target_dir / "file.txt").write_text("content")
        symlink_path = tmp_path / "link_dir"

        delta = MockDelta(
            target_path=str(symlink_path),
            symlink_target=str(target_dir),
            relative_to=None,
        )

        SymlinkDirCreateHandler.apply_forward(delta)

        assert symlink_path.is_symlink()
        assert symlink_path.resolve() == target_dir.resolve()
        assert (symlink_path / "file.txt").read_text() == "content"

    def test_create_relative_dir_symlink(self, tmp_path: Path):
        """Test creating a relative directory symlink."""
        # Create structure: tmp_path/dir1/target_dir and tmp_path/dir2/link_dir
        dir1 = tmp_path / "dir1"
        dir2 = tmp_path / "dir2"
        dir1.mkdir()
        dir2.mkdir()

        target_dir = dir1 / "target_dir"
        target_dir.mkdir()
        (target_dir / "file.txt").write_text("content")
        symlink_path = dir2 / "link_dir"

        delta = MockDelta(
            target_path=str(symlink_path),
            symlink_target=str(target_dir),
            relative_to=str(dir2),
        )

        SymlinkDirCreateHandler.apply_forward(delta)

        assert symlink_path.is_symlink()
        assert symlink_path.resolve() == target_dir.resolve()
        assert (symlink_path / "file.txt").read_text() == "content"

        # Verify it's a relative symlink
        link_target = Path.readlink(symlink_path)
        assert not Path(link_target).is_absolute()

    def test_create_relative_symlink_with_complex_path(self, tmp_path: Path):
        """Test creating relative symlink with complex directory structure."""
        # Structure: tmp_path/a/b/c/target and tmp_path/x/y/link
        target_dir = tmp_path / "a" / "b" / "c" / "target"
        target_dir.mkdir(parents=True)
        (target_dir / "data.txt").write_text("data")

        link_parent = tmp_path / "x" / "y"
        link_parent.mkdir(parents=True)
        symlink_path = link_parent / "link"

        delta = MockDelta(
            target_path=str(symlink_path),
            symlink_target=str(target_dir),
            relative_to=str(link_parent),
        )

        SymlinkDirCreateHandler.apply_forward(delta)

        assert symlink_path.is_symlink()
        assert symlink_path.resolve() == target_dir.resolve()
        assert (symlink_path / "data.txt").read_text() == "data"

    def test_reverse_dir_symlink(self, tmp_path: Path):
        """Test reversing (deleting) a directory symlink."""
        target_dir = tmp_path / "target_dir"
        target_dir.mkdir()
        (target_dir / "file.txt").write_text("content")
        symlink_path = tmp_path / "link_dir"
        symlink_path.symlink_to(target_dir)

        delta = MockDelta(target_path=str(symlink_path))

        SymlinkDirCreateHandler.apply_reverse(delta)

        assert not symlink_path.exists()
        assert target_dir.exists()  # Original directory should remain
        assert (target_dir / "file.txt").exists()


class TestSymlinkFileDeleteHandler:
    """Test suite for SymlinkFileDeleteHandler."""

    def test_delete_file_symlink_forward(self, tmp_path: Path):
        """Test forward deletion of file symlink."""
        target_file = tmp_path / "target.txt"
        target_file.write_text("content")
        symlink_path = tmp_path / "link.txt"
        symlink_path.symlink_to(target_file)

        delta = MockDelta(target_path=str(symlink_path))

        SymlinkFileDeleteHandler.apply_forward(delta)

        assert not symlink_path.exists()
        assert target_file.exists()

    def test_delete_file_symlink_reverse(self, tmp_path: Path):
        """Test reverse of file symlink deletion (recreation)."""
        target_file = tmp_path / "target.txt"
        target_file.write_text("content")
        symlink_path = tmp_path / "link.txt"

        delta = MockDelta(target_path=str(symlink_path), symlink_target=str(target_file))

        SymlinkFileDeleteHandler.apply_reverse(delta)

        assert symlink_path.is_symlink()
        assert symlink_path.resolve() == target_file.resolve()


class TestSymlinkDirDeleteHandler:
    """Test suite for SymlinkDirDeleteHandler."""

    def test_delete_dir_symlink_forward(self, tmp_path: Path):
        """Test forward deletion of directory symlink."""
        target_dir = tmp_path / "target_dir"
        target_dir.mkdir()
        symlink_path = tmp_path / "link_dir"
        symlink_path.symlink_to(target_dir)

        delta = MockDelta(target_path=str(symlink_path))

        SymlinkDirDeleteHandler.apply_forward(delta)

        assert not symlink_path.exists()
        assert target_dir.exists()

    def test_delete_dir_symlink_reverse(self, tmp_path: Path):
        """Test reverse of directory symlink deletion (recreation)."""
        target_dir = tmp_path / "target_dir"
        target_dir.mkdir()
        symlink_path = tmp_path / "link_dir"

        delta = MockDelta(target_path=str(symlink_path), symlink_target=str(target_dir))

        SymlinkDirDeleteHandler.apply_reverse(delta)

        assert symlink_path.is_symlink()
        assert symlink_path.resolve() == target_dir.resolve()


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_relative_to_nonexistent_directory(self, tmp_path: Path):
        """Test behavior when relative_to points to non-existent directory."""
        target_file = tmp_path / "target.txt"
        target_file.write_text("content")
        symlink_path = tmp_path / "link.txt"
        nonexistent = tmp_path / "nonexistent"

        delta = MockDelta(
            target_path=str(symlink_path),
            symlink_target=str(target_file),
            relative_to=str(nonexistent),
        )

        # Should raise an error because relative_to must exist
        with pytest.raises(ValueError, match="relative_to path does not exist"):
            SymlinkFileCreateHandler.apply_forward(delta)

    def test_symlink_target_is_invalid(self, tmp_path: Path):
        """Test error when symlink target doesn't exist."""
        symlink_path = tmp_path / "link.txt"
        nonexistent_target = tmp_path / "nonexistent.txt"

        delta = MockDelta(
            target_path=str(symlink_path),
            symlink_target=str(nonexistent_target),
        )

        with pytest.raises(ValueError, match="Invalid symlink target"):
            SymlinkFileCreateHandler.apply_forward(delta)

    def test_circular_symlink_prevention(self, tmp_path: Path):
        """Test that we can't create a symlink pointing to itself."""
        symlink_path = tmp_path / "circular.txt"

        delta = MockDelta(
            target_path=str(symlink_path),
            symlink_target=str(symlink_path),
        )

        # This should fail because symlink_target doesn't exist yet
        with pytest.raises(ValueError, match="Invalid symlink target"):
            SymlinkFileCreateHandler.apply_forward(delta)
