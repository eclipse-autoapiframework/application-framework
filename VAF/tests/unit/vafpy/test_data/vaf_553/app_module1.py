from datetime import timedelta

from vaf import vafpy

from .imported_models.interfaces import *

app_module1 = vafpy.ApplicationModule(name="AppModule1", namespace="demo")
app_module1.add_consumed_interface(
    instance_name="ParkingBrakeConsumer",
    interface=Vss.Vehicle.Chassis.parking_brake_if,
)
app_module1.add_provided_interface(
    instance_name="DataExchangeProvider",
    interface=Demo.data_exchange_interface,
)

periodic_task = vafpy.Task(name="PeriodicTask", period=timedelta(milliseconds=200))
app_module1.add_task(task=periodic_task)
