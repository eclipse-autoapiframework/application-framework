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
/*!        \file  my_interface_consumer.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef TEST_MY_INTERFACE_CONSUMER_H
#define TEST_MY_INTERFACE_CONSUMER_H

#include "vaf/container_types.h"
#include <functional>

#include "vaf/future.h"
#include "vaf/result.h"
#include "vaf/data_ptr.h"

#include "test/my_function.h"
#include <cstdint>

namespace test {

class MyInterfaceConsumer {
public:
  virtual ~MyInterfaceConsumer() = default;

  virtual ::vaf::Result<::vaf::ConstDataPtr<const std::uint64_t>> GetAllocated_my_data_element() = 0;
  virtual std::uint64_t Get_my_data_element() = 0;
  virtual void RegisterDataElementHandler_my_data_element(vaf::String owner, std::function<void(const ::vaf::ConstDataPtr<const std::uint64_t>)>&& f) = 0;

  virtual ::vaf::Future<test::my_function::Output> my_function(const std::uint64_t& in, const std::uint64_t& inout) = 0;
  virtual ::vaf::Future<void> my_function_void(const std::uint64_t& in) = 0;
};

} // namespace test

#endif // TEST_MY_INTERFACE_CONSUMER_H
