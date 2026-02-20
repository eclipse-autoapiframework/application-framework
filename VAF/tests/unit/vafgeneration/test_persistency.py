# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Persistency generator test."""

# pylint: disable=duplicate-code
import copy
import filecmp
import os
from pathlib import Path

from vaf import vafmodel
from vaf.core.common import constants
from vaf.vafgeneration import vaf_persistency


# pylint: disable=too-many-statements
# pylint: disable=missing-any-param-doc
# pylint: disable=missing-param-doc
# pylint: disable=missing-type-doc
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-locals
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
        lit1 = vafmodel.EnumLiteral(
            Item="MyLit1",
            Value=0,
        )
        lit2 = vafmodel.EnumLiteral(
            Item="MyLit2",
            Value=1,
        )
        lit3 = vafmodel.EnumLiteral(
            Item="MyLit3",
            Value=4,
        )
        m.DataTypeDefinitions.Enums.append(
            vafmodel.VafEnum(
                Name="MyEnum",
                Namespace="test",
                Literals=[lit1, lit2, lit3],
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

        m.PlatformProviderModules.append(
            vafmodel.PlatformModule(
                Name="MyProviderModule",
                Namespace="test",
                ModuleInterfaceRef=m.ModuleInterfaces[0],
                OriginalEcoSystem=vafmodel.OriginalEcoSystemEnum.SILKIT,
                ConnectionPointRef=vafmodel.SILKITConnectionPoint(
                    Name="CPoint", SilkitInstance="MyInterface", SilkitInstanceIsOptional=False
                ),
            )
        )

        m.PlatformConsumerModules.append(copy.deepcopy(m.PlatformProviderModules[0]))
        m.PlatformConsumerModules[0].Name = "MyConsumerModule"

        persistencyfile1mapping = vafmodel.PersistencyFileMapping(
            AppModuleName="MyApp",
            FileName="MyFile1",
            FilePath="./MyFile1.db",
            Sync="true",
        )
        persistencyfile2mapping = vafmodel.PersistencyFileMapping(
            AppModuleName="MyApp",
            FileName="MyFile2",
            FilePath="./MyFile2.db",
            Sync="false",
        )

        m.ApplicationModules.append(
            vafmodel.ApplicationModule(
                Name="MyApp1",
                Namespace="test",
                ConsumedInterfaces=[],
                ProvidedInterfaces=[],
                PersistencyFiles=["MyFile1", "MyFileShared"],
                PersistencyInitValues=[
                    vafmodel.PersistencyInitValue(
                        FileName="MyFileShared",
                        Key="Key1Int",
                        TypeRef=vafmodel.DataType(Name="uint8_t", Namespace=""),
                        Value=vafmodel.UInt8Init(InitValue=1),
                    ),
                    vafmodel.PersistencyInitValue(
                        FileName="MyFile1",
                        Key="Key1Array",
                        TypeRef=vafmodel.DataType(Name="MyArray", Namespace="test"),
                        Value=vafmodel.ArrayInit(InitValue=[1, 2, 3]),
                    ),
                ],
                DataTypesForSerialization=[
                    vafmodel.DataTypeForSerialization(TypeRef=vafmodel.DataType(Name="MyArray", Namespace="test"))
                ],
                Tasks=[],
            )
        )

        persistencyfilemapping = [persistencyfile1mapping, persistencyfile2mapping]
        m.Executables.append(
            vafmodel.Executable(
                Name="MyExecutable1",
                ExecutorPeriod="10ms",
                PersistencyModule=vafmodel.ExecutablePersistencyMapping(
                    PersistencyLibrary=constants.PersistencyLibrary.LEVELDB,
                    PersistencyFiles=persistencyfilemapping,
                ),
                ApplicationModules=[
                    vafmodel.ExecutableApplicationModuleMapping(
                        ApplicationModuleRef=m.ApplicationModules[0],
                        InterfaceInstanceToModuleMappings=[
                            vafmodel.InterfaceInstanceToModuleMapping(
                                InstanceName="TestConsumedInterfaceInstance",
                                ModuleRef=m.PlatformConsumerModules[0],
                            ),
                            vafmodel.InterfaceInstanceToModuleMapping(
                                InstanceName="TestProvidedInterfaceInstance",
                                ModuleRef=m.PlatformProviderModules[0],
                            ),
                        ],
                    )
                ],
                InternalCommunicationModules=[],
            )
        )

        vaf_persistency.generate(m, tmp_path)

        script_dir = Path(os.path.realpath(__file__)).parent

        pm_path = tmp_path / "src-gen/libs/interfaces/include/persistency"
        assert filecmp.cmp(
            pm_path / "persistency_interface.h",
            script_dir / "persistency/leveldb/persistency_interface.h",
        )

        pm_path = tmp_path / "src-gen/libs/persistency/"
        assert filecmp.cmp(
            pm_path / "include/persistency/persistency.h",
            script_dir / "persistency/leveldb/persistency.h",
        )
        assert filecmp.cmp(
            pm_path / "src/persistency/persistency.cpp",
            script_dir / "persistency/leveldb/persistency.cpp",
        )


# pylint: enable=too-many-statements
