# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Common generator functionality."""

import filecmp
from pathlib import Path
from typing import Any

from jinja2 import Environment, PackageLoader, select_autoescape

from vaf import vafmodel
from vaf.core.common.constants import PersistencyLibrary
from vaf.core.common.utils import (
    create_name_namespace_full_name,
    to_camel_case,
    to_snake_case,
)


def data_type_to_str(data_type: vafmodel.DataType) -> str:
    """Converts a DataType to string

    Args:
        data_type (vafmodel.DataType): The data type

    Returns:
        str: DataType as string
    """
    if data_type.is_cstdint_type:
        result = "std::" + data_type.Name
    else:
        result = (
            create_name_namespace_full_name(data_type.Name, data_type.Namespace.lower())
            if data_type.Namespace != ""
            else data_type.Name
        )
    return result


def implicit_data_type_to_str(name: str, namespace: str) -> str:
    """Converts a data type given by name and namespace to string

    Args:
        name (str): The name of the data type
        namespace (str): The namespace of the data type

    Returns:
        str: DataType as string
    """
    return data_type_to_str(vafmodel.DataType(Name=name, Namespace=namespace))


def add_namespace_to_name(name: str, namespace: str) -> str:
    """Add a namespace to name string

    Args:
        name (str): Name
        namespace (str): Namespace

    Returns:
        str: namespace + name as string
    """
    return namespace.replace("::", "_") + "_" + name if namespace != "" else name


def time_str_to_milliseconds(s: str) -> int:
    """Converts a time string to milliseconds. Example "10ms" -> 10

    Args:
        s (str): The time string.

    Raises:
        Exception: If the time string is invalid

    Returns:
        int: The time in milliseconds
    """
    if s.endswith("ns"):
        return int(int(s.removesuffix("ns")) / 1_000_000)
    if s.endswith("us"):
        return int(int(s.removesuffix("us")) / 1_000)
    if s.endswith("ms"):
        return int(s.removesuffix("ms"))
    if s.endswith("s"):
        return int(s.removesuffix("s")) * 1_000
    raise ValueError("Invalid time string: " + s)


def time_str_to_nanoseconds(s: str) -> int:
    """Converts a time string to nanoseconds. Example "10ns" -> 10

    Args:
        s (str): The time string.

    Raises:
        Exception: If the time string is invalid

    Returns:
        int: The time in nanoseconds
    """
    if s.endswith("ns"):
        return int(s.removesuffix("ns"))
    if s.endswith("us"):
        return int(s.removesuffix("us")) * 1_000
    if s.endswith("ms"):
        return int(s.removesuffix("ms")) * 1_000_000
    if s.endswith("s"):
        return int(s.removesuffix("s")) * 1_000_000_000
    raise ValueError("Invalid time string: " + s)


