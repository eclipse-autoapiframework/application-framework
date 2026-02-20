# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Application module generator."""

import filecmp
import os

# pylint: disable=too-few-public-methods
# pylint: disable=duplicate-code
# pylint: disable=missing-param-doc
# pylint: disable=missing-type-doc
# mypy: disable-error-code="no-untyped-def"
from pathlib import Path
from typing import List, Tuple
from unittest import mock

import pytest

from vaf import vafmodel
from vaf.vafgeneration import vaf_application_module


class TestIntegration:
    """Basic generation test class"""

    def test_basic_generation(self, tmp_path) -> None:
        """Basic test for interface generation"""
        m = vafmodel.MainModel()

        data_elements: list[vafmodel.DataElement] = []
        operations: list[vafmodel.Operation] = []

        data_elements.append(
            vafmodel.DataElement(
                Name="my_data_element",
                TypeRef=vafmodel.DataType(Name="uint64_t", Namespace=""),
            )
        )

        m.ModuleInterfaces.append(
            vafmodel.ModuleInterface(
                Name="MyInterface",
                Namespace="test",
                DataElements=data_elements,
                Operations=operations,
            )
        )

        consumed_interfaces: list[vafmodel.ApplicationModuleConsumedInterface] = []
        provided_interfaces: list[vafmodel.ApplicationModuleProvidedInterface] = []
        tasks: list[vafmodel.ApplicationModuleTasks] = []

        consumed_interfaces.append(
            vafmodel.ApplicationModuleConsumedInterface(
                InstanceName="c_interface_instance_1",
                ModuleInterfaceRef=m.ModuleInterfaces[0],
            )
        )
        consumed_interfaces.append(
            vafmodel.ApplicationModuleConsumedInterface(
                InstanceName="c_interface_instance_2",
                ModuleInterfaceRef=m.ModuleInterfaces[0],
            )
        )
        provided_interfaces.append(
            vafmodel.ApplicationModuleProvidedInterface(
                InstanceName="p_interface_instance_1",
                ModuleInterfaceRef=m.ModuleInterfaces[0],
            )
        )
        provided_interfaces.append(
            vafmodel.ApplicationModuleProvidedInterface(
                InstanceName="p_interface_instance_2",
                ModuleInterfaceRef=m.ModuleInterfaces[0],
            )
        )

        tasks.append(vafmodel.ApplicationModuleTasks(Name="task1", Period="10ms"))
        tasks.append(
            vafmodel.ApplicationModuleTasks(Name="task2", Period="20ms", PreferredOffset=0, RunAfter=["task1"])
        )

        app_module = vafmodel.ApplicationModule(
            Name="MyApplicationModule",
            Namespace="apps",
            ConsumedInterfaces=consumed_interfaces,
            ProvidedInterfaces=provided_interfaces,
            PersistencyFiles=["MyFile1"],
            Tasks=tasks,
        )

        vaf_application_module.generate_app_module_project_files(app_module, tmp_path)

        script_dir = Path(os.path.realpath(__file__)).parent

        assert filecmp.cmp(
            tmp_path
            # pylint: disable-next=line-too-long
            / "src-gen/libs/application_modules_base/my_application_module/include/apps/my_application_module_base.h",
            script_dir / "application_module/base.h",
        )
        assert filecmp.cmp(
            tmp_path
            # pylint: disable-next=line-too-long
            / "src-gen/libs/application_modules_base/my_application_module/src/apps/my_application_module_base.cpp",
            script_dir / "application_module/base.cpp",
        )
        assert filecmp.cmp(
            tmp_path / "src-gen/libs/application_modules_base/my_application_module/CMakeLists.txt",
            script_dir / "application_module/base_cmake.txt",
        )
        assert filecmp.cmp(
            tmp_path / "src-gen/libs/application_modules_base/my_application_module/CMakeLists.txt",
            script_dir / "application_module/base_cmake.txt",
        )

        assert filecmp.cmp(
            tmp_path
            # pylint: disable-next=line-too-long
            / "implementation/test/unittest/include/apps/my_application_module_base.h",
            script_dir / "application_module/test_base.h",
        )
        assert filecmp.cmp(
            tmp_path
            # pylint: disable-next=line-too-long
            / "implementation//test/unittest/src/apps/my_application_module_base.cpp",
            script_dir / "application_module/test_base.cpp",
        )
        assert filecmp.cmp(
            tmp_path
            # pylint: disable-next=line-too-long
            / "implementation//test/unittest/src/tests.cpp",
            script_dir / "application_module/tests.cpp",
        )
        assert filecmp.cmp(
            tmp_path
            # pylint: disable-next=line-too-long
            / "implementation//test/unittest/src/main.cpp",
            script_dir / "application_module/main.cpp",
        )
        assert filecmp.cmp(
            tmp_path / "implementation//test/unittest/CMakeLists.txt",
            script_dir / "application_module/test_cmake.txt",
        )

    def __mock_app_modules_data(
        self,
        mocked_model: mock.MagicMock,
        mocked_app_modules_data: List[Tuple[str, str]],
    ) -> mock.MagicMock:
        mocked_app_modules = []
        for mocked_data in mocked_app_modules_data:
            tmp_app_module = mock.MagicMock()
            type(tmp_app_module).Name = mocked_data[0]
            type(tmp_app_module).ImplementationProperties = mock.PropertyMock()
            type(tmp_app_module).ImplementationProperties.InstallationPath = mocked_data[1]
            mocked_app_modules.append(tmp_app_module)
        type(mocked_model).ApplicationModules = mocked_app_modules

        return mocked_model

    @mock.patch.object(vafmodel, "MainModel")
    def test_validate_names_success(self, mocked_model) -> None:
        """Test validate_names() that ends with success"""
        mocked_app_modules_data = [
            ("Amari", "one"),
            ("Amari", "two"),
            ("Amarilo", "one"),
            ("Countach", "one"),
            ("Countacht", "one"),
            ("Countacht", "two"),
        ]

        mocked_model = self.__mock_app_modules_data(mocked_model, mocked_app_modules_data)

        vaf_application_module.validate_model_app_modules(mocked_model)

    @mock.patch.object(vafmodel, "MainModel")
    def test_validate_names_failed(self, mocked_model) -> None:
        """Test validate_names() that ends with success"""
        mocked_app_modules_data = [
            ("Ver", "one"),
            ("Mero", "one"),
            ("Countr", "one"),
            ("Berk", "one"),
            ("Mero", "one"),
            ("Loct", "one"),
            ("Countr", "one"),
            ("Mero", "one"),
            ("Herald", "one"),
        ]
        mocked_model = self.__mock_app_modules_data(mocked_model, mocked_app_modules_data)

        with pytest.raises(RuntimeError) as err:
            vaf_application_module.validate_model_app_modules(mocked_model)

        for app_name in [("Mero", "one"), ("Countr", "one")]:
            assert (
                " ".join(
                    [
                        f"ERROR: There are {mocked_app_modules_data.count(app_name)} application modules",
                        f"with name {app_name[0]} and install path '{app_name[1]}'.",
                        "Application Module must have a unique pair of name and install path!",
                    ]
                )
                in err.value.args[0]
            )
