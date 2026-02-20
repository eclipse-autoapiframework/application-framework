from datetime import timedelta
from vaf import vafpy, BaseTypes

# TODO: Import the CaC support from platform derive or interface import
from .vss import *

vss_provider = vafpy.ApplicationModule(name="VssProvider", namespace="demo")

vss_provider.add_provided_interface(
    "AccelerationProvider", interface=Vss.Vehicle.acceleration_if
)
vss_provider.add_provided_interface("DriverProvider", interface=Vss.Vehicle.driver_if)

periodic_task = vafpy.Task(name="PeriodicTask", period=timedelta(milliseconds=200))
vss_provider.add_task(task=periodic_task)
