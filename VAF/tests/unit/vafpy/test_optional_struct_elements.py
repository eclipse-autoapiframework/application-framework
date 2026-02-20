# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for optional struct elements support

This test file demonstrates the need for optional struct element support,
particularly for ARXML structs with <IS-OPTIONAL>true</IS-OPTIONAL> elements.

The tests here will initially FAIL, showing the gap in our current implementation.
As we implement the feature, these tests should pass.
"""

# pylint: disable=missing-param-doc
# pylint: disable=missing-yield-type-doc
# pylint: disable=missing-yield-doc
# pylint: disable=too-few-public-methods
# mypy: disable-error-code="no-untyped-def"

import pytest

from vaf import vafpy
from vaf.vafpy.model_runtime import ModelRuntime


@pytest.fixture(autouse=True)
def reset_model_runtime():
    """Reset ModelRuntime singleton between tests to avoid duplicate errors."""
    yield
    # Clear the singleton instance after each test
    ModelRuntime.reset()


class TestOptionalStructElements:
    """Test suite for optional struct element functionality"""

    def test_struct_add_subelement_accepts_optional_parameter(self):
        """Test that add_subelement accepts is_optional parameter

        Given: A struct definition
        When: Adding a subelement with is_optional=True
        Then: The subelement should be marked as optional
        """
        # Arrange
        TestStruct = vafpy.Struct(name="TestStruct", namespace="test")

        # Act - this should NOT raise an error
        TestStruct.add_subelement("required_field", vafpy.BaseTypes.UINT32_T)
        TestStruct.add_subelement("optional_field", vafpy.BaseTypes.UINT32_T, is_optional=True)

        # Assert - verify fields were added
        assert len(TestStruct.SubElements) == 2

    def test_struct_subelement_has_optional_attribute(self):
        """Test that struct subelements expose their optional status

        Given: A struct with required and optional fields
        When: Querying the subelement properties
        Then: Optional status should be accessible
        """
        # Arrange
        TestStruct = vafpy.Struct(name="TestStruct2", namespace="test")
        TestStruct.add_subelement("required_field", vafpy.BaseTypes.UINT32_T, is_optional=False)
        TestStruct.add_subelement("optional_field", vafpy.BaseTypes.UINT32_T, is_optional=True)

        # Act
        subelements = TestStruct.SubElements

        # Assert - find elements and check optional status
        required_elem = next(e for e in subelements if e.Name == "required_field")
        optional_elem = next(e for e in subelements if e.Name == "optional_field")

        # These attributes should exist and have correct values
        assert hasattr(required_elem, "IsOptional"), "SubElement should have IsOptional attribute"
        assert required_elem.IsOptional is False, "required_field should not be optional"
        assert optional_elem.IsOptional is True, "optional_field should be optional"

    def test_optional_parameter_defaults_to_false(self):
        """Test that is_optional defaults to False for backward compatibility

        Given: Existing code that doesn't specify is_optional
        When: Adding subelements without the optional parameter
        Then: Elements should default to required (is_optional=False)
        """
        # Arrange
        TestStruct = vafpy.Struct(name="TestStruct3", namespace="test")

        # Act - add element without specifying optional (old API usage)
        TestStruct.add_subelement("legacy_field", vafpy.BaseTypes.UINT32_T)

        # Assert
        elem = TestStruct.SubElements[0]
        assert hasattr(elem, "IsOptional"), "SubElement should have IsOptional attribute"
        assert elem.IsOptional is False, "Default should be False (required)"

    def test_optional_with_complex_types(self):
        """Test optional fields work with complex types (nested structs, arrays, etc.)

        Given: Structs with complex type hierarchies
        When: Marking nested structs or arrays as optional
        Then: Optionality should be preserved
        """
        # Arrange
        InnerStruct = vafpy.Struct(name="InnerStruct", namespace="test")
        InnerStruct.add_subelement("inner_value", vafpy.BaseTypes.UINT32_T)

        OuterStruct = vafpy.Struct(name="OuterStruct", namespace="test")

        # Act - optional nested struct
        OuterStruct.add_subelement("required_inner", InnerStruct, is_optional=False)
        OuterStruct.add_subelement("optional_inner", InnerStruct, is_optional=True)

        # Assert
        required = next(e for e in OuterStruct.SubElements if e.Name == "required_inner")
        optional = next(e for e in OuterStruct.SubElements if e.Name == "optional_inner")

        assert required.IsOptional is False
        assert optional.IsOptional is True

    def test_optional_array_elements(self):
        """Test that array elements can be marked as optional

        Given: A struct with array type elements
        When: Marking an array as optional
        Then: The entire array should be optional (not the elements within)
        """
        # Arrange
        TestStruct = vafpy.Struct(name="TestStruct5", namespace="test")
        ArrayType = vafpy.Array(name="TestArray5", namespace="test", datatype=vafpy.BaseTypes.UINT32_T, size=10)

        # Act
        TestStruct.add_subelement("required_array", ArrayType, is_optional=False)
        TestStruct.add_subelement("optional_array", ArrayType, is_optional=True)

        # Assert
        required = next(e for e in TestStruct.SubElements if e.Name == "required_array")
        optional = next(e for e in TestStruct.SubElements if e.Name == "optional_array")

        assert required.IsOptional is False
        assert optional.IsOptional is True


class TestOptionalStructElementsModelSerialization:
    """Test that optional fields are properly serialized to/from model.json"""

    def test_optional_field_serialized_to_json(self):
        """Test that IsOptional attribute is included in JSON serialization

        Given: A struct with optional fields
        When: Serializing to JSON (model.json)
        Then: IsOptional attribute should be present in output
        """
        ModelRuntime()

        TestStruct = vafpy.Struct(name="TestStruct6", namespace="test")
        TestStruct.add_subelement("optional_field", vafpy.BaseTypes.UINT32_T, is_optional=True)

        # Act - use pydantic's model_dump method
        json_dict = TestStruct.model_dump()

        # Assert
        subelements = json_dict.get("SubElements", [])
        assert len(subelements) == 1
        optional_elem = subelements[0]

        # IsOptional should be in the serialized form
        assert "IsOptional" in optional_elem, "IsOptional should be serialized to JSON"
        assert optional_elem["IsOptional"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
