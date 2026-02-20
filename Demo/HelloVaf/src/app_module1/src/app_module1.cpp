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
/*!        \file  app_module1.cpp
 *         \brief
 *
 *********************************************************************************************************************/

#include "demo/app_module1.h"

namespace demo {

/*
  Generated based on configuration in ../../model/app_module1.py

  Provider interfaces
  ===================
    Data element API example for Message of type vaf::String
     - ::vaf::Result<::vaf::DataPtr<vaf::String>> Allocate_Message()
     - ::vaf::Result<void> SetAllocated_Message(::vaf::DataPtr<vaf::String>&& data)
     - ::vaf::Result<void> Set_Message(const vaf::String& data)

    - HelloWorldProvider_ : demo::HelloWorldIfProvider
      - Data elements
        - Message : vaf::String
      - Operations
        - void RegisterOperationHandler_SetMsgId(std::function<void(const std::uint8_t&)>&& f)
*/

/**********************************************************************************************************************
  Constructor
**********************************************************************************************************************/
AppModule1::AppModule1(ConstructorToken&& token) : AppModule1Base(std::move(token)) {
  HelloWorldProvider_->RegisterOperationHandler_SetMsgId(
      [this](const std::uint8_t& msg_id) { msg_id_ = static_cast<uint8_t>(msg_id); });
}

/**********************************************************************************************************************
  1 periodic task(s)
**********************************************************************************************************************/
// Task with name PeriodicTask and a period of 500ms.
void AppModule1::PeriodicTask() {
  std::string myMsg = "Hello, VAF! - MsgID: " + std::to_string(msg_id_);
  HelloWorldProvider_->Set_Message(myMsg.c_str());
}

//vaf::Result<void> AppModule1::Init() {
//  return vaf::Result<void>{};
//}
//void AppModule1::Start() {
//  ReportOperational();
//}
//void AppModule1::Stop() {}
//void AppModule1::DeInit() {}
//void AppModule1::OnError(const vaf::Error& error) {
//  static_cast<void>(error);
//}

}  // namespace demo
