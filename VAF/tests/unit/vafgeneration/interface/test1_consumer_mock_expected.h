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
/*!        \file  my_interface_consumer_mock.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef TEST_MY_INTERFACE_CONSUMER_MOCK_H
#define TEST_MY_INTERFACE_CONSUMER_MOCK_H

#include "vaf/container_types.h"
#include <functional>

#include "vaf/future.h"
#include "vaf/result.h"
#include "vaf/data_ptr.h"
#include "gmock/gmock.h"

#include "test/my_function.h"
#include "test/my_interface_consumer.h"
#include <cstdint>

namespace test {

class MyInterfaceConsumerMock : public MyInterfaceConsumer{
public:
  MOCK_METHOD(::vaf::Result<::vaf::ConstDataPtr<const std::uint64_t>>, GetAllocated_my_data_element, (), (override));
  MOCK_METHOD(std::uint64_t, Get_my_data_element, (), (override));
  MOCK_METHOD(void, RegisterDataElementHandler_my_data_element, (vaf::String owner, std::function<void(const ::vaf::ConstDataPtr<const std::uint64_t>)>&& f), (override));

  MOCK_METHOD(::vaf::Future<test::my_function::Output>, my_function, (const std::uint64_t& in, const std::uint64_t& inout), (override));
  MOCK_METHOD(::vaf::Future<void>, my_function_void, (const std::uint64_t& in), (override));
};

} // namespace test

#endif // TEST_MY_INTERFACE_CONSUMER_MOCK_H
