# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Tests for TrailSheriff Relative Symlink Support

This test suite follows TDD principles to ensure that the TrailSheriff tracker
correctly supports relative symlinks through the updated create_file_symlink and
create_dir_symlink methods.
"""
# mypy: disable-error-code="no-untyped-def"

import os
from pathlib import Path

from vaf.core.state_manager.tracker import TrailSheriff


class TestTrailSheriffFileSymlinkRelative:
    """Test TrailSheriff file symlink tracking with relative paths."""

    def test_create_file_symlink_absolute_backward_compatible(self, tmp_path: Path):
        """Test that absolute file symlinks still work (backward compatibility)."""
        # Arrange
        tracker = TrailSheriff("Test absolute file symlink")
        source_file = tmp_path / "source.txt"
        source_file.write_text("test content")
        target_symlink = tmp_path / "link.txt"

        # Act
        tracker.create_file_symlink(
            target_path=target_symlink,
            symlink_target=source_file,
            processed=True,  # Mark as processed to avoid actual creation
        )

        # Assert
        assert len(tracker.deltas) == 1
        delta = tracker.deltas[0]
        assert delta.target_path == str(target_symlink)
        assert delta.symlink_target == str(source_file)
        assert delta.relative_to is None  # Should be None for absolute symlinks

    def test_create_file_symlink_with_relative_to(self, tmp_path: Path):
        """Test creating file symlink with relative_to parameter."""
        # Arrange
        tracker = TrailSheriff("Test relative file symlink")
        base_dir = tmp_path / "base"
        base_dir.mkdir()
        source_file = tmp_path / "source" / "file.txt"
        source_file.parent.mkdir()
        source_file.write_text("relative content")
        target_symlink = base_dir / "link.txt"

        # Act
        tracker.create_file_symlink(
            target_path=target_symlink, symlink_target=source_file, relative_to=base_dir, processed=True
        )

        # Assert
        assert len(tracker.deltas) == 1
        delta = tracker.deltas[0]
        assert delta.target_path == str(target_symlink)
        assert delta.symlink_target == str(source_file)
        assert delta.relative_to == str(base_dir)

    def test_create_file_symlink_relative_integration(self, tmp_path: Path):
        """Test end-to-end file symlink creation with relative path."""
        # Arrange
        tracker = TrailSheriff("Test relative file symlink E2E")
        base_dir = tmp_path / "base"
        base_dir.mkdir()
        source_file = tmp_path / "source" / "file.txt"
        source_file.parent.mkdir()
        source_file.write_text("integration test")
        target_symlink = base_dir / "link.txt"

        # Act - Track and apply
        tracker.create_file_symlink(
            target_path=target_symlink,
            symlink_target=source_file,
            relative_to=base_dir,
            processed=False,  # Will actually create the symlink
        )

        # Apply the delta
        tracker.deltas[0].delta_type.apply_forward(tracker.deltas[0])

        # Assert
        assert target_symlink.is_symlink()
        link_target = Path.readlink(target_symlink)
        assert not Path(link_target).is_absolute()  # Should be relative
        assert target_symlink.resolve() == source_file.resolve()
        assert target_symlink.read_text() == "integration test"

    def test_create_file_symlink_none_relative_to_uses_absolute(self, tmp_path: Path):
        """Test that passing relative_to=None creates absolute symlink."""
        # Arrange
        tracker = TrailSheriff("Test explicit None")
        source_file = tmp_path / "source.txt"
        source_file.write_text("content")
        target_symlink = tmp_path / "link.txt"

        # Act
        tracker.create_file_symlink(
            target_path=target_symlink, symlink_target=source_file, relative_to=None, processed=True
        )

        # Assert
        delta = tracker.deltas[0]
        assert delta.relative_to is None


class TestTrailSheriffDirSymlinkRelative:
    """Test TrailSheriff directory symlink tracking with relative paths."""

    def test_create_dir_symlink_absolute_backward_compatible(self, tmp_path: Path):
        """Test that absolute directory symlinks still work (backward compatibility)."""
        # Arrange
        tracker = TrailSheriff("Test absolute dir symlink")
        source_dir = tmp_path / "source_dir"
        source_dir.mkdir()
        (source_dir / "file.txt").write_text("content")
        target_symlink = tmp_path / "link_dir"

        # Act
        tracker.create_dir_symlink(target_path=target_symlink, symlink_target=source_dir, processed=True)

        # Assert
        assert len(tracker.deltas) == 1
        delta = tracker.deltas[0]
        assert delta.target_path == str(target_symlink)
        assert delta.symlink_target == str(source_dir)
        assert delta.relative_to is None

    def test_create_dir_symlink_with_relative_to(self, tmp_path: Path):
        """Test creating directory symlink with relative_to parameter."""
        # Arrange
        tracker = TrailSheriff("Test relative dir symlink")
        base_dir = tmp_path / "base"
        base_dir.mkdir()
        source_dir = tmp_path / "modules" / "my_module"
        source_dir.mkdir(parents=True)
        (source_dir / "code.py").write_text("print('hello')")
        target_symlink = base_dir / "module_link"

        # Act
        tracker.create_dir_symlink(
            target_path=target_symlink, symlink_target=source_dir, relative_to=base_dir, processed=True
        )

        # Assert
        assert len(tracker.deltas) == 1
        delta = tracker.deltas[0]
        assert delta.target_path == str(target_symlink)
        assert delta.symlink_target == str(source_dir)
        assert delta.relative_to == str(base_dir)

    def test_create_dir_symlink_relative_integration(self, tmp_path: Path):
        """Test end-to-end directory symlink creation with relative path."""
        # Arrange
        tracker = TrailSheriff("Test relative dir symlink E2E")
        base_dir = tmp_path / "app_modules"
        base_dir.mkdir()
        source_dir = tmp_path / "import_modules" / "my_library"
        source_dir.mkdir(parents=True)
        (source_dir / "__init__.py").write_text("# library init")
        target_symlink = base_dir / "imported_lib"

        # Act - Track and apply
        tracker.create_dir_symlink(
            target_path=target_symlink, symlink_target=source_dir, relative_to=base_dir, processed=False
        )

        # Apply the delta
        tracker.deltas[0].delta_type.apply_forward(tracker.deltas[0])

        # Assert
        assert target_symlink.is_symlink()
        link_target = Path.readlink(target_symlink)
        assert not Path(link_target).is_absolute()  # Should be relative
        assert target_symlink.resolve() == source_dir.resolve()
        assert (target_symlink / "__init__.py").exists()

    def test_create_dir_symlink_complex_nested_structure(self, tmp_path: Path):
        """Test relative directory symlink with complex nested structure."""
        # Arrange
        tracker = TrailSheriff("Test nested structure")
        app_dir = tmp_path / "app" / "imports"
        lib_dir = tmp_path / "shared" / "libraries" / "lib"
        app_dir.mkdir(parents=True)
        lib_dir.mkdir(parents=True)
        (lib_dir / "module.py").write_text("# library module")
        target_symlink = app_dir / "lib_link"

        # Act
        tracker.create_dir_symlink(
            target_path=target_symlink, symlink_target=lib_dir, relative_to=app_dir, processed=False
        )

        # Apply
        tracker.deltas[0].delta_type.apply_forward(tracker.deltas[0])

        # Assert
        assert target_symlink.is_symlink()
        assert target_symlink.is_dir()
        link_target = Path.readlink(target_symlink)
        assert not Path(link_target).is_absolute()
        assert (target_symlink / "module.py").exists()


class TestTrailSheriffSymlinkFinalize:
    """Test that tracked symlinks can be finalized and applied."""

    def test_finalize_file_symlink_with_relative_to(self, tmp_path: Path):
        """Test finalizing and recording a file symlink operation."""
        # Arrange
        tracker = TrailSheriff("Finalize file symlink test")
        base_dir = tmp_path / "base"
        base_dir.mkdir()
        source_file = tmp_path / "source.txt"
        source_file.write_text("test")
        target_symlink = base_dir / "link.txt"

        # Act
        tracker.create_file_symlink(
            target_path=target_symlink, symlink_target=source_file, relative_to=base_dir, processed=False
        )

        # Apply before finalize
        tracker.deltas[0].delta_type.apply_forward(tracker.deltas[0])
        tracker.deltas[0].processed = True  # Mark as processed to avoid double-application

        # Finalize
        tracker.finalize()

        # Assert - just check symlink was created
        assert target_symlink.is_symlink()
        assert str(Path.readlink(target_symlink)) == os.path.relpath(source_file, base_dir)

    def test_finalize_dir_symlink_with_relative_to(self, tmp_path: Path):
        """Test finalizing and recording a directory symlink operation."""
        # Arrange
        tracker = TrailSheriff("Finalize dir symlink test")
        base_dir = tmp_path / "base"
        base_dir.mkdir()
        source_dir = tmp_path / "source_dir"
        source_dir.mkdir()
        target_symlink = base_dir / "link_dir"

        # Act
        tracker.create_dir_symlink(
            target_path=target_symlink, symlink_target=source_dir, relative_to=base_dir, processed=False
        )

        # Apply before finalize
        tracker.deltas[0].delta_type.apply_forward(tracker.deltas[0])
        tracker.deltas[0].processed = True  # Mark as processed to avoid double-application

        # Finalize
        tracker.finalize()

        # Assert - just check symlink was created
        assert target_symlink.is_symlink()
        assert str(Path.readlink(target_symlink)) == os.path.relpath(source_dir, base_dir)


class TestTrailSheriffSymlinkUndo:
    """Test undo functionality with relative symlinks."""

    def test_undo_relative_file_symlink(self, tmp_path: Path):
        """Test undoing a relative file symlink creation."""
        # Arrange
        tracker = TrailSheriff("Undo file symlink test")
        base_dir = tmp_path / "base"
        base_dir.mkdir()
        source_file = tmp_path / "source.txt"
        source_file.write_text("test")
        target_symlink = base_dir / "link.txt"

        # Act - Create and finalize symlink
        tracker.create_file_symlink(
            target_path=target_symlink, symlink_target=source_file, relative_to=base_dir, processed=False
        )
        tracker.deltas[0].delta_type.apply_forward(tracker.deltas[0])
        tracker.deltas[0].processed = True  # Mark as processed to avoid double-application
        tracker.finalize()

        assert target_symlink.is_symlink()

        # Undo - directly apply reverse
        tracker.deltas[0].delta_type.apply_reverse(tracker.deltas[0])

        # Assert
        assert not target_symlink.exists()
        assert source_file.exists()  # Source should still exist

    def test_undo_relative_dir_symlink(self, tmp_path: Path):
        """Test undoing a relative directory symlink creation."""
        # Arrange
        tracker = TrailSheriff("Undo dir symlink test")
        base_dir = tmp_path / "base"
        base_dir.mkdir()
        source_dir = tmp_path / "source_dir"
        source_dir.mkdir()
        (source_dir / "file.txt").write_text("content")
        target_symlink = base_dir / "link_dir"

        # Act - Create and finalize symlink
        tracker.create_dir_symlink(
            target_path=target_symlink, symlink_target=source_dir, relative_to=base_dir, processed=False
        )
        tracker.deltas[0].delta_type.apply_forward(tracker.deltas[0])
        tracker.deltas[0].processed = True  # Mark as processed to avoid double-application
        tracker.finalize()

        assert target_symlink.is_symlink()

        # Undo - directly apply reverse
        tracker.deltas[0].delta_type.apply_reverse(tracker.deltas[0])

        # Assert
        assert not target_symlink.exists()
        assert source_dir.exists()  # Source should still exist
        assert (source_dir / "file.txt").exists()
