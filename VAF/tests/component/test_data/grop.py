from datetime import timedelta
from vaf import vafpy, BaseTypes

# TODO: Import the CaC support from platform derive or interface import
# from .imported_models import *

grop = vafpy.ApplicationModule(name="grop", namespace="duh")
# TODO: Add consumed and provided interfaces using the ApplicationModule API
# e.g. grop.add_consumed_interface(instance_name="DriverConsumer", interface=Vehicle.driver_if)

periodic_task = vafpy.Task(name="PeriodicTask", period=timedelta(milliseconds=200))
grop.add_task(task=periodic_task)
