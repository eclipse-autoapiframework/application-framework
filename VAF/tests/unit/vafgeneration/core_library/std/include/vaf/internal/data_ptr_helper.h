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
/*!        \file  data_ptr_helper.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef VAF_DATA_PTR_HELPER_H_
#define VAF_DATA_PTR_HELPER_H_

#include "vaf/data_ptr.h"

namespace vaf {
namespace internal {

template <typename T>
class DataPtrHelper {
 public:
  DataPtrHelper() = delete;
  DataPtrHelper(const DataPtrHelper&) = delete;
  DataPtrHelper& operator=(const DataPtrHelper&) = delete;

  static std::unique_ptr<T> getRawPtr(::vaf::DataPtr<T>& ptr) { return std::move(ptr.container_->raw_ptr_); };
};

}  // namespace internal
}  // namespace vaf

#endif  // VAF_DATA_PTR_HELPER_H_
