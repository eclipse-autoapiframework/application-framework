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

#include "gtest/gtest.h"
#include <fstream>

int main(int argc, char **argv) {
  int gtest_ret{0};
  ::testing::InitGoogleTest(&argc, argv);

  // Set death tests to threadsafe globally because logging uses a separate thread.
  //::testing::FLAGS_gtest_death_test_style = "threadsafe";

  // Execute tests via gtest
  gtest_ret = RUN_ALL_TESTS();

  return gtest_ret;
}
