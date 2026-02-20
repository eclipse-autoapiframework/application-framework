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
/*!        \file  vss_consumer.cpp
 *         \brief
 *
 *********************************************************************************************************************/

#include "demo/vss_consumer.h"
#include "vaf/output_sync_stream.h"

namespace demo {

/*
  Generated based on configuration in ../../model/vss_consumer.py

  Consumer interfaces
  ===================
    Data element API example for Lateral of type float
      - ::vaf::Result<::vaf::ConstDataPtr<const float>> GetAllocated_Lateral()
      - float Get_Lateral()
      - void RegisterDataElementHandler_Lateral(vaf::String owner, std::function<void(const ::vaf::ConstDataPtr<const float>)>&& f)

    - AccelerationConsumer_ : vss::vehicle::Acceleration_IfConsumer
      - Data elements
        - Lateral : float
        - Longitudinal : float
        - Vertical : float
    - DriverConsumer_ : vss::vehicle::Driver_IfConsumer
      - Data elements
        - AttentiveProbability : float
        - DistractionLevel : float
        - FatigueLevel : float
        - HeartRate : std::uint16_t
        - Identifier : vss::vehicle::driver::Identifier
        - IsEyesOnRoad : bool
        - IsHandsOnWheel : bool
*/

/**********************************************************************************************************************
  Constructor
**********************************************************************************************************************/
VssConsumer::VssConsumer(ConstructorToken&& token) : VssConsumerBase(std::move(token)) {
  // Insert your code here...
}

/**********************************************************************************************************************
  1 periodic task(s)
**********************************************************************************************************************/
// Task with name PeriodicTask and a period of 200ms.
void VssConsumer::PeriodicTask() {
  auto acceleration = AccelerationConsumer_->Get_Longitudinal();
  auto isEyesOnRoad = DriverConsumer_->Get_IsEyesOnRoad();
  auto driverId = DriverConsumer_->Get_Identifier();

  vaf::OutputSyncStream{} << "Longitudinal acceleration: " << acceleration << " m/s^2" << std::endl;
  if (isEyesOnRoad) {
    vaf::OutputSyncStream{} << "'" << driverId.Subject << "' has the eyes on the road." << std::endl;
  } else {
    vaf::OutputSyncStream{} << "'" << driverId.Subject << "' does not have the eyes on the road." << std::endl;
  }
}

//vaf::Result<void> VssConsumer::Init() {
//  return vaf::Result<void>{};
//}
//void VssConsumer::Start() {
//  ReportOperational();
//}
//void VssConsumer::Stop() {}
//void VssConsumer::DeInit() {}
//void VssConsumer::OnError(const vaf::Error& error) {
//  static_cast<void>(error);
//}

}  // namespace demo
