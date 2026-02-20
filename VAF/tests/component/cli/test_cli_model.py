# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Test model CLI with minimal configuration."""
# pylint: disable=missing-param-doc
# pylint: disable=missing-any-param-doc
# pylint: disable=duplicate-code
# mypy: disable-error-code="no-untyped-def,union-attr"

# from unittest import mock
from pathlib import Path
from shutil import copyfile
from typing import List

from click import Group
from click.testing import Result

from vaf.entry_points.default.entry_point import model, project

from ...utils.test_helpers import TestHelpers


def __invoke_vaf_cli(cmds: List[str], args: List[str], cli_cmd: Group = model, with_assert: bool = True) -> Result:
    return TestHelpers.invoke_vaf_cli(cli_cmd, cmds, args, with_assert)


path_to_data = Path(__file__).parent.parent / "test_data"


def test_model_import_vss(tmp_path, monkeypatch) -> None:
    """model import vss"""
    monkeypatch.chdir(tmp_path)
    __invoke_vaf_cli(
        ["init", "app-module"],
        ["-n", "dummy", "--namespace", "duh", "-p", "."],
        cli_cmd=project,
    )
    monkeypatch.chdir("dummy")

    # run platform derive without generating
    __invoke_vaf_cli(["import", "vss"], ["-i", (path_to_data / "vss.json").as_posix()])
    assert (Path.cwd() / "model/vss-derived-model.json").is_file()


def test_model_generate_update(tmp_path, monkeypatch) -> None:
    """model generate & update"""
    monkeypatch.chdir(tmp_path)
    __invoke_vaf_cli(["init", "integration"], ["-n", "dummy", "-p", "."], cli_cmd=project)
    __invoke_vaf_cli(["init", "interface"], ["-n", "inti", "-p", "."], cli_cmd=project)
    __invoke_vaf_cli(
        ["init", "app-module"],
        ["-n", "grop", "--namespace", "duh", "-p", "."],
        cli_cmd=project,
    )
    base_path = Path.cwd()

    # interface prj
    monkeypatch.chdir("inti")
    __invoke_vaf_cli(["generate"], [])
    assert Path("export/inti.json").is_file()

    # app module project
    monkeypatch.chdir(base_path / "grop")

    test_data_dir = Path(__file__).parent.parent / "test_data"
    copyfile(
        test_data_dir / "grop.py",
        base_path / "grop" / "model" / "grop.py",
    )
    # plain
    __invoke_vaf_cli(["generate"], [])
    assert Path("model/model.json").is_file()
    # with import interface
    __invoke_vaf_cli(["import"], ["--input-file", "../inti/export/inti.json"], cli_cmd=project)
    __invoke_vaf_cli(["generate"], [])
    assert Path("model/imported_models/_imported_models.json").is_file()
    assert Path("model/imported_models/inti.json").is_file()
    assert Path("model/imported_models/inti.py").is_file()
    __invoke_vaf_cli(["update"], [])

    monkeypatch.chdir(base_path / "dummy")
    __invoke_vaf_cli(["generate"], [])
    assert Path("model/vaf/model.json").is_file()

    __invoke_vaf_cli(["import"], ["--input-dir", "../grop"], cli_cmd=project)
    __invoke_vaf_cli(["generate"], [])
    assert Path("model/vaf/application_modules/import_grop.py").is_file()
    # can't test vaf model update for integration project, since click.Choice can't be tested in CliRunner
    # __invoke_vaf_cli(["update"], [])
