# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Test platform CLI with minimal configuration."""
# pylint: disable=missing-param-doc
# pylint: disable=missing-any-param-doc
# mypy: disable-error-code="no-untyped-def"

# from unittest import mock
from pathlib import Path
from typing import List

from click import Group
from click.testing import Result

from vaf.entry_points.default.entry_point import platform

from ...utils.test_helpers import TestHelpers


def __invoke_vaf_cli(
    cmds: List[str],
    args: List[str],
    cli_cmd: Group = platform,
    with_assert: bool = True,
) -> Result:
    return TestHelpers.invoke_vaf_cli(cli_cmd, cmds, args, with_assert)


path_to_data = Path(__file__).parent.parent / "test_data"
