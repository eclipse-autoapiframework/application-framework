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
/*!        \file  runtime.cpp
 *         \brief
 *
 *********************************************************************************************************************/

#include "vaf/runtime.h"
#include "vaf/logging.h"

namespace vaf {

    Runtime::Runtime() {
        vaf::LoggerSingleton::getInstance()->SetLogLevelVerbose();
    }

    Runtime::~Runtime() {
        vaf::LoggerSingleton::getInstance()->CleanLoggers();
    }

} // namespace vaf
