/*!********************************************************************************************************************
 *  COPYRIGHT
 *  -------------------------------------------------------------------------------------------------------------------
 *  \verbatim
 *  Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
 *  SPDX-License-Identifier: Apache-2.0
 *  \endverbatim
 *  -------------------------------------------------------------------------------------------------------------------
 *  FILE DESCRIPTION
 *  -----------------------------------------------------------------------------------------------------------------*/
/*!        \file  sensor_fusion.cpp
 *         \brief
 *
 *********************************************************************************************************************/

#include "nsapplicationunit/nssensorfusion/sensor_fusion.h"

namespace NsApplicationUnit {
namespace NsSensorFusion {

/*
  Generated based on configuration in ../../model/sensor_fusion.py

  Consumer interfaces
  ===================
    Data element API example for camera_image of type datatypes::Image
      - ::vaf::Result<::vaf::ConstDataPtr<const datatypes::Image>> GetAllocated_camera_image()
      - datatypes::Image Get_camera_image()
      - void RegisterDataElementHandler_camera_image(vaf::String owner, std::function<void(const ::vaf::ConstDataPtr<const datatypes::Image>)>&& f)

    - ImageServiceConsumer1_ : af::adas_demo_app::services::ImageServiceConsumer
      - Data elements
        - camera_image : datatypes::Image
        - image_scaling_factor_FieldNotifier : std::uint64_t
      - Operations
        - ::vaf::Future<af::adas_demo_app::services::GetImageSize::Output> GetImageSize()
        - ::vaf::Future<af::adas_demo_app::services::image_scaling_factor_FieldGetter::Output> image_scaling_factor_FieldGetter()
        - ::vaf::Future<void> image_scaling_factor_FieldSetter(const std::uint64_t& data)
    - ImageServiceConsumer2_ : af::adas_demo_app::services::ImageServiceConsumer
      - Data elements
        - camera_image : datatypes::Image
        - image_scaling_factor_FieldNotifier : std::uint64_t
      - Operations
        - ::vaf::Future<af::adas_demo_app::services::GetImageSize::Output> GetImageSize()
        - ::vaf::Future<af::adas_demo_app::services::image_scaling_factor_FieldGetter::Output> image_scaling_factor_FieldGetter()
        - ::vaf::Future<void> image_scaling_factor_FieldSetter(const std::uint64_t& data)
    - SteeringAngleServiceConsumer_ : af::adas_demo_app::services::SteeringAngleServiceConsumer
      - Data elements
        - steering_angle : datatypes::SteeringAngle
    - VelocityServiceConsumer_ : af::adas_demo_app::services::VelocityServiceConsumer
      - Data elements
        - car_velocity : datatypes::Velocity

  Provider interfaces
  ===================
    Data element API example for object_detection_list of type adas::interfaces::ObjectDetectionList
     - ::vaf::Result<::vaf::DataPtr<adas::interfaces::ObjectDetectionList>> Allocate_object_detection_list()
     - ::vaf::Result<void> SetAllocated_object_detection_list(::vaf::DataPtr<adas::interfaces::ObjectDetectionList>&& data)
     - ::vaf::Result<void> Set_object_detection_list(const adas::interfaces::ObjectDetectionList& data)

    - ObjectDetectionListModule_ : nsapplicationunit::nsmoduleinterface::nsobjectdetectionlist::ObjectDetectionListInterfaceProvider
      - Data elements
        - object_detection_list : adas::interfaces::ObjectDetectionList
*/

/**********************************************************************************************************************
  Constructor
**********************************************************************************************************************/
SensorFusion::SensorFusion(ConstructorToken&& token) : SensorFusionBase(std::move(token)) {
  // Insert your code here...
}

/**********************************************************************************************************************
  0 periodic task(s)
**********************************************************************************************************************/

//vaf::Result<void> SensorFusion::Init() {
//  return vaf::Result<void>{};
//}
//void SensorFusion::Start() {
//  ReportOperational();
//}
//void SensorFusion::Stop() {}
//void SensorFusion::DeInit() {}
//void SensorFusion::OnError(const vaf::Error& error) {
//  static_cast<void>(error);
//}

}  // namespace NsSensorFusion
}  // namespace NsApplicationUnit
