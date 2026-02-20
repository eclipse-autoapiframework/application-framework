from pathlib import Path

from vaf import BaseTypes, save_part_of_main_model, vafpy
from vaf.vafgeneration import generate_cac_support

object_detection = vafpy.datatypes.Struct(name="ObjectDetection", namespace="demo")
object_detection.add_subelement(name="x", datatype=BaseTypes.UINT64_T)
object_detection.add_subelement(name="y", datatype=BaseTypes.UINT64_T)
object_detection.add_subelement(name="z", datatype=BaseTypes.UINT64_T)

od_list = vafpy.datatypes.Vector(name="ObjectDetectionList", namespace="demo", datatype=object_detection)

data_element_if = vafpy.ModuleInterface(name="DataElementInterface", namespace="demo")
data_element_if.add_data_element(name="object_detection_list", datatype=od_list)

operation_if = vafpy.ModuleInterface(name="OperationInterface", namespace="demo")
operation_if.add_operation(name="my_operation")

both_if = vafpy.ModuleInterface(name="BothInterface", namespace="demo")
both_if.add_data_element(name="object_detection_list", datatype=od_list)
both_if.add_operation(name="my_operation")

empty_if = vafpy.ModuleInterface(name="EmptyInterface", namespace="demo")


def export_model():
    script_path = Path(__file__).resolve().parent
    export_path = script_path / "export"
    export_path.mkdir(parents=True, exist_ok=True)
    save_part_of_main_model((export_path / "asdfIf.json").as_posix(), ["DataTypeDefinitions", "ModuleInterfaces"])
    generate_cac_support(export_path, "asdfIf.json", "asdfIf", script_path / "export")


if __name__ == "__main__":
    export_model()
