from datetime import timedelta
from vaf import vafpy, BaseTypes

# TODO: Import the CaC support from platform derive or interface import
# from .imported_models import *

nobunaga = vafpy.ApplicationModule(name="Nobunaga", namespace="oda")
# TODO: Add consumed and provided interfaces using the ApplicationModule API
# e.g. nobunaga.add_consumed_interface(instance_name="DriverConsumer", interface=Vehicle.driver_if)

periodic_task = vafpy.Task(name="PeriodicTask", period=timedelta(milliseconds=200))
nobunaga.add_task(task=periodic_task)
