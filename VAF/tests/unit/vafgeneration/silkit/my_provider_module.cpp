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
/*!        \file  my_provider_module.cpp
 *         \brief
 *
 *********************************************************************************************************************/

#include "test/my_provider_module.h"

#include <cstdlib>
#include <google/protobuf/serial_arena.h>
#include <memory>

#include "vaf/internal/data_ptr_helper.h"
#include "vaf/result.h"
#include "vaf/controller_interface.h"
#include "vaf/error_domain.h"
#include "protobuf/interface/test/myinterface/protobuf_transformer.h"

namespace test {

MyProviderModule::MyProviderModule(vaf::Executor& executor, vaf::String name, vaf::ExecutableControllerInterface& executable_controller_interface)
  	: vaf::ControlInterface(std::move(name), {}, executable_controller_interface, executor) {
}

vaf::Result<void> MyProviderModule::Init() noexcept {
  return vaf::Result<void>{};
}

void MyProviderModule::Start() noexcept {
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
  participant_ = SilKit::CreateParticipant(config, "test_MyProviderModule", registry_uri);

  SilKit::Services::PubSub::PubSubSpec pubsubspec_test_my_data_element1{"MyInterface_my_data_element1", "application/protobuf"};
  pubsubspec_test_my_data_element1.AddLabel("Instance", "MyInterface", SilKit::Services::MatchingLabel::Kind::Mandatory);
  publisher_test_my_data_element1_= participant_->CreateDataPublisher("Publisher_test_my_data_element1", pubsubspec_test_my_data_element1);

  SilKit::Services::PubSub::PubSubSpec pubsubspec_test_my_data_element2{"MyInterface_my_data_element2", "application/protobuf"};
  pubsubspec_test_my_data_element2.AddLabel("Instance", "MyInterface", SilKit::Services::MatchingLabel::Kind::Mandatory);
  publisher_test_my_data_element2_= participant_->CreateDataPublisher("Publisher_test_my_data_element2", pubsubspec_test_my_data_element2);


  SilKit::Services::Rpc::RpcSpec rpcspec_test_MyVoidOperation{"MyInterface_MyVoidOperation", "application/protobuf"};
  rpcspec_test_MyVoidOperation.AddLabel("Instance", "MyInterface", SilKit::Services::MatchingLabel::Kind::Mandatory);
  auto RemoteFunc_test_MyVoidOperation = [&](auto* server, const auto& event) {
    protobuf::interface::test::MyInterface::MyVoidOperation_in deserialized;
    deserialized.ParseFromArray(event.argumentData.data(), event.argumentData.size());
    std::uint64_t in{};
    protobuf::interface::test::MyInterface::MyVoidOperationInProtoToVaf(deserialized, in);
    if (CbkFunction_test_MyVoidOperation_) {
      CbkFunction_test_MyVoidOperation_(in);
    }
    protobuf::interface::test::MyInterface::MyVoidOperation_out request;
    size_t nbytes = request.ByteSizeLong();
    std::vector<std::uint8_t> serialized(nbytes);
    if (nbytes != 0u) {
      request.SerializeToArray(serialized.data(), nbytes);
    }
    server->SubmitResult(event.callHandle, serialized);
  };
  server_test_MyVoidOperation_= participant_->CreateRpcServer("test::MyVoidOperation", rpcspec_test_MyVoidOperation, RemoteFunc_test_MyVoidOperation);

  SilKit::Services::Rpc::RpcSpec rpcspec_test_MyOperation{"MyInterface_MyOperation", "application/protobuf"};
  rpcspec_test_MyOperation.AddLabel("Instance", "MyInterface", SilKit::Services::MatchingLabel::Kind::Mandatory);
  auto RemoteFunc_test_MyOperation = [&](auto* server, const auto& event) {
    protobuf::interface::test::MyInterface::MyOperation_in deserialized;
    deserialized.ParseFromArray(event.argumentData.data(), event.argumentData.size());
    std::uint64_t in{};
    std::uint64_t inout{};
    protobuf::interface::test::MyInterface::MyOperationInProtoToVaf(deserialized, in, inout);
    test::MyOperation::Output result;
    if (CbkFunction_test_MyOperation_) {
      result = CbkFunction_test_MyOperation_(in, inout);
    }
    protobuf::interface::test::MyInterface::MyOperation_out request;
    protobuf::interface::test::MyInterface::MyOperationOutVafToProto(result, request);
    size_t nbytes = request.ByteSizeLong();
    std::vector<std::uint8_t> serialized(nbytes);
    if (nbytes != 0u) {
      request.SerializeToArray(serialized.data(), nbytes);
    }
    server->SubmitResult(event.callHandle, serialized);
  };
  server_test_MyOperation_= participant_->CreateRpcServer("test::MyOperation", rpcspec_test_MyOperation, RemoteFunc_test_MyOperation);

  SilKit::Services::Rpc::RpcSpec rpcspec_test_MyGetter{"MyInterface_MyGetter", "application/protobuf"};
  rpcspec_test_MyGetter.AddLabel("Instance", "MyInterface", SilKit::Services::MatchingLabel::Kind::Mandatory);
  auto RemoteFunc_test_MyGetter = [&](auto* server, const auto& event) {
    protobuf::interface::test::MyInterface::MyGetter_in deserialized;
    deserialized.ParseFromArray(event.argumentData.data(), event.argumentData.size());
    test::MyGetter::Output result;
    if (CbkFunction_test_MyGetter_) {
      result = CbkFunction_test_MyGetter_();
    }
    protobuf::interface::test::MyInterface::MyGetter_out request;
    protobuf::interface::test::MyInterface::MyGetterOutVafToProto(result, request);
    size_t nbytes = request.ByteSizeLong();
    std::vector<std::uint8_t> serialized(nbytes);
    if (nbytes != 0u) {
      request.SerializeToArray(serialized.data(), nbytes);
    }
    server->SubmitResult(event.callHandle, serialized);
  };
  server_test_MyGetter_= participant_->CreateRpcServer("test::MyGetter", rpcspec_test_MyGetter, RemoteFunc_test_MyGetter);

  SilKit::Services::Rpc::RpcSpec rpcspec_test_MySetter{"MyInterface_MySetter", "application/protobuf"};
  rpcspec_test_MySetter.AddLabel("Instance", "MyInterface", SilKit::Services::MatchingLabel::Kind::Mandatory);
  auto RemoteFunc_test_MySetter = [&](auto* server, const auto& event) {
    protobuf::interface::test::MyInterface::MySetter_in deserialized;
    deserialized.ParseFromArray(event.argumentData.data(), event.argumentData.size());
    std::uint64_t a{};
    protobuf::interface::test::MyInterface::MySetterInProtoToVaf(deserialized, a);
    if (CbkFunction_test_MySetter_) {
      CbkFunction_test_MySetter_(a);
    }
    protobuf::interface::test::MyInterface::MySetter_out request;
    size_t nbytes = request.ByteSizeLong();
    std::vector<std::uint8_t> serialized(nbytes);
    if (nbytes != 0u) {
      request.SerializeToArray(serialized.data(), nbytes);
    }
    server->SubmitResult(event.callHandle, serialized);
  };
  server_test_MySetter_= participant_->CreateRpcServer("test::MySetter", rpcspec_test_MySetter, RemoteFunc_test_MySetter);

  ReportOperational();
}

void MyProviderModule::Stop() noexcept {
}

void MyProviderModule::DeInit() noexcept {
}

::vaf::Result<::vaf::DataPtr<std::uint64_t>> MyProviderModule::Allocate_my_data_element1() {
  std::unique_ptr< std::uint64_t > ptr{
      std::make_unique< std::uint64_t >()};
  return ::vaf::Result<vaf::DataPtr< std::uint64_t >>::FromValue(std::move(ptr));
}

::vaf::Result<void> MyProviderModule::SetAllocated_my_data_element1(::vaf::DataPtr<std::uint64_t>&& data) {
  protobuf::interface::test::MyInterface::my_data_element1 request;
  protobuf::interface::test::MyInterface::my_data_element1VafToProto(*vaf::internal::DataPtrHelper<std::uint64_t>::getRawPtr(data), request);
  size_t nbytes = request.ByteSizeLong();
  std::vector<std::uint8_t> serialized(nbytes);
  if (nbytes != 0u) {
    request.SerializeToArray(serialized.data(), nbytes);
  }
  publisher_test_my_data_element1_->Publish(serialized);

  return ::vaf::Result<void>{};
}

::vaf::Result<void> MyProviderModule::Set_my_data_element1(const std::uint64_t& data) {
  protobuf::interface::test::MyInterface::my_data_element1 request;
  protobuf::interface::test::MyInterface::my_data_element1VafToProto(data, request);
  size_t nbytes = request.ByteSizeLong();
  std::vector<std::uint8_t> serialized(nbytes);
  if (nbytes != 0u) {
    request.SerializeToArray(serialized.data(), nbytes);
  }
  publisher_test_my_data_element1_->Publish(serialized);

  return ::vaf::Result<void>{};
}
::vaf::Result<::vaf::DataPtr<std::uint64_t>> MyProviderModule::Allocate_my_data_element2() {
  std::unique_ptr< std::uint64_t > ptr{
      std::make_unique< std::uint64_t >()};
  return ::vaf::Result<vaf::DataPtr< std::uint64_t >>::FromValue(std::move(ptr));
}

::vaf::Result<void> MyProviderModule::SetAllocated_my_data_element2(::vaf::DataPtr<std::uint64_t>&& data) {
  protobuf::interface::test::MyInterface::my_data_element2 request;
  protobuf::interface::test::MyInterface::my_data_element2VafToProto(*vaf::internal::DataPtrHelper<std::uint64_t>::getRawPtr(data), request);
  size_t nbytes = request.ByteSizeLong();
  std::vector<std::uint8_t> serialized(nbytes);
  if (nbytes != 0u) {
    request.SerializeToArray(serialized.data(), nbytes);
  }
  publisher_test_my_data_element2_->Publish(serialized);

  return ::vaf::Result<void>{};
}

::vaf::Result<void> MyProviderModule::Set_my_data_element2(const std::uint64_t& data) {
  protobuf::interface::test::MyInterface::my_data_element2 request;
  protobuf::interface::test::MyInterface::my_data_element2VafToProto(data, request);
  size_t nbytes = request.ByteSizeLong();
  std::vector<std::uint8_t> serialized(nbytes);
  if (nbytes != 0u) {
    request.SerializeToArray(serialized.data(), nbytes);
  }
  publisher_test_my_data_element2_->Publish(serialized);

  return ::vaf::Result<void>{};
}

void MyProviderModule::RegisterOperationHandler_MyVoidOperation(std::function<void(const std::uint64_t&)>&& f) {
  CbkFunction_test_MyVoidOperation_ = std::move(f);
}

void MyProviderModule::RegisterOperationHandler_MyOperation(std::function<test::MyOperation::Output(const std::uint64_t&, const std::uint64_t&)>&& f) {
  CbkFunction_test_MyOperation_ = std::move(f);
}

void MyProviderModule::RegisterOperationHandler_MyGetter(std::function<test::MyGetter::Output()>&& f) {
  CbkFunction_test_MyGetter_ = std::move(f);
}

void MyProviderModule::RegisterOperationHandler_MySetter(std::function<void(const std::uint64_t&)>&& f) {
  CbkFunction_test_MySetter_ = std::move(f);
}


} // namespace test
