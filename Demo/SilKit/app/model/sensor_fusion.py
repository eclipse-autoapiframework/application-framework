from datetime import timedelta
from vaf import vafpy, BaseTypes

from .imported_models import *

sensor_fusion = vafpy.ApplicationModule(name="SensorFusion", namespace="NsApplicationUnit::NsSensorFusion")

sensor_fusion.add_provided_interface(
    "ObjectDetectionListModule",
    interfaces.Nsapplicationunit.Nsmoduleinterface.Nsobjectdetectionlist.object_detection_list_interface,
)
sensor_fusion.add_consumed_interface("ImageServiceConsumer1", interfaces.Af.AdasDemoApp.Services.image_service)
sensor_fusion.add_consumed_interface("ImageServiceConsumer2", interfaces.Af.AdasDemoApp.Services.image_service)
sensor_fusion.add_consumed_interface(
    "SteeringAngleServiceConsumer", interfaces.Af.AdasDemoApp.Services.steering_angle_service
)
sensor_fusion.add_consumed_interface("VelocityServiceConsumer", interfaces.Af.AdasDemoApp.Services.velocity_service)

p_200ms = timedelta(milliseconds=200)
step1 = vafpy.Task(name="Step1", period=p_200ms, preferred_offset=0)
step2 = vafpy.Task(name="Step2", period=p_200ms, preferred_offset=0)
step3 = vafpy.Task(name="Step3", period=p_200ms, preferred_offset=0)

sensor_fusion.add_task(task=step1)
sensor_fusion.add_task_chain(tasks=[step2, step3], run_after=[step1])
sensor_fusion.add_task(vafpy.Task(name="Step4", period=p_200ms, preferred_offset=0, run_after=[step1]))
