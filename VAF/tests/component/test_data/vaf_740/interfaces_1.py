from vaf import BaseTypes, vafpy

# Brake Service
brake_pressure = vafpy.datatypes.Struct(name="BrakeForce", namespace="datatypes")
brake_pressure.add_subelement(name="timestamp", datatype=BaseTypes.UINT32_T)
brake_pressure.add_subelement(name="force", datatype=BaseTypes.UINT16_T)

brake_service = vafpy.ModuleInterface(name="BrakeControl", namespace="af::adas_demo_app::controls")
brake_service.add_data_element(name="brake_command", datatype=brake_pressure)
brake_service.add_data_element(name="brake_multiplier_FieldNotifier", datatype=BaseTypes.UINT32_T)
brake_service.add_operation(name="brake_multiplier_FieldGetter", out_parameter={"data": BaseTypes.UINT32_T})
brake_service.add_operation(name="brake_multiplier_FieldSetter", in_parameter={"data": BaseTypes.UINT32_T})
brake_service.add_operation(
    name="MultiplyTwoValues",
    in_parameter={"value_one": BaseTypes.UINT8_T, "value_two": BaseTypes.UINT8_T},
    out_parameter={"product": BaseTypes.UINT16_T},
)

# Object Detection List
od_struct = vafpy.datatypes.Struct(name="ObjectPosition", namespace="adas::interfaces")
od_struct.add_subelement(name="latitude", datatype=BaseTypes.FLOAT)
od_struct.add_subelement(name="longitude", datatype=BaseTypes.FLOAT)
od_struct.add_subelement(name="altitude", datatype=BaseTypes.FLOAT)

od_list = vafpy.datatypes.Vector(
    name="ObjectPositionList",
    namespace="adas::interfaces",
    datatype=od_struct,
)

od_interface = vafpy.ModuleInterface(
    name="ObjectPositionListInterface",
    namespace="nsapplicationunit::nsmoduleinterface::nsobjectpositionlist",
)
od_interface.add_data_element(name="object_position_list", datatype=od_list)

# ImageService
uint8_vector_102400 = vafpy.datatypes.Vector(name="UInt8Vector", namespace="datatypes", datatype=BaseTypes.UINT8_T)

image = vafpy.datatypes.Struct(name="Snapshot", namespace="datatypes")
image.add_subelement(name="timestamp", datatype=BaseTypes.UINT32_T)
image.add_subelement(name="height", datatype=BaseTypes.UINT8_T)
image.add_subelement(name="width", datatype=BaseTypes.UINT8_T)
image.add_subelement(name="R", datatype=uint8_vector_102400)
image.add_subelement(name="G", datatype=uint8_vector_102400)
image.add_subelement(name="B", datatype=uint8_vector_102400)

image_service = vafpy.ModuleInterface(name="SnapshotService", namespace="af::adas_demo_app::controls")
image_service.add_data_element(name="camera_snapshot", datatype=image)
image_service.add_data_element(name="snapshot_scaling_factor_FieldNotifier", datatype=BaseTypes.UINT32_T)
image_service.add_operation(name="snapshot_scaling_factor_FieldGetter", out_parameter={"data": BaseTypes.UINT32_T})
image_service.add_operation(name="snapshot_scaling_factor_FieldSetter", in_parameter={"data": BaseTypes.UINT32_T})
image_service.add_operation(
    name="GetSnapshotSize", out_parameter={"width": BaseTypes.UINT8_T, "height": BaseTypes.UINT8_T}
)

# VelocityService
velocity = vafpy.datatypes.Struct(name="Speed", namespace="datatypes")
velocity.add_subelement(name="timestamp", datatype=BaseTypes.UINT32_T)
velocity.add_subelement(name="magnitude", datatype=BaseTypes.UINT8_T)

velocity_service = vafpy.ModuleInterface(name="SpeedService", namespace="af::adas_demo_app::controls")
velocity_service.add_data_element(name="vehicle_speed", datatype=velocity)

# Steering Angle
steering_angle = vafpy.datatypes.Struct(name="WheelAngle", namespace="datatypes")
steering_angle.add_subelement(name="timestamp", datatype=BaseTypes.UINT32_T)
steering_angle.add_subelement(name="angle", datatype=BaseTypes.UINT8_T)

steering_angle_service = vafpy.ModuleInterface(name="WheelAngleService", namespace="af::adas_demo_app::controls")
steering_angle_service.add_data_element(name="wheel_angle", datatype=steering_angle)
