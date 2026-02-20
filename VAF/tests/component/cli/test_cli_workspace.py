# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Test project CLI with minimal configuration."""
# pylint: disable=missing-param-doc
# pylint: disable=missing-any-param-doc
# mypy: disable-error-code="no-untyped-def,union-attr"

# from unittest import mock
import json
import re
from typing import Any, List
from unittest import mock

from click import Group
from click.testing import Result

from vaf.core.common.constants import get_package_version
from vaf.entry_points.default.entry_point import workspace

from ...utils.test_helpers import TestHelpers


def __invoke_vaf_workspace(
    cmds: List[str], args: List[str], cli_cmd: Group = workspace, with_assert: bool = True, **kwargs: Any
) -> Result:
    return TestHelpers.invoke_vaf_cli(cli_cmd, cmds, args, with_assert, **kwargs)


def remove_json_comments(json_string: str) -> str:
    """Remove comments from a JSON string."""
    # Remove single-line comments (// ...)
    json_string = re.sub(r"//.*", "", json_string)
    # Remove multi-line comments (/* ... */)
    json_string = re.sub(r"/\*.*?\*/", "", json_string, flags=re.DOTALL)
    return json_string


def test_project_init_workspace_default(tmp_path, monkeypatch) -> None:
    """project init workspace with default version"""
    monkeypatch.chdir(tmp_path)
    __invoke_vaf_workspace(["init"], ["-n", "dummy_workspace", "-w", "."])
    assert (tmp_path / "dummy_workspace").is_dir()

    # Read the JSON file as a string
    with open("dummy_workspace/.devcontainer/devcontainer.json", "r", encoding="utf-8") as file:
        json_string = file.read()

    # Remove comments
    cleaned_json_string = remove_json_comments(json_string)

    # Parse the cleaned JSON string
    data = json.loads(cleaned_json_string)

    devcontainer_version = data.get("image", "")
    with open("dummy_workspace/.vafconfig.json", "r", encoding="utf-8") as file:
        vafconfig = json.loads(file.read())
    # somehow in CI version is always 0.1.0
    assert devcontainer_version.endswith((":latest", ":0.1.0")), devcontainer_version
    assert vafconfig.get("version", "") in ["0.1.0", get_package_version()], vafconfig


def test_project_init_workspace_mocked_version(tmp_path, monkeypatch) -> None:
    """project init workspace with mocked version"""
    monkeypatch.chdir(tmp_path)

    with mock.patch("vaf.core.common.constants.version", return_value="0.5.5"):
        __invoke_vaf_workspace(["init"], ["-n", "dummy_workspace_mocked", "-w", "."])
        assert (tmp_path / "dummy_workspace_mocked").is_dir()

    # Read the JSON file as a string
    with open("dummy_workspace_mocked/.devcontainer/devcontainer.json", "r", encoding="utf-8") as file:
        json_string = file.read()

    # Remove comments
    cleaned_json_string = remove_json_comments(json_string)

    # Parse the cleaned JSON string
    data = json.loads(cleaned_json_string)

    assert data.get("image", "").endswith(":latest"), data

    # assert vafconfig
    with open("dummy_workspace_mocked/.vafconfig.json", "r", encoding="utf-8") as file:
        vafconfig = json.loads(file.read())
    assert vafconfig.get("version", "") == "0.5.5", vafconfig

    with mock.patch("vaf.core.common.constants.version", return_value="0.3.7+dbcrde23jdnhuf"):
        __invoke_vaf_workspace(["init"], ["-n", "dummy_workspace_mockingbird", "-w", "."])
        assert (tmp_path / "dummy_workspace_mockingbird").is_dir()

    # Read the JSON file as a string
    with open("dummy_workspace_mockingbird/.devcontainer/devcontainer.json", "r", encoding="utf-8") as file:
        json_string = file.read()

    # Remove comments
    cleaned_json_string = remove_json_comments(json_string)

    # Parse the cleaned JSON string
    data = json.loads(cleaned_json_string)

    assert data.get("image", "").endswith(":latest"), data

    # assert vafconfig
    with open("dummy_workspace_mockingbird/.vafconfig.json", "r", encoding="utf-8") as file:
        vafconfig = json.loads(file.read())
    assert vafconfig.get("version", "") == "0.3.7+d", vafconfig

    with mock.patch("vaf.core.common.constants.version", return_value="0.3.1.dev.45456e23jdnhuf"):
        __invoke_vaf_workspace(["init"], ["-n", "dummidummi", "-w", "."])
        assert (tmp_path / "dummidummi").is_dir()

    # Read the JSON file as a string
    with open("dummidummi/.devcontainer/devcontainer.json", "r", encoding="utf-8") as file:
        json_string = file.read()

    # Remove comments
    cleaned_json_string = remove_json_comments(json_string)

    # Parse the cleaned JSON string
    data = json.loads(cleaned_json_string)

    assert data.get("image", "").endswith(":latest"), data
    with open("dummidummi/.vafconfig.json", "r", encoding="utf-8") as file:
        vafconfig = json.loads(file.read())
    assert vafconfig.get("version", "") == "0.3.1.dev", vafconfig
