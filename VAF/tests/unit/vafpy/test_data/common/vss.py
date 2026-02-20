import os

from vaf.vafpy.runtime import (
    get_module_interface,
    import_model,
)

script_path = os.path.dirname(os.path.realpath(__file__))

import_model(os.path.join(script_path, "vss-derived-model.json"))


class Vss:
    # ModuleInterfaces
    vehicle_if = get_module_interface("Vehicle_If", "vss")

    class Vehicle:
        # ModuleInterfaces
        adas_if = get_module_interface("ADAS_If", "vss::vehicle")
        acceleration_if = get_module_interface("Acceleration_If", "vss::vehicle")
        angular_velocity_if = get_module_interface("AngularVelocity_If", "vss::vehicle")
        body_if = get_module_interface("Body_If", "vss::vehicle")
        cabin_if = get_module_interface("Cabin_If", "vss::vehicle")
        chassis_if = get_module_interface("Chassis_If", "vss::vehicle")
        connectivity_if = get_module_interface("Connectivity_If", "vss::vehicle")
        current_location_if = get_module_interface("CurrentLocation_If", "vss::vehicle")
        diagnostics_if = get_module_interface("Diagnostics_If", "vss::vehicle")
        driver_if = get_module_interface("Driver_If", "vss::vehicle")
        exterior_if = get_module_interface("Exterior_If", "vss::vehicle")
        low_voltage_battery_if = get_module_interface("LowVoltageBattery_If", "vss::vehicle")
        obd_if = get_module_interface("OBD_If", "vss::vehicle")
        occupant_if = get_module_interface("Occupant_If", "vss::vehicle")
        powertrain_if = get_module_interface("Powertrain_If", "vss::vehicle")
        service_if = get_module_interface("Service_If", "vss::vehicle")
        trailer_if = get_module_interface("Trailer_If", "vss::vehicle")
        vehicle_identification_if = get_module_interface("VehicleIdentification_If", "vss::vehicle")
        version_vss_if = get_module_interface("VersionVSS_If", "vss::vehicle")

        class Adas:
            # ModuleInterfaces
            abs_if = get_module_interface("ABS_If", "vss::vehicle::adas")
            cruise_control_if = get_module_interface("CruiseControl_If", "vss::vehicle::adas")
            dms_if = get_module_interface("DMS_If", "vss::vehicle::adas")
            eba_if = get_module_interface("EBA_If", "vss::vehicle::adas")
            ebd_if = get_module_interface("EBD_If", "vss::vehicle::adas")
            esc_if = get_module_interface("ESC_If", "vss::vehicle::adas")
            lane_departure_detection_if = get_module_interface("LaneDepartureDetection_If", "vss::vehicle::adas")
            obstacle_detection_if = get_module_interface("ObstacleDetection_If", "vss::vehicle::adas")
            tcs_if = get_module_interface("TCS_If", "vss::vehicle::adas")

            class Esc:
                # ModuleInterfaces
                road_friction_if = get_module_interface("RoadFriction_If", "vss::vehicle::adas::esc")

        class Body:
            # ModuleInterfaces
            hood_if = get_module_interface("Hood_If", "vss::vehicle::body")
            horn_if = get_module_interface("Horn_If", "vss::vehicle::body")
            lights_if = get_module_interface("Lights_If", "vss::vehicle::body")
            mirrors_if = get_module_interface("Mirrors_If", "vss::vehicle::body")
            raindetection_if = get_module_interface("Raindetection_If", "vss::vehicle::body")
            trunk_if = get_module_interface("Trunk_If", "vss::vehicle::body")
            windshield_if = get_module_interface("Windshield_If", "vss::vehicle::body")

            class Lights:
                # ModuleInterfaces
                backup_if = get_module_interface("Backup_If", "vss::vehicle::body::lights")
                beam_if = get_module_interface("Beam_If", "vss::vehicle::body::lights")
                brake_if = get_module_interface("Brake_If", "vss::vehicle::body::lights")
                direction_indicator_if = get_module_interface("DirectionIndicator_If", "vss::vehicle::body::lights")
                fog_if = get_module_interface("Fog_If", "vss::vehicle::body::lights")
                hazard_if = get_module_interface("Hazard_If", "vss::vehicle::body::lights")
                license_plate_if = get_module_interface("LicensePlate_If", "vss::vehicle::body::lights")
                parking_if = get_module_interface("Parking_If", "vss::vehicle::body::lights")
                running_if = get_module_interface("Running_If", "vss::vehicle::body::lights")

                class Beam:
                    # ModuleInterfaces
                    high_if = get_module_interface("High_If", "vss::vehicle::body::lights::beam")
                    low_if = get_module_interface("Low_If", "vss::vehicle::body::lights::beam")

                class Directionindicator:
                    # ModuleInterfaces
                    left_if = get_module_interface("Left_If", "vss::vehicle::body::lights::directionindicator")
                    right_if = get_module_interface("Right_If", "vss::vehicle::body::lights::directionindicator")

                class Fog:
                    # ModuleInterfaces
                    front_if = get_module_interface("Front_If", "vss::vehicle::body::lights::fog")
                    rear_if = get_module_interface("Rear_If", "vss::vehicle::body::lights::fog")

            class Mirrors:
                # ModuleInterfaces
                driver_side_if = get_module_interface("DriverSide_If", "vss::vehicle::body::mirrors")
                passenger_side_if = get_module_interface("PassengerSide_If", "vss::vehicle::body::mirrors")

            class Trunk:
                # ModuleInterfaces
                front_if = get_module_interface("Front_If", "vss::vehicle::body::trunk")
                rear_if = get_module_interface("Rear_If", "vss::vehicle::body::trunk")

            class Windshield:
                # ModuleInterfaces
                front_if = get_module_interface("Front_If", "vss::vehicle::body::windshield")
                rear_if = get_module_interface("Rear_If", "vss::vehicle::body::windshield")

                class Front:
                    # ModuleInterfaces
                    washer_fluid_if = get_module_interface("WasherFluid_If", "vss::vehicle::body::windshield::front")
                    wiping_if = get_module_interface("Wiping_If", "vss::vehicle::body::windshield::front")

                    class Wiping:
                        # ModuleInterfaces
                        system_if = get_module_interface("System_If", "vss::vehicle::body::windshield::front::wiping")

                class Rear:
                    # ModuleInterfaces
                    washer_fluid_if = get_module_interface("WasherFluid_If", "vss::vehicle::body::windshield::rear")
                    wiping_if = get_module_interface("Wiping_If", "vss::vehicle::body::windshield::rear")

                    class Wiping:
                        # ModuleInterfaces
                        system_if = get_module_interface("System_If", "vss::vehicle::body::windshield::rear::wiping")

        class Cabin:
            # ModuleInterfaces
            convertible_if = get_module_interface("Convertible_If", "vss::vehicle::cabin")
            door_if = get_module_interface("Door_If", "vss::vehicle::cabin")
            hvac_if = get_module_interface("HVAC_If", "vss::vehicle::cabin")
            infotainment_if = get_module_interface("Infotainment_If", "vss::vehicle::cabin")
            light_if = get_module_interface("Light_If", "vss::vehicle::cabin")
            rear_shade_if = get_module_interface("RearShade_If", "vss::vehicle::cabin")
            rearview_mirror_if = get_module_interface("RearviewMirror_If", "vss::vehicle::cabin")
            seat_if = get_module_interface("Seat_If", "vss::vehicle::cabin")
            sunroof_if = get_module_interface("Sunroof_If", "vss::vehicle::cabin")

            class Door:
                # ModuleInterfaces
                row1_if = get_module_interface("Row1_If", "vss::vehicle::cabin::door")
                row2_if = get_module_interface("Row2_If", "vss::vehicle::cabin::door")

                class Row1:
                    # ModuleInterfaces
                    driver_side_if = get_module_interface("DriverSide_If", "vss::vehicle::cabin::door::row1")
                    passenger_side_if = get_module_interface("PassengerSide_If", "vss::vehicle::cabin::door::row1")

                    class Driverside:
                        # ModuleInterfaces
                        shade_if = get_module_interface("Shade_If", "vss::vehicle::cabin::door::row1::driverside")
                        window_if = get_module_interface("Window_If", "vss::vehicle::cabin::door::row1::driverside")

                    class Passengerside:
                        # ModuleInterfaces
                        shade_if = get_module_interface("Shade_If", "vss::vehicle::cabin::door::row1::passengerside")
                        window_if = get_module_interface("Window_If", "vss::vehicle::cabin::door::row1::passengerside")

                class Row2:
                    # ModuleInterfaces
                    driver_side_if = get_module_interface("DriverSide_If", "vss::vehicle::cabin::door::row2")
                    passenger_side_if = get_module_interface("PassengerSide_If", "vss::vehicle::cabin::door::row2")

                    class Driverside:
                        # ModuleInterfaces
                        shade_if = get_module_interface("Shade_If", "vss::vehicle::cabin::door::row2::driverside")
                        window_if = get_module_interface("Window_If", "vss::vehicle::cabin::door::row2::driverside")

                    class Passengerside:
                        # ModuleInterfaces
                        shade_if = get_module_interface("Shade_If", "vss::vehicle::cabin::door::row2::passengerside")
                        window_if = get_module_interface("Window_If", "vss::vehicle::cabin::door::row2::passengerside")

            class Hvac:
                # ModuleInterfaces
                station_if = get_module_interface("Station_If", "vss::vehicle::cabin::hvac")

                class Station:
                    # ModuleInterfaces
                    row1_if = get_module_interface("Row1_If", "vss::vehicle::cabin::hvac::station")
                    row2_if = get_module_interface("Row2_If", "vss::vehicle::cabin::hvac::station")
                    row3_if = get_module_interface("Row3_If", "vss::vehicle::cabin::hvac::station")
                    row4_if = get_module_interface("Row4_If", "vss::vehicle::cabin::hvac::station")

                    class Row1:
                        # ModuleInterfaces
                        driver_if = get_module_interface("Driver_If", "vss::vehicle::cabin::hvac::station::row1")
                        passenger_if = get_module_interface("Passenger_If", "vss::vehicle::cabin::hvac::station::row1")

                    class Row2:
                        # ModuleInterfaces
                        driver_if = get_module_interface("Driver_If", "vss::vehicle::cabin::hvac::station::row2")
                        passenger_if = get_module_interface("Passenger_If", "vss::vehicle::cabin::hvac::station::row2")

                    class Row3:
                        # ModuleInterfaces
                        driver_if = get_module_interface("Driver_If", "vss::vehicle::cabin::hvac::station::row3")
                        passenger_if = get_module_interface("Passenger_If", "vss::vehicle::cabin::hvac::station::row3")

                    class Row4:
                        # ModuleInterfaces
                        driver_if = get_module_interface("Driver_If", "vss::vehicle::cabin::hvac::station::row4")
                        passenger_if = get_module_interface("Passenger_If", "vss::vehicle::cabin::hvac::station::row4")

            class Infotainment:
                # ModuleInterfaces
                hmi_if = get_module_interface("HMI_If", "vss::vehicle::cabin::infotainment")
                media_if = get_module_interface("Media_If", "vss::vehicle::cabin::infotainment")
                navigation_if = get_module_interface("Navigation_If", "vss::vehicle::cabin::infotainment")
                smartphone_projection_if = get_module_interface(
                    "SmartphoneProjection_If", "vss::vehicle::cabin::infotainment"
                )
                smartphone_screen_mirroring_if = get_module_interface(
                    "SmartphoneScreenMirroring_If", "vss::vehicle::cabin::infotainment"
                )

                class Media:
                    # ModuleInterfaces
                    played_if = get_module_interface("Played_If", "vss::vehicle::cabin::infotainment::media")

                class Navigation:
                    # ModuleInterfaces
                    destination_set_if = get_module_interface(
                        "DestinationSet_If", "vss::vehicle::cabin::infotainment::navigation"
                    )
                    map_if = get_module_interface("Map_If", "vss::vehicle::cabin::infotainment::navigation")

            class Light:
                # ModuleInterfaces
                ambient_light_if = get_module_interface("AmbientLight_If", "vss::vehicle::cabin::light")
                interactive_light_bar_if = get_module_interface("InteractiveLightBar_If", "vss::vehicle::cabin::light")
                spotlight_if = get_module_interface("Spotlight_If", "vss::vehicle::cabin::light")

                class Ambientlight:
                    # ModuleInterfaces
                    row1_if = get_module_interface("Row1_If", "vss::vehicle::cabin::light::ambientlight")
                    row2_if = get_module_interface("Row2_If", "vss::vehicle::cabin::light::ambientlight")

                    class Row1:
                        # ModuleInterfaces
                        driver_side_if = get_module_interface(
                            "DriverSide_If", "vss::vehicle::cabin::light::ambientlight::row1"
                        )
                        passenger_side_if = get_module_interface(
                            "PassengerSide_If", "vss::vehicle::cabin::light::ambientlight::row1"
                        )

                    class Row2:
                        # ModuleInterfaces
                        driver_side_if = get_module_interface(
                            "DriverSide_If", "vss::vehicle::cabin::light::ambientlight::row2"
                        )
                        passenger_side_if = get_module_interface(
                            "PassengerSide_If", "vss::vehicle::cabin::light::ambientlight::row2"
                        )

                class Spotlight:
                    # ModuleInterfaces
                    row1_if = get_module_interface("Row1_If", "vss::vehicle::cabin::light::spotlight")
                    row2_if = get_module_interface("Row2_If", "vss::vehicle::cabin::light::spotlight")
                    row3_if = get_module_interface("Row3_If", "vss::vehicle::cabin::light::spotlight")
                    row4_if = get_module_interface("Row4_If", "vss::vehicle::cabin::light::spotlight")

                    class Row1:
                        # ModuleInterfaces
                        driver_side_if = get_module_interface(
                            "DriverSide_If", "vss::vehicle::cabin::light::spotlight::row1"
                        )
                        passenger_side_if = get_module_interface(
                            "PassengerSide_If", "vss::vehicle::cabin::light::spotlight::row1"
                        )

                    class Row2:
                        # ModuleInterfaces
                        driver_side_if = get_module_interface(
                            "DriverSide_If", "vss::vehicle::cabin::light::spotlight::row2"
                        )
                        passenger_side_if = get_module_interface(
                            "PassengerSide_If", "vss::vehicle::cabin::light::spotlight::row2"
                        )

                    class Row3:
                        # ModuleInterfaces
                        driver_side_if = get_module_interface(
                            "DriverSide_If", "vss::vehicle::cabin::light::spotlight::row3"
                        )
                        passenger_side_if = get_module_interface(
                            "PassengerSide_If", "vss::vehicle::cabin::light::spotlight::row3"
                        )

                    class Row4:
                        # ModuleInterfaces
                        driver_side_if = get_module_interface(
                            "DriverSide_If", "vss::vehicle::cabin::light::spotlight::row4"
                        )
                        passenger_side_if = get_module_interface(
                            "PassengerSide_If", "vss::vehicle::cabin::light::spotlight::row4"
                        )

            class Seat:
                # ModuleInterfaces
                row1_if = get_module_interface("Row1_If", "vss::vehicle::cabin::seat")
                row2_if = get_module_interface("Row2_If", "vss::vehicle::cabin::seat")

                class Row1:
                    # ModuleInterfaces
                    driver_side_if = get_module_interface("DriverSide_If", "vss::vehicle::cabin::seat::row1")
                    middle_if = get_module_interface("Middle_If", "vss::vehicle::cabin::seat::row1")
                    passenger_side_if = get_module_interface("PassengerSide_If", "vss::vehicle::cabin::seat::row1")

                    class Driverside:
                        # ModuleInterfaces
                        airbag_if = get_module_interface("Airbag_If", "vss::vehicle::cabin::seat::row1::driverside")
                        backrest_if = get_module_interface("Backrest_If", "vss::vehicle::cabin::seat::row1::driverside")
                        headrest_if = get_module_interface("Headrest_If", "vss::vehicle::cabin::seat::row1::driverside")
                        occupant_if = get_module_interface("Occupant_If", "vss::vehicle::cabin::seat::row1::driverside")
                        seating_if = get_module_interface("Seating_If", "vss::vehicle::cabin::seat::row1::driverside")
                        switch_if = get_module_interface("Switch_If", "vss::vehicle::cabin::seat::row1::driverside")

                        class Backrest:
                            # ModuleInterfaces
                            lumbar_if = get_module_interface(
                                "Lumbar_If", "vss::vehicle::cabin::seat::row1::driverside::backrest"
                            )
                            side_bolster_if = get_module_interface(
                                "SideBolster_If", "vss::vehicle::cabin::seat::row1::driverside::backrest"
                            )

                        class Occupant:
                            # ModuleInterfaces
                            identifier_if = get_module_interface(
                                "Identifier_If", "vss::vehicle::cabin::seat::row1::driverside::occupant"
                            )

                        class Switch:
                            # ModuleInterfaces
                            backrest_if = get_module_interface(
                                "Backrest_If", "vss::vehicle::cabin::seat::row1::driverside::switch"
                            )
                            headrest_if = get_module_interface(
                                "Headrest_If", "vss::vehicle::cabin::seat::row1::driverside::switch"
                            )
                            massage_if = get_module_interface(
                                "Massage_If", "vss::vehicle::cabin::seat::row1::driverside::switch"
                            )
                            seating_if = get_module_interface(
                                "Seating_If", "vss::vehicle::cabin::seat::row1::driverside::switch"
                            )

                            class Backrest:
                                # ModuleInterfaces
                                lumbar_if = get_module_interface(
                                    "Lumbar_If", "vss::vehicle::cabin::seat::row1::driverside::switch::backrest"
                                )
                                side_bolster_if = get_module_interface(
                                    "SideBolster_If", "vss::vehicle::cabin::seat::row1::driverside::switch::backrest"
                                )

                    class Middle:
                        # ModuleInterfaces
                        airbag_if = get_module_interface("Airbag_If", "vss::vehicle::cabin::seat::row1::middle")
                        backrest_if = get_module_interface("Backrest_If", "vss::vehicle::cabin::seat::row1::middle")
                        headrest_if = get_module_interface("Headrest_If", "vss::vehicle::cabin::seat::row1::middle")
                        occupant_if = get_module_interface("Occupant_If", "vss::vehicle::cabin::seat::row1::middle")
                        seating_if = get_module_interface("Seating_If", "vss::vehicle::cabin::seat::row1::middle")
                        switch_if = get_module_interface("Switch_If", "vss::vehicle::cabin::seat::row1::middle")

                        class Backrest:
                            # ModuleInterfaces
                            lumbar_if = get_module_interface(
                                "Lumbar_If", "vss::vehicle::cabin::seat::row1::middle::backrest"
                            )
                            side_bolster_if = get_module_interface(
                                "SideBolster_If", "vss::vehicle::cabin::seat::row1::middle::backrest"
                            )

                        class Occupant:
                            # ModuleInterfaces
                            identifier_if = get_module_interface(
                                "Identifier_If", "vss::vehicle::cabin::seat::row1::middle::occupant"
                            )

                        class Switch:
                            # ModuleInterfaces
                            backrest_if = get_module_interface(
                                "Backrest_If", "vss::vehicle::cabin::seat::row1::middle::switch"
                            )
                            headrest_if = get_module_interface(
                                "Headrest_If", "vss::vehicle::cabin::seat::row1::middle::switch"
                            )
                            massage_if = get_module_interface(
                                "Massage_If", "vss::vehicle::cabin::seat::row1::middle::switch"
                            )
                            seating_if = get_module_interface(
                                "Seating_If", "vss::vehicle::cabin::seat::row1::middle::switch"
                            )

                            class Backrest:
                                # ModuleInterfaces
                                lumbar_if = get_module_interface(
                                    "Lumbar_If", "vss::vehicle::cabin::seat::row1::middle::switch::backrest"
                                )
                                side_bolster_if = get_module_interface(
                                    "SideBolster_If", "vss::vehicle::cabin::seat::row1::middle::switch::backrest"
                                )

                    class Passengerside:
                        # ModuleInterfaces
                        airbag_if = get_module_interface("Airbag_If", "vss::vehicle::cabin::seat::row1::passengerside")
                        backrest_if = get_module_interface(
                            "Backrest_If", "vss::vehicle::cabin::seat::row1::passengerside"
                        )
                        headrest_if = get_module_interface(
                            "Headrest_If", "vss::vehicle::cabin::seat::row1::passengerside"
                        )
                        occupant_if = get_module_interface(
                            "Occupant_If", "vss::vehicle::cabin::seat::row1::passengerside"
                        )
                        seating_if = get_module_interface(
                            "Seating_If", "vss::vehicle::cabin::seat::row1::passengerside"
                        )
                        switch_if = get_module_interface("Switch_If", "vss::vehicle::cabin::seat::row1::passengerside")

                        class Backrest:
                            # ModuleInterfaces
                            lumbar_if = get_module_interface(
                                "Lumbar_If", "vss::vehicle::cabin::seat::row1::passengerside::backrest"
                            )
                            side_bolster_if = get_module_interface(
                                "SideBolster_If", "vss::vehicle::cabin::seat::row1::passengerside::backrest"
                            )

                        class Occupant:
                            # ModuleInterfaces
                            identifier_if = get_module_interface(
                                "Identifier_If", "vss::vehicle::cabin::seat::row1::passengerside::occupant"
                            )

                        class Switch:
                            # ModuleInterfaces
                            backrest_if = get_module_interface(
                                "Backrest_If", "vss::vehicle::cabin::seat::row1::passengerside::switch"
                            )
                            headrest_if = get_module_interface(
                                "Headrest_If", "vss::vehicle::cabin::seat::row1::passengerside::switch"
                            )
                            massage_if = get_module_interface(
                                "Massage_If", "vss::vehicle::cabin::seat::row1::passengerside::switch"
                            )
                            seating_if = get_module_interface(
                                "Seating_If", "vss::vehicle::cabin::seat::row1::passengerside::switch"
                            )

                            class Backrest:
                                # ModuleInterfaces
                                lumbar_if = get_module_interface(
                                    "Lumbar_If", "vss::vehicle::cabin::seat::row1::passengerside::switch::backrest"
                                )
                                side_bolster_if = get_module_interface(
                                    "SideBolster_If", "vss::vehicle::cabin::seat::row1::passengerside::switch::backrest"
                                )

                class Row2:
                    # ModuleInterfaces
                    driver_side_if = get_module_interface("DriverSide_If", "vss::vehicle::cabin::seat::row2")
                    middle_if = get_module_interface("Middle_If", "vss::vehicle::cabin::seat::row2")
                    passenger_side_if = get_module_interface("PassengerSide_If", "vss::vehicle::cabin::seat::row2")

                    class Driverside:
                        # ModuleInterfaces
                        airbag_if = get_module_interface("Airbag_If", "vss::vehicle::cabin::seat::row2::driverside")
                        backrest_if = get_module_interface("Backrest_If", "vss::vehicle::cabin::seat::row2::driverside")
                        headrest_if = get_module_interface("Headrest_If", "vss::vehicle::cabin::seat::row2::driverside")
                        occupant_if = get_module_interface("Occupant_If", "vss::vehicle::cabin::seat::row2::driverside")
                        seating_if = get_module_interface("Seating_If", "vss::vehicle::cabin::seat::row2::driverside")
                        switch_if = get_module_interface("Switch_If", "vss::vehicle::cabin::seat::row2::driverside")

                        class Backrest:
                            # ModuleInterfaces
                            lumbar_if = get_module_interface(
                                "Lumbar_If", "vss::vehicle::cabin::seat::row2::driverside::backrest"
                            )
                            side_bolster_if = get_module_interface(
                                "SideBolster_If", "vss::vehicle::cabin::seat::row2::driverside::backrest"
                            )

                        class Occupant:
                            # ModuleInterfaces
                            identifier_if = get_module_interface(
                                "Identifier_If", "vss::vehicle::cabin::seat::row2::driverside::occupant"
                            )

                        class Switch:
                            # ModuleInterfaces
                            backrest_if = get_module_interface(
                                "Backrest_If", "vss::vehicle::cabin::seat::row2::driverside::switch"
                            )
                            headrest_if = get_module_interface(
                                "Headrest_If", "vss::vehicle::cabin::seat::row2::driverside::switch"
                            )
                            massage_if = get_module_interface(
                                "Massage_If", "vss::vehicle::cabin::seat::row2::driverside::switch"
                            )
                            seating_if = get_module_interface(
                                "Seating_If", "vss::vehicle::cabin::seat::row2::driverside::switch"
                            )

                            class Backrest:
                                # ModuleInterfaces
                                lumbar_if = get_module_interface(
                                    "Lumbar_If", "vss::vehicle::cabin::seat::row2::driverside::switch::backrest"
                                )
                                side_bolster_if = get_module_interface(
                                    "SideBolster_If", "vss::vehicle::cabin::seat::row2::driverside::switch::backrest"
                                )

                    class Middle:
                        # ModuleInterfaces
                        airbag_if = get_module_interface("Airbag_If", "vss::vehicle::cabin::seat::row2::middle")
                        backrest_if = get_module_interface("Backrest_If", "vss::vehicle::cabin::seat::row2::middle")
                        headrest_if = get_module_interface("Headrest_If", "vss::vehicle::cabin::seat::row2::middle")
                        occupant_if = get_module_interface("Occupant_If", "vss::vehicle::cabin::seat::row2::middle")
                        seating_if = get_module_interface("Seating_If", "vss::vehicle::cabin::seat::row2::middle")
                        switch_if = get_module_interface("Switch_If", "vss::vehicle::cabin::seat::row2::middle")

                        class Backrest:
                            # ModuleInterfaces
                            lumbar_if = get_module_interface(
                                "Lumbar_If", "vss::vehicle::cabin::seat::row2::middle::backrest"
                            )
                            side_bolster_if = get_module_interface(
                                "SideBolster_If", "vss::vehicle::cabin::seat::row2::middle::backrest"
                            )

                        class Occupant:
                            # ModuleInterfaces
                            identifier_if = get_module_interface(
                                "Identifier_If", "vss::vehicle::cabin::seat::row2::middle::occupant"
                            )

                        class Switch:
                            # ModuleInterfaces
                            backrest_if = get_module_interface(
                                "Backrest_If", "vss::vehicle::cabin::seat::row2::middle::switch"
                            )
                            headrest_if = get_module_interface(
                                "Headrest_If", "vss::vehicle::cabin::seat::row2::middle::switch"
                            )
                            massage_if = get_module_interface(
                                "Massage_If", "vss::vehicle::cabin::seat::row2::middle::switch"
                            )
                            seating_if = get_module_interface(
                                "Seating_If", "vss::vehicle::cabin::seat::row2::middle::switch"
                            )

                            class Backrest:
                                # ModuleInterfaces
                                lumbar_if = get_module_interface(
                                    "Lumbar_If", "vss::vehicle::cabin::seat::row2::middle::switch::backrest"
                                )
                                side_bolster_if = get_module_interface(
                                    "SideBolster_If", "vss::vehicle::cabin::seat::row2::middle::switch::backrest"
                                )

                    class Passengerside:
                        # ModuleInterfaces
                        airbag_if = get_module_interface("Airbag_If", "vss::vehicle::cabin::seat::row2::passengerside")
                        backrest_if = get_module_interface(
                            "Backrest_If", "vss::vehicle::cabin::seat::row2::passengerside"
                        )
                        headrest_if = get_module_interface(
                            "Headrest_If", "vss::vehicle::cabin::seat::row2::passengerside"
                        )
                        occupant_if = get_module_interface(
                            "Occupant_If", "vss::vehicle::cabin::seat::row2::passengerside"
                        )
                        seating_if = get_module_interface(
                            "Seating_If", "vss::vehicle::cabin::seat::row2::passengerside"
                        )
                        switch_if = get_module_interface("Switch_If", "vss::vehicle::cabin::seat::row2::passengerside")

                        class Backrest:
                            # ModuleInterfaces
                            lumbar_if = get_module_interface(
                                "Lumbar_If", "vss::vehicle::cabin::seat::row2::passengerside::backrest"
                            )
                            side_bolster_if = get_module_interface(
                                "SideBolster_If", "vss::vehicle::cabin::seat::row2::passengerside::backrest"
                            )

                        class Occupant:
                            # ModuleInterfaces
                            identifier_if = get_module_interface(
                                "Identifier_If", "vss::vehicle::cabin::seat::row2::passengerside::occupant"
                            )

                        class Switch:
                            # ModuleInterfaces
                            backrest_if = get_module_interface(
                                "Backrest_If", "vss::vehicle::cabin::seat::row2::passengerside::switch"
                            )
                            headrest_if = get_module_interface(
                                "Headrest_If", "vss::vehicle::cabin::seat::row2::passengerside::switch"
                            )
                            massage_if = get_module_interface(
                                "Massage_If", "vss::vehicle::cabin::seat::row2::passengerside::switch"
                            )
                            seating_if = get_module_interface(
                                "Seating_If", "vss::vehicle::cabin::seat::row2::passengerside::switch"
                            )

                            class Backrest:
                                # ModuleInterfaces
                                lumbar_if = get_module_interface(
                                    "Lumbar_If", "vss::vehicle::cabin::seat::row2::passengerside::switch::backrest"
                                )
                                side_bolster_if = get_module_interface(
                                    "SideBolster_If", "vss::vehicle::cabin::seat::row2::passengerside::switch::backrest"
                                )

            class Sunroof:
                # ModuleInterfaces
                shade_if = get_module_interface("Shade_If", "vss::vehicle::cabin::sunroof")

        class Chassis:
            # ModuleInterfaces
            accelerator_if = get_module_interface("Accelerator_If", "vss::vehicle::chassis")
            axle_if = get_module_interface("Axle_If", "vss::vehicle::chassis")
            brake_if = get_module_interface("Brake_If", "vss::vehicle::chassis")
            parking_brake_if = get_module_interface("ParkingBrake_If", "vss::vehicle::chassis")
            steering_wheel_if = get_module_interface("SteeringWheel_If", "vss::vehicle::chassis")

            class Axle:
                # ModuleInterfaces
                row1_if = get_module_interface("Row1_If", "vss::vehicle::chassis::axle")
                row2_if = get_module_interface("Row2_If", "vss::vehicle::chassis::axle")

                class Row1:
                    # ModuleInterfaces
                    wheel_if = get_module_interface("Wheel_If", "vss::vehicle::chassis::axle::row1")

                    class Wheel:
                        # ModuleInterfaces
                        left_if = get_module_interface("Left_If", "vss::vehicle::chassis::axle::row1::wheel")
                        right_if = get_module_interface("Right_If", "vss::vehicle::chassis::axle::row1::wheel")

                        class Left:
                            # ModuleInterfaces
                            brake_if = get_module_interface(
                                "Brake_If", "vss::vehicle::chassis::axle::row1::wheel::left"
                            )
                            tire_if = get_module_interface("Tire_If", "vss::vehicle::chassis::axle::row1::wheel::left")

                        class Right:
                            # ModuleInterfaces
                            brake_if = get_module_interface(
                                "Brake_If", "vss::vehicle::chassis::axle::row1::wheel::right"
                            )
                            tire_if = get_module_interface("Tire_If", "vss::vehicle::chassis::axle::row1::wheel::right")

                class Row2:
                    # ModuleInterfaces
                    wheel_if = get_module_interface("Wheel_If", "vss::vehicle::chassis::axle::row2")

                    class Wheel:
                        # ModuleInterfaces
                        left_if = get_module_interface("Left_If", "vss::vehicle::chassis::axle::row2::wheel")
                        right_if = get_module_interface("Right_If", "vss::vehicle::chassis::axle::row2::wheel")

                        class Left:
                            # ModuleInterfaces
                            brake_if = get_module_interface(
                                "Brake_If", "vss::vehicle::chassis::axle::row2::wheel::left"
                            )
                            tire_if = get_module_interface("Tire_If", "vss::vehicle::chassis::axle::row2::wheel::left")

                        class Right:
                            # ModuleInterfaces
                            brake_if = get_module_interface(
                                "Brake_If", "vss::vehicle::chassis::axle::row2::wheel::right"
                            )
                            tire_if = get_module_interface("Tire_If", "vss::vehicle::chassis::axle::row2::wheel::right")

        class Currentlocation:
            # ModuleInterfaces
            gnss_receiver_if = get_module_interface("GNSSReceiver_If", "vss::vehicle::currentlocation")

            class Gnssreceiver:
                # ModuleInterfaces
                mounting_position_if = get_module_interface(
                    "MountingPosition_If", "vss::vehicle::currentlocation::gnssreceiver"
                )

        class Driver:
            # ModuleInterfaces
            identifier_if = get_module_interface("Identifier_If", "vss::vehicle::driver")

        class Obd:
            # ModuleInterfaces
            catalyst_if = get_module_interface("Catalyst_If", "vss::vehicle::obd")
            drive_cycle_status_if = get_module_interface("DriveCycleStatus_If", "vss::vehicle::obd")
            o2_wr_if = get_module_interface("O2WR_If", "vss::vehicle::obd")
            o2_if = get_module_interface("O2_If", "vss::vehicle::obd")
            status_if = get_module_interface("Status_If", "vss::vehicle::obd")

            class Catalyst:
                # ModuleInterfaces
                bank1_if = get_module_interface("Bank1_If", "vss::vehicle::obd::catalyst")
                bank2_if = get_module_interface("Bank2_If", "vss::vehicle::obd::catalyst")

            class O2:
                # ModuleInterfaces
                sensor1_if = get_module_interface("Sensor1_If", "vss::vehicle::obd::o2")
                sensor2_if = get_module_interface("Sensor2_If", "vss::vehicle::obd::o2")
                sensor3_if = get_module_interface("Sensor3_If", "vss::vehicle::obd::o2")
                sensor4_if = get_module_interface("Sensor4_If", "vss::vehicle::obd::o2")
                sensor5_if = get_module_interface("Sensor5_If", "vss::vehicle::obd::o2")
                sensor6_if = get_module_interface("Sensor6_If", "vss::vehicle::obd::o2")
                sensor7_if = get_module_interface("Sensor7_If", "vss::vehicle::obd::o2")
                sensor8_if = get_module_interface("Sensor8_If", "vss::vehicle::obd::o2")

            class O2Wr:
                # ModuleInterfaces
                sensor1_if = get_module_interface("Sensor1_If", "vss::vehicle::obd::o2wr")
                sensor2_if = get_module_interface("Sensor2_If", "vss::vehicle::obd::o2wr")
                sensor3_if = get_module_interface("Sensor3_If", "vss::vehicle::obd::o2wr")
                sensor4_if = get_module_interface("Sensor4_If", "vss::vehicle::obd::o2wr")
                sensor5_if = get_module_interface("Sensor5_If", "vss::vehicle::obd::o2wr")
                sensor6_if = get_module_interface("Sensor6_If", "vss::vehicle::obd::o2wr")
                sensor7_if = get_module_interface("Sensor7_If", "vss::vehicle::obd::o2wr")
                sensor8_if = get_module_interface("Sensor8_If", "vss::vehicle::obd::o2wr")

        class Occupant:
            # ModuleInterfaces
            row1_if = get_module_interface("Row1_If", "vss::vehicle::occupant")
            row2_if = get_module_interface("Row2_If", "vss::vehicle::occupant")

            class Row1:
                # ModuleInterfaces
                driver_side_if = get_module_interface("DriverSide_If", "vss::vehicle::occupant::row1")
                middle_if = get_module_interface("Middle_If", "vss::vehicle::occupant::row1")
                passenger_side_if = get_module_interface("PassengerSide_If", "vss::vehicle::occupant::row1")

                class Driverside:
                    # ModuleInterfaces
                    head_position_if = get_module_interface(
                        "HeadPosition_If", "vss::vehicle::occupant::row1::driverside"
                    )
                    identifier_if = get_module_interface("Identifier_If", "vss::vehicle::occupant::row1::driverside")
                    mid_eye_gaze_if = get_module_interface("MidEyeGaze_If", "vss::vehicle::occupant::row1::driverside")

                class Middle:
                    # ModuleInterfaces
                    head_position_if = get_module_interface("HeadPosition_If", "vss::vehicle::occupant::row1::middle")
                    identifier_if = get_module_interface("Identifier_If", "vss::vehicle::occupant::row1::middle")
                    mid_eye_gaze_if = get_module_interface("MidEyeGaze_If", "vss::vehicle::occupant::row1::middle")

                class Passengerside:
                    # ModuleInterfaces
                    head_position_if = get_module_interface(
                        "HeadPosition_If", "vss::vehicle::occupant::row1::passengerside"
                    )
                    identifier_if = get_module_interface("Identifier_If", "vss::vehicle::occupant::row1::passengerside")
                    mid_eye_gaze_if = get_module_interface(
                        "MidEyeGaze_If", "vss::vehicle::occupant::row1::passengerside"
                    )

            class Row2:
                # ModuleInterfaces
                driver_side_if = get_module_interface("DriverSide_If", "vss::vehicle::occupant::row2")
                middle_if = get_module_interface("Middle_If", "vss::vehicle::occupant::row2")
                passenger_side_if = get_module_interface("PassengerSide_If", "vss::vehicle::occupant::row2")

                class Driverside:
                    # ModuleInterfaces
                    head_position_if = get_module_interface(
                        "HeadPosition_If", "vss::vehicle::occupant::row2::driverside"
                    )
                    identifier_if = get_module_interface("Identifier_If", "vss::vehicle::occupant::row2::driverside")
                    mid_eye_gaze_if = get_module_interface("MidEyeGaze_If", "vss::vehicle::occupant::row2::driverside")

                class Middle:
                    # ModuleInterfaces
                    head_position_if = get_module_interface("HeadPosition_If", "vss::vehicle::occupant::row2::middle")
                    identifier_if = get_module_interface("Identifier_If", "vss::vehicle::occupant::row2::middle")
                    mid_eye_gaze_if = get_module_interface("MidEyeGaze_If", "vss::vehicle::occupant::row2::middle")

                class Passengerside:
                    # ModuleInterfaces
                    head_position_if = get_module_interface(
                        "HeadPosition_If", "vss::vehicle::occupant::row2::passengerside"
                    )
                    identifier_if = get_module_interface("Identifier_If", "vss::vehicle::occupant::row2::passengerside")
                    mid_eye_gaze_if = get_module_interface(
                        "MidEyeGaze_If", "vss::vehicle::occupant::row2::passengerside"
                    )

        class Powertrain:
            # ModuleInterfaces
            combustion_engine_if = get_module_interface("CombustionEngine_If", "vss::vehicle::powertrain")
            electric_motor_if = get_module_interface("ElectricMotor_If", "vss::vehicle::powertrain")
            fuel_system_if = get_module_interface("FuelSystem_If", "vss::vehicle::powertrain")
            traction_battery_if = get_module_interface("TractionBattery_If", "vss::vehicle::powertrain")
            transmission_if = get_module_interface("Transmission_If", "vss::vehicle::powertrain")

            class Combustionengine:
                # ModuleInterfaces
                diesel_exhaust_fluid_if = get_module_interface(
                    "DieselExhaustFluid_If", "vss::vehicle::powertrain::combustionengine"
                )
                diesel_particulate_filter_if = get_module_interface(
                    "DieselParticulateFilter_If", "vss::vehicle::powertrain::combustionengine"
                )
                engine_coolant_if = get_module_interface(
                    "EngineCoolant_If", "vss::vehicle::powertrain::combustionengine"
                )
                engine_oil_if = get_module_interface("EngineOil_If", "vss::vehicle::powertrain::combustionengine")

            class Electricmotor:
                # ModuleInterfaces
                engine_coolant_if = get_module_interface("EngineCoolant_If", "vss::vehicle::powertrain::electricmotor")

            class Tractionbattery:
                # ModuleInterfaces
                battery_conditioning_if = get_module_interface(
                    "BatteryConditioning_If", "vss::vehicle::powertrain::tractionbattery"
                )
                cell_voltage_if = get_module_interface("CellVoltage_If", "vss::vehicle::powertrain::tractionbattery")
                charging_if = get_module_interface("Charging_If", "vss::vehicle::powertrain::tractionbattery")
                dcdc_if = get_module_interface("DCDC_If", "vss::vehicle::powertrain::tractionbattery")
                state_of_charge_if = get_module_interface(
                    "StateOfCharge_If", "vss::vehicle::powertrain::tractionbattery"
                )
                temperature_if = get_module_interface("Temperature_If", "vss::vehicle::powertrain::tractionbattery")

                class Charging:
                    # ModuleInterfaces
                    charge_current_if = get_module_interface(
                        "ChargeCurrent_If", "vss::vehicle::powertrain::tractionbattery::charging"
                    )
                    charge_voltage_if = get_module_interface(
                        "ChargeVoltage_If", "vss::vehicle::powertrain::tractionbattery::charging"
                    )
                    location_if = get_module_interface(
                        "Location_If", "vss::vehicle::powertrain::tractionbattery::charging"
                    )
                    maximum_charging_current_if = get_module_interface(
                        "MaximumChargingCurrent_If", "vss::vehicle::powertrain::tractionbattery::charging"
                    )
                    timer_if = get_module_interface("Timer_If", "vss::vehicle::powertrain::tractionbattery::charging")
