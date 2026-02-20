# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""example tests"""

import os
from pathlib import Path

from vaf.vafgeneration import vaf_core_library

# pylint: disable=too-few-public-methods
# pylint: disable=duplicate-code
# pylint: disable=missing-param-doc
# pylint: disable=missing-type-doc
# mypy: disable-error-code="no-untyped-def"


class TestIntegration:
    """Basic generation test class"""

    @staticmethod
    def __assert_files_identical(f1: Path, f2: Path) -> None:
        assert f1.read_text("utf-8") == f2.read_text("utf-8")

    def test_basic_generation(self, tmp_path) -> None:
        """Basic test for interface generation"""
        script_dir = Path(os.path.realpath(__file__)).parent

        # STD
        vaf_core_library.generate(tmp_path, "std")
        self.__assert_files_identical(
            tmp_path / "src-gen/libs/core_library/CMakeLists.txt",
            script_dir / "core_library/std/CMakeLists.txt",
        )

        # src
        self.__assert_files_identical(
            tmp_path / "src-gen/libs/core_library/src/runtime.cpp",
            script_dir / "core_library/std/src/runtime.cpp",
        )
        self.__assert_files_identical(
            tmp_path / "src-gen/libs/core_library/src/executor.cpp",
            script_dir / "core_library/std/src/executor.cpp",
        )
        self.__assert_files_identical(
            tmp_path / "src-gen/libs/core_library/src/logging.cpp",
            script_dir / "core_library/std/src/logging.cpp",
        )
        self.__assert_files_identical(
            tmp_path / "src-gen/libs/core_library/src/executable_controller_base.cpp",
            script_dir / "core_library/std/src/executable_controller_base.cpp",
        )
        self.__assert_files_identical(
            tmp_path / "src-gen/libs/core_library/src/controller_interface.cpp",
            script_dir / "core_library/std/src/controller_interface.cpp",
        )
        # include
        self.__assert_files_identical(
            tmp_path / "src-gen/libs/core_library/include/vaf/container_types.h",
            script_dir / "core_library/std/include/vaf/container_types.h",
        )
        self.__assert_files_identical(
            tmp_path / "src-gen/libs/core_library/include/vaf/receiver_handler_container.h",
            script_dir / "core_library/std/include/vaf/receiver_handler_container.h",
        )
        self.__assert_files_identical(
            tmp_path / "src-gen/libs/core_library/include/vaf/controller_interface.h",
            script_dir / "core_library/std/include/vaf/controller_interface.h",
        )
        self.__assert_files_identical(
            tmp_path / "src-gen/libs/core_library/include/vaf/data_ptr.h",
            script_dir / "core_library/std/include/vaf/data_ptr.h",
        )
        self.__assert_files_identical(
            tmp_path / "src-gen/libs/core_library/include/vaf/error_domain.h",
            script_dir / "core_library/std/include/vaf/error_domain.h",
        )
        self.__assert_files_identical(
            tmp_path / "src-gen/libs/core_library/include/vaf/executable_controller_base.h",
            script_dir / "core_library/std/include/vaf/executable_controller_base.h",
        )
        self.__assert_files_identical(
            tmp_path / "src-gen/libs/core_library/include/vaf/executable_controller_interface.h",
            script_dir / "core_library/std/include/vaf/executable_controller_interface.h",
        )
        self.__assert_files_identical(
            tmp_path / "src-gen/libs/core_library/include/vaf/executor.h",
            script_dir / "core_library/std/include/vaf/executor.h",
        )
        self.__assert_files_identical(
            tmp_path / "src-gen/libs/core_library/include/vaf/future.h",
            script_dir / "core_library/std/include/vaf/future.h",
        )
        self.__assert_files_identical(
            tmp_path / "src-gen/libs/core_library/include/vaf/logging.h",
            script_dir / "core_library/std/include/vaf/logging.h",
        )
        self.__assert_files_identical(
            tmp_path / "src-gen/libs/core_library/include/vaf/module_states.h",
            script_dir / "core_library/std/include/vaf/module_states.h",
        )
        self.__assert_files_identical(
            tmp_path / "src-gen/libs/core_library/include/vaf/result.h",
            script_dir / "core_library/std/include/vaf/result.h",
        )
        self.__assert_files_identical(
            tmp_path / "src-gen/libs/core_library/include/vaf/runtime.h",
            script_dir / "core_library/std/include/vaf/runtime.h",
        )
        self.__assert_files_identical(
            tmp_path / "src-gen/libs/core_library/include/vaf/user_controller_interface.h",
            script_dir / "core_library/std/include/vaf/user_controller_interface.h",
        )
        self.__assert_files_identical(
            tmp_path / "src-gen/libs/core_library/include/vaf/output_sync_stream.h",
            script_dir / "core_library/std/include/vaf/output_sync_stream.h",
        )
        # internal
        self.__assert_files_identical(
            tmp_path / "src-gen/libs/core_library/include/vaf/internal/data_ptr_helper.h",
            script_dir / "core_library/std/include/vaf/internal/data_ptr_helper.h",
        )
