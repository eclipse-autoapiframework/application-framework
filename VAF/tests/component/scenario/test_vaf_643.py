# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Test scenarios via CLI combinations."""
# mypy: disable-error-code="no-untyped-def,union-attr"
# pylint: disable=missing-any-param-doc
# pylint: disable=duplicate-code

import os
from pathlib import Path
from shutil import copyfile
from typing import List

from click import Group
from click.testing import Result

from vaf.entry_points.default.entry_point import model, project

from ...utils.test_helpers import TestHelpers


def __invoke_vaf_cli(cmds: List[str], args: List[str], cli_cmd: Group = project, with_assert: bool = True) -> Result:
    return TestHelpers.invoke_vaf_cli(cli_cmd, cmds, args, with_assert)


test_data_dir = Path(__file__).parent.parent / "test_data/vaf_643"

os.environ["TYPE_VARIANT"] = "prj"


def test_bug_three_way_merge_app_module_no_model_generate(tmp_path, monkeypatch) -> None:
    """VAF-643: Corruption of old model.json due to model generate
    Scenario: App-Module project without inbetween model generate
    """
    monkeypatch.chdir(tmp_path)
    __invoke_vaf_cli(["init", "app-module"], ["-n", "Nobunaga", "--namespace", "oda", "-p", "."])
    monkeypatch.chdir(tmp_path / "Nobunaga")

    copyfile(test_data_dir / "nobunaga_initial.py", "model/nobunaga.py")

    # initial project generate
    __invoke_vaf_cli(["generate"], ["--mode", "prj", "-t", "std", "--skip-make-preset"])

    # adapt implementation
    copyfile(test_data_dir / "nobunaga.h", "implementation/include/oda/nobunaga.h")
    copyfile(test_data_dir / "nobunaga.cpp", "implementation/src/nobunaga.cpp")

    # update model
    copyfile(test_data_dir / "nobunaga.py", "model/nobunaga.py")

    # project generate
    __invoke_vaf_cli(["generate"], ["--mode", "prj", "-t", "std", "--skip-make-preset"])

    assert (test_data_dir / "goal_nobunaga.cpp").read_text("utf-8") == Path(
        "implementation/src/nobunaga.cpp"
    ).read_text("utf-8")

    assert (test_data_dir / "goal_nobunaga.h").read_text("utf-8") == Path(
        "implementation/include/oda/nobunaga.h"
    ).read_text("utf-8")


def test_bug_three_way_merge_app_module(tmp_path, monkeypatch) -> None:
    """VAF-643: Corruption of old model.json due to model generate
    Scenario: App-Module project with inbetween model generate
    """
    monkeypatch.chdir(tmp_path)
    __invoke_vaf_cli(["init", "app-module"], ["-n", "Nobunaga", "--namespace", "oda", "-p", "."])
    monkeypatch.chdir(tmp_path / "Nobunaga")

    copyfile(test_data_dir / "nobunaga_initial.py", "model/nobunaga.py")

    # initial project generate
    __invoke_vaf_cli(["generate"], ["--mode", "prj", "-t", "std", "--skip-make-preset"])

    # adapt implementation
    copyfile(test_data_dir / "nobunaga.h", "implementation/include/oda/nobunaga.h")
    copyfile(test_data_dir / "nobunaga.cpp", "implementation/src/nobunaga.cpp")

    # update model
    copyfile(test_data_dir / "nobunaga.py", "model/nobunaga.py")

    # model generate
    __invoke_vaf_cli(["generate"], ["--mode", "prj"], cli_cmd=model)

    # project generate
    __invoke_vaf_cli(["generate"], ["--mode", "prj", "-t", "std", "--skip-make-preset"])

    assert (test_data_dir / "goal_nobunaga.cpp").read_text("utf-8") == Path(
        "implementation/src/nobunaga.cpp"
    ).read_text("utf-8")

    assert (test_data_dir / "goal_nobunaga.h").read_text("utf-8") == Path(
        "implementation/include/oda/nobunaga.h"
    ).read_text("utf-8")


os.environ["TYPE_VARIANT"] = "all"


