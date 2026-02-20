from datetime import timedelta
from vaf import vafpy, BaseTypes

from .imported_models import *

collision_detection = vafpy.ApplicationModule(
    name="CollisionDetection", namespace="NsApplicationUnit::NsCollisionDetection"
)
collision_detection.add_provided_interface("BrakeServiceProvider", interfaces.Af.AdasDemoApp.Services.brake_service)
collision_detection.add_consumed_interface(
    "ObjectDetectionListModule",
    interfaces.Nsapplicationunit.Nsmoduleinterface.Nsobjectdetectionlist.object_detection_list_interface,
)

periodic_task = vafpy.Task(name="PeriodicTask", period=timedelta(milliseconds=200))
collision_detection.add_task(task=periodic_task)
