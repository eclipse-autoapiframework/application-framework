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
#include <vaf/result.h>
#include <chrono>
#include "vaf/output_sync_stream.h"
#include "vaf/error_domain.h"
#include "vaf/module_states.h"

namespace NsApplicationUnit {
namespace NsSensorFusion {

SensorFusion::SensorFusion(ConstructorToken&& token) : SensorFusionBase(std::move(token)) {
  VelocityServiceConsumer_->RegisterDataElementHandler_car_velocity(
      GetName(), [this](vaf::ConstDataPtr<const ::datatypes::Velocity> velocity) { OnVelocity(std::move(velocity)); });

  ImageServiceConsumer1_->RegisterDataElementHandler_image_scaling_factor_FieldNotifier(
      GetName(), [this](vaf::ConstDataPtr<const ::std::uint64_t> data) {
        vaf::OutputSyncStream{} << "Received Field Notifier value: " << *data << "\n";
      });
}

void SensorFusion::OnVelocity(vaf::ConstDataPtr<const ::datatypes::Velocity> velocity) {
  vaf::OutputSyncStream{} << "Received Velocity: " << velocity->value << "\n";
  is_enabled_ = velocity->value < kMaxVelocity;
}

void SensorFusion::Step1() {
  if (is_enabled_) {
    vaf::OutputSyncStream{} << "SensorFusion::step\n";

    static std::uint64_t counter = 23;
    counter++;
    ImageServiceConsumer1_->image_scaling_factor_FieldSetter(counter);
    vaf::Future<af::adas_demo_app::services::image_scaling_factor_FieldGetter::Output> getter_result =
        ImageServiceConsumer1_->image_scaling_factor_FieldGetter();
    if (vaf::is_future_ready(getter_result)) {
      vaf::Result<af::adas_demo_app::services::image_scaling_factor_FieldGetter::Output> result{
          getter_result.GetResult()};
      if (result.HasValue()) {
        vaf::OutputSyncStream{} << "Getter of Field results in: " << result.Value().data << "\n";
      } else {
        vaf::OutputSyncStream{} << "Getter received following error code: " << result.Error().UserMessage() << "\n";
      }
    }
    bool no_new_image{false};

    auto image1 = ImageServiceConsumer1_->GetAllocated_camera_image().InspectError(
        [&no_new_image](const vaf::Error&) { no_new_image = true; });
    auto image2 = ImageServiceConsumer2_->GetAllocated_camera_image().InspectError(
        [&no_new_image](const vaf::Error&) { no_new_image = true; });
    auto steering_angle = SteeringAngleServiceConsumer_->Get_steering_angle();
    auto velocity = VelocityServiceConsumer_->Get_car_velocity();

    if (!no_new_image) {
      vaf::OutputSyncStream{} << "Received new Images\n";
      ::adas::interfaces::ObjectDetectionList object_list =
          DoDetection(*image1.Value(), *image2.Value(), steering_angle, velocity);
      vaf::OutputSyncStream{} << "SensorFusion sending detection list\n";
      ObjectDetectionListModule_->Set_object_detection_list(object_list);
    }
  }
}

::adas::interfaces::ObjectDetectionList SensorFusion::DoDetection(const ::datatypes::Image& image1,
                                                                  const ::datatypes::Image& image2,
                                                                  ::datatypes::SteeringAngle, ::datatypes::Velocity) {
  static_cast<void>(image2);

  // vaf::OutputSyncStream{} << "Image1: " << "\n";
  // vaf::OutputSyncStream{} << "-------------------------------------------- " << "\n";
  // vaf::OutputSyncStream{} << "timestamp: " << image1.timestamp << "\n";
  // vaf::OutputSyncStream{} << "width: " << image1.width << "\n";
  // vaf::OutputSyncStream{} << "height: " << image1.height << "\n";
  // vaf::OutputSyncStream{} << "R: ";
  // for (auto element : image1.R) {
  //   vaf::OutputSyncStream{} << static_cast<uint32_t>(element) << " ";
  // }
  // vaf::OutputSyncStream{} << "\n";
  // vaf::OutputSyncStream{} << "G: ";
  // for (auto element : image1.G) {
  //   vaf::OutputSyncStream{} << static_cast<uint32_t>(element) << " ";
  // }
  // vaf::OutputSyncStream{} << "\n";
  // vaf::OutputSyncStream{} << "B: ";
  // for (auto element : image1.B) {
  //   vaf::OutputSyncStream{} << static_cast<uint32_t>(element) << " ";
  // }
  // vaf::OutputSyncStream{} << "\n";

  vaf::Future<af::adas_demo_app::services::GetImageSize::Output> answer = ImageServiceConsumer1_->GetImageSize();
  if (vaf::is_future_ready(answer)) {
    auto result = answer.GetResult();
    if (result.HasValue()) {
      vaf::OutputSyncStream{} << "GetImageSize() yields: " << result.Value().width << "x" << result.Value().height << "\n";
    }
  }
  return ::adas::interfaces::ObjectDetectionList{};  // dummy implementation
}

void SensorFusion::OnError(const vaf::Error& error) {
  vaf::OutputSyncStream{} << "Error in sensor fusion: " << error.Message() << "\n";
  ReportError(error, true);
}

void SensorFusion::Step2() {}

void SensorFusion::Step3() {}

void SensorFusion::Step4() {}

}  // namespace NsSensorFusion
}  // namespace NsApplicationUnit
