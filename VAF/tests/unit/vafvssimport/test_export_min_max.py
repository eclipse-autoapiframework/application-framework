# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for ensuring that min and max values are correctly exported for elements with unit 'percent'."""

import unittest
from typing import Any

from vaf.vafvssimport.vss.vss_model import VSS

# pylint: disable=duplicate-code


class TestExportMinMaxForPercent(unittest.TestCase):
    """Tests the export of min and max values from VSS JSON."""

    def setUp(self) -> None:
        """Set up mock data for testing."""
        self.mock_vss_data = {
            "RoadFriction": {
                "children": {
                    "LowerBound": {
                        "datatype": "float",
                        "description": "Lower bound road friction",
                        "max": 100,
                        "min": 0,
                        "type": "sensor",
                        "unit": "percent",
                    },
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
                },
                "type": "branch",
            }
        }

    def test_export_with_min_max(self) -> None:
        """Test that min and max values for percent-based fields are correctly exported."""
        vss_model = VSS(self.mock_vss_data)
        derived_model = vss_model.export()
        elements = derived_model.DataTypeDefinitions.TypeRefs

        expected_elements: dict[str, Any] = {
            "LowerBound": {"min": 0, "max": 100, "passed": False},
            "NonPercentField": {"min": 0, "max": 55.3, "passed": False},
            "NonLimitField": {"min": None, "max": None, "passed": False},
        }

        self.assertEqual(len(elements), len(expected_elements))
        for element in elements:
            self.assertEqual(
                element.Min,
                expected_elements[element.Name]["min"],
                f"in subelement {element.Name}",
            )
            self.assertEqual(
                element.Max,
                expected_elements[element.Name]["max"],
                f"in subelement {element.Name}",
            )
            expected_elements[element.Name]["passed"] = True

        for key, value in expected_elements.items():
            assert value["passed"], f"Expected element {key} not found"


if __name__ == "__main__":
    unittest.main()
