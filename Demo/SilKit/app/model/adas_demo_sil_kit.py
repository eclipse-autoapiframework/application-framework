from datetime import timedelta

from .application_modules import *
from vaf import Executable

# Create application
adas_demo_app = Executable("adas_demo_app", timedelta(milliseconds=20))

b_10ms = timedelta(milliseconds=10)
adas_demo_app.add_application_module(
    SensorFusion,
    [
        (Instances.SensorFusion.Tasks.Step1, b_10ms, 0),
        (Instances.SensorFusion.Tasks.Step2, b_10ms, 0),
        (Instances.SensorFusion.Tasks.Step3, b_10ms, 0),
        (Instances.SensorFusion.Tasks.Step4, b_10ms, 0),
    ],
)
adas_demo_app.add_application_module(
    CollisionDetection, [(Instances.CollisionDetection.Tasks.PeriodicTask, timedelta(milliseconds=1), 1)]
)

# connect intra process interfaces
adas_demo_app.connect_interfaces(
    SensorFusion,
    Instances.SensorFusion.ProvidedInterfaces.ObjectDetectionListModule,
    CollisionDetection,
    Instances.CollisionDetection.ConsumedInterfaces.ObjectDetectionListModule,
)

# connect middleware interfaces
adas_demo_app.connect_consumed_interface_to_silkit(
    SensorFusion,
    Instances.SensorFusion.ConsumedInterfaces.ImageServiceConsumer1,
    "Silkit_ImageService1",
)
adas_demo_app.connect_consumed_interface_to_silkit(
    SensorFusion,
    Instances.SensorFusion.ConsumedInterfaces.ImageServiceConsumer2,
    "Silkit_ImageService2",
)
adas_demo_app.connect_consumed_interface_to_silkit(
    SensorFusion,
    Instances.SensorFusion.ConsumedInterfaces.SteeringAngleServiceConsumer,
    "Silkit_SteeringAngleService",
)
adas_demo_app.connect_consumed_interface_to_silkit(
    SensorFusion,
    Instances.SensorFusion.ConsumedInterfaces.VelocityServiceConsumer,
    "Silkit_VelocityService",
)

adas_demo_app.connect_provided_interface_to_silkit(
    CollisionDetection,
    Instances.CollisionDetection.ProvidedInterfaces.BrakeServiceProvider,
    "Silkit_BrakeService",
)
