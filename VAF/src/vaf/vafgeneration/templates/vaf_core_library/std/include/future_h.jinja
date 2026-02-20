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
/*!        \file  future.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef VAF_FUTURE_H_
#define VAF_FUTURE_H_

#include <future>

#include "vaf/logging.h"
#include "vaf/result.h"

namespace vaf {
namespace internal {

template <typename T>
class Promise;

} // namespace internal

template <typename T>
class Future {
 public:
  Future() : future_{} {}

  Future(Future&& future) : future_{std::move(future.future_)} {}
  Future(const Future& other) = delete;

  Future& operator=(Future&& other) noexcept {
    if (this != &other) future_ = std::move(other.future_);
    return *this;
  }
  Future& operator=(const Future& other) = delete;

  bool valid() const noexcept { return future_.valid(); }

  void wait() const { future_.wait(); }

  std::future_status wait_for(std::chrono::nanoseconds const& timeout_duration) const {
    return future_.wait_for(timeout_duration);
  }

  std::future_status wait_until(const std::chrono::system_clock::time_point& timeout_time) const {
    return wait_until(timeout_time);
  }

  vaf::Result<T> GetResult() { return future_.get(); }

  T get() {
    vaf::Result<T> res{GetResult()};
    if (!res.HasValue()) {
      vaf::LoggerSingleton::getInstance()->default_logger_.LogFatal() << "Future result has no value!";
      std::abort();
    }
    return std::move(res).Value();
  }

  bool is_ready() const noexcept {
    if (this->valid()) return future_.wait_for(std::chrono::milliseconds(0)) == std::future_status::ready;
    return false;
  }

 private:
  std::future<vaf::Result<T>> future_;
  Future(std::future<vaf::Result<T>>&& future) : future_{std::move(future)} {}

  friend vaf::internal::Promise<T>;
};

template <typename T>
bool is_future_ready(vaf::Future<T> const& f, uint32_t timeout_ms = 0) {
  if (f.valid()) return f.wait_for(std::chrono::milliseconds(timeout_ms)) == std::future_status::ready;
  return false;
}

}  // namespace vaf

#endif  // VAF_FUTURE_H_
