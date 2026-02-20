# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Runtime for building a complete model with Config as Code."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from vaf import vafmodel
from vaf.vafpy.factory import VafpyFactory
from vaf.vafpy.validator import CleanupOverride

from ..core.common.utils import ProjectType
from .core import ModelError, VafpyAbstractBase
from .datatypes import Array, Enum, Map, String, Struct, TypeRef, VafpyFactoryWithTypeRef, Vector
from .elements import (
    ApplicationModule,
    ModuleInterface,
    PlatformConsumerModule,
    PlatformProviderModule,
    VafpyModuleInterfaceFactory,
)
from .model_runtime import ModelRuntime


def get_main_model() -> Any:
    """Get the main model as JSON

    Returns:
        Any: The model
    """
    return json.loads(ModelRuntime().main_model.model_dump_json(indent=2, exclude_none=True, exclude_defaults=True))


def save_main_model(
    path: Path,
    project_type: ProjectType,
    cleanup: CleanupOverride = CleanupOverride.DEFAULT,
    skip_validation: bool = False,
) -> None:
    """Saves the main model to file

    Args:
        path (Path): Path to the file
        project_type (ProjectType): Type of the current project
        cleanup (bool): Boolean flag to remove unused data elements & module interfaces in model
        skip_validation (bool): Boolean flag to indicate the need for model validation
    """
    ModelRuntime().save(path, project_type, keys=None, cleanup=cleanup, skip_validation=skip_validation)


def save_part_of_main_model(
    path: Path,
    keys: list[str],
    project_type: ProjectType,
    cleanup: CleanupOverride = CleanupOverride.DEFAULT,
    skip_validation: bool = False,
) -> None:
    """Saves the main model to file

    Args:
        path (Path): Path to the file
        keys: (list[str]): Key to be saved in the export
        project_type (ProjectType): Type of the current project
        cleanup: (bool): Boolean flag to remove unused data elements & module interfaces in model
        skip_validation (bool): Boolean flag to indicate the need for model validation
    """
    ModelRuntime().save(path, project_type, keys=keys, cleanup=cleanup, skip_validation=skip_validation)


class _ModelReader:
    __vafpy_factory_dict: Dict[str, Tuple[type[VafpyFactory], type[VafpyAbstractBase]]] = {
        "ApplicationModule": (VafpyFactory, ApplicationModule),
        "Array": (VafpyFactoryWithTypeRef, Array),
        "Enum": (VafpyFactory, Enum),
        "Map": (VafpyFactory, Map),
        "ModuleInterface": (VafpyModuleInterfaceFactory, ModuleInterface),
        "PlatformConsumerModule": (VafpyFactory, PlatformConsumerModule),
        "PlatformProviderModule": (VafpyFactory, PlatformProviderModule),
        "String": (VafpyFactory, String),
        "Struct": (VafpyFactory, Struct),
        "TypeRef": (VafpyFactoryWithTypeRef, TypeRef),
        "Vector": (VafpyFactoryWithTypeRef, Vector),
    }

    @classmethod
    def create_vafpy_from_vafmodel(
        cls,
        data: vafmodel.VafBaseModel,
        element_type: str,
    ) -> None:
        """Method to create vafpy element based on vafmodel
        Args:
            data: vafmodel element to be converted to vafpy
            element_type: string that describe the element type
        """
        # construct vafpy object from vafmodel via Factory class
        assert element_type in cls.__vafpy_factory_dict, f"ERROR: invalid Element {element_type}"
        factory, vafpy_cls = cls.__vafpy_factory_dict[element_type]
        factory.create_from_model(vaf_model=data, vafpy_class=vafpy_cls, imported=True)

    @classmethod
    def read_model(  # pylint:disable=too-many-nested-blocks
        cls,
        path: str,
        import_type: str,
        am_path: Optional[str] = None,
    ) -> None:
        """Method to read model from a model file
        Args:
            path: path to model file
            import_type: type of import: "model" or "app-module"
            am_path: optional path for app-module project
        """
        imported_model = vafmodel.load_json(path)

        model_runtime = ModelRuntime()

        assert import_type in ("app-module", "model")
        if import_type == "app-module":
            assert am_path is not None

        for key, value in vars(imported_model).items():
            if key == "DataTypeDefinitions":
                for dtd_type_str in vafmodel.data_types:
                    for new_data in getattr(value, dtd_type_str):
                        # create vafpy object from the imported vafmodel object
                        cls.create_vafpy_from_vafmodel(
                            new_data,
                            dtd_type_str.removesuffix("s"),
                        )
            elif key in [
                "ModuleInterfaces",
                "PlatformConsumerModules",
                "PlatformProviderModules",
                "ApplicationModules",
            ]:
                for val in value:
                    # if import_app_module -> add installation paths to app modules
                    if import_type == "app-module" and isinstance(val, vafmodel.ApplicationModule):
                        if val.ImplementationProperties is None:
                            val.ImplementationProperties = vafmodel.ImplementationProperty()
                        val.ImplementationProperties.InstallationPath = am_path
                    # create vafpy object from the imported vafmodel object
                    cls.create_vafpy_from_vafmodel(val, key.removesuffix("s"))
            else:  # other keys
                if import_type == "model":
                    if key.endswith("AdditionalConfiguration") and value is not None:
                        # <x>AdditionalConfiguration should only be set in the integration project.
                        # Therefore it's valid to just overwrite anything that is currently set in the model.
                        setattr(model_runtime.main_model, key, getattr(imported_model, key))
                    elif isinstance(value, List) and len(value) > 0:
                        setattr(
                            model_runtime.main_model,
                            key,
                            getattr(model_runtime.main_model, key) + value,
                        )


