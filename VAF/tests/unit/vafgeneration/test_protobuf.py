# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Protobuf generator test."""

# pylint: disable=duplicate-code
import copy
import filecmp
import os
from pathlib import Path

from vaf import vafmodel
from vaf.vafgeneration import vaf_protobuf_serdes
from vaf.vafpy import import_model


# pylint: disable=too-many-statements
# pylint: disable=missing-any-param-doc
# pylint: disable=missing-param-doc
# pylint: disable=missing-type-doc
# pylint: disable=too-few-public-methods
# mypy: disable-error-code="no-untyped-def"
class TestIntegration:
    """Basic generation test class"""

    def test_basic_generation(self, tmp_path) -> None:
        """Basic test for silkit generation"""
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
        m.DataTypeDefinitions.Vectors.append(
            vafmodel.Vector(
                Name="MyVector",
                Namespace="test",
                TypeRef=vafmodel.DataType(Name="uint8_t", Namespace=""),
            )
        )
        sub1 = vafmodel.SubElement(
            Name="MySub1",
            TypeRef=vafmodel.DataType(Name="MyStruct", Namespace="test2"),
        )
        sub2 = vafmodel.SubElement(
            Name="MySub2",
            TypeRef=vafmodel.DataType(Name="MyVector", Namespace="test"),
        )
        m.DataTypeDefinitions.Structs.append(
            vafmodel.Struct(
                Name="MyStruct",
                Namespace="test",
                SubElements=[sub1, sub2],
            )
        )
        m.DataTypeDefinitions.Strings.append(
            vafmodel.String(
                Name="MyString",
                Namespace="test",
            )
        )
        literals = [
            vafmodel.EnumLiteral(
                Item="MyLit1",
                Value=0,
            ),
            vafmodel.EnumLiteral(
                Item="MyLit2",
                Value=1,
            ),
            vafmodel.EnumLiteral(
                Item="MyLit3",
                Value=4,
            ),
        ]
        m.DataTypeDefinitions.Enums.append(
            vafmodel.VafEnum(
                Name="MyEnum",
                Namespace="test",
                Literals=literals,
            )
        )
        m.DataTypeDefinitions.Maps.append(
            vafmodel.Map(
                Name="MyMap",
                Namespace="test",
                MapKeyTypeRef=vafmodel.DataType(Name="uint64_t", Namespace=""),
                MapValueTypeRef=vafmodel.DataType(Name="MyString", Namespace="test"),
            )
        )
        m.DataTypeDefinitions.TypeRefs.append(
            vafmodel.TypeRef(
                Name="MyTypeRef",
                Namespace="test",
                TypeRef=vafmodel.DataType(Name="uint64_t", Namespace=""),
            )
        )

        m.DataTypeDefinitions.Arrays.append(
            vafmodel.Array(
                Name="MyArray",
                Namespace="test2",
                TypeRef=vafmodel.DataType(Name="uint64_t", Namespace=""),
                Size=1,
            )
        )
        m.DataTypeDefinitions.Vectors.append(
            vafmodel.Vector(
                Name="MyVector",
                Namespace="test2",
                TypeRef=vafmodel.DataType(Name="uint8_t", Namespace=""),
            )
        )
        sub1 = vafmodel.SubElement(
            Name="MySub1",
            TypeRef=vafmodel.DataType(Name="MyStruct", Namespace="test2"),
        )
        sub2 = vafmodel.SubElement(
            Name="MySub2",
            TypeRef=vafmodel.DataType(Name="MyVector", Namespace="test2"),
        )
        m.DataTypeDefinitions.Structs.append(
            vafmodel.Struct(
                Name="MyStruct",
                Namespace="test2",
                SubElements=[sub1, sub2],
            )
        )

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
                InitialValue="{64}",
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

        operations.append(
            vafmodel.Operation(
                Name="MyGetter",
                Parameters=[
                    vafmodel.Parameter(
                        Name="a",
                        TypeRef=vafmodel.DataType(Name="uint64_t", Namespace=""),
                        Direction=vafmodel.ParameterDirection.OUT,
                    )
                ],
            )
        )

        operations.append(
            vafmodel.Operation(
                Name="MySetter",
                Parameters=[
                    vafmodel.Parameter(
                        Name="a",
                        TypeRef=vafmodel.DataType(Name="uint64_t", Namespace=""),
                        Direction=vafmodel.ParameterDirection.IN,
                    )
                ],
            )
        )

        m.ModuleInterfaces.append(
            vafmodel.ModuleInterface(
                Name="MyInterface",
                Namespace="test",
                DataElements=data_elements,
                Operations=operations,
            )
        )

        silkit_connection_point = vafmodel.SILKITConnectionPoint(
            Name="CPoint", SilkitInstance="MyInterface", SilkitInstanceIsOptional=False
        )

        m.PlatformProviderModules.append(
            vafmodel.PlatformModule(
                Name="MyProviderModule",
                Namespace="test",
                ModuleInterfaceRef=m.ModuleInterfaces[0],
                OriginalEcoSystem=vafmodel.OriginalEcoSystemEnum.SILKIT,
                ConnectionPointRef=silkit_connection_point,
            )
        )

        m.PlatformConsumerModules.append(copy.deepcopy(m.PlatformProviderModules[0]))
        m.PlatformConsumerModules[0].Name = "MyConsumerModule"

        m.SILKITAdditionalConfiguration = vafmodel.SILKITAdditionalConfigurationType(
            ConnectionPoints=[silkit_connection_point],
        )

        tmp_file = tmp_path / "tmp.json"
        with open(tmp_file, "w", encoding="utf-8") as f:
            f.write(m.model_dump_json(indent=2, exclude_none=True, exclude_defaults=True, by_alias=True))

        import_model(str(tmp_file))

        vaf_protobuf_serdes.generate(tmp_path)

        script_dir = Path(os.path.realpath(__file__)).parent

        pm_path = tmp_path / "src-gen/libs/protobuf_serdes"
        assert filecmp.cmp(
            pm_path / "CMakeLists.txt",
            script_dir / "protobuf_serdes/CMakeLists.txt",
        )

        pm_path = tmp_path / "src-gen/libs/protobuf_serdes/proto"
        assert filecmp.cmp(
            pm_path / "CMakeLists.txt",
            script_dir / "protobuf_serdes/proto/CMakeLists.txt",
        )
        assert filecmp.cmp(
            pm_path / "protobuf_test.proto",
            script_dir / "protobuf_serdes/proto/protobuf_test.proto",
        )
        assert filecmp.cmp(
            pm_path / "protobuf_test2.proto",
            script_dir / "protobuf_serdes/proto/protobuf_test2.proto",
        )
        assert filecmp.cmp(
            pm_path / "protobuf_basetypes.proto",
            script_dir / "protobuf_serdes/proto/protobuf_basetypes.proto",
        )
        assert filecmp.cmp(
            pm_path / "protobuf_interface_test_MyInterface.proto",
            script_dir / "protobuf_serdes/proto/protobuf_interface_test_MyInterface.proto",
        )

        pm_path = tmp_path / "src-gen/libs/protobuf_serdes/transformer"
        assert filecmp.cmp(
            pm_path / "CMakeLists.txt",
            script_dir / "protobuf_serdes/transformer/CMakeLists.txt",
        )
        assert filecmp.cmp(
            pm_path / "include/protobuf/interface/test/myinterface/protobuf_transformer.h",
            script_dir
            / "protobuf_serdes/transformer/include/protobuf/interface/test/myinterface/protobuf_transformer.h",
        )
        # assert filecmp.cmp(
        #     pm_path / "include/protobuf/test/protobuf_transformer.h",
        #     script_dir / "protobuf_serdes/transformer/include/protobuf/test/protobuf_transformer.h",
        # )
        assert filecmp.cmp(
            pm_path / "include/protobuf/test2/protobuf_transformer.h",
            script_dir / "protobuf_serdes/transformer/include/protobuf/test2/protobuf_transformer.h",
        )

    def test_optional_struct_fields_protobuf_generation(self, tmp_path: Path) -> None:
        """
        Test that struct fields with IsOptional=True generate 'optional' keyword in protobuf.
        This follows TDD approach - test first, then implement.
        """
        # Create model with optional struct fields
        m = vafmodel.MainModel()
        m.DataTypeDefinitions = vafmodel.DataTypeDefinition()

        # Create struct with mixed optional and non-optional fields
        m.DataTypeDefinitions.Structs.append(
            vafmodel.Struct(
                Name="OptionalTestStruct",
                Namespace="test::optional",
                SubElements=[
                    vafmodel.SubElement(
                        Name="required_field",
                        TypeRef=vafmodel.DataType(Name="uint64_t", Namespace=""),
                        IsOptional=False,  # Required field
                    ),
                    vafmodel.SubElement(
                        Name="optional_field",
                        TypeRef=vafmodel.DataType(Name="uint32_t", Namespace=""),
                        IsOptional=True,  # Optional field
                    ),
                    vafmodel.SubElement(
                        Name="another_optional",
                        TypeRef=vafmodel.DataType(Name="int32_t", Namespace=""),
                        IsOptional=True,  # Optional field
                    ),
                ],
            )
        )

        # Write model to JSON and import it
        with open(tmp_path / "model.json", "w", encoding="utf-8") as file:
            file.write(m.model_dump_json(indent=2, exclude_none=True, exclude_defaults=True, by_alias=True))
        import_model(str(tmp_path / "model.json"))

        # Generate protobuf files
        vaf_protobuf_serdes.generate(tmp_path)

        # Read generated proto file
        proto_file = tmp_path / "src-gen/libs/protobuf_serdes/proto/protobuf_test_optional.proto"
        assert proto_file.exists(), "Protobuf file should be generated"

        proto_content = proto_file.read_text()

        # Verify the message structure
        assert "message OptionalTestStruct {" in proto_content, "OptionalTestStruct message should exist"

        # Verify required_field does NOT have 'optional' keyword
        assert "uint64 required_field = 1;" in proto_content, "required_field should not have 'optional' keyword"

        # Verify optional_field HAS 'optional' keyword
        assert "optional uint32 optional_field = 2;" in proto_content, "optional_field should have 'optional' keyword"

        # Verify another_optional HAS 'optional' keyword
        assert "optional int32 another_optional = 3;" in proto_content, (
            "another_optional should have 'optional' keyword"
        )

    def test_all_optional_struct_fields(self, tmp_path: Path) -> None:
        """Test struct with all optional fields"""
        m = vafmodel.MainModel()
        m.DataTypeDefinitions = vafmodel.DataTypeDefinition()

        m.DataTypeDefinitions.Structs.append(
            vafmodel.Struct(
                Name="AllOptionalStruct",
                Namespace="test::alloptional",
                SubElements=[
                    vafmodel.SubElement(
                        Name="field1",
                        TypeRef=vafmodel.DataType(Name="uint32_t", Namespace=""),
                        IsOptional=True,
                    ),
                    vafmodel.SubElement(
                        Name="field2",
                        TypeRef=vafmodel.DataType(Name="int32_t", Namespace=""),
                        IsOptional=True,
                    ),
                ],
            )
        )

        with open(tmp_path / "model.json", "w", encoding="utf-8") as file:
            file.write(m.model_dump_json(indent=2, exclude_none=True, exclude_defaults=True, by_alias=True))
        import_model(str(tmp_path / "model.json"))

        vaf_protobuf_serdes.generate(tmp_path)

        proto_file = tmp_path / "src-gen/libs/protobuf_serdes/proto/protobuf_test_alloptional.proto"
        assert proto_file.exists()

        proto_content = proto_file.read_text()

        # Both fields should have 'optional' keyword
        assert "optional uint32 field1 = 1;" in proto_content
        assert "optional int32 field2 = 2;" in proto_content

    def test_backward_compatibility_no_optional_fields(self, tmp_path: Path) -> None:
        """Test backward compatibility - structs without IsOptional should work as before"""
        m = vafmodel.MainModel()
        m.DataTypeDefinitions = vafmodel.DataTypeDefinition()

        m.DataTypeDefinitions.Structs.append(
            vafmodel.Struct(
                Name="RequiredOnlyStruct",
                Namespace="test::required",
                SubElements=[
                    vafmodel.SubElement(
                        Name="field1",
                        TypeRef=vafmodel.DataType(Name="uint64_t", Namespace=""),
                        IsOptional=False,
                    ),
                    vafmodel.SubElement(
                        Name="field2",
                        TypeRef=vafmodel.DataType(Name="uint32_t", Namespace=""),
                        IsOptional=False,
                    ),
                ],
            )
        )

        with open(tmp_path / "model.json", "w", encoding="utf-8") as file:
            file.write(m.model_dump_json(indent=2, exclude_none=True, exclude_defaults=True, by_alias=True))
        import_model(str(tmp_path / "model.json"))

        vaf_protobuf_serdes.generate(tmp_path)

        proto_file = tmp_path / "src-gen/libs/protobuf_serdes/proto/protobuf_test_required.proto"
        assert proto_file.exists()

        proto_content = proto_file.read_text()

        # No 'optional' keyword should appear
        assert "uint64 field1 = 1;" in proto_content
        assert "uint32 field2 = 2;" in proto_content
        # Verify 'optional' doesn't appear before these fields
        assert "optional uint64 field1" not in proto_content
        assert "optional uint32 field2" not in proto_content


# pylint: enable=too-many-statements
