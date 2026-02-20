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
/*!        \file  main.cpp
 *         \brief
 *
 *********************************************************************************************************************/

#include "executable_controller/executable_controller.h"

int main() {
  executable_controller::ExecutableController executable_controller;
  executable_controller.Run(false);

  return 0;
}