def import_model(path: str) -> None:
    """Imports a module from json.
    Merges existing lists, does not overwrite other members.

    Args:
        path (str): Path to the json file
    """
    _ModelReader.read_model(path, import_type="model")


def import_application_module(model_path: str, am_path: str) -> None:  # pylint: disable=too-many-locals, too-many-branches
    """Imports a app module from json.
    Merges existing lists, does not overwrite other members.

    Args:
        model_path (str): Path to the json file
        am_path (str): Relative path to the application module
    """
    _ModelReader.read_model(
        model_path,
        import_type="app-module",
        am_path=am_path,
    )


def get_datatype(name: str, namespace: str, datatype: Optional[str] = None) -> VafpyAbstractBase:
    """Gets a datatype

    Args:
        name (str): The name of the datatype
        namespace (str): The namespace of the datatype
        datatype (str): Type of the searched datatype, e.g.: Structs or Vectors
    Raises:
        ModelError: no corresponding datatype is found
    Returns:
        VafpyAbstractDataType: The vafpy datatype object which has vafmodel obj and its reference
    """
    plural_datatype = datatype + "s" if isinstance(datatype, str) else ""
    # if datatypes defined, then look specifically for this data type:
    if datatype is not None and plural_datatype in vafmodel.data_types:
        result = ModelRuntime().get_model_runtime_element(name, namespace, plural_datatype)
        assert result.__class__.__name__ == datatype
    else:  # not defined, look over all data types
        for dt_type in vafmodel.data_types:
            # don't raise errors if nothing found!
            result = ModelRuntime().get_model_runtime_element(
                name, namespace, dt_type.removesuffix("s"), assert_result=False
            )
            if result is not None:
                break
    if not isinstance(result, VafpyAbstractBase):
        raise ModelError(f"Datatype {namespace}::{name} has invalid type: {type(result)}")
    return result


def get_module_interface(name: str, namespace: str) -> ModuleInterface:
    """Gets a module interface by full name

    Args:
        name (str): The name of the module interface
        namespace (str): The namespace of the module interface

    Returns:
        vafmodel.ModuleInterface: The interface
    """
    result = ModelRuntime().get_model_runtime_element(name, namespace, "ModuleInterfaces")
    assert isinstance(result, ModuleInterface)
    return result


def get_platform_consumer_module(name: str, namespace: str) -> PlatformConsumerModule:
    """Gets a platform consumer module by full name

    Args:
        name (str): The name of the module
        namespace (str): The namespace of the module

    Raises:
        ModelError: If the module was not found

    Returns:
        vafmodel.PlatformModule: The found module
    """
    result = ModelRuntime().get_model_runtime_element(name, namespace, "PlatformConsumerModules")
    assert isinstance(result, PlatformConsumerModule)
    return result


def get_platform_provider_module(name: str, namespace: str) -> PlatformProviderModule:
    """Gets a platform provider module by full name

    Args:
        name (str): The name of the module
        namespace (str): The namespace of the module

    Raises:
        ModelError: If the module was not found

    Returns:
        vafmodel.PlatformModule: The found module
    """
    result = ModelRuntime().get_model_runtime_element(name, namespace, "PlatformProviderModules")
    assert isinstance(result, PlatformProviderModule)
    return result


def get_application_module(name: str, namespace: str) -> ApplicationModule:
    """Gets an application module by full name

    Args:
        name (str): The name of the application module
        namespace (str): The namespace of the application module

    Raises:
        ModelError: If the module is not found

    Returns:
        vafmodel.ApplicationModule: The application module
    """
    result = ModelRuntime().get_model_runtime_element(name, namespace, "ApplicationModules")
    assert isinstance(result, ApplicationModule)
    return result
