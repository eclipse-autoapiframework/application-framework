# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Test project CLI with minimal configuration."""
# pylint: disable=missing-param-doc
# pylint: disable=missing-any-param-doc
# mypy: disable-error-code="no-untyped-def,union-attr"

# from unittest import mock
from typing import Any, List

import pytest
from click import Group
from click.testing import Result

from vaf.entry_points.default.entry_point import model, project

from ...utils.test_helpers import TestHelpers


def __invoke_vaf_cli(
    cmds: List[str], args: List[str], cli_cmd: Group = project, with_assert: bool = True, **kwargs: Any
) -> Result:
    return TestHelpers.invoke_vaf_cli(cli_cmd, cmds, args, with_assert, **kwargs)


def test_project_init(tmp_path, monkeypatch) -> None:
    """project init"""
    monkeypatch.chdir(tmp_path)
    __invoke_vaf_cli(["init", "integration"], ["-n", "dummy_integration", "-p", "."])
    __invoke_vaf_cli(["init", "interface"], ["-n", "dummy_inteface", "-p", "."])
    __invoke_vaf_cli(["init", "app-module"], ["-n", "dummy_am", "--namespace", "duh", "-p", "."])


def test_project_create_remove(tmp_path, monkeypatch) -> None:
    """project create & remove app module"""
    monkeypatch.chdir(tmp_path)
    __invoke_vaf_cli(["init", "integration"], ["-n", "dummy", "-p", "."])

    monkeypatch.chdir(tmp_path / "dummy")
    result = __invoke_vaf_cli(["create", "app-module"], ["-n", "beng", "--namespace", "duh", "-p", "."])
    assert "App-Module duh::beng will be stored in model/vaf" in result.output
    assert (tmp_path / "dummy/src/application_modules/beng").is_dir()

    # remove prompt_required from model_dir
    model_dir = project.commands["remove"].commands["app-module"].params[2]  # type:ignore[attr-defined]
    assert model_dir.name == "model_dir"
    model_dir.prompt_required = False
    __invoke_vaf_cli(["remove", "app-module"], ["-n", "beng", "-p", "."])
    assert not (tmp_path / "dummy/src/application_modules/beng").is_dir()


@pytest.mark.slow
def test_project_generate(tmp_path, monkeypatch) -> None:
    """project generate"""
    monkeypatch.chdir(tmp_path)
    __invoke_vaf_cli(["init", "integration"], ["-n", "dummy", "-p", "."])

    monkeypatch.chdir(tmp_path / "dummy")
    # use default
    __invoke_vaf_cli(["generate"], ["-t", "std"], input="prj")


def test_project_import(tmp_path, monkeypatch) -> None:
    """project import"""

    ## app module
    monkeypatch.chdir(tmp_path)
    __invoke_vaf_cli(["init", "app-module"], ["-n", "megon", "--namespace", "duh", "-p", "."])
    __invoke_vaf_cli(["init", "interface"], ["-n", "gala", "-p", "."])
    monkeypatch.chdir(tmp_path / "gala")
    __invoke_vaf_cli(["generate"], [], cli_cmd=model)

    monkeypatch.chdir(tmp_path / "megon")

    __invoke_vaf_cli(["import"], ["--input-file", "../gala/export/gala.json"])

    ## integration project
    monkeypatch.chdir(tmp_path)
    __invoke_vaf_cli(["init", "integration"], ["-n", "dummy", "-p", "."])

    monkeypatch.chdir(tmp_path / "dummy")

    __invoke_vaf_cli(["import"], ["--input-dir", "../megon"])
