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
/*!        \file  user_controller.cpp
 *         \brief
 *
 *********************************************************************************************************************/

#include "user_controller.h"

#include "vaf/output_sync_stream.h"

std::unique_ptr<vaf::UserControllerInterface> CreateUserController() {
  return std::make_unique<UserController>();
}

void UserController::PreInitialize() {
 vaf::OutputSyncStream{} << "UserController::PreInitialize\n";
}

void UserController::PostInitialize() {
  vaf::OutputSyncStream{} << "UserController::PostInitialize\n";
}

void UserController::PreStart() {
  vaf::OutputSyncStream{} << "UserController::PreStart\n";
}

void UserController::PostStart() {
  vaf::OutputSyncStream{} << "UserController::PostStart\n";
}

void UserController::PreShutdown() {
  vaf::OutputSyncStream{} << "UserController::PreShutdown\n";
}

void UserController::PostShutdown() {
  vaf::OutputSyncStream{} << "UserController::PostShutdown\n";
}

void UserController::OnError(vaf::Error error, vaf::String name, bool critical) {
  vaf::OutputSyncStream{} << "UserController::OnError: name: " << name << ", Message: " << error.Message() << ", critical: " << critical << "\n";
  if(critical){
    vaf::OutputSyncStream{} << "UserController::OnError: Critical call, aborting execution!" << std::endl;
    std::abort();
  }
}
