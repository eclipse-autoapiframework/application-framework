# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Test CaC with vafpy."""

# pylint: disable=missing-param-doc
# pylint: disable=missing-any-param-doc
# pylint: disable=anomalous-backslash-in-string
# pylint: disable=missing-raises-doc
# pylint: disable=line-too-long
# pylint: disable=too-few-public-methods
# pylint: disable=unused-variable
# pylint: disable=missing-class-docstring
# pylint: disable=too-many-locals
# pylint: disable=duplicate-code
# mypy: disable-error-code="no-untyped-def,union-attr"


# Ruff: ignore unused variables
# ruff: noqa: F841

import importlib
import json
import os
import re
import sys
from pathlib import Path
from shutil import copyfile, copytree
from types import ModuleType
from unittest import mock

from jinja2 import Template

from vaf import save_main_model, save_part_of_main_model, vafmodel, vafpy
from vaf.core.common.constants import get_package_version
from vaf.core.common.utils import ProjectType, create_name_namespace_full_name
from vaf.vafpy import CleanupOverride
from vaf.vafpy.model_runtime import ModelRuntime

### IMPORT MOCKING ###
# Store original __import__
orig_import = __import__
mock_import: dict[str, ModuleType] = {}


def import_mock(name: str, *args, **kwargs) -> ModuleType:
    """Function to mock import calls from CaC python files"""
    return mock_import[name] if name in mock_import else orig_import(name, *args, **kwargs)


def import_by_file_name(path_to_file: Path | str, file_name: str) -> ModuleType:
    """importlib.import_module somehow fails in pytest and can't find the modules"""
    spec = importlib.util.spec_from_file_location(file_name, f"{path_to_file}/{file_name}.py")
    if spec:
        module = importlib.util.module_from_spec(spec)
        if module and spec.loader:
            sys.modules[file_name] = module
            spec.loader.exec_module(module)

    if not module:
        raise RuntimeError(f"Failed to import module in {path_to_file}/{file_name}.py")

    return module


def mock_vafpy(path_to_model: str | Path, imports_list: list[str]) -> None:
    """Mock vafpy call using __import__
    Args:
        path_to_model: path to the output dir that contains the CaC models
        imports_list: all modules to be imported
    """
    with mock.patch("builtins.__import__", side_effect=import_mock):
        mock_import["vafpy"] = importlib.import_module("vaf.vafpy")
        for import_name in imports_list:
            if "/" in import_name:
                import_file_data = import_name.split("/")
                mock_import[".".join(import_file_data)] = import_by_file_name(
                    f"{path_to_model}/{''.join(import_file_data[:-1])}",
                    import_file_data[-1],
                )
            else:
                mock_import[import_name] = import_by_file_name(path_to_model, import_name)
        import_by_file_name(path_to_model, "model")


def __get_type_ref_string(typeref: vafmodel.TypeRef | vafmodel.DataType) -> str:
    return create_name_namespace_full_name(typeref.Name, typeref.Namespace)


def generate_jinja_files(file_path: Path, output_path: Path, **kwargs):
    """
    Generate Jinja files from JSON files by rendering a Jinja template.

    Args:
        file_path (Path): Path to the input JSON file.
        output_path (Path): Path to save the rendered Jinja file.
        **kwargs: Additional keyword arguments for Jinja rendering.
    """

    with open(file_path, "r", encoding="utf-8") as json_file:
        template_content = json_file.read()

    # Create a Jinja template from the JSON content
    template = Template(template_content)

    # Render the template with the provided kwargs
    rendered_content = template.render(vaf_version=get_package_version(), **kwargs)

    # Save the rendered content as a Jinja file
    with open(output_path, "w", encoding="utf-8") as jinja_file:
        jinja_file.write(rendered_content)


UT_PATH = Path(__file__).parent


