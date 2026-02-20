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
/*!        \file  my_consumer_module.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef TEST_MY_CONSUMER_MODULE_H
#define TEST_MY_CONSUMER_MODULE_H

#include <atomic>
#include <mutex>
#include <memory>
#include "vaf/container_types.h"
#include "vaf/receiver_handler_container.h"
#include "vaf/controller_interface.h"
#include "vaf/data_ptr.h"
#include "vaf/executable_controller_interface.h"
#include "vaf/result.h"

#include "silkit/SilKit.hpp"
#include "silkit/services/all.hpp"
#include "silkit/services/orchestration/string_utils.hpp"
#include "silkit/util/serdes/Serialization.hpp"
#include "protobuf_interface_test_MyInterface.pb.h"

#include "test/my_interface_consumer.h"


namespace test {

class MyConsumerModule final : public test::MyInterfaceConsumer, public vaf::ControlInterface {
 public:
  MyConsumerModule(vaf::Executor& executor, vaf::String name, vaf::ExecutableControllerInterface& executable_controller_interface);
  ~MyConsumerModule() override = default;

  MyConsumerModule(const MyConsumerModule&) = delete;
  MyConsumerModule(MyConsumerModule&&) = delete;
  MyConsumerModule& operator=(const MyConsumerModule&) = delete;
  MyConsumerModule& operator=(MyConsumerModule&&) = delete;

  // Management related operations
  vaf::Result<void> Init() noexcept override;
  void Start() noexcept override;
  void Stop() noexcept override;
  void DeInit() noexcept override;
  void StartEventHandlerForModule(const vaf::String& module) override;
  void StopEventHandlerForModule(const vaf::String& module) override;

  ::vaf::Result<::vaf::ConstDataPtr<const std::uint64_t>> GetAllocated_my_data_element1() override;
  std::uint64_t Get_my_data_element1() override;
  void RegisterDataElementHandler_my_data_element1(vaf::String owner, std::function<void(const ::vaf::ConstDataPtr<const std::uint64_t>)>&& f) override;
  ::vaf::Result<::vaf::ConstDataPtr<const std::uint64_t>> GetAllocated_my_data_element2() override;
  std::uint64_t Get_my_data_element2() override;
  void RegisterDataElementHandler_my_data_element2(vaf::String owner, std::function<void(const ::vaf::ConstDataPtr<const std::uint64_t>)>&& f) override;

  ::vaf::Future<void> MyVoidOperation(const std::uint64_t& in) override;
  ::vaf::Future<test::MyOperation::Output> MyOperation(const std::uint64_t& in, const std::uint64_t& inout) override;
  ::vaf::Future<test::MyGetter::Output> MyGetter() override;
  ::vaf::Future<void> MySetter(const std::uint64_t& a) override;

 private:
  vaf::ModuleExecutor& executor_;
  vaf::Vector<vaf::String> active_modules_;
  std::unique_ptr<SilKit::IParticipant> participant_;

  ::vaf::ConstDataPtr<const std::uint64_t> cached_test_my_data_element1_{};
  vaf::Vector<::vaf::ReceiverHandlerContainer<std::function<void(const ::vaf::ConstDataPtr<const std::uint64_t>)>>> registered_test_my_data_element1_event_handlers_{};
  std::mutex cached_test_my_data_element1_mutex_;
  SilKit::Services::PubSub::IDataSubscriber* subscriber_test_my_data_element1_;
  ::vaf::ConstDataPtr<const std::uint64_t> cached_test_my_data_element2_{std::make_unique<const std::uint64_t>(std::uint64_t{64})};
  vaf::Vector<::vaf::ReceiverHandlerContainer<std::function<void(const ::vaf::ConstDataPtr<const std::uint64_t>)>>> registered_test_my_data_element2_event_handlers_{};
  std::mutex cached_test_my_data_element2_mutex_;
  SilKit::Services::PubSub::IDataSubscriber* subscriber_test_my_data_element2_;
  SilKit::Services::Rpc::IRpcClient* rpc_client_test_MyVoidOperation_;
  SilKit::Services::Rpc::IRpcClient* rpc_client_test_MyOperation_;
  SilKit::Services::Rpc::IRpcClient* rpc_client_test_MyGetter_;
  SilKit::Services::Rpc::IRpcClient* rpc_client_test_MySetter_;
};


} // namespace test

#endif // TEST_MY_CONSUMER_MODULE_H
