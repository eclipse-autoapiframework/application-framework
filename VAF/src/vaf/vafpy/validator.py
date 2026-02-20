# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Validator to raise Errors in case of Configuration Error before generating JSON."""

import math
import warnings
from copy import deepcopy
from enum import Enum
from typing import Callable, Dict, List, Tuple

import networkx as nx

from vaf import vafmodel

from ..core.common.utils import ProjectType as PType
from ..core.common.utils import create_name_namespace_full_name
from ..vafmodel import Executable
from .core import ModelError, VafpyAbstractBase, VafpyAbstractModelRuntime


class _Action(Enum):
    VALIDATE = 1
    CLEANUP = 2


class CleanupOverride(Enum):
    """Class to define override of ModelRuntime's ModelCleaner
    DEFAULT: Let ModelCleaner decide whether to do cleanup
    DISABLE: Override to disable cleanup
    ENABLE: Override to enable cleanup
    """

    DEFAULT = None
    DISABLE = False
    ENABLE = True


class _ModelCleaner:
    """Class for cleaning up the model"""

    # List of data types for cleanups
    ## Special: Structs & Maps
    ## Generic: Arrays, Enums (VafEnums -> Enums), Strings, TypeRefs, Vectors
    special_dtd_cleanup_data_types: List[str] = ["Structs", "Maps"]
    generic_dtd_cleanup_data_types: List[str]

    __model: VafpyAbstractModelRuntime
    __connected_platform_modules: List[str]

    def __init__(self, runtime_model: VafpyAbstractModelRuntime) -> None:
        self.generic_dtd_cleanup_data_types = [
            data_type for data_type in vafmodel.data_types if data_type not in self.special_dtd_cleanup_data_types
        ]
        self.__model = runtime_model
        self.__connected_platform_modules = runtime_model.connected_interfaces.get("platform_modules", [])

    ### DATATYPES CLEANUP ###
    def cleanup_datatypes(self) -> None:
        """Method to cleanup unused datatypes"""
        # get all nested references of namespaces
        namespace_references, all_base_types = self.__get_all_nested_namespaces_references(self.__model)
        # get all needed custom namespaces
        used_namespaces: List[str] = self.__get_used_namespaces(self.__model, namespace_references, all_base_types)

        # deepcopy since the real dictionary might change dynamically during the loop
        for ns_elements_data in deepcopy(self.__model.element_by_namespace).values():
            # Structs: Special Case due to possible reference by their SubElements
            # structs need to be looped also in the Subelements
            for struct in ns_elements_data.get("Structs", {}).values():
                assert isinstance(struct, vafmodel.Struct)
                struct_identifier = create_name_namespace_full_name(struct.Name, struct.Namespace)
                # check if whole struct is needed
                if struct_identifier not in used_namespaces:
                    used_subelements = [
                        subelement
                        for subelement in struct.SubElements
                        if create_name_namespace_full_name(subelement.Name, subelement.TypeRef.Namespace)
                        in used_namespaces
                    ]
                    # remove struct if it's not needed
                    if used_subelements:
                        struct.SubElements = used_subelements
                        self.__model.replace_element(struct)
                    else:
                        self.__model.remove_element(struct)

            # get used arrays, enums, vectors, strings, typerefs, maps
            ## Maps is not special here: since they can't be referenced by their children attribute
            for dtd_type_str in [*self.generic_dtd_cleanup_data_types, "Maps"]:
                for data in ns_elements_data.get(dtd_type_str, {}).values():
                    assert isinstance(
                        data,
                        (
                            vafmodel.Array,
                            vafmodel.VafEnum,
                            vafmodel.Map,
                            vafmodel.String,
                            vafmodel.TypeRef,
                            vafmodel.Vector,
                        ),
                    )
                    if create_name_namespace_full_name(data.Name, data.Namespace) not in used_namespaces:
                        self.__model.remove_element(data)

            # loop module interfaces
            for module_interface in ns_elements_data.get("ModuleInterfaces", {}).values():
                assert isinstance(module_interface, vafmodel.ModuleInterface)
                module_interface_identifier = create_name_namespace_full_name(
                    module_interface.Name, module_interface.Namespace
                )
                # ignore if already listed as used module interfaces
                # only check if not listed as used module interfaces and identifier not in used_namespaces
                if (
                    module_interface_identifier not in self.__model.used_module_interfaces
                    and module_interface_identifier not in used_namespaces
                ):
                    # check if module interface is not used (possibility as needed parents or grandparents)
                    # get used module interface data elements
                    # first data element also needed as it's for itself
                    used_data_elements = module_interface.DataElements[0:1] + [
                        data_element
                        for data_element in module_interface.DataElements
                        if (data_element.Name == data_element.TypeRef.Name)
                        and (
                            create_name_namespace_full_name(
                                data_element.TypeRef.Name,
                                data_element.TypeRef.Namespace,
                            )
                            in used_namespaces
                        )
                    ]

                    # if found used data element == itself/empty then it's unused
                    if len(used_data_elements) <= 1:
                        # remove module interface
                        self.__model.remove_element(module_interface)
                    # if data elements differ then replace
                    elif len(used_data_elements) != len(module_interface.DataElements):
                        module_interface.DataElements = used_data_elements
                        self.__model.replace_element(module_interface)

    def __get_all_nested_namespaces_references(self, model: VafpyAbstractModelRuntime) -> Tuple[nx.DiGraph, List[str]]:
        """Get all namespaces references
        E.g.: a::b::c refers to a::b::d -> if one needs a::b::c, a::b::d is also needed

        Args:
            model: ModelRuntime whose artifacts are to be reduced

        Returns:
            Directional Graph of nested references of namespaces
            List of all strings of base types data
        """
        graph = nx.DiGraph()
        base_types: List[str] = []

        for ns_elements_data in model.element_by_namespace.values():
            # Special Data Types: Structs & Maps

            ## Structs due to the real type refs referenced in the subelements level
            ## add structs & their subelements reference to graph
            graph, new_base_types = self.__add_struct_to_graph(
                graph, list(ns_elements_data.get("Structs", {}).values())
            )
            base_types += new_base_types

            ## Maps due to typerefs referenced in key & value
            ## add key & value reference to graph
            graph, new_base_types = self.__add_maps_to_graph(graph, list(ns_elements_data.get("Maps", {}).values()))
            base_types += new_base_types

            # Generic Data Types: All Data Types that have vafmodel.TypeRef as direct attribute
            ## arrays, vectors, strings, typeref, enums
            for data_type in self.generic_dtd_cleanup_data_types:
                graph, new_base_types = self.__add_generic_data_types_to_graph(
                    graph, list(ns_elements_data.get(data_type, {}).values())
                )
                base_types += new_base_types

        return graph, list(set(base_types))

    @staticmethod
    def __get_used_namespaces(
        model: VafpyAbstractModelRuntime,
        nested_references_graph: nx.DiGraph,
        base_types_list: List[str],
    ) -> List[str]:
        """Get lists of all used namespaces by using tree
        Args:
            model: ModelRuntime object
            nested_references_graph: graph object that represents all references between namespaces
            base_types_list: list that contains all base types
        Returns:
            Lists of all used namespaces
        """
        # used namespace: persistency ref & module interface refs
        used_namespaces: List[str] = [
            create_name_namespace_full_name(ser.TypeRef.Name, ser.TypeRef.Namespace)
            for am in model.main_model.ApplicationModules
            if am.DataTypesForSerialization is not None
            for ser in am.DataTypesForSerialization
        ] + [mi_type_ref for mi_type_refs in model.used_module_interfaces.values() for mi_type_ref in mi_type_refs]

        # loop over all used refs to check over nested reference
        for used_ref_id in deepcopy(used_namespaces):
            ### DEBUGGING nx.DiGraphs ###
            # getting list of all paths
            # list(nx.all_simple_paths(graph, node1, node2))

            # getting all direct "neighbour" nodes pointed out by a node
            # list(graph.out_edges(node))
            #############################

            # check graph only if data_element_identifier is a node in the graph
            if nested_references_graph.has_node(used_ref_id):
                # get all nested references by checking all paths between data element and all base types
                used_namespaces += [
                    referenced_nodes
                    for base_type in base_types_list  # loop over all base types
                    for path in list(
                        nx.all_simple_paths(nested_references_graph, used_ref_id, base_type)
                    )  # get all paths
                    for referenced_nodes in path[1:]  # ignore first element (data_element), since already added
                ]

        return list(set(used_namespaces))

    @staticmethod
    def __add_struct_to_graph(graph: nx.DiGraph, structs: List[VafpyAbstractBase]) -> Tuple[nx.DiGraph, List[str]]:
        """Function to add a list of struct to graph and collect base types from their subelements
        Args:
            graph: Directional Graph
            structs: List of structs
            dtd_namespace: namespace of current DataTypeDef
        Returns:
            updated Directional Graph
            list of new base types
        """
        new_base_types: List[str] = []
        for struct in structs:
            assert isinstance(struct, vafmodel.Struct)
            # add struct to graph
            struct_identifier = create_name_namespace_full_name(struct.Name, struct.Namespace)
            graph.add_node(struct_identifier)

            # add subelements to struct
            for subelement in struct.SubElements:
                subelement_identifier = create_name_namespace_full_name(subelement.Name, struct_identifier)
                graph.add_edge(struct_identifier, subelement_identifier)
                typeref_identifier = create_name_namespace_full_name(
                    subelement.TypeRef.Name, subelement.TypeRef.Namespace
                )

                # typeref non base types: connect typeref to subelements
                graph.add_edge(subelement_identifier, typeref_identifier)
                if not subelement.TypeRef.Namespace:
                    # add base types
                    new_base_types.append(typeref_identifier)
        return graph, new_base_types

    @staticmethod
    def __add_generic_data_types_to_graph(
        graph: nx.DiGraph,
        generic_data: List[VafpyAbstractBase],
    ) -> Tuple[nx.DiGraph, List[str]]:
        """Function to add a list of generic data types to graph
            Generic Data Types: All Data Types that has vafmodel.TypeRef as direct attribute
            -> Arrays, Enums, Strings, TypeRefs, Vectors
        Args:
            graph: Directional Graph
            generic_data: List of Generic Data
            dtd_namespace: namespace of current DataTypeDef
        Returns:
            updated Directional Graph
            list of new base types
        """
        new_base_types: List[str] = []

        for data in generic_data:
            assert isinstance(
                data,
                (
                    vafmodel.Array,
                    vafmodel.VafEnum,
                    vafmodel.String,
                    vafmodel.TypeRef,
                    vafmodel.Vector,
                ),
            )
            # add data to graph
            data_identifier = create_name_namespace_full_name(data.Name, data.Namespace)
            graph.add_node(data_identifier)

            # if data has typeref then create the typeref node and connect it to the data
            if isinstance(data, (vafmodel.Array, vafmodel.TypeRef, vafmodel.Vector)):
                # typeref non base types: connect typeref to data
                graph.add_edge(
                    data_identifier,
                    create_name_namespace_full_name(data.TypeRef.Name, data.TypeRef.Namespace),  # pylint:disable=line-too-long
                )
                # Vectors, Arrays, TypeRefs: if vafmodel.TypeRef.Namespace is empty -> base types
                if data.TypeRef.Namespace == "":
                    new_base_types.append(data_identifier)
            else:
                # Not Vectors, Arrays, TypeRefs: base types
                new_base_types.append(data_identifier)

        return graph, new_base_types

    @staticmethod
    def __add_maps_to_graph(graph: nx.DiGraph, maps: List[VafpyAbstractBase]) -> Tuple[nx.DiGraph, List[str]]:
        """Function to add a list of maps to graph
        Args:
            graph: Directional Graph
            maps: List of Maps
            dtd_namespace: namespace of current DataTypeDef
        Returns:
            updated Directional Graph
            list of new base types
        """
        new_base_types: List[str] = []
        for map_data in maps:
            assert isinstance(map_data, vafmodel.Map)
            map_identifier = create_name_namespace_full_name(map_data.Name, map_data.Namespace)
            for type_ref in [
                getattr(map_data, f"Map{which_type_ref.capitalize()}TypeRef") for which_type_ref in ["key", "value"]
            ]:
                # connect both typerefs to data
                graph.add_edge(
                    map_identifier,
                    create_name_namespace_full_name(type_ref.Name, type_ref.Namespace),
                )
                # add to base types if typeref namespace is empty
                if type_ref.Namespace == "":
                    new_base_types.append(map_identifier)
        return graph, new_base_types

    ### PLATFORM MODULES CLEANUP ###
    def cleanup_unconnected_platform_modules(self) -> None:
        """Method to cleanup unconnected platform modules"""
        # get unconnected platform modules
        unconnected_pm = self.__get_unconnected_platform_module(self.__model.main_model.PlatformConsumerModules)
        unconnected_pm += self.__get_unconnected_platform_module(self.__model.main_model.PlatformProviderModules)

        # Pass. SIL Kit does not need to be cleaned, because the configuration is not
        # imported but created when one adds the connections.

    def __get_unconnected_platform_module(
        self, platform_modules: List[vafmodel.PlatformModule]
    ) -> List[vafmodel.PlatformModule]:
        """Method to get list of unconnected platform modules
        Args:
            platform_modules: List of platform modules to be analyzed & cleaned up
            model: ModelRuntime that stores connected interfaces
        Returns:
            List of unconnected platform modules
        """
        unconnected: List[vafmodel.PlatformModule] = []
        for pm in deepcopy(platform_modules):
            if (
                create_name_namespace_full_name(pm.ModuleInterfaceRef.Name, pm.ModuleInterfaceRef.Namespace)
                not in self.__connected_platform_modules
            ):
                unconnected.append(pm)
                platform_modules.remove(pm)

        return unconnected


