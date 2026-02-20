# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Runtime for building a complete model with Config as Code."""

from pathlib import Path
from typing import List, Optional, Tuple

from typing_extensions import Self

from vaf import vafmodel
from vaf.core.common.utils import ProjectType as PType
from vaf.core.common.utils import create_name_namespace_full_name
from vaf.core.state_manager.tracker import tracking_context

from .core import ModelError, VafpyAbstractBase, VafpyAbstractModelRuntime
from .validator import CleanupOverride, _Validator


class ModelRuntime(VafpyAbstractModelRuntime):
    """Runtime to store modeling progress"""

    # validator
    __validator: _Validator

    @staticmethod
    def __get_element_type(vaf_model_obj: VafpyAbstractBase) -> str:
        """Method to get element type of a vafmodel object
        Args:
            vaf_model_obj: vafmodel obj
        Return:
            data type of vafmodel in plural (Enums instead of VafEnums)
        """
        return type(vaf_model_obj).__name__.removeprefix("Vaf") + "s"

    def __get_element_data(self, element: VafpyAbstractBase) -> Tuple[str, str, str]:
        """Method to get data of a vafpy/vafmodel object
        Args:
            element: vafpy/vafmodel object
        Return:
            Tuple that contains: object's name, object's namespace, element's type
        """
        return (
            element.Name,
            element.Namespace,
            self.__get_element_type(element),
        )

    def add_element(self, element: VafpyAbstractBase, imported: bool = False) -> None:
        """Adds an element to the model
        Args:
            element: element to be added to the model
            imported: boolean to define if it's addition for import/load
        Raises:
            ModelError: if element already exists
        """
        if isinstance(element, VafpyAbstractBase):
            # get element data
            name, namespace, element_type = self.__get_element_data(element)

            # add to main model if not yet recorded
            if self.element_by_namespace.get(namespace, {}).get(element_type, {}).get(name, None) is None:
                getattr(
                    self.main_model.DataTypeDefinitions if element_type in vafmodel.data_types else self.main_model,
                    element_type,
                ).append(element)

            # add vafpy objects to element_by_namespace database
            if namespace not in self.element_by_namespace:
                self.element_by_namespace[namespace] = {}
            if element_type not in self.element_by_namespace[namespace]:
                self.element_by_namespace[namespace][element_type] = {name: element}
            else:
                duplicate = name in self.element_by_namespace[namespace][element_type]
                if not duplicate:
                    self.element_by_namespace[namespace][element_type][name] = element
                elif not imported:
                    # raise ModelError for duplicates if not imported
                    # means: user wrongly modelled an object twice
                    # This must be simply silently ignored in import
                    # operations (via import_json())
                    raise ModelError(
                        "".join(
                            [
                                f"Failed to add a duplicate for MainModel Element {element_type}:"
                                f" with Identifier: {namespace}::{name}"
                            ]
                        )
                    )

            # special operations for specific elements
            # ModuleInterface, Executable
            if not imported:
                if isinstance(element, vafmodel.ModuleInterface):
                    self.add_used_module_interfaces(element)
                elif isinstance(element, vafmodel.ApplicationModule):
                    self.add_used_module_interfaces(
                        [mi.ModuleInterfaceRef for mi in element.ConsumedInterfaces + element.ProvidedInterfaces]
                    )

    def remove_element(self, element: VafpyAbstractBase) -> None:
        """Remove an element from the model
        Args:
            element: element to be removed from the model
        """
        if isinstance(element, VafpyAbstractBase):
            name, namespace, element_type = self.__get_element_data(element)

            if name in self.element_by_namespace[namespace][element_type]:
                # remove from main_model via model from internal lookup
                # reason: element is a deepcopy and might not the same object
                # like the one in the model that needs to be deleted
                getattr(
                    self.main_model.DataTypeDefinitions if element_type in vafmodel.data_types else self.main_model,
                    element_type,
                ).remove(self.element_by_namespace[namespace][element_type][name])
                # remove element from internal lookup
                del self.element_by_namespace[namespace][element_type][name]

            if not self.element_by_namespace[namespace][element_type]:
                del self.element_by_namespace[namespace][element_type]

            if not self.element_by_namespace[namespace]:
                del self.element_by_namespace[namespace]

            # special operations for specific elements
            # ModuleInterface, PlatformModule, Executable
            if isinstance(element, vafmodel.ModuleInterface):
                self.remove_used_module_interfaces(element)
            elif isinstance(element, vafmodel.ApplicationModule):
                self.remove_used_module_interfaces(
                    [mi.ModuleInterfaceRef for mi in element.ConsumedInterfaces + element.ProvidedInterfaces]
                )

    def replace_element(self, element: VafpyAbstractBase) -> None:
        """Replace an element with same name & namespace
        Args:
            element: element to be replaced in the model
        """
        if isinstance(element, VafpyAbstractBase):
            # replace element from model by namespace
            name, namespace, element_type = self.__get_element_data(element)
            if name in self.element_by_namespace[namespace][element_type]:
                self.element_by_namespace[namespace][element_type][name] = element
                # replace in main model
                element_list = getattr(
                    self.main_model.DataTypeDefinitions if element_type in vafmodel.data_types else self.main_model,
                    element_type,
                )
                for idx, el in enumerate(element_list):
                    if el.Name == element.Name and el.Namespace == element.Namespace:
                        element_list[idx] = element
                        break

    def get_model_runtime_element(
        self, name: str, namespace: str, element_type: str, assert_result: bool = True
    ) -> Optional[VafpyAbstractBase]:
        """Method to get element's object based on type
        Args:
            name: name of the element
            namespace: namespace of the element
            element_type: type of the element
            assert_result: flag to activate result assertion

        Raises:
            ModelError: if no element found

        Returns:
            Vafpy type belongs to the element
        """
        found = self.element_by_namespace.get(namespace, {}).get(element_type, {}).get(name, None)
        if assert_result:
            if found is None:
                raise ModelError(f"Could not find {element_type}: {namespace}::{name}!")
        return found

    def add_used_module_interfaces(
        self,
        module_interfaces: List[vafmodel.ModuleInterface] | vafmodel.ModuleInterface,
    ) -> None:
        """Adds a module interface to the used module interface
        Args:
            module_interfaces (vafmodel.ModuleInterface): list of module interface
        """
        if not isinstance(module_interfaces, List):
            module_interfaces = [module_interfaces]
        for mi in module_interfaces:
            module_interface_id = create_name_namespace_full_name(mi.Name, mi.Namespace)
            if module_interface_id not in self.used_module_interfaces:
                self.used_module_interfaces[module_interface_id] = list(
                    set(
                        [
                            create_name_namespace_full_name(data_el.TypeRef.Name, data_el.TypeRef.Namespace)
                            for data_el in mi.DataElements
                        ]
                        + [
                            create_name_namespace_full_name(
                                surgery_parameter.TypeRef.Name,
                                surgery_parameter.TypeRef.Namespace,
                            )
                            for surgery in mi.Operations
                            for surgery_parameter in surgery.Parameters
                        ]
                    )
                )

    def remove_used_module_interfaces(
        self,
        module_interfaces: List[vafmodel.ModuleInterface] | vafmodel.ModuleInterface,
    ) -> None:
        """Adds a module interface to the used module interface
        Args:
            module_interfaces (vafmodel.ModuleInterface): list of module interface
        """
        if not isinstance(module_interfaces, List):
            module_interfaces = [module_interfaces]
        for mi in module_interfaces:
            module_interface_id = create_name_namespace_full_name(mi.Name, mi.Namespace)
            if module_interface_id in self.used_module_interfaces:
                del self.used_module_interfaces[module_interface_id]

    def validate(self, project_type: PType, override_cleanup: CleanupOverride = CleanupOverride.DEFAULT) -> Self:
        """Method to validate and cleanup model based on project_type
        Args:
            project_type: Type of the project
            override_cleanup: boolean to override the project_type logic
        """
        self.__validator = _Validator(self, project_type, override_cleanup)
        self.__validator.validate_model()

        # returns self so it can be used in one-liner
        return self

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-positional-arguments
    def save(
        self,
        path: Path,
        project_type: PType,
        keys: Optional[List[str]] = None,
        cleanup: CleanupOverride = CleanupOverride.DEFAULT,
        skip_validation: bool = False,
    ) -> None:
        """
        Saves the main model to file with undo/redo support.

        Args:
            path (Path): Path to the file
            keys: (list[str]): Key to be saved in the export
            project_type (ProjectType): Type of the current project
            cleanup (bool): Boolean flag to remove unused data elements & module interfaces in model
            skip_validation (bool): Boolean flag to indicate the need for model validation
        """
        if not skip_validation:
            self.validate(project_type, override_cleanup=cleanup)
        else:
            print("Skipping the model validation.")

        if keys is not None:
            target_model: vafmodel.MainModel = vafmodel.MainModel()
            for key in keys:
                if hasattr(target_model, key):
                    getattr(target_model, key).extend(getattr(self.main_model, key))

        # Generate new model JSON string
        model_as_string = (self.main_model if keys is None else target_model).model_dump_json(
            indent=2, exclude_none=True, exclude_defaults=True, by_alias=True
        )

        # Use stateless undo manager with context for atomic operations
        with tracking_context(f"Save model to {path.name}") as tracker:
            # Handle main file modification
            # Create/ Modify main file
            tracker.create_modify_file(path, model_as_string)
