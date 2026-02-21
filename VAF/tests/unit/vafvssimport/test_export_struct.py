# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for ensuring that string-based enums are correctly created and exported."""

import unittest

from vaf import vafmodel
from vaf.vafvssimport.vss.vss_model import VSS

# pylint: disable=duplicate-code


class TestExportStringEnums(unittest.TestCase):
    """Tests the creation and export of string-based enums from VSS JSON."""

    def setUp(self) -> None:
        """Set up mock data for testing."""
        self.mock_vss_data_simple = {
            "SeatConfiguration": {
                "children": {
                    "NonPercentField": {
                        "datatype": "float",
                        "description": "A non-percent field",
                        "max": 55.3,
                        "min": 0,
                        "type": "sensor",
                    },
                    "NonLimitField": {
                        "datatype": "float",
                        "description": "A field wihtout limits",
                        "type": "sensor",
                    },
                    "Mode": {
                        "datatype": "string",
                        "allowed": ["AUTO", "MANUAL"],
                        "description": "Mirror mode.",
                        "type": "actuator",
                    },
                },
                "type": "branch",
            }
        }

        self.mock_vss_data_nested = {
            "SeatConfiguration": {
                "children": {
                    "NonPercentField": {
                        "datatype": "float",
                        "description": "A non-percent field",
                        "max": 55.3,
                        "min": 0,
                        "type": "sensor",
                    },
                    "NonLimitField": {
                        "datatype": "float",
                        "description": "A field wihtout limits",
                        "type": "sensor",
                    },
                    "Mode": {
                        "datatype": "string",
                        "allowed": ["AUTO", "MANUAL"],
                        "description": "Mirror mode.",
                        "type": "actuator",
                    },
                    "Acceleration": {
                        "children": {
                            "Lateral": {
                                "datatype": "float",
                                "description": "Vehicle acceleration in Y (lateral acceleration).",
                                "type": "sensor",
                                "unit": "m/s^2",
                            },
                            "Longitudinal": {
                                "datatype": "float",
                                "description": "Vehicle acceleration in X (longitudinal acceleration).",
                                "type": "sensor",
                                "unit": "m/s^2",
                            },
                            "Vertical": {
                                "datatype": "float",
                                "description": "Vehicle acceleration in Z (vertical acceleration).",
                                "type": "sensor",
                                "max": 5.8,
                                "min": 0,
                                "unit": "m/s^2",
                            },
                        },
                        "description": "Spatial acceleration. Axis definitions according to ISO 8855.",
                        "type": "branch",
                    },
                },
                "type": "branch",
            }
        }

    def test_create_and_export_structs(self) -> None:
        """Test that structs are correctly created and exported."""

        expected_struct_childs = {
            "NonPercentField": vafmodel.DataType(Name="NonPercentField", Namespace="vss::seatconfiguration"),
            "NonLimitField": vafmodel.DataType(Name="NonLimitField", Namespace="vss::seatconfiguration"),
            "Mode": vafmodel.DataType(Name="Mode", Namespace="vss::seatconfiguration"),
        }

        vss_model = VSS(self.mock_vss_data_simple)
        derived_model = vss_model.export()
        struct: vafmodel.Struct = derived_model.DataTypeDefinitions.Structs[0]

        # Assertions for data_elements
        self.assertEqual(len(struct.SubElements), len(expected_struct_childs))
        for subelement in struct.SubElements:
            self.assertEqual(expected_struct_childs[subelement.Name], subelement.TypeRef)

    def test_create_and_export_nested_structs(self) -> None:
        """Test that nested structs are correctly created and exported."""

        expected_outer_struct = {
            "NonPercentField": vafmodel.DataType(Name="NonPercentField", Namespace="vss::seatconfiguration"),
            "NonLimitField": vafmodel.DataType(Name="NonLimitField", Namespace="vss::seatconfiguration"),
            "Mode": vafmodel.DataType(Name="Mode", Namespace="vss::seatconfiguration"),
            "Acceleration": vafmodel.DataType(Name="Acceleration", Namespace="vss::seatconfiguration"),
        }

        expected_inner_struct = {
            "Lateral": vafmodel.DataType(Name="Lateral", Namespace="vss::seatconfiguration::acceleration"),
            "Longitudinal": vafmodel.DataType(Name="Longitudinal", Namespace="vss::seatconfiguration::acceleration"),
            "Vertical": vafmodel.DataType(Name="Vertical", Namespace="vss::seatconfiguration::acceleration"),
        }

        vss_model = VSS(self.mock_vss_data_nested)
        derived_model = vss_model.export()

        structs = derived_model.DataTypeDefinitions.Structs
        for struct in structs:
            if struct.Name == "SeatConfiguration":
                self.assertEqual(len(struct.SubElements), len(expected_outer_struct))
                for subelement in struct.SubElements:
                    self.assertEqual(expected_outer_struct[subelement.Name], subelement.TypeRef)
            elif struct.Name == "Acceleration":
                self.assertEqual(len(struct.SubElements), len(expected_inner_struct))
                for subelement in struct.SubElements:
                    self.assertEqual(expected_inner_struct[subelement.Name], subelement.TypeRef)
            else:
                self.assertEqual(1, 0)


if __name__ == "__main__":
    unittest.main()
