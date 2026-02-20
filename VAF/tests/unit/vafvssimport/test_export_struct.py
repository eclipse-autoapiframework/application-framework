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

        expected_data_elements = {
            "NonPercentField": vafmodel.DataType(Name="float", Namespace=""),
            "NonLimitField": vafmodel.DataType(Name="float", Namespace=""),
            "Mode": vafmodel.DataType(Name="Mode", Namespace="vss::seatconfiguration"),
        }

        vss_model = VSS(self.mock_vss_data_simple)
        derived_model = vss_model.export()
        data_elements = derived_model.ModuleInterfaces[0].DataElements

        # Assertions for data_elements
        self.assertEqual(len(data_elements), len(expected_data_elements))
        for de in data_elements:
            self.assertEqual(expected_data_elements[de.Name], de.TypeRef)

    def test_create_and_export_nested_structs(self) -> None:
        """Test that nested structs are correctly created and exported."""

        expected_outer_de = {
            "NonPercentField": vafmodel.DataType(Name="float", Namespace=""),
            "NonLimitField": vafmodel.DataType(Name="float", Namespace=""),
            "Mode": vafmodel.DataType(Name="Mode", Namespace="vss::seatconfiguration"),
            "Acceleration": vafmodel.DataType(Name="Acceleration", Namespace="vss::seatconfiguration"),
        }

        expected_inner_de = {
            "Lateral": vafmodel.DataType(Name="float", Namespace=""),
            "Longitudinal": vafmodel.DataType(Name="float", Namespace=""),
            "Vertical": vafmodel.DataType(Name="float", Namespace=""),
        }

        vss_model = VSS(self.mock_vss_data_nested)
        derived_model = vss_model.export()

        # Assertions for outer struct
        data_elements = derived_model.ModuleInterfaces[0].DataElements
        self.assertEqual(len(data_elements), len(expected_outer_de))
        for de in data_elements:
            self.assertEqual(expected_outer_de[de.Name], de.TypeRef)
        # assert setter callback for actuator
        self.assertEqual(
            derived_model.ModuleInterfaces[0].Operations[0].Name,
            "Mode_Setter_Callback",
        )

        # Assertions for inner struct
        data_elements = derived_model.ModuleInterfaces[1].DataElements
        self.assertEqual(len(data_elements), len(expected_inner_de))
        for de in data_elements:
            self.assertEqual(expected_inner_de[de.Name], de.TypeRef)


if __name__ == "__main__":
    unittest.main()
