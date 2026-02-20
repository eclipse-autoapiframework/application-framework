# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Executable integration calls and helper functions."""  # pylint: disable=too-many-lines

# pylint bug, see https://github.com/pylint-dev/pylint/issues/4899 and https://github.com/pylint-dev/pylint/issues/10087
# marked with # pylint-bug

from datetime import timedelta
from enum import Enum
from typing import Any, List

from vaf import vafmodel
from vaf.core.common.constants import PersistencyLibrary

from ..core.common.utils import create_name_namespace_full_name
from .core import ModelError
from .elements import ApplicationModule
from .model_runtime import ModelRuntime


class AssigmentTypeEnum(Enum):
    """Represents enum for assignment type"""

    UserAssigned = "User assigned"
    AutomaticallyAssigned = "Automatically assigned"


# pylint:disable=protected-access
class _ExecutablePlatformConnector:  # pylint:disable=too-few-public-methods
    """Handle platform connection APIs of vafpy.Executable"""

    __model: ModelRuntime = ModelRuntime()

    #### PUBLIC API ####
    def connect_interface_to_silkit(  # pylint:disable=too-many-arguments,too-many-positional-arguments,
        self,
        executable: vafmodel.Executable,
        app_module: ApplicationModule,
        instance_name: str,
        interface_type: str,
        silkit_instance: str,
        silkit_instance_is_optional: bool = False,
        silkit_namespace: str | None = None,
        silkit_namespace_is_optional: bool | None = None,
    ) -> None:
        """Connects a module interface of an application module as a silkit consumer

        Args:
            executable: The executable
            app_module (vafpy.ApplicationModule): Application module instance to
            connect
            instance_name (str): The interface instance name
            interface_type (str): Type of interface (consumer/provider)
            silkit_instance (str): The SilKit Instance
            silkit_instance_is_optional (bool): Indicates if Silkit Instance is optional or mandatory for discovery
            silkit_namespace (str): The SilKit Namespace
            silkit_namespace_is_optional (bool): Indicates if Silkit Namespace is optional or mandatory for discovery

        Raises:
            ValueError: If the parameter interface_type and/or silkit_namespace_is_optional is wrongly specified
            ModelError: If more than one SilKit provider configured for Module Interface with same SilKit Instance and SilKit Namespace # pylint: disable=line-too-long
        """
        am = self.__ensure_app_module(executable, app_module)

        interface = self.__find_interface(app_module, instance_name, interface_type)

        if silkit_namespace is not None and silkit_namespace == "":
            raise ValueError(('connect interface to silkit command found with specified "silkit_namespace" but empty'))

        if silkit_namespace is None and silkit_namespace_is_optional is not None:
            raise ValueError(
                (
                    'connect interface to silkit command found with specified "silkit_namespace_is_optional" but not specified "silkit_namespace" this is not allowed'  # pylint: disable=line-too-long
                )
            )

        if silkit_namespace is not None and silkit_namespace_is_optional is None:
            silkit_namespace_is_optional = True

        found_module: List[vafmodel.PlatformModule] = self.__find_platform_module(
            interface,
            interface_type,
            vafmodel.OriginalEcoSystemEnum.SILKIT,
            silkit_instance=silkit_instance,
            silkit_namespace=silkit_namespace,
        )

        if interface_type == "consumer" and len(found_module) > 1:
            pm = found_module[0]
        elif interface_type == "provider" and len(found_module) > 0:
            raise ModelError(
                f"More than one SilKit provider configured for Module Interface {interface.ModuleInterfaceRef.Name} with SilKit Instance {silkit_instance} and SikKit Namespace {silkit_namespace}"  # pylint: disable=line-too-long
            )
        else:
            scp = vafmodel.SILKITConnectionPoint(
                Name=f"ConnectionPoint_{interface_type}_{instance_name}",
                SilkitInstance=silkit_instance,
                SilkitInstanceIsOptional=silkit_instance_is_optional,
                SilkitNamespace=silkit_namespace,
                SilkitNamespaceIsOptional=silkit_namespace_is_optional,
            )
            if self.__model.main_model.SILKITAdditionalConfiguration is None:
                self.__model.main_model.SILKITAdditionalConfiguration = vafmodel.SILKITAdditionalConfigurationType(
                    ConnectionPoints=[]
                )
            # pylint-bug
            # pylint: disable-next=no-member
            self.__model.main_model.SILKITAdditionalConfiguration.ConnectionPoints.append(scp)
            pm = vafmodel.PlatformModule(
                Name=f"{interface_type.capitalize()}Module_{interface.ModuleInterfaceRef.Name}_{instance_name}",  # pylint:disable=line-too-long
                Namespace=interface.ModuleInterfaceRef.Namespace,
                ModuleInterfaceRef=interface.ModuleInterfaceRef,
                OriginalEcoSystem=vafmodel.OriginalEcoSystemEnum.SILKIT,
                ConnectionPointRef=scp,
            )
            (
                self.__model.main_model.PlatformProviderModules
                if interface_type == "provider"
                else self.__model.main_model.PlatformConsumerModules
            ).append(pm)

        # add the mapping
        self.__post_platform_connect_operations(am, interface, instance_name, pm)

    #### PRIVATE API ####
    @staticmethod
    def __ensure_app_module(
        executable: vafmodel.Executable, app_module: ApplicationModule
    ) -> vafmodel.ExecutableApplicationModuleMapping:
        """Method to ensure passed app modules for connection
        Args:
            executable: The executable
            app_module (vafpy.ApplicationModule): Application module to be connected
        Raises:
            ModelError: If the application module was not found,
                        if the instance was not found
        """
        found_am = [
            a
            for a in executable.ApplicationModules
            if a.ApplicationModuleRef.Name == app_module.Name
            and a.ApplicationModuleRef.Namespace == app_module.Namespace
        ]

        if len(found_am) != 1:
            raise ModelError("Could not find application module " + app_module.Name + " mapped on executable")

        return found_am[0]

    @staticmethod
    def __find_interface(
        app_module: ApplicationModule, instance_name: str, interface_type: str
    ) -> vafmodel.ApplicationModuleProvidedInterface | vafmodel.ApplicationModuleConsumedInterface:
        """Method to find interface based on instance name
        Args:
            app_module (vafpy.ApplicationModule): Application module instance to
            connect
            instance_name (str): The interface instance name
            interface_type (str): Type of interface (consumer/provider)
        Raises:
            ModelError: if the interfaces do not match
        """
        assert interface_type in ["provider", "consumer"]
        found_interface = [
            pi
            for pi in (app_module.ProvidedInterfaces if interface_type == "provider" else app_module.ConsumedInterfaces)
            if pi.InstanceName == instance_name
        ]
        if len(found_interface) != 1:
            raise ModelError(f"No {interface_type} interface with instance {instance_name} in Module {app_module.Name}")

        return found_interface[0]

    def __find_platform_module(
        self,
        interface: vafmodel.ApplicationModuleProvidedInterface | vafmodel.ApplicationModuleConsumedInterface,
        interface_type: str,
        ecosystem: vafmodel.OriginalEcoSystemEnum,
        **kwargs: Any,
    ) -> List[vafmodel.PlatformModule]:
        """Method to find interface based on instance name
        Args:
            interface: interface mapping in app module
            interface_type (str): Type of interface (consumer/provider)
            ecosystem: ecosystem for the logic
        Raises:
            ModelError: if the interfaces do not match
        """
        valid: bool = False
        identifier: str = ""
        connection_point_type: type[vafmodel.SILKITConnectionPoint]
        match ecosystem:
            case vafmodel.OriginalEcoSystemEnum.SILKIT:
                assert all(arg in kwargs for arg in ["silkit_instance", "silkit_namespace"])
                identifier = kwargs["silkit_instance"]
                connection_str = "SilKit Instance"
                connection_point_type = vafmodel.SILKITConnectionPoint

        found_module = []
        for pm in (
            self.__model.main_model.PlatformProviderModules
            if interface_type == "provider"
            else self.__model.main_model.PlatformConsumerModules
        ):
            if pm.ModuleInterfaceRef == interface.ModuleInterfaceRef:
                valid = isinstance(pm.ConnectionPointRef, connection_point_type)
                if isinstance(pm.ConnectionPointRef, vafmodel.SILKITConnectionPoint):
                    valid &= (pm.ConnectionPointRef.SilkitInstance == identifier) and (
                        pm.ConnectionPointRef.SilkitNamespace == kwargs["silkit_namespace"]
                    )
                else:
                    valid = False

                if valid:
                    found_module.append(pm)

        missconfiguration = len(found_module) > 1

        if missconfiguration:
            raise ModelError(
                (
                    f"Found missconfiguration of {ecosystem.value} {interface_type.capitalize()} modules for module interface"  # pylint:disable=line-too-long
                    f" {interface.ModuleInterfaceRef.Namespace}"
                    f"::{interface.ModuleInterfaceRef.Name} with  {ecosystem.value} {connection_str}"
                    f" {identifier}"
                )
            )

        return found_module

    def __update_connected_interfaces_catalogue(
        self,
        app_module: vafmodel.ApplicationModule,
        interface_instance: vafmodel.ApplicationModuleConsumedInterface | vafmodel.ApplicationModuleProvidedInterface,
    ) -> None:
        """Method to update connected interfaces catalogue
        Args:
            app_module: app module design that is connected now
            interface_instance: interface instance that is connected
        """
        self.__model.connected_interfaces[
            create_name_namespace_full_name(app_module.Name, app_module.Namespace)
        ].append(interface_instance.InstanceName)
        self.__model.connected_interfaces["platform_modules"].append(
            create_name_namespace_full_name(
                interface_instance.ModuleInterfaceRef.Name,
                interface_instance.ModuleInterfaceRef.Namespace,
            )
        )
        self.__model.add_used_module_interfaces(module_interfaces=interface_instance.ModuleInterfaceRef)

    def __post_platform_connect_operations(
        self,
        am: vafmodel.ExecutableApplicationModuleMapping,
        interface: vafmodel.ApplicationModuleProvidedInterface | vafmodel.ApplicationModuleConsumedInterface,
        instance_name: str,
        pm: vafmodel.PlatformModule,
    ) -> None:
        """After connect platform to SIL Kit operations

        Args:
            am: app module mapping in executable
            interface: interface mapping in app module
            instance_name: str
            pm: platform module to be mapped
        """
        # add the mapping
        mapping = vafmodel.InterfaceInstanceToModuleMapping(InstanceName=instance_name, ModuleRef=pm)
        am.InterfaceInstanceToModuleMappings.append(mapping)
        self.__update_connected_interfaces_catalogue(am.ApplicationModuleRef, interface)