### UNIT TESTS ###
def test_generate_vss_model(tmp_path) -> None:
    """Test Generation of VSS Artifacts based on CaC"""
    path_out = tmp_path / "vaf_260"

    copytree(UT_PATH / "test_data/common", path_out)
    copyfile(UT_PATH / "test_data/vaf_260/model.py", path_out / "model.py")

    mock_vafpy(path_out, ["vss"])

    save_main_model(path_out / "model.json", cleanup=CleanupOverride.ENABLE, project_type=ProjectType.INTEGRATION)

    generate_jinja_files(UT_PATH / "test_data/vaf_260/model.json.jinja", tmp_path / "goal-model.json")

    with open(path_out / "model.json", "r", encoding="utf-8") as generated:
        with open(tmp_path / "goal-model.json", "r", encoding="utf-8") as goal:
            assert json.loads(generated.read()) == json.loads(goal.read())


def test_adapt_persistency_cleanup(tmp_path) -> None:
    """VAF-633: Extend vafpy cleanup feature to respect persistency as well"""

    vafpy.import_model((UT_PATH / "test_data/vaf_633/model.json").as_posix())

    save_main_model(tmp_path / "model.json", cleanup=CleanupOverride.ENABLE, project_type=ProjectType.APP_MODULE)

    generate_jinja_files(UT_PATH / "test_data/vaf_633/goal-model.json.jinja", tmp_path / "goal-model.json")
    with open(tmp_path / "model.json", "r", encoding="utf-8") as generated:
        with open(tmp_path / "goal-model.json", "r", encoding="utf-8") as goal:
            assert json.loads(generated.read()) == json.loads(goal.read())


def test_validation_empty_interfaces(tmp_path, recwarn) -> None:
    """Detect and warn about empty interface definition in vafpy if cleanup is false"""
    original_working_dir = Path.cwd()
    path_out = tmp_path / "vaf_457"
    copytree(UT_PATH / "test_data/common", path_out)
    copyfile(
        UT_PATH / "test_data/vaf_457/model.py",
        path_out / "model.py",
    )
    os.chdir(path_out)

    try:
        mock_vafpy(path_out, [])

        save_part_of_main_model(
            Path("model.json"),
            ["DataTypeDefinitions", "ModuleInterfaces"],
            project_type=ProjectType.INTEGRATION,
        )

        relevant_warnings = [
            wrn for wrn in str(recwarn[0].message).split("\n") if wrn.startswith("Following interfaces")
        ]
        assert len(relevant_warnings) == 1

        goal_epmty_interfaces = [
            "demo::EmptyInterface",
        ]

        result_epmty_interfaces = re.findall(
            r"Following interfaces are defined without data elements and operations: \[(.+?)\]",
            relevant_warnings[0],
        )
        assert result_epmty_interfaces, f"Incorrect Warning returned: {relevant_warnings[0]}"
        result_epmty_interfaces = [
            epmty_interface.replace("'", "").replace('"', "")
            for epmty_interface in result_epmty_interfaces[0].split(", '")
        ]
        assert set(goal_epmty_interfaces) == set(result_epmty_interfaces)
    finally:
        os.chdir(original_working_dir)


def test_bug_remove_unused_artifacts(tmp_path) -> None:
    """Bug in __remove_unused_artifacts"""
    path_out = tmp_path / "vaf_386"

    copytree(UT_PATH / "test_data/vaf_386", path_out)

    mock_vafpy(path_out, ["imported_models/interface_project", "app_module1"])

    save_main_model(path_out / "model.json", cleanup=CleanupOverride.ENABLE, project_type=ProjectType.INTEGRATION)

    generate_jinja_files(UT_PATH / "test_data/vaf_386/model.json.jinja", tmp_path / "goal-model.json")

    with open(path_out / "model.json", "r", encoding="utf-8") as generated:
        with open(tmp_path / "goal-model.json", "r", encoding="utf-8") as goal:
            assert json.loads(generated.read()) == json.loads(goal.read())


