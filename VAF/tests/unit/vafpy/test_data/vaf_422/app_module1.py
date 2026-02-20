from datetime import timedelta

from imported_models.interface import *

from vaf import vafpy

app_module1 = vafpy.ApplicationModule(name="app-module1", namespace="demo")
app_module1.add_provided_interface(
    instance_name="ObjectDetectionListProvider", interface=Demo.object_detection_list_interface
)
app_module1.add_consumed_interface(
    instance_name="HvacStatusConsumer", interface=Nsprototype.Nsserviceinterface.Nshvacstatus.hvac_status
)
app_module1.add_consumed_interface(instance_name="ChassisLeftAxleConsumer", interface=Vss.Vehicle.Chassis.axle)

periodic_task = vafpy.Task(name="PeriodicTask", period=timedelta(milliseconds=200))
app_module1.add_task(task=periodic_task)
