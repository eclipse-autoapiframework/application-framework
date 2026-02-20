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
/*!        \file  my_consumer_module.cpp
 *         \brief
 *
 *********************************************************************************************************************/

#include "test/my_consumer_module.h"

#include <chrono>
#include <cstdlib>
#include <google/protobuf/serial_arena.h>

#include "vaf/error_domain.h"
#include "vaf/future.h"
#include "vaf/internal/promise.h"
#include "protobuf/interface/test/myinterface/protobuf_transformer.h"

namespace test {

MyConsumerModule::MyConsumerModule(::vaf::Executor& executor, vaf::String name, ::vaf::ExecutableControllerInterface& executable_controller_interface)
  : ::vaf::ControlInterface(std::move(name), {}, executable_controller_interface, executor),
    executor_{ControlInterface::executor_} {
}

::vaf::Result<void> MyConsumerModule::Init() noexcept {
  return ::vaf::Result<void>{};
}

void MyConsumerModule::Start() noexcept {
  const char* value = std::getenv("SILKIT_REGISTRY_URI");
  const auto registry_uri = (value != nullptr) ? std::string(value) : "silkit://localhost:8501";

  const std::string participant_config_text = R"(
  Description: My participant configuration
  Logging:
      Sinks:
      - Type: Stdout
        Level: Info
  )";
  auto config = SilKit::Config::ParticipantConfigurationFromString(participant_config_text);
  participant_ = SilKit::CreateParticipant(config, "test_MyConsumerModule", registry_uri);

  SilKit::Services::PubSub::PubSubSpec pubsubspec_test_my_data_element1{"MyInterface_my_data_element1", "application/protobuf"};
  pubsubspec_test_my_data_element1.AddLabel("Instance", "MyInterface", SilKit::Services::MatchingLabel::Kind::Mandatory);
  auto receptionHandler_test_my_data_element1 = [&](auto* subscriber, const auto& dataMessageEvent) {
    const std::lock_guard<std::mutex> lock(cached_test_my_data_element1_mutex_);

    std::unique_ptr< std::uint64_t > ptr;
    protobuf::interface::test::MyInterface::my_data_element1  deserialized;
    deserialized.ParseFromArray( dataMessageEvent.data.data(), dataMessageEvent.data.size() );
    ptr = std::make_unique< std::uint64_t >();
    ::protobuf::interface::test::MyInterface::my_data_element1ProtoToVaf(deserialized,*ptr);
    this->cached_test_my_data_element1_ = vaf::ConstDataPtr<const std::uint64_t>{std::move(ptr)};

    for(auto& handler_container : registered_test_my_data_element1_event_handlers_) {
      if(handler_container.is_active_) {
        handler_container.handler_(cached_test_my_data_element1_);
      }
    }
  };
  subscriber_test_my_data_element1_= participant_->CreateDataSubscriber("Subscriber_test_my_data_element1", pubsubspec_test_my_data_element1, receptionHandler_test_my_data_element1);

  SilKit::Services::PubSub::PubSubSpec pubsubspec_test_my_data_element2{"MyInterface_my_data_element2", "application/protobuf"};
  pubsubspec_test_my_data_element2.AddLabel("Instance", "MyInterface", SilKit::Services::MatchingLabel::Kind::Mandatory);
  auto receptionHandler_test_my_data_element2 = [&](auto* subscriber, const auto& dataMessageEvent) {
    const std::lock_guard<std::mutex> lock(cached_test_my_data_element2_mutex_);

    std::unique_ptr< std::uint64_t > ptr;
    protobuf::interface::test::MyInterface::my_data_element2  deserialized;
    deserialized.ParseFromArray( dataMessageEvent.data.data(), dataMessageEvent.data.size() );
    ptr = std::make_unique< std::uint64_t >();
    ::protobuf::interface::test::MyInterface::my_data_element2ProtoToVaf(deserialized,*ptr);
    this->cached_test_my_data_element2_ = vaf::ConstDataPtr<const std::uint64_t>{std::move(ptr)};

    for(auto& handler_container : registered_test_my_data_element2_event_handlers_) {
      if(handler_container.is_active_) {
        handler_container.handler_(cached_test_my_data_element2_);
      }
    }
  };
  subscriber_test_my_data_element2_= participant_->CreateDataSubscriber("Subscriber_test_my_data_element2", pubsubspec_test_my_data_element2, receptionHandler_test_my_data_element2);


