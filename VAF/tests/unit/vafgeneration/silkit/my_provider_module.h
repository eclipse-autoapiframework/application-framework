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
/*!        \file  my_provider_module.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef TEST_MY_PROVIDER_MODULE_H
#define TEST_MY_PROVIDER_MODULE_H

#include <memory>
#include "vaf/container_types.h"
#include "vaf/controller_interface.h"
#include "vaf/data_ptr.h"
#include "vaf/executable_controller_interface.h"
#include "vaf/result.h"

#include "silkit/SilKit.hpp"
#include "silkit/services/all.hpp"
#include "silkit/services/orchestration/string_utils.hpp"
#include "silkit/util/serdes/Serialization.hpp"
#include "protobuf_interface_test_MyInterface.pb.h"

#include "test/my_interface_provider.h"

namespace test {

class MyProviderModule final : public test::MyInterfaceProvider, public vaf::ControlInterface {
 public:
  explicit MyProviderModule(vaf::Executor& executor, vaf::String name, vaf::ExecutableControllerInterface& executable_controller_interface);
  ~MyProviderModule() override = default;

  vaf::Result<void> Init() noexcept override;
  void Start() noexcept override;
  void Stop() noexcept override;
  void DeInit() noexcept override;

  ::vaf::Result<::vaf::DataPtr<std::uint64_t>> Allocate_my_data_element1() override;
  ::vaf::Result<void> SetAllocated_my_data_element1(::vaf::DataPtr<std::uint64_t>&& data) override;
  ::vaf::Result<void> Set_my_data_element1(const std::uint64_t& data) override;
  ::vaf::Result<::vaf::DataPtr<std::uint64_t>> Allocate_my_data_element2() override;
  ::vaf::Result<void> SetAllocated_my_data_element2(::vaf::DataPtr<std::uint64_t>&& data) override;
  ::vaf::Result<void> Set_my_data_element2(const std::uint64_t& data) override;

  void RegisterOperationHandler_MyVoidOperation(std::function<void(const std::uint64_t&)>&& f) override;
  void RegisterOperationHandler_MyOperation(std::function<test::MyOperation::Output(const std::uint64_t&, const std::uint64_t&)>&& f) override;
  void RegisterOperationHandler_MyGetter(std::function<test::MyGetter::Output()>&& f) override;
  void RegisterOperationHandler_MySetter(std::function<void(const std::uint64_t&)>&& f) override;

 private:
  std::unique_ptr<SilKit::IParticipant> participant_;
  SilKit::Services::PubSub::IDataPublisher* publisher_test_my_data_element1_;
  SilKit::Services::PubSub::IDataPublisher* publisher_test_my_data_element2_;

  std::function<void(const std::uint64_t&)> CbkFunction_test_MyVoidOperation_{};
  SilKit::Services::Rpc::IRpcServer* server_test_MyVoidOperation_;
  std::function<test::MyOperation::Output(const std::uint64_t&, const std::uint64_t&)> CbkFunction_test_MyOperation_{};
  SilKit::Services::Rpc::IRpcServer* server_test_MyOperation_;
  std::function<test::MyGetter::Output()> CbkFunction_test_MyGetter_{};
  SilKit::Services::Rpc::IRpcServer* server_test_MyGetter_;
  std::function<void(const std::uint64_t&)> CbkFunction_test_MySetter_{};
  SilKit::Services::Rpc::IRpcServer* server_test_MySetter_;
};

} // namespace test

#endif // TEST_MY_PROVIDER_MODULE_H
