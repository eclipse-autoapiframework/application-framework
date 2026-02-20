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
/*!        \file  my_application_module_base.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef APPS_MY_APPLICATION_MODULE_BASE_H
#define APPS_MY_APPLICATION_MODULE_BASE_H

#include <memory>
#include "vaf/controller_interface.h"

#include "test/my_interface_consumer.h"
#include "test/my_interface_provider.h"
#include "persistency/persistency_interface.h"

namespace apps {

class MyApplicationModuleBase {
 public:
  struct ConstructorToken {
    std::shared_ptr<test::MyInterfaceConsumer> c_interface_instance_1_;
    std::shared_ptr<test::MyInterfaceConsumer> c_interface_instance_2_;
    std::shared_ptr<test::MyInterfaceProvider> p_interface_instance_1_;
    std::shared_ptr<test::MyInterfaceProvider> p_interface_instance_2_;
    std::shared_ptr<persistency::PersistencyInterface> persistency_my_file1_;
  };

  MyApplicationModuleBase(ConstructorToken&& token);
  virtual ~MyApplicationModuleBase() = default;

  void ReportError(const vaf::Error&, bool) {}
  virtual void OnError(const vaf::Error&) {}
  vaf::String GetName() { return ""; }

  virtual void task1() = 0;
  virtual void task2() = 0;

 protected:
  std::shared_ptr<test::MyInterfaceConsumer> c_interface_instance_1_;
  std::shared_ptr<test::MyInterfaceConsumer> c_interface_instance_2_;
  std::shared_ptr<test::MyInterfaceProvider> p_interface_instance_1_;
  std::shared_ptr<test::MyInterfaceProvider> p_interface_instance_2_;
  std::shared_ptr<persistency::PersistencyInterface> persistency_my_file1_;
};

} // namespace apps

#endif // APPS_MY_APPLICATION_MODULE_BASE_H
