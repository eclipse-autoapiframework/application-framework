# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Example tests."""
# pylint: disable=missing-param-doc

import inspect
import os
from pathlib import Path
from types import ModuleType
from unittest import mock

import pytest

from vaf.core.objects import project_cmd, project_init_cmd
from vaf.vafpy.elements import ApplicationModule

from ...utils.test_helpers import TestHelpers


def mock_importlib_import_module(name: str) -> ModuleType:
    """importlib.import_module somehow fails in CI pytest and can't find the modules
    Args:
        name: name of the python module
    Returns:
        Python module contained by the file
    """
    return TestHelpers.mock_importlib_import_application_modules(
        name=name, app_modules=["gerberit", "wakanda", "ipsum"]
    )


class TestProjectCmd:  # pylint: disable=too-few-public-methods
    """
    Class docstrings are also parsed
    """

    def test_project_init_default(self, tmp_path: Path) -> None:
        """
        .. test:: First unit test greet()
            :id: TCASE-INTEG_001
            :links: CREQ-001

            First unit test for greet()
        Args:
            Path tmp_path: Temporary path provided by pytest
        """
        pj = project_init_cmd.ProjectInitCmd()
        pj.integration_project_init("UutestProject", str(tmp_path))
        assert (tmp_path / "UutestProject").is_dir()

    def test_project_init_non_existing(self, tmp_path: Path) -> None:
        """
        .. test:: Test the reporting of an error if the passed template is not
                  existing.
        Args:
            Path tmp_path: Temporary path provided by pytest
        """
        pj = project_init_cmd.ProjectInitCmd()
        with pytest.raises(Exception):
            pj.integration_project_init("UutestProject", str(tmp_path), template="not-existing")

    def test_missing_vafconfig(self, tmp_path: Path) -> None:
        """
        Test verifying the existence of VAF_CFG_FILE
        Args:
            Path tmp_path: Temporary path provided by pytest
        """
        pj = project_init_cmd.ProjectInitCmd()

        pwd = Path(__file__).resolve().parent
        broken_template = pwd / "data" / "broken_templates" / "missing_vafconfig"
        with pytest.raises(Exception):
            pj.integration_project_init("UutestProject2", str(tmp_path), template=str(broken_template))

    @pytest.mark.slow
    def test_generate_integration(self, tmp_path: Path) -> None:
        """Identical Name of Application Modules are not allowed
        Args:
            Path tmp_path: Temporary path provided by pytest
        """
        pj = project_cmd.ProjectCmd(True)
        pj.generate_integration(
            str(Path(__file__).parent / "test_data/mock_prj/model/vaf/model.json"),
            str(tmp_path),
            "prj",
            "std",
        )

    @pytest.mark.slow
    def test_generate_app_module(self, tmp_path: Path) -> None:
        """Identical Name of Application Modules are not allowed"""
        pj = project_cmd.ProjectCmd(True)
        pj.generate_app_module(
            str(Path(__file__).parent / "test_data/mock_prj/model/app/model.json"),
            str(tmp_path),
            "std",
        )

    def test_add_import_appmodule(self, tmp_path: Path) -> None:
        """
        Test to verify create_appmodule & import_appmodule
        Args:
            Path tmp_path: Temporary path provided by pytest
        """
        pj = project_cmd.ProjectCmd(True)
        pj_init = project_init_cmd.ProjectInitCmd()

        # init project
        pj_init.integration_project_init("ExecuteOrder123", str(tmp_path))
        prj_path = tmp_path / "ExecuteOrder123"

        with mock.patch("importlib.import_module", side_effect=mock_importlib_import_module):
            # add app-module
            pj.create_appmodule("Klaus", "Gerberit", str(prj_path), ".", "model/vaf")
            pj.create_appmodule("Forever", "Wakanda", str(prj_path), ".", "model/vaf")

            # init app-module and then import them to integration project
            pj_init.app_module_project_init("Speck", "Ipsum", str(tmp_path / "SesameStreet"))
            pj.import_appmodule(
                str(tmp_path / "SesameStreet/Ipsum"),
                str(prj_path),
                ".",
                "model/vaf",
            )

        os.environ["IMPORT_APPLICATION_MODULES"] = "import"
        # import __init__.py
        init_module = TestHelpers.import_by_file_name(str(prj_path / "model/vaf/application_modules/__init__.py"))

        # assert imported app modules
        goal_app_modules = ["Gerberit", "Wakanda", "Ipsum"]
        imported_app_modules = [
            app_module_name
            for app_module_name, _ in inspect.getmembers(init_module, lambda x: isinstance(x, ApplicationModule))
        ]
        assert sorted(imported_app_modules) == sorted(goal_app_modules)

        # assert imported python files
        goal_py_modules = [f"import_{module_name.lower()}" for module_name in goal_app_modules + ["instances"]]
        imported_py_modules = [
            app_module_name for app_module_name, _ in inspect.getmembers(init_module, inspect.ismodule)
        ]
        assert sorted(imported_py_modules) == sorted(goal_py_modules)

    def test_remove_appmodule(self, tmp_path: Path) -> None:
        """
        Test to verify create_appmodule, import_appmodule & remove_appmodule
        Args:
            Path tmp_path: Temporary path provided by pytest
        """
        pj = project_cmd.ProjectCmd(True)
        pj_init = project_init_cmd.ProjectInitCmd()

        # init project
        pj_init.integration_project_init("ExecuteOrder123", str(tmp_path))
        prj_path = tmp_path / "ExecuteOrder123"

        with mock.patch("importlib.import_module", side_effect=mock_importlib_import_module):
            # add app-module
            pj.create_appmodule("Klaus", "Gerberit", str(prj_path), ".", "model/vaf")
            pj.create_appmodule("Forever", "Wakanda", str(prj_path), ".", "model/vaf")

            # init app-module and then import them to integration project
            pj_init.app_module_project_init("Speck", "Ipsum", str(tmp_path / "SesameStreet"))
            pj.import_appmodule(
                str(tmp_path / "SesameStreet/Ipsum"),
                str(prj_path),
                ".",
                "model/vaf",
            )

        for removed in ["Gerberit", "Ipsum"]:
            # remove Gerberit and Ipsum
            pj.remove_appmodule(
                prj_path,
                Path("model/vaf"),
                [str(prj_path / "src/application_modules" / removed.lower())],
            )
            # assert app modules project and import_<app_module>.py removed
            assert not Path(prj_path / "src/application_modules" / removed.lower()).is_dir()
            assert not Path(prj_path / "model/vaf" / f"import_{removed.lower()}").is_file()

        os.environ["IMPORT_APPLICATION_MODULES"] = "import"
        # import __init__.py
        init_path = prj_path / "model/vaf/application_modules/__init__.py"
        init_module = TestHelpers.import_by_file_name(str(init_path))
        # assert imported app modules
        goal_app_modules = ["Wakanda"]
        imported_app_modules = [
            app_module_name
            for app_module_name, _ in inspect.getmembers(init_module, lambda x: isinstance(x, ApplicationModule))
        ]
        assert sorted(imported_app_modules) == sorted(goal_app_modules)

        # assert imported python files
        # use text assertion since using mechanism like in test_add_import_addmodule
        # causes interference of the init_module value
        goal_py_modules = [f"import_{module_name.lower()}" for module_name in goal_app_modules]
        not_exist_py_modules = [f"import_{module_name.lower()}" for module_name in ["Gerberit", "Klaus"]]
        init_path_content = init_path.read_text()
        assert all(goal in init_path_content for goal in goal_py_modules)
        assert not any(bad_apple in init_path_content for bad_apple in not_exist_py_modules)

    def test_replace_import(self, tmp_path: Path) -> None:
        """Assert replacement of import path"""
        fct = project_cmd.ProjectCmd._ProjectCmd__update_model_imports  # type:ignore[attr-defined] # pylint: disable=protected-access

        import_str = "Geneva, Vatican, Scandalous"
        basic_str = """from .application_modules import A, B, Frozen, Tilapia
from my_life import Vengena, Kikla
"""
        output_file = tmp_path / "test.py"
        output_file.write_text(basic_str)

        fct(output_file, import_str)

        result = output_file.read_text("utf-8")
        goal = """from .application_modules import Geneva, Vatican, Scandalous
from my_life import Vengena, Kikla
"""
        assert result == goal

        complex_str = """from .application_modules import (
    A,
    B,
    Frozen,
    Tilapia
)
from my_life import Vengena, Kikla
"""
        output_file.write_text(complex_str)
        fct(output_file, import_str)

        result = output_file.read_text("utf-8")
        assert result == goal

        complex_str_2 = """from .application_modules import (
    A,
    B,
    Frozen,
    Tilapia
)
from my_life import (
    Vengena,
    Kikla
)
"""
        output_file.write_text(complex_str_2)
        fct(output_file, import_str)

        result = output_file.read_text("utf-8")
        goal = """from .application_modules import Geneva, Vatican, Scandalous
from my_life import (
    Vengena,
    Kikla
)
"""
        assert result == goal
