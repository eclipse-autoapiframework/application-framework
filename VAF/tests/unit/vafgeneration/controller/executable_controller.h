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
/*!        \file  executable_controller.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef EXECUTABLE_CONTROLLER_EXECUTABLE_CONTROLLER_H
#define EXECUTABLE_CONTROLLER_EXECUTABLE_CONTROLLER_H

#include <memory>

#include "vaf/executable_controller_base.h"
#include "vaf/executor.h"

namespace executable_controller {

class ExecutableController final : public vaf::ExecutableControllerBase {
 public:
  ExecutableController();
  ~ExecutableController() override = default;

 protected:
  void DoInitialize() override;
  void DoStart() override;
  void DoShutdown() override;

 private:
  std::unique_ptr<vaf::Executor> executor_;
};

} // namespace executable_controller

#endif // EXECUTABLE_CONTROLLER_EXECUTABLE_CONTROLLER_H
