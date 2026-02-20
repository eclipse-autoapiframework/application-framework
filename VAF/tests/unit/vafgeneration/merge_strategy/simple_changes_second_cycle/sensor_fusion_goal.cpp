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
#include "vaf/output_sync_stream.h"

namespace NsApplicationUnit {
namespace NsSensorFusion {

/*
  Data element API example for MyDataElement of type std::uint64_t
  ================================================================
  - Provider
    ::vaf::Result<::vaf::DataPtr<std::uint64_t>> Allocate_MyDataElement()
    ::vaf::Result<void> SetAllocated_MyDataElement(::vaf::DataPtr<std::uint64_t>&& data)
    ::vaf::Result<void> Set_MyDataElement(const std::uint64_t& data)
  - Consumer
    ::vaf::Result<::vaf::ConstDataPtr<const std::uint64_t>> GetAllocated_MyDataElement()
    std::uint64_t Get_MyDataElement()
    std::function<void(const ::vaf::ConstDataPtr<const std::uint64_t>)>
    void RegisterDataElementHandler_MyDataElement(vaf::String owner, std::function<void(const ::vaf::ConstDataPtr<const std::uint64_t>)>&& f)

  Consumer interfaces
  ===================
    - ImageServiceConsumer1 : af::adas_demo_app::services::ImageServiceConsumer
      - Data elements
        - camera_image : datatypes::Image
        - image_scaling_factor_FieldNotifier : std::uint64_t

      - Operations
        - ::vaf::Future<af::adas_demo_app::services::internal::methods::GetImageSize::Output> GetImageSize()
        - ::vaf::Future<af::adas_demo_app::services::internal::methods::image_scaling_factor_FieldGetter::Output> image_scaling_factor_FieldGetter()
        - ::vaf::Future<void> image_scaling_factor_FieldSetter(const std::uint64_t& data)

    - ImageServiceConsumer2 : af::adas_demo_app::services::ImageServiceConsumer
      - Data elements
        - camera_image : datatypes::Image
        - image_scaling_factor_FieldNotifier : std::uint64_t

      - Operations
        - ::vaf::Future<af::adas_demo_app::services::internal::methods::GetImageSize::Output> GetImageSize()
        - ::vaf::Future<af::adas_demo_app::services::internal::methods::image_scaling_factor_FieldGetter::Output> image_scaling_factor_FieldGetter()
        - ::vaf::Future<void> image_scaling_factor_FieldSetter(const std::uint64_t& data)

    - SteeringAngleServiceConsumer : af::adas_demo_app::services::SteeringAngleServiceConsumer
      - Data elements
        - steering_angle : datatypes::SteeringAngle


    - VelocityServiceConsumer : af::adas_demo_app::services::VelocityServiceConsumer
      - Data elements
        - car_velocity : datatypes::Velocity


  Provider interfaces
  ===================
    - ObjectDetectionListModule : nsapplicationunit::nsmoduleinterface::nsobjectdetectionlist::ObjectDetectionListInterfaceProvider
      - Data elements
        - object_detection_list : adas::interfaces::ObjectDetectionList


*/

SensorFusion::SensorFusion(ConstructorToken&& token) : SensorFusionBase(std::move(token)) {
  vaf::String marker{"MARK-2"};
  bool constructed_{true};
  vaf::OutputSyncStream{} << marker << ": Construction of SensorFusion is " << constructed_ << std::endl;
  // Init sensor id & current task id
  sensor_id = 2;
  current_task_id = 007;
}

<<<<<<< {TMP_PATH}/SensorFusion/implementation/src/sensor_fusion.cpp.new~
/**********************************************************************************************************************
  4 periodic task(s)
**********************************************************************************************************************/
// Task with name Steppe and a period of 300ms.
void SensorFusion::Steppe() {
  // Insert your code for periodic execution here...
}

// Task with name Estepo and a period of 150ms.
void SensorFusion::Estepo() {
  // Insert your code for periodic execution here...
}

// Task with name Staipo and a period of 200ms.
void SensorFusion::Staipo() {
  // Insert your code for periodic execution here...
}

// Task with name Finales and a period of 200ms.
void SensorFusion::Finales() {
  // Insert your code for periodic execution here...
=======
void SensorFusion::Step1() { vaf::OutputSyncStream{} << "Step1 is performed: Clapton likes to clap" << std::endl; }

void SensorFusion::Step2() { vaf::OutputSyncStream{} << "Step2 is performed: Mayo is naise" << std::endl; }

void SensorFusion::Step2a() {
  vaf::OutputSyncStream{} << "Step2a is performed: Penultimate is not Penaldo" << std::endl;
  _status = true;
}

void SensorFusion::Step2b() {
  vaf::OutputSyncStream{} << "Step2b is performed -> Done!" << std::endl;
  nada = "Pico-Bello";
>>>>>>> {TMP_PATH}/SensorFusion/implementation/src/sensor_fusion.cpp
}

}  // namespace NsSensorFusion
}  // namespace NsApplicationUnit
