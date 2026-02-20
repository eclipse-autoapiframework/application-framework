from datetime import timedelta

from vaf import BaseTypes, vafpy

# TODO: Import the CaC support from platform derive or interface import
# from .imported_models import *

str_type = vafpy.String(name="string", namespace="demo")

interface = vafpy.ModuleInterface(name="HelloWorldIf", namespace="demo")
interface.add_data_element("Message", datatype=str_type)
interface.add_data_element("Message_base_string", BaseTypes.STRING)
interface.add_operation("SetMsgId", in_parameter={"MsgId": BaseTypes.UINT8_T})

app_module1 = vafpy.ApplicationModule(name="AppModule1", namespace="demo")

# Add consumed and provided interfaces using the ApplicationModule API
app_module1.add_provided_interface("HelloWorldProvider", interface)

periodic_task = vafpy.Task(name="PeriodicTask", period=timedelta(milliseconds=500))
app_module1.add_task(task=periodic_task)
