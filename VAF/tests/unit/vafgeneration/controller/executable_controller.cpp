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
/*!        \file  executable_controller.cpp
 *         \brief
 *
 *********************************************************************************************************************/

#include "executable_controller/executable_controller.h"

#include "vaf/output_sync_stream.h"
#include "test/my_module1.h"
#include "test/my_module2.h"
#include "test/my_module3.h"
#include "test/my_module4.h"
#include "test/my_app1.h"
#include "test/my_app2.h"

#include "persistency/persistency.h"
#include "vaf/result.h"

namespace executable_controller {

ExecutableController::ExecutableController()
  : ExecutableControllerBase(),
    executor_{} {
}

void ExecutableController::DoInitialize() {
  executor_ = std::make_unique<vaf::Executor>(std::chrono::milliseconds{ 10 });
  auto Persistency_MyApp1_MyFile1 = std::make_shared<persistency::Persistency>();
  ::vaf::Result<void> result_MyApp1_MyFile1 = Persistency_MyApp1_MyFile1->Open("./MyFile1.db", true);
  if(!result_MyApp1_MyFile1.HasValue()){
    vaf::OutputSyncStream{} << "Could not open persistency kvs storage: ./MyFile1.db." << std::endl;
    ReportErrorOfModule(result_MyApp1_MyFile1.Error(), "ExecutableController::DoInitialize", true);
  }
  auto Persistency_MyApp2_MyFile2 = std::make_shared<persistency::Persistency>();
  ::vaf::Result<void> result_MyApp2_MyFile2 = Persistency_MyApp2_MyFile2->Open("./MyFile2.db", true);
  if(!result_MyApp2_MyFile2.HasValue()){
    vaf::OutputSyncStream{} << "Could not open persistency kvs storage: ./MyFile2.db." << std::endl;
    ReportErrorOfModule(result_MyApp2_MyFile2.Error(), "ExecutableController::DoInitialize", true);
  }
  auto Persistency_SharedFile1 = std::make_shared<persistency::Persistency>();
    ::vaf::Result<void> result1 = Persistency_SharedFile1->Open("./MyFileShared.db", true);
  if(!result1.HasValue()){
    vaf::OutputSyncStream{} << "Could not open persistency kvs storage: ./MyFileShared.db." << std::endl;
    ReportErrorOfModule(result1.Error(), "ExecutableController::DoInitialize", true);
  }
  auto Persistency_MyApp1_MyFile1_Key1Array_result = Persistency_MyApp1_MyFile1->Get_MyArrayValue("Key1Array");
  if (!Persistency_MyApp1_MyFile1_Key1Array_result.HasValue()) {
    vaf::OutputSyncStream{} << "Persistency_MyApp1_MyFile1: Key-Value Key1Array NOT initialized, set init value." << std::endl;
    ReportErrorOfModule(Persistency_MyApp1_MyFile1_Key1Array_result.Error(), "ExecutableController::DoInitialize", false);
    test::MyArray Persistency_MyApp1_MyFile1_Key1Array_value = { 1,2,3 };
    Persistency_MyApp1_MyFile1->Set_MyArrayValue("Key1Array", Persistency_MyApp1_MyFile1_Key1Array_value);
  }
  auto Persistency_SharedFile1_Key1Int_result = Persistency_SharedFile1->Get_UInt8Value("Key1Int");
  if (!Persistency_SharedFile1_Key1Int_result.HasValue()) {
    vaf::OutputSyncStream{} << "Persistency_SharedFile1: Key-Value Key1Int NOT initialized, set init value." << std::endl;
    ReportErrorOfModule(Persistency_SharedFile1_Key1Int_result.Error(), "ExecutableController::DoInitialize", false);
    Persistency_SharedFile1->Set_UInt8Value("Key1Int", 1);
  }
  auto Persistency_MyApp2_MyFile2_Key2Array_result = Persistency_MyApp2_MyFile2->Get_MyArrayValue("Key2Array");
  if (!Persistency_MyApp2_MyFile2_Key2Array_result.HasValue()) {
    vaf::OutputSyncStream{} << "Persistency_MyApp2_MyFile2: Key-Value Key2Array NOT initialized, set init value." << std::endl;
    ReportErrorOfModule(Persistency_MyApp2_MyFile2_Key2Array_result.Error(), "ExecutableController::DoInitialize", false);
    test::MyArray Persistency_MyApp2_MyFile2_Key2Array_value = { 2,3,4 };
    Persistency_MyApp2_MyFile2->Set_MyArrayValue("Key2Array", Persistency_MyApp2_MyFile2_Key2Array_value);
  }
  auto Persistency_SharedFile1_Key2Int_result = Persistency_SharedFile1->Get_UInt8Value("Key2Int");
  if (!Persistency_SharedFile1_Key2Int_result.HasValue()) {
    vaf::OutputSyncStream{} << "Persistency_SharedFile1: Key-Value Key2Int NOT initialized, set init value." << std::endl;
    ReportErrorOfModule(Persistency_SharedFile1_Key2Int_result.Error(), "ExecutableController::DoInitialize", false);
    Persistency_SharedFile1->Set_UInt8Value("Key2Int", 2);
  }

  auto MyModule3 = std::make_shared<test::MyModule3>(
    *executor_,
    "MyModule3",
    *this);

  auto MyModule4 = std::make_shared<test::MyModule4>(
    *executor_,
    "MyModule4",
    *this);

  auto MyModule2 = std::make_shared<test::MyModule2>(
    *executor_,
    "MyModule2",
    *this);

  auto MyModule1 = std::make_shared<test::MyModule1>(
    *executor_,
    "MyModule1",
    vaf::Vector<vaf::String>{},
    *this);

  auto MyApp1 = std::make_shared<test::MyApp1>( test::MyApp1::ConstructorToken{
    "MyApp1",
    vaf::Vector<vaf::String>{
      {"MyModule1"},
      {"MyModule2"},
      {"MyModule3"}
    },
    *this,
    *executor_,
    MyModule3,
    MyModule4,
    MyModule1,
    MyModule2,
    Persistency_MyApp1_MyFile1,
    Persistency_SharedFile1
,    0,
    std::chrono::nanoseconds{ 10000000 },
    1,
    std::chrono::nanoseconds{ 0 }
    });

  auto MyApp2 = std::make_shared<test::MyApp2>( test::MyApp2::ConstructorToken{
    "MyApp2",
    vaf::Vector<vaf::String>{
    },
    *this,
    *executor_,
    Persistency_MyApp2_MyFile2,
    Persistency_SharedFile1
,    0,
    std::chrono::nanoseconds{ 10000000 },
    1,
    std::chrono::nanoseconds{ 0 }
    });

  RegisterModule(MyModule3);

  RegisterModule(MyModule4);

  RegisterModule(MyModule1);

  RegisterModule(MyModule2);

  RegisterModule(MyApp1);

  RegisterModule(MyApp2);

  ExecutableControllerBase::DoInitialize();
}

void ExecutableController::DoStart() {
  ExecutableControllerBase::DoStart();
}

void ExecutableController::DoShutdown() {
  ExecutableControllerBase::DoShutdown();
}

} // namespace executable_controller
