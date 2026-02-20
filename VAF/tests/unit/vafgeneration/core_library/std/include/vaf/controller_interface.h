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
/*!        \file  controller_interface.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef INCLUDE_VAF_CONTROLLER_INTERFACE_H
#define INCLUDE_VAF_CONTROLLER_INTERFACE_H

#include "vaf/error_domain.h"
#include "vaf/executable_controller_interface.h"
#include "vaf/executor.h"
#include "vaf/result.h"

namespace vaf {

class ControlInterface {
 public:
  ControlInterface(vaf::String name, vaf::Vector<vaf::String> dependencies,
                   ExecutableControllerInterface& executable_controller_interface, vaf::Executor& executor);
  ControlInterface(const ControlInterface&) = delete;
  ControlInterface(ControlInterface&&) = delete;
  ControlInterface& operator=(const ControlInterface&) = delete;
  ControlInterface& operator=(ControlInterface&&) = delete;

  virtual ~ControlInterface() = default;

  virtual vaf::Result<void> Init() noexcept = 0;
  virtual void Start() noexcept = 0;
  virtual void Stop() noexcept = 0;
  virtual void DeInit() noexcept = 0;

  void ReportOperational();
  // The SkipStartingOfModule is only allowed to be used if there are no tasks within the module
  void SkipStartingOfModule();
  void ReportError(const vaf::Error& error, bool critical = false);

  virtual void OnError(const vaf::Error& error);

  vaf::String GetName();
  vaf::Vector<vaf::String> GetDependencies();

  void StartExecutor();
  void StopExecutor();

  virtual void StartEventHandlerForModule(const vaf::String& module_name);
  virtual void StopEventHandlerForModule(const vaf::String& module_name);

 protected:
  vaf::String name_;
  vaf::Vector<vaf::String> dependencies_;
  ExecutableControllerInterface& executable_controller_interface_;
  vaf::ModuleExecutor executor_;
};

} // namespace vaf

#endif  // INCLUDE_VAF_CONTROLLER_INTERFACE_H
