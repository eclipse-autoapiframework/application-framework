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
/*!        \file  result.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef VAF_RESULT_H_
#define VAF_RESULT_H_

#include "vaf/error_domain.h"
#include "tl/expected.h"

namespace vaf {

    template<typename T, typename E = vaf::Error>
    using Result = tl::expected<T, E>;

} // namespace vaf

#endif // VAF_RESULT_H_
