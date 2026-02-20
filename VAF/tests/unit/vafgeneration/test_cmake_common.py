# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Tests for cmake common."""

import filecmp
import os
from pathlib import Path

from vaf import vafmodel
from vaf.vafgeneration import vaf_cmake_common

# pylint: disable=too-few-public-methods
# pylint: disable=duplicate-code
# pylint: disable=line-too-long
# pylint: disable=missing-param-doc
# pylint: disable=missing-type-doc
# mypy: disable-error-code="no-untyped-def"


class TestIntegration:
    """Basic generation test class"""

    def test_basic_generation(self, tmp_path) -> None:
        """Basic test for cmake common generation"""

        m = vafmodel.MainModel()
        m.ModuleInterfaces.append(vafmodel.ModuleInterface(Name="MyInterface", Namespace="test"))
        m.ApplicationModules.append(
            vafmodel.ApplicationModule(
                Name="MyApp",
                Namespace="test",
                ConsumedInterfaces=[],
                ProvidedInterfaces=[],
                PersistencyFiles=[],
            )
        )

        vaf_module = vafmodel.PlatformModule(
            Name="MyModule",
            Namespace="test",
            ModuleInterfaceRef=m.ModuleInterfaces[0],
            OriginalEcoSystem=vafmodel.OriginalEcoSystemEnum.SILKIT,
            ConnectionPointRef=vafmodel.SILKITConnectionPoint(
                Name="MyConnectionPoint1", SilkitInstance="MySilkitInstance"
            ),
        )

        m.PlatformProviderModules.append(vaf_module)

        mapping = vafmodel.ExecutableApplicationModuleMapping(
            ApplicationModuleRef=m.ApplicationModules[0],
            InterfaceInstanceToModuleMappings=[
                vafmodel.InterfaceInstanceToModuleMapping(InstanceName="instance1", ModuleRef=vaf_module)
            ],
            TaskMapping=[],
        )

        m.Executables.append(
            vafmodel.Executable(
                Name="MyExecutable",
                ExecutorPeriod="10ms",
                InternalCommunicationModules=[vaf_module],
                ApplicationModules=[mapping],
            )
        )

        (tmp_path / "src-gen/executables/already_existing_executable1").mkdir(parents=True, exist_ok=True)
        (tmp_path / "src-gen/executables/already_existing_executable2").mkdir(parents=True, exist_ok=True)

        vaf_cmake_common.generate(m, tmp_path)

        script_dir = Path(os.path.realpath(__file__)).parent

        assert filecmp.cmp(
            tmp_path / "src-gen/CMakeLists.txt",
            script_dir / "cmake_common/cmake.txt",
        )

        assert filecmp.cmp(
            tmp_path / "src-gen/executables/CMakeLists.txt",
            script_dir / "cmake_common/exe_cmake.txt",
        )

        assert filecmp.cmp(
            tmp_path / "src-gen/libs/CMakeLists.txt",
            script_dir / "cmake_common/libs_cmake.txt",
        )

        m.ApplicationModules[0].PersistencyFiles.append("file1.db")
        vaf_cmake_common.generate(m, tmp_path)

        assert filecmp.cmp(
            tmp_path / "src-gen/libs/CMakeLists.txt",
            script_dir / "cmake_common/libs_cmake_append.txt",
        )

        m.ApplicationModules[0].PersistencyFiles.remove("file1.db")

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

        vaf_cmake_common.generate(m, tmp_path)

        assert filecmp.cmp(
            tmp_path / "src-gen/libs/CMakeLists.txt",
            script_dir / "cmake_common/libs_cmake_append2.txt",
        )
