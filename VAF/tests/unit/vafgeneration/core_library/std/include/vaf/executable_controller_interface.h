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
/*!        \file  executable_controller_interface.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef VAF_EXECUTABLE_CONTROLLER_INTERFACE_H_
#define VAF_EXECUTABLE_CONTROLLER_INTERFACE_H_

/*!********************************************************************************************************************
 *  INCLUDES
 *********************************************************************************************************************/

#include "vaf/container_types.h"
#include "vaf/error_domain.h"
#include "vaf/module_states.h"

namespace vaf {

class ExecutableControllerInterface {
 public:
  virtual ~ExecutableControllerInterface() = default;
  virtual void ReportOperationalOfModule(vaf::String name) = 0;
  virtual void SkipStartingOfModule(vaf::String name) = 0;
  virtual void ReportErrorOfModule(const vaf::Error& error, vaf::String name, bool critical) = 0;
};

} // namespace vaf

#endif // VAF_EXECUTABLE_CONTROLLER_INTERFACE_H_
