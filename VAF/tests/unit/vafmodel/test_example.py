# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Test of vafmodel."""

# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods
# pylint: disable=unused-variable

# from unittest import mock

import json
from copy import deepcopy
from pathlib import Path

from vaf import vafmodel

from ...utils.test_helpers import Brahma


class TestMain:
    """
    TestMain class
    """

    def test_schema_export(self) -> None:
        """test schema export"""
        vafmodel.generate_json_schema("./schema.json")
        Path.unlink(Path("./schema.json"))

    def test_manual_usage(self) -> None:
        """Test for direct usage of the classes"""
        m = vafmodel.MainModel()
        m.DataTypeDefinitions = vafmodel.DataTypeDefinition()
        m.DataTypeDefinitions.Arrays.append(
            vafmodel.Array(
                Name="MyArray",
                Namespace="test",
                TypeRef=vafmodel.DataType(Name="uint64_t", Namespace=""),
                Size=1,
            )
        )
        j = json.loads(m.model_dump_json())
        assert j["DataTypeDefinitions"]["Arrays"][0]["Name"] == "MyArray"
        assert j["DataTypeDefinitions"]["Arrays"][0]["TypeRef"] == "uint64_t"
        assert j["DataTypeDefinitions"]["Arrays"][0]["Size"] == 1

    def test_persistency_integration(self) -> None:
        """VAF-542: Fix persistency integration in vafgeneration"""
        mock_mi = Brahma.create_dummy_module_interface(name="test", namespace="test")
        mock_am_basic = vafmodel.ApplicationModule(
            Name="BoneyM",
            Namespace="like::a::fool",
            ConsumedInterfaces=[
                vafmodel.ApplicationModuleConsumedInterface(InstanceName="Consiuuumed", ModuleInterfaceRef=mock_mi)
            ],
            ProvidedInterfaces=[],
            PersistencyFiles=[],
        )

        # check negative
        assert not vafmodel.MainModel(
            ModuleInterfaces=[mock_mi], ApplicationModules=[mock_am_basic]
        ).is_persistency_used

        mock_am_per = deepcopy(mock_am_basic)
        mock_am_per.PersistencyFiles.append("test_per")

        # check positive
        assert vafmodel.MainModel(ModuleInterfaces=[mock_mi], ApplicationModules=[mock_am_per]).is_persistency_used

        # check positive by adding after model is created
        mock_model = vafmodel.MainModel(
            ModuleInterfaces=[mock_mi],
        )
        assert not mock_model.is_persistency_used
        mock_model.ApplicationModules.append(mock_am_per)
        assert mock_model.is_persistency_used
