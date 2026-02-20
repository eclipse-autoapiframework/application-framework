# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for CLI undo/redo functionality in the VAF.

This module contains tests to verify the correctness of undo and redo
operations for CLI commands in the framework.
"""
# mypy: disable-error-code="no-untyped-def,union-attr"
# pylint: disable=missing-type-doc
# pylint: disable=too-many-statements

from pathlib import Path
from shutil import copyfile
from typing import Any, List

from click import Group
from click.testing import Result

from tests.utils.test_helpers import TestHelpers
from vaf.entry_points.default.entry_point import model, project


def __invoke_vaf_cli(
    cmds: List[str], args: List[str], cli_cmd: Group = project, with_assert: bool = True, **kwargs: Any
) -> Result:
    """Invoke the VAF CLI with the specified commands and arguments.

    Args:
        cmds (List[str]): List of CLI commands.
        args (List[str]): List of arguments for the commands.
        cli_cmd (Group): The CLI command group to invoke.
        with_assert (bool): Whether to assert the result.
        **kwargs (Any): Additional keyword arguments.

    Returns:
        Result: The result of the CLI invocation.
    """
    return TestHelpers.invoke_vaf_cli(cli_cmd, cmds, args, with_assert, **kwargs)


def __get_current_state_file_content(file_path: Path) -> str:
    """Read the content of the specified file.

    Args:
        file_path (Path): Path to the file.

    Returns:
        str: The content of the file.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def test_undo_redo_app_module_project(tmp_path, monkeypatch):
    """Test undo and redo functionality for an app module project.

    Args:
        tmp_path: Temporary path for the test.
        monkeypatch: Monkeypatching utility for modifying behavior.
    """
    MODEL_DATA_PATH = Path(__file__).parent.parent / "test_data/vaf_740"

    monkeypatch.chdir(tmp_path)
    # init app module project
    __invoke_vaf_cli(["init", "app-module"], ["-n", "menapp", "--namespace", "well", "-p", "."])

    monkeypatch.chdir("menapp")
    model_py_path = Path("model/menapp.py")
    model_json_path = Path("model/model.json")

    last_state_str = __get_current_state_file_content(model_json_path)
    # copy first model
    copyfile(MODEL_DATA_PATH / "random_config_1.py", model_py_path)
    # run model generate
    __invoke_vaf_cli(["generate"], ["--mode", "prj", "-p", "."], cli_cmd=model)
    new_state_str = __get_current_state_file_content(model_json_path)
    # run undo
    __invoke_vaf_cli(["undo"], [])
    # assert undo value
    assert __get_current_state_file_content(model_json_path) == last_state_str
    # run endo
    __invoke_vaf_cli(["redo"], [])
    # assert redo value
    assert __get_current_state_file_content(model_json_path) == new_state_str
    # check --list
    result = __invoke_vaf_cli(["undo"], ["--list"])
    assert "Can undo: True, Can redo: False" in result.output
    assert "[Position 1] file_modify:" in result.output, result.output
    # check --clear
    __invoke_vaf_cli(["undo"], ["--clear"])
    result = __invoke_vaf_cli(["undo"], ["--list"])
    assert "No operations in history." in result.output


