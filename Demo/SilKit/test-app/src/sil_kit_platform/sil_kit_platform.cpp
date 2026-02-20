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
/*!        \file  sil_kit_platform.cpp
 *         \brief
 *
 *********************************************************************************************************************/

#include <chrono>
#include "vaf/output_sync_stream.h"

#include "nsapplicationunit/nssilkitplatform/sil_kit_platform.h"

namespace NsApplicationUnit {
namespace NsSilKitPlatform {


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
    void RegisterDataElementHandler_MyDataElement(std::string owner, std::function<void(const ::vaf::ConstDataPtr<const
  std::uint64_t>)>&& f)

  Consumer interfaces
  ===================
    - BrakeServiceConsumer_ : af::adas_demo_app::services::BrakeServiceConsumer
      - Data elements
        - brake_action : datatypes::BrakePressure
        - brake_summand_coefficient_FieldNotifier : std::uint64_t

      - Operations
        - ::vaf::Future<af::adas_demo_app::services::SumTwoSummands::Output> SumTwoSummands(const
  std::uint16_t& summand_one, const std::uint16_t& summand_two)
        - ::vaf::Future<af::adas_demo_app::services::brake_summand_coefficient_FieldGetter::Output>
  brake_summand_coefficient_FieldGetter()
        - ::vaf::Future<void> brake_summand_coefficient_FieldSetter(const std::uint64_t& data)

  Provider interfaces
  ===================
    - ImageServiceProvider1_ : af::adas_demo_app::services::ImageServiceProvider
      - Data elements
        - camera_image : datatypes::Image
        - image_scaling_factor_FieldNotifier : std::uint64_t

      - Operations
        - void
  RegisterOperationHandler_image_scaling_factor_FieldGetter(std::function<af::adas_demo_app::services::image_scaling_factor_FieldGetter::Output()>&&
  f)
        - void RegisterOperationHandler_image_scaling_factor_FieldSetter(std::function<void(const std::uint64_t&)>&& f)
        - void
  RegisterOperationHandler_GetImageSize(std::function<af::adas_demo_app::services::GetImageSize::Output()>&& f)

    - ImageServiceProvider2_ : af::adas_demo_app::services::ImageServiceProvider
      - Data elements
        - camera_image : datatypes::Image
        - image_scaling_factor_FieldNotifier : std::uint64_t

      - Operations
        - void
  RegisterOperationHandler_GetImageSize(std::function<af::adas_demo_app::services::GetImageSize::Output()>&&
  f)
        - void
  RegisterOperationHandler_image_scaling_factor_FieldGetter(std::function<af::adas_demo_app::services::image_scaling_factor_FieldGetter::Output()>&&
  f)
        - void RegisterOperationHandler_image_scaling_factor_FieldSetter(std::function<void(const std::uint64_t&)>&& f)

    - SteeringAngleServiceProvider_ : af::adas_demo_app::services::SteeringAngleServiceProvider
      - Data elements
        - steering_angle : datatypes::SteeringAngle


