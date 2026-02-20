from datetime import timedelta

from vaf import *

from .application_modules import Instances, Nobunaga, Tadakatsu

executable = Executable("Daimyo", timedelta(milliseconds=10))

executable.add_application_module(Nobunaga, [(Instances.Nobunaga.Tasks.Deploy, timedelta(milliseconds=10), 0)])
executable.add_application_module(Tadakatsu, [(Instances.Tadakatsu.Tasks.Deploy, timedelta(milliseconds=5), 0)])

executable.connect_interfaces(
    Tadakatsu,
    Instances.Tadakatsu.ProvidedInterfaces.BraveSamurai,
    Nobunaga,
    Instances.Nobunaga.ConsumedInterfaces.EliteSamurai,
)
