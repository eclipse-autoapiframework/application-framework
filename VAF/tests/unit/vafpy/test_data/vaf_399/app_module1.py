from datetime import timedelta

from vss import Vss

from vaf import vafpy

app_module1 = vafpy.ApplicationModule(name="AppModule1", namespace="demo")
app_module1.add_consumed_interface(instance_name="AxleRow1Consumer", interface=Vss.Vehicle.Chassis.Axle.row1)
app_module1.add_task(vafpy.Task(name="PeriodicTask", period=timedelta(milliseconds=200)))
