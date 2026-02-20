# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for ensuring that string-based enums are correctly created and exported."""

import unittest

from vaf import vafmodel
from vaf.vafvssimport.vss.vss_model import VSS
from vaf.vafvssimport.vss.vss_types import EnumType

# pylint: disable=duplicate-code


class TestExportStringEnums(unittest.TestCase):
    """Tests the creation and export of string-based enums from VSS JSON."""

    def setUp(self) -> None:
        """Set up mock data for testing."""
        self.mock_vss_data = {
            "MirrorState": {
                "children": {
                    "Active": {
                        "datatype": "string",
                        "allowed": ["NONE", "ACTIVE", "INACTIVE"],
                        "description": "Mirror state values.",
                        "type": "actuator",
                    },
                    "Mode": {
                        "datatype": "string",
                        "allowed": ["AUTO", "MANUAL"],
                        "description": "Mirror mode.",
                        "type": "actuator",
                    },
                    "UnsupportedField": {
                        "datatype": "float",
                        "allowed": [1.0, 5.0],
                        "description": "A non-enum field.",
                        "type": "sensor",
                    },
                },
                "type": "branch",
            }
        }

    def test_create_and_export_enums(self) -> None:
        """Test that enums are correctly created and exported."""
        expected_enums = [
            vafmodel.VafEnum(
                Name="Active",
                Namespace="vss::mirrorstate",
                Literals=[
                    vafmodel.EnumLiteral(Item="NONE", Value=1),
                    vafmodel.EnumLiteral(Item="ACTIVE", Value=2),
                    vafmodel.EnumLiteral(Item="INACTIVE", Value=3),
                ],
                BaseType=vafmodel.DataType(Name="uint8_t", Namespace=""),
            ),
            vafmodel.VafEnum(
                Name="Mode",
                Namespace="vss::mirrorstate",
                Literals=[
                    vafmodel.EnumLiteral(Item="AUTO", Value=1),
                    vafmodel.EnumLiteral(Item="MANUAL", Value=2),
                ],
                BaseType=vafmodel.DataType(Name="uint8_t", Namespace=""),
            ),
        ]

        vss_model = VSS(self.mock_vss_data)
        derived_model = vss_model.export()

        # Assertions for enums
        self.assertEqual(
            len(derived_model.DataTypeDefinitions.Enums), len(expected_enums)
        )  # Only 2 enums created (Active, Mode)
        for enum in expected_enums:
            self.assertTrue(
                enum in derived_model.DataTypeDefinitions.Enums,
                f"Enum {enum.Name} not found",
            )

    def test_export_enum(self) -> None:
        """Test the export functionality for enums."""
        enum_type = EnumType(name="Active", namespace="example")
        enum_type.add_literal(item="NONE", value=1)
        enum_type.add_literal(item="ACTIVE", value=2)
        enum_type.add_literal(item="INACTIVE", value=3)

        exported_enum = enum_type.export()

        # Assertions for exported enum
        self.assertEqual(exported_enum.Name, "Active")
        self.assertEqual(exported_enum.BaseType.Name, "uint8_t")  # type: ignore
        self.assertEqual(len(exported_enum.Literals), 3)
        self.assertEqual(exported_enum.Literals[0].Item, "NONE")
        self.assertEqual(exported_enum.Literals[0].Value, 1)
        self.assertEqual(exported_enum.Literals[2].Item, "INACTIVE")
        self.assertEqual(exported_enum.Literals[2].Value, 3)


if __name__ == "__main__":
    unittest.main()
