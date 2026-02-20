# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""
Helpers for Testing
"""

import importlib
import sys
from types import ModuleType
from typing import Any, List

from click import Group
from click.testing import CliRunner, Result

from vaf import vafmodel


class Brahma:  # pylint: disable=dangerous-default-value
    @staticmethod
    def create_dummy_data_element(
        name: str = "dummy_element", namespace: str = "", data_type: str = "uint64_t"
    ) -> vafmodel.DataElement:
        return vafmodel.DataElement(
            Name=name,
            TypeRef=vafmodel.DataType(Name=data_type, Namespace=namespace),
        )

    @staticmethod
    def create_dummy_parameter(
        name: str = "dummy_parameter",
        namespace: str = "",
        data_type: str = "uint64_t",
        direction: vafmodel.ParameterDirection = vafmodel.ParameterDirection.OUT,
    ) -> vafmodel.Parameter:
        return vafmodel.Parameter(
            Name=name,
            TypeRef=vafmodel.DataType(Name=data_type, Namespace=namespace),
            Direction=direction,
        )

    @staticmethod
    def create_dummy_operation(
        name: str = "DummyOp",
        parameters: List[vafmodel.Parameter] = [create_dummy_parameter()],
    ) -> vafmodel.Operation:
        return vafmodel.Operation(Name=name, Parameters=parameters)

    @staticmethod
    def create_dummy_module_interface(
        name: str = "DummyInterface",
        namespace: str = "nada",
        data_elements: List[vafmodel.DataElement] = [create_dummy_data_element()],
        operations: List[vafmodel.Operation] = [create_dummy_operation()],
    ) -> vafmodel.ModuleInterface:
        return vafmodel.ModuleInterface(
            Name=name,
            Namespace=namespace,
            DataElements=data_elements,
            Operations=operations,
        )


class TestHelpers:
    """Class for test helpers"""

    @staticmethod
    def invoke_vaf_cli(
        cli_cmd: Group, cmds: List[str], args: List[str], with_assert: bool = True, **kwargs: Any
    ) -> Result:
        """Method to invoke vaf cli and assert its run
        Args:
            cli_cmd: click Group for the CLI call
            cmds: List of click commands as strings
            args: arguments to be passed
            with_assert: boolean to turn on/off assertion
        Return:
            result of the invoke
        """
        result = CliRunner().invoke(cli_cmd, cmds + args, **kwargs)
        if with_assert:
            assert result.exit_code == 0, result.output
        return result

    @staticmethod
    def import_by_file_name(file_path: str) -> ModuleType:
        """importlib.import_module somehow fails in pytest and can't find the modules
        Args:
            file_path: string of path of the file name
        Returns:
            Python module contained by the file
        Raises:
            RuntimeError: if python file is not valid or can't import the module
        """
        if not file_path.endswith(".py"):
            raise RuntimeError(f"Invalid python file in {file_path}")

        file_name = file_path.rsplit("/")[1].rstrip(".py")
        spec = importlib.util.spec_from_file_location(file_name, file_path)
        if spec:
            module = importlib.util.module_from_spec(spec)
            if module and spec.loader:
                sys.modules[file_name] = module
                spec.loader.exec_module(module)

        if not module:
            raise RuntimeError(f"Failed to import module in {file_path}")

        return module

    @classmethod
    def mock_importlib_import_application_modules(cls, name: str, app_modules: List[str]) -> ModuleType:
        """Import application modules' python module in unit test
        Reason: importlib.import_module somehow fails in CI pytest and can't find the modules
        Args:
            name: name of the python module
            app_modules: list of app modules name in snake
        Returns:
            Python module contained by the file
        """
        module = None
        if name in [f"application_modules.import_{mocked_module}" for mocked_module in ["instances"] + app_modules]:
            file_dir, file_name = name.split(".")
            module = cls.import_by_file_name(f"{sys.path[-1]}/{file_dir}/{file_name}.py")
        if module is None:
            module = importlib.import_module(name)
        return module

    @classmethod
    def mock_importlib_import_python_module(cls, name: str) -> ModuleType:
        """Import any python module in unit test
        importlib.import_module somehow fails in pytest and can't find the modules
        Args:
            name: name of the python module
        Returns:
            Python module contained by the file
        """
        file_dir, file_name = name.split(".")
        module: ModuleType = cls.import_by_file_name(f"{sys.path[-1]}/{file_dir}/{file_name}.py")

        return module
