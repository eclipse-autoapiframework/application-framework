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
/*!        \file  app_module2.cpp
 *         \brief
 *
 *********************************************************************************************************************/

#include "demo/app_module2.h"
#include "vaf/output_sync_stream.h"

namespace demo {

/*
  Generated based on configuration in ../../model/app_module2.py

  Consumer interfaces
  ===================
    Data element API example for Message of type vaf::String
      - ::vaf::Result<::vaf::ConstDataPtr<const vaf::String>> GetAllocated_Message()
      - vaf::String Get_Message()
      - void RegisterDataElementHandler_Message(vaf::String owner, std::function<void(const ::vaf::ConstDataPtr<const vaf::String>)>&& f)

    - HelloWorldConsumer_ : demo::HelloWorldIfConsumer
      - Data elements
        - Message : vaf::String
      - Operations
        - ::vaf::Future<void> SetMsgId(const std::uint8_t& MsgId)
*/

/**********************************************************************************************************************
  Constructor
**********************************************************************************************************************/
AppModule2::AppModule2(ConstructorToken&& token) : AppModule2Base(std::move(token)) {
  HelloWorldConsumer_->RegisterDataElementHandler_Message(
      GetName(), [](const auto& hello_text) { vaf::OutputSyncStream{} << "Received: " << *hello_text << std::endl; });
}

/**********************************************************************************************************************
  1 periodic task(s)
**********************************************************************************************************************/
// Task with name PeriodicTask and a period of 1000ms.
void AppModule2::PeriodicTask() {
  static uint8_t msg_id = 0;
  HelloWorldConsumer_->SetMsgId(msg_id++);
}

//vaf::Result<void> AppModule2::Init() {
//  return vaf::Result<void>{};
//}
//void AppModule2::Start() {
//  ReportOperational();
//}
//void AppModule2::Stop() {}
//void AppModule2::DeInit() {}
//void AppModule2::OnError(const vaf::Error& error) {
//  static_cast<void>(error);
//}

}  // namespace demo