class FileHelper:
    """Helper class for files to be generated"""

    def __init__(self, name: str, namespace: str, force_file_name: bool = False) -> None:
        self.name = name
        self.namespace = namespace
        self.namespaces = namespace.split("::") if len(namespace) > 0 else []
        self.force_file_name = force_file_name

    def get_name(self) -> str:
        """Gets the name of the file

        Returns:
            str: The file name
        """
        if self.force_file_name:
            return self.name
        return to_snake_case(self.name)

    def _get_relative_file_path(self) -> str:
        """Gets the path to the file

        Args:
            base_dir (str): A base directory which will be prefixed

        Returns:
            str: The full file path
        """
        path = ""
        for n in self.namespaces:
            path += n.lower() + "/"
        path += self.get_name()
        return path

    def get_file_path(self, base_dir: Path | str, postfix: str) -> Path:
        """Gets the path to the file

        Args:
            base_dir (Path | str): A base directory which will be prefixed
            postfix (str): The file postfix

        Returns:
            str: The full file path
        """
        if isinstance(base_dir, str):
            base_dir = Path(base_dir)

        path = base_dir
        if ".h" in postfix:
            path = path / "include"
        elif ".cpp" in postfix:
            path = path / "src"
        path = path / Path(self._get_relative_file_path() + postfix)
        return path

    def get_simple_file_path(self, base_dir: Path | str, postfix: str) -> Path:
        """Gets the simple path to the file, i.e. without namespace structure

        Args:
            base_dir (Path | str): A base directory which will be prefixed
            postfix (str): The file postfix

        Returns:
            str: The full file path
        """
        if isinstance(base_dir, str):
            base_dir = Path(base_dir)

        path = base_dir
        if ".h" in postfix:
            path = path / "include"
        elif ".cpp" in postfix:
            path = path / "src"
        path = path / Path(self.get_name() + postfix)
        return path

    def get_include(self) -> str:
        """Gets the include of this file, so other files can include it

        Returns:
            str: The include
        """
        return '#include "' + self._get_relative_file_path() + '.h"'

    def get_datatype_include(self) -> str:
        """Gets the include of data type file, so other files can include it

        Returns:
            str: The include
        """

        path = ""
        for n in self.namespaces:
            path += n.lower() + "/"
        path += "impl_type_" + self.name.lower() + '.h"'

        return '#include "' + path

    def get_guard(self) -> str:
        """Get the include guard

        Returns:
            str: The include guard
        """
        ret = ""
        for n in self.namespaces:
            ret += n.upper() + "_"
        ret += self.get_name().upper() + "_H"
        ret = ret.replace(".", "_")

        return ret

    def get_include_guard_start(self) -> str:
        """Gets the include guard start

        Returns:
            str: The include guard start
        """
        return "#ifndef {guard}\n#define {guard}\n".format(guard=self.get_guard())

    def get_include_guard_end(self) -> str:
        """Gets the include guard end

        Returns:
            str: The include guard end
        """
        return f"#endif // {self.get_guard()}"

    def get_namespace_start(self) -> str:
        """Get the namespace opening

        Returns:
            str: The namespace opening
        """
        return "\n".join(f"namespace {ns} {{" for ns in self.namespaces) if self.namespaces else ""

    def get_namespace_end(self) -> str:
        """Get the namespace closing

        Returns:
            str: The namespace closing
        """
        return "\n".join([f"}} // namespace {ns}" for ns in reversed(self.namespaces)])  # if self.namespaces else ""

    def get_full_type_name(self) -> str:
        """Gets the full type name (including namespace)

        Returns:
            str: The full type name
        """
        return self.namespace + "::" + self.name if self.namespace != "" else self.name


def is_data_type_base_type(name: str, namespace: str) -> bool:
    """Checks if a data type is a C++ base type

    Args:
        name (str): The name of the data type
        namespace (str): The namespace of the data type

    Returns:
        bool: True if the data type is a C++ base type, False otherwise
    """
    return vafmodel.DataType(Name=name, Namespace=namespace).is_base_type


def is_data_type_cstdint_type(name: str, namespace: str) -> bool:
    """Checks if a data type is a C++ std int type

    Args:
        name (str): The name of the data type
        namespace (str): The namespace of the data type

    Returns:
        bool: True if the data type is a C++ std int type, False otherwise
    """
    return vafmodel.DataType(Name=name, Namespace=namespace).is_cstdint_type


def get_include(name: str, namespace: str) -> str:
    """Gets the C++ include line to include the object

    Args:
        name (str): The name of the object
        namespace (str): The namespace of the object

    Returns:
        str: C++ code to include the object
    """
    return FileHelper(name, namespace).get_include()


def get_data_type_include(datatype: vafmodel.DataType) -> str:
    """Gets the C++ include line to include a data type

    Args:
        datatype: DataType from which the include has to be derived

    Returns:
        str: C++ code to include the data type
    """
    result = None
    if datatype.is_base_type:
        result = ""
    elif datatype.is_cstdint_type:
        result = "#include <cstdint>"
    return result if result is not None else FileHelper(datatype.Name, datatype.Namespace).get_datatype_include()


def operation_get_return_type(operation: vafmodel.Operation, interface: vafmodel.ModuleInterface) -> str:
    """returns the operation return type

    Args:
        operation (vafmodel.Operation): The operation
        interface (vafmodel.ModuleInterface): The interface

    Returns:
        str: operation return type
    """

    out_parameters: list[vafmodel.Parameter] = []
    for p in operation.Parameters:
        if p.Direction is not vafmodel.ParameterDirection.IN:
            out_parameters.append(p)

    if len(out_parameters) > 0:
        out_parameter_type_namespace: str = interface.Namespace
        return out_parameter_type_namespace + "::" + operation.Name + "::Output"

    return "void"