def test_bug_three_way_merge_integration_no_model_generate(tmp_path, monkeypatch) -> None:
    """VAF-643: Corruption of old model.json due to model generate
    Scenario: Integration project without inbetween model generate
    """
    monkeypatch.chdir(tmp_path)
    __invoke_vaf_cli(["init", "integration"], ["-n", "daimyo", "-p", "."])
    monkeypatch.chdir(tmp_path / "daimyo")
    __invoke_vaf_cli(["create", "app-module"], ["-n", "Nobunaga", "--namespace", "oda", "-p", "."])

    copyfile(test_data_dir / "nobunaga_initial.py", "src/application_modules/nobunaga/model/nobunaga.py")

    copyfile(test_data_dir / "daimyo.py", "model/vaf/daimyo.py")
    # initial project generate
    __invoke_vaf_cli(["generate"], ["-t", "std", "--skip-make-preset", "--mode", "all"])

    # adapt implementation
    copyfile(
        test_data_dir / "nobunaga.h",
        "src/application_modules/nobunaga/implementation/include/oda/nobunaga.h",
    )
    copyfile(
        test_data_dir / "nobunaga.cpp",
        "src/application_modules/nobunaga/implementation/src/nobunaga.cpp",
    )
    copyfile(
        test_data_dir / "nobunaga.py",
        "src/application_modules/nobunaga/model/nobunaga.py",
    )

    # create new app module
    __invoke_vaf_cli(["create", "app-module"], ["-n", "Tadakatsu", "--namespace", "honda", "-p", "."])
    # adapt its model
    copyfile(
        test_data_dir / "tadakatsu.py",
        "src/application_modules/tadakatsu/model/tadakatsu.py",
    )
    # create mock third party app module
    Path("src/application_modules/ieyasu").mkdir()
    # adapt CMakeList in application-modules
    copyfile(
        test_data_dir / "app-modules-CMakeLists.txt",
        "src/application_modules/CMakeLists.txt",
    )
    # adapt CMakeList in controller
    copyfile(
        test_data_dir / "user-controller-CMakeLists.txt",
        "src/executables/daimyo/CMakeLists.txt",
    )
    # adapt model
    copyfile(test_data_dir / "daimyo1.py", "model/vaf/daimyo.py")

    # project generate
    __invoke_vaf_cli(["generate"], ["-t", "std", "--skip-make-preset", "--mode", "all"])

    assert (test_data_dir / "goal_nobunaga_integration.cpp").read_text("utf-8") == Path(
        "src/application_modules/nobunaga/implementation/src/nobunaga.cpp"
    ).read_text("utf-8")
    assert (test_data_dir / "goal_nobunaga_integration.h").read_text("utf-8") == Path(
        "src/application_modules/nobunaga/implementation/include/oda/nobunaga.h"
    ).read_text("utf-8")
    assert (test_data_dir / "goal-app-modules-CMakeLists.txt").read_text("utf-8") == Path(
        "src/application_modules/CMakeLists.txt"
    ).read_text("utf-8")
    assert (test_data_dir / "goal-user-controller-CMakeLists.txt").read_text("utf-8") == Path(
        "src/executables/daimyo/CMakeLists.txt"
    ).read_text("utf-8")


def test_bug_three_way_merge_integration(tmp_path, monkeypatch) -> None:
    """VAF-643: Corruption of old model.json due to model generate
    Scenario: Integration project with inbetween model generate
    """
    monkeypatch.chdir(tmp_path)
    __invoke_vaf_cli(["init", "integration"], ["-n", "daimyo", "-p", "."])
    monkeypatch.chdir(tmp_path / "daimyo")
    __invoke_vaf_cli(["create", "app-module"], ["-n", "Nobunaga", "--namespace", "oda", "-p", "."])

    copyfile(test_data_dir / "nobunaga_initial.py", "src/application_modules/nobunaga/model/nobunaga.py")

    copyfile(test_data_dir / "daimyo.py", "model/vaf/daimyo.py")
    # initial project generate
    __invoke_vaf_cli(["generate"], ["-t", "std", "--skip-make-preset", "--mode", "all"])

    # adapt implementation
    copyfile(
        test_data_dir / "nobunaga.h",
        "src/application_modules/nobunaga/implementation/include/oda/nobunaga.h",
    )
    copyfile(
        test_data_dir / "nobunaga.cpp",
        "src/application_modules/nobunaga/implementation/src/nobunaga.cpp",
    )
    copyfile(
        test_data_dir / "nobunaga.py",
        "src/application_modules/nobunaga/model/nobunaga.py",
    )

    # create new app module
    __invoke_vaf_cli(["create", "app-module"], ["-n", "Tadakatsu", "--namespace", "honda", "-p", "."])
    # adapt its model
    copyfile(
        test_data_dir / "tadakatsu.py",
        "src/application_modules/tadakatsu/model/tadakatsu.py",
    )
    # create mock third party app module
    Path("src/application_modules/ieyasu").mkdir()
    # adapt CMakeList in application-modules
    copyfile(
        test_data_dir / "app-modules-CMakeLists.txt",
        "src/application_modules/CMakeLists.txt",
    )
    # adapt CMakeList in controller
    copyfile(
        test_data_dir / "user-controller-CMakeLists.txt",
        "src/executables/daimyo/CMakeLists.txt",
    )
    # adapt model
    copyfile(test_data_dir / "daimyo1.py", "model/vaf/daimyo.py")

    # model generate
    __invoke_vaf_cli(["generate"], [], cli_cmd=model)

    # project generate
    __invoke_vaf_cli(["generate"], ["-t", "std", "--skip-make-preset", "--mode", "all"])

    assert (test_data_dir / "goal_nobunaga_integration.cpp").read_text("utf-8") == Path(
        "src/application_modules/nobunaga/implementation/src/nobunaga.cpp"
    ).read_text("utf-8")
    assert (test_data_dir / "goal_nobunaga_integration.h").read_text("utf-8") == Path(
        "src/application_modules/nobunaga/implementation/include/oda/nobunaga.h"
    ).read_text("utf-8")
    assert (test_data_dir / "goal-app-modules-CMakeLists.txt").read_text("utf-8") == Path(
        "src/application_modules/CMakeLists.txt"
    ).read_text("utf-8")
    assert (test_data_dir / "goal-user-controller-CMakeLists.txt").read_text("utf-8") == Path(
        "src/executables/daimyo/CMakeLists.txt"
    ).read_text("utf-8")
