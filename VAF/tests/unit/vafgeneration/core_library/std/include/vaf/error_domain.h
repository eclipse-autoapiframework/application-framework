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
/*!        \file  error_domain.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef VAF_ERROR_DOMAIN_H_
#define VAF_ERROR_DOMAIN_H_

#include <stdexcept>

#include "vaf/container_types.h"

namespace vaf {

enum class ErrorCode {
  kOk = 1,
  kNotOk,
  kUnknown,
};

class Error {
 public:
  Error(ErrorCode error_code, vaf::String message) : error_code_{error_code}, message_{message} {}

  const vaf::String Message() const noexcept {
    return vaf::String{std::to_string(static_cast<int>(error_code_)) + ": " + message_.c_str()};
  }

  void ThrowAsException() const { throw std::runtime_error(message_.c_str()); }

  const vaf::String UserMessage() const noexcept { return message_; }

  Error(const Error&) = default;
  Error(Error&&) = default;

  Error& operator=(const Error&) = default;
  Error& operator=(Error&&) = default;

 private:
  ErrorCode error_code_;
  vaf::String message_;
};
}  // namespace vaf

#endif  // VAF_ERROR_DOMAIN_H_
