from datetime import timedelta
from vaf import vafpy

from .imported_models import *

vss_provider = vafpy.ApplicationModule(name="VssProvider", namespace="demo")

vss_provider.add_provided_interface("AccelerationProvider", interface=vss_interfaces.Demo.acceleration_if)
vss_provider.add_provided_interface("DriverProvider", interface=vss_interfaces.Demo.driver_if)

periodic_task = vafpy.Task(name="PeriodicTask", period=timedelta(milliseconds=200))
vss_provider.add_task(task=periodic_task)
