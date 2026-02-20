# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Test example."""

# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods
# pylint: disable=unused-variable
# pylint: disable=missing-function-docstring
# pylint: disable=dangerous-default-value
# pylint: disable=unused-argument
# pylint: disable=too-many-function-args
# pylint: disable=no-value-for-parameter
# pylint: disable=unexpected-keyword-arg
# pylint: disable=too-many-statements

# mypy: disable-error-code="union-attr, call-arg, arg-type"

# Ruff: ignore unused variables
# ruff: noqa: F841
import unittest
from datetime import timedelta

import pytest

from vaf import vafmodel, vafpy
from vaf.core.common.utils import create_name_namespace_full_name
from vaf.vafpy.core import ModelError, VafpyAbstractBase, VafpyAbstractModelRuntime
from vaf.vafpy.factory import VafpyFactory
from vaf.vafpy.model_runtime import ModelRuntime


class VafpyIntruder(VafpyAbstractModelRuntime):
    def remove_element(self, element: VafpyAbstractBase) -> None:
        """Remove an element from the model
        Args:
            element: element to be removed from the model
        Raises:
            NotImplementedError
        """
        pass  # pylint: disable=unnecessary-pass

    def replace_element(self, element: VafpyAbstractBase) -> None:
        """Replace an element with same name & namespace
        Args:
            element: element to be replaced in the model
        Raises:
            NotImplementedError
        """
        pass  # pylint: disable=unnecessary-pass


def test_intruders() -> None:
    """Ensure nobody can misuse VafpyAbstractModelRuntime"""
    with pytest.raises(TypeError):
        VafpyAbstractModelRuntime()  # type:ignore[abstract]  # pylint: disable=abstract-class-instantiated
    with pytest.raises(NotImplementedError) as err:
        VafpyIntruder()

    assert err.value.args[0] == "__init__() is not implemented."