def has_exactly_one_output_parameter(operation: vafmodel.Operation) -> bool:
    """Check operation  has exactly one out parameter

    Args:
        operation (vafmodel.Operation): The operation

    Returns:
        bool: True if has exactly one out parameter, False otherwise
    """
    out_parameters: list[vafmodel.Parameter] = []
    for p in operation.Parameters:
        if p.Direction is not vafmodel.ParameterDirection.IN:
            out_parameters.append(p)
    if len(out_parameters) == 1:
        return True
    return False


def split_full_type(full_type: str) -> tuple[str, str]:
    """Splits a full type into name and namespace

    Args:
        full_type (str): The full type

    Returns:
        tuple[str, str]: The name of the type and the namespace: Example: test::Test -> Test, test
    """
    separator = full_type.rfind("::")
    if separator == -1:
        return full_type, ""
    return full_type[separator + 2 :], full_type[0:separator]


class Generator:
    """Class for generating files."""

    def __init__(self) -> None:
        self.env = Environment(
            loader=PackageLoader("vaf.vafgeneration"),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )
        self.base_directory = Path.cwd()

    def set_base_directory(self, new_dir: Path) -> None:
        """Sets the base directory where files will be generated into.

        Args:
            new_dir (Path): The new directory.
        """
        self.base_directory = new_dir

    def _generate_to_file_common(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self,
        file: FileHelper,
        postfix: str,
        template_path: str,
        output_path: Path,
        check_to_overwrite: bool,
        **kwargs: Any,
    ) -> None:
        old_file_exists: bool = False
        old_file_output_path: Path
        if check_to_overwrite and output_path.exists() and Path.stat(output_path).st_size > 0:
            old_file_exists = True
            old_file_output_path = output_path
            output_path = output_path.parent / (output_path.name + ".new~")

        Path.mkdir(output_path.parent, parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            template = self.env.get_template(template_path)

            content = template.render(
                file_helper=file,
                file_postfix=postfix,
                to_camel_case=to_camel_case,
                to_snake_case=to_snake_case,
                data_type_to_str=data_type_to_str,
                implicit_data_type_to_str=implicit_data_type_to_str,
                add_namespace_to_name=add_namespace_to_name,
                time_str_to_milliseconds=time_str_to_milliseconds,
                operation_get_return_type=operation_get_return_type,
                **kwargs,
            )

            f.write(content)

        if kwargs.get("verbose_mode", False):
            print(f"VAF: Generating {output_path}")

        if old_file_exists:
            if not filecmp.cmp(old_file_output_path, output_path):
                if kwargs.get("verbose_mode", False):
                    print(f"File {old_file_output_path} already exists, file is generated to {output_path}")
            else:
                output_path.unlink()

    def generate_to_file(
        self,
        file: FileHelper,
        postfix: str,
        template_path: str,
        check_to_overwrite: bool = False,
        **kwargs: Any,
    ) -> None:
        """Generates a template to file.

        Args:
            file (FileHelper): The file to generate
            postfix (str): The file postfix
            template_path (str): The template file to use
            check_to_overwrite (bool): if true and already present file exits user is asked to overwrite or not
            **kwargs (Any): additional parameters to the render call
        """
        output_path = file.get_file_path(self.base_directory, postfix)
        self._generate_to_file_common(file, postfix, template_path, output_path, check_to_overwrite, **kwargs)

    def generate_to_simple_file(
        self,
        file: FileHelper,
        postfix: str,
        template_path: str,
        check_to_overwrite: bool = False,
        **kwargs: Any,
    ) -> None:
        """Generates a template to file not nested in namespaces.

        Args:
            file (FileHelper): The file to generate
            postfix (str): The file postfix
            template_path (str): The template file to use
            check_to_overwrite (bool): if true and already present file exits it is asked to overwrite or not
            **kwargs (Any): additional parameters to the render call
        """
        output_path = file.get_simple_file_path(self.base_directory, postfix)
        self._generate_to_file_common(file, postfix, template_path, output_path, check_to_overwrite, **kwargs)


def get_used_persistency_libs(model: vafmodel.MainModel) -> set[PersistencyLibrary]:
    """Returns a set of the used persistency libraries.
    Note: Works for integration projects only

    Args:
        model (vafmodel.MainModel): The main model

    Returns:
        set[constants.PersistencyLibrary]: Set of persistency libraries
    """
    return {exe.PersistencyModule.PersistencyLibrary for exe in model.Executables if exe.PersistencyModule}
