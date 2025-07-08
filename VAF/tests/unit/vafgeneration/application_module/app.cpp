/*!********************************************************************************************************************
 *  COPYRIGHT
 *  -------------------------------------------------------------------------------------------------------------------
 *  \verbatim
 *  Copyright (c) 2025 by Vector Informatik GmbH. All rights reserved.
 *
 *                This software is copyright protected and proprietary to Vector Informatik GmbH.
 *                Vector Informatik GmbH grants to you only those rights as set out in the license conditions.
 *                All other rights remain with Vector Informatik GmbH.
 *  \endverbatim
 *  -------------------------------------------------------------------------------------------------------------------
 *  FILE DESCRIPTION
 *  -----------------------------------------------------------------------------------------------------------------*/
/*!        \file  my_application_module.cpp
 *         \brief
 *
 *********************************************************************************************************************/

#include "apps/my_application_module.h"

namespace apps {


/*
  Data element API example for MyDataElement of type std::uint64_t
  ================================================================
  - Provider
    ::vaf::Result<::vaf::DataPtr<std::uint64_t>> Allocate_MyDataElement()
    ::vaf::Result<void> SetAllocated_MyDataElement(::vaf::DataPtr<std::uint64_t>&& data)
    ::vaf::Result<void> Set_MyDataElement(const std::uint64_t& data)
  - Consumer
    ::vaf::Result<::vaf::ConstDataPtr<const std::uint64_t>> GetAllocated_MyDataElement()
    std::uint64_t Get_MyDataElement()
    std::function<void(const ::vaf::ConstDataPtr<const std::uint64_t>)>
    void RegisterDataElementHandler_MyDataElement(std::string owner, std::function<void(const ::vaf::ConstDataPtr<const std::uint64_t>)>&& f)

  Consumer interfaces
  ===================
    - c_interface_instance_1 : test::MyInterfaceConsumer
      - Data elements
        - my_data_element : std::uint64_t


    - c_interface_instance_2 : test::MyInterfaceConsumer
      - Data elements
        - my_data_element : std::uint64_t


  Provider interfaces
  ===================
    - p_interface_instance_1 : test::MyInterfaceProvider
      - Data elements
        - my_data_element : std::uint64_t


    - p_interface_instance_2 : test::MyInterfaceProvider
      - Data elements
        - my_data_element : std::uint64_t


*/

MyApplicationModule::MyApplicationModule(ConstructorToken&& token)
    : MyApplicationModuleBase(std::move(token))
{
}

void MyApplicationModule::task1() {
}

void MyApplicationModule::task2() {
}


} // namespace apps
