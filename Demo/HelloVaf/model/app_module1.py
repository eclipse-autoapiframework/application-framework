from datetime import timedelta
from vaf import vafpy, BaseTypes

# TODO: Import the CaC support from platform derive or interface import
# from .imported_models import *

interface = vafpy.ModuleInterface(name="HelloWorldIf", namespace="demo")
interface.add_data_element("Message", datatype=BaseTypes.STRING)
interface.add_operation("SetMsgId", in_parameter={"MsgId": BaseTypes.UINT8_T})

app_module1 = vafpy.ApplicationModule(name="AppModule1", namespace="demo")
app_module1.add_provided_interface("HelloWorldProvider", interface)

periodic_task = vafpy.Task(name="PeriodicTask", period=timedelta(milliseconds=500))
app_module1.add_task(task=periodic_task)
