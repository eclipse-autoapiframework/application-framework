from datetime import timedelta

from .application_modules import AppModule1, Instances, AppModule2
from vaf import *

# Create executable instances (or configure existing ones from the platform configuration)
executable = Executable("HelloVaf")

# Add application modules to executable instances
executable.add_application_module(AppModule1, [(Instances.AppModule1.Tasks.PeriodicTask, timedelta(milliseconds=10), 0)])
executable.add_application_module(AppModule2, [(Instances.AppModule2.Tasks.PeriodicTask, timedelta(milliseconds=10), 1)])

# Connect the internal application module instances
executable.connect_interfaces(
    AppModule1,
    Instances.AppModule1.ProvidedInterfaces.HelloWorldProvider,
    AppModule2,
    Instances.AppModule2.ConsumedInterfaces.HelloWorldConsumer,
)
