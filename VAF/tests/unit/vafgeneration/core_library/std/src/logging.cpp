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
/*!        \file  logging.cpp
 *         \brief
 *
 *********************************************************************************************************************/

#include "vaf/logging.h"

namespace vaf {

// Initialize static members outside the class definition
    std::mutex LoggerSingleton::mtx;
    LoggerSingleton *LoggerSingleton::instance = nullptr;

    Logger &CreateLogger(const char *ctx_id, const char *ctx_description) {
        return LoggerSingleton::getInstance()->CreateLogger(ctx_id, ctx_description);
    }

} // namespace vaf