def test_consolidation_fixed_size_array_vector() -> None:
    """Consolidation of Fixed Size Arrays & Vectors
    Update: Feature reverted!
    """

    ma_struct = vafpy.datatypes.Struct(name="MaStruct", namespace="test")
    ma_struct.add_subelement(name="x", datatype=vafpy.BaseTypes.DOUBLE)

    vafpy.datatypes.Vector(name="MaVector", namespace="test", datatype=ma_struct)

    vafpy.datatypes.Vector(name="MyVectorFixed", namespace="test", datatype=ma_struct)
    vafpy.datatypes.Vector(name="MyVectorFixedAgain", namespace="test", datatype=ma_struct)

    vafpy.datatypes.Vector(name="MockVector1", namespace="test", datatype=vafpy.BaseTypes.UINT16_T)
    vafpy.datatypes.Vector(name="MockVector2", namespace="test", datatype=vafpy.BaseTypes.UINT16_T)
    vafpy.datatypes.Vector(name="MockVector3", namespace="test", datatype=vafpy.BaseTypes.UINT16_T)
    vafpy.datatypes.Vector(name="MockVector4", namespace="test", datatype=vafpy.BaseTypes.FLOAT)
    vafpy.datatypes.Vector(name="MockVector5", namespace="test", datatype=vafpy.BaseTypes.BOOL)

    vafpy.datatypes.Array(name="MyFixedArray", namespace="test", datatype=ma_struct, size=2)
    vafpy.datatypes.Array(name="MyFixedArray2", namespace="test", datatype=ma_struct, size=2)

    vafpy.datatypes.Array(name="MockArray1", namespace="test", datatype=vafpy.BaseTypes.UINT16_T, size=2)
    vafpy.datatypes.Array(name="MockArray2", namespace="test", datatype=vafpy.BaseTypes.UINT16_T, size=2)
    vafpy.datatypes.Array(name="MockArray3", namespace="test", datatype=vafpy.BaseTypes.FLOAT, size=2)
    vafpy.datatypes.Array(name="MockArray4", namespace="test", datatype=vafpy.BaseTypes.BOOL, size=2)

    model = ModelRuntime()
    assert len(model.main_model.DataTypeDefinitions.Vectors) == 8
    for idx, name in enumerate(
        [
            "MaVector",
            "MyVectorFixed",
            "MyVectorFixedAgain",
            "MockVector1",
            "MockVector2",
            "MockVector3",
            "MockVector4",
            "MockVector5",
        ]
    ):
        assert model.main_model.DataTypeDefinitions.Vectors[idx].Name == name

    assert len(model.main_model.DataTypeDefinitions.Arrays) == 6
    for idx, name in enumerate(
        [
            "MyFixedArray",
            "MyFixedArray2",
            "MockArray1",
            "MockArray2",
            "MockArray3",
            "MockArray4",
        ]
    ):
        assert model.main_model.DataTypeDefinitions.Arrays[idx].Name == name


