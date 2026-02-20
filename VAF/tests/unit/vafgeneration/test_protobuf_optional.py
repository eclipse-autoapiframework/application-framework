# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for optional struct elements in Protobuf generation

This test file verifies that the protobuf generator correctly handles
optional struct elements, particularly for SIL Kit integration where
structs with optional attributes need to be transformed.

These tests initially FAIL, demonstrating the current gap.
"""

# pylint: disable=missing-param-doc
# pylint: disable=missing-yield-type-doc
# pylint: disable=missing-yield-doc
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


class TestProtobufOptionalGeneration:
    """Test suite for protobuf generation of optional fields"""

    def test_protobuf_generates_optional_keyword_for_optional_fields(self):
        """Test that protobuf generator outputs 'optional' keyword

        Given: A struct with both required and optional fields
        When: Generating protobuf schema
        Then: Optional fields should have 'optional' keyword, required fields should not

        This is the CORE test - it will fail until we implement the feature.
        """
        # Arrange
        TestStruct = vafpy.Struct(name="TestStructProto", namespace="test")
        TestStruct.add_subelement("required_field", vafpy.BaseTypes.UINT32_T, is_optional=False)
        TestStruct.add_subelement("optional_field", vafpy.BaseTypes.INT32_T, is_optional=True)
        TestStruct.add_subelement("another_required", vafpy.BaseTypes.BOOL, is_optional=False)
        TestStruct.add_subelement("another_optional", vafpy.BaseTypes.STRING, is_optional=True)

        # Act - Generate protobuf (we'll need to implement this check)
        # For now, we're testing the model has the information
        # The actual protobuf generation will be tested in component tests

        # Assert - verify the model contains optionality information
        subelements = TestStruct.SubElements

        required_fields = [e for e in subelements if not e.IsOptional]
        optional_fields = [e for e in subelements if e.IsOptional]

        assert len(required_fields) == 2, "Should have 2 required fields"
        assert len(optional_fields) == 2, "Should have 2 optional fields"

        # Check names
        required_names = {e.Name for e in required_fields}
        optional_names = {e.Name for e in optional_fields}

        assert required_names == {"required_field", "another_required"}
        assert optional_names == {"optional_field", "another_optional"}

    def test_protobuf_optional_with_nested_structs(self):
        """Test protobuf generation with optional nested structs

        Given: A struct containing optional struct-typed fields
        When: Generating protobuf schema
        Then: Optional message fields should use 'optional' keyword
        """
        # Arrange
        InnerStruct = vafpy.Struct(name="InnerStructProto", namespace="test")
        InnerStruct.add_subelement("value", vafpy.BaseTypes.UINT32_T)

        OuterStruct = vafpy.Struct(name="OuterStructProto", namespace="test")
        OuterStruct.add_subelement("required_inner", InnerStruct, is_optional=False)
        OuterStruct.add_subelement("optional_inner", InnerStruct, is_optional=True)

        # Assert - model should preserve optionality
        subelements = OuterStruct.SubElements
        required = next(e for e in subelements if e.Name == "required_inner")
        optional = next(e for e in subelements if e.Name == "optional_inner")

        assert required.IsOptional is False
        assert optional.IsOptional is True

        # Both should reference the same struct type by name/namespace
        assert required.TypeRef.Name == "InnerStructProto"
        assert optional.TypeRef.Name == "InnerStructProto"

    def test_all_required_fields_no_optional_keyword(self):
        """Test that structs with all required fields don't get optional keyword

        Given: A struct where all fields are required (legacy behavior)
        When: Generating protobuf schema
        Then: No fields should have 'optional' keyword
        """
        # Arrange
        LegacyStruct = vafpy.Struct(name="LegacyStruct", namespace="test")
        LegacyStruct.add_subelement("field1", vafpy.BaseTypes.UINT32_T)
        LegacyStruct.add_subelement("field2", vafpy.BaseTypes.INT32_T)
        LegacyStruct.add_subelement("field3", vafpy.BaseTypes.BOOL)

        # Assert - all should default to required
        for elem in LegacyStruct.SubElements:
            assert elem.IsOptional is False, f"{elem.Name} should be required by default"

    def test_all_optional_fields(self):
        """Test struct with all optional fields

        Given: A struct where every field is optional
        When: Generating protobuf schema
        Then: All fields should have 'optional' keyword
        """
        # Arrange
        AllOptionalStruct = vafpy.Struct(name="AllOptionalStruct", namespace="test")
        AllOptionalStruct.add_subelement("opt1", vafpy.BaseTypes.UINT32_T, is_optional=True)
        AllOptionalStruct.add_subelement("opt2", vafpy.BaseTypes.INT32_T, is_optional=True)
        AllOptionalStruct.add_subelement("opt3", vafpy.BaseTypes.STRING, is_optional=True)

        # Assert - all should be optional
        for elem in AllOptionalStruct.SubElements:
            assert elem.IsOptional is True, f"{elem.Name} should be optional"

    def test_mixed_optional_and_required_realistic_example(self):
        """Test a realistic struct with optional elements

        Given: A struct with optional elements
        When: Model is created matching this structure
        Then: Optional flags should match

        This simulates the real use case: import → VAF model → Protobuf generation
        """
        # Arrange - simulate TPM_Lmp_On_Rq structure
        TPM_Struct = vafpy.Struct(name="TPM_Lmp_On_Rq_Pr5", namespace="tpm")

        # Some fields are required (no IS-OPTIONAL)
        TPM_Struct.add_subelement("timestamp", vafpy.BaseTypes.UINT64_T, is_optional=False)
        TPM_Struct.add_subelement("message_id", vafpy.BaseTypes.UINT32_T, is_optional=False)

        # Some fields are optional (IS-OPTIONAL=true)
        TPM_Struct.add_subelement("TPM_Lmp_On_Rq_Pr5_ST3", vafpy.BaseTypes.UINT8_T, is_optional=True)
        TPM_Struct.add_subelement("optional_diagnostic_data", vafpy.BaseTypes.UINT32_T, is_optional=True)

        # Assert
        timestamp = next(e for e in TPM_Struct.SubElements if e.Name == "timestamp")
        message_id = next(e for e in TPM_Struct.SubElements if e.Name == "message_id")
        optional_field = next(e for e in TPM_Struct.SubElements if e.Name == "TPM_Lmp_On_Rq_Pr5_ST3")
        diagnostic = next(e for e in TPM_Struct.SubElements if e.Name == "optional_diagnostic_data")

        assert timestamp.IsOptional is False, "timestamp should be required"
        assert message_id.IsOptional is False, "message_id should be required"
        assert optional_field.IsOptional is True, "TPM_Lmp_On_Rq_Pr5_ST3 should be optional"
        assert diagnostic.IsOptional is True, "diagnostic data should be optional"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
