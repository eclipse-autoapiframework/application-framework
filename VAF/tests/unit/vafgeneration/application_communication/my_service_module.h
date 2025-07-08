/*!********************************************************************************************************************
 *  COPYRIGHT
 *  -------------------------------------------------------------------------------------------------------------------
 *  \verbatim
 *  Copyright (c) 2025 by Vector Informatik GmbH. All rights reserved.
 *
 *                This software is copyright protected and proprietary to Vector Informatik GmbH.
 *                Vector Informatik GmbH grants to you only those rights as set out in the license conditions.
 *                All other rights remain with Vector Informatik GmbH.
 *  \endverbatim
 *  -------------------------------------------------------------------------------------------------------------------
 *  FILE DESCRIPTION
 *  -----------------------------------------------------------------------------------------------------------------*/
/*!        \file  my_service_module.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef TEST_MY_SERVICE_MODULE_H
#define TEST_MY_SERVICE_MODULE_H

#include <memory>
#include <string>
#include <vector>

#include "vaf/receiver_handler_container.h"
#include "vaf/controller_interface.h"
#include "vaf/data_ptr.h"
#include "vaf/executable_controller_interface.h"
#include "vaf/result.h"

#include "test/my_interface_consumer.h"
#include "test/my_interface_provider.h"

namespace test {


class MyServiceModule
    : public test::MyInterfaceConsumer, public test::MyInterfaceProvider, public vaf::ControlInterface {
 public:
  MyServiceModule(vaf::Executor& executor, std::string name, std::vector<std::string> dependencies, vaf::ExecutableControllerInterface& executable_controller_interface);
  ~MyServiceModule() override = default;

  MyServiceModule(const MyServiceModule&) = delete;
  MyServiceModule(MyServiceModule&&) = delete;
  MyServiceModule& operator=(const MyServiceModule&) = delete;
  MyServiceModule& operator=(MyServiceModule&&) = delete;

  vaf::Result<void> Init() noexcept override;
  void Start() noexcept override;
  void Stop() noexcept override;
  void DeInit() noexcept override;
  void StartEventHandlerForModule(const std::string& module) override;
  void StopEventHandlerForModule(const std::string& module) override;

  ::vaf::Result<::vaf::ConstDataPtr<const std::uint64_t>> GetAllocated_my_data_element1() override;
  std::uint64_t Get_my_data_element1() override;
  void RegisterDataElementHandler_my_data_element1(std::string owner, std::function<void(const ::vaf::ConstDataPtr<const std::uint64_t>)>&& f) override;

  ::vaf::Result<::vaf::DataPtr<std::uint64_t>> Allocate_my_data_element1() override;
  ::vaf::Result<void> SetAllocated_my_data_element1(::vaf::DataPtr<std::uint64_t>&& data) override;
  ::vaf::Result<void> Set_my_data_element1(const std::uint64_t& data) override;
  ::vaf::Result<::vaf::ConstDataPtr<const std::uint64_t>> GetAllocated_my_data_element2() override;
  std::uint64_t Get_my_data_element2() override;
  void RegisterDataElementHandler_my_data_element2(std::string owner, std::function<void(const ::vaf::ConstDataPtr<const std::uint64_t>)>&& f) override;

  ::vaf::Result<::vaf::DataPtr<std::uint64_t>> Allocate_my_data_element2() override;
  ::vaf::Result<void> SetAllocated_my_data_element2(::vaf::DataPtr<std::uint64_t>&& data) override;
  ::vaf::Result<void> Set_my_data_element2(const std::uint64_t& data) override;

  ::vaf::Future<void> MyVoidOperation(const std::uint64_t& in) override;
  void RegisterOperationHandler_MyVoidOperation(std::function<void(const std::uint64_t&)>&& f) override;
  ::vaf::Future<test::MyOperation::Output> MyOperation(const std::uint64_t& in, const std::uint64_t& inout) override;
  void RegisterOperationHandler_MyOperation(std::function<test::MyOperation::Output(const std::uint64_t&, const std::uint64_t&)>&& f) override;

 private:
  vaf::ModuleExecutor& executor_;
  std::vector<std::string> active_modules_;

  vaf::ConstDataPtr<const std::uint64_t> my_data_element1_sample_{std::make_unique<std::uint64_t>()};
  std::vector<vaf::ReceiverHandlerContainer<std::function<void(const ::vaf::ConstDataPtr<const std::uint64_t>)>>> my_data_element1_handlers_;
  vaf::ConstDataPtr<const std::uint64_t> my_data_element2_sample_{std::make_unique<std::uint64_t>()};
  std::vector<vaf::ReceiverHandlerContainer<std::function<void(const ::vaf::ConstDataPtr<const std::uint64_t>)>>> my_data_element2_handlers_;

  std::function<void(const std::uint64_t&)> MyVoidOperation_handler_;
  std::function<test::MyOperation::Output(const std::uint64_t&, const std::uint64_t&)> MyOperation_handler_;

};


} // namespace test

#endif // TEST_MY_SERVICE_MODULE_H
