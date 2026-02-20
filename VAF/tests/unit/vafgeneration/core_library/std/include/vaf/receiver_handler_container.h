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
/*!        \file  receiver_handler_container.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef INCLUDE_VAF_RECEIVER_HANDLER_CONTAINER_H_
#define INCLUDE_VAF_RECEIVER_HANDLER_CONTAINER_H_

#include "vaf/container_types.h"

namespace vaf {
template <typename T>

class ReceiverHandlerContainer {
 public:
  ReceiverHandlerContainer(vaf::String owner, T&& handler)
    : owner_{std::move(owner)}, handler_{std::move(handler)}, is_active_{false} {
  }

  vaf::String owner_;
  T handler_;
  bool is_active_;
};

} // namespace vaf

#endif // INCLUDE_VAF_RECEIVER_HANDLER_CONTAINER_H_