def test_undo_redo_import_interface(tmp_path, monkeypatch):
    """Test undo and redo functionality for import interface project.

    Args:
        tmp_path: Temporary path for the test.
        monkeypatch: Monkeypatching utility for modifying behavior.
    """
    MODEL_DATA_PATH = Path(__file__).parent.parent / "test_data/vaf_740"

    monkeypatch.chdir(tmp_path)
    # init interface project
    __invoke_vaf_cli(["init", "interface"], ["-n", "meniface", "-p", "."])
    monkeypatch.chdir("meniface")
    copyfile(MODEL_DATA_PATH / "interfaces.py", "meniface.py")

    __invoke_vaf_cli(["generate"], ["--mode", "all", "--model-dir", "."], cli_cmd=model)
    interface_json_path = Path("export/meniface.json").absolute()
    monkeypatch.chdir(tmp_path)
    # init app module project
    __invoke_vaf_cli(["init", "app-module"], ["-n", "menapp", "--namespace", "well", "-p", "."])
    # import interface project
    monkeypatch.chdir("menapp")
    __invoke_vaf_cli(
        ["import"],
        [
            "--input-file",
            interface_json_path.as_posix(),
            "--model-dir",
            "model",
        ],
    )
    # undo
    __invoke_vaf_cli(["undo"], [])
    for file in ["meniface.json", "_imported_models.json", "meniface.py", "__init__.py"]:
        assert not (Path("model/imported_models") / file).is_file()
    # redo
    __invoke_vaf_cli(["redo"], [])
    for file in ["meniface.json", "_imported_models.json", "meniface.py", "__init__.py"]:
        assert (Path("model/imported_models") / file).is_file()

    # rerun import -> no changes
    __invoke_vaf_cli(
        ["import"],
        ["--input-file", interface_json_path.as_posix(), "--model-dir", "model", "--force-import"],
    )
    result = __invoke_vaf_cli(["undo"], ["-n", "2"])
    # second import doesn't have any change to first import -> nothing to undo
    assert "Successfully undid 1 operation(s)" in result.output
    __invoke_vaf_cli(["redo"], [])

    monkeypatch.chdir(tmp_path / "meniface")
    copyfile(MODEL_DATA_PATH / "interfaces_1.py", "meniface.py")
    __invoke_vaf_cli(["generate"], ["--mode", "all", "--model-dir", "."], cli_cmd=model)

    monkeypatch.chdir(tmp_path / "menapp")
    # rerun import interface project to ensure old behaviour
    __invoke_vaf_cli(
        ["import"],
        ["--input-file", interface_json_path.as_posix(), "--model-dir", "model", "--force-import"],
    )
    result = __invoke_vaf_cli(["undo"], ["-n", "2"])
    # second import doesn't have any change to first import -> nothing to undo
    assert "Successfully undid 2 operation(s)" in result.output


def test_undo_redo_integration_project(tmp_path, monkeypatch):
    """Test undo and redo functionality for integration project.

    Args:
        tmp_path: Temporary path for the test.
        monkeypatch: Monkeypatching utility for modifying behavior.
    """
    MODEL_DATA_PATH = Path(__file__).parent.parent / "test_data/vaf_740"

    monkeypatch.chdir(tmp_path)
    # init interface project
    __invoke_vaf_cli(["init", "interface"], ["-n", "meniface", "-p", "."])
    monkeypatch.chdir("meniface")
    copyfile(MODEL_DATA_PATH / "interfaces.py", "meniface.py")

    __invoke_vaf_cli(["generate"], ["--mode", "all", "--model-dir", "."], cli_cmd=model)
    interface_json_path = Path("export/meniface.json").absolute()
    monkeypatch.chdir(tmp_path)
    # init app module project
    __invoke_vaf_cli(["init", "app-module"], ["-n", "menapp", "--namespace", "well", "-p", "."])
    # import interface project
    monkeypatch.chdir("menapp")
    __invoke_vaf_cli(
        ["import"],
        [
            "--input-file",
            interface_json_path.as_posix(),
            "--model-dir",
            "model",
        ],
    )
    copyfile(MODEL_DATA_PATH / "random_config_1.py", Path("model/menapp.py"))
    __invoke_vaf_cli(["generate"], ["--mode", "prj", "-p", "."], cli_cmd=model)
    monkeypatch.chdir(tmp_path)

    # init app module project
    __invoke_vaf_cli(["init", "app-module"], ["-n", "wiener", "--namespace", "well", "-p", "."])
    # import interface project
    monkeypatch.chdir("wiener")
    __invoke_vaf_cli(
        ["import"],
        [
            "--input-file",
            interface_json_path.as_posix(),
            "--model-dir",
            "model",
        ],
    )
    copyfile(MODEL_DATA_PATH / "random_config_2.py", Path("model/wiener.py"))
    __invoke_vaf_cli(["generate"], ["--mode", "prj", "-p", "."], cli_cmd=model)

    monkeypatch.chdir(tmp_path)
    menapp_path = Path("menapp").absolute()
    wiener_path = Path("wiener").absolute()
    monkeypatch.chdir(tmp_path)
    # init integration project
    __invoke_vaf_cli(["init", "integration"], ["-n", "minecraft", "-p", "."])

    monkeypatch.chdir("minecraft")
    # import app module
    __invoke_vaf_cli(["import"], ["--input-dir", menapp_path.as_posix(), "-p", "."])
    __invoke_vaf_cli(["import"], ["--input-dir", wiener_path.as_posix(), "-p", "."])

    model_py_path = Path("model/vaf/minecraft.py")
    model_json_path = Path("model/vaf/model.json")

    # copy first model
    copyfile(MODEL_DATA_PATH / "random_model_1.py", model_py_path)
    # run model generate
    __invoke_vaf_cli(["generate"], ["--mode", "prj", "-p", "."], cli_cmd=model)
    first_state_str = __get_current_state_file_content(model_json_path)
    # run undo
    __invoke_vaf_cli(["undo"], [])
    # assert undo value
    assert not model_json_path.is_file()
    # run redo
    __invoke_vaf_cli(["redo"], [])
    # assert redo value
    assert __get_current_state_file_content(model_json_path) == first_state_str
    # check --list
    result = __invoke_vaf_cli(["undo"], ["--list"])
    assert "Can undo: True, Can redo: False" in result.output
    assert "[Position 3] file_create:" in result.output, result.output
    # copy 2nd model
    copyfile(MODEL_DATA_PATH / "random_model_2.py", model_py_path)
    # run model generate
    __invoke_vaf_cli(["generate"], ["--mode", "prj", "-p", "."], cli_cmd=model)
    second_state_str = __get_current_state_file_content(model_json_path)

    # copy 3rd model
    copyfile(MODEL_DATA_PATH / "random_model_3.py", model_py_path)
    # run model generate
    __invoke_vaf_cli(["generate"], ["--mode", "prj", "-p", "."], cli_cmd=model)

    # Undo two steps
    __invoke_vaf_cli(["undo"], ["-n", "2"])
    assert __get_current_state_file_content(model_json_path) == first_state_str
    __invoke_vaf_cli(["redo"], [])
    assert __get_current_state_file_content(model_json_path) == second_state_str

    # check --clear
    __invoke_vaf_cli(["undo"], ["--clear"])
    result = __invoke_vaf_cli(["undo"], ["--list"])
    assert "No operations in history." in result.output


