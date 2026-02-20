# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Abstraction layer for vafmodel.ModuleInterfaces in Config as Code."""

from copy import deepcopy
from typing import Any, List, Optional

from pydantic import TypeAdapter

from vaf import vafmodel
from vaf.core.common.utils import create_name_namespace_full_name

from .core import BaseTypesWrapper, ModelError, VafpyAbstractBase
from .datatypes import (
    Array,
    String,
    Struct,
    VafpyFactoryWithTypeRef,
    Vector,
)
from .factory import VafpyFactory
from .model_runtime import ModelRuntime
from .task import Task

# pylint: disable = too-few-public-methods
# pylint: disable = unused-private-member # Used via decorators
# pylint: disable = super-init-not-called # DUE to decorators' use
# pylint: disable = unused-argument # DUE to overload in decorator
# pylint: disable = protected-access
# pylint:disable=too-many-ancestors
# mypy: disable-error-code="misc"

ElementType = vafmodel.ApplicationModule | vafmodel.PlatformModule


class VafpyModuleInterfaceFactory(VafpyFactory, VafpyAbstractBase):
    """Factory class for ModuleInterface"""

    @classmethod
    def create(cls, constructor: type[vafmodel.VafBaseModel], obj: VafpyAbstractBase, **kwargs: Any) -> None:
        """Method to build an vafpy module interfaces
        Args:
            constructor: parent of object whose constructor will be used
            obj: object to be built
            kwargs: attributes of the object
        """
        # call parent's build
        super().create(constructor=constructor, obj=obj, **kwargs)
        # append element name to internal interfaces
        assert obj is not None
        ModelRuntime().internal_interfaces.append(obj.Name)


class ModuleInterface(vafmodel.ModuleInterface, VafpyAbstractBase):
    """Represents a VAF module interface"""

    def __init__(
        self,
        name: str,
        namespace: str,
    ) -> None:
        VafpyModuleInterfaceFactory.create(
            constructor=vafmodel.ModuleInterface,
            obj=self,
            Name=name,
            Namespace=namespace,
        )

    def add_data_element(self, name: str, datatype: VafpyAbstractBase | BaseTypesWrapper) -> None:
        """Add a data element to the module interface

        Args:
            name (str): Unique name for the data element
            datatype (VafpyAbstractBase | BaseTypesWrapper): VAF Datatype of the element

        Raises:
            ModelError: If a data element with the same name already exists.
        """
        data_element_names = [da.Name for da in self.DataElements]
        if name in data_element_names:
            raise ModelError(f"Duplicated DataElement {name} for inter  face {self.Namespace}:{self.Name}.")

        self.DataElements.append(
            vafmodel.DataElement(
                Name=name,
                TypeRef=datatype.type_ref,
            )
        )

        # borrow check typeref from vafpyAbstractDatatypeTyperef
        VafpyFactoryWithTypeRef.check_typeref(datatype)

        ModelRuntime().used_module_interfaces[create_name_namespace_full_name(self.Name, self.Namespace)].append(
            create_name_namespace_full_name(datatype.Name, datatype.Namespace)
        )

    def add_operation(
        self,
        name: str,
        in_parameter: dict[str, VafpyAbstractBase | BaseTypesWrapper] | None = None,
        out_parameter: dict[str, VafpyAbstractBase | BaseTypesWrapper] | None = None,
        inout_parameter: dict[str, VafpyAbstractBase | BaseTypesWrapper] | None = None,
    ) -> None:
        """
        Add an operation to the module interface.

        Args:
            name (str): Unique name for the operation.
            in_parameter (dict[str, VafpyAbstractBase | BaseTypesWrapper], optional): Dictionary of input parameters.
            Defaults to None.
            out_parameter (dict[str, VafpyAbstractBase | BaseTypesWrapper], optional): Dictionary of output parameters.
            Defaults to None.
            inout_parameter (dict[str, VafpyAbstractBase | BaseTypesWrapper], optional): Dictionary of input/output
            parameters. Defaults to None.

        Raises:
            ModelError: If an operation with the same name already exists.
        """
        # consolidate parameters
        params: dict[vafmodel.ParameterDirection, dict[str, VafpyAbstractBase | BaseTypesWrapper]] = {
            vafmodel.ParameterDirection.IN: in_parameter if in_parameter is not None else {},
            vafmodel.ParameterDirection.OUT: out_parameter if out_parameter is not None else {},
            vafmodel.ParameterDirection.INOUT: inout_parameter if inout_parameter is not None else {},
        }

        operation_names = [op.Name for op in self.Operations]
        if name in operation_names:
            raise ModelError(f"Duplicated operation {name} for interface {self.Namespace}:{self.Name}.")

        function_parameters: List[vafmodel.Parameter] = []

        for param_direction, param_dict in params.items():
            for param_name, datatype in param_dict.items():
                function_parameters.append(
                    vafmodel.Parameter(
                        Name=param_name,
                        TypeRef=datatype.type_ref,
                        Direction=param_direction,
                    )
                )
                # borrow check typeref from vafpyAbstractDatatypeTyperef
                VafpyFactoryWithTypeRef.check_typeref(datatype)

        self.Operations.append(vafmodel.Operation(Name=name, Parameters=function_parameters))


