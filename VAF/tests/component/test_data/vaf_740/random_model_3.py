from datetime import timedelta

from vaf import *

from .application_modules import Instances, RandomAppModule, ExampleAppModule

executable = Executable("Warrior", timedelta(milliseconds=25))

executable.add_application_module(RandomAppModule, [(Instances.RandomAppModule.Tasks.RandomTask, timedelta(milliseconds=8), 0)])
executable.add_application_module(ExampleAppModule, [(Instances.ExampleAppModule.Tasks.ExampleTask, timedelta(milliseconds=12), 0)])

executable.connect_interfaces(
    ExampleAppModule,
    Instances.ExampleAppModule.ProvidedInterfaces.ExampleInterfaceProvider,
    RandomAppModule,
    Instances.RandomAppModule.ConsumedInterfaces.RandomInterfaceConsumer,
)
