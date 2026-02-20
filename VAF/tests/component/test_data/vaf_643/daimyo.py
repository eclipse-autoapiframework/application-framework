from datetime import timedelta

from vaf import *

from .application_modules import Instances, Nobunaga

executable = Executable("Daimyo", timedelta(milliseconds=10))

executable.add_application_module(Nobunaga, [(Instances.Nobunaga.Tasks.PeriodicTask, timedelta(milliseconds=1), 0)])
