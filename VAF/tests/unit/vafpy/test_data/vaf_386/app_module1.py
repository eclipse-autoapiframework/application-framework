from datetime import timedelta

from imported_models.interface_project import *

from vaf import vafpy

app_module1 = vafpy.ApplicationModule(name="AppModule1", namespace="demo")
app_module1.add_consumed_interface(instance_name="CostmapConsumer", interface=Localplanner.Costmap.costmap_interface)
app_module1.add_provided_interface(
    instance_name="HvacControlProvider", interface=Nsprototype.Nsserviceinterface.Nshvaccontrol.hvac_control
)
app_module1.add_task(vafpy.Task(name="PeriodicTask", period=timedelta(milliseconds=200)))
