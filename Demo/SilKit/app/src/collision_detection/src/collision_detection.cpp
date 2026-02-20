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
/*!        \file  collision_detection.cpp
 *         \brief
 *
 *********************************************************************************************************************/

#include "nsapplicationunit/nscollisiondetection/collision_detection.h"
#include <vaf/result.h>
#include <chrono>
#include "vaf/output_sync_stream.h"
#include "vaf/controller_interface.h"
#include "vaf/data_ptr.h"

namespace NsApplicationUnit {
namespace NsCollisionDetection {

CollisionDetection::CollisionDetection(ConstructorToken&& token) : CollisionDetectionBase(std::move(token)) {
  ObjectDetectionListModule_->RegisterDataElementHandler_object_detection_list(
      GetName(),
      [this](vaf::ConstDataPtr<const ::adas::interfaces::ObjectDetectionList> object_detection_list) {
        OnObjectList(object_detection_list);
      });
  BrakeServiceProvider_->RegisterOperationHandler_SumTwoSummands(
      [](std::uint16_t const& summand_one, std::uint16_t const& summand_two) {
        af::adas_demo_app::services::SumTwoSummands::Output output{};
        output.sum = summand_one + summand_two;
        return output;
      });
  BrakeServiceProvider_->RegisterOperationHandler_brake_summand_coefficient_FieldSetter([this](uint64_t const& data) {
    vaf::OutputSyncStream{} << "Setter Handler gets called with value: " << data << "\n";
    field_value_ = data;
  });
  BrakeServiceProvider_->RegisterOperationHandler_brake_summand_coefficient_FieldGetter([this]() {
    vaf::OutputSyncStream{} << "Getter Handler gets called return: " << field_value_ << "\n";
    return af::adas_demo_app::services::brake_summand_coefficient_FieldGetter::Output{field_value_};
  });
}

void CollisionDetection::PeriodicTask() {
  vaf::OutputSyncStream{} << "Collision detection is active\n";
  BrakeServiceProvider_->Set_brake_summand_coefficient_FieldNotifier(field_value_);
}

void CollisionDetection::OnObjectList(vaf::ConstDataPtr<const ::adas::interfaces::ObjectDetectionList>& object_list) {
  vaf::OutputSyncStream{} << "Collision onObjectList\n";
  ::datatypes::BrakePressure brake_pressure = ComputeBrakePressure(object_list);
  BrakeServiceProvider_->Set_brake_action(brake_pressure);

  BrakeServiceProvider_->Allocate_brake_action()
      .InspectError([](auto) { vaf::OutputSyncStream{} << "Failed to allocate break action\n"; })
      .AndThen([this, &brake_pressure](auto allocated_break_action) {
        *allocated_break_action = brake_pressure;
        BrakeServiceProvider_->SetAllocated_brake_action(std::move(allocated_break_action));
        return vaf::Result<void>{};
      });
}

::datatypes::BrakePressure CollisionDetection::ComputeBrakePressure(
    vaf::ConstDataPtr<const ::adas::interfaces::ObjectDetectionList>& object_list) {
  // internal logic
  static_cast<void>(object_list);
  return ::datatypes::BrakePressure{11, 22};
}

void CollisionDetection::OnError(const vaf::Error& error) {
  ReportError(error, true);
}

}  // namespace NsCollisionDetection
}  // namespace NsApplicationUnit
