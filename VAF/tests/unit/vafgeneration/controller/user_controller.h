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
/*!        \file  user_controller.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef USER_CONTROLLER_H
#define USER_CONTROLLER_H

#include "vaf/user_controller_interface.h"

class UserController : public vaf::UserControllerInterface {
  public:
    void PreInitialize() override;
    void PostInitialize() override;
    void PreStart() override;
    void PostStart() override;
    void PreShutdown() override;
    void PostShutdown() override;

    void OnError(vaf::Error error, vaf::String name, bool critical) override;
};

#endif // USER_CONTROLLER_H
