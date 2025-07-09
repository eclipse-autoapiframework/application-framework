import os

from vaf.vafpy import Executable
from vaf.vafpy.runtime import (
    get_module_interface,
    get_platform_consumer_module,
    get_platform_provider_module,
    import_model,
)

script_path = os.path.dirname(os.path.realpath(__file__))

import_model(os.path.join(script_path, "interface.json"))



class Demo:
    # ModuleInterfaces
    object_detection_list_interface = get_module_interface(
        "ObjectDetectionListInterface", "demo"
    )


class Nsprototype:
    class Nsserviceinterface:
        class Nshvaccontrol:
            # ModuleInterfaces
            hvac_control = get_module_interface(
                "HvacControl", "nsprototype::nsserviceinterface::nshvaccontrol"
            )
        class Nshvacstatus:
            # ModuleInterfaces
            hvac_status = get_module_interface(
                "HvacStatus", "nsprototype::nsserviceinterface::nshvacstatus"
            )


class Vss:
    # ModuleInterfaces
    vehicle = get_module_interface(
        "Vehicle", "vss"
    )
    class Vehicle:
        # ModuleInterfaces
        chassis = get_module_interface(
            "Chassis", "vss::vehicle"
        )
        class Chassis:
            # ModuleInterfaces
            accelerator = get_module_interface(
                "Accelerator", "vss::vehicle::chassis"
            )
            axle = get_module_interface(
                "Axle", "vss::vehicle::chassis"
            )
            brake = get_module_interface(
                "Brake", "vss::vehicle::chassis"
            )
            parking_brake = get_module_interface(
                "ParkingBrake", "vss::vehicle::chassis"
            )
            steering_wheel = get_module_interface(
                "SteeringWheel", "vss::vehicle::chassis"
            )
            class Axle:
                # ModuleInterfaces
                row1 = get_module_interface(
                    "Row1", "vss::vehicle::chassis::axle"
                )
                row2 = get_module_interface(
                    "Row2", "vss::vehicle::chassis::axle"
                )
                class Row1:
                    # ModuleInterfaces
                    wheel = get_module_interface(
                        "Wheel", "vss::vehicle::chassis::axle::row1"
                    )
                    class Wheel:
                        # ModuleInterfaces
                        left = get_module_interface(
                            "Left", "vss::vehicle::chassis::axle::row1::wheel"
                        )
                        right = get_module_interface(
                            "Right", "vss::vehicle::chassis::axle::row1::wheel"
                        )
                        class Left:
                            # ModuleInterfaces
                            brake = get_module_interface(
                                "Brake", "vss::vehicle::chassis::axle::row1::wheel::left"
                            )
                            tire = get_module_interface(
                                "Tire", "vss::vehicle::chassis::axle::row1::wheel::left"
                            )
                        class Right:
                            # ModuleInterfaces
                            brake = get_module_interface(
                                "Brake", "vss::vehicle::chassis::axle::row1::wheel::right"
                            )
                            tire = get_module_interface(
                                "Tire", "vss::vehicle::chassis::axle::row1::wheel::right"
                            )
                class Row2:
                    # ModuleInterfaces
                    wheel = get_module_interface(
                        "Wheel", "vss::vehicle::chassis::axle::row2"
                    )
                    class Wheel:
                        # ModuleInterfaces
                        left = get_module_interface(
                            "Left", "vss::vehicle::chassis::axle::row2::wheel"
                        )
                        right = get_module_interface(
                            "Right", "vss::vehicle::chassis::axle::row2::wheel"
                        )
                        class Left:
                            # ModuleInterfaces
                            brake = get_module_interface(
                                "Brake", "vss::vehicle::chassis::axle::row2::wheel::left"
                            )
                            tire = get_module_interface(
                                "Tire", "vss::vehicle::chassis::axle::row2::wheel::left"
                            )
                        class Right:
                            # ModuleInterfaces
                            brake = get_module_interface(
                                "Brake", "vss::vehicle::chassis::axle::row2::wheel::right"
                            )
                            tire = get_module_interface(
                                "Tire", "vss::vehicle::chassis::axle::row2::wheel::right"
                            )


