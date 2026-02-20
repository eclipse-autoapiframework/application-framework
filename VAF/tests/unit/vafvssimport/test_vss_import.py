# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Example tests."""

from pathlib import Path

from vaf.vafvssimport.vss_import import run_import

# pylint: disable=too-few-public-methods
# pylint: disable=duplicate-code
# pylint: disable=missing-param-doc
# pylint: disable=missing-type-doc
# mypy: disable-error-code="no-untyped-def"


class TestUnit:
    """Basic generation test class"""

    def test_run_import(self, tmp_path) -> None:
        """Basic test for interface generation"""

        run_import(str(tmp_path), str(Path(__file__).parent / "test_data/minimal_vss.json"))

        assert (tmp_path / "vss-derived-model.json").is_file()
