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
/*!        \file  sensor_fusion_base.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef NSAPPLICATIONUNIT_NSSENSORFUSION_SENSOR_FUSION_BASE_H
#define NSAPPLICATIONUNIT_NSSENSORFUSION_SENSOR_FUSION_BASE_H

#include <memory>
#include "vaf/controller_interface.h"

#include "af/adas_demo_app/services/image_service_consumer.h"
#include "af/adas_demo_app/services/steering_angle_service_consumer.h"
#include "af/adas_demo_app/services/velocity_service_consumer.h"
#include "nsapplicationunit/nsmoduleinterface/nsobjectdetectionlist/object_detection_list_interface_provider.h"

namespace NsApplicationUnit {
namespace NsSensorFusion {

class SensorFusionBase {
 public:
  struct ConstructorToken {
    std::shared_ptr<af::adas_demo_app::services::ImageServiceConsumer> ImageServiceConsumer1_;
    std::shared_ptr<af::adas_demo_app::services::ImageServiceConsumer> ImageServiceConsumer2_;
    std::shared_ptr<af::adas_demo_app::services::SteeringAngleServiceConsumer> SteeringAngleServiceConsumer_;
    std::shared_ptr<af::adas_demo_app::services::VelocityServiceConsumer> VelocityServiceConsumer_;
    std::shared_ptr<nsapplicationunit::nsmoduleinterface::nsobjectdetectionlist::ObjectDetectionListInterfaceProvider>
        ObjectDetectionListModule_;
  };

  SensorFusionBase(ConstructorToken&& token);
  virtual ~SensorFusionBase() = default;

  void ReportError(const vaf::Error&, bool) {}
  virtual void OnError(const vaf::Error&) {}
  vaf::String GetName() { return ""; }

 protected:
  std::shared_ptr<af::adas_demo_app::services::ImageServiceConsumer> ImageServiceConsumer1_;
  std::shared_ptr<af::adas_demo_app::services::ImageServiceConsumer> ImageServiceConsumer2_;
  std::shared_ptr<af::adas_demo_app::services::SteeringAngleServiceConsumer> SteeringAngleServiceConsumer_;
  std::shared_ptr<af::adas_demo_app::services::VelocityServiceConsumer> VelocityServiceConsumer_;
  std::shared_ptr<nsapplicationunit::nsmoduleinterface::nsobjectdetectionlist::ObjectDetectionListInterfaceProvider>
      ObjectDetectionListModule_;
};

}  // namespace NsSensorFusion
}  // namespace NsApplicationUnit

#endif  // NSAPPLICATIONUNIT_NSSENSORFUSION_SENSOR_FUSION_BASE_H
