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
/*!        \file  module_states.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef INCLUDE_VAF_MODULE_STATES_H_
#define INCLUDE_VAF_MODULE_STATES_H_

#include "vaf/container_types.h"

namespace vaf {

enum class ModuleStates {
  kNotInitialized,
  kNotOperational,
  kStarting,
  kOperational,
  kShutdown
};

inline vaf::String ModuleStateToString(ModuleStates state) {
  switch (state) {
    case ModuleStates::kNotInitialized:
      return "kNotInitialized";
    case ModuleStates::kNotOperational:
      return "kNotOperational";
    case ModuleStates::kStarting:
      return "kStarting";
    case ModuleStates::kOperational:
      return "kOperational";
    case ModuleStates::kShutdown:
      return "kShutdown";
  }
  return "Unknown state";
}

} // namespace vaf

#endif // INCLUDE_VAF_MODULE_STATES_H_
