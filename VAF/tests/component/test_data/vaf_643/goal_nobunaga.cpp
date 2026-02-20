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
/*!        \file  nobunaga.cpp
 *         \brief
 *
 *********************************************************************************************************************/

#include "oda/nobunaga.h"

namespace oda {

/*
  Generated based on configuration in ../../model/nobunaga.py

  Consumer interfaces
  ===================
    Data element API example for samurai of type sengoku::samurai
      - ::vaf::Result<::vaf::ConstDataPtr<const sengoku::samurai>> GetAllocated_samurai()
      - sengoku::samurai Get_samurai()
      - void RegisterDataElementHandler_samurai(vaf::String owner, std::function<void(const ::vaf::ConstDataPtr<const sengoku::samurai>)>&& f)

    - EliteSamurai_ : sengoku::sonaeConsumer
      - Data elements
        - samurai : sengoku::samurai
*/

/**********************************************************************************************************************
  Constructor
**********************************************************************************************************************/
Nobunaga::Nobunaga(ConstructorToken&& token) : NobunagaBase(std::move(token)) {
  // Insert your code here...
  main_weapon{"sword"};
  secondary_weapon{"musket"};
  vaf::OutputSyncStream{} << "oda Nobunaga is alive, main weapon is " << main_weapon << ", second weapon is "
                          << secondary_weapon << std::endl;
}

/**********************************************************************************************************************
  1 periodic task(s)
**********************************************************************************************************************/
// Task with name Deploy and a period of 15ms.
void Nobunaga::Deploy() {
  // Insert your code for periodic execution here...
  deploy_army = true;
  vaf::OutputSyncStream{} << "oda Nobunaga deploys his army!" << std::endl;
}

// vaf::Result<void> Nobunaga::Init() {
//   return vaf::Result<void>{};
// }
// void Nobunaga::Start() {
//   ReportOperational();
// }
// void Nobunaga::Stop() {}
// void Nobunaga::DeInit() {}
// void Nobunaga::OnError(const vaf::Error& error) {
//   static_cast<void>(error);
// }

}  // namespace oda
