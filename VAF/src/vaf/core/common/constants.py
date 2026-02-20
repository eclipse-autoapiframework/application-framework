# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Constants relevant for all VAF modules"""

from enum import Enum
from importlib.metadata import PackageNotFoundError, version


class TruthyEnum(Enum):
    """Enum that allows the usage in if/while by checking against the first entry"""

    def __bool__(self) -> bool:
        first_element = list(self.__class__)[0]
        return self != first_element


class PersistencyLibrary(TruthyEnum):
    """Enum class representing persistency libraries"""

    NONE = ""
    LEVELDB = "leveldb"


VAF_CFG_FILE = ".vafconfig.json"

BASE_TYPE = ["float", "double", "bool"]
CSTDINT_TYPE = [
    "uint8_t",
    "uint16_t",
    "uint32_t",
    "uint64_t",
    "int8_t",
    "int16_t",
    "int32_t",
    "int64_t",
]

SUFFIX: dict[str, str] = {
    "old_file": "~",
    "ancestor_file": "~ancestor",
    "new_file": ".new~",
}

# Define pip package name
PACKAGE_NAME = "vaf"


def get_package_version() -> str:
    """
    Fetches the version of the specified package.

    This function uses the `metadata.version` method from the `importlib.metadata` module
    to retrieve the version of the package defined by `PACKAGE_NAME`. If the package
    metadata is not found (e.g., the package is not installed), it returns "unknown".
    If the version contains any .dev*, the function will cut everything after .dev
    and return it as the version.

    Returns:
        str: The version of the package if available, otherwise "unknown".

    Raises:
        None: This function handles `PackageNotFoundError` internally and does not raise it.

    """
    try:
        version_str = version(PACKAGE_NAME)
    except PackageNotFoundError:
        return "unknown"

    # Check if the version is already stable
    # dev suffix means changes in branch that based on the tag before .dev
    # e.g.: tag 0.6.5 == main -> create branch x based on main
    # -> do changes in main -> vaf --version == 0.6.5.dev*
    dev_version = version_str.find(".dev")
    if dev_version > 0:
        return version_str[: dev_version + 4]  # 4 = len(".dev")
    # +d suffix means changes directly on top of the tag before +d
    # e.g.: tag 0.6.5 -> do changes locally after checking out tag -> vaf --version == 0.6.5+d*
    # one of this might caused by the fact that you adapt dependencies in pyproject.toml
    # and then you change version.txt, but you didn't run make start and then commit the uv.lock
    # in docker, then it does make build, which updates uv.lock -> detected as changes on top of version
    d_version = version_str.find("+d")
    if d_version > 0:
        return version_str[: d_version + 2]  # 2 = len("+d")
    return version_str
