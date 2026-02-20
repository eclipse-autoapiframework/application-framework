from pathlib import Path

from conan import ConanFile
from conan.tools.cmake import cmake_layout
from conan.tools.files import load


class VafRecipe(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"

    def requirements(self):
        self.requires("gtest/1.13.0")

        for dependency in load(self, Path(__file__).resolve().parent / "src-gen" / "conan_deps.list").splitlines():
            self.requires(dependency)

    def layout(self):
        cmake_layout(self)
