# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Test of generation.py"""

from pathlib import Path

from vaf import vafmodel
from vaf.core.common.utils import to_camel_case, to_snake_case
from vaf.vafgeneration.generation import (
    FileHelper,
    data_type_to_str,
    get_data_type_include,
    is_data_type_base_type,
    is_data_type_cstdint_type,
    split_full_type,
)


def test_to_camel_case() -> None:
    """Test to camel case conversion"""
    assert to_camel_case("HelloWorld") == "HelloWorld"
    assert to_camel_case("Hello World") == "HelloWorld"
    assert to_camel_case("Hello_world") == "HelloWorld"
    assert to_camel_case("hello_world") == "HelloWorld"
    assert to_camel_case("Hello  World") == "HelloWorld"
    assert to_camel_case("hello") == "Hello"
    assert to_camel_case("Hello") == "Hello"


def test_to_snake_case() -> None:
    """Test to snake case conversion"""
    assert to_snake_case("Hello World") == "hello_world"
    assert to_snake_case("Hello_world") == "hello_world"
    assert to_snake_case("hello_world") == "hello_world"
    assert to_snake_case("Hello  World") == "hello_world"
    assert to_snake_case("hello") == "hello"
    assert to_snake_case("Hello") == "hello"
    assert to_snake_case("HelloWorld") == "hello_world"
    assert to_snake_case("HelloWorldPPortVHato") == "hello_world_p_port_v_hato"
    assert to_snake_case("HelloWorld_PPortVHato") == "hello_world_p_port_v_hato"


def test_data_type_to_str() -> None:
    """Test data type to string conversion"""
    # fmt: off
    assert data_type_to_str(vafmodel.DataType(Name="uint64_t", Namespace="")) == "std::uint64_t"
    assert data_type_to_str(vafmodel.DataType(Name="uint32_t", Namespace="")) == "std::uint32_t"
    assert data_type_to_str(vafmodel.DataType(Name="uint16_t", Namespace="")) == "std::uint16_t"
    assert data_type_to_str(vafmodel.DataType(Name="uint8_t", Namespace="")) == "std::uint8_t"
    assert data_type_to_str(vafmodel.DataType(Name="int64_t", Namespace="")) == "std::int64_t"
    assert data_type_to_str(vafmodel.DataType(Name="int32_t", Namespace="")) == "std::int32_t"
    assert data_type_to_str(vafmodel.DataType(Name="int16_t", Namespace="")) == "std::int16_t"
    assert data_type_to_str(vafmodel.DataType(Name="int8_t", Namespace="")) == "std::int8_t"
    assert data_type_to_str(vafmodel.DataType(Name="uint64_t", Namespace="std")) == "std::uint64_t"
    assert data_type_to_str(vafmodel.DataType(Name="uint8_t", Namespace="std")) == "std::uint8_t"
    assert data_type_to_str(vafmodel.DataType(Name="uint8_t", Namespace="not_std")) == "not_std::uint8_t"
    assert data_type_to_str(vafmodel.DataType(Name="double", Namespace="")) == "double"
    assert data_type_to_str(vafmodel.DataType(Name="float", Namespace="")) == "float"
    assert data_type_to_str(vafmodel.DataType(Name="bool", Namespace="")) == "bool"
    assert data_type_to_str(vafmodel.DataType(Name="ABC", Namespace="")) == "ABC"
    assert data_type_to_str(vafmodel.DataType(Name="ABC", Namespace="test")) == "test::ABC"
    assert data_type_to_str(vafmodel.DataType(Name="ABC", Namespace="test::1")) == "test::1::ABC"
    # fmt: on


def test_file_helper() -> None:
    """Test of file helper class"""
    f = FileHelper("file", "abc::dfg")

    assert f.get_file_path(Path.cwd(), ".h") == Path.cwd() / "include/abc/dfg/file.h"
    assert f.get_guard() == "ABC_DFG_FILE_H"
    assert f.get_include() == '#include "abc/dfg/file.h"'
    assert f.get_name() == "file"
    assert f.get_namespace_start() == "namespace abc {\nnamespace dfg {"

    f2 = FileHelper("file", "MyNamespace")
    assert f2.get_file_path(Path.cwd(), ".cpp") == Path.cwd() / "src/mynamespace/file.cpp"

    f3 = FileHelper("file", "MyNamespace")
    assert f3.get_file_path(Path.cwd(), ".txt") == Path.cwd() / "mynamespace/file.txt"
    assert f3.get_namespace_start() == "namespace MyNamespace {"


