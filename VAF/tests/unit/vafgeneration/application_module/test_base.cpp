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
/*!        \file  my_application_module_base.cpp
 *         \brief
 *
 *********************************************************************************************************************/

#include "apps/my_application_module_base.h"

namespace apps {

MyApplicationModuleBase::MyApplicationModuleBase(ConstructorToken&& token):
      c_interface_instance_1_{std::move(token.c_interface_instance_1_)},
      c_interface_instance_2_{std::move(token.c_interface_instance_2_)},
      p_interface_instance_1_{std::move(token.p_interface_instance_1_)},
      p_interface_instance_2_{std::move(token.p_interface_instance_2_)},
      persistency_my_file1_{std::move(token.persistency_my_file1_)}{
}

} // namespace apps
