# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Generator for conan dependencies based on used VAF features.
Generates
    - src-gen/conan_deps.list
"""

from pathlib import Path

from vaf import vafmodel

from .generation import FileHelper, Generator

CONAN_DEPENDENCY_MAP = {
    "protobuf": ["protobuf/5.27.0"],
    "leveldb": ["leveldb/1.23"],
}


def _generate_dependencies(generator: Generator, model: vafmodel.MainModel, verbose_mode: bool) -> None:
    deps: set[str] = set()

    if model.is_silkit_used or model.is_persistency_used:
        deps.update(CONAN_DEPENDENCY_MAP["protobuf"])
        deps.update(CONAN_DEPENDENCY_MAP["leveldb"])

    generator.generate_to_file(
        FileHelper("conan_deps", "", True),
        ".list",
        "vaf_conan/conan_deps.list.jinja",
        dependencies=deps,
        verbose_mode=verbose_mode,
    )


def generate(model: vafmodel.MainModel, output_dir: Path, verbose_mode: bool = False) -> None:
    """Generate files for conan

    Args:
        model (vafmodel.MainModel): The model
        output_dir (Path): Base output directory
        verbose_mode: flag to enable verbose_mode mode
    """
    generator = Generator()

    generator.set_base_directory(output_dir / "src-gen")
    _generate_dependencies(generator, model, verbose_mode)
