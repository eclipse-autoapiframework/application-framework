from datetime import timedelta
from vaf import vafpy, BaseTypes

# TODO: Import the CaC support from platform derive or interface import
from .vss import *

vss_consumer = vafpy.ApplicationModule(name="VssConsumer", namespace="demo")

vss_consumer.add_consumed_interface(
    "AccelerationConsumer", interface=Vss.Vehicle.acceleration_if
)
vss_consumer.add_consumed_interface("DriverConsumer", interface=Vss.Vehicle.driver_if)

periodic_task = vafpy.Task(name="PeriodicTask", period=timedelta(milliseconds=200))
vss_consumer.add_task(task=periodic_task)
