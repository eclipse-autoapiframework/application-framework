# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Example tests."""

from pathlib import Path

import pytest

from vaf import vafmodel
from vaf.vafgeneration import vaf_generate_project

# pylint: disable=too-few-public-methods
# pylint: disable=duplicate-code
# pylint: disable=missing-param-doc
# pylint: disable=missing-type-doc
# mypy: disable-error-code="no-untyped-def"


class TestIntegration:
    """Basic generation test class"""

    def test_get_ecosystems(self) -> None:
        """Basic test for get_ecosystems function"""
        project_path = str(Path(__file__).parent.parent.parent.parent.parent)

        test_dict = {
            "SILKIT": "VAF/tests/unit/vafgeneration/input_model_examples/silkit.json",
        }

        for ecosystem_name, ecosystem_mock_data in test_dict.items():
            main_model = vafmodel.load_json(f"{project_path}/{ecosystem_mock_data}")
            assert [ecosystem_name] == vaf_generate_project.get_ecosystems(main_model)

    @pytest.mark.slow
    def test_basic_generation(self, tmp_path) -> None:
        """Basic test for interface generation

        Raises:
            FileNotFoundError: Raised if conanfile not present
            ValueError: Raised if package not found

        """

        project_path = str(Path(__file__).parent.parent.parent.parent.parent)

        test_dict = {
            "SILKIT": {
                "mock_data": "VAF/tests/unit/vafgeneration/input_model_examples/silkit.json",
                "not_exist_list": [
                    "vaf",
                ],  # platform_vaf should also not generated due to empty app modules
            },
        }

        for ecosystem_test_data in test_dict.values():
            vaf_generate_project.generate_integration_project(
                f"{project_path}/{ecosystem_test_data['mock_data']}",
                str(tmp_path),
                "std",
            )

            for i_must_not_exist in ecosystem_test_data["not_exist_list"]:
                assert not Path(f"{tmp_path}/src-gen/libs/platform_{i_must_not_exist}").is_dir(), (
                    f"{tmp_path}/src-gen/libs/platform_{i_must_not_exist}"
                )