# pylint:enable=protected-access


class Executable(vafmodel.Executable):
    """Represents a VAF executable"""

    _connector: _ExecutablePlatformConnector

    def __init__(self, name: str, executor_period: timedelta | None = None) -> None:
        """Initialize an Executable with an optional executor_period

        Args:
            name (str): Executable name
            executor_period (datetime.timedelta, optional): Executor period. Defaults to an ideal value calculated using
            the tasks of all AppModules.
        """
        period_str = f"{int(executor_period.total_seconds() * 1000)}ms" if executor_period else "Default"

        super().__init__(Name=name, ExecutorPeriod=period_str, ApplicationModules=[])

        ModelRuntime().main_model.Executables.append(self)

        self._connector = _ExecutablePlatformConnector()

    def set_executor_period(self, executor_period: timedelta) -> None:
        """Method to set ExecutorPeriod
        Args:
            executor_period (datetime.timedelta): Executor period as timedelta
        """
        self.ExecutorPeriod = f"{int(executor_period.total_seconds() * 1000)}ms"

    def add_application_module(
        self,
        module: ApplicationModule,
        task_mapping_info: list[tuple[str, timedelta, int]],
    ) -> None:
        """Add an application module to the executable

        Args:
            module (vafpy.ApplicationModule): Application module instance to add
            task_mapping_info (list[tuple[str, timedelta, int]]): Mapping info for tasks a list of tuples with
            (task_name, budget, offset)
        """
        task_mappings: list[vafmodel.ExecutableTaskMapping] = []
        for r in task_mapping_info:
            budget_str = f"{int(r[1].total_seconds() * 1000)}ms"
            task_mappings.append(vafmodel.ExecutableTaskMapping(TaskName=r[0], Offset=r[2], Budget=budget_str))
        self.ApplicationModules.append(
            vafmodel.ExecutableApplicationModuleMapping(
                ApplicationModuleRef=module,
                InterfaceInstanceToModuleMappings=[],
                TaskMapping=task_mappings,
            )
        )

    # pylint: disable-next=too-many-locals, too-many-branches
    def connect_interfaces(
        self,
        module_a: ApplicationModule,
        instance_name_a: str,
        module_b: ApplicationModule,
        instance_name_b: str,
    ) -> None:
        """Connects two interfaces of two application modules in this executable

        Args:
            module_a (vafpy.ApplicationModule): The provider application module
            instance_name_a (str): The instance name of the provided interface
            module_b (vafpy.ApplicationModule): The consumer application module
            instance_name_b (str): The instance name of the consumed interface

        Raises:
            ModelError: If any of the modules are not mapped to the executable,
                        if any of the instances names is not found
                        or if the interfaces are not compatible
        """
        found_pi = [pi for pi in module_a.ProvidedInterfaces if pi.InstanceName == instance_name_a]
        found_ci = [ci for ci in module_b.ConsumedInterfaces if ci.InstanceName == instance_name_b]

        if len(found_pi) != 1:
            raise ModelError(
                "Could not find interface instance "
                + instance_name_a
                + " on a provided interface of module "
                + module_a.Name
            )

        if len(found_ci) != 1:
            raise ModelError(
                "Could not find interface instance "
                + instance_name_b
                + " on a consumed interface of module "
                + module_b.Name
            )

        if found_pi[0].ModuleInterfaceRef != found_ci[0].ModuleInterfaceRef:
            raise ModelError(
                "Interfaces do not match: "
                + found_pi[0].ModuleInterfaceRef.Namespace
                + "::"
                + found_pi[0].ModuleInterfaceRef.Name
                + " and "
                + found_ci[0].ModuleInterfaceRef.Namespace
                + "::"
                + found_ci[0].ModuleInterfaceRef.Name
            )

        found_am_a = [
            a
            for a in self.ApplicationModules
            if a.ApplicationModuleRef.Name == module_a.Name and a.ApplicationModuleRef.Namespace == module_a.Namespace
        ]
        found_am_b = [
            a
            for a in self.ApplicationModules
            if a.ApplicationModuleRef.Name == module_b.Name and a.ApplicationModuleRef.Namespace == module_b.Namespace
        ]

        if len(found_am_a) != 1:
            raise ModelError("Could not find application module " + module_a.Name + " mapped on executable")

        if len(found_am_b) != 1:
            raise ModelError("Could not find application module " + module_b.Name + " mapped on executable")

        already_mapped_on_provider = False
        for instance in found_am_a[0].InterfaceInstanceToModuleMappings:
            if instance.InstanceName == instance_name_a:
                already_mapped_on_provider = True
                sm = instance.ModuleRef

        if not already_mapped_on_provider:
            sm = vafmodel.PlatformModule(
                Name=found_pi[0].ModuleInterfaceRef.Name
                + module_a.Name
                + instance_name_a
                + "To"
                + module_b.Name
                + instance_name_b
                + "Module",
                Namespace="application_communication",
                ModuleInterfaceRef=found_pi[0].ModuleInterfaceRef,
            )
            self.InternalCommunicationModules.append(sm)

        mapping_a = vafmodel.InterfaceInstanceToModuleMapping(InstanceName=instance_name_a, ModuleRef=sm)
        mapping_b = vafmodel.InterfaceInstanceToModuleMapping(InstanceName=instance_name_b, ModuleRef=sm)

        if not already_mapped_on_provider:
            found_am_a[0].InterfaceInstanceToModuleMappings.append(mapping_a)
        found_am_b[0].InterfaceInstanceToModuleMappings.append(mapping_b)

        model = ModelRuntime()
        model.connected_interfaces[f"{module_a.Namespace}::{module_a.Name}"].append(found_pi[0].InstanceName)
        model.connected_interfaces[f"{module_b.Namespace}::{module_b.Name}"].append(found_ci[0].InstanceName)
        # add both interfaces to used_module_interfaces
        model.add_used_module_interfaces([found_pi[0].ModuleInterfaceRef, found_ci[0].ModuleInterfaceRef])

    def connect_consumed_interface_to_silkit(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        app_module: ApplicationModule,
        instance_name: str,
        silkit_instance: str,
        silkit_instance_is_optional: bool = False,
        silkit_namespace: str | None = None,
        silkit_namespace_is_optional: bool | None = None,
    ) -> None:
        """Connects a module interface of an application module as a silkit consumer

        Args:
            app_module (vafpy.ApplicationModule): Application module instance to
            connect
            instance_name (str): The interface instance name
            silkit_instance (str): The SilKit Instance
            silkit_instance_is_optional (bool): Indicates if Silkit Instance is optional or mandatory for discovery
            silkit_namespace (str): The SilKit Namespace
            silkit_namespace_is_optional (bool): Indicates if Silkit Namespace is optional or mandatory for discovery
        """
        self._connector.connect_interface_to_silkit(
            self,
            app_module,
            instance_name,
            interface_type="consumer",
            silkit_instance=silkit_instance,
            silkit_instance_is_optional=silkit_instance_is_optional,
            silkit_namespace=silkit_namespace,
            silkit_namespace_is_optional=silkit_namespace_is_optional,
        )

    def connect_provided_interface_to_silkit(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        app_module: ApplicationModule,
        instance_name: str,
        silkit_instance: str,
        silkit_instance_is_optional: bool = False,
        silkit_namespace: str | None = None,
        silkit_namespace_is_optional: bool | None = None,
    ) -> None:
        """Connects a module interface of an application module as a silkit provider

        Args:
            app_module (vafpy.ApplicationModule): Application module instance to
            connect
            instance_name (str): The interface instance name
            silkit_instance (str): The SilKit Instance
            silkit_instance_is_optional (bool): Indicates if Silkit Instance is optional or mandatory for discovery
            silkit_namespace (str): The SilKit Namespace
            silkit_namespace_is_optional (bool): Indicates if Silkit Namespace is optional or mandatory for discovery

        """
        self._connector.connect_interface_to_silkit(
            self,
            app_module,
            instance_name,
            interface_type="provider",
            silkit_instance=silkit_instance,
            silkit_instance_is_optional=silkit_instance_is_optional,
            silkit_namespace=silkit_namespace,
            silkit_namespace_is_optional=silkit_namespace_is_optional,
        )

    def connect_persistency_keyvalue_store(
        self,
        library: PersistencyLibrary,
    ) -> None:
        """Connects a persistency key value store

        Args:
            library (PersistencyLibrary): The key value store name
        """
        if self.PersistencyModule is None:
            self.PersistencyModule = vafmodel.ExecutablePersistencyMapping(PersistencyLibrary=library)
        else:
            self.PersistencyModule.PersistencyLibrary = library

    def connect_persistency_instance(
        self,
        app_module: ApplicationModule,
        file_name: str,
        file_path: str,
        sync: bool,
    ) -> None:
        """Connects a module interface of an application module as a silkit provider

        Args:
            app_module (vafpy.ApplicationModule): The application module class
            annotated with vaf_application_module
            file_name (str): The file name used in the application module
            file_path (str): The path to the file realtive to ./
            sync (bool): Sync to storage on write.

        Raises:
            ModelError: If the application module was not found,
                        if the instance was not found,
                        or if there is a missconfiguration of silkit provider modules
        """

        found_am = [
            a
            for a in self.ApplicationModules
            if a.ApplicationModuleRef.Name == app_module.Name
            and a.ApplicationModuleRef.Namespace == app_module.Namespace
        ]

        if len(found_am) != 1:
            raise ModelError("Could not find application module " + app_module.Name + " mapped on executable")
        found_persistency_file = [pf for pf in app_module.PersistencyFiles if pf == file_name]
        if len(found_persistency_file) != 1:
            raise ModelError("Could not find persistency file instance " + file_name + " on module " + app_module.Name)
        file_mapping = vafmodel.PersistencyFileMapping(
            AppModuleName=app_module.Name,
            FileName=file_name,
            FilePath=file_path,
            Sync="true" if sync else "false",
        )
        if self.PersistencyModule is None:
            self.PersistencyModule = vafmodel.ExecutablePersistencyMapping()

        for per_map in self.PersistencyModule.PersistencyFiles:
            if file_mapping.FilePath == per_map.FilePath and file_mapping.Sync != per_map.Sync:
                raise ModelError("Shared file path must have same sync option: " + file_mapping.FilePath)

        self.PersistencyModule.PersistencyFiles.append(file_mapping)
