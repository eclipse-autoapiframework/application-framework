# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Example tests."""

# pylint: disable=missing-function-docstring
# pylint: disable=redefined-builtin
# pylint: disable=missing-yield-doc
# pylint: disable=redefined-outer-name
# pylint: disable=missing-param-doc
# pylint: disable=missing-yield-type-doc
# pylint: disable=missing-type-doc
# mypy: disable-error-code="no-untyped-def"

import os
from contextlib import contextmanager
from pathlib import Path

import pytest

from vaf.core.objects import make_cmd as makecmd
from vaf.core.objects import project_cmd as project
from vaf.core.objects import project_init_cmd as project_init


@contextmanager
def change_dir(dir: Path):
    current_dir = Path.cwd().as_posix()
    os.chdir(dir)
    try:
        yield
    finally:
        os.chdir(current_dir)


@pytest.fixture(scope="session")
def shared_tmp_path(tmp_path_factory):
    return tmp_path_factory.mktemp("test")


class TestMakeCmd:  # pylint: disable=too-few-public-methods
    """
    Class docstrings are also parsed
    """

    proj_name = "TestProject"
    proj_parent_dir = Path(__file__).parent / "tmp"
    build_dir = "build"

    @pytest.mark.dependency()
    def test_make_preset_default(self, shared_tmp_path) -> None:
        """
        .. test:: Tests the Preset command.
        """
        pj_init = project_init.ProjectInitCmd()
        pj_init.integration_project_init(str(self.proj_name), str(shared_tmp_path))
        proj_dir = shared_tmp_path / self.proj_name
        assert Path(proj_dir).is_dir()  # make sure we have a generated project
        current_dir = Path.cwd().as_posix()
        make = makecmd.MakeCmd()
        make.preset(
            self.build_dir,
            "gcc12__x86_64-pc-linux-elf",
            "Release",
            "",
            str(current_dir / proj_dir),
        )
        assert (proj_dir / self.build_dir).is_dir()  # make sure we have a generated build folder

    @pytest.mark.slow
    @pytest.mark.dependency(depends=["TestMakeCmd::test_make_preset_default"])
    def test_make_application_modules_default(self, shared_tmp_path) -> None:
        """
        .. test:: Tests the create_appmodule command. Depends on preset successful
        """
        proj_dir = shared_tmp_path / self.proj_name
        pj = project.ProjectCmd(True)
        pj.create_appmodule(
            name="AppModule1",
            namespace="demo",
            project_dir=proj_dir.as_posix(),
            rel_pre_path=".",
            model_dir="model/vaf",
        )
        pj.create_appmodule(
            name="AppModule2",
            namespace="demo",
            project_dir=proj_dir.as_posix(),
            rel_pre_path="demo",
            model_dir="model/vaf",
        )
        pj = project.ProjectCmd(True)
        test_dir = Path(__file__).parent
        pj.generate_app_module(
            input_file=str(test_dir / "test_data/vaf_305/model/vaf/model_module1.json"),
            project_dir=proj_dir.as_posix() + "/src/application_modules/app_module1",
            type_variant="std",
        )
        pj.generate_app_module(
            input_file=str(test_dir / "test_data/vaf_305/model/vaf/model_module2.json"),
            project_dir=proj_dir.as_posix() + "/src/application_modules/demo/app_module2",
            type_variant="std",
        )

    @pytest.mark.slow
    @pytest.mark.dependency(depends=["TestMakeCmd::test_make_application_modules_default"])
    def test_make_build_default(self, shared_tmp_path) -> None:
        """
        .. test:: Tests the build command. Depends on create_appmodule successful
        """
        proj_dir = shared_tmp_path / self.proj_name
        pj = project.ProjectCmd(True)
        test_dir = Path(__file__).parent

        pj.generate_integration(
            input_file=str(test_dir / "test_data/vaf_305/model/vaf/model.json"),
            mode="prj",
            type_variant="std",
            project_dir=proj_dir,
        )

        make = makecmd.MakeCmd(True)
        with change_dir(proj_dir):
            make.build("conan-release")
        assert (
            proj_dir / self.build_dir / "Release/bin/DemoExecutable/bin/DemoExecutable"
        ).is_file()  # make sure we have a built executable

    @pytest.mark.dependency(depends=["TestMakeCmd::test_make_build_default"])
    def test_make_install_default(self, shared_tmp_path) -> None:
        """
        .. test:: Tests the install command. Depends on build successful
        """
        proj_dir = shared_tmp_path / self.proj_name
        make = makecmd.MakeCmd(True)
        with change_dir(proj_dir):
            make.install("conan-release")
        assert (proj_dir / self.build_dir / "Release/install/opt/DemoExecutable/bin/DemoExecutable").is_file()

    @pytest.mark.dependency(depends=["TestMakeCmd::test_make_install_default"])
    def test_make_clean_default(self, shared_tmp_path) -> None:
        """
        .. test:: Tests the build command. Depends on preset successful
        """
        proj_dir = shared_tmp_path / self.proj_name
        make = makecmd.MakeCmd(True)
        with change_dir(proj_dir):
            make.clean("conan-release")
        assert not (proj_dir / self.build_dir / "Release/bin/DemoExecutable/bin/DemoExecutable").is_file()

    def test_make_preset_failure(self, tmp_path) -> None:
        """
        .. test:: Tests the Preset command.
        """
        pj_init = project_init.ProjectInitCmd()
        pj_init.integration_project_init(str(self.proj_name), tmp_path.as_posix())
        proj_dir = tmp_path / self.proj_name
        assert Path(proj_dir).is_dir()  # make sure we have a generated project
        current_dir = Path.cwd().as_posix()
        make = makecmd.MakeCmd()
        with pytest.raises(RuntimeError):
            make.preset(
                self.build_dir,
                "gcc12__x86_64-pc-baba-banana",
                "Release",
                "",
                str(current_dir / proj_dir),
            )
        with pytest.raises(RuntimeError):
            make.preset(
                self.build_dir,
                "gcc12__x86_64-pc-linux-elf",
                "EspressoMacchato",
                "",
                str(current_dir / proj_dir),
            )
