#!/bin/python3
import os
import sys

sys.path.append(".")

from datetime import timedelta

from vss import *

from vaf import save_main_model, vafpy

vss_provider = vafpy.ApplicationModule(name="VssProvider", namespace="demo")
vss_provider.add_provided_interface(instance_name="AccelerationProvider", interface=Vss.Vehicle.acceleration_if)
vss_provider.add_provided_interface(instance_name="DriverProvider", interface=Vss.Vehicle.driver_if)
vss_provider.add_task(vafpy.Task(name="PeriodicTask", period=timedelta(milliseconds=200)))

vss_consumer = vafpy.ApplicationModule(name="VssConsumer", namespace="demo")
vss_consumer.add_consumed_interface(instance_name="AccelerationConsumer", interface=Vss.Vehicle.acceleration_if)
vss_consumer.add_consumed_interface(instance_name="DriverConsumer", interface=Vss.Vehicle.driver_if)
vss_consumer.add_task(vafpy.Task(name="PeriodicTask", period=timedelta(milliseconds=200)))


# Create application
app = vafpy.Executable("DemoExecutable", timedelta(milliseconds=10))
app.add_application_module(vss_provider, [("PeriodicTask", timedelta(milliseconds=1), 0)])
app.add_application_module(vss_consumer, [("PeriodicTask", timedelta(milliseconds=1), 1)])

# connect intra process interfaces
app.connect_interfaces(vss_provider, "AccelerationProvider", vss_consumer, "AccelerationConsumer")
app.connect_interfaces(vss_provider, "DriverProvider", vss_consumer, "DriverConsumer")


if __name__ == "__main__":
    script_path = os.path.dirname(os.path.realpath(__file__))
    save_main_model(os.path.join(script_path, "model.json"))
