from datetime import timedelta

from .application_modules import *
from vaf import *

executable = Executable("MyExecutable", timedelta(milliseconds=10))

executable.add_application_module(Module1, [(Instances.Module1.Tasks.PeriodicTask, timedelta(milliseconds=1), 0)])
executable.add_application_module(Module2, [(Instances.Module2.Tasks.PeriodicTask, timedelta(milliseconds=1), 0)])
executable.add_application_module(Module4, [(Instances.Module4.Tasks.PeriodicTask, timedelta(milliseconds=1), 0)])
