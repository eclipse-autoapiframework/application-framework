# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Example tests"""

import filecmp
import os
from pathlib import Path

from vaf import vafmodel
from vaf.vafgeneration import vaf_interface

# pylint: disable=too-few-public-methods
# pylint: disable=duplicate-code
# pylint: disable=missing-param-doc
# pylint: disable=missing-type-doc
# mypy: disable-error-code="no-untyped-def"


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
        parameters = [
            vafmodel.Parameter(
                Name="in",
                TypeRef=vafmodel.DataType(Name="uint64_t", Namespace=""),
                Direction=vafmodel.ParameterDirection.IN,
            ),
            vafmodel.Parameter(
                Name="inout",
                TypeRef=vafmodel.DataType(Name="uint64_t", Namespace=""),
                Direction=vafmodel.ParameterDirection.INOUT,
            ),
            vafmodel.Parameter(
                Name="out",
                TypeRef=vafmodel.DataType(Name="uint64_t", Namespace=""),
                Direction=vafmodel.ParameterDirection.OUT,
            ),
        ]
        operations.append(vafmodel.Operation(Name="my_function", Parameters=parameters))
        operations.append(vafmodel.Operation(Name="my_function_void", Parameters=parameters[:1]))  # pylint: disable=line-too-long

        m.ModuleInterfaces.append(
            vafmodel.ModuleInterface(
                Name="MyInterface",
                Namespace="test",
                DataElements=data_elements,
                Operations=operations,
            )
        )
        vaf_interface.generate_module_interfaces(m, tmp_path)

        script_dir = Path(os.path.realpath(__file__)).parent
        assert filecmp.cmp(
            tmp_path / "src-gen/libs/interfaces/include/test/my_interface_consumer.h",
            script_dir / "interface/test1_consumer_expected.h",
        )
        assert filecmp.cmp(
            tmp_path / "src-gen/libs/interfaces/include/test/my_interface_provider.h",
            script_dir / "interface/test1_provider_expected.h",
        )
        assert filecmp.cmp(
            tmp_path / "test-gen/mocks/interfaces/include/test/my_interface_consumer_mock.h",
            script_dir / "interface/test1_consumer_mock_expected.h",
        )
        assert filecmp.cmp(
            tmp_path / "test-gen/mocks/interfaces/include/test/my_interface_provider_mock.h",
            script_dir / "interface/test1_provider_mock_expected.h",
        )
