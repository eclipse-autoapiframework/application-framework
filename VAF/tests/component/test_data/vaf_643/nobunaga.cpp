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

*/

/**********************************************************************************************************************
  Constructor
**********************************************************************************************************************/
Nobunaga::Nobunaga(ConstructorToken&& token) : NobunagaBase(std::move(token)) {
  // Insert your code here...
  main_weapon{"sword"};
  secondary_weapon{"musket"};
  vaf::OutputSyncStream{} << "oda Nobunaga is alive, main weapon is " << main_weapon << ", second weapon is " << secondary_weapon << std::endl;
}

/**********************************************************************************************************************
  1 periodic task(s)
**********************************************************************************************************************/
// Task with name PeriodicTask and a period of 200ms.
void Nobunaga::PeriodicTask() {
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
