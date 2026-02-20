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
/*!        \file  collision_detection.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef NSAPPLICATIONUNIT_NSCOLLISIONDETECTION_COLLISION_DETECTION_H
#define NSAPPLICATIONUNIT_NSCOLLISIONDETECTION_COLLISION_DETECTION_H

#include "nsapplicationunit/nscollisiondetection/collision_detection_base.h"

namespace NsApplicationUnit {
namespace NsCollisionDetection {

class CollisionDetection : public CollisionDetectionBase {
 public:
  CollisionDetection(ConstructorToken&& token);

  void OnError(const vaf::Error& error) override;

  void PeriodicTask() override;
  void OnObjectList(vaf::ConstDataPtr<const ::adas::interfaces::ObjectDetectionList>& object_list);
  ::datatypes::BrakePressure ComputeBrakePressure(
      vaf::ConstDataPtr<const ::adas::interfaces::ObjectDetectionList>& object_list);

 private:
  std::uint64_t field_value_{0};
};

}  // namespace NsCollisionDetection
}  // namespace NsApplicationUnit

#endif  // NSAPPLICATIONUNIT_NSCOLLISIONDETECTION_COLLISION_DETECTION_H
