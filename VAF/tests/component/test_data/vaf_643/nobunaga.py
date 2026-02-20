from datetime import timedelta
from vaf import vafpy, BaseTypes

# TODO: Import the CaC support from platform derive or interface import
# from .imported_models import *

nobunaga = vafpy.ApplicationModule(name="Nobunaga", namespace="oda")
# TODO: Add consumed and provided interfaces using the ApplicationModule API

samurai = vafpy.Struct("samurai", "sengoku")
samurai.add_subelement("health", BaseTypes.FLOAT)
samurai.add_subelement("attack", BaseTypes.FLOAT)
samurai.add_subelement("defense", BaseTypes.FLOAT)

army = vafpy.ModuleInterface("sonae", "sengoku")
army.add_data_element("samurai", samurai)
nobunaga.add_consumed_interface(instance_name="EliteSamurai", interface=army)

deploy = vafpy.Task(name="Deploy", period=timedelta(milliseconds=15))
nobunaga.add_task(task=deploy)
