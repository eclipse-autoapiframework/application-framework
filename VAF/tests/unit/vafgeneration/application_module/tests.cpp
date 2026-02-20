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
/*!        \file  tests.cpp
 *         \brief
 *
 *********************************************************************************************************************/

#include <cstddef>
#include <cstdint>
#include <csignal>
#include "gtest/gtest.h"
#include "gmock/gmock.h"
#include "test/my_interface_consumer_mock.h"
#include "test/my_interface_provider_mock.h"
#include "persistency/persistency_mock.h"
#include "apps/my_application_module.h"

// Put inside test to skip
//GTEST_SKIP() << "Skipping single test";
using ::testing::Return;
using ::testing::_;

namespace vaf {
    /*!
     * \brief Initializes the signal handling.
     * \return void.
     */
    void InitializeSignalHandling() noexcept {
      bool success{true};
      sigset_t signals;

      /* Block all signals except the SIGABRT, SIGBUS, SIGFPE, SIGILL, SIGSEGV signals because blocking them will lead to
       * undefined behavior. Their default handling shall not be changed (dependent on underlying POSIX environment, usually
       * process is killed and a dump file is written). Signal mask will be inherited by subsequent threads. */

      success = success && (0 == sigfillset(&signals));
      success = success && (0 == sigdelset(&signals, SIGABRT));
      success = success && (0 == sigdelset(&signals, SIGBUS));
      success = success && (0 == sigdelset(&signals, SIGFPE));
      success = success && (0 == sigdelset(&signals, SIGILL));
      success = success && (0 == sigdelset(&signals, SIGSEGV));
      success = success && (0 == pthread_sigmask(SIG_SETMASK, &signals, nullptr));

      if (!success) {
        // Exit
      }
    }

    class MyApplicationModuleUnitTest : public ::testing::Test {
    protected:
      MyApplicationModuleUnitTest() {}

      virtual ~MyApplicationModuleUnitTest() {}

      virtual void SetUp() {
        InitializeSignalHandling();
      }

      virtual void TearDown() {
      }
    };

    TEST_F(MyApplicationModuleUnitTest, Test_1) {
      auto c_interface_instance_1Mock = std::make_shared<test::MyInterfaceConsumerMock>();
      auto c_interface_instance_2Mock = std::make_shared<test::MyInterfaceConsumerMock>();
      auto p_interface_instance_1Mock = std::make_shared<test::MyInterfaceProviderMock>();
      auto p_interface_instance_2Mock = std::make_shared<test::MyInterfaceProviderMock>();
      auto PersistencyMock = std::make_shared<persistency::PersistencyMock>();

      auto MyApplicationModule = std::make_shared<apps::MyApplicationModule>( apps::MyApplicationModule ::ConstructorToken{
        c_interface_instance_1Mock,
        c_interface_instance_2Mock,
        p_interface_instance_1Mock,
        p_interface_instance_2Mock,
        PersistencyMock      });
    }
} // namespace vaf