def test_undo_redo_import_app_module(tmp_path, monkeypatch):
    """Test undo and redo functionality for import app module project.

    Args:
        tmp_path: Temporary path for the test.
        monkeypatch: Monkeypatching utility for modifying behavior.
    """
    MODEL_DATA_PATH = Path(__file__).parent.parent / "test_data/vaf_740"

    monkeypatch.chdir(tmp_path)
    # init interface project
    __invoke_vaf_cli(["init", "interface"], ["-n", "meniface", "-p", "."])
    monkeypatch.chdir("meniface")
    copyfile(MODEL_DATA_PATH / "interfaces.py", "meniface.py")

    __invoke_vaf_cli(["generate"], ["--mode", "all", "--model-dir", "."], cli_cmd=model)
    interface_json_path = Path("export/meniface.json").absolute()
    monkeypatch.chdir(tmp_path)
    # init app module project
    __invoke_vaf_cli(["init", "app-module"], ["-n", "menapp", "--namespace", "well", "-p", "."])
    # import interface project
    monkeypatch.chdir("menapp")
    __invoke_vaf_cli(
        ["import"],
        [
            "--input-file",
            interface_json_path.as_posix(),
            "--model-dir",
            "model",
        ],
    )
    copyfile(MODEL_DATA_PATH / "random_config_1.py", Path("model/menapp.py"))
    __invoke_vaf_cli(["generate"], ["--mode", "prj", "-p", "."], cli_cmd=model)

    monkeypatch.chdir(tmp_path)
    app_module_path = Path("menapp").absolute()
    # init integration project
    __invoke_vaf_cli(["init", "integration"], ["-n", "minecraft", "-p", "."])

    monkeypatch.chdir("minecraft")
    # import app module
    __invoke_vaf_cli(["import"], ["--input-dir", app_module_path.as_posix(), "-p", "."])
    # assert files
    for file in ["import_instances.py", "import_random_app_module.py"]:
        assert (Path("model/vaf/application_modules") / file).is_file()
    assert (Path("model/vaf/application_modules") / "__init__.py").read_text(encoding="utf-8") != ""

    # undo
    __invoke_vaf_cli(["undo"], [])
    # assert files
    for file in ["import_instances.py", "import_random_app_module.py"]:
        assert not (Path("model/vaf/application_modules") / file).is_file()
    assert (Path("model/vaf/application_modules") / "__init__.py").read_text(encoding="utf-8") == ""


