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
/*!        \file  my_service_module.cpp
 *         \brief
 *
 *********************************************************************************************************************/

#include "test/my_service_module.h"

#include "vaf/internal/data_ptr_helper.h"
#include "vaf/internal/promise.h"

namespace test {

MyServiceModule::MyServiceModule(vaf::Executor& executor, vaf::String name, vaf::Vector<vaf::String> dependencies, vaf::ExecutableControllerInterface& executable_controller_interface)
  : vaf::ControlInterface(std::move(name), std::move(dependencies), executable_controller_interface, executor),
    executor_{vaf::ControlInterface::executor_} {
}

vaf::Result<void> MyServiceModule::Init() noexcept {
  return vaf::Result<void>{};
}

void MyServiceModule::Start() noexcept {
  ReportOperational();
}

void MyServiceModule::Stop() noexcept {
}

void MyServiceModule::DeInit() noexcept  {
}

void MyServiceModule::StartEventHandlerForModule(const vaf::String& module) {
  for(auto& handler_container : my_data_element1_handlers_) {
    if(handler_container.owner_ == module) {
      handler_container.is_active_ = true;
    }
  }
  for(auto& handler_container : my_data_element2_handlers_) {
    if(handler_container.owner_ == module) {
      handler_container.is_active_ = true;
    }
  }

  active_modules_.push_back(module);
}

void MyServiceModule::StopEventHandlerForModule(const vaf::String& module) {
  for(auto& handler_container : my_data_element1_handlers_) {
    if(handler_container.owner_ == module) {
      handler_container.is_active_ = false;
    }
  }
  for(auto& handler_container : my_data_element2_handlers_) {
    if(handler_container.owner_ == module) {
      handler_container.is_active_ = false;
    }
  }

  active_modules_.erase(std::remove(active_modules_.begin(), active_modules_.end(), module));
}


::vaf::Result<::vaf::ConstDataPtr<const std::uint64_t>> MyServiceModule::GetAllocated_my_data_element1() {
  return vaf::Result<vaf::ConstDataPtr<const std::uint64_t >>::FromValue( my_data_element1_sample_);
}

std::uint64_t MyServiceModule::Get_my_data_element1() { return *my_data_element1_sample_; }

void MyServiceModule::RegisterDataElementHandler_my_data_element1(vaf::String owner, std::function<void(const ::vaf::ConstDataPtr<const std::uint64_t>)>&& f) {
  StartEventHandlerForModule(owner);
  my_data_element1_handlers_.emplace_back(owner, std::move(f));
  if(std::find(active_modules_.begin(), active_modules_.end(), owner) != active_modules_.end()) {
    my_data_element1_handlers_.back().is_active_ = true;
  }
}

::vaf::Result<::vaf::DataPtr<std::uint64_t>> MyServiceModule::Allocate_my_data_element1() {
  std::unique_ptr< std::uint64_t > ptr{
      std::make_unique< std::uint64_t >()};
  return ::vaf::Result<vaf::DataPtr< std::uint64_t >>::FromValue(std::move(ptr));
}

::vaf::Result<void> MyServiceModule::SetAllocated_my_data_element1(::vaf::DataPtr<std::uint64_t>&& data) {
  my_data_element1_sample_ = vaf::ConstDataPtr<const std::uint64_t>{std::move(vaf::internal::DataPtrHelper<std::uint64_t>::getRawPtr(data))};

  for(auto& handler_container : my_data_element1_handlers_) {
    if(handler_container.is_active_) {
      handler_container.handler_(my_data_element1_sample_);
    }
  }

  return vaf::Result<void>{};
}

::vaf::Result<void> MyServiceModule::Set_my_data_element1(const std::uint64_t& data) {
  std::unique_ptr< std::uint64_t > ptr{
      std::make_unique< std::uint64_t >(data)};
  my_data_element1_sample_ = vaf::ConstDataPtr<const std::uint64_t>{std::move(ptr)};

  for(auto& handler_container : my_data_element1_handlers_) {
    if(handler_container.is_active_) {
      handler_container.handler_(my_data_element1_sample_);
    }
  }

  return vaf::Result<void>{};
}

::vaf::Result<::vaf::ConstDataPtr<const std::uint64_t>> MyServiceModule::GetAllocated_my_data_element2() {
  return vaf::Result<vaf::ConstDataPtr<const std::uint64_t >>::FromValue( my_data_element2_sample_);
}

std::uint64_t MyServiceModule::Get_my_data_element2() { return *my_data_element2_sample_; }

void MyServiceModule::RegisterDataElementHandler_my_data_element2(vaf::String owner, std::function<void(const ::vaf::ConstDataPtr<const std::uint64_t>)>&& f) {
  StartEventHandlerForModule(owner);
  my_data_element2_handlers_.emplace_back(owner, std::move(f));
  if(std::find(active_modules_.begin(), active_modules_.end(), owner) != active_modules_.end()) {
    my_data_element2_handlers_.back().is_active_ = true;
  }
}

::vaf::Result<::vaf::DataPtr<std::uint64_t>> MyServiceModule::Allocate_my_data_element2() {
  std::unique_ptr< std::uint64_t > ptr{
      std::make_unique< std::uint64_t >()};
  return ::vaf::Result<vaf::DataPtr< std::uint64_t >>::FromValue(std::move(ptr));
}

::vaf::Result<void> MyServiceModule::SetAllocated_my_data_element2(::vaf::DataPtr<std::uint64_t>&& data) {
  my_data_element2_sample_ = vaf::ConstDataPtr<const std::uint64_t>{std::move(vaf::internal::DataPtrHelper<std::uint64_t>::getRawPtr(data))};

  for(auto& handler_container : my_data_element2_handlers_) {
    if(handler_container.is_active_) {
      handler_container.handler_(my_data_element2_sample_);
    }
  }

  return vaf::Result<void>{};
}

::vaf::Result<void> MyServiceModule::Set_my_data_element2(const std::uint64_t& data) {
  std::unique_ptr< std::uint64_t > ptr{
      std::make_unique< std::uint64_t >(data)};
  my_data_element2_sample_ = vaf::ConstDataPtr<const std::uint64_t>{std::move(ptr)};

  for(auto& handler_container : my_data_element2_handlers_) {
    if(handler_container.is_active_) {
      handler_container.handler_(my_data_element2_sample_);
    }
  }

  return vaf::Result<void>{};
}


void MyServiceModule::RegisterOperationHandler_MyVoidOperation(std::function<void(const std::uint64_t&)>&& f) {
  MyVoidOperation_handler_ = std::move(f);
}

::vaf::Future<void> MyServiceModule::MyVoidOperation(const std::uint64_t& in) {
  ::vaf::internal::Promise<void> p;

  if(MyVoidOperation_handler_) {
    MyVoidOperation_handler_(in);
    p.set_value();
  } else {
    vaf::Error error_code{::vaf::ErrorCode::kNotOk, "No operation handler registered for MyVoidOperation."};
    vaf::internal::SetVafErrorCodeToPromise(p, error_code);
  }

  return ::vaf::internal::CreateVafFutureFromVafPromise<void>(p);
}

void MyServiceModule::RegisterOperationHandler_MyOperation(std::function<test::MyOperation::Output(const std::uint64_t&, const std::uint64_t&)>&& f) {
  MyOperation_handler_ = std::move(f);
}

::vaf::Future<test::MyOperation::Output> MyServiceModule::MyOperation(const std::uint64_t& in, const std::uint64_t& inout) {
  ::vaf::internal::Promise<test::MyOperation::Output> p;

  if(MyOperation_handler_) {
    p.set_value(MyOperation_handler_(in, inout));
  } else {
    vaf::Error error_code{::vaf::ErrorCode::kNotOk, "No operation handler registered for MyOperation."};
    vaf::internal::SetVafErrorCodeToPromise(p, error_code);
  }

  return ::vaf::internal::CreateVafFutureFromVafPromise<test::MyOperation::Output>(p);
}

} // namespace test
