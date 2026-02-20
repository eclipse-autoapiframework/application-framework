# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Generator for CaC support.
Generates CaC Support for a model.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from vaf import vafmodel
from vaf.vafpy import import_model
from vaf.vafpy.core import VafpyAbstractBase
from vaf.vafpy.model_runtime import ModelRuntime

from ..core.common.utils import ProjectType
from .generation import FileHelper, Generator


def __consolidate_namespaces(
    element_by_namespace: Dict[str, Dict[str, Dict[str, VafpyAbstractBase]]],
    generate_elements: List[str],
) -> Dict[str, Any]:
    """Consolidate namespaces' data into common classes for CaC generation
    Args:
        element_by_namespace: dictionary that stores the model data by namespaces
        generate_elements: list of elements to be generated
    Returns:
        dictionary that can be easily accessible by CaC generation
    """
    result: Dict[str, Any] = {}
    # loop over namespace models
    for namespace in sorted(element_by_namespace.keys()):
        # check if current data has relevant information for CaC
        # this is important to prevent creation of empty classes in CaC
        set_elements = [
            key for key, value in element_by_namespace[namespace].items() if value and key in generate_elements
        ]
        # add to CaC result if set_elements is not empty
        if set_elements:
            # get namespace parts -> classes in CaC
            ns_parts = namespace.split("::")
            for level in range(len(ns_parts)):
                # get identifier
                identifier = "::".join(ns_parts[: level + 1])
                # add identifier to dictionary if it hasn't exists
                if identifier not in result:
                    result[identifier] = {
                        "level": level,
                        "set_elements": set_elements if level == len(ns_parts) - 1 else [],
                        "data": element_by_namespace[namespace] if level == len(ns_parts) - 1 else {},
                    }

    return result


def __write_cac_support_file(file_base_name: str, output_dir: Path, **kwargs: Any) -> None:
    """Generates the CaC support file

    Args:
        file_base_name (str): The base name of the generated file
        output_dir (Path): The output directory
    """
    generator = Generator()
    generator.set_base_directory(output_dir)
    python_cac_support = FileHelper(file_base_name, "")
    generator.generate_to_file(python_cac_support, ".py", **kwargs)


def __read_model(input_dir: Path, model_file_name: str) -> None:
    """Read model as model_runtime

    Args:
        input_dir (Path): The input directory
        model_file_name (str): The model file name inside the input directory
    Returns:
        model data as dictionary
    """
    # Read in model
    model_path: Path = input_dir / model_file_name

    ModelRuntime().reset()
    import_model(str(model_path))


def generate(
    input_dir: Path,
    model_file_name: str,
    file_base_name: str,
    output_dir: Path,
    project_type: Optional[ProjectType] = None,
) -> None:
    """Generates Vanilla CaC support file

    Args:
        input_dir (Path): The input directory
        model_file_name (str): The model file name inside the input directory
        file_base_name (str): The base name of the generated file
        output_dir (Path): The output directory
        project_type (ProjectType): type of project that affects the jinja generation
    """
    __read_model(input_dir, model_file_name)

    __write_cac_support_file(
        file_base_name,
        output_dir,
        **{
            "template_path": "vaf_cac_support/platform.py.jinja",
            "cac_model": __consolidate_namespaces(
                ModelRuntime().element_by_namespace,
                generate_elements=[
                    *(vafmodel.data_types if project_type == ProjectType.INTERFACE else []),
                    "Executables",
                    "ModuleInterfaces",
                    "PlatformConsumerModules",
                    "PlatformProviderModules",
                ],
            ),
            "model": ModelRuntime().main_model,
            "model_name": model_file_name,
            "data_types": vafmodel.data_types,
        },
    )
