# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Test model CLI with minimal configuration."""
# pylint: disable=missing-param-doc
# pylint: disable=missing-any-param-doc
# pylint: disable=duplicate-code
# mypy: disable-error-code="no-untyped-def,union-attr"

# from unittest import mock
from pathlib import Path
from typing import List

import pytest
from click import Group
from click.testing import Result

from vaf.entry_points.default.entry_point import make, project

from ...utils.test_helpers import TestHelpers


def __invoke_vaf_cli(cmds: List[str], args: List[str], cli_cmd: Group = make, with_assert: bool = True) -> Result:
    return TestHelpers.invoke_vaf_cli(cli_cmd, cmds, args, with_assert)


path_to_data = Path(__file__).parent.parent / "test_data"


@pytest.mark.slow
def test_make(tmp_path, monkeypatch) -> None:
    """all make commands"""
    monkeypatch.chdir(tmp_path)
    # init integration
    __invoke_vaf_cli(["init", "integration"], ["-n", "dummy", "-p", "."], cli_cmd=project)
    monkeypatch.chdir("dummy")
    # make preset
    __invoke_vaf_cli(["preset"], [])
    # make build
    __invoke_vaf_cli(["build"], [])
    # make install
    __invoke_vaf_cli(["install"], [])
    # make clean
    __invoke_vaf_cli(["clean"], [])
    # make clean all
    __invoke_vaf_cli(["clean", "all"], [])
