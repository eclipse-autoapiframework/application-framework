# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Application module generator."""

import filecmp

# pylint: disable=too-few-public-methods
# pylint: disable=duplicate-code
# pylint: disable=missing-param-doc
# pylint: disable=missing-type-doc
# pylint: disable=line-too-long
# pylint: disable=missing-function-docstring
# mypy: disable-error-code="no-untyped-def, no-untyped-call"
from pathlib import Path
from shutil import copyfile
from typing import Dict

from vaf.core.common.constants import SUFFIX
from vaf.core.common.utils import concat_str_to_path
from vaf.core.objects import project_cmd, project_init_cmd
from vaf.vafgeneration.vaf_generate_application_module import (
    generate_application_module,
)
from vaf.vafgeneration.vaf_generate_common import (
    __file_has_conflict,
    __get_ancestor_file_rel_path,
    __get_newly_generated_file_path,
)


def get_newly_generated_file_path(*args, **kwargs):
    return __get_newly_generated_file_path(*args, **kwargs)


def file_has_conflict(*args, **kwargs):
    return __file_has_conflict(*args, **kwargs)


def get_ancestor_file_rel_path(*args, **kwargs):
    return __get_ancestor_file_rel_path(*args, **kwargs)


class TestRegenerationMerge:
    """Testing regeneration in app module project"""

    ut_mock_data_path = Path(__file__).parent / "merge_strategy"
    model_rel_out_path = "model/model.json"
    cpp_rel_path = "implementation/src/sensor_fusion.cpp"
    h_rel_path = "implementation/include/nsapplicationunit/nssensorfusion/sensor_fusion.h"
    ut_h_rel_path = "implementation/test/unittest/include/nsapplicationunit/nssensorfusion/sensor_fusion_base.h"
    cmake_rel_path = "implementation/CMakeLists.txt"
    prj_cmd = project_cmd.ProjectCmd()
    prj_init_cmd = project_init_cmd.ProjectInitCmd()
    int_to_ordinal_dict: Dict[int, str] = {1: "first", 2: "second"}

    def _update_model_json(self, path_new_json: Path, path_old_json: Path) -> None:
        # simulate regeneration: current model.json -> model.json~
        copyfile(
            path_old_json,
            concat_str_to_path(path_old_json, "~"),
        )
        # copy new model
        copyfile(
            path_new_json,
            path_old_json,
        )

    def _compare_file_with_conflict(self, gen_file_path: Path, goal_file_path: Path, workspace_path: Path) -> bool:
        with open(gen_file_path, "r", encoding="utf-8") as gen_file:
            with open(goal_file_path, "r", encoding="utf-8") as goal_file:
                assert gen_file.read() == goal_file.read().replace("{TMP_PATH}", str(workspace_path))
                return True

    def _generate(self, out_path: Path, disable_auto_merge: bool = False) -> None:
        generate_application_module(
            str(out_path / "SensorFusion" / self.model_rel_out_path),
            str(out_path / "SensorFusion"),
            "SILKIT",
            execute_merge=not disable_auto_merge,
        )

    def _prerun_test_merge_regeneration(self, out_path: Path, cycle: int, edited_source: bool = True) -> None:
        # init stuffs only needed in first cycle:
        if cycle == 1:
            # create app module project
            self.prj_init_cmd.app_module_project_init(
                "NsApplicationUnit::NsSensorFusion", "SensorFusion", str(out_path)
            )

            # copy model_base.json
            copyfile(
                self.ut_mock_data_path / "model_base.json",
                out_path / "SensorFusion" / self.model_rel_out_path,
            )

            # vaf project generate model base
            self._generate(out_path)

        if edited_source:
            # simulate user editing cpp & h implementations & ut
            copyfile(
                self.ut_mock_data_path
                / f"{self.int_to_ordinal_dict[cycle]}_cycle_editing"
                / "sensor_fusion_edited.cpp",
                out_path / "SensorFusion" / self.cpp_rel_path,
            )
            copyfile(
                self.ut_mock_data_path / f"{self.int_to_ordinal_dict[cycle]}_cycle_editing" / "sensor_fusion_edited.h",
                out_path / "SensorFusion" / self.h_rel_path,
            )
            copyfile(
                self.ut_mock_data_path
                / f"{self.int_to_ordinal_dict[cycle]}_cycle_editing"
                / "sensor_fusion_base_test_edited.h",
                out_path / "SensorFusion" / self.ut_h_rel_path,
            )
            if (
                self.ut_mock_data_path / f"{self.int_to_ordinal_dict[cycle]}_cycle_editing" / "CMakeLists.txt"
            ).is_file():
                copyfile(
                    self.ut_mock_data_path / f"{self.int_to_ordinal_dict[cycle]}_cycle_editing" / "CMakeLists.txt",
                    out_path / "SensorFusion" / self.cmake_rel_path,
                )

    def test_simple_merge_regeneration(self, tmp_path) -> None:
        """Test merging files after regeneration in app module with simple model changes"""
        self._prerun_test_merge_regeneration(tmp_path, cycle=1)
        copyfile(
            tmp_path / "SensorFusion" / self.model_rel_out_path,
            concat_str_to_path(tmp_path / "SensorFusion" / self.model_rel_out_path, "~"),
        )
        # update model
        self._update_model_json(
            self.ut_mock_data_path / "simple_changes/model_changed.json",
            tmp_path / "SensorFusion" / self.model_rel_out_path,
        )

        # regenerate
        self._generate(tmp_path)

        # assert conflicts exist in cpp
        assert self._compare_file_with_conflict(
            gen_file_path=tmp_path / "SensorFusion" / self.cpp_rel_path,
            goal_file_path=self.ut_mock_data_path / "simple_changes/sensor_fusion_goal.cpp",
            workspace_path=tmp_path,
        )
        # assert no conflicts in h
        assert filecmp.cmp(
            tmp_path / "SensorFusion" / self.h_rel_path,
            self.ut_mock_data_path / "simple_changes/sensor_fusion_goal.h",
        )
        # assert conflicts exist ut h
        assert self._compare_file_with_conflict(
            gen_file_path=tmp_path / "SensorFusion" / self.ut_h_rel_path,
            goal_file_path=self.ut_mock_data_path / "simple_changes/sensor_fusion_base_test_goal.h",
            workspace_path=tmp_path,
        )
        # assert CMakeLists
        assert (tmp_path / "SensorFusion" / (self.cmake_rel_path + SUFFIX["old_file"])).is_file()
        assert not (tmp_path / "SensorFusion" / get_newly_generated_file_path(self.cmake_rel_path)).is_file()

    def test_complex_merge_regeneration(self, tmp_path) -> None:
        """Test merging files after regeneration in app module with complex model changes"""
        self._prerun_test_merge_regeneration(tmp_path, cycle=1)
        # update model
        self._update_model_json(
            self.ut_mock_data_path / "complex_changes/model_changed_complex.json",
            tmp_path / "SensorFusion" / self.model_rel_out_path,
        )

        # regenerate
        self._generate(tmp_path)

        # assert conflicts exist in cpp
        assert self._compare_file_with_conflict(
            gen_file_path=tmp_path / "SensorFusion" / self.cpp_rel_path,
            goal_file_path=self.ut_mock_data_path / "complex_changes/sensor_fusion_goal.cpp",
            workspace_path=tmp_path,
        )
        # assert no conflicts in h
        assert filecmp.cmp(
            tmp_path / "SensorFusion" / self.h_rel_path,
            self.ut_mock_data_path / "complex_changes/sensor_fusion_goal.h",
        )
        # assert conflicts exist ut h
        assert self._compare_file_with_conflict(
            gen_file_path=tmp_path / "SensorFusion" / self.ut_h_rel_path,
            goal_file_path=self.ut_mock_data_path / "complex_changes/sensor_fusion_base_test_goal.h",
            workspace_path=tmp_path,
        )

    def test_merge_regeneration_without_model_change(self, tmp_path) -> None:
        """Test merging files after regeneration in app module without any model changes"""
        self._prerun_test_merge_regeneration(tmp_path, cycle=1)
        # regenerate
        self._generate(tmp_path)

        # assert user changes are kept and not overwritten
        assert filecmp.cmp(
            tmp_path / "SensorFusion" / self.cpp_rel_path,
            self.ut_mock_data_path / "first_cycle_editing/sensor_fusion_edited.cpp",
        )
        assert filecmp.cmp(
            tmp_path / "SensorFusion" / self.h_rel_path,
            self.ut_mock_data_path / "first_cycle_editing/sensor_fusion_edited.h",
        )
        assert filecmp.cmp(
            tmp_path / "SensorFusion" / self.ut_h_rel_path,
            self.ut_mock_data_path / "first_cycle_editing/sensor_fusion_base_test_edited.h",
        )

    def test_two_cycle_merge_regeneration(self, tmp_path) -> None:
        """Test merging files after regeneration in app module in two cycles"""
        self._prerun_test_merge_regeneration(tmp_path, cycle=1)
        # update model
        self._update_model_json(
            self.ut_mock_data_path / "simple_changes/model_changed.json",
            tmp_path / "SensorFusion" / self.model_rel_out_path,
        )

        # regenerate
        self._generate(tmp_path)

        self._prerun_test_merge_regeneration(tmp_path, cycle=2)
        # update model
        self._update_model_json(
            self.ut_mock_data_path / "simple_changes_second_cycle/model_changed.json",
            tmp_path / "SensorFusion" / self.model_rel_out_path,
        )

        # regenerate
        self._generate(tmp_path)

        # assert conflicts exist in cpp
        assert self._compare_file_with_conflict(
            gen_file_path=tmp_path / "SensorFusion" / self.cpp_rel_path,
            goal_file_path=self.ut_mock_data_path / "simple_changes_second_cycle/sensor_fusion_goal.cpp",
            workspace_path=tmp_path,
        )
        # assert conflicts exist in h
        assert self._compare_file_with_conflict(
            gen_file_path=tmp_path / "SensorFusion" / self.h_rel_path,
            goal_file_path=self.ut_mock_data_path / "simple_changes_second_cycle/sensor_fusion_goal.h",
            workspace_path=tmp_path,
        )
        # assert conflicts exist ut h
        assert self._compare_file_with_conflict(
            gen_file_path=tmp_path / "SensorFusion" / self.ut_h_rel_path,
            goal_file_path=self.ut_mock_data_path / "simple_changes_second_cycle/sensor_fusion_base_test_goal.h",
            workspace_path=tmp_path,
        )

    def test_old_way(self, tmp_path) -> None:
        """Test old way of regeneration"""
        self._prerun_test_merge_regeneration(tmp_path, cycle=1)
        copyfile(
            tmp_path / "SensorFusion" / self.model_rel_out_path,
            concat_str_to_path(tmp_path / "SensorFusion" / self.model_rel_out_path, "~"),
        )
        # update model
        self._update_model_json(
            self.ut_mock_data_path / "simple_changes/model_changed.json",
            tmp_path / "SensorFusion" / self.model_rel_out_path,
        )

        # regenerate
        self._generate(tmp_path, disable_auto_merge=True)

        # assert ~new is generated and no ancestor
        assert (tmp_path / "SensorFusion" / get_newly_generated_file_path(self.cpp_rel_path)).is_file()
        assert not (tmp_path / "SensorFusion" / get_ancestor_file_rel_path(self.cpp_rel_path)).is_file()
        assert (tmp_path / "SensorFusion" / get_newly_generated_file_path(self.h_rel_path)).is_file()
        assert not (tmp_path / "SensorFusion" / get_ancestor_file_rel_path(self.h_rel_path)).is_file()
        assert (tmp_path / "SensorFusion" / get_newly_generated_file_path(self.ut_h_rel_path)).is_file()
        assert not (tmp_path / "SensorFusion" / get_ancestor_file_rel_path(self.ut_h_rel_path)).is_file()

    def test_not_overwrite_conflicted_file(self, tmp_path) -> None:
        """Test source files with conflict won't be overwritten"""
        self._prerun_test_merge_regeneration(tmp_path, cycle=1)
        # update model
        self._update_model_json(
            self.ut_mock_data_path / "simple_changes/model_changed.json",
            tmp_path / "SensorFusion" / self.model_rel_out_path,
        )

        # regenerate
        self._generate(tmp_path)

        # update model
        self._update_model_json(
            self.ut_mock_data_path / "simple_changes_second_cycle/model_changed.json",
            tmp_path / "SensorFusion" / self.model_rel_out_path,
        )

        # regenerate
        self._generate(tmp_path)

        # assert no conflicts in backup files
        assert not file_has_conflict(
            concat_str_to_path(tmp_path / "SensorFusion" / self.cpp_rel_path, SUFFIX["old_file"])
        )
        assert not file_has_conflict(
            concat_str_to_path(tmp_path / "SensorFusion" / self.h_rel_path, SUFFIX["old_file"])
        )
        assert not file_has_conflict(
            concat_str_to_path(tmp_path / "SensorFusion" / self.ut_h_rel_path, SUFFIX["old_file"])
        )

    def test_merge_removal(self, tmp_path) -> None:
        """Test merging files after regeneration in app module with removal in models"""
        self._prerun_test_merge_regeneration(tmp_path, cycle=1, edited_source=False)
        copyfile(
            tmp_path / "SensorFusion" / self.model_rel_out_path,
            concat_str_to_path(tmp_path / "SensorFusion" / self.model_rel_out_path, "~"),
        )
        # update model
        self._update_model_json(
            self.ut_mock_data_path / "removal/model_changed.json",
            tmp_path / "SensorFusion" / self.model_rel_out_path,
        )

        # regenerate
        self._generate(tmp_path)

        # assert conflicts exist in cpp
        assert self._compare_file_with_conflict(
            gen_file_path=tmp_path / "SensorFusion" / self.cpp_rel_path,
            goal_file_path=self.ut_mock_data_path / "removal/sensor_fusion_goal.cpp",
            workspace_path=tmp_path,
        )
        # assert no conflicts in h
        assert filecmp.cmp(
            tmp_path / "SensorFusion" / self.h_rel_path,
            self.ut_mock_data_path / "removal/sensor_fusion_goal.h",
        )
        # assert no conflicts in h
        assert filecmp.cmp(
            tmp_path / "SensorFusion" / self.ut_h_rel_path,
            self.ut_mock_data_path / "removal/sensor_fusion_base_test_goal.h",
        )
