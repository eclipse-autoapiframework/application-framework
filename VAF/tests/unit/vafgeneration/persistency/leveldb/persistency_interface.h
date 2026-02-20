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
/*!        \file  persistency_interface.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef PERSISTENCY_PERSISTENCY_INTERFACE_H
#define PERSISTENCY_PERSISTENCY_INTERFACE_H

#include "vaf/container_types.h"
#include "vaf/data_ptr.h"
#include "vaf/result.h"
#include "vaf/error_domain.h"
#include "test/impl_type_myarray.h"
#include "test/impl_type_myenum.h"
#include "test/impl_type_mymap.h"
#include "test/impl_type_mystring.h"
#include "test/impl_type_mystruct.h"
#include "test/impl_type_mytyperef.h"
#include "test/impl_type_myvector.h"
#include "test2/impl_type_myarray.h"
#include "test2/impl_type_mystruct.h"
#include "test2/impl_type_myvector.h"

namespace persistency {

class PersistencyInterface {
 public:
  virtual ~PersistencyInterface() = default;

  virtual ::vaf::Result<std::uint64_t> Get_UInt64Value(const vaf::String& key) = 0;
  virtual ::vaf::Result<void> Set_UInt64Value(const vaf::String& key, const std::uint64_t& value) = 0;
  virtual ::vaf::Result<std::uint32_t> Get_UInt32Value(const vaf::String& key) = 0;
  virtual ::vaf::Result<void> Set_UInt32Value(const vaf::String& key, const std::uint32_t& value) = 0;
  virtual ::vaf::Result<std::uint16_t> Get_UInt16Value(const vaf::String& key) = 0;
  virtual ::vaf::Result<void> Set_UInt16Value(const vaf::String& key, const std::uint16_t& value) = 0;
  virtual ::vaf::Result<std::uint8_t> Get_UInt8Value(const vaf::String& key) = 0;
  virtual ::vaf::Result<void> Set_UInt8Value(const vaf::String& key, const std::uint8_t& value) = 0;
  virtual ::vaf::Result<std::int64_t> Get_Int64Value(const vaf::String& key) = 0;
  virtual ::vaf::Result<void> Set_Int64Value(const vaf::String& key, const std::int64_t& value) = 0;
  virtual ::vaf::Result<std::int32_t> Get_Int32Value(const vaf::String& key) = 0;
  virtual ::vaf::Result<void> Set_Int32Value(const vaf::String& key, const std::int32_t& value) = 0;
  virtual ::vaf::Result<std::int16_t> Get_Int16Value(const vaf::String& key) = 0;
  virtual ::vaf::Result<void> Set_Int16Value(const vaf::String& key, const std::int16_t& value) = 0;
  virtual ::vaf::Result<std::int8_t> Get_Int8Value(const vaf::String& key) = 0;
  virtual ::vaf::Result<void> Set_Int8Value(const vaf::String& key, const std::int8_t& value) = 0;
  virtual ::vaf::Result<bool> Get_BoolValue(const vaf::String& key) = 0;
  virtual ::vaf::Result<void> Set_BoolValue(const vaf::String& key, const bool& value) = 0;
  virtual ::vaf::Result<float> Get_FloatValue(const vaf::String& key) = 0;
  virtual ::vaf::Result<void> Set_FloatValue(const vaf::String& key, const float& value) = 0;
  virtual ::vaf::Result<double> Get_DoubleValue(const vaf::String& key) = 0;
  virtual ::vaf::Result<void> Set_DoubleValue(const vaf::String& key, const double& value) = 0;
  virtual ::vaf::Result<::vaf::String> Get_StringValue(const vaf::String& key) = 0;
  virtual ::vaf::Result<void> Set_StringValue(const vaf::String& key, const ::vaf::String& value) = 0;
  virtual ::vaf::Result<::test::MyArray> Get_MyArrayValue(const vaf::String& key) = 0;
  virtual ::vaf::Result<void> Set_MyArrayValue(const vaf::String& key, const ::test::MyArray& value) = 0;
};

} // namespace persistency

#endif // PERSISTENCY_PERSISTENCY_INTERFACE_H