class TestMain(unittest.TestCase):
    """
    TestMain class
    """

    def __get_type_ref_string(self, typeref: vafmodel.DataTypeRef | vafmodel.ModelElement) -> str:
        return create_name_namespace_full_name(typeref.Name, typeref.Namespace)

    def setUp(self) -> None:
        """Reset model runtime for each test"""
        self.model = ModelRuntime()
        self.model.reset()

    def test_string(self) -> None:
        """test string creation"""
        vafpy.datatypes.String("FirstString", "test")
        r = vafpy.datatypes.String(name="MyString", namespace="test")
        assert isinstance(r, vafpy.datatypes.String)

        VafpyFactory.create_from_model(vafmodel.String(Name="Mulligan", Namespace="test"), vafpy.String)  # pylint:disable=protected-access

        assert len(self.model.element_by_namespace["test"]["Strings"]) == 3
        assert self.model.element_by_namespace["test"]["Strings"]["FirstString"].Name == "FirstString"
        assert self.model.element_by_namespace["test"]["Strings"]["MyString"].Name == "MyString"
        assert self.model.main_model.DataTypeDefinitions.Strings[0].Name == "FirstString"
        assert self.model.main_model.DataTypeDefinitions.Strings[1].Name == "MyString"
        assert self.model.main_model.DataTypeDefinitions.Strings[2].Name == "Mulligan"

    def test_enum(self) -> None:
        """test string creation"""
        # correct construction with default_values
        my_enum = vafpy.datatypes.Enum(name="MyEnum", namespace="test")
        my_enum.add_literal(item="ABC")
        my_enum.add_literal(item="DEF")
        my_enum.add_literal_list(literals=["COB", "PREN"])

        assert self.model.main_model.DataTypeDefinitions.Enums[0].Literals[0].Item == "ABC"
        assert self.model.main_model.DataTypeDefinitions.Enums[0].Literals[0].Value == 0
        assert self.model.main_model.DataTypeDefinitions.Enums[0].Literals[1].Item == "DEF"
        assert self.model.main_model.DataTypeDefinitions.Enums[0].Literals[1].Value == 1
        assert self.model.main_model.DataTypeDefinitions.Enums[0].Literals[2].Item == "COB"
        assert self.model.main_model.DataTypeDefinitions.Enums[0].Literals[2].Value == 2
        assert self.model.main_model.DataTypeDefinitions.Enums[0].Literals[3].Item == "PREN"
        assert self.model.main_model.DataTypeDefinitions.Enums[0].Literals[3].Value == 3

        vafpy.datatypes.Enum(name="MyEnum2", namespace="test", literals=["AVA", "CBE"])

        assert len(self.model.element_by_namespace["test"]["Enums"]) == 2
        assert self.model.main_model.DataTypeDefinitions.Enums[1].Literals[0].Item == "AVA"
        assert self.model.main_model.DataTypeDefinitions.Enums[1].Literals[0].Value == 0
        assert self.model.main_model.DataTypeDefinitions.Enums[1].Literals[1].Item == "CBE"
        assert self.model.main_model.DataTypeDefinitions.Enums[1].Literals[1].Value == 1

        # construction with user defined values
        yummy = vafpy.datatypes.Enum(name="Yummy", namespace="test", literals=[("AVA", 3), ("CBE", 77), "THN"])
        yummy.add_literal(item="ABC")
        yummy.add_literal(item="DEF", value=2)
        yummy.add_literal(item="ERF")
        yummy.add_literal_list(literals=["AXR", ("VERANDA", 101)])
        yummy.add_literal(item="CIC")

        assert self.model.main_model.DataTypeDefinitions.Enums[2].Literals[0].Item == "AVA"
        assert self.model.main_model.DataTypeDefinitions.Enums[2].Literals[0].Value == 3
        assert self.model.main_model.DataTypeDefinitions.Enums[2].Literals[1].Item == "CBE"
        assert self.model.main_model.DataTypeDefinitions.Enums[2].Literals[1].Value == 77
        assert self.model.main_model.DataTypeDefinitions.Enums[2].Literals[2].Item == "THN"
        assert self.model.main_model.DataTypeDefinitions.Enums[2].Literals[2].Value == 78
        assert self.model.main_model.DataTypeDefinitions.Enums[2].Literals[3].Item == "ABC"
        assert self.model.main_model.DataTypeDefinitions.Enums[2].Literals[3].Value == 79
        assert self.model.main_model.DataTypeDefinitions.Enums[2].Literals[4].Item == "DEF"
        assert self.model.main_model.DataTypeDefinitions.Enums[2].Literals[4].Value == 2
        assert self.model.main_model.DataTypeDefinitions.Enums[2].Literals[5].Item == "ERF"
        assert self.model.main_model.DataTypeDefinitions.Enums[2].Literals[5].Value == 80
        assert self.model.main_model.DataTypeDefinitions.Enums[2].Literals[6].Item == "AXR"
        assert self.model.main_model.DataTypeDefinitions.Enums[2].Literals[6].Value == 81
        assert self.model.main_model.DataTypeDefinitions.Enums[2].Literals[7].Item == "VERANDA"
        assert self.model.main_model.DataTypeDefinitions.Enums[2].Literals[7].Value == 101
        assert self.model.main_model.DataTypeDefinitions.Enums[2].Literals[8].Item == "CIC"
        assert self.model.main_model.DataTypeDefinitions.Enums[2].Literals[8].Value == 102

        ## assert validations: test bad constructions
        # duplicate entries
        with pytest.raises(ModelError):
            yummy.add_literal(item="ABC")
        with pytest.raises(ModelError):
            yummy.add_literal(item="ABC", value=2)
        with pytest.raises(ModelError):
            yummy.add_literal(item=" COPACABANA", value=55)
        with pytest.raises(ModelError):
            yummy.add_literal(item="SIU", value=79)
        # duplicate entry from lists
        with pytest.raises(ModelError) as err_msg:
            yummy.add_literal_list(literals=["AXR", ("GARNA", 101), "GARNA", "CBD", "HBL", ("AXR", 45)])
        assert err_msg.value.args[0] == "Enum - Duplicate label not allowed: 'AXR'"
        with pytest.raises(ModelError) as err_msg:
            yummy.add_literal_list(literals=[("GARNA", 101), "GARNA", "CBD", "HBL", ("RRT", 45)])
        assert err_msg.value.args[0] == "Enum - Duplicate value not allowed: '101' from label 'GARNA'"

        with pytest.raises(ModelError) as err_msg:
            vafpy.datatypes.Enum(
                name="Gummi",
                namespace="test",
                literals=["AXR", ("GARNA", 101), "GARNA", "CBD", "HBL", ("AXR", 45)],
            )
        assert err_msg.value.args[0] == "Enum - Duplicate label in constructor: '['AXR', 'GARNA', 'GARNA', 'AXR']'"
        with pytest.raises(ModelError) as err_msg:
            vafpy.datatypes.Enum(
                name="Bummi",
                namespace="test",
                literals=[("GARNA", 101), "TRN", ("CBD", 102), "HBL", ("RRT", 101)],
            )
        assert (
            err_msg.value.args[0]
            == "Enum - Duplicate value in constructor: '[('GARNA', 101), ('TRN', 102), ('CBD', 102), ('RRT', 101)]'"
        )

    def test_invalid_data_types(self) -> None:
        """Test unnamed vector creation"""
        # invalid init arguments
        with pytest.raises(TypeError):
            vafpy.datatypes.String("test", "TestString", vafpy.BaseTypes.UINT16_T, 223, 815)

        # invalid namespace
        with pytest.raises(vafpy.core.ModelError):
            vafpy.datatypes.String("123test", "TestString")

        # invalid name
        with pytest.raises(vafpy.core.ModelError):
            vafpy.datatypes.String("aber::comb", "TestString")
            vafpy.datatypes.String("aber", "comb::TestString")

        # duplicates
        with pytest.raises(vafpy.core.ModelError):
            vafpy.datatypes.String("valid", "TestString")
            vafpy.datatypes.String("valid", "TestString")

    def test_invalid_vector_array(self) -> None:
        """Test unnamed vector creation"""

        # vector doesn't accept sizes
        with pytest.raises(TypeError):
            vafpy.datatypes.Vector("test", vafpy.BaseTypes.UINT16_T, 223, "TestVector", 815)

        # invalid arguments
        with pytest.raises(TypeError):
            vafpy.datatypes.Vector(
                namespace="test",
                name="TestVector",
                datatype=vafpy.BaseTypes.UINT16_T,
                abrakadabra=815,
            )

        # array with no size
        with pytest.raises(TypeError):
            vafpy.datatypes.Array(namespace="test", name="TestArray", datatype=vafpy.BaseTypes.UINT16_T)

        # vector and array without name
        with pytest.raises(TypeError):
            vafpy.datatypes.Array(namespace="test", datatype=vafpy.BaseTypes.UINT16_T, size=2)
        with pytest.raises(TypeError):
            vafpy.datatypes.Vector(namespace="test", datatype=vafpy.BaseTypes.UINT16_T)

    def test_named_vector(self) -> None:
        """Test named vector creation"""

        vafpy.datatypes.Vector(name="MyVector", namespace="test", datatype=vafpy.BaseTypes.UINT16_T)

        assert "TypeRefs" not in self.model.element_by_namespace["test"]
        self.assertEqual(
            self.model.element_by_namespace["test"]["Vectors"]["MyVector"].Name,
            "MyVector",
        )
        self.assertEqual(
            self.__get_type_ref_string(self.model.element_by_namespace["test"]["Vectors"]["MyVector"].TypeRef),
            "::uint16_t",
        )
        assert len(self.model.main_model.DataTypeDefinitions.Vectors) == 1
        assert self.model.main_model.DataTypeDefinitions.Vectors[0].Name == "MyVector"
        assert self.model.main_model.DataTypeDefinitions.Vectors[0].TypeRef == vafmodel.DataType(
            Name="uint16_t", Namespace=""
        )

    def test_named_vector_in_struct(self) -> None:
        """Test named vectors as struct subelement"""

        my_struct = vafpy.datatypes.Struct(name="MyStruct", namespace="test")
        my_struct.add_subelement(name="x", datatype=vafpy.BaseTypes.DOUBLE)

        my_vector = vafpy.datatypes.Vector(name="MyVector", namespace="test", datatype=my_struct)

        my_outer_struct = vafpy.datatypes.Struct(name="MyStruct2", namespace="test")
        my_outer_struct.add_subelement(name="y", datatype=my_vector)

        self.assertEqual(len(self.model.main_model.DataTypeDefinitions.Structs), 2)
        self.assertEqual(
            self.__get_type_ref_string(self.model.main_model.DataTypeDefinitions.Structs[1].SubElements[0].TypeRef),
            "test::MyVector",
        )
        self.assertEqual(len(self.model.main_model.DataTypeDefinitions.Vectors), 1)
        self.assertEqual(self.model.main_model.DataTypeDefinitions.Vectors[0].Name, "MyVector")

    def test_exe(self) -> None:
        """Test creating a simple but complete model"""

        my_interface = vafpy.ModuleInterface(name="MyInterface", namespace="interfaces")
        my_interface.add_data_element(name="data_element1", datatype=vafpy.BaseTypes.UINT16_T)

        app_module1 = vafpy.ApplicationModule(name="AppModule1", namespace="app_modules")
        app_module1.add_provided_interface(instance_name="Instance1", interface=my_interface)

        app_module2 = vafpy.ApplicationModule(name="AppModule2", namespace="app_modules")
        app_module2.add_consumed_interface(instance_name="Instance1", interface=my_interface)

        exe = vafpy.Executable("exe", timedelta(milliseconds=10))
        exe.add_application_module(app_module1, [])
        exe.add_application_module(app_module2, [])
        exe.connect_interfaces(app_module1, "Instance1", app_module2, "Instance1")

        vafpy.runtime.get_main_model()

    def test_complex(self) -> None:
        """Test creating a complex and complete model"""

        my_string = vafpy.datatypes.String(name="MyString", namespace="complex")

        my_struct = vafpy.datatypes.Struct(name="MyStruct", namespace="complex")
        my_struct.add_subelement(name="a", datatype=my_string)
        my_struct.add_subelement(name="b", datatype=vafpy.BaseTypes.BOOL)

        my_vector = vafpy.datatypes.Vector(name="MyVector", namespace="complex1", datatype=my_struct)
        my_map = vafpy.datatypes.Map(
            name="MyMap",
            namespace="complex3",
            key_type=vafpy.BaseTypes.UINT16_T,
            value_type=vafpy.BaseTypes.DOUBLE,
        )

        my_array = vafpy.datatypes.Array(name="MyArray", namespace="complex2", datatype=my_map, size=100)

        my_type_ref = vafpy.datatypes.TypeRef(name="MyTypeRef", namespace="other", datatype=my_vector)

        my_enum = vafpy.datatypes.Enum(name="MyEnum", namespace="complex")
        my_enum.add_literal(item="ABC", value=1)
        my_enum.add_literal(item="DEF", value=2)

        my_interface = vafpy.ModuleInterface(name="MyInterface", namespace="inter")
        my_interface.add_data_element(name="a", datatype=my_string)
        my_interface.add_data_element(name="b", datatype=my_struct)
        my_interface.add_data_element(name="c", datatype=my_vector)
        my_interface.add_data_element(name="d", datatype=my_map)
        my_interface.add_data_element(name="e", datatype=my_array)
        my_interface.add_data_element(name="f", datatype=my_type_ref)
        my_interface.add_data_element(name="g", datatype=my_enum)

        app1 = vafpy.ApplicationModule(name="App1", namespace="app1")
        app1.add_provided_interface(instance_name="Instance1", interface=my_interface)

        app2 = vafpy.ApplicationModule(name="App2", namespace="app2")
        app2.add_consumed_interface(instance_name="Instance2", interface=my_interface)

        exe = vafpy.Executable("exe", timedelta(milliseconds=10))
        exe.add_application_module(app1, [])
        exe.add_application_module(app2, [])
        exe.connect_interfaces(app1, "Instance1", app2, "Instance2")

    def test_operations(self) -> None:
        """Test creating operations"""

        my_array = vafpy.datatypes.Array(
            name="MyArray",
            namespace="operations_types",
            datatype=vafpy.BaseTypes.DOUBLE,
            size=100,
        )

        my_interface = vafpy.ModuleInterface(name="MyInterface", namespace="interfaces1")
        my_interface.add_operation(
            name="func1",
            in_parameter={"in1": vafpy.BaseTypes.BOOL, "in2": my_array},
            out_parameter={"out1": vafpy.BaseTypes.BOOL, "out2": my_array},
            inout_parameter={"inout1": vafpy.BaseTypes.BOOL, "inout2": my_array},
        )
        my_interface.add_operation(name="func2", out_parameter={"out": vafpy.BaseTypes.BOOL})
        my_interface.add_operation(
            name="func3",
            out_parameter={"out": vafpy.BaseTypes.BOOL},
            inout_parameter={"inout": vafpy.BaseTypes.BOOL},
        )

    def test_tasks(self) -> None:
        """Test creating tasks and task chains"""

        app = vafpy.ApplicationModule(name="App", namespace="app")

        p_10ms = timedelta(milliseconds=10)
        step1 = vafpy.Task(name="Step1", period=p_10ms, preferred_offset=0)
        step2 = vafpy.Task(name="Step2", period=p_10ms, preferred_offset=0, run_after=[step1])
        step3 = vafpy.Task(name="Step3", period=p_10ms, preferred_offset=0, run_after=[step1])
        step4 = vafpy.Task(
            name="Step4",
            period=p_10ms,
            preferred_offset=0,
            run_after=[step1, step2, step3],
        )

        app.add_task_chain(tasks=[step1])
        app.add_task_chain(tasks=[step2], run_after=[step3])
        app.add_task_chain(tasks=[step4, step3], run_after=[step1], increment_preferred_offset=True)

    def test_vaf_string_base_datatype(self) -> None:
        """Add vaf::string in model is used"""
        # datatypes: vector/array/typeref
        vafpy.Vector("test", "MacVector", vafpy.BaseTypes.STRING)

        assert isinstance(
            self.model.element_by_namespace.get("vaf", {}).get("Strings", {}).get("String", None),
            vafpy.String,
        )
        assert self.model.main_model.DataTypeDefinitions.Strings[0].Namespace == "vaf"
        assert self.model.main_model.DataTypeDefinitions.Strings[0].Name == "String"

        self.model.reset()
        vafpy.Array("test", "MaXRay", vafpy.BaseTypes.STRING, 2)

        assert isinstance(
            self.model.element_by_namespace.get("vaf", {}).get("Strings", {}).get("String", None),
            vafpy.String,
        )
        assert self.model.main_model.DataTypeDefinitions.Strings[0].Namespace == "vaf"
        assert self.model.main_model.DataTypeDefinitions.Strings[0].Name == "String"

        self.model.reset()
        vafpy.TypeRef("test", "T-Rex", vafpy.BaseTypes.STRING)

        assert isinstance(
            self.model.element_by_namespace.get("vaf", {}).get("Strings", {}).get("String", None),
            vafpy.String,
        )
        vafpy.Array("test", "MaXRay", vafpy.BaseTypes.STRING, 2)
        assert len(self.model.element_by_namespace.get("vaf", {}).get("Strings", {}).keys()) == 1
        assert self.model.main_model.DataTypeDefinitions.Strings[0].Namespace == "vaf"
        assert self.model.main_model.DataTypeDefinitions.Strings[0].Name == "String"

        self.model.reset()
        vafpy.Vector("test", "MacVector", vafpy.BaseTypes.BOOL)
        assert self.model.element_by_namespace.get("vaf", {}).get("Strings", {}).get("String", None) is None
        assert len(self.model.main_model.DataTypeDefinitions.Strings) == 0

        # struct
        self.model.reset()
        struct = vafpy.Struct(name="MyStruct", namespace="demo")
        struct.add_subelement(name="MaStr", datatype=vafpy.BaseTypes.STRING)
        assert len(self.model.element_by_namespace.get("vaf", {}).get("Strings", {}).keys()) == 1
        assert self.model.main_model.DataTypeDefinitions.Strings[0].Namespace == "vaf"
        assert self.model.main_model.DataTypeDefinitions.Strings[0].Name == "String"

    def test_vaf_string_base_module_interface(self) -> None:
        """Add vaf::string in model is used"""

        # module interface
        self.model.reset()
        interface = vafpy.ModuleInterface("Milan", "Inter")
        assert self.model.element_by_namespace.get("vaf", {}).get("Strings", {}).get("String", None) is None
        assert len(self.model.main_model.DataTypeDefinitions.Strings) == 0

        # via add data elements
        interface.add_data_element("Stringulation", vafpy.BaseTypes.STRING)
        assert len(self.model.element_by_namespace.get("vaf", {}).get("Strings", {}).keys()) == 1
        assert self.model.main_model.DataTypeDefinitions.Strings[0].Namespace == "vaf"
        assert self.model.main_model.DataTypeDefinitions.Strings[0].Name == "String"

        self.model.reset()
        interface = vafpy.ModuleInterface("Milan", "Inter")

        # via add operations in
        interface.add_operation("inopt", in_parameter={"in_string": vafpy.BaseTypes.STRING})
        assert len(self.model.element_by_namespace.get("vaf", {}).get("Strings", {}).keys()) == 1
        assert self.model.main_model.DataTypeDefinitions.Strings[0].Namespace == "vaf"
        assert self.model.main_model.DataTypeDefinitions.Strings[0].Name == "String"

        self.model.reset()
        interface = vafpy.ModuleInterface("Milan", "Inter")

        # via add operations out
        interface.add_operation("outopt", out_parameter={"out_string": vafpy.BaseTypes.STRING})
        assert len(self.model.element_by_namespace.get("vaf", {}).get("Strings", {}).keys()) == 1
        assert self.model.main_model.DataTypeDefinitions.Strings[0].Namespace == "vaf"
        assert self.model.main_model.DataTypeDefinitions.Strings[0].Name == "String"

        self.model.reset()
        interface = vafpy.ModuleInterface("Milan", "Inter")

        # via add operations inout
        interface.add_operation("twoway", inout_parameter={"bidirect_string": vafpy.BaseTypes.STRING})
        assert len(self.model.element_by_namespace.get("vaf", {}).get("Strings", {}).keys()) == 1
        assert self.model.main_model.DataTypeDefinitions.Strings[0].Namespace == "vaf"
        assert self.model.main_model.DataTypeDefinitions.Strings[0].Name == "String"

        # full add
        self.model.reset()
        interface = vafpy.ModuleInterface("Milan", "Inter")
        interface.add_operation(
            "inopt",
            in_parameter={"in_string": vafpy.BaseTypes.STRING},
            out_parameter={"out_string": vafpy.BaseTypes.STRING},
            inout_parameter={"bidirect_string": vafpy.BaseTypes.STRING},
        )
        interface.add_data_element("Stringulation", vafpy.BaseTypes.STRING)
        assert len(self.model.element_by_namespace.get("vaf", {}).get("Strings", {}).keys()) == 1
        assert self.model.main_model.DataTypeDefinitions.Strings[0].Namespace == "vaf"
        assert self.model.main_model.DataTypeDefinitions.Strings[0].Name == "String"
