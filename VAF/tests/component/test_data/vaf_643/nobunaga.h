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
/*!        \file  nobunaga.h
 *         \brief
 *
 *********************************************************************************************************************/
#ifndef ODA_NOBUNAGA_H
#define ODA_NOBUNAGA_H

#include "oda/nobunaga_base.h"
#include "vaf/container_types.h"

namespace oda {

class Nobunaga : public NobunagaBase {
 public:
  Nobunaga(ConstructorToken&& token);

  //vaf::Result<void> Init() override;
  //void Start() noexcept override;
  //void Stop() noexcept override;
  //void DeInit() noexcept override;
  //void OnError(const vaf::Error& error) override;

  void PeriodicTask() override;

 private:
  vaf::String main_weapon{};
  vaf::String secondary_weapon{};
  bool deploy_army{false};
};

} // namespace oda

#endif // ODA_NOBUNAGA_H
