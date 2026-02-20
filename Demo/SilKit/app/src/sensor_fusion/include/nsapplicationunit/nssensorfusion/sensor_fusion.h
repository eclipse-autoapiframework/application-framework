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
/*!        \file  sensor_fusion.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef NSAPPLICATIONUNIT_NSSENSORFUSION_SENSOR_FUSION_H
#define NSAPPLICATIONUNIT_NSSENSORFUSION_SENSOR_FUSION_H

#include "nsapplicationunit/nssensorfusion/sensor_fusion_base.h"

namespace NsApplicationUnit {
namespace NsSensorFusion {

class SensorFusion : public SensorFusionBase {
 public:
  SensorFusion(ConstructorToken&& token);

  void OnVelocity(vaf::ConstDataPtr<const ::datatypes::Velocity> velocity);
  ::adas::interfaces::ObjectDetectionList DoDetection(const ::datatypes::Image&, const ::datatypes::Image&,
                                                      ::datatypes::SteeringAngle, ::datatypes::Velocity);

  void OnError(const vaf::Error& error) override;

  void Step1() override;
  void Step2() override;
  void Step3() override;
  void Step4() override;

 private:
  constexpr static uint16_t kMaxVelocity{100};
  bool is_enabled_{true};
};

}  // namespace NsSensorFusion
}  // namespace NsApplicationUnit

#endif  // NSAPPLICATIONUNIT_NSSENSORFUSION_SENSOR_FUSION_H
