# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for ensuring that arrays are correctly exported."""

import unittest

from vaf import vafpy
from vaf.vafvssimport.vss.vss_model import VSS


class TestExportArrays(unittest.TestCase):
    """Tests the export of arrays from VSS JSON."""

    def setUp(self) -> None:
        """Set up mock data for testing."""
        self.mock_vss_data = {
            "SeatConfiguration": {
                "children": {
                    "SeatRowCounts": {
                        "datatype": "uint8[]",
                        "description": "Number of seats in each row.",
                        "arraysize": 5,
                        "type": "sensor",
                    },
                    "TemperatureLevels": {
                        "datatype": "float[]",
                        "description": "Temperature settings for each zone.",
                        "arraysize": 10,
                        "type": "sensor",
                    },
                    "DynamicArray": {
                        "datatype": "int32[]",
                        "description": "Dynamically sized array example.",
                        "type": "sensor",
                    },
                },
                "type": "branch",
            }
        }

        self.mock_vss_data_duplicates = {
            "SeatConfiguration": {
                "children": {
                    "SeatRowCounts": {
                        "datatype": "float[]",
                        "description": "Number of seats in each row.",
                        "arraysize": 5,
                        "type": "sensor",
                    },
                    "TemperatureLevels": {
                        "datatype": "float[]",
                        "description": "Temperature settings for each zone.",
                        "arraysize": 10,
                        "type": "sensor",
                    },
                    "DynamicArray": {
                        "datatype": "int32[]",
                        "description": "Dynamically sized array example.",
                        "type": "sensor",
                    },
                    "DuplicateVec": {
                        "datatype": "int32[]",
                        "description": "Dynamically sized array example.",
                        "type": "sensor",
                    },
                    "DuplicateArr": {
                        "datatype": "float[]",
                        "description": "Dynamically sized array example.",
                        "type": "sensor",
                        "arraysize": 10,
                    },
                },
                "type": "branch",
            }
        }

    def test_export_fixed_size_arrays(self) -> None:
        """Test that fixed-size arrays are correctly exported."""
        expected_arrays = {
            "uint8ArraySize5": {
                "size": 5,
                "type": vafpy.BaseTypes.UINT8_T.TypeRef,
                "passed": False,
            },
            "floatArraySize10": {
                "size": 10,
                "type": vafpy.BaseTypes.FLOAT.TypeRef,
                "passed": False,
            },
        }
        expected_vectors = {
            "int32Vector": {"type": vafpy.BaseTypes.INT32_T.TypeRef, "passed": False},
        }

        vss_model = VSS(self.mock_vss_data)
        derived_model = vss_model.export()

        for array in derived_model.DataTypeDefinitions.Arrays:
            self.assertEqual(array.Size, expected_arrays[array.Name]["size"])
            self.assertEqual(array.TypeRef, expected_arrays[array.Name]["type"])
            expected_arrays[array.Name]["passed"] = True

        for vector in derived_model.DataTypeDefinitions.Vectors:
            self.assertEqual(vector.TypeRef, expected_vectors[vector.Name]["type"])
            expected_vectors[vector.Name]["passed"] = True

        for key, value in (expected_arrays | expected_vectors).items():
            assert value["passed"], f"Expected element {key} not found"

    def test_export_duplicated_arrays(self) -> None:
        """Test that duplicated arrays and vectors are correctly only exported once."""
        expected_arrays = {
            "floatArraySize10": {
                "size": 10,
                "type": vafpy.BaseTypes.FLOAT.TypeRef,
                "passed": False,
            },
            "floatArraySize5": {
                "size": 5,
                "type": vafpy.BaseTypes.FLOAT.TypeRef,
                "passed": False,
            },
        }
        expected_vectors = {
            "int32Vector": {"type": vafpy.BaseTypes.INT32_T.TypeRef, "passed": False},
        }

        vss_model = VSS(self.mock_vss_data_duplicates)
        derived_model = vss_model.export()

        for array in derived_model.DataTypeDefinitions.Arrays:
            if array.Namespace == "vss":
                self.assertEqual(array.Size, expected_arrays[array.Name]["size"])
                self.assertEqual(array.TypeRef, expected_arrays[array.Name]["type"])
                expected_arrays[array.Name]["passed"] = True

        for vector in derived_model.DataTypeDefinitions.Vectors:
            if vector.Namespace == "vss":
                self.assertEqual(vector.TypeRef, expected_vectors[vector.Name]["type"])
                expected_vectors[vector.Name]["passed"] = True

        for key, value in (expected_arrays | expected_vectors).items():
            assert value["passed"], f"Expected element {key} not found"


if __name__ == "__main__":
    unittest.main()
