# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Example tests."""
# pylint: disable=missing-param-doc
# pylint: disable=too-many-locals
# pylint: disable=unused-argument
# pylint: disable=duplicate-code

from pathlib import Path
from typing import Any, Dict, List

from vaf.core.objects import model_cmd as uut


class TestModelCmd:
    """
    Class docstrings are also parsed
    """

    def assert_two_dictionary_identical(self, dict_1: Dict[str, Any], dict_2: Dict[str, Any]) -> None:
        """Assert that two dictionaries are identical by checking contents and ignore orders"""

        def __sort_dictionary_by_key(dict_obj: Dict[str, Any]) -> Dict[str, Any]:
            return {key: dict_obj[key] for key in sorted(list(dict_obj.keys()))}

        # first assert the keys
        assert sorted(list(dict_1.keys())) == sorted(list(dict_2.keys()))
        # assert values by ignoring orders
        for key, values in dict_1.items():
            if isinstance(values, Dict):
                assert __sort_dictionary_by_key(dict_1) == __sort_dictionary_by_key(dict_2)
            elif isinstance(values, List):
                assert sorted(values) == sorted(dict_2[key])

    def test_import_vss(self, tmp_path: Path) -> None:
        """Test generate_vss function"""
        model_cmd = uut.ModelCmd()
        model_dir = tmp_path / "tmp_out"
        model_dir.mkdir(exist_ok=True)
        input_json = Path(__file__).parent / "test_data/minimal_vss.json"
        model_cmd.import_vss(str(input_json), str(model_dir))
        assert (model_dir / "vss.py").is_file()
