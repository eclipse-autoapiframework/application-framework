# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""SIL Kit generator test."""

# pylint: disable=duplicate-code
import copy
import filecmp
import os
from pathlib import Path

from vaf import vafmodel
from vaf.vafgeneration import vaf_silkit


# pylint: disable=too-many-statements
# pylint: disable=missing-any-param-doc
# pylint: disable=missing-param-doc
# pylint: disable=missing-type-doc
# pylint: disable=too-few-public-methods
# mypy: disable-error-code="no-untyped-def"
class TestIntegration:
    """Basic generation test class"""

    def test_basic_generation(self, tmp_path) -> None:  # pylint: disable=too-many-locals
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
        amci = vafmodel.ApplicationModuleConsumedInterface(
            ModuleInterfaceRef=m.ModuleInterfaces[0], InstanceName="ConsumedInstance"
        )
        ampi = vafmodel.ApplicationModuleProvidedInterface(
            ModuleInterfaceRef=m.ModuleInterfaces[0], InstanceName="ProvidedInstance"
        )

        am = vafmodel.ApplicationModule(
            Name="MyApplicationModule",
            Namespace="test",
            ConsumedInterfaces=[amci],
            ProvidedInterfaces=[ampi],
            PersistencyFiles=[],
        )

        m.ApplicationModules.append(am)

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

        iitmm1 = vafmodel.InterfaceInstanceToModuleMapping(
            InstanceName="ConsumedInstance", ModuleRef=m.PlatformConsumerModules[0]
        )
        iitmm2 = vafmodel.InterfaceInstanceToModuleMapping(
            InstanceName="ProvidedInstance", ModuleRef=m.PlatformProviderModules[0]
        )

        eap = vafmodel.ExecutableApplicationModuleMapping(
            ApplicationModuleRef=am, InterfaceInstanceToModuleMappings=[iitmm1, iitmm2], TaskMapping=[]
        )

        e = vafmodel.Executable(Name="MyExecutable", ExecutorPeriod="10ms", ApplicationModules=[eap])

        m.Executables.append(e)

        vaf_silkit.generate(m, tmp_path)

        script_dir = Path(os.path.realpath(__file__)).parent

        assert filecmp.cmp(
            tmp_path
            / "src-gen/libs/platform_silkit/platform_consumer_modules/my_consumer_module/include/test/my_consumer_module.h",  # pylint: disable=line-too-long
            script_dir / "silkit/my_consumer_module.h",
        )

        assert filecmp.cmp(
            tmp_path
            / "src-gen/libs/platform_silkit/platform_consumer_modules/my_consumer_module/src/test/my_consumer_module.cpp",  # pylint: disable=line-too-long
            script_dir / "silkit/my_consumer_module.cpp",
        )

        pm_path = tmp_path / "src-gen/libs/platform_silkit/platform_provider_modules/my_provider_module"
        assert filecmp.cmp(
            pm_path / "include/test/my_provider_module.h",
            script_dir / "silkit/my_provider_module.h",
        )

        assert filecmp.cmp(
            pm_path / "src/test/my_provider_module.cpp",
            script_dir / "silkit/my_provider_module.cpp",
        )


# pylint: enable=too-many-statements
