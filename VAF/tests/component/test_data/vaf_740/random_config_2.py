from vaf import BaseTypes, save_main_model, vafpy
import os
from datetime import timedelta

# Define a random module interface
random_interface = vafpy.ModuleInterface(name="ExchangeInterface", namespace="Namespace::Common")
random_interface.add_data_element(name="TheElement", datatype=BaseTypes.UINT64_T)

# Define a random application module
example_module = vafpy.ApplicationModule(name="ExampleAppModule", namespace="ExampleNamespace")
example_module.add_provided_interface(instance_name="ExampleInterfaceProvider", interface=random_interface)
example_module.add_task(vafpy.Task(name="ExampleTask", period=timedelta(milliseconds=500), preferred_offset=0))

if __name__ == "__main__":
    script_path = os.path.dirname(os.path.realpath(__file__))
    save_main_model(os.path.join(script_path, "random_model_2.json"))
