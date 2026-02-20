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
/*!        \file  runtime.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef INCLUDE_VAF_RUNTIME_H_
#define INCLUDE_VAF_RUNTIME_H_

namespace vaf {
  class Runtime {
    public:
      Runtime();
      ~Runtime();

      Runtime(const Runtime&) = delete;
      Runtime(Runtime&&) = delete;
      Runtime& operator=(const Runtime&) = delete;
      Runtime& operator=(Runtime&&) = delete;
  };

} // namespace vaf

#endif // INCLUDE_VAF_RUNTIME_H_
