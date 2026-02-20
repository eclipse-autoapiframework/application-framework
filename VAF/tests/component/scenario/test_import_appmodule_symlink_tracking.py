# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Test scenarios for import_appmodule with absolute and relative symlinks

This test verifies that import_appmodule correctly creates absolute or relative
symlinks based on whether the import path is absolute or relative.
"""
# mypy: disable-error-code="no-untyped-def,union-attr"
# pylint: disable=missing-any-param-doc
# pylint: disable=duplicate-code

import os
import subprocess
from pathlib import Path
from typing import List

from click import Group
from click.testing import Result

from vaf.entry_points.default.entry_point import project

from ...utils.test_helpers import TestHelpers


def __invoke_vaf_cli(cmds: List[str], args: List[str], cli_cmd: Group = project, with_assert: bool = True) -> Result:
    return TestHelpers.invoke_vaf_cli(cli_cmd, cmds, args, with_assert)


def test_import_appmodule_with_absolute_path_creates_absolute_symlink(tmp_path, monkeypatch) -> None:
    """
    Test that importing an app module using an absolute path creates an absolute symlink.
    This can be verified using 'ls -la' which shows the symlink target.
    """
    monkeypatch.chdir(tmp_path)

    # Create integration project
    __invoke_vaf_cli(["init", "integration"], ["-n", "IntegrationPrj", "-p", "."])
    integration_dir = tmp_path / "IntegrationPrj"

    # Create external app module to import
    external_module_dir = tmp_path / "external_modules" / "MyExternalModule"
    external_module_dir.mkdir(parents=True)

    # Create app module using CLI
    monkeypatch.chdir(tmp_path / "external_modules")
    __invoke_vaf_cli(["init", "app-module"], ["-n", "MyExternalModule", "--namespace", "ext::mymodule", "-p", "."])

    # Import with ABSOLUTE path
    monkeypatch.chdir(integration_dir)
    absolute_import_path = str(external_module_dir.resolve())

    # Import may fail at generate step, but symlink should be created
    __invoke_vaf_cli(
        ["import"],
        ["--input-dir", absolute_import_path, "-p", ".", "-m", "model/vaf"],
        with_assert=False,  # Don't assert success - we only care about symlink type
    )

    # Check symlink was created
    symlink_path = integration_dir / "src" / "application_modules" / "my_external_module"
    assert symlink_path.exists(), "Symlink should be created"
    assert symlink_path.is_symlink(), "Should be a symlink"

    # Verify with ls -la that the target is absolute
    result = subprocess.run(
        ["ls", "-la", str(symlink_path)], capture_output=True, text=True, check=True, cwd=str(integration_dir)
    )

    ls_output = result.stdout.strip()
    assert "-> /" in ls_output, f"ls -la should show symlink arrow: {ls_output}"

    # Extract target from ls output
    target_in_ls = ls_output.split("->")[-1].strip()

    # Absolute path starts with /
    assert target_in_ls.startswith("/"), (
        f"Symlink target should be absolute (start with /). ls -la shows: {target_in_ls}"
    )

    # Also verify with readlink
    link_target = Path.readlink(symlink_path)
    assert Path(link_target).is_absolute(), f"readlink should show absolute path: {link_target}"


def test_import_appmodule_with_relative_path_creates_relative_symlink(tmp_path, monkeypatch) -> None:
    """
    Test that importing an app module using a relative path creates a relative symlink.
    This can be verified using 'ls -la' which shows the symlink target.
    """
    monkeypatch.chdir(tmp_path)

    # Create integration project
    __invoke_vaf_cli(["init", "integration"], ["-n", "IntegrationPrj", "-p", "."])
    integration_dir = tmp_path / "IntegrationPrj"

    # Create external app module to import (as sibling directory)
    external_module_dir = tmp_path / "shared" / "MySharedModule"
    external_module_dir.mkdir(parents=True)

    # Create app module using CLI
    monkeypatch.chdir(tmp_path / "shared")
    __invoke_vaf_cli(["init", "app-module"], ["-n", "MySharedModule", "--namespace", "shared::mymodule", "-p", "."])

    # Import with RELATIVE path (must be relative to integration_dir)
    monkeypatch.chdir(integration_dir)
    relative_import_path = os.path.relpath(external_module_dir, integration_dir)

    # Ensure it's actually relative
    assert not Path(relative_import_path).is_absolute(), (
        f"Test setup error: path should be relative: {relative_import_path}"
    )

    # Import may fail at generate step, but symlink should be created
    __invoke_vaf_cli(
        ["import"],
        ["--input-dir", relative_import_path, "-p", ".", "-m", "model/vaf"],
        with_assert=False,  # Don't assert success - we only care about symlink type
    )

    # Check symlink was created
    symlink_path = integration_dir / "src" / "application_modules" / "my_shared_module"
    assert symlink_path.exists(), "Symlink should be created"
    assert symlink_path.is_symlink(), "Should be a symlink"

    # Verify with ls -la that the target is relative
    result = subprocess.run(
        ["ls", "-la", str(symlink_path)], capture_output=True, text=True, check=True, cwd=str(integration_dir)
    )

    ls_output = result.stdout.strip()
    assert "-> ../" in ls_output, f"ls -la should show symlink arrow: {ls_output}"

    # Extract target from ls output
    target_in_ls = ls_output.split("->")[-1].strip()

    # Relative path does NOT start with /
    assert not target_in_ls.startswith("/"), (
        f"Symlink target should be relative (NOT start with /). ls -la shows: {target_in_ls}"
    )

    # Also verify with readlink
    link_target = str(Path.readlink(symlink_path))
    assert not Path(link_target).is_absolute(), f"readlink should show relative path: {link_target}"

    # Should contain .. for parent directory traversal
    assert ".." in link_target, f"Relative path should use '..' for parent traversal: {link_target}"


def test_import_appmodule_symlinks_resolve_correctly(tmp_path, monkeypatch) -> None:
    """
    Test that both absolute and relative symlinks resolve to the correct target.
    """
    monkeypatch.chdir(tmp_path)

    # Create integration project
    __invoke_vaf_cli(["init", "integration"], ["-n", "TestPrj", "-p", "."])
    integration_dir = tmp_path / "TestPrj"

    # Create two external modules
    abs_module_dir = tmp_path / "absolute_module"
    abs_module_dir.mkdir()

    rel_module_dir = tmp_path / "relative_module"
    rel_module_dir.mkdir()

    # Create modules
    monkeypatch.chdir(abs_module_dir.parent)
    __invoke_vaf_cli(
        ["init", "app-module"], ["-n", "absolute_module", "--namespace", "abs", "-p", str(abs_module_dir.parent)]
    )

    monkeypatch.chdir(rel_module_dir.parent)
    __invoke_vaf_cli(
        ["init", "app-module"], ["-n", "relative_module", "--namespace", "rel", "-p", str(rel_module_dir.parent)]
    )

    # Import with absolute path
    monkeypatch.chdir(integration_dir)
    # Import may fail at generate step, but symlink should be created
    __invoke_vaf_cli(
        ["import"], ["--input-dir", str(abs_module_dir.resolve()), "-p", ".", "-m", "model/vaf"], with_assert=False
    )

    # Import with relative path
    rel_path = os.path.relpath(rel_module_dir, integration_dir)
    __invoke_vaf_cli(["import"], ["--input-dir", rel_path, "-p", ".", "-m", "model/vaf"], with_assert=False)

    # Both symlinks should resolve to correct targets
    abs_symlink = integration_dir / "src" / "application_modules" / "absolute_module"
    rel_symlink = integration_dir / "src" / "application_modules" / "relative_module"

    # Check that symlinks exist
    assert abs_symlink.exists(), "Absolute symlink should be created"
    assert rel_symlink.exists(), "Relative symlink should be created"

    assert abs_symlink.is_symlink(), "Should be a symlink"
    assert rel_symlink.is_symlink(), "Should be a symlink"

    # Check symlink types
    abs_link_target = Path.readlink(abs_symlink)
    rel_link_target = Path.readlink(rel_symlink)

    assert Path(abs_link_target).is_absolute(), "Absolute import should create absolute symlink"
    assert not Path(rel_link_target).is_absolute(), "Relative import should create relative symlink"
