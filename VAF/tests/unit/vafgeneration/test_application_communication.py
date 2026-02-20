# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Application communication generator test."""

# pylint: disable=duplicate-code
# pylint: disable=missing-param-doc
# pylint: disable=missing-type-doc
# pylint: disable=too-few-public-methods
# mypy: disable-error-code="no-untyped-def"
import filecmp
import os
from pathlib import Path

from vaf import vafmodel
from vaf.vafgeneration import vaf_application_communication


class TestIntegration:
    """Basic generation test class"""

    def test_basic_generation(self, tmp_path) -> None:
        """Basic test for application communication generation"""
        m = vafmodel.MainModel()

        data_elements: list[vafmodel.DataElement] = []
        operations: list[vafmodel.Operation] = []

        data_elements.append(
            vafmodel.DataElement(
                Name="my_data_element1",
                TypeRef=vafmodel.DataType(Name="uint64_t", Namespace=""),
            )
        )

        data_elements.append(
            vafmodel.DataElement(
                Name="my_data_element2",
                TypeRef=vafmodel.DataType(Name="uint64_t", Namespace=""),
            )
        )

        parameters: list[vafmodel.Parameter] = []
        parameters.append(
            vafmodel.Parameter(
                Name="in",
                TypeRef=vafmodel.DataType(Name="uint64_t", Namespace=""),
                Direction=vafmodel.ParameterDirection.IN,
            )
        )
        operations.append(vafmodel.Operation(Name="MyVoidOperation", Parameters=parameters))

        parameters.append(
            vafmodel.Parameter(
                Name="out",
                TypeRef=vafmodel.DataType(Name="uint64_t", Namespace=""),
                Direction=vafmodel.ParameterDirection.OUT,
            )
        )
        parameters.append(
            vafmodel.Parameter(
                Name="inout",
                TypeRef=vafmodel.DataType(Name="uint64_t", Namespace=""),
                Direction=vafmodel.ParameterDirection.INOUT,
            )
        )
        operations.append(vafmodel.Operation(Name="MyOperation", Parameters=parameters))

        m.ModuleInterfaces.append(
            vafmodel.ModuleInterface(
                Name="MyInterface",
                Namespace="test",
                DataElements=data_elements,
                Operations=operations,
            )
        )

        m.Executables.append(
            vafmodel.Executable(
                Name="my_executable",
                ExecutorPeriod="10ms",
                InternalCommunicationModules=[
                    vafmodel.PlatformModule(
                        Name="MyServiceModule",
                        Namespace="test",
                        ModuleInterfaceRef=m.ModuleInterfaces[0],
                    )
                ],
                ApplicationModules=[],
            )
        )

        vaf_application_communication.generate(m, tmp_path)

        script_dir = Path(os.path.realpath(__file__)).parent

        assert filecmp.cmp(
            tmp_path / "src-gen/libs/platform_vaf/my_service_module/include/test/my_service_module.h",
            script_dir / "application_communication/my_service_module.h",
        )
        assert filecmp.cmp(
            tmp_path / "src-gen/libs/platform_vaf/my_service_module/src/test/my_service_module.cpp",
            script_dir / "application_communication/my_service_module.cpp",
        )
        assert filecmp.cmp(
            tmp_path / "src-gen/libs/platform_vaf/my_service_module/CMakeLists.txt",
            script_dir / "application_communication/CMakeLists.txt",
        )
