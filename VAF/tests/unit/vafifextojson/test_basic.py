"""
Basic test for IFEX to JSON converter
"""

# pylint: disable=missing-param-doc
# pylint: disable=too-few-public-methods
# pylint: disable=missing-type-doc
# pylint: disable=too-many-lines
# pylint: disable=too-many-public-methods
# mypy: disable-error-code="no-untyped-def"
import json
import os
from pathlib import Path

from vaf.vafifextojson import ifex_batch_to_json
from vaf.vafifextojson.ifex_helper import load_ifex_file, load_ifex_with_includes
from vaf.vafmodel import load_json


class TestBasic:
    """Basic test class for IFEX conversion"""

    def test_load_ifex_file(self) -> None:
        """Test loading an IFEX YAML file"""
        script_dir = Path(os.path.realpath(__file__)).parent
        test_file = script_dir / "test_data" / "test.yaml"

        # Test that the file can be loaded
        ast = load_ifex_file(test_file)

        # Basic assertions on the loaded AST
        assert ast is not None
        assert hasattr(ast, "namespaces")
        assert hasattr(ast, "name")

    def test_ifex_to_json_conversion(self, tmp_path) -> None:
        """Test that ifex_batch_to_json successfully converts and writes JSON"""
        script_dir = Path(os.path.realpath(__file__)).parent
        input_file = script_dir / "test_data" / "test.yaml"
        output_file = tmp_path / "model.json"

        # Convert IFEX to JSON using batch converter (works with single file too)
        ifex_batch_to_json([input_file], output_file)

        # Verify output file was created
        assert output_file.exists(), "Output JSON file was not created"

        # Verify the JSON is valid
        with output_file.open("r") as f:
            json_data = json.load(f)

        assert json_data is not None
        assert "DataTypeDefinitions" in json_data
        assert "ModuleInterfaces" in json_data

        # Load using VAF model loader
        model = load_json(str(output_file))
        assert model is not None

        # Verify data types were extracted
        assert model.DataTypeDefinitions is not None
        assert len(model.DataTypeDefinitions.Structs) == 2, "Expected 2 structs"
        assert len(model.DataTypeDefinitions.Enums) == 1, "Expected 1 enum"

        # Verify struct names
        struct_names = [s.Name for s in model.DataTypeDefinitions.Structs]
        assert "Position" in struct_names
        assert "SpeedInfo" in struct_names

        # Verify enum name
        enum_names = [e.Name for e in model.DataTypeDefinitions.Enums]
        assert "SpeedUnit" in enum_names

        # Verify module interfaces were extracted
        assert len(model.ModuleInterfaces) == 1, "Expected 1 module interface"
        module_interface = model.ModuleInterfaces[0]
        assert module_interface.Name == "VehicleControlService"  # Name comes from AST
        assert module_interface.Namespace == "VehicleControl"  # Namespace comes from namespace

        # Verify operations (methods)
        assert len(module_interface.Operations) == 2, "Expected 2 operations"
        operation_names = [op.Name for op in module_interface.Operations]
        assert "SetSpeed" in operation_names
        assert "GetPosition" in operation_names

        # Verify data elements (events)
        assert len(module_interface.DataElements) == 2, "Expected 2 data elements"
        data_element_names = [de.Name for de in module_interface.DataElements]
        assert "SpeedChanged" in data_element_names
        assert "PositionUpdated" in data_element_names

    def test_comprehensive_ifex_conversion(self, tmp_path) -> None:
        # pylint: disable=too-many-locals,too-many-statements
        """Test comprehensive IFEX file with arrays, maps, and properties"""
        script_dir = Path(os.path.realpath(__file__)).parent
        input_file = script_dir / "test_data" / "test2.yaml"
        output_file = tmp_path / "test2_model.json"

        # Convert IFEX to JSON using batch converter (works with single file too)
        ifex_batch_to_json([input_file], output_file)

        # Verify output file was created
        assert output_file.exists(), "Output JSON file was not created"

        # Load using VAF model loader
        model = load_json(str(output_file))
        assert model is not None

        # Verify data types were extracted
        assert model.DataTypeDefinitions is not None
        assert len(model.DataTypeDefinitions.Structs) == 3, "Expected 3 structs"
        assert len(model.DataTypeDefinitions.Enums) == 2, "Expected 2 enums"

        # Verify struct names
        struct_names = [s.Name for s in model.DataTypeDefinitions.Structs]
        assert "Coordinates" in struct_names
        assert "SpeedInfo" in struct_names
        assert "ComplexTelemetry" in struct_names

        # Verify enum names
        enum_names = [e.Name for e in model.DataTypeDefinitions.Enums]
        assert "SpeedUnit" in enum_names
        assert "StatusCode" in enum_names

        # Verify module interfaces were extracted
        assert len(model.ModuleInterfaces) == 1, "Expected 1 module interface"
        module_interface = model.ModuleInterfaces[0]
        assert module_interface.Name == "UltimateInterfaceService"  # Uses AST name
        assert module_interface.Namespace == "UltimateInterface"  # Namespace from YAML

        # Verify operations (methods + property getters/setters)
        # Should have 4 methods + 6 property operations (3 properties × 2 operations each) = 10 total
        assert len(module_interface.Operations) == 10, f"Expected 10 operations, got {len(module_interface.Operations)}"
        operation_names = [op.Name for op in module_interface.Operations]

        # Methods
        assert "SetSpeed" in operation_names
        assert "GetPosition" in operation_names
        assert "UploadTelemetry" in operation_names
        assert "GetMultipleReadings" in operation_names

        # Property getters
        assert "GetCurrentSpeed" in operation_names
        assert "GetCurrentPosition" in operation_names
        assert "GetTelemetryBuffer" in operation_names

        # Property setters
        assert "SetCurrentSpeed" in operation_names
        assert "SetCurrentPosition" in operation_names
        assert "SetTelemetryBuffer" in operation_names

        # Verify data elements (events + properties)
        # Should have 4 events + 3 properties = 7 total
        assert len(module_interface.DataElements) == 7, "Expected 7 data elements"
        data_element_names = [de.Name for de in module_interface.DataElements]

        # Events
        assert "SpeedChanged" in data_element_names
        assert "PositionUpdated" in data_element_names
        assert "TelemetryAlert" in data_element_names
        assert "EmergencyStop" in data_element_names

        # Properties
        assert "CurrentSpeed" in data_element_names
        assert "CurrentPosition" in data_element_names
        assert "TelemetryBuffer" in data_element_names

        # Verify array types are preserved (even if not fully converted)
        get_readings_op = next(op for op in module_interface.Operations if op.Name == "GetMultipleReadings")
        assert len(get_readings_op.Parameters) == 2
        # The array types should be properly converted to VAF Array types
        param_type_names = [p.TypeRef.Name for p in get_readings_op.Parameters]
        assert "StringArray" in param_type_names
        assert "FloatArray" in param_type_names

        # Verify that String and Array types were created
        assert model.DataTypeDefinitions.Strings is not None
        assert len(model.DataTypeDefinitions.Strings) == 1
        assert model.DataTypeDefinitions.Strings[0].Name == "String"
        assert model.DataTypeDefinitions.Strings[0].Namespace == "vaf"

        # Should have 4 vectors:
        # - FloatVector (typedef float[] -> Vector, namespace "UltimateInterface")
        # - CoordinatesArray (typedef Coordinates[] -> Vector, namespace "UltimateInterface")
        # - StringArray (inline string[] -> Vector, namespace "ifex_to_vaf")
        # - FloatArray (inline float[] -> Vector, namespace "ifex_to_vaf")
        assert model.DataTypeDefinitions.Vectors is not None
        assert len(model.DataTypeDefinitions.Vectors) == 4
        vector_names = [v.Name for v in model.DataTypeDefinitions.Vectors]
        assert "FloatVector" in vector_names
        assert "CoordinatesArray" in vector_names
        assert "StringArray" in vector_names
        assert "FloatArray" in vector_names

        # Verify typedef-created vectors have the correct namespace
        float_vector = next((v for v in model.DataTypeDefinitions.Vectors if v.Name == "FloatVector"), None)
        assert float_vector is not None
        assert float_vector.Namespace == "UltimateInterface"

        coords_array = next((v for v in model.DataTypeDefinitions.Vectors if v.Name == "CoordinatesArray"), None)
        assert coords_array is not None
        assert coords_array.Namespace == "UltimateInterface"

        # Inline vectors should have "ifex_to_vaf" namespace
        string_array = next((v for v in model.DataTypeDefinitions.Vectors if v.Name == "StringArray"), None)
        assert string_array is not None
        assert string_array.Namespace == "ifex_to_vaf"

        float_array = next((v for v in model.DataTypeDefinitions.Vectors if v.Name == "FloatArray"), None)
        assert float_array is not None
        assert float_array.Namespace == "ifex_to_vaf"

        # Verify TypeRefs (typedefs) were created
        # Only non-vector, non-map typedefs become TypeRefs (none in this case)
        assert model.DataTypeDefinitions.TypeRefs is not None
        assert len(model.DataTypeDefinitions.TypeRefs) == 0
        # Verify Maps (map typedefs) were created
        assert model.DataTypeDefinitions.Maps is not None
        assert len(model.DataTypeDefinitions.Maps) == 1
        map_names = [m.Name for m in model.DataTypeDefinitions.Maps]
        assert "SensorDataMap" in map_names
        # Verify the map structure and namespace
        sensor_map = model.DataTypeDefinitions.Maps[0]
        assert sensor_map.Namespace == "UltimateInterface"
        assert sensor_map.MapKeyTypeRef.Name == "String"
        assert sensor_map.MapKeyTypeRef.Namespace == "vaf"
        assert sensor_map.MapValueTypeRef.Name == "float"

    def test_ifex_layering(self, tmp_path) -> None:
        """Test IFEX layering with includes"""
        script_dir = Path(os.path.realpath(__file__)).parent
        input_file = script_dir / "test_data" / "vehicle_layered.yaml"
        output_file = tmp_path / "layered_model.json"

        # Convert with layering enabled using batch converter (works with single file too)
        ifex_batch_to_json([input_file], output_file, enable_layering=True)

        # Verify output file was created
        assert output_file.exists(), "Output JSON file was not created"

        # Load and validate the model
        model = load_json(str(output_file))

        # Should have structs from both base_types.yaml (2) and vehicle_layered.yaml (1)
        assert model.DataTypeDefinitions.Structs is not None
        assert len(model.DataTypeDefinitions.Structs) >= 3
        struct_names = [s.Name for s in model.DataTypeDefinitions.Structs]
        assert "Timestamp" in struct_names  # From base_types.yaml
        assert "Position" in struct_names  # From base_types.yaml
        assert "WheelData" in struct_names  # From vehicle_layered.yaml

        # Verify nested namespace support
        # Timestamp should be in Common.Types namespace (converted to Common::Types)
        timestamp_struct = next((s for s in model.DataTypeDefinitions.Structs if s.Name == "Timestamp"), None)
        assert timestamp_struct is not None
        assert timestamp_struct.Namespace == "Common::Types"

        # WheelData should be in Vehicle.Chassis namespace (converted to Vehicle::Chassis)
        wheel_data_struct = next((s for s in model.DataTypeDefinitions.Structs if s.Name == "WheelData"), None)
        assert wheel_data_struct is not None
        assert wheel_data_struct.Namespace == "Vehicle::Chassis"

        # Should have enum from base_types.yaml
        assert model.DataTypeDefinitions.Enums is not None
        assert len(model.DataTypeDefinitions.Enums) >= 1
        enum_names = [e.Name for e in model.DataTypeDefinitions.Enums]
        assert "Status" in enum_names

        # Verify Status enum has correct namespace
        status_enum = next((e for e in model.DataTypeDefinitions.Enums if e.Name == "Status"), None)
        assert status_enum is not None
        assert status_enum.Namespace == "Common::Types"

        # Should have module interface from vehicle_layered.yaml
        assert model.ModuleInterfaces is not None
        assert len(model.ModuleInterfaces) >= 1
        # Check operations in the interfaces
        operations = []
        for interface in model.ModuleInterfaces:
            if interface.Operations:
                operations.extend([op.Name for op in interface.Operations])
        assert "GetWheelData" in operations

    def test_load_ifex_with_includes(self) -> None:
        """Test loading IFEX with includes helper function"""
        script_dir = Path(os.path.realpath(__file__)).parent
        input_file = script_dir / "test_data" / "vehicle_layered.yaml"

        # Load with includes
        ast = load_ifex_with_includes(input_file)

        # Should have namespaces from both files
        assert ast.namespaces is not None
        assert len(ast.namespaces) >= 2
        namespace_names = [ns.name for ns in ast.namespaces]
        assert "Common.Types" in namespace_names
        assert "Vehicle.Chassis" in namespace_names

        # Includes should be cleared (merged)
        assert ast.includes is None

    def test_ifex_batch_import(self, tmp_path) -> None:
        """Test batch import of multiple IFEX files"""
        script_dir = Path(os.path.realpath(__file__)).parent
        # Import both test.yaml and test2.yaml as a batch
        input_files = [script_dir / "test_data" / "test.yaml", script_dir / "test_data" / "test2.yaml"]
        output_file = tmp_path / "batch_model.json"

        # Convert batch with layering enabled
        ifex_batch_to_json(input_files, output_file, enable_layering=True)

        # Verify output file was created
        assert output_file.exists(), "Output JSON file was not created"

        # Load and validate the model
        model = load_json(str(output_file))
        assert model is not None

        # Should have structs from both files
        # test.yaml has Position, SpeedInfo
        # test2.yaml has Coordinates, SpeedInfo, ComplexTelemetry
        # Total unique: Position, SpeedInfo, Coordinates, ComplexTelemetry (4 structs)
        assert model.DataTypeDefinitions.Structs is not None
        assert len(model.DataTypeDefinitions.Structs) >= 4
        struct_names = [s.Name for s in model.DataTypeDefinitions.Structs]
        assert "Position" in struct_names  # From test.yaml
        assert "SpeedInfo" in struct_names  # From both files
        assert "Coordinates" in struct_names  # From test2.yaml
        assert "ComplexTelemetry" in struct_names  # From test2.yaml

        # Should have enums from both files
        # test.yaml has SpeedUnit
        # test2.yaml has SpeedUnit, StatusCode
        # Total unique: SpeedUnit, StatusCode (2 enums)
        assert model.DataTypeDefinitions.Enums is not None
        assert len(model.DataTypeDefinitions.Enums) >= 2
        enum_names = [e.Name for e in model.DataTypeDefinitions.Enums]
        assert "SpeedUnit" in enum_names  # From both files
        assert "StatusCode" in enum_names  # From test2.yaml

        # Should have module interfaces from both files
        # test.yaml has VehicleControlService (AST name) with VehicleControl namespace
        # test2.yaml has UltimateInterfaceService (AST name) with UltimateInterface namespace
        assert model.ModuleInterfaces is not None
        assert len(model.ModuleInterfaces) >= 2
        interface_names = [i.Name for i in model.ModuleInterfaces]
        assert "VehicleControlService" in interface_names  # From test.yaml (AST name)
        assert "UltimateInterfaceService" in interface_names  # From test2.yaml (AST name)

        # Verify namespaces are set correctly
        vehicle_interface = next((i for i in model.ModuleInterfaces if i.Name == "VehicleControlService"), None)
        assert vehicle_interface is not None
        assert vehicle_interface.Namespace == "VehicleControl"

        ultimate_interface = next((i for i in model.ModuleInterfaces if i.Name == "UltimateInterfaceService"), None)
        assert ultimate_interface is not None
        assert ultimate_interface.Namespace == "UltimateInterface"

        # Verify operations from both interfaces are present
        operations = []
        for interface in model.ModuleInterfaces:
            if interface.Operations:
                operations.extend([op.Name for op in interface.Operations])

        # From test.yaml (VehicleControl)
        assert "SetSpeed" in operations
        assert "GetPosition" in operations

        # From test2.yaml (UltimateInterface)
        assert "UploadTelemetry" in operations
        assert "GetMultipleReadings" in operations

        # Verify data elements from both interfaces
        data_elements = []
        for interface in model.ModuleInterfaces:
            if interface.DataElements:
                data_elements.extend([de.Name for de in interface.DataElements])

        # From test.yaml (VehicleControl)
        assert "SpeedChanged" in data_elements
        assert "PositionUpdated" in data_elements

        # From test2.yaml (UltimateInterface)
        assert "TelemetryAlert" in data_elements
        assert "EmergencyStop" in data_elements

    def test_ifex_batch_type_conflict(self, tmp_path) -> None:
        """Test batch import detects conflicting type names (array vs map with same name)"""
        script_dir = Path(os.path.realpath(__file__)).parent
        # Import files with conflicting typedef names in same namespace
        input_files = [script_dir / "test_data" / "conflict_array.yaml", script_dir / "test_data" / "conflict_map.yaml"]
        output_file = tmp_path / "conflict_model.json"

        # Should raise ValueError due to type name conflict
        import pytest  # pylint: disable=import-outside-toplevel

        with pytest.raises(ValueError) as exc_info:
            ifex_batch_to_json(input_files, output_file, enable_layering=True)

        # Check that the error message mentions the conflict
        error_msg = str(exc_info.value)
        assert "Type name conflicts detected" in error_msg
        assert "DataCollection" in error_msg
        assert "Common::DataCollection" in error_msg
        assert "Vector" in error_msg
        assert "Map" in error_msg

    def test_ifex_batch_interface_conflict_between_files(self, tmp_path) -> None:
        """Test batch import detects interface conflicts between different top-level files"""
        script_dir = Path(os.path.realpath(__file__)).parent
        # Import two DIFFERENT top-level files with same interface but different methods
        # conflict_interface1.yaml: SensorService with GetTemperature, SetThreshold
        # conflict_interface2.yaml: SensorService with GetPressure, Calibrate
        input_files = [
            script_dir / "test_data" / "conflict_interface1.yaml",
            script_dir / "test_data" / "conflict_interface2.yaml",
        ]
        output_file = tmp_path / "interface_conflict_model.json"

        # Should raise ValueError - different top-level batch files with conflicting interfaces
        import pytest  # pylint: disable=import-outside-toplevel

        with pytest.raises(ValueError) as exc_info:
            ifex_batch_to_json(input_files, output_file, enable_layering=True)

        # Check that the error message mentions cross-file conflict
        error_msg = str(exc_info.value)
        assert "Conflicting ModuleInterface" in error_msg
        assert "across different batch files" in error_msg or "across top-level files" in error_msg
        assert "SensorService" in error_msg

    def test_ifex_batch_nested_namespace_references(self, tmp_path) -> None:  # pylint: disable= too-many-locals, too-many-statements
        """Test batch import correctly handles nested namespace references with dots converted to ::

        This test uses five layered files with a diamond dependency pattern:
        - nested_base.yaml: defines Common.Geometry.Point2D and Point3D (no includes)
        - nested_derived.yaml: includes nested_base, uses Common.Geometry types in arrays/maps
        - nested_top_level.yaml: includes nested_derived, creates navigation service
        - nested_second_top_level.yaml: includes nested_derived, creates fleet management service
        - nested_alternative.yaml: includes nested_base directly, creates mapping service

        This creates a diamond dependency with multiple include paths:
          Path 1: nested_top_level → nested_derived → nested_base
          Path 2: nested_second_top_level → nested_derived → nested_base
          Path 3: nested_alternative → nested_base

        Both nested_derived.yaml and nested_base.yaml are included multiple times through different paths.

        Tests the fix for:
        1. Dot notation conversion (Common.Geometry.Point2D -> Common::Geometry::Point2D)
        2. Deduplication of types from multiply-included files (nested_base loaded 3 times, nested_derived loaded 2 times) # pylint: disable= line-too-long
        """
        script_dir = Path(os.path.realpath(__file__)).parent
        # Import three top-level files that create a diamond dependency
        # This tests that types are properly deduplicated even with complex include chains
        input_files = [
            script_dir / "test_data" / "nested_top_level.yaml",
            script_dir / "test_data" / "nested_second_top_level.yaml",
            script_dir / "test_data" / "nested_alternative.yaml",
        ]
        output_file = tmp_path / "nested_model.json"

        # Should successfully import and convert dots to ::
        ifex_batch_to_json(input_files, output_file, enable_layering=True)

        # Verify the output file was created
        assert output_file.exists()

        # Load and verify the model
        with open(output_file, encoding="utf-8") as f:
            model = json.load(f)

        # Check that nested namespace types are correctly referenced with ::
        structs = model["DataTypeDefinitions"]["Structs"]

        # Verify base types exist (should be deduplicated, not duplicated)
        point2d = next((s for s in structs if s["Name"] == "Point2D"), None)
        assert point2d is not None
        assert point2d["Namespace"] == "Common::Geometry"

        point3d = next((s for s in structs if s["Name"] == "Point3D"), None)
        assert point3d is not None
        assert point3d["Namespace"] == "Common::Geometry"

        # Verify Location struct from nested_derived.yaml
        location_struct = next((s for s in structs if s["Name"] == "Location"), None)
        assert location_struct is not None
        assert location_struct["Namespace"] == "Vehicle::Position"

        # Check that the struct member uses :: notation
        current_pos = next((m for m in location_struct["SubElements"] if m["Name"] == "currentPosition"), None)
        assert current_pos is not None
        # TypeRef is just a string in the JSON, not a dict
        assert current_pos["TypeRef"] == "Common::Geometry::Point3D"

        # Verify Route struct from nested_top_level.yaml
        route_struct = next((s for s in structs if s["Name"] == "Route"), None)
        assert route_struct is not None
        assert route_struct["Namespace"] == "Navigation::Service"

        # Check that Route references Location correctly
        start_loc = next((m for m in route_struct["SubElements"] if m["Name"] == "startLocation"), None)
        assert start_loc is not None
        assert start_loc["TypeRef"] == "Vehicle::Position::Location"

        # Verify MapRegion struct from nested_alternative.yaml
        map_region = next((s for s in structs if s["Name"] == "MapRegion"), None)
        assert map_region is not None
        assert map_region["Namespace"] == "Mapping::Service"

        # Check that MapRegion uses Point2D correctly with :: notation
        top_left = next((m for m in map_region["SubElements"] if m["Name"] == "topLeft"), None)
        assert top_left is not None
        assert top_left["TypeRef"] == "Common::Geometry::Point2D"

        # Verify Vehicle struct from nested_second_top_level.yaml
        vehicle_struct = next((s for s in structs if s["Name"] == "Vehicle"), None)
        assert vehicle_struct is not None
        assert vehicle_struct["Namespace"] == "Fleet::Management"

        # Check that Vehicle also uses Location correctly (nested_derived included again)
        current_loc = next((m for m in vehicle_struct["SubElements"] if m["Name"] == "currentLocation"), None)
        assert current_loc is not None
        assert current_loc["TypeRef"] == "Vehicle::Position::Location"

        # Verify Fleet struct which uses both Vehicle array and Point3D
        fleet_struct = next((s for s in structs if s["Name"] == "Fleet"), None)
        assert fleet_struct is not None
        assert fleet_struct["Namespace"] == "Fleet::Management"

        base_loc = next((m for m in fleet_struct["SubElements"] if m["Name"] == "baseLocation"), None)
        assert base_loc is not None
        assert base_loc["TypeRef"] == "Common::Geometry::Point3D"

        # Check that arrays of nested types are correctly created with :: notation
        vectors = model["DataTypeDefinitions"]["Vectors"]
        point2d_array = next((v for v in vectors if "Commongeometrypoint2D" in v["Name"]), None)
        assert point2d_array is not None
        assert point2d_array["TypeRef"] == "Common::Geometry::Point2D"

        # Check that maps with nested types are correctly created with :: notation
        maps = model["DataTypeDefinitions"]["Maps"]
        assert len(maps) > 0
        waypoints_map = next((m for m in maps if "Commongeometrypoint3D" in m["Name"]), None)
        assert waypoints_map is not None
        assert waypoints_map["MapValueTypeRef"] == "Common::Geometry::Point3D"

        # Verify deduplication worked - count how many times each base type appears
        # Even though nested_base.yaml was included through three different paths, types should appear only once
        point2d_count = sum(1 for s in structs if s["Name"] == "Point2D" and s["Namespace"] == "Common::Geometry")
        point3d_count = sum(1 for s in structs if s["Name"] == "Point3D" and s["Namespace"] == "Common::Geometry")
        assert point2d_count == 1, (
            f"Point2D should be deduplicated to appear exactly once, but appears {point2d_count} times"
        )
        assert point3d_count == 1, (
            f"Point3D should be deduplicated to appear exactly once, but appears {point3d_count} times"
        )

        # Verify that nested_derived.yaml types (Location) are also deduplicated
        # nested_derived is included by both nested_top_level and nested_second_top_level
        location_count = sum(1 for s in structs if s["Name"] == "Location" and s["Namespace"] == "Vehicle::Position")
        assert location_count == 1, (
            f"Location should be deduplicated to appear exactly once, but appears {location_count} times"
        )
        assert point3d_count == 1, (
            f"Point3D should be deduplicated to appear exactly once, but appears {point3d_count} times"
        )

    def test_ifex_batch_struct_enum_conflict(self, tmp_path) -> None:
        """Test batch import detects conflict when same name is defined as both Struct and Enum"""
        script_dir = Path(os.path.realpath(__file__)).parent
        # Import files with same type name but different categories (Struct vs Enum)
        input_files = [
            script_dir / "test_data" / "conflict_struct_enum_struct.yaml",
            script_dir / "test_data" / "conflict_struct_enum_enum.yaml",
        ]
        output_file = tmp_path / "struct_enum_conflict.json"

        # Should raise ValueError due to type category conflict
        import pytest  # pylint: disable=import-outside-toplevel

        with pytest.raises(ValueError) as exc_info:
            ifex_batch_to_json(input_files, output_file, enable_layering=True)

        # Check that the error message mentions the conflict between categories
        error_msg = str(exc_info.value)
        assert "Type name conflicts detected" in error_msg
        assert "DataPoint" in error_msg
        assert "Sensors::DataPoint" in error_msg
        assert "Struct" in error_msg
        assert "Enum" in error_msg

    def test_ifex_batch_same_name_different_namespace(self, tmp_path) -> None:
        """Test batch import allows same local name in different namespaces (not a conflict)"""
        script_dir = Path(os.path.realpath(__file__)).parent
        # Import files with same local name "Status" but different namespaces
        input_files = [
            script_dir / "test_data" / "same_name_diff_ns1.yaml",
            script_dir / "test_data" / "same_name_diff_ns2.yaml",
        ]
        output_file = tmp_path / "same_name_diff_ns.json"

        # Should successfully import - different namespaces means different types
        ifex_batch_to_json(input_files, output_file, enable_layering=True)

        # Verify the output file was created
        assert output_file.exists()

        # Load and verify both Status enums exist with different namespaces
        with open(output_file, encoding="utf-8") as f:
            model = json.load(f)

        enums = model["DataTypeDefinitions"]["Enums"]
        status_enums = [e for e in enums if e["Name"] == "Status"]
        assert len(status_enums) == 2, "Should have two Status enums in different namespaces"

        namespaces = {e["Namespace"] for e in status_enums}
        assert "App::Core" in namespaces
        assert "Network::Protocol" in namespaces

    def test_ifex_batch_identical_interfaces_deduplicated(self, tmp_path) -> None:
        """Test batch import accepts and deduplicates identical interface definitions

        When two files define interfaces with identical content (same name, namespace,
        methods, and parameters), they should be deduplicated successfully. This is the
        smart deduplication behavior that distinguishes:
        - Exact duplicates (same content) → deduplicate
        - True conflicts (different content) → reject
        """
        script_dir = Path(os.path.realpath(__file__)).parent
        # Import two files with identical interface definitions
        input_files = [
            script_dir / "test_data" / "identical_interface1.yaml",
            script_dir / "test_data" / "identical_interface2.yaml",
        ]
        output_file = tmp_path / "identical_interfaces.json"

        # Should successfully import and deduplicate
        ifex_batch_to_json(input_files, output_file, enable_layering=True)

        # Verify the output file was created
        assert output_file.exists()

        # Load and verify only one SharedService interface exists
        with open(output_file, encoding="utf-8") as f:
            model = json.load(f)

        interfaces = model["ModuleInterfaces"]
        shared_service = [i for i in interfaces if i["Name"] == "SharedService"]
        assert len(shared_service) == 1, "SharedService should be deduplicated to appear exactly once"

        # Verify the interface has expected content
        service = shared_service[0]
        assert service["Namespace"] == "Shared"

        # Verify operations exist (GetData and SetData)
        operations = service["Operations"]
        assert len(operations) == 2
        op_names = {op["Name"] for op in operations}
        assert "GetData" in op_names
        assert "SetData" in op_names

        # Verify Data struct exists and is deduplicated
        structs = model["DataTypeDefinitions"]["Structs"]
        data_structs = [s for s in structs if s["Name"] == "Data" and s["Namespace"] == "Shared"]
        assert len(data_structs) == 1, "Data struct should be deduplicated to appear exactly once"

    def test_ifex_batch_struct_content_conflict(self, tmp_path) -> None:
        """Test batch import detects structs with same name but different member definitions"""
        script_dir = Path(os.path.realpath(__file__)).parent

        # Create two files with Config struct having different members
        config1 = script_dir / "test_data" / "struct_conflict1.yaml"
        config2 = script_dir / "test_data" / "struct_conflict2.yaml"

        config1.write_text("""name: ConfigService1
major_version: 1
minor_version: 0

namespaces:
  - name: Settings
    structs:
      - name: Config
        members:
          - name: timeout
            datatype: uint32
          - name: retries
            datatype: uint8
""")

        config2.write_text("""name: ConfigService2
major_version: 1
minor_version: 0

namespaces:
  - name: Settings
    structs:
      - name: Config
        members:
          - name: timeout
            datatype: uint32
          - name: enabled
            datatype: boolean
""")

        output_file = tmp_path / "struct_conflict.json"

        # Should raise ValueError due to conflicting struct definitions
        import pytest  # pylint: disable=import-outside-toplevel

        with pytest.raises(ValueError) as exc_info:
            ifex_batch_to_json([config1, config2], output_file, enable_layering=True)

        error_msg = str(exc_info.value)
        assert "Conflicting Struct" in error_msg
        assert "Config" in error_msg
        assert "Settings::Config" in error_msg
        assert "defined differently in batch files" in error_msg

    def test_ifex_batch_enum_content_conflict(self, tmp_path) -> None:
        """Test batch import detects enums with same name but different literal definitions"""
        script_dir = Path(os.path.realpath(__file__)).parent

        # Create two files with Status enum having different literals
        enum1 = script_dir / "test_data" / "enum_conflict1.yaml"
        enum2 = script_dir / "test_data" / "enum_conflict2.yaml"

        enum1.write_text("""name: StatusService1
major_version: 1
minor_version: 0

namespaces:
  - name: System
    enumerations:
      - name: Status
        datatype: uint8
        options:
          - name: Idle
            value: 0
          - name: Active
            value: 1
""")

        enum2.write_text("""name: StatusService2
major_version: 1
minor_version: 0

namespaces:
  - name: System
    enumerations:
      - name: Status
        datatype: uint8
        options:
          - name: Idle
            value: 0
          - name: Running
            value: 1
""")

        output_file = tmp_path / "enum_conflict.json"

        # Should raise ValueError due to conflicting enum definitions
        import pytest  # pylint: disable=import-outside-toplevel

        with pytest.raises(ValueError) as exc_info:
            ifex_batch_to_json([enum1, enum2], output_file, enable_layering=True)

        error_msg = str(exc_info.value)
        assert "Conflicting Enum" in error_msg
        assert "Status" in error_msg
        assert "System::Status" in error_msg
        assert "defined differently in batch files" in error_msg

    def test_ifex_batch_identical_structs_deduplicated(self, tmp_path) -> None:
        """Test batch import accepts and deduplicates identical struct definitions"""
        script_dir = Path(os.path.realpath(__file__)).parent

        # Create two files with identical Point struct
        point1 = script_dir / "test_data" / "identical_struct1.yaml"
        point2 = script_dir / "test_data" / "identical_struct2.yaml"

        identical_struct_yaml = """name: PointService
major_version: 1
minor_version: 0

namespaces:
  - name: Geometry
    structs:
      - name: Point
        description: "2D point"
        members:
          - name: x
            datatype: float
          - name: y
            datatype: float
"""

        point1.write_text(identical_struct_yaml)
        point2.write_text(identical_struct_yaml)

        output_file = tmp_path / "identical_structs.json"

        # Should successfully import and deduplicate
        ifex_batch_to_json([point1, point2], output_file, enable_layering=True)

        assert output_file.exists()

        # Load and verify only one Point struct exists
        with open(output_file, encoding="utf-8") as f:
            model = json.load(f)

        structs = model["DataTypeDefinitions"]["Structs"]
        point_structs = [s for s in structs if s["Name"] == "Point" and s["Namespace"] == "Geometry"]
        assert len(point_structs) == 1, "Point should be deduplicated to appear exactly once"

    def test_ifex_batch_interface_override_within_file(self, tmp_path) -> None:
        """Test interface override within a single file's include hierarchy"""
        script_dir = Path(os.path.realpath(__file__)).parent

        # Create base interface file
        base_iface = script_dir / "test_data" / "base_service_interface.yaml"
        base_iface.write_text("""name: BaseServiceInterface
major_version: 1
minor_version: 0

namespaces:
  - name: Services
    methods:
      - name: Start
        input: []
        output:
          - name: success
            datatype: boolean
""")

        # Create extended interface file that includes base
        extended_iface = script_dir / "test_data" / "extended_service_interface.yaml"
        extended_iface.write_text("""name: ExtendedServiceInterface
major_version: 1
minor_version: 0

includes:
  - file: base_service_interface.yaml

namespaces:
  - name: Services
    methods:
      - name: Start
        input: []
        output:
          - name: success
            datatype: boolean
      - name: Stop
        input: []
        output:
          - name: success
            datatype: boolean
      - name: GetStatus
        input: []
        output:
          - name: status
            datatype: string
""")

        output_file = tmp_path / "extended_interface.json"

        # Import only the top-level file (it includes base via includes)
        ifex_batch_to_json([extended_iface], output_file, enable_layering=True)

        assert output_file.exists()

        # Load and verify extended interface is kept (within-file override)
        with open(output_file, encoding="utf-8") as f:
            model = json.load(f)

        interfaces = model["ModuleInterfaces"]
        # Should have both BaseServiceInterface and ExtendedServiceInterface
        # since they have different names (not an override case)
        assert len(interfaces) >= 1

    def test_ifex_batch_interface_identical_across_files(self, tmp_path) -> None:
        """Test identical interfaces from different batch files are deduplicated"""
        script_dir = Path(os.path.realpath(__file__)).parent

        # Create two DIFFERENT top-level files with IDENTICAL interface
        file1 = script_dir / "test_data" / "identical_batch1.yaml"
        file2 = script_dir / "test_data" / "identical_batch2.yaml"

        identical_yaml = """name: IdenticalBatchService
major_version: 1
minor_version: 0

namespaces:
  - name: Common
    methods:
      - name: Execute
        input:
          - name: command
            datatype: string
        output:
          - name: result
            datatype: boolean
"""

        file1.write_text(identical_yaml)
        file2.write_text(identical_yaml)

        output_file = tmp_path / "identical_batch.json"

        # Should successfully import - identical interfaces across files are OK
        ifex_batch_to_json([file1, file2], output_file, enable_layering=True)

        assert output_file.exists()

        # Load and verify only one interface exists (deduplicated)
        with open(output_file, encoding="utf-8") as f:
            model = json.load(f)

        interfaces = model["ModuleInterfaces"]
        common_services = [i for i in interfaces if i["Namespace"] == "Common"]
        assert len(common_services) == 1, "Identical interfaces across files should be deduplicated"

    def test_ifex_batch_interface_extension(self, tmp_path) -> None:
        """Test that different interfaces in different batch files works (no conflict if names differ)"""
        script_dir = Path(os.path.realpath(__file__)).parent

        # Create base interface with minimal methods
        base_iface = script_dir / "test_data" / "base_interface.yaml"
        base_iface.write_text("""name: BaseService
major_version: 1
minor_version: 0

namespaces:
  - name: Services
    methods:
      - name: Start
        input: []
        output:
          - name: success
            datatype: boolean
""")

        # Create a DIFFERENT interface (different name, so no conflict)
        extended_iface = script_dir / "test_data" / "other_interface.yaml"
        extended_iface.write_text("""name: ExtendedService
major_version: 1
minor_version: 0

namespaces:
  - name: Services
    methods:
      - name: StartExtended
        input: []
        output:
          - name: success
            datatype: boolean
      - name: Stop
        input: []
        output:
          - name: success
            datatype: boolean
""")

        output_file = tmp_path / "multi_interfaces.json"

        # Import both as separate batch files - should work (different interface names)
        ifex_batch_to_json([base_iface, extended_iface], output_file, enable_layering=True)

        assert output_file.exists()

        # Load and verify both interfaces exist
        with open(output_file, encoding="utf-8") as f:
            model = json.load(f)

        interfaces = model["ModuleInterfaces"]
        assert len(interfaces) >= 2, "Should have multiple interfaces from different batch files"

    def test_ifex_batch_interface_chain_override(self, tmp_path) -> None:
        """Test multiple interface overrides within same file's include chain"""
        script_dir = Path(os.path.realpath(__file__)).parent

        # This test should use includes to create a chain within ONE top-level file
        # For now, convert to test cross-file identical interfaces

        version1 = script_dir / "test_data" / "versioned_interface_v1.yaml"
        version1.write_text("""name: VersionedService
major_version: 1
minor_version: 0

namespaces:
  - name: API
    methods:
      - name: Process
        input:
          - name: data
            datatype: string
        output:
          - name: result
            datatype: string
""")

        version2 = script_dir / "test_data" / "versioned_interface_v2_conflict.yaml"
        version2.write_text("""name: VersionedService
major_version: 2
minor_version: 0

namespaces:
  - name: API
    methods:
      - name: Process
        input:
          - name: data
            datatype: string
          - name: options
            datatype: string
        output:
          - name: result
            datatype: string
""")

        output_file = tmp_path / "versioned_interface.json"

        # Import as different batch files - should CONFLICT (different definitions)
        import pytest  # pylint: disable=import-outside-toplevel

        with pytest.raises(ValueError) as exc_info:
            ifex_batch_to_json([version1, version2], output_file, enable_layering=True)

        error_msg = str(exc_info.value)
        assert "Conflicting ModuleInterface" in error_msg
        assert "across" in error_msg  # across batch files or top-level files

    def test_ifex_batch_import_error_handling(self, tmp_path) -> None:
        """Test batch import properly handles and reports errors"""
        script_dir = Path(os.path.realpath(__file__)).parent
        # Try to import a file with invalid syntax
        input_files = [script_dir / "test_data" / "invalid_syntax.yaml"]
        output_file = tmp_path / "error_model.json"

        # Should raise an exception (could be dacite error or other parsing error)
        import pytest  # pylint: disable=import-outside-toplevel

        with pytest.raises(Exception) as exc_info:
            ifex_batch_to_json(input_files, output_file, enable_layering=True)

        # Verify some error was raised (don't check specific message as it varies)
        assert exc_info.value is not None

        # Verify output file was not created
        assert not output_file.exists()

    def test_ifex_empty_file(self, tmp_path) -> None:
        """Test handling of empty or minimal IFEX file"""
        script_dir = Path(os.path.realpath(__file__)).parent

        # Create an empty IFEX file with just a name
        empty_file = script_dir / "test_data" / "empty_ifex.yaml"
        empty_file.write_text("""name: EmptyService
major_version: 1
minor_version: 0
""")

        output_file = tmp_path / "empty_model.json"

        # Should successfully import but produce an empty model
        ifex_batch_to_json([empty_file], output_file, enable_layering=True)

        assert output_file.exists()

        # Load using VAF model loader
        model = load_json(str(output_file))

        # Should have empty or None data type definitions and no interfaces
        if model.DataTypeDefinitions is not None:
            assert len(model.DataTypeDefinitions.Structs) == 0
            assert len(model.DataTypeDefinitions.Enums) == 0
        assert len(model.ModuleInterfaces) == 0

    def test_ifex_no_namespaces(self, tmp_path) -> None:
        """Test IFEX file without namespaces section"""
        script_dir = Path(os.path.realpath(__file__)).parent

        no_ns_file = script_dir / "test_data" / "no_namespaces.yaml"
        no_ns_file.write_text("""name: NoNamespaceService
major_version: 1
minor_version: 0
description: "Service with no namespaces"
""")

        output_file = tmp_path / "no_ns_model.json"

        # Should succeed with empty collections
        ifex_batch_to_json([no_ns_file], output_file, enable_layering=True)

        assert output_file.exists()

        model = load_json(str(output_file))
        assert len(model.ModuleInterfaces) == 0
        assert len(model.DataTypeDefinitions.Structs) == 0

    def test_ifex_deeply_nested_namespaces(self, tmp_path) -> None:
        """Test deeply nested namespace hierarchies (3+ levels)"""
        script_dir = Path(os.path.realpath(__file__)).parent

        nested_file = script_dir / "test_data" / "deeply_nested.yaml"
        nested_file.write_text("""name: DeeplyNestedService
major_version: 1
minor_version: 0

namespaces:
  - name: Level1
    namespaces:
      - name: Level2
        namespaces:
          - name: Level3
            structs:
              - name: DeepStruct
                members:
                  - name: value
                    datatype: int32
            methods:
              - name: DeepMethod
                input: []
                output:
                  - name: result
                    datatype: DeepStruct
""")

        output_file = tmp_path / "deeply_nested_model.json"

        ifex_batch_to_json([nested_file], output_file, enable_layering=True)

        assert output_file.exists()

        model = load_json(str(output_file))

        # Verify deeply nested struct has correct FQN
        assert len(model.DataTypeDefinitions.Structs) == 1
        deep_struct = model.DataTypeDefinitions.Structs[0]
        assert deep_struct.Name == "DeepStruct"
        assert deep_struct.Namespace == "Level1::Level2::Level3"

        # Verify interface has correct namespace (parent of the methods/level)
        assert len(model.ModuleInterfaces) == 1
        interface = model.ModuleInterfaces[0]
        # Interface namespace is the parent namespace where methods are defined
        assert "Level1::Level2" in interface.Namespace

    def test_ifex_method_with_error_attribute(self, tmp_path) -> None:
        """Test that methods with error attributes are converted correctly"""
        script_dir = Path(os.path.realpath(__file__)).parent

        error_method_file = script_dir / "test_data" / "method_with_errors.yaml"
        error_method_file.write_text("""name: ErrorHandlingService
major_version: 1
minor_version: 0

namespaces:
  - name: Services
    structs:
      - name: ErrorInfo
        members:
          - name: code
            datatype: uint32
          - name: message
            datatype: string
    methods:
      - name: RiskyOperation
        input:
          - name: data
            datatype: string
        output:
          - name: result
            datatype: boolean
        error:
          - name: error
            datatype: ErrorInfo
""")

        output_file = tmp_path / "error_method_model.json"

        ifex_batch_to_json([error_method_file], output_file, enable_layering=True)

        assert output_file.exists()

        model = load_json(str(output_file))

        # Verify struct is created
        assert len(model.DataTypeDefinitions.Structs) == 1
        error_struct = model.DataTypeDefinitions.Structs[0]
        assert error_struct.Name == "ErrorInfo"

        # Verify method is converted with error parameter
        assert len(model.ModuleInterfaces) == 1
        interface = model.ModuleInterfaces[0]
        assert len(interface.Operations) == 1

        operation = interface.Operations[0]
        assert operation.Name == "RiskyOperation"

        # Check that error parameter is included (as OUT parameter)
        out_params = [p for p in operation.Parameters if p.Direction == "OUT"]
        param_names = [p.Name for p in out_params]

        # Error parameter should be present
        assert "error" in param_names or "result" in param_names

    def test_ifex_property_generates_getters_setters(self, tmp_path) -> None:
        """Test that IFEX properties generate both Get and Set operations"""
        script_dir = Path(os.path.realpath(__file__)).parent

        property_file = script_dir / "test_data" / "service_with_properties.yaml"
        property_file.write_text("""name: PropertyService
major_version: 1
minor_version: 0

namespaces:
  - name: Config
    properties:
      - name: MaxSpeed
        datatype: uint32
      - name: EnableLogging
        datatype: boolean
""")

        output_file = tmp_path / "property_model.json"

        ifex_batch_to_json([property_file], output_file, enable_layering=True)

        assert output_file.exists()

        model = load_json(str(output_file))

        # Verify property generates operations (Get and Set)
        assert len(model.ModuleInterfaces) == 1
        interface = model.ModuleInterfaces[0]

        # Should have getter and setter for each property (4 operations total)
        assert len(interface.Operations) == 4

        operation_names = [op.Name for op in interface.Operations]
        assert "GetMaxSpeed" in operation_names
        assert "SetMaxSpeed" in operation_names
        assert "GetEnableLogging" in operation_names
        assert "SetEnableLogging" in operation_names

        # Verify DataElement is also created for each property
        assert len(interface.DataElements) == 2
        data_element_names = [de.Name for de in interface.DataElements]
        assert "MaxSpeed" in data_element_names
        assert "EnableLogging" in data_element_names

    def test_ifex_batch_import_with_layering_disabled(self, tmp_path) -> None:
        """Test batch import with enable_layering=False (includes not processed)"""
        script_dir = Path(os.path.realpath(__file__)).parent

        # Create base file with struct
        base_file = script_dir / "test_data" / "base_no_layering.yaml"
        base_file.write_text("""name: BaseService
major_version: 1
minor_version: 0

namespaces:
  - name: Base
    structs:
      - name: BaseStruct
        members:
          - name: id
            datatype: uint32
""")

        # Create file that includes base
        including_file = script_dir / "test_data" / "including_no_layering.yaml"
        including_file.write_text("""name: IncludingService
major_version: 1
minor_version: 0

includes:
  - file: base_no_layering.yaml

namespaces:
  - name: Extended
    structs:
      - name: ExtendedStruct
        members:
          - name: value
            datatype: uint32
""")

        output_file = tmp_path / "no_layering_model.json"

        # Import with layering DISABLED - should only get ExtendedStruct, not BaseStruct
        ifex_batch_to_json([including_file], output_file, enable_layering=False)

        assert output_file.exists()

        model = load_json(str(output_file))

        # Should only have ExtendedStruct (BaseStruct not loaded due to disabled layering)
        assert len(model.DataTypeDefinitions.Structs) == 1
        assert model.DataTypeDefinitions.Structs[0].Name == "ExtendedStruct"

    def test_ifex_typedef_edge_cases(self, tmp_path) -> None:
        """Test various typedef edge cases and formats"""
        script_dir = Path(os.path.realpath(__file__)).parent

        typedef_file = script_dir / "test_data" / "typedef_edge_cases.yaml"
        typedef_file.write_text("""name: TypedefTestService
major_version: 1
minor_version: 0

namespaces:
  - name: Types
    typedefs:
      # Simple typedef (alias)
      - name: Counter
        datatype: uint32
      # Array typedef
      - name: CounterArray
        datatype: uint32[]
      # Map typedef
      - name: CounterMap
        datatype: map<string, uint32>
      # Nested array of strings
      - name: StringMatrix
        datatype: string[]
""")

        output_file = tmp_path / "typedef_edge_model.json"

        ifex_batch_to_json([typedef_file], output_file, enable_layering=True)

        assert output_file.exists()

        model = load_json(str(output_file))

        # TypeRef for simple typedef
        assert len(model.DataTypeDefinitions.TypeRefs) >= 1
        typedef_names = [t.Name for t in model.DataTypeDefinitions.TypeRefs]
        assert "Counter" in typedef_names

        # Vectors for array typedefs
        assert len(model.DataTypeDefinitions.Vectors) >= 2
        vector_names = [v.Name for v in model.DataTypeDefinitions.Vectors]
        assert "CounterArray" in vector_names
        assert "StringMatrix" in vector_names

        # Map for map typedef
        assert len(model.DataTypeDefinitions.Maps) >= 1
        map_names = [m.Name for m in model.DataTypeDefinitions.Maps]
        assert "CounterMap" in map_names

    def test_ifex_struct_with_complex_members(self, tmp_path) -> None:
        """Test struct with array and map members"""
        script_dir = Path(os.path.realpath(__file__)).parent

        complex_struct_file = script_dir / "test_data" / "complex_struct_members.yaml"
        complex_struct_file.write_text("""name: ComplexStructService
major_version: 1
minor_version: 0

namespaces:
  - name: Data
    structs:
      - name: ComplexData
        members:
          - name: values
            datatype: float[]
          - name: metadata
            datatype: map<string, string>
          - name: flags
            datatype: boolean[]
""")

        output_file = tmp_path / "complex_struct_model.json"

        ifex_batch_to_json([complex_struct_file], output_file, enable_layering=True)

        assert output_file.exists()

        model = load_json(str(output_file))

        # Verify struct is created
        assert len(model.DataTypeDefinitions.Structs) == 1
        complex_data = model.DataTypeDefinitions.Structs[0]
        assert complex_data.Name == "ComplexData"
        assert len(complex_data.SubElements) == 3

        # Verify that array and map types are created
        assert len(model.DataTypeDefinitions.Vectors) >= 2  # FloatArray, BooleanArray
        assert len(model.DataTypeDefinitions.Maps) >= 1  # StringStringMap

    def test_ifex_event_with_multiple_parameters(self, tmp_path) -> None:
        """Test event with multiple parameters"""
        script_dir = Path(os.path.realpath(__file__)).parent

        multi_param_event_file = script_dir / "test_data" / "event_multi_params.yaml"
        multi_param_event_file.write_text("""name: MultiParamEventService
major_version: 1
minor_version: 0

namespaces:
  - name: Events
    events:
      - name: StatusChanged
        input:
          - name: oldStatus
            datatype: uint32
          - name: newStatus
            datatype: uint32
          - name: timestamp
            datatype: uint64
""")

        output_file = tmp_path / "multi_param_event_model.json"

        ifex_batch_to_json([multi_param_event_file], output_file, enable_layering=True)

        assert output_file.exists()

        model = load_json(str(output_file))

        # Verify event is converted to DataElement
        assert len(model.ModuleInterfaces) == 1
        interface = model.ModuleInterfaces[0]
        assert len(interface.DataElements) == 1

        data_element = interface.DataElements[0]
        assert data_element.Name == "StatusChanged"

    def test_ifex_mixed_content_namespace(self, tmp_path) -> None:
        """Test namespace with mixed content: structs, enums, methods, events, properties"""
        script_dir = Path(os.path.realpath(__file__)).parent

        mixed_file = script_dir / "test_data" / "mixed_namespace_content.yaml"
        mixed_file.write_text("""name: MixedContentService
major_version: 1
minor_version: 0

namespaces:
  - name: Mixed
    structs:
      - name: MixedStruct
        members:
          - name: id
            datatype: uint32
    enumerations:
      - name: MixedEnum
        datatype: uint32
        options:
          - name: OPTION_A
            value: 1
          - name: OPTION_B
            value: 2
    methods:
      - name: MixedMethod
        input: []
        output:
          - name: result
            datatype: boolean
    events:
      - name: MixedEvent
        input:
          - name: data
            datatype: uint32
    properties:
      - name: MixedProperty
        datatype: string
""")

        output_file = tmp_path / "mixed_content_model.json"

        ifex_batch_to_json([mixed_file], output_file, enable_layering=True)

        assert output_file.exists()

        model = load_json(str(output_file))

        # Verify all types are extracted
        assert len(model.DataTypeDefinitions.Structs) == 1
        assert model.DataTypeDefinitions.Structs[0].Name == "MixedStruct"

        assert len(model.DataTypeDefinitions.Enums) == 1
        assert model.DataTypeDefinitions.Enums[0].Name == "MixedEnum"

        # Verify interface is created with all operations and data elements
        assert len(model.ModuleInterfaces) == 1
        interface = model.ModuleInterfaces[0]

        # Method + Property Get + Property Set = 3 operations
        assert len(interface.Operations) == 3
        operation_names = [op.Name for op in interface.Operations]
        assert "MixedMethod" in operation_names
        assert "GetMixedProperty" in operation_names
        assert "SetMixedProperty" in operation_names

        # Event + Property = 2 data elements
        assert len(interface.DataElements) == 2
        data_element_names = [de.Name for de in interface.DataElements]
        assert "MixedEvent" in data_element_names
        assert "MixedProperty" in data_element_names

    def test_ifex_fully_qualified_type_references(self, tmp_path) -> None:
        """Test that fully qualified type references with dots are converted to ::"""
        script_dir = Path(os.path.realpath(__file__)).parent

        fqn_file = script_dir / "test_data" / "fully_qualified_refs.yaml"
        fqn_file.write_text("""name: FullyQualifiedService
major_version: 1
minor_version: 0

namespaces:
  - name: Common
    namespaces:
      - name: Types
        structs:
          - name: Position
            members:
              - name: x
                datatype: float
              - name: y
                datatype: float
  - name: Services
    methods:
      - name: SetPosition
        input:
          - name: pos
            datatype: Common.Types.Position
        output:
          - name: success
            datatype: boolean
""")

        output_file = tmp_path / "fqn_model.json"

        ifex_batch_to_json([fqn_file], output_file, enable_layering=True)

        assert output_file.exists()

        model = load_json(str(output_file))

        # Verify Position struct with :: namespace separator
        assert len(model.DataTypeDefinitions.Structs) == 1
        position = model.DataTypeDefinitions.Structs[0]
        assert position.Name == "Position"
        assert position.Namespace == "Common::Types"

        # Verify method uses :: in type reference
        assert len(model.ModuleInterfaces) >= 1
        # Find the interface with SetPosition
        set_position_interface = None
        for iface in model.ModuleInterfaces:
            if any(op.Name == "SetPosition" for op in iface.Operations):
                set_position_interface = iface
                break

        assert set_position_interface is not None
        set_position_op = next(op for op in set_position_interface.Operations if op.Name == "SetPosition")

        # Find the input parameter
        input_param = next(p for p in set_position_op.Parameters if p.Name == "pos")
        # Type reference should use :: not .
        assert "::" in input_param.TypeRef.Name or input_param.TypeRef.Name == "Position"

    def test_ifex_enum_with_explicit_values(self, tmp_path) -> None:
        """Test enum with explicit values including gaps"""
        script_dir = Path(os.path.realpath(__file__)).parent

        enum_values_file = script_dir / "test_data" / "enum_explicit_values.yaml"
        enum_values_file.write_text("""name: EnumValueService
major_version: 1
minor_version: 0

namespaces:
  - name: Config
    enumerations:
      - name: Priority
        datatype: uint32
        options:
          - name: LOW
            value: 10
          - name: MEDIUM
            value: 20
          - name: HIGH
            value: 30
          - name: CRITICAL
            value: 100
""")

        output_file = tmp_path / "enum_values_model.json"

        ifex_batch_to_json([enum_values_file], output_file, enable_layering=True)

        assert output_file.exists()

        model = load_json(str(output_file))

        # Verify enum with correct values
        assert len(model.DataTypeDefinitions.Enums) == 1
        priority_enum = model.DataTypeDefinitions.Enums[0]
        assert priority_enum.Name == "Priority"
        assert len(priority_enum.Literals) == 4

        # Check specific values
        literal_dict = {lit.Item: lit.Value for lit in priority_enum.Literals}
        assert literal_dict["LOW"] == 10
        assert literal_dict["MEDIUM"] == 20
        assert literal_dict["HIGH"] == 30
        assert literal_dict["CRITICAL"] == 100

    def test_ifex_interface_with_description_fields(self, tmp_path) -> None:
        """Test that description fields are preserved (or handled gracefully)"""
        script_dir = Path(os.path.realpath(__file__)).parent

        description_file = script_dir / "test_data" / "interface_with_descriptions.yaml"
        description_file.write_text("""name: DescriptiveService
description: "A service with detailed descriptions"
major_version: 1
minor_version: 0

namespaces:
  - name: Docs
    description: "Documentation namespace"
    structs:
      - name: Config
        description: "Configuration structure"
        members:
          - name: timeout
            datatype: uint32
            description: "Timeout in milliseconds"
    methods:
      - name: Initialize
        description: "Initialize the service"
        input:
          - name: config
            datatype: Config
            description: "Initial configuration"
        output:
          - name: success
            datatype: boolean
            description: "True if initialization succeeded"
""")

        output_file = tmp_path / "description_model.json"

        # Should not fail even with description fields
        ifex_batch_to_json([description_file], output_file, enable_layering=True)

        assert output_file.exists()

        model = load_json(str(output_file))

        # Verify basic structure is correct (descriptions may or may not be preserved)
        assert len(model.DataTypeDefinitions.Structs) == 1
        assert model.DataTypeDefinitions.Structs[0].Name == "Config"

        assert len(model.ModuleInterfaces) == 1
        interface = model.ModuleInterfaces[0]
        assert len(interface.Operations) == 1
        assert interface.Operations[0].Name == "Initialize"

    def test_ifex_batch_vector_typedef_conflict_between_files(self, tmp_path) -> None:
        """Test that vector typedefs with different definitions across batch files are detected"""
        # First file: DataList is Vector of uint32
        file1 = tmp_path / "vector1.yaml"
        file1.write_text("""name: Service1
major_version: 1
minor_version: 0
namespaces:
  - name: Types
    typedefs:
      - name: DataList
        datatype: uint32[]
""")

        # Second file: DataList is Vector of float (CONFLICT!)
        file2 = tmp_path / "vector2.yaml"
        file2.write_text("""name: Service2
major_version: 1
minor_version: 0
namespaces:
  - name: Types
    typedefs:
      - name: DataList
        datatype: float[]
""")

        output_file = tmp_path / "conflict_model.json"

        import pytest  # pylint: disable=import-outside-toplevel

        with pytest.raises(ValueError) as exc_info:
            ifex_batch_to_json([file1, file2], output_file, enable_layering=True)

        error_msg = str(exc_info.value)
        assert "Vector" in error_msg
        assert "Types::DataList" in error_msg
        assert "defined differently in batch files" in error_msg

    def test_ifex_batch_map_typedef_conflict_between_files(self, tmp_path) -> None:
        """Test that map typedefs with different definitions across batch files are detected"""
        # First file: Registry is Map<string, uint32>
        file1 = tmp_path / "map1.yaml"
        file1.write_text("""name: Service1
major_version: 1
minor_version: 0
namespaces:
  - name: Types
    typedefs:
      - name: Registry
        datatype: map<string, uint32>
""")

        # Second file: Registry is Map<string, float> (CONFLICT!)
        file2 = tmp_path / "map2.yaml"
        file2.write_text("""name: Service2
major_version: 1
minor_version: 0
namespaces:
  - name: Types
    typedefs:
      - name: Registry
        datatype: map<string, float>
""")

        output_file = tmp_path / "conflict_model.json"

        import pytest  # pylint: disable=import-outside-toplevel

        with pytest.raises(ValueError) as exc_info:
            ifex_batch_to_json([file1, file2], output_file, enable_layering=True)

        error_msg = str(exc_info.value)
        assert "Map" in error_msg
        assert "Types::Registry" in error_msg
        assert "defined differently in batch files" in error_msg

    def test_ifex_batch_typeref_conflict_between_files(self, tmp_path) -> None:
        """Test that typeref (simple typedef) with different targets across batch files are detected"""
        # First file: Counter aliases to uint32
        file1 = tmp_path / "typeref1.yaml"
        file1.write_text("""name: Service1
major_version: 1
minor_version: 0
namespaces:
  - name: Types
    typedefs:
      - name: Counter
        datatype: uint32
""")

        # Second file: Counter aliases to uint64 (CONFLICT!)
        file2 = tmp_path / "typeref2.yaml"
        file2.write_text("""name: Service2
major_version: 1
minor_version: 0
namespaces:
  - name: Types
    typedefs:
      - name: Counter
        datatype: uint64
""")

        output_file = tmp_path / "conflict_model.json"

        import pytest  # pylint: disable=import-outside-toplevel

        with pytest.raises(ValueError) as exc_info:
            ifex_batch_to_json([file1, file2], output_file, enable_layering=True)

        error_msg = str(exc_info.value)
        assert "TypeRef" in error_msg
        assert "Types::Counter" in error_msg
        assert "defined differently in batch files" in error_msg

    def test_ifex_typedef_layering_within_file(self, tmp_path) -> None:
        """Test that typedef redefinitions within a single file's include hierarchy don't cause errors"""
        # Base file with initial typedef definitions
        base_file = tmp_path / "base_types.yaml"
        base_file.write_text("""name: BaseTypes
major_version: 1
minor_version: 0
namespaces:
  - name: Types
    typedefs:
      - name: DataList
        datatype: uint32[]
      - name: Registry
        datatype: map<string, uint32>
      - name: Counter
        datatype: uint32
""")

        # Override file that redefines the typedefs with IDENTICAL definitions
        # (within-file layering is supported, meaning no error should occur)
        override_file = tmp_path / "override_types.yaml"
        override_file.write_text(f"""name: OverrideTypes
major_version: 1
minor_version: 0
includes:
  - file: {base_file.name}
namespaces:
  - name: Types
    typedefs:
      # Redefine with same types - should not cause error (layering allowed)
      - name: DataList
        datatype: uint32[]
      - name: Registry
        datatype: map<string, uint32>
      - name: Counter
        datatype: uint32
""")

        output_file = tmp_path / "layered_model.json"

        # Should NOT raise error - layering within same file is allowed even for typedefs
        ifex_batch_to_json([override_file], output_file, enable_layering=True)

        assert output_file.exists()

        model = load_json(str(output_file))

        # Verify typedefs are present and deduplicated (should only appear once each)
        vector_names = [v.Name for v in model.DataTypeDefinitions.Vectors]
        assert "DataList" in vector_names
        assert vector_names.count("DataList") == 1

        map_names = [m.Name for m in model.DataTypeDefinitions.Maps]
        assert "Registry" in map_names
        assert map_names.count("Registry") == 1

        typeref_names = [t.Name for t in model.DataTypeDefinitions.TypeRefs]
        assert "Counter" in typeref_names
        assert typeref_names.count("Counter") == 1

    def test_ifex_batch_identical_typedef_deduplication(self, tmp_path) -> None:
        """Test that identical typedef definitions across different batch files are properly deduplicated"""
        # First file with typedefs
        file1 = tmp_path / "types1.yaml"
        file1.write_text("""name: Service1
major_version: 1
minor_version: 0
namespaces:
  - name: Common
    typedefs:
      - name: DataList
        datatype: uint32[]
      - name: Registry
        datatype: map<string, uint32>
      - name: Counter
        datatype: uint32
""")

        # Second file with IDENTICAL typedefs
        file2 = tmp_path / "types2.yaml"
        file2.write_text("""name: Service2
major_version: 1
minor_version: 0
namespaces:
  - name: Common
    typedefs:
      - name: DataList
        datatype: uint32[]
      - name: Registry
        datatype: map<string, uint32>
      - name: Counter
        datatype: uint32
""")

        output_file = tmp_path / "dedup_model.json"

        # Should NOT raise error - identical definitions are allowed and deduplicated
        ifex_batch_to_json([file1, file2], output_file, enable_layering=True)

        assert output_file.exists()

        model = load_json(str(output_file))

        # Verify each typedef appears only once (deduplicated)
        vector_names = [v.Name for v in model.DataTypeDefinitions.Vectors]
        assert vector_names.count("DataList") == 1

        map_names = [m.Name for m in model.DataTypeDefinitions.Maps]
        assert map_names.count("Registry") == 1

        typeref_names = [t.Name for t in model.DataTypeDefinitions.TypeRefs]
        assert typeref_names.count("Counter") == 1

    def test_ifex_typedef_override_order_with_includes(self, tmp_path) -> None:
        """Test that typedef overrides in main file properly override included base definitions"""
        # Base file with base typedefs (uint32 types)
        base_file = tmp_path / "base_types.yaml"
        base_file.write_text("""name: BaseTypes
major_version: 1
minor_version: 0
namespaces:
  - name: Types
    typedefs:
      - name: Counter
        datatype: uint32
      - name: Size
        datatype: uint32
""")

        # Override file with different typedefs (uint64 types) - should win!
        override_file = tmp_path / "override_types.yaml"
        override_file.write_text(f"""name: OverrideTypes
major_version: 1
minor_version: 0
includes:
  - file: {base_file.name}
namespaces:
  - name: Types
    typedefs:
      # These overrides should win over the base definitions
      - name: Counter
        datatype: uint64
      - name: Size
        datatype: uint64
""")

        output_file = tmp_path / "override_order_model.json"

        # Should NOT raise error - overrides within same file hierarchy are allowed
        ifex_batch_to_json([override_file], output_file, enable_layering=True)

        assert output_file.exists()

        model = load_json(str(output_file))

        # Verify that the OVERRIDE definitions are used (last seen = main file, not includes)
        counter = next((t for t in model.DataTypeDefinitions.TypeRefs if t.Name == "Counter"), None)
        assert counter is not None
        counter_type = str(counter.TypeRef)
        # The override file defines Counter as uint64, base file has uint32
        # With correct include order (includes first, main last), uint64 should win
        assert "uint64" in counter_type or "UInt64" in counter_type, (
            f"Expected Counter to be uint64 (override), but got {counter_type}"
        )

        size = next((t for t in model.DataTypeDefinitions.TypeRefs if t.Name == "Size"), None)
        assert size is not None
        size_type = str(size.TypeRef)
        assert "uint64" in size_type or "UInt64" in size_type, (
            f"Expected Size to be uint64 (override), but got {size_type}"
        )
