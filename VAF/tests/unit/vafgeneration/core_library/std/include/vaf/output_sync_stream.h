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
/*!        \file  output_sync_stream.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef INCLUDE_VAF_OUTPUT_SYNC_STREAM_H_
#define INCLUDE_VAF_OUTPUT_SYNC_STREAM_H_

#include <mutex>
#include <iostream>
#include <sstream>

namespace vaf {

class OutputSyncStream : public std::ostringstream {
public:
  explicit OutputSyncStream(std::ostream& ostream = std::cout) : ostream_{ostream} {}
  ~OutputSyncStream() override {
    if(is_thread_safe_) {
      std::unique_lock unique_lock(mutex_);
      ostream_ << this->str();
    }
  }

  OutputSyncStream(OutputSyncStream const&) = delete;
  OutputSyncStream(OutputSyncStream&&) = delete;
  auto operator=(OutputSyncStream const&) -> OutputSyncStream& = delete;
  auto operator=(OutputSyncStream&&) -> OutputSyncStream& = delete;

  static auto EnableThreadSafety() -> void  { is_thread_safe_ = true; }
  static auto DisableThreadSafety() -> void { is_thread_safe_ = false; }

private:
  static inline bool is_thread_safe_{true};
  static inline std::mutex mutex_{};
  std::ostream& ostream_;
};

}  // namespace vaf

#endif  // INCLUDE_VAF_MODULE_STATES_H_
