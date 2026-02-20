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
/*!        \file  controller_interface.cpp
 *         \brief
 *
 *********************************************************************************************************************/

#include "vaf/controller_interface.h"
#include "vaf/output_sync_stream.h"
#include "vaf/error_domain.h"

namespace vaf {

ControlInterface::ControlInterface(vaf::String name, vaf::Vector<vaf::String> dependencies, ExecutableControllerInterface& executable_controller_interface, vaf::Executor& executor)
  : name_{std::move(name)},
    dependencies_{std::move(dependencies)},
    executable_controller_interface_{executable_controller_interface},
    executor_{vaf::ModuleExecutor{executor, name_, dependencies_}} {
}

void ControlInterface::ReportOperational() {
  executable_controller_interface_.ReportOperationalOfModule(name_);
}

void ControlInterface::SkipStartingOfModule() {
  executable_controller_interface_.SkipStartingOfModule(name_);
}

void ControlInterface::ReportError(const vaf::Error& error, bool critical) {
  vaf::OutputSyncStream{} << "ReportError of module " << name_ << " (msg: " << error.Message() << ")\n";
  executable_controller_interface_.ReportErrorOfModule(std::move(error), name_, critical);
}

void ControlInterface::OnError(const vaf::Error& error) {
  ReportError(error, true);
}

vaf::String ControlInterface::GetName() {
  return name_;
}

vaf::Vector<vaf::String> ControlInterface::GetDependencies() {
  return dependencies_;
}

void ControlInterface::StartExecutor() {
  executor_.Start();
}

void ControlInterface::StopExecutor() {
  executor_.Stop();
}

void ControlInterface::StartEventHandlerForModule(const vaf::String& module_name) {
  static_cast<void>(module_name);
};

void ControlInterface::StopEventHandlerForModule(const vaf::String& module_name) {
  static_cast<void>(module_name);
};

} // namespace vaf
