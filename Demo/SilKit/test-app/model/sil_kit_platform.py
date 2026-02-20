from datetime import timedelta
from vaf import vafpy, BaseTypes

# TODO: Import the CaC support from platform derive or interface import
from .imported_models import *

sil_kit_platform = vafpy.ApplicationModule(name="SilKitPlatform", namespace="NsApplicationUnit::NsSilKitPlatform")
# TODO: Add consumed and provided interfaces using the ApplicationModule API
sil_kit_platform.add_consumed_interface(
    instance_name="BrakeServiceConsumer", interface=interfaces.Af.AdasDemoApp.Services.brake_service
)
sil_kit_platform.add_provided_interface(
    instance_name="ImageServiceProvider1", interface=interfaces.Af.AdasDemoApp.Services.image_service
)
sil_kit_platform.add_provided_interface(
    instance_name="ImageServiceProvider2", interface=interfaces.Af.AdasDemoApp.Services.image_service
)
sil_kit_platform.add_provided_interface(
    instance_name="SteeringAngleServiceProvider", interface=interfaces.Af.AdasDemoApp.Services.steering_angle_service
)
sil_kit_platform.add_provided_interface(
    instance_name="VelocityServiceProvider", interface=interfaces.Af.AdasDemoApp.Services.velocity_service
)

sil_kit_platform.add_task(task=vafpy.Task(name="BrakeTask", period=timedelta(milliseconds=100)))
sil_kit_platform.add_task(task=vafpy.Task(name="ImageTask", period=timedelta(milliseconds=100)))
sil_kit_platform.add_task(task=vafpy.Task(name="SteeringAngleTask", period=timedelta(milliseconds=1000)))
sil_kit_platform.add_task(task=vafpy.Task(name="VelocityTask", period=timedelta(milliseconds=1000)))
