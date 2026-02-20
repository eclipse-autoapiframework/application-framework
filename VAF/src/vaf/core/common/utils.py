# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Utilities function that are used across components"""

import importlib.util
import json
import re
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Tuple

from vaf.core.common.constants import VAF_CFG_FILE


class ProjectType(Enum):
    """Enum class representing a VAF project type"""

    UNKNOWN = "unknown"
    INTERFACE = "interface-project"
    APP_MODULE = "application-module-project"
    INTEGRATION = "integration-project"
    WORKSPACE = "workspace"


def create_name_namespace_full_name(name: str, namespace: str) -> str:
    """Function to create full name based on name & namespace
    Args:
        name: name string
        namespace: namespace string
    Returns:
        Full Name
    """
    return "::".join([namespace, name])


def concat_str_to_path(path: Path, concat_str: str) -> Path:
    """Function to concatenate a string to a path
    Args:
        path: Path to dir/file to be concatenated
        concat_str: string to be concatenated at the end of the path
    """
    return path.parent / (path.name + concat_str)


def check_str_has_conflict(in_str: str) -> bool:
    """Function to check if a string has conflict
    Args:
        in_str: string to be checked
    Returns:
        boolean if string has any conflicts
    """
    return all(conflict_sign in in_str for conflict_sign in ["<<<<<<<", "=======", ">>>>>>>"])


def check_file_has_conflict(file_path: Path) -> bool:
    """Function to check if file has conflict(s)
    Args:
        file_path: Path to file to be checked
    Returns:
        boolean if file has any conflicts
    """
    with open(file_path, "r", encoding="utf-8") as file:
        file_content = file.read()

    return check_str_has_conflict(file_content)


def remove_file_if_exist(file_path: str | Path) -> None:
    """Function to remove file if it exists
    Args:
        file_path: Path/str of the file to be removed
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    if file_path.is_file():
        file_path.unlink()


def resolve_dotdot(path: Path) -> Path:
    """Resolve the dotdot notation in a path.
    Args:
        path (Path): The path to resolve.
    Returns:
        The resolved, absolute path.
    """
    parts = path.absolute().parts
    new_parts: list[str] = []
    for part in parts:
        if part == "..":
            if new_parts and new_parts[-1] != "..":
                new_parts.pop()
            else:
                new_parts.append(part)
        else:
            new_parts.append(part)
    return Path("/").joinpath(*new_parts)


def _get_default_model_path(project_type: ProjectType) -> str:
    if project_type == ProjectType.INTEGRATION:
        return "model/vaf/"
    if project_type == ProjectType.APP_MODULE:
        return "model/"
    if project_type == ProjectType.INTERFACE:
        return "."
    return ""


def get_project_type(path: Path | None = None) -> ProjectType:
    """Function to read the current project type from vaf_CFG_FILE
    Args:
        path (Path, optional): Project path to search for the VAF_CFG_FILE
    Returns:
        ProjectType enum representation of the project in the specified path or cwd
    """
    project_type_str = ""
    config_path = Path(VAF_CFG_FILE)
    if path is not None:
        config_path = path / VAF_CFG_FILE
    if config_path.is_file():
        with open(config_path, encoding="utf-8") as fh:
            project_type_str = json.load(fh).get("project-type", "unknown")
            return ProjectType(project_type_str)
    return ProjectType.UNKNOWN


def get_subprojects_in_path(project_type: ProjectType, search_path: Path) -> list[Path]:
    """Function that recursively returns the path of imported vaf subprojects.

    Interface projects are only returned, if they are imported be copy.

    Note:
        This function is only implemented for APP_MODULE project type.

    Args:
        project_type (ProjectType): Project type to search for
        search_path (Path): Directory to search in
    Returns:
        List of paths to VAF projects
    """
    assert project_type == ProjectType.APP_MODULE, (
        "This function is currently only implemented for APP_MODULE project type."
    )

    project_paths = []
    for file_path in search_path.rglob("import_*.py"):
        spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
        if spec is not None and spec.loader is not None:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Check if 'model_path' variable exists in the module
            if hasattr(module, "model_path"):
                project_paths.append(resolve_dotdot((file_path.parent / module.model_path)).parent)
    return project_paths


def get_projects_in_path(search_path: Path) -> list[tuple[Path, ProjectType]]:
    """Function that returns the paths and types of all VAF projects in the search path.

    Args:
        search_path (Path): Directory to search in
    Returns:
        List of tuples containing the paths and project types
    """
    projects = set()

    def search_directory(directory: Path) -> None:
        for path in directory.iterdir():
            if path.is_dir():
                project_type = get_project_type(path)
                if project_type != ProjectType.UNKNOWN:
                    projects.add((path, project_type))
                else:
                    search_directory(path)

    search_directory(search_path)
    return list(projects)


def get_parent_ws(search_path: Path) -> Path | None:
    """Function that searches for a parent workspace in the specified path.

    Args:
        search_path (Path): Directory to start the search from
    Returns:
        Path to workspace or None if no workspace is found
    """
    current_path = search_path.resolve()

    while current_path != current_path.parent:
        if get_project_type(current_path) == ProjectType.WORKSPACE:
            return current_path
        current_path = current_path.parent
    return None


def convert_args_to_kwargs(args: Tuple[Any], target_function: Callable[[Any], Any]) -> Dict[str, Any]:
    """Function to convert args into kwargs for a given target function
    Example: args = ("Devil Jin", 35, 95676)
             target_function's arguments (name, age, power)
             -> kwargs = {"name": "Devil Jin", "age": 35, "power": 95676}
             if args = (2234, "Kazuya", 44)
             -> kwargs = {"name": 2234, "age": "Kazuya", "power": 44}
    Args:
        args: Tuple of positional arguments that are going to be passed into target_function as kwargs
        target_function: function to which kwargs will be passed
    Returns:
        Dictionary that contains can be passed as kwargs to target_function
    """
    function_varnames = target_function.__code__.co_varnames
    return {function_varnames[idx]: arg for idx, arg in enumerate(args)}


def get_kwargs_from_local_variables(
    local_vars: Dict[str, Any], target_function: Callable[[Any], Any]
) -> Dict[str, Any]:
    """Function to build kwargs for a given target function based on current locals variables
    Args:
        local_vars: Dictionary that contains local variables
        target_function: function to which kwargs will be passed
    Returns:
        Dictionary that contains can be passed as kwargs to target_function
    """
    # also consider variables index
    function_varnames = target_function.__code__.co_varnames[: target_function.__code__.co_argcount]
    return {key: value for key, value in local_vars.items() if key in function_varnames}


def to_snake_case(s: str) -> str:
    """Converts a string to snake case

    Args:
        s (str): The input string

    Returns:
        str: The string converted to snake case
    """
    return (
        "_".join(re.sub("([A-Z][a-z]+)", r" \1", re.sub("([A-Z]+)", r" \1", s.replace("-", " "))).split())
        .lower()
        .replace(" ", "")
        .replace("__", "_")
    )


def to_camel_case(s: str) -> str:
    """Converts a string to camel case

    Args:
        s (str): The input string

    Returns:
        str: The string converted to camel case
    """
    pattern = re.compile(r"(?<!^)(?=[A-Z])")
    tmp = pattern.sub(" ", s)
    return re.sub(r"(_|-)+", " ", tmp).title().replace(" ", "")