  SilKit::Services::Rpc::RpcSpec rpcspec_test_MyVoidOperation{"MyInterface_MyVoidOperation", "application/protobuf"};
  rpcspec_test_MyVoidOperation.AddLabel("Instance", "MyInterface", SilKit::Services::MatchingLabel::Kind::Mandatory);
  auto ReturnFunc_test_MyVoidOperation = [&](auto* /*client*/, const auto& event) {
    ::vaf::internal::Promise<void>*
        promise_pointer = static_cast<
          ::vaf::internal::Promise<void>*>(
            event.userContext);
    if (event.callStatus == SilKit::Services::Rpc::RpcCallStatus::Success) {
      promise_pointer->set_value();
    } else {
      vaf::Error error_code{::vaf::ErrorCode::kNotOk, "Rpc call failed"};
      vaf::internal::SetVafErrorCodeToPromise(*promise_pointer, error_code);
    }
    delete promise_pointer;
  };
  rpc_client_test_MyVoidOperation_= participant_->CreateRpcClient("test_MyVoidOperation", rpcspec_test_MyVoidOperation, ReturnFunc_test_MyVoidOperation);

  SilKit::Services::Rpc::RpcSpec rpcspec_test_MyOperation{"MyInterface_MyOperation", "application/protobuf"};
  rpcspec_test_MyOperation.AddLabel("Instance", "MyInterface", SilKit::Services::MatchingLabel::Kind::Mandatory);
  auto ReturnFunc_test_MyOperation = [&](auto* /*client*/, const auto& event) {
    ::vaf::internal::Promise<test::MyOperation::Output>*
        promise_pointer = static_cast<
          ::vaf::internal::Promise<test::MyOperation::Output>*>(
            event.userContext);
    if (event.callStatus == SilKit::Services::Rpc::RpcCallStatus::Success) {
      test::MyOperation::Output output;
      protobuf::interface::test::MyInterface::MyOperation_out deserialized;
      deserialized.ParseFromArray( event.resultData.data(), event.resultData.size() );
      ::protobuf::interface::test::MyInterface::MyOperationOutProtoToVaf(deserialized, output);
      promise_pointer->set_value(output);
    } else {
      vaf::Error error_code{::vaf::ErrorCode::kNotOk, "Rpc call failed"};
      vaf::internal::SetVafErrorCodeToPromise(*promise_pointer, error_code);
    }
    delete promise_pointer;
  };
  rpc_client_test_MyOperation_= participant_->CreateRpcClient("test_MyOperation", rpcspec_test_MyOperation, ReturnFunc_test_MyOperation);

  SilKit::Services::Rpc::RpcSpec rpcspec_test_MyGetter{"MyInterface_MyGetter", "application/protobuf"};
  rpcspec_test_MyGetter.AddLabel("Instance", "MyInterface", SilKit::Services::MatchingLabel::Kind::Mandatory);
  auto ReturnFunc_test_MyGetter = [&](auto* /*client*/, const auto& event) {
    ::vaf::internal::Promise<test::MyGetter::Output>*
        promise_pointer = static_cast<
          ::vaf::internal::Promise<test::MyGetter::Output>*>(
            event.userContext);
    if (event.callStatus == SilKit::Services::Rpc::RpcCallStatus::Success) {
      test::MyGetter::Output output;
      protobuf::interface::test::MyInterface::MyGetter_out deserialized;
      deserialized.ParseFromArray( event.resultData.data(), event.resultData.size() );
      ::protobuf::interface::test::MyInterface::MyGetterOutProtoToVaf(deserialized, output);
      promise_pointer->set_value(output);
    } else {
      vaf::Error error_code{::vaf::ErrorCode::kNotOk, "Rpc call failed"};
      vaf::internal::SetVafErrorCodeToPromise(*promise_pointer, error_code);
    }
    delete promise_pointer;
  };
  rpc_client_test_MyGetter_= participant_->CreateRpcClient("test_MyGetter", rpcspec_test_MyGetter, ReturnFunc_test_MyGetter);

