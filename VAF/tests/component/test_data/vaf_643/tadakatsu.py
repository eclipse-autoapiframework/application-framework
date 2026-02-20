from datetime import timedelta
from vaf import vafpy, BaseTypes

# TODO: Import the CaC support from platform derive or interface import
# from .imported_models import *

tadakatsu = vafpy.ApplicationModule(name="Tadakatsu", namespace="honda")
# TODO: Add consumed and provided interfaces using the ApplicationModule API
samurai = vafpy.Struct("samurai", "sengoku")
samurai.add_subelement("health", BaseTypes.FLOAT)
samurai.add_subelement("attack", BaseTypes.FLOAT)
samurai.add_subelement("defense", BaseTypes.FLOAT)

army = vafpy.ModuleInterface("sonae", "sengoku")
army.add_data_element("samurai", samurai)
tadakatsu.add_provided_interface(instance_name="BraveSamurai", interface=army)

periodic_task = vafpy.Task(name="Deploy", period=timedelta(milliseconds=15))
tadakatsu.add_task(task=periodic_task)