def test_undo_redo_multiple_changes(tmp_path, monkeypatch):
    """Test undo and redo functionality for multiple model changes.

    Args:
        tmp_path: Temporary path for the test.
        monkeypatch: Monkeypatching utility for modifying behavior.
    """
    MODEL_DATA_PATH = Path(__file__).parent.parent / "test_data/vaf_740"

    monkeypatch.chdir(tmp_path)
    # Initialize app module project
    __invoke_vaf_cli(["init", "app-module"], ["-n", "menapp", "--namespace", "well", "-p", "."])

    monkeypatch.chdir("menapp")
    model_py_path = Path("model/menapp.py")
    model_json_path = Path("model/model.json")

    # Save the initial state
    first_state_str = __get_current_state_file_content(model_json_path)

    # Apply first model change
    copyfile(MODEL_DATA_PATH / "random_config_1.py", model_py_path)
    __invoke_vaf_cli(["generate"], ["--mode", "prj", "-p", "."], cli_cmd=model)
    second_state_str = __get_current_state_file_content(model_json_path)

    # Apply second model change
    copyfile(MODEL_DATA_PATH / "random_config_2.py", model_py_path)
    __invoke_vaf_cli(["generate"], ["--mode", "prj", "-p", "."], cli_cmd=model)

    # Apply third model change
    copyfile(MODEL_DATA_PATH / "random_config_3.py", model_py_path)
    __invoke_vaf_cli(["generate"], ["--mode", "prj", "-p", "."], cli_cmd=model)
    fourth_state_str = __get_current_state_file_content(model_json_path)

    # Undo two steps
    __invoke_vaf_cli(["undo"], ["-n", "2"])
    assert __get_current_state_file_content(model_json_path) == second_state_str
    __invoke_vaf_cli(["undo"], [])
    assert __get_current_state_file_content(model_json_path) == first_state_str

    # Redo three steps
    __invoke_vaf_cli(["redo"], ["-n", "3"])
    assert __get_current_state_file_content(model_json_path) == fourth_state_str


def test_redo_removal(tmp_path, monkeypatch):
    """Test that redo is removed if user regenerates.

    Args:
        tmp_path: Temporary path for the test.
        monkeypatch: Monkeypatching utility for modifying behavior.
    """
    MODEL_DATA_PATH = Path(__file__).parent.parent / "test_data/vaf_740"

    monkeypatch.chdir(tmp_path)
    # Initialize app module project
    __invoke_vaf_cli(["init", "app-module"], ["-n", "menapp", "--namespace", "well", "-p", "."])

    monkeypatch.chdir("menapp")
    model_py_path = Path("model/menapp.py")
    model_json_path = Path("model/model.json")

    # Apply first model change
    copyfile(MODEL_DATA_PATH / "random_config_1.py", model_py_path)
    __invoke_vaf_cli(["generate"], ["--mode", "prj", "-p", "."], cli_cmd=model)
    second_state_str = __get_current_state_file_content(model_json_path)

    # Apply second model change
    copyfile(MODEL_DATA_PATH / "random_config_2.py", model_py_path)
    __invoke_vaf_cli(["generate"], ["--mode", "prj", "-p", "."], cli_cmd=model)

    # Apply third model change
    copyfile(MODEL_DATA_PATH / "random_config_3.py", model_py_path)
    __invoke_vaf_cli(["generate"], ["--mode", "prj", "-p", "."], cli_cmd=model)

    # Undo two steps
    __invoke_vaf_cli(["undo"], ["-n", "2"])
    assert __get_current_state_file_content(model_json_path) == second_state_str
    __invoke_vaf_cli(["generate"], ["--mode", "prj", "-p", "."], cli_cmd=model)

    # Check that redo is not possible
    result = __invoke_vaf_cli(["redo"], ["--list"])
    assert "Can redo: False" in result.output
