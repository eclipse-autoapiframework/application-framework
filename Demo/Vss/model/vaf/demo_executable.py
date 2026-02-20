from datetime import timedelta

from .application_modules import *
from vaf import *

executable = Executable("DemoExecutable", timedelta(milliseconds=10))

executable.add_application_module(
    VssProvider,
    [(Instances.VssProvider.Tasks.PeriodicTask, timedelta(milliseconds=1), 0)],
)
executable.add_application_module(
    VssConsumer,
    [(Instances.VssConsumer.Tasks.PeriodicTask, timedelta(milliseconds=1), 1)],
)

executable.connect_interfaces(
    VssProvider,
    Instances.VssProvider.ProvidedInterfaces.AccelerationProvider,
    VssConsumer,
    Instances.VssConsumer.ConsumedInterfaces.AccelerationConsumer,
)
executable.connect_interfaces(
    VssProvider,
    Instances.VssProvider.ProvidedInterfaces.DriverProvider,
    VssConsumer,
    Instances.VssConsumer.ConsumedInterfaces.DriverConsumer,
)
