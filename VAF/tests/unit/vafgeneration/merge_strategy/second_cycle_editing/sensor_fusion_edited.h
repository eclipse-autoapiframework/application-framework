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

#include "external/ros/include/VAFROSApp.h"
#include "vaf/output_sync_stream.h"
#include "easylogging++.h"
#include "nsapplicationunit/nssensorfusion/sensor_fusion_base.h"
#include "mock.h"
#include "sleep.h"

namespace NsApplicationUnit {
namespace NsSensorFusion {

class SensorFusion : public SensorFusionBase {
 public:
  SensorFusion(ConstructorToken&& token);

  //vaf::Result<void> Init() override;
  //void Start() noexcept override;
  //void Stop() noexcept override;
  //void DeInit() noexcept override;
  //void OnError(const vaf::Error& error) override;

  void Step1() override;
  void RepeatSomething(vaf::String& repeat_id, const int& task_id);
  void Step2() override;
  void Step2a() override;
  int GetTaskId();
  void Step2b() override;

 private:
  bool _status{false};
  int sensor_id;
  int current_task_id;
  vaf::String nada{"Gellow"};
};

} // namespace NsSensorFusion
} // namespace NsApplicationUnit

#endif // NSAPPLICATIONUNIT_NSSENSORFUSION_SENSOR_FUSION_H