class ApplicationModule(vafmodel.ApplicationModule, VafpyAbstractBase):
    """Represents a VAF application module"""

    # pylint: disable-next=too-many-positional-arguments,too-many-arguments
    def __init__(
        self,
        name: str,
        namespace: str,
        consumed_interfaces: Optional[List[vafmodel.ApplicationModuleConsumedInterface]] = None,
        provided_interfaces: Optional[List[vafmodel.ApplicationModuleProvidedInterface]] = None,
        tasks: Optional[List[vafmodel.ApplicationModuleTasks]] = None,
        persistency_files: Optional[List[str]] = None,
    ) -> None:
        VafpyFactory.create(
            constructor=vafmodel.ApplicationModule,
            obj=self,
            Name=name,
            Namespace=namespace,
            ConsumedInterfaces=consumed_interfaces if consumed_interfaces is not None else [],
            ProvidedInterfaces=provided_interfaces if provided_interfaces is not None else [],
            ImplementationProperties=vafmodel.ImplementationProperty(GenerateUnitTestStubs=True),
            Tasks=tasks if tasks is not None else [],
            PersistencyFiles=persistency_files if persistency_files is not None else [],
        )

    def __add_interface(
        self,
        instance_name: str,
        interface: ModuleInterface,
        interface_type: str,
        is_optional: bool = False,
    ) -> None:
        """Add a consumed interface to the AppModule

        Args:
            instance_name (str): Unique name for the interface instance
            interface (vafpy.ModuleInterface): The module interface to add
            interface_type (str): consumed/provided
            is_optional (bool): Whether the interface is mandatory for the AppModule to start

        Raises:
            ModelError: If a consumed interface with the same name already exists.
        """
        vafmodel_interfaces = getattr(self, f"{interface_type.capitalize()}Interfaces")
        assert isinstance(vafmodel_interfaces, List)
        mi_names = [mi.InstanceName for mi in vafmodel_interfaces]
        if instance_name in mi_names:
            raise ModelError(
                f"Duplicated {interface_type} interface {instance_name}for AppModule {self.Namespace}::{self.Name}."
            )

        vafmodel_interfaces.append(
            # vafmodel.ApplicationModuleConsumedInterface or vafmodel.ApplicationModuleProvidedInterface
            getattr(vafmodel, f"ApplicationModule{interface_type.capitalize()}Interface")(
                InstanceName=instance_name,
                ModuleInterfaceRef=interface,
                # IsOptional is only available for Consumed
                **({"IsOptional": is_optional} if interface_type == "consumed" else {}),
            )
        )
        ModelRuntime().add_used_module_interfaces(interface)

    def add_consumed_interface(self, instance_name: str, interface: ModuleInterface, is_optional: bool = False) -> None:
        """Add a consumed interface to the AppModule

        Args:
            instance_name (str): Unique name for the interface instance
            interface (vafpy.ModuleInterface): The module interface to add
            is_optional (bool): Whether the interface is mandatory for the AppModule to start

        Raises:
            ModelError: If a consumed interface with the same name already exists.
        """
        self.__add_interface(instance_name, interface, interface_type="consumed", is_optional=is_optional)

    def add_provided_interface(self, instance_name: str, interface: ModuleInterface) -> None:
        """Add a provided interface to the app module

        Args:
            instance_name (str): Unique name for the interface instance
            interface (vafpy.ModuleInterface): The module interface to add

        Raises:
            ModelError: If a provided interface with the same name already exists.
        """
        self.__add_interface(instance_name, interface, interface_type="provided")

    def _get_task_ref(self, task: vafmodel.ApplicationModuleTasks | Task) -> vafmodel.ApplicationModuleTasks:
        if isinstance(task, vafmodel.ApplicationModuleTasks):
            return task
        return task.model

    def add_task(self, task: vafmodel.ApplicationModuleTasks | Task) -> None:
        """Add a task to the app module

        Args:
            task (vafmodel.ApplicationModuleTasks | vafpy.Task): Task to add

        Raises:
            ModelError: If a task with the same name already exists.
        """
        task_names = [task.Name for task in self.Tasks]
        task_ref = self._get_task_ref(task)
        if task_ref.Name in task_names:
            raise ModelError(f"Duplicated task {task_ref.Name} for AppModule {self.Namespace}::{self.Name}.")

        self.Tasks.append(task_ref)

    def add_task_chain(
        self,
        tasks: List[vafmodel.ApplicationModuleTasks | Task],
        run_after: List[vafmodel.ApplicationModuleTasks | Task] | None = None,
        increment_preferred_offset: bool = False,
    ) -> None:
        """
        Add multiple tasks with a strict execution order to the app module

        Args:
            tasks (List[vafmodel.ApplicationModuleTasks | vafpy.Task]): Tasks to add
            run_after (List[vafmodel.ApplicationModuleTasks | vafpy.Task]): Tasks that should run before this one
            increment_preferred_offset (bool): Uses the preferred offset of the first task as base value and increments
            it for every following task.

        Raises:
            ModelError: If a task with the same name already exists.
        """
        task_names = [task.Name for task in self.Tasks]
        last_name = None
        current_offset = self._get_task_ref(tasks[0]).PreferredOffset or 0
        for task in tasks:
            task_ref = self._get_task_ref(task)
            if task_ref.Name in task_names:
                raise ModelError(f"Duplicated task {task_ref.Name} for AppModule {self.Namespace}::{self.Name}.")

            run_after_ = task_ref.RunAfter + [self._get_task_ref(task_).Name for task_ in run_after or []]
            if last_name:
                run_after_.append(last_name)

            local_task = deepcopy(task_ref)
            local_task.RunAfter = run_after_
            if increment_preferred_offset:
                local_task.PreferredOffset = current_offset
            self.Tasks.append(local_task)

            if increment_preferred_offset:
                current_offset += 1
            last_name = task_ref.Name
            task_names.append(task_ref.Name)

    def add_persistency_file(self, file_name: str) -> None:
        """Add a persistency file to the app module

        Args:
            file_name (str): Persistency file to add

        Raises:
            ModelError: If a persistency file with the same name already exists.
        """
        if file_name in self.PersistencyFiles:
            raise ModelError(f"Duplicated persistency file {file_name} for AppModule {self.Namespace}::{self.Name}.")

        self.PersistencyFiles.append(file_name)  # pylint:disable=no-member

    def init_key_value_pair(
        self, file_name: str, key: str, datatype: VafpyAbstractBase | BaseTypesWrapper, value: Any
    ) -> None:
        """Add a persistency key-value init pair

        Args:
            file_name (str): Persistency file intended
            key (str): Key
            datatype (str): Datatype of value
            value (Any): Value

        Raises:
            ModelError: If a key for a persistency file with the same name already exists or type not in
            DataTypeForSerialization
        """
        if self.PersistencyInitValues is None:
            self.PersistencyInitValues = []
        for item in self.PersistencyInitValues:
            if file_name == item.FileName and key == item.Key:
                raise ModelError(
                    f"Duplicated key {key} for persistency file {file_name}for AppModule {self.Namespace}::{self.Name}."
                )

        # Special handling for vaf string type as its considered as base type
        if "String" == datatype.Name and "vaf" == datatype.Namespace:
            self.add_persistency_type(datatype)

        if (
            not vafmodel.DataType(Name=datatype.Name, Namespace=datatype.Namespace).is_base_type
            and not vafmodel.DataType(Name=datatype.Name, Namespace=datatype.Namespace).is_cstdint_type
            and not ("String" == datatype.Name and "vaf" == datatype.Namespace)
        ):
            if self.DataTypesForSerialization is not None:
                dts = vafmodel.DataTypeForSerialization(
                    TypeRef=vafmodel.DataTypeRef(
                        Name=datatype.Name,
                        Namespace=datatype.Namespace,
                    )
                )
                if dts not in self.DataTypesForSerialization:
                    raise ModelError(
                        f"DataType {datatype.Name} for {key} must be added with add_persistency_type before use."
                    )
            else:
                raise ModelError(
                    f"DataType {datatype.Name} for {key} must be added with add_persistency_type before use."
                )

        data = {"Type": datatype.Name, "InitValue": value}
        if isinstance(datatype, Array):
            data = {"Type": "array", "InitValue": value}
        elif isinstance(datatype, Vector):
            data = {"Type": "array", "InitValue": value}
        elif isinstance(datatype, Struct):
            data = {"Type": "struct", "InitValue": value}
        elif isinstance(datatype, String):
            data = {"Type": "String", "InitValue": value}

        typed_data = TypeAdapter(vafmodel.InitValueTypes).validate_python(data)  # type: vafmodel.InitValueTypes

        self.PersistencyInitValues.append(  # pylint:disable=no-member
            vafmodel.PersistencyInitValue(
                FileName=file_name,
                Key=key,
                TypeRef=datatype.type_ref,
                Value=typed_data,
            )
        )

        # borrow check typeref from vafpyAbstractDatatypeTyperef
        VafpyFactoryWithTypeRef.check_typeref(datatype)

    def add_persistency_type(self, datatype: VafpyAbstractBase | BaseTypesWrapper) -> None:
        """Add a peristency type for serialization

        Args:
            datatype (VafpyAbstractBase | BaseTypesWrapper): VAF Datatype

        Raises:
            ModelError: If a data type with the same name already exists.
        """
        dts = vafmodel.DataTypeForSerialization(
            TypeRef=vafmodel.DataTypeRef(
                Name=datatype.Name,
                Namespace=datatype.Namespace,
            )
        )

        if self.DataTypesForSerialization is not None:
            if dts in self.DataTypesForSerialization:
                raise ModelError(f"Duplicated datatype {datatype.Name} for AppModule {self.Namespace}::{self.Name}.")

            self.DataTypesForSerialization.append(dts)
        else:
            self.DataTypesForSerialization = [dts]

        # borrow check typeref from vafpyAbstractDatatypeTyperef
        VafpyFactoryWithTypeRef.check_typeref(datatype)


# pylint: disable = too-many-ancestors
class PlatformConsumerModule(vafmodel.PlatformModule, VafpyAbstractBase):
    """Represents a VAF platform consumer module"""

    def __init__(self, name: str, namespace: str, module_interface: ModuleInterface) -> None:
        VafpyFactory.create(
            constructor=vafmodel.PlatformModule,
            obj=self,
            Name=name,
            Namespace=namespace,
            ModuleInterfaceRef=module_interface,
        )


class PlatformProviderModule(PlatformConsumerModule, VafpyAbstractBase):
    """Represents a VAF platform provider module"""
