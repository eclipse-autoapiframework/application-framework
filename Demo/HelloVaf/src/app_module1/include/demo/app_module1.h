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
/*!        \file  app_module1.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef DEMO_APP_MODULE1_H
#define DEMO_APP_MODULE1_H

#include "demo/app_module1_base.h"

namespace demo {

class AppModule1 : public AppModule1Base {
 public:
  AppModule1(ConstructorToken&& token);

  //vaf::Result<void> Init() override;
  //void Start() noexcept override;
  //void Stop() noexcept override;
  //void DeInit() noexcept override;
  //void OnError(const vaf::Error& error) override;

  void PeriodicTask() override;

 private:
  uint8_t msg_id_;
};

}  // namespace demo

#endif  // DEMO_APP_MODULE1_H