def test_consolidation_fixed_size_array_vector_reference() -> None:
    """Assert References of Consolidated Fixed Size Arrays & Vectors"""

    ma_struct = vafpy.datatypes.Struct(name="MaStruct", namespace="test")
    ma_struct.add_subelement(name="x", datatype=vafpy.BaseTypes.DOUBLE)

    vafpy.datatypes.Vector(name="MaVector", namespace="test", datatype=ma_struct)

    my_vector_fix = vafpy.datatypes.Vector(name="MyVectorFixed", namespace="test", datatype=ma_struct)

    mock_vector2 = vafpy.datatypes.Vector(name="MockVector2", namespace="test", datatype=vafpy.BaseTypes.FLOAT)
    mock_vector3 = vafpy.datatypes.Vector(name="MockVector3", namespace="test", datatype=vafpy.BaseTypes.FLOAT)
    mock_vector4 = vafpy.datatypes.Vector(name="MockVector4", namespace="test", datatype=vafpy.BaseTypes.FLOAT)

    mock_array1 = vafpy.datatypes.Array(name="MockArray1", namespace="test", datatype=vafpy.BaseTypes.UINT16_T, size=2)
    mock_array2 = vafpy.datatypes.Array(name="MockArray2", namespace="test", datatype=vafpy.BaseTypes.UINT16_T, size=2)
    mock_array3 = vafpy.datatypes.Array(name="MockArray3", namespace="test", datatype=vafpy.BaseTypes.FLOAT, size=2)

    mock_struct = vafpy.datatypes.Struct(name="MockStruct", namespace="test")
    mock_struct.add_subelement(name="W", datatype=mock_vector3)
    mock_struct.add_subelement(name="H", datatype=mock_vector2)
    mock_struct.add_subelement(name="Y", datatype=mock_array3)
    mock_struct.add_subelement(name="M", datatype=mock_array1)
    mock_struct.add_subelement(name="C", datatype=mock_array2)
    mock_struct.add_subelement(name="A", datatype=mock_vector4)

    vafpy.datatypes.TypeRef(name="MockTypeRef", namespace="test", datatype=mock_array3)

    vafpy.datatypes.Map(name="MockMap", namespace="test", key_type=mock_array2, value_type=mock_array3)
    vafpy.datatypes.Map(
        name="MockMap1",
        namespace="test",
        key_type=mock_struct,
        value_type=my_vector_fix,
    )

    vafpy.datatypes.Vector(name="RefVector", namespace="test", datatype=mock_array2)

    vafpy.datatypes.Array(name="RefArray", namespace="test", datatype=mock_vector4, size=2)

    mock_interface = vafpy.ModuleInterface(name="MockInterface", namespace="test")
    mock_interface.add_data_element(name="struct", datatype=mock_struct)
    mock_interface.add_data_element(name="array", datatype=mock_array2)
    mock_interface.add_data_element(name="vector", datatype=mock_vector4)

    mock_interface_func = vafpy.ModuleInterface(name="MockInterfaceFWraps", namespace="interfaces1")
    mock_interface_func.add_operation(
        name="func1",
        in_parameter={"in1": mock_array2, "in2": mock_vector4},
        out_parameter={"out1": mock_array3, "out2": mock_vector4},
        inout_parameter={"inout1": mock_array1, "inout2": mock_array2},
    )

    mock_mod = vafpy.ApplicationModule(name="temp", namespace="test")
    mock_mod.add_provided_interface(instance_name="MockIf1", interface=mock_interface)
    mock_mod.add_provided_interface(instance_name="MockIf2", interface=mock_interface_func)

    # assert reference in struct
    mock_struct_goal = {
        "W": "test::MockVector3",
        "H": "test::MockVector2",
        "Y": "test::MockArray3",
        "M": "test::MockArray1",
        "C": "test::MockArray2",
        "A": "test::MockVector4",
    }
    model = ModelRuntime()
    for subelement in model.main_model.DataTypeDefinitions.Structs[-1].SubElements:
        assert __get_type_ref_string(subelement.TypeRef) == mock_struct_goal[subelement.Name]
    # assert corresponding typerefs
    mock_typeref_goal = {
        "MockTypeRef": "test::MockArray3",
    }
    assert len(model.main_model.DataTypeDefinitions.TypeRefs) == len(mock_typeref_goal)
    for typeref in model.main_model.DataTypeDefinitions.TypeRefs:
        assert __get_type_ref_string(typeref.TypeRef) == mock_typeref_goal[typeref.Name]

    # assert reference in maps
    assert __get_type_ref_string(model.main_model.DataTypeDefinitions.Maps[-2].MapKeyTypeRef) == "test::MockArray2"
    assert __get_type_ref_string(model.main_model.DataTypeDefinitions.Maps[-2].MapValueTypeRef) == "test::MockArray3"
    assert __get_type_ref_string(model.main_model.DataTypeDefinitions.Maps[-1].MapKeyTypeRef) == "test::MockStruct"
    assert __get_type_ref_string(model.main_model.DataTypeDefinitions.Maps[-1].MapValueTypeRef) == "test::MyVectorFixed"

    # assert reference in vectors
    assert __get_type_ref_string(model.main_model.DataTypeDefinitions.Vectors[-1].TypeRef) == "test::MockArray2"
    # assert reference in arrays
    assert __get_type_ref_string(model.main_model.DataTypeDefinitions.Arrays[-1].TypeRef) == "test::MockVector4"

    # assert reference in module interface
    mock_interface_goal = {
        "struct": "test::MockStruct",
        "array": "test::MockArray2",
        "vector": "test::MockVector4",
    }
    for data_element in model.main_model.ModuleInterfaces[0].DataElements:
        assert __get_type_ref_string(data_element.TypeRef) == mock_interface_goal[data_element.Name]

    mock_interface_fwrap_goal = {
        "in1": "test::MockArray2",
        "in2": "test::MockVector4",
        "out1": "test::MockArray3",
        "out2": "test::MockVector4",
        "inout1": "test::MockArray1",
        "inout2": "test::MockArray2",
    }
    for param in model.main_model.ModuleInterfaces[1].Operations[0].Parameters:
        assert __get_type_ref_string(param.TypeRef) == mock_interface_fwrap_goal[param.Name]


