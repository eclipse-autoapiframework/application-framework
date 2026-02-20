# ruff: noqa: F401
"""Initialize the module.

Could be used to define the public interface of the module.
"""

# Import modules and objects that belong to the public interface  # pylint: disable=W0511
__all__ = [
    "generate_app_module_project_files",
    "generate_application_communication",
    "generate_application_module_project",
    "generate_cac_support",
    "generate_cmake_common",
    "generate_conan_deps",
    "generate_controller",
    "generate_core_library",
    "generate_interface",
    "generate_project",
    "generate_persistency",
    "generate_protobuf_serdes",
    "generate_silkit",
    "generate_std_vaf_data_types",
    "generate_core_library",
]
from .vaf_application_communication import (
    generate as generate_application_communication,
)
from .vaf_application_module import generate_app_module_project_files
from .vaf_cac_support import generate as generate_cac_support
from .vaf_cmake_common import generate as generate_cmake_common
from .vaf_conan import generate as generate_conan_deps
from .vaf_controller import generate as generate_controller
from .vaf_core_library import generate as generate_core_library
from .vaf_generate_application_module import (
    generate_application_module as generate_application_module_project,
)
from .vaf_generate_project import generate_integration_project as generate_project
from .vaf_interface import generate_module_interfaces as generate_interface
from .vaf_persistency import generate as generate_persistency
from .vaf_protobuf_serdes import generate as generate_protobuf_serdes
from .vaf_silkit import generate as generate_silkit
from .vaf_std_data_types import generate as generate_std_vaf_data_types