  SilKit::Services::Rpc::RpcSpec rpcspec_test_MySetter{"MyInterface_MySetter", "application/protobuf"};
  rpcspec_test_MySetter.AddLabel("Instance", "MyInterface", SilKit::Services::MatchingLabel::Kind::Mandatory);
  auto ReturnFunc_test_MySetter = [&](auto* /*client*/, const auto& event) {
    ::vaf::internal::Promise<void>*
        promise_pointer = static_cast<
          ::vaf::internal::Promise<void>*>(
            event.userContext);
    if (event.callStatus == SilKit::Services::Rpc::RpcCallStatus::Success) {
      promise_pointer->set_value();
    } else {
      vaf::Error error_code{::vaf::ErrorCode::kNotOk, "Rpc call failed"};
      vaf::internal::SetVafErrorCodeToPromise(*promise_pointer, error_code);
    }
    delete promise_pointer;
  };
  rpc_client_test_MySetter_= participant_->CreateRpcClient("test_MySetter", rpcspec_test_MySetter, ReturnFunc_test_MySetter);

  ReportOperational();
}

void MyConsumerModule::Stop() noexcept {
}

void MyConsumerModule::DeInit() noexcept {
}

void MyConsumerModule::StartEventHandlerForModule(const vaf::String& module) {
  for(auto& handler_container : registered_test_my_data_element1_event_handlers_) {
    if(handler_container.owner_ == module) {
      handler_container.is_active_ = true;
    }
  }
  for(auto& handler_container : registered_test_my_data_element2_event_handlers_) {
    if(handler_container.owner_ == module) {
      handler_container.is_active_ = true;
    }
  }
  active_modules_.push_back(module);
}

void MyConsumerModule::StopEventHandlerForModule(const vaf::String& module) {
  for(auto& handler_container : registered_test_my_data_element1_event_handlers_) {
    if(handler_container.owner_ == module) {
      handler_container.is_active_ = false;
    }
  }
  for(auto& handler_container : registered_test_my_data_element2_event_handlers_) {
    if(handler_container.owner_ == module) {
      handler_container.is_active_ = false;
    }
  }
  active_modules_.erase(std::remove(active_modules_.begin(), active_modules_.end(), module));
}


::vaf::Result<::vaf::ConstDataPtr<const std::uint64_t>> MyConsumerModule::GetAllocated_my_data_element1() {
  ::vaf::Result<::vaf::ConstDataPtr<const std::uint64_t>> result_value{
      ::vaf::Error{::vaf::ErrorCode::kNotOk, "No sample available"}};
  const std::lock_guard<std::mutex> lock(cached_test_my_data_element1_mutex_);
  if (cached_test_my_data_element1_) {
    result_value = ::vaf::Result<::vaf::ConstDataPtr<const std::uint64_t>>{cached_test_my_data_element1_};
  }
  return result_value;
}

std::uint64_t MyConsumerModule::Get_my_data_element1() {
  std::uint64_t return_value{};
  const std::lock_guard<std::mutex> lock(cached_test_my_data_element1_mutex_);
  if (cached_test_my_data_element1_) {
    return_value = *cached_test_my_data_element1_;
  }
  return return_value;
}

void MyConsumerModule::RegisterDataElementHandler_my_data_element1(vaf::String owner, std::function<void(const ::vaf::ConstDataPtr<const std::uint64_t>)>&& f) {
  registered_test_my_data_element1_event_handlers_.emplace_back(owner, std::move(f));
  if(std::find(active_modules_.begin(), active_modules_.end(), owner) != active_modules_.end()) {
    registered_test_my_data_element1_event_handlers_.back().is_active_ = true;
  }
}


::vaf::Result<::vaf::ConstDataPtr<const std::uint64_t>> MyConsumerModule::GetAllocated_my_data_element2() {
  ::vaf::Result<::vaf::ConstDataPtr<const std::uint64_t>> result_value{
      ::vaf::Error{::vaf::ErrorCode::kNotOk, "No sample available"}};
  const std::lock_guard<std::mutex> lock(cached_test_my_data_element2_mutex_);
  if (cached_test_my_data_element2_) {
    result_value = ::vaf::Result<::vaf::ConstDataPtr<const std::uint64_t>>{cached_test_my_data_element2_};
  }
  return result_value;
}

