from vaf import BaseTypes, save_main_model, vafpy
import os
from datetime import timedelta

# Define a random module interface
random_interface = vafpy.ModuleInterface(name="ExchangeInterface", namespace="Namespace::Common")
random_interface.add_data_element(name="TheElement", datatype=BaseTypes.UINT64_T)

# Define a random application module
random_module = vafpy.ApplicationModule(name="RandomAppModule", namespace="RandomNamespace")
random_module.add_consumed_interface(instance_name="RandomInterfaceConsumer", interface=random_interface)
random_module.add_task(vafpy.Task(name="RandomTask", period=timedelta(milliseconds=300), preferred_offset=0))

if __name__ == "__main__":
    script_path = os.path.dirname(os.path.realpath(__file__))
    save_main_model(os.path.join(script_path, "random_model_1.json"))
