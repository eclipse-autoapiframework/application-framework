from vaf import vafpy

from .vss import *

acceleration_if = vafpy.ModuleInterface(name="Acceleration_If", namespace="demo")
acceleration_if.add_data_element(name="Lateral", datatype=Vss.Vehicle.Acceleration.lateral)
acceleration_if.add_data_element(name="Longitudinal", datatype=Vss.Vehicle.Acceleration.longitudinal)
acceleration_if.add_data_element(name="Vertical", datatype=Vss.Vehicle.Acceleration.vertical)

driver_if = vafpy.ModuleInterface(name="Driver_If", namespace="demo")
driver_if.add_data_element(name="Identifier", datatype=Vss.Vehicle.Driver.identifier)
driver_if.add_data_element(name="IsEyesOnRoad", datatype=Vss.Vehicle.Driver.is_eyes_on_road)