def test_bug_cleanup_vss_model(tmp_path) -> None:
    """Test Bug on Cleanup of VSS Model"""
    path_out = tmp_path / "vaf_399"

    copytree(UT_PATH / "test_data/vaf_399", path_out)

    mock_vafpy(path_out, ["vss", "app_module1"])

    save_main_model(path_out / "model.json", cleanup=CleanupOverride.ENABLE, project_type=ProjectType.APP_MODULE)

    generate_jinja_files(UT_PATH / "test_data/vaf_399/model.json.jinja", tmp_path / "goal-model.json")

    with open(path_out / "model.json", "r", encoding="utf-8") as generated:
        with open(tmp_path / "goal-model.json", "r", encoding="utf-8") as goal:
            assert json.loads(generated.read()) == json.loads(goal.read())


def test_bug_cleanup_vaf_422(tmp_path) -> None:
    """Test vafpy cleanup fails with source node ::uint32_t not in graph"""
    path_out = tmp_path / "vaf_422"

    copytree(UT_PATH / "test_data/vaf_422", path_out)

    mock_vafpy(path_out, ["imported_models/interface", "app_module1"])

    save_main_model(path_out / "model.json", cleanup=CleanupOverride.ENABLE, project_type=ProjectType.APP_MODULE)

    generate_jinja_files(UT_PATH / "test_data/vaf_422/model.json.jinja", tmp_path / "goal-model.json")

    with open(path_out / "model.json", "r", encoding="utf-8") as generated:
        with open(tmp_path / "goal-model.json", "r", encoding="utf-8") as goal:
            assert json.loads(generated.read()) == json.loads(goal.read())


def test_bug_vaf_553(tmp_path) -> None:
    """Custom datatype as operation parameter is removed from model"""
    path_out = tmp_path / "vaf_553"

    copytree(UT_PATH / "test_data/vaf_553", path_out)

    mock_vafpy(path_out, ["imported_models/interfaces", "app_module1"])

    save_main_model(path_out / "model.json", cleanup=CleanupOverride.ENABLE, project_type=ProjectType.APP_MODULE)

    vafmodel.load_json(path_out / "model.json")


def test_vaf_577_string_base_type(tmp_path) -> None:
    """Add string to basetypes"""
    original_working_dir = Path.cwd()
    path_out = tmp_path / "vaf_577_string_base_type"
    path_out.mkdir(parents=True, exist_ok=True)
    copyfile(UT_PATH / "test_data/vaf_577/model.py", path_out / "model.py")
    os.chdir(path_out)

    try:
        mock_vafpy(path_out, [])

        save_main_model(path_out / "model.json", cleanup=CleanupOverride.ENABLE, project_type=ProjectType.INTEGRATION)

        generate_jinja_files(UT_PATH / "test_data/vaf_577/model.json.jinja", tmp_path / "goal-model.json")

        with open(path_out / "model.json", "r", encoding="utf-8") as generated:
            with open(tmp_path / "goal-model.json", "r", encoding="utf-8") as goal:
                assert json.loads(generated.read()) == json.loads(goal.read())
    finally:
        os.chdir(original_working_dir)
