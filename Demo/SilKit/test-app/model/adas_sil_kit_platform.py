from datetime import timedelta

from .application_modules import *
from vaf import *

executable = Executable("SilKitPlatform")

executable.add_application_module(SilKitPlatform, [])

executable.connect_consumed_interface_to_silkit(
    SilKitPlatform,
    Instances.SilKitPlatform.ConsumedInterfaces.BrakeServiceConsumer,
    "Silkit_BrakeService",
)

executable.connect_provided_interface_to_silkit(
    SilKitPlatform,
    Instances.SilKitPlatform.ProvidedInterfaces.ImageServiceProvider1,
    "Silkit_ImageService1",
)
executable.connect_provided_interface_to_silkit(
    SilKitPlatform,
    Instances.SilKitPlatform.ProvidedInterfaces.ImageServiceProvider2,
    "Silkit_ImageService2",
)
executable.connect_provided_interface_to_silkit(
    SilKitPlatform,
    Instances.SilKitPlatform.ProvidedInterfaces.SteeringAngleServiceProvider,
    "Silkit_SteeringAngleService",
)
executable.connect_provided_interface_to_silkit(
    SilKitPlatform,
    Instances.SilKitPlatform.ProvidedInterfaces.VelocityServiceProvider,
    "Silkit_VelocityService",
)
