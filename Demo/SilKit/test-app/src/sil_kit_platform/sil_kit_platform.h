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
/*!        \file  sil_kit_platform.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef NSAPPLICATIONUNIT_SILKITPLATFORM_SIL_KIT_PLATFORM_H
#define NSAPPLICATIONUNIT_SILKITPLATFORM_SIL_KIT_PLATFORM_H

#include "nsapplicationunit/nssilkitplatform/sil_kit_platform_base.h"

namespace NsApplicationUnit {
namespace NsSilKitPlatform {

class SilKitPlatform : public SilKitPlatformBase {
 public:
  SilKitPlatform(ConstructorToken&& token);

  void BrakeTask() override;
  void ImageTask() override;
  void SteeringAngleTask() override;
  void VelocityTask() override;

 private:
  datatypes::Image image{};
  vaf::Future<af::adas_demo_app::services::brake_summand_coefficient_FieldGetter::Output>
      brake_summand_coefficient_getter_future_{};
};

}  // namespace SilKitPlatform
}  // namespace NsApplicationUnit

#endif  // NSAPPLICATIONUNIT_SILKITPLATFORM_SIL_KIT_PLATFORM_H