class _Validator:
    # pylint: disable=too-few-public-methods, too-many-instance-attributes
    """Handling Config Validation"""

    # model reference
    __model: VafpyAbstractModelRuntime
    # project type
    __project_type: PType
    # execution manager of the main actions
    __main_executor: List[Tuple[_Action, List[PType], Callable[[], None]]]
    # execution manager of the post actions (if no errors raised)
    __post_run_executor: List[Callable[[], None]]

    # errors & warnings collector
    __hard_errors: List[str]
    __light_warnings: List[str]

    # cleanups
    __cleanup: bool
    __cleaner: _ModelCleaner

    # valid executables collector
    __valid_executable: Dict[str, vafmodel.Executable]
    # collector for conencted/unconnected app modules (added to Executables)
    __connected_app_modules: Dict[str, vafmodel.ApplicationModule]

    # string headers for warnings/errors
    __output_headers: str

    def __init__(
        self,
        runtime_model: VafpyAbstractModelRuntime,
        project_type: PType,
        override_cleanup: CleanupOverride = CleanupOverride.DEFAULT,
    ) -> None:
        """Method to perform model cleanup
        Args:
            runtime_model: model to be validated
            project_type: type of the project
            override_cleanup: boolean to override the project_type logic
        """
        self.__model = runtime_model
        self.__project_type = project_type

        self.__valid_executable = {}
        self.__connected_app_modules = {}

        # initialize cleaner otherwise executor manager init will fail
        self.__cleaner = _ModelCleaner(self.__model)
        # activate cleanup based on project type or user override
        self.__cleanup = (
            project_type in [PType.APP_MODULE, PType.INTEGRATION]
            if override_cleanup is CleanupOverride.DEFAULT
            else override_cleanup.value
        )

        # Main Execution Jobs
        self.__main_executor = [
            # first cleanup datatypes, if cleanup is activated
            (_Action.CLEANUP, [], self.__cleaner.cleanup_datatypes),
            # then validate executables
            (
                _Action.VALIDATE,
                [PType.INTEGRATION, PType.APP_MODULE],
                self.__validate_executables,
            ),
            # validate app modules afterwards
            (
                _Action.VALIDATE,
                [PType.INTEGRATION, PType.APP_MODULE],
                self.__validate_application_module,
            ),
            # validate interfaces
            (
                _Action.VALIDATE,
                [PType.INTEGRATION],
                self.__validate_interface_connections,
            ),
            (
                _Action.VALIDATE,
                [PType.INTEGRATION, PType.APP_MODULE, PType.INTERFACE],
                self.__validate_interface_definition,
            ),
        ]
        # Cleanups that are only necessary if no errors are raised -> performance!
        self.__post_run_executor = [
            # cleanup unconnected platforms
            self.__cleaner.cleanup_unconnected_platform_modules,
        ]

        self.__output_headers = f"Validation for Project Type {project_type}"
        self.__light_warnings = []
        self.__hard_errors = []

    def validate_model(self) -> None:
        """Method to validate CaC model
        Raises:
            ModelError: hard modelling list_errors
        """
        # set warnings format
        warnings.formatwarning = self.__format_warning

        for action_type, project_types, validate_method in self.__main_executor:
            validate_check: bool = (action_type == _Action.VALIDATE) and (self.__project_type in project_types)
            cleanup_check: bool = (action_type == _Action.CLEANUP) and (self.__cleanup)
            if validate_check or cleanup_check:
                validate_method()

        if self.__light_warnings:
            self.__light_warnings.insert(0, f"WARNINGS: {self.__output_headers}")
            warnings.warn("\n".join(self.__light_warnings))
        if self.__hard_errors:
            self.__hard_errors.insert(0, f"ERRORS: {self.__output_headers}")
            raise ModelError("\n".join(self.__hard_errors))

        if self.__cleanup:
            for post_cleanup_job in self.__post_run_executor:
                post_cleanup_job()

    def __validate_executable_executor_period(self, executable: Executable) -> None:
        """Method to validate an executable's persistency
        Args:
            exec: Executable to be validated
        """
        # get all periodic tasks from all app modules belonging to the executable
        periodic_tasks_data = [
            [
                create_name_namespace_full_name(
                    app_module.ApplicationModuleRef.Name,
                    app_module.ApplicationModuleRef.Namespace,
                ),
                task.Name,
                int(task.Period.rstrip("ms")),
            ]
            for app_module in executable.ApplicationModules
            for task in app_module.ApplicationModuleRef.Tasks
            if task.Period.rstrip("ms").isdigit()
        ]
        if periodic_tasks_data:
            app_module_names, tasks_names, all_tasks_period = zip(*periodic_tasks_data)

            if executable.ExecutorPeriod == "Default":
                # calculate the common denominators of all PeriodicTasks
                executable.ExecutorPeriod = f"{math.gcd(*all_tasks_period)}ms"
            elif executable.ExecutorPeriod.rstrip("ms").isdigit():
                # ensure Executor Period <= the smallest task period
                executor_period = int(executable.ExecutorPeriod.rstrip("ms"))
                if executor_period > min(all_tasks_period):
                    # get tasks with the minimum
                    self.__hard_errors.append(
                        "\n".join(
                            [
                                f"Invalid ExecutorPeriod of Executable {executable.Name}: {executable.ExecutorPeriod}!",
                                f"Executor Period {executable.ExecutorPeriod} is longer than its Task(s)' period:",
                            ]
                            + [
                                f"   AppModule: {app_module_names[idx]} - Task: {tasks_names[idx]} with period {task_period}ms"  # pylint:disable=line-too-long
                                for idx, task_period in enumerate(all_tasks_period)
                                if executor_period > task_period
                            ]
                        )
                    )

    def __validate_executables(self) -> None:
        """Method to validate model's executables"""
        for executable in self.__model.main_model.Executables:
            # raise error if duplicates are discovered
            if executable.Name in self.__valid_executable:
                self.__hard_errors.append(f"Executable {executable.Name} is defined multiple times!")

            # valid executables have at least 1 ApplicationModule
            if executable.ApplicationModules:
                # add to valid executables
                self.__valid_executable[executable.Name] = executable
                # verify that all persistency files from all app modules are connected
                executable_persistency_filenames = (
                    {exec_per_file.FileName for exec_per_file in executable.PersistencyModule.PersistencyFiles}
                    if isinstance(
                        executable.PersistencyModule,
                        vafmodel.ExecutablePersistencyMapping,
                    )
                    else set()
                )

                for app_module_obj in executable.ApplicationModules:
                    # add App Module Design to the collection of connected app modules
                    app_module_id = create_name_namespace_full_name(
                        app_module_obj.ApplicationModuleRef.Name,
                        app_module_obj.ApplicationModuleRef.Namespace,
                    )
                    if app_module_id not in self.__connected_app_modules:
                        self.__connected_app_modules[app_module_id] = app_module_obj.ApplicationModuleRef
                    # get all persistency files from all app modules and verify they are connected
                    self.__hard_errors += [
                        f"AppModule {app_module_obj.ApplicationModuleRef.Name} has unconnected persistency file {per_file}!"  # pylint:disable=line-too-long
                        for per_file in app_module_obj.ApplicationModuleRef.PersistencyFiles
                        if per_file not in executable_persistency_filenames
                    ]

            # verify periodic task
            self.__validate_executable_executor_period(executable)

        # build warnings for unconnected app modules for integration project
        if self.__project_type == PType.INTEGRATION:
            self.__light_warnings += [
                f"App Module '{create_name_namespace_full_name(app_module.Name, app_module.Namespace)}' is defined, but not connected in any Executable"  # pylint:disable=line-too-long
                for app_module in self.__model.main_model.ApplicationModules
                if create_name_namespace_full_name(app_module.Name, app_module.Namespace)
                not in self.__connected_app_modules
            ]

        if self.__cleanup:
            # remove executables without app modules
            self.__model.main_model.Executables = list(self.__valid_executable.values())
            if self.__project_type == PType.INTEGRATION:
                # remove unconnected app modules if cleanup is activated
                self.__model.main_model.ApplicationModules = list(self.__connected_app_modules.values())

    def __validate_application_module(self) -> None:
        """Method to validate model's application modules"""
        for app_module in list(self.__connected_app_modules.values()):
            # validate Tasks
            all_task_names: list[str] = []
            all_run_afters: set[str] = set()
            for task in app_module.Tasks:
                all_task_names.append(task.Name)
                all_run_afters.update(task.RunAfter)

            for run_after in all_run_afters:
                if run_after not in all_task_names:
                    self.__hard_errors.append(
                        f"Task {run_after} is used in as a 'run_after' dependency in ApplicationModule"
                        f" {app_module.Namespace}::{app_module.Name}, but is not part of it."
                    )

    def __validate_interface_connections(self) -> None:
        """Method to validate model's interface connections"""
        unconnected_interfaces = []

        for app_module in self.__model.main_model.ApplicationModules:
            app_module_str = create_name_namespace_full_name(app_module.Name, app_module.Namespace)
            for ci in app_module.ConsumedInterfaces:
                if not ci.IsOptional and ci.InstanceName not in self.__model.connected_interfaces[app_module_str]:
                    unconnected_interfaces.append(f"{app_module_str} - {ci.InstanceName}")
            for pi in app_module.ProvidedInterfaces:
                if pi.InstanceName not in self.__model.connected_interfaces[app_module_str]:
                    unconnected_interfaces.append(f"{app_module_str} - {pi.InstanceName}")

        if unconnected_interfaces:
            self.__light_warnings.append(
                f"Following interfaces are defined but not connected: {unconnected_interfaces}"
            )

    def __validate_interface_definition(self) -> None:
        """Method to validate model's interface definitions"""
        # use module interface from main model since validation takes place after cleanup
        empty_interfaces = [
            create_name_namespace_full_name(module_interface.Name, module_interface.Namespace)
            for module_interface in self.__model.main_model.ModuleInterfaces
            if not module_interface.DataElements and not module_interface.Operations
        ]
        if empty_interfaces:
            self.__light_warnings.append(
                f"Following interfaces are defined without data elements and operations: {empty_interfaces}"
            )

    @staticmethod
    def __format_warning(
        message: Warning | str,
        category: type[Warning],
        filename: str,
        lineno: int,
        line: str | None = None,
    ) -> str:
        # pylint: disable=unused-argument
        """Format the warnings to be more user-friendly.
        Args:
            message (Warning | str): The warning message to format.
            category (type[Warning]): The category of the warning.
            filename (str): The name of the file where the warning occurred.
            lineno (int): The line number where the warning occurred.
            line (str, optional): The line of code where the warning occurred (default is None).
        Returns:
            str: Formatted warning message.
        """
        return "\n" + str(filename) + ":" + str(lineno) + ": " + category.__name__ + ":\n" + str(message) + "\n"
