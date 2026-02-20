from vaf import BaseTypes, vafpy


# Brake Service
brake_pressure = vafpy.datatypes.Struct(name="BrakePressure", namespace="datatypes")
brake_pressure.add_subelement(name="timestamp", datatype=BaseTypes.UINT64_T)
brake_pressure.add_subelement(name="value", datatype=BaseTypes.UINT8_T)
brake_pressure.add_subelement(name="status", datatype=BaseTypes.BOOL, is_optional=True)

brake_service = vafpy.ModuleInterface(name="BrakeService", namespace="af::adas_demo_app::services")
brake_service.add_data_element(name="brake_action", datatype=brake_pressure)
brake_service.add_data_element(name="brake_summand_coefficient_FieldNotifier", datatype=BaseTypes.UINT64_T)
brake_service.add_operation(name="brake_summand_coefficient_FieldGetter", out_parameter={"data": BaseTypes.UINT64_T})
brake_service.add_operation(name="brake_summand_coefficient_FieldSetter", in_parameter={"data": BaseTypes.UINT64_T})
brake_service.add_operation(
    name="SumTwoSummands",
    in_parameter={"summand_one": BaseTypes.UINT16_T, "summand_two": BaseTypes.UINT16_T},
    out_parameter={"sum": BaseTypes.UINT16_T},
)


# Object Detection List
od_struct = vafpy.datatypes.Struct(name="ObjectDetection", namespace="adas::interfaces")
od_struct.add_subelement(name="x", datatype=BaseTypes.UINT64_T)
od_struct.add_subelement(name="y", datatype=BaseTypes.UINT64_T)
od_struct.add_subelement(name="z", datatype=BaseTypes.UINT64_T)

od_list = vafpy.datatypes.Vector(
    name="ObjectDetectionList",
    namespace="adas::interfaces",
    datatype=od_struct,
)

od_interface = vafpy.ModuleInterface(
    name="ObjectDetectionListInterface",
    namespace="nsapplicationunit::nsmoduleinterface::nsobjectdetectionlist",
)
od_interface.add_data_element(name="object_detection_list", datatype=od_list)


# ImageService
uint8_vector_307200 = vafpy.datatypes.Vector(
    name="UInt8Vector", namespace="datatypes", datatype=BaseTypes.UINT8_T
)

image = vafpy.datatypes.Struct(name="Image", namespace="datatypes")
image.add_subelement(name="timestamp", datatype=BaseTypes.UINT64_T)
image.add_subelement(name="height", datatype=BaseTypes.UINT16_T)
image.add_subelement(name="width", datatype=BaseTypes.UINT16_T)
image.add_subelement(name="R", datatype=uint8_vector_307200)
image.add_subelement(name="G", datatype=uint8_vector_307200)
image.add_subelement(name="B", datatype=uint8_vector_307200)

image_service = vafpy.ModuleInterface(name="ImageService", namespace="af::adas_demo_app::services")
image_service.add_data_element(name="camera_image", datatype=image)
image_service.add_data_element(name="image_scaling_factor_FieldNotifier", datatype=BaseTypes.UINT64_T)
image_service.add_operation(name="image_scaling_factor_FieldGetter", out_parameter={"data": BaseTypes.UINT64_T})
image_service.add_operation(name="image_scaling_factor_FieldSetter", in_parameter={"data": BaseTypes.UINT64_T})
image_service.add_operation(
    name="GetImageSize", out_parameter={"width": BaseTypes.UINT16_T, "height": BaseTypes.UINT16_T}
)


# VelocityService
velocity = vafpy.datatypes.Struct(name="Velocity", namespace="datatypes")
velocity.add_subelement(name="timestamp", datatype=BaseTypes.UINT64_T)
velocity.add_subelement(name="value", datatype=BaseTypes.UINT16_T)

velocity_service = vafpy.ModuleInterface(name="VelocityService", namespace="af::adas_demo_app::services")
velocity_service.add_data_element(name="car_velocity", datatype=velocity)


# Steering Angle
steering_angle = vafpy.datatypes.Struct(name="SteeringAngle", namespace="datatypes")
steering_angle.add_subelement(name="timestamp", datatype=BaseTypes.UINT64_T)
steering_angle.add_subelement(name="value", datatype=BaseTypes.UINT16_T)

steering_angle_service = vafpy.ModuleInterface(name="SteeringAngleService", namespace="af::adas_demo_app::services")
steering_angle_service.add_data_element(name="steering_angle", datatype=steering_angle)
