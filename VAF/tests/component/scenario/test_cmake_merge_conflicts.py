# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Test CMake merging."""
# mypy: disable-error-code="no-untyped-def,union-attr"
# pylint: disable=missing-any-param-doc
# pylint: disable=duplicate-code

from pathlib import Path
from shutil import copyfile
from typing import List

from click import Group
from click.testing import Result

from vaf.entry_points.default.entry_point import project

from ...utils.test_helpers import TestHelpers


def __invoke_vaf_cli(cmds: List[str], args: List[str], cli_cmd: Group = project, with_assert: bool = True) -> Result:
    return TestHelpers.invoke_vaf_cli(cli_cmd, cmds, args, with_assert)


test_data_dir = Path(__file__).parent.parent / "test_data/cmake_conflicts"


def test_cmake_conflict_merge(tmp_path, monkeypatch) -> None:
    """CMake conflict merge somehow"""
    monkeypatch.chdir(tmp_path)
    __invoke_vaf_cli(["init", "integration"], ["-n", "MyProject", "-p", "."])
    monkeypatch.chdir(tmp_path / "MyProject")
    __invoke_vaf_cli(["create", "app-module"], ["-n", "Module1", "--namespace", "dixi", "-p", "."])
    __invoke_vaf_cli(["create", "app-module"], ["-n", "Module2", "--namespace", "dixi", "-p", "."])
    __invoke_vaf_cli(["create", "app-module"], ["-n", "Module3", "--namespace", "dixi", "-p", "."])

    copyfile(test_data_dir / "my_project.py", "model/vaf/my_project.py")
    # initial project generate
    __invoke_vaf_cli(["generate"], ["-t", "std", "--skip-make-preset", "--mode", "prj"])

    # user removes Module3 manually from CMakeList
    copyfile(test_data_dir / "CMakeLists.txt", "src/application_modules/CMakeLists.txt")
    # then call vaf remove app-module
    __invoke_vaf_cli(
        ["remove", "app-module"],
        [
            "-n",
            "Module3",
            "-p",
            ".",
            "-m",
            "model/vaf",
            "--app-modules",
            f"{Path.cwd()}/src/application_modules/module3",
        ],
    )
    # then add a new app module
    __invoke_vaf_cli(["create", "app-module"], ["-n", "Module4", "--namespace", "dixi", "-p", "."])
    # update model ofc
    copyfile(test_data_dir / "my_project1.py", "model/vaf/my_project.py")
    # initial project generate

    res = __invoke_vaf_cli(["generate"], ["-t", "std", "--skip-make-preset", "--mode", "prj"])
    goal_str = """\nMERGE WARNING:
    Merge of src/application_modules/CMakeLists.txt.new~ with src/application_modules/CMakeLists.txt has conflicts!"""
    assert goal_str in res.stdout