std::uint64_t MyConsumerModule::Get_my_data_element2() {
  std::uint64_t return_value{};
  const std::lock_guard<std::mutex> lock(cached_test_my_data_element2_mutex_);
  if (cached_test_my_data_element2_) {
    return_value = *cached_test_my_data_element2_;
  }
  return return_value;
}

void MyConsumerModule::RegisterDataElementHandler_my_data_element2(vaf::String owner, std::function<void(const ::vaf::ConstDataPtr<const std::uint64_t>)>&& f) {
  registered_test_my_data_element2_event_handlers_.emplace_back(owner, std::move(f));
  if(std::find(active_modules_.begin(), active_modules_.end(), owner) != active_modules_.end()) {
    registered_test_my_data_element2_event_handlers_.back().is_active_ = true;
  }
}



::vaf::Future<void> MyConsumerModule::MyVoidOperation(const std::uint64_t& in) {
  ::vaf::Future<void> return_value;
  ::vaf::internal::Promise<void>* promise_pointer =
                  new ::vaf::internal::Promise<void>();
  return_value = ::vaf::internal::CreateVafFutureFromVafPromise<void>(*promise_pointer);
  protobuf::interface::test::MyInterface::MyVoidOperation_in request;
  protobuf::interface::test::MyInterface::MyVoidOperationInVafToProto(in, request);
  size_t nbytes = request.ByteSizeLong();
  std::vector<std::uint8_t> serialized(nbytes);
  if (nbytes != 0u) {
    request.SerializeToArray(serialized.data(), nbytes);
  }
  rpc_client_test_MyVoidOperation_->Call(serialized, promise_pointer);

  return return_value;
}
::vaf::Future<test::MyOperation::Output> MyConsumerModule::MyOperation(const std::uint64_t& in, const std::uint64_t& inout) {
  ::vaf::Future<test::MyOperation::Output> return_value;
  ::vaf::internal::Promise<test::MyOperation::Output>* promise_pointer =
                  new ::vaf::internal::Promise<test::MyOperation::Output>();
  return_value = ::vaf::internal::CreateVafFutureFromVafPromise<test::MyOperation::Output>(*promise_pointer);
  protobuf::interface::test::MyInterface::MyOperation_in request;
  protobuf::interface::test::MyInterface::MyOperationInVafToProto(in, inout, request);
  size_t nbytes = request.ByteSizeLong();
  std::vector<std::uint8_t> serialized(nbytes);
  if (nbytes != 0u) {
    request.SerializeToArray(serialized.data(), nbytes);
  }
  rpc_client_test_MyOperation_->Call(serialized, promise_pointer);

  return return_value;
}
::vaf::Future<test::MyGetter::Output> MyConsumerModule::MyGetter() {
  ::vaf::Future<test::MyGetter::Output> return_value;
  ::vaf::internal::Promise<test::MyGetter::Output>* promise_pointer =
                  new ::vaf::internal::Promise<test::MyGetter::Output>();
  return_value = ::vaf::internal::CreateVafFutureFromVafPromise<test::MyGetter::Output>(*promise_pointer);
  protobuf::interface::test::MyInterface::MyGetter_in request;
  size_t nbytes = request.ByteSizeLong();
  std::vector<std::uint8_t> serialized(nbytes);
  if (nbytes != 0u) {
    request.SerializeToArray(serialized.data(), nbytes);
  }
  rpc_client_test_MyGetter_->Call(serialized, promise_pointer);

  return return_value;
}
::vaf::Future<void> MyConsumerModule::MySetter(const std::uint64_t& a) {
  ::vaf::Future<void> return_value;
  ::vaf::internal::Promise<void>* promise_pointer =
                  new ::vaf::internal::Promise<void>();
  return_value = ::vaf::internal::CreateVafFutureFromVafPromise<void>(*promise_pointer);
  protobuf::interface::test::MyInterface::MySetter_in request;
  protobuf::interface::test::MyInterface::MySetterInVafToProto(a, request);
  size_t nbytes = request.ByteSizeLong();
  std::vector<std::uint8_t> serialized(nbytes);
  if (nbytes != 0u) {
    request.SerializeToArray(serialized.data(), nbytes);
  }
  rpc_client_test_MySetter_->Call(serialized, promise_pointer);

  return return_value;
}

} // namespace test
