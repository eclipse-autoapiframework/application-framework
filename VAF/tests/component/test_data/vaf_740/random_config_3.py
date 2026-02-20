from vaf import BaseTypes, save_main_model, vafpy
import os
from datetime import timedelta

# Define a random struct
sample_struct = vafpy.datatypes.Struct(name="SampleStruct", namespace="SampleNamespace::Test")
sample_struct.add_subelement(name="SampleID", datatype=BaseTypes.INT64_T)
sample_struct.add_subelement(name="SampleValue", datatype=BaseTypes.FLOAT)

# Define a random vector
sample_vector = vafpy.datatypes.Vector(name="SampleVector", namespace="SampleNamespace::Test", datatype=sample_struct)

# Define a random module interface
sample_interface = vafpy.ModuleInterface(name="SampleInterface", namespace="SampleNamespace::Test")
sample_interface.add_data_element(name="SampleElement", datatype=sample_vector)

# Define a random application module
sample_module = vafpy.ApplicationModule(name="SampleAppModule", namespace="SampleNamespace")
sample_module.add_consumed_interface(instance_name="SampleInterfaceProvider", interface=sample_interface)
sample_module.add_task(vafpy.Task(name="SampleTask", period=timedelta(milliseconds=100), preferred_offset=0))

if __name__ == "__main__":
    script_path = os.path.dirname(os.path.realpath(__file__))
    save_main_model(os.path.join(script_path, "random_model_3.json"))
