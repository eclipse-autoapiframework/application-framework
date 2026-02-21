from datetime import timedelta
from vaf import vafpy

from .imported_models import *

vss_consumer = vafpy.ApplicationModule(name="VssConsumer", namespace="demo")

vss_consumer.add_consumed_interface("AccelerationConsumer", interface=vss_interfaces.Demo.acceleration_if)
vss_consumer.add_consumed_interface("DriverConsumer", interface=vss_interfaces.Demo.driver_if)

periodic_task = vafpy.Task(name="PeriodicTask", period=timedelta(milliseconds=200))
vss_consumer.add_task(task=periodic_task)
