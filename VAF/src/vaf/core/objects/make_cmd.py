# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""This module contains the implementation of the make commands."""

import os
import subprocess
from pathlib import Path

from vaf.core.common.utils import ProjectType, get_project_type


class MakeCmd:
    """Class implementing the make related commands"""

    def __init__(self, verbose_mode: bool = False) -> None:
        """
        Ctor for CmdProject class
        Args:
            verbose_mode (bool): Flag to enable verbose mode
        """
        self.verbose_mode = verbose_mode

    @staticmethod
    def __ensure_subprocess_run(subprocess_result: subprocess.CompletedProcess[bytes], error_msg: str) -> None:
        """Method to ensure subprocess run
        Args:
            subprocess_result: returns of subprocess.run, make sure stderr=subprocess.PIPE to be captured
            error_msg: string as error msg in case run fails
        """
        if subprocess_result.returncode != 0:
            raise RuntimeError(f"{error_msg} ERROR: \n{subprocess_result.stderr.decode('utf-8')}")

    def preset(self, build_dir: str, compiler: str, build_type: str, defines: str, cwd: str) -> None:  # pylint: disable=too-many-arguments, too-many-positional-arguments
        """
        Preset.

        Args:
            build_dir: Build directory
            compiler: Compiler version
            build_type: Debug or release build
            defines: Additional defines
            cwd: Current working directory

        Raises:
            RuntimeError: in case conan install or cmake preset fails!

        """
        opt_build_dir = "tools.cmake.cmake_layout:build_folder=" + build_dir
        opt_compiler = "-pr:a=" + cwd + "/.conan/" + compiler
        opt_type = "build_type=" + build_type
        result = subprocess.run(
            [
                "conan",
                "install",
                cwd,
                opt_compiler,
                "-s",
                opt_type,
                "-c",
                opt_build_dir,
                "--build=missing",
            ],
            check=False,
            stderr=subprocess.PIPE,  # capture stderr -> will not shown in console
            stdout=None if self.verbose_mode else subprocess.DEVNULL,
        )
        self.__ensure_subprocess_run(result, "Conan Install failed")

        current_dir = Path.cwd()
        os.chdir(cwd)  # cmake --preset must run in project root directory
        result = subprocess.run(
            ["cmake", "--preset", f"conan-{build_type.lower()}", defines],
            check=False,
            stderr=subprocess.PIPE,  # capture stderr -> will not shown in console
            stdout=None if self.verbose_mode else subprocess.DEVNULL,
        )
        self.__ensure_subprocess_run(result, "CMake Preset failed")

        os.chdir(current_dir)

    def build(self, preset: str) -> None:
        """
        Build.

        Args:
            preset: CMake preset

        """
        cpu_count = os.cpu_count() or 1
        result = subprocess.run(
            ["cmake", "--build", "--preset", preset, "--parallel", str(cpu_count)],
            check=False,
            stderr=subprocess.PIPE,  # capture stderr -> will not shown in console
            stdout=None,
        )
        self.__ensure_subprocess_run(result, "CMake Build failed")

    def clean(self, preset: str) -> None:
        """
        Clean.

        Args:
            preset: CMake preset

        """
        result = subprocess.run(
            ["cmake", "--build", "--target", "clean", "--preset", preset],
            check=False,
            stderr=subprocess.PIPE,  # capture stderr -> will not shown in console
            stdout=None,
        )
        self.__ensure_subprocess_run(result, "CMake Clean failed")

    def clean_all(self) -> None:
        """
        Clean all.
        """
        result: subprocess.CompletedProcess[bytes] = subprocess.run(
            ["rm", "-rf", "./build"],
            check=False,
            stderr=subprocess.PIPE,  # capture stderr -> will not shown in console
            stdout=None,
        )
        self.__ensure_subprocess_run(result, "CMake Clean failed")

    def install(self, preset: str) -> None:
        """
        Install.

        Args:
            preset: CMake preset

        """
        cpu_count = os.cpu_count() or 1
        project_type = get_project_type()
        # check for executables and install folder
        if (
            project_type == ProjectType.APP_MODULE
            or [fp.is_dir() for fp in Path.cwd().glob("build/**/install")]
            or (Path("src/executables").is_dir() and any(fp.is_dir() for fp in Path("src/executables").iterdir()))
        ):
            result = subprocess.run(
                [
                    "cmake",
                    "--build",
                    "--target",
                    "install",
                    "--preset",
                    preset,
                    "--parallel",
                    str(cpu_count),
                ],
                check=False,
                stderr=subprocess.PIPE,  # capture stderr -> will not shown in console
                stdout=None,
            )
            self.__ensure_subprocess_run(result, "CMake Install failed")
        else:
            print("No executables to be installed.")
