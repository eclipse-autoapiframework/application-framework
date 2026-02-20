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
/*!        \file  my_application_module.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef APPS_MY_APPLICATION_MODULE_H
#define APPS_MY_APPLICATION_MODULE_H

#include "apps/my_application_module_base.h"

namespace apps {

class MyApplicationModule : public MyApplicationModuleBase {
 public:
  MyApplicationModule(ConstructorToken&& token);

  void task1() override;
  void task2() override;

 private:
};

} // namespace apps

#endif // APPS_MY_APPLICATION_MODULE_H