def test_get_data_type_include() -> None:
    """Test function get_data_type_include"""
    assert get_data_type_include(vafmodel.DataType(Name="T", Namespace="ABC")) == '#include "abc/impl_type_t.h"'
    assert (
        get_data_type_include(vafmodel.DataType(Name="T", Namespace="ABC::dfg")) == '#include "abc/dfg/impl_type_t.h"'
    )

    assert get_data_type_include(vafmodel.DataType(Name="uint8_t", Namespace="")) == "#include <cstdint>"
    assert get_data_type_include(vafmodel.DataType(Name="uint16_t", Namespace="")) == "#include <cstdint>"
    assert get_data_type_include(vafmodel.DataType(Name="uint32_t", Namespace="")) == "#include <cstdint>"
    assert get_data_type_include(vafmodel.DataType(Name="uint64_t", Namespace="")) == "#include <cstdint>"
    assert get_data_type_include(vafmodel.DataType(Name="int8_t", Namespace="")) == "#include <cstdint>"
    assert get_data_type_include(vafmodel.DataType(Name="int16_t", Namespace="")) == "#include <cstdint>"
    assert get_data_type_include(vafmodel.DataType(Name="int32_t", Namespace="")) == "#include <cstdint>"
    assert get_data_type_include(vafmodel.DataType(Name="int64_t", Namespace="")) == "#include <cstdint>"
    assert get_data_type_include(vafmodel.DataType(Name="int64_t", Namespace="std")) == "#include <cstdint>"

    assert (
        get_data_type_include(vafmodel.DataType(Name="int64_t", Namespace="not_std"))
        == '#include "not_std/impl_type_int64_t.h"'
    )

    assert get_data_type_include(vafmodel.DataType(Name="double", Namespace="")) == ""
    assert get_data_type_include(vafmodel.DataType(Name="float", Namespace="")) == ""
    assert get_data_type_include(vafmodel.DataType(Name="bool", Namespace="")) == ""

    assert get_data_type_include(vafmodel.DataType(Name="bool", Namespace="std")) == ""


def test_has_operation_out_or_inout_parameter() -> None:
    """Tests function has_operation_out_or_inout_parameter"""
    parameters: list[vafmodel.Parameter] = []
    parameters.append(
        vafmodel.Parameter(
            Name="dummy",
            TypeRef=vafmodel.DataType(Name="uint8_t", Namespace=""),
            Direction=vafmodel.ParameterDirection.IN,
        )
    )

    assert not vafmodel.Operation(Name="dummy", Parameters=parameters).has_any_parameter_out_inout

    parameters.append(
        vafmodel.Parameter(
            Name="dummy",
            TypeRef=vafmodel.DataType(Name="uint8_t", Namespace=""),
            Direction=vafmodel.ParameterDirection.INOUT,
        )
    )

    assert vafmodel.Operation(Name="dummy", Parameters=parameters).has_any_parameter_out_inout


def test_is_out_parameter() -> None:
    """Tests function is_out_parameter"""
    assert not vafmodel.Parameter(
        Name="dummy",
        TypeRef=vafmodel.DataType(Name="uint8_t", Namespace=""),
        Direction=vafmodel.ParameterDirection.IN,
    ).is_direction_out
    assert not vafmodel.Parameter(
        Name="dummy",
        TypeRef=vafmodel.DataType(Name="uint8_t", Namespace=""),
        Direction=vafmodel.ParameterDirection.INOUT,
    ).is_direction_out
    assert vafmodel.Parameter(
        Name="dummy",
        TypeRef=vafmodel.DataType(Name="uint8_t", Namespace=""),
        Direction=vafmodel.ParameterDirection.OUT,
    ).is_direction_out


def test_split_full_type() -> None:
    """Test for split_full_type"""
    assert split_full_type("test::Test") == ("Test", "test")
    assert split_full_type("Test") == ("Test", "")
    assert split_full_type("test1::test2::Test") == ("Test", "test1::test2")


def test_is_data_type_base_type() -> None:
    """Test for is_data_type_base_type"""
    assert is_data_type_base_type("float", "")
    assert is_data_type_base_type("double", "")
    assert is_data_type_base_type("bool", "")
    assert is_data_type_base_type("float", "std")
    assert is_data_type_base_type("double", "std")
    assert is_data_type_base_type("bool", "std")

    assert not is_data_type_base_type("float", "test")
    assert not is_data_type_base_type("double", "std1")
    assert not is_data_type_base_type("bool", "sstd")
    assert not is_data_type_base_type("uint8_t", "std")
    assert not is_data_type_base_type("dummy", "test")
    assert not is_data_type_base_type("uint8_t", "")


def test_is_data_type_cstdint_type() -> None:
    """Test for is_data_type_cstdint_type"""
    assert is_data_type_cstdint_type("uint8_t", "")
    assert is_data_type_cstdint_type("uint16_t", "")
    assert is_data_type_cstdint_type("uint32_t", "")
    assert is_data_type_cstdint_type("uint64_t", "")
    assert is_data_type_cstdint_type("int8_t", "")
    assert is_data_type_cstdint_type("int16_t", "")
    assert is_data_type_cstdint_type("int32_t", "")
    assert is_data_type_cstdint_type("int64_t", "")

    assert is_data_type_cstdint_type("uint8_t", "std")
    assert is_data_type_cstdint_type("uint16_t", "std")
    assert is_data_type_cstdint_type("uint32_t", "std")
    assert is_data_type_cstdint_type("uint64_t", "std")
    assert is_data_type_cstdint_type("int8_t", "std")
    assert is_data_type_cstdint_type("int16_t", "std")
    assert is_data_type_cstdint_type("int32_t", "std")
    assert is_data_type_cstdint_type("int64_t", "std")

    assert not is_data_type_cstdint_type("int64_t2", "")
    assert not is_data_type_cstdint_type("test", "test")
    assert not is_data_type_cstdint_type("test", "")
    assert not is_data_type_cstdint_type("int64_t", "test")