    - VelocityServiceProvider_ : af::adas_demo_app::services::VelocityServiceProvider
      - Data elements
        - car_velocity : datatypes::Velocity


*/


/**********************************************************************************************************************
  Constructor
**********************************************************************************************************************/
SilKitPlatform::SilKitPlatform(ConstructorToken&& token)
    : SilKitPlatformBase(std::move(token))
{
  image.height = 1080;
  image.width = 1920;
  image.timestamp = 0;

  image.R.push_back(10);
  image.R.push_back(11);
  image.R.push_back(12);
  image.R.push_back(13);

  image.G.push_back(20);
  image.G.push_back(21);
  image.G.push_back(22);
  image.G.push_back(23);
  image.G.push_back(24);

  image.B.push_back(30);
  image.B.push_back(31);
  image.B.push_back(32);
  image.B.push_back(33);
  image.B.push_back(34);
  image.B.push_back(35);

  ImageServiceProvider1_->RegisterOperationHandler_image_scaling_factor_FieldGetter(
      [this]() -> ::af::adas_demo_app::services::image_scaling_factor_FieldGetter::Output {
        ::af::adas_demo_app::services::image_scaling_factor_FieldGetter::Output output{};
        vaf::OutputSyncStream{} << "ImageServiceProvider1::image_scaling_factor_FieldGetter handler called" << std::endl;
        output.data = 42;
        return output;
      });
  ImageServiceProvider1_->RegisterOperationHandler_image_scaling_factor_FieldSetter(
      [this](std::uint64_t const& data) -> void {
        vaf::OutputSyncStream{} << "ImageServiceProvider1::image_scaling_factor_FieldSetter handler called with parameter: " << data
                  << std::endl;
      });
  ImageServiceProvider1_->RegisterOperationHandler_GetImageSize(
      [this]() -> af::adas_demo_app::services::GetImageSize::Output {
        af::adas_demo_app::services::GetImageSize::Output output{};
        vaf::OutputSyncStream{} << "ImageServiceProvider1::GetImageSize handler called" << std::endl;
        output.width = image.width;
        output.height = image.height;
        return output;
      });
  ImageServiceProvider2_->RegisterOperationHandler_image_scaling_factor_FieldGetter(
      [this]() -> ::af::adas_demo_app::services::image_scaling_factor_FieldGetter::Output {
        ::af::adas_demo_app::services::image_scaling_factor_FieldGetter::Output output{};
        vaf::OutputSyncStream{} << "ImageServiceProvider2::image_scaling_factor_FieldGetter handler called" << std::endl;
        output.data = 42;
        return output;
      });
  ImageServiceProvider2_->RegisterOperationHandler_image_scaling_factor_FieldSetter(
      [this](std::uint64_t const& data) -> void {
        vaf::OutputSyncStream{} << "ImageServiceProvider2::image_scaling_factor_FieldSetter handler called with parameter: " << data
                  << std::endl;
      });
  ImageServiceProvider2_->RegisterOperationHandler_GetImageSize(
      [this]() -> af::adas_demo_app::services::GetImageSize::Output {
        af::adas_demo_app::services::GetImageSize::Output output{};
        vaf::OutputSyncStream{} << "ImageServiceProvider2::GetImageSize handler called" << std::endl;
        output.width = image.width;
        output.height = image.height;
        return output;
      });

  BrakeServiceConsumer_->RegisterDataElementHandler_brake_action(
      GetName(), [this](vaf::ConstDataPtr<const datatypes::BrakePressure> brake_pressure) {
        vaf::OutputSyncStream{} << "Received brake_action call with timestamp: " << brake_pressure->timestamp
                  << " and value "
                  << static_cast<int>(brake_pressure->value) << std::endl;
      });
  BrakeServiceConsumer_->RegisterDataElementHandler_brake_summand_coefficient_FieldNotifier(
      GetName(), [this](vaf::ConstDataPtr<const std::uint64_t> data) {
        vaf::OutputSyncStream{} << "Received brake_summand_coefficient field notifier value: " << *data << std::endl;
      });
}

/**********************************************************************************************************************
  4 periodic task(s)
**********************************************************************************************************************/
// Task with name BrakeTask and a period of 100ms.
void SilKitPlatform::BrakeTask() {
  static uint64_t counter = 0;
  static uint8_t step = 0;

  if (brake_summand_coefficient_getter_future_.is_ready()) {
    auto result = brake_summand_coefficient_getter_future_.GetResult();
    if (result.HasValue()) {
      vaf::OutputSyncStream{} << "RPC call brake_summand_coefficient_FieldGetter result is: " << result.Value().data << std::endl;
    } else {
      vaf::OutputSyncStream{} << "RPC call brake_summand_coefficient_FieldGetter failed: " << result.Error().Message() << std::endl;
    }
    brake_summand_coefficient_getter_future_ =
        vaf::Future<af::adas_demo_app::services::brake_summand_coefficient_FieldGetter::Output>{};
  }

  if (0 == step) {
    brake_summand_coefficient_getter_future_ = BrakeServiceConsumer_->brake_summand_coefficient_FieldGetter();
  } else {
    BrakeServiceConsumer_->brake_summand_coefficient_FieldSetter(counter);
    counter++;
  }
  step = 1 - step;
}

// Task with name ImageTask and a period of 100ms.
void SilKitPlatform::ImageTask() {
  static uint64_t counter = 0;
  static uint8_t step = 0;

  if (0 == step) {
    image.timestamp =
        std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch())
            .count();
    ImageServiceProvider1_->Set_camera_image(image);
    ImageServiceProvider2_->Set_camera_image(image);
  } else {
    ImageServiceProvider1_->Set_image_scaling_factor_FieldNotifier(counter);
    ImageServiceProvider2_->Set_image_scaling_factor_FieldNotifier(counter);
    counter++;
  }
  step = 1 - step;
}


// Task with name SteeringAngleTask and a period of 1000ms.
void SilKitPlatform::SteeringAngleTask() {
  static uint16_t counter = 0;

  auto steering_angle = datatypes::SteeringAngle();
  steering_angle.timestamp =
      std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch())
          .count();
  steering_angle.value = counter;
  SteeringAngleServiceProvider_->Set_steering_angle(steering_angle);

  counter += 1000;
}

// Task with name VelocityTask and a period of 1000ms.
void SilKitPlatform::VelocityTask() {
  static uint16_t counter = 0;

  auto velocity = datatypes::Velocity();
  velocity.timestamp =
      std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch())
          .count();
  velocity.value = counter++;
  VelocityServiceProvider_->Set_car_velocity(velocity);
}

}  // namespace SilKitPlatform
}  // namespace NsApplicationUnit
