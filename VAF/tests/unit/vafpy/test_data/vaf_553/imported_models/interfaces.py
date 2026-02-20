import os

from vaf.vafpy.runtime import (
    get_datatype,
    get_module_interface,
    import_model,
)

script_path = os.path.dirname(os.path.realpath(__file__))

import_model(os.path.join(script_path, "Interfaces.json"))


class Af:
    class AdasDemoApp:
        class Services:
            # Module Interfaces
            brake_service = get_module_interface("BrakeService", "af::adas_demo_app::services")
            image_service = get_module_interface("ImageService", "af::adas_demo_app::services")
            steering_angle_service = get_module_interface("SteeringAngleService", "af::adas_demo_app::services")
            velocity_service = get_module_interface("VelocityService", "af::adas_demo_app::services")


class Datatypes:
    # Vectors
    u_int8_vector = get_datatype("UInt8Vector", "datatypes", "Vector")
    # Structs
    velocity = get_datatype("Velocity", "datatypes", "Struct")
    steering_angle = get_datatype("SteeringAngle", "datatypes", "Struct")
    brake_pressure = get_datatype("BrakePressure", "datatypes", "Struct")
    image = get_datatype("Image", "datatypes", "Struct")


class Demo:
    # Strings
    my_string_type = get_datatype("MyStringType", "demo", "String")
    # Module Interfaces
    data_exchange_interface = get_module_interface("DataExchangeInterface", "demo")


class Vaf:
    # Strings
    string = get_datatype("string", "vaf", "String")


class Vss:
    # Structs
    vehicle = get_datatype("Vehicle", "vss", "Struct")
    # Module Interfaces
    vehicle_if = get_module_interface("Vehicle_If", "vss")

    class Vehicle:
        # Structs
        chassis = get_datatype("Chassis", "vss::vehicle", "Struct")
        # Module Interfaces
        chassis_if = get_module_interface("Chassis_If", "vss::vehicle")

        class Chassis:
            # Structs
            accelerator = get_datatype("Accelerator", "vss::vehicle::chassis", "Struct")
            axle = get_datatype("Axle", "vss::vehicle::chassis", "Struct")
            brake = get_datatype("Brake", "vss::vehicle::chassis", "Struct")
            steering_wheel = get_datatype("SteeringWheel", "vss::vehicle::chassis", "Struct")
            parking_brake = get_datatype("ParkingBrake", "vss::vehicle::chassis", "Struct")
            # Module Interfaces
            accelerator_if = get_module_interface("Accelerator_If", "vss::vehicle::chassis")
            axle_if = get_module_interface("Axle_If", "vss::vehicle::chassis")
            brake_if = get_module_interface("Brake_If", "vss::vehicle::chassis")
            parking_brake_if = get_module_interface("ParkingBrake_If", "vss::vehicle::chassis")
            steering_wheel_if = get_module_interface("SteeringWheel_If", "vss::vehicle::chassis")

            class Axle:
                # Structs
                row1 = get_datatype("Row1", "vss::vehicle::chassis::axle", "Struct")
                row2 = get_datatype("Row2", "vss::vehicle::chassis::axle", "Struct")
                # Module Interfaces
                row1_if = get_module_interface("Row1_If", "vss::vehicle::chassis::axle")
                row2_if = get_module_interface("Row2_If", "vss::vehicle::chassis::axle")

                class Row1:
                    # Structs
                    wheel = get_datatype("Wheel", "vss::vehicle::chassis::axle::row1", "Struct")
                    # Module Interfaces
                    wheel_if = get_module_interface("Wheel_If", "vss::vehicle::chassis::axle::row1")

                    class Wheel:
                        # Structs
                        left = get_datatype("Left", "vss::vehicle::chassis::axle::row1::wheel", "Struct")
                        right = get_datatype("Right", "vss::vehicle::chassis::axle::row1::wheel", "Struct")
                        # Module Interfaces
                        left_if = get_module_interface("Left_If", "vss::vehicle::chassis::axle::row1::wheel")
                        right_if = get_module_interface("Right_If", "vss::vehicle::chassis::axle::row1::wheel")

                        class Left:
                            # Structs
                            tire = get_datatype("Tire", "vss::vehicle::chassis::axle::row1::wheel::left", "Struct")
                            brake = get_datatype("Brake", "vss::vehicle::chassis::axle::row1::wheel::left", "Struct")
                            # Module Interfaces
                            brake_if = get_module_interface(
                                "Brake_If", "vss::vehicle::chassis::axle::row1::wheel::left"
                            )
                            tire_if = get_module_interface("Tire_If", "vss::vehicle::chassis::axle::row1::wheel::left")

                        class Right:
                            # Structs
                            tire = get_datatype("Tire", "vss::vehicle::chassis::axle::row1::wheel::right", "Struct")
                            brake = get_datatype("Brake", "vss::vehicle::chassis::axle::row1::wheel::right", "Struct")
                            # Module Interfaces
                            brake_if = get_module_interface(
                                "Brake_If", "vss::vehicle::chassis::axle::row1::wheel::right"
                            )
                            tire_if = get_module_interface("Tire_If", "vss::vehicle::chassis::axle::row1::wheel::right")

                class Row2:
                    # Structs
                    wheel = get_datatype("Wheel", "vss::vehicle::chassis::axle::row2", "Struct")
                    # Module Interfaces
                    wheel_if = get_module_interface("Wheel_If", "vss::vehicle::chassis::axle::row2")

                    class Wheel:
                        # Structs
                        left = get_datatype("Left", "vss::vehicle::chassis::axle::row2::wheel", "Struct")
                        right = get_datatype("Right", "vss::vehicle::chassis::axle::row2::wheel", "Struct")
                        # Module Interfaces
                        left_if = get_module_interface("Left_If", "vss::vehicle::chassis::axle::row2::wheel")
                        right_if = get_module_interface("Right_If", "vss::vehicle::chassis::axle::row2::wheel")

                        class Left:
                            # Structs
                            brake = get_datatype("Brake", "vss::vehicle::chassis::axle::row2::wheel::left", "Struct")
                            tire = get_datatype("Tire", "vss::vehicle::chassis::axle::row2::wheel::left", "Struct")
                            # Module Interfaces
                            brake_if = get_module_interface(
                                "Brake_If", "vss::vehicle::chassis::axle::row2::wheel::left"
                            )
                            tire_if = get_module_interface("Tire_If", "vss::vehicle::chassis::axle::row2::wheel::left")

                        class Right:
                            # Structs
                            tire = get_datatype("Tire", "vss::vehicle::chassis::axle::row2::wheel::right", "Struct")
                            brake = get_datatype("Brake", "vss::vehicle::chassis::axle::row2::wheel::right", "Struct")
                            # Module Interfaces
                            brake_if = get_module_interface(
                                "Brake_If", "vss::vehicle::chassis::axle::row2::wheel::right"
                            )
                            tire_if = get_module_interface("Tire_If", "vss::vehicle::chassis::axle::row2::wheel::right")
