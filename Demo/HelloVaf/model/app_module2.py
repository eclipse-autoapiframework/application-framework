from datetime import timedelta
from vaf import vafpy, BaseTypes

# TODO: Import the CaC support from platform derive or interface import
# from .imported_models import *

interface = vafpy.ModuleInterface(name="HelloWorldIf", namespace="demo")
interface.add_data_element("Message", datatype=BaseTypes.STRING)
interface.add_operation("SetMsgId", in_parameter={"MsgId": BaseTypes.UINT8_T})

app_module2 = vafpy.ApplicationModule(name="AppModule2", namespace="demo")
app_module2.add_consumed_interface("HelloWorldConsumer", interface)

periodic_task = vafpy.Task(name="PeriodicTask", period=timedelta(milliseconds=1000))
app_module2.add_task(task=periodic_task)
