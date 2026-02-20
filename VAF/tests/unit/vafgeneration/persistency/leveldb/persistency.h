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
/*!        \file  persistency.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef PERSISTENCY_PERSISTENCY_H
#define PERSISTENCY_PERSISTENCY_H

#include <memory>
#include <utility>
#include "vaf/container_types.h"
#include "vaf/data_ptr.h"
#include "vaf/result.h"
#include "vaf/error_domain.h"
#include "leveldb/db.h"
#include "persistency/persistency_interface.h"
#include "protobuf/vaf/protobuf_transformer.h"
#include "protobuf/test/protobuf_transformer.h"


namespace persistency {

class Persistency final : public ::persistency::PersistencyInterface {
 public:
  explicit Persistency();
  ~Persistency() noexcept override;
  Persistency(const Persistency&) = delete;
  Persistency(Persistency&&) = delete;
  Persistency& operator=(const Persistency&) = delete;
  Persistency& operator=(Persistency&&) = delete;

  ::vaf::Result<void> Open(const vaf::String& filename, bool sync_on_write) noexcept;
  ::vaf::Result<void> Set(const vaf::String& key, const vaf::String& value) noexcept;
  ::vaf::Result<vaf::String> Get(const vaf::String& key) noexcept;

  ::vaf::Result<std::uint64_t> Get_UInt64Value(const vaf::String& key) noexcept override;
  ::vaf::Result<void> Set_UInt64Value(const vaf::String& key, const std::uint64_t& value) noexcept override;
  ::vaf::Result<std::uint32_t> Get_UInt32Value(const vaf::String& key) noexcept override;
  ::vaf::Result<void> Set_UInt32Value(const vaf::String& key, const std::uint32_t& value) noexcept override;
  ::vaf::Result<std::uint16_t> Get_UInt16Value(const vaf::String& key) noexcept override;
  ::vaf::Result<void> Set_UInt16Value(const vaf::String& key, const std::uint16_t& value) noexcept override;
  ::vaf::Result<std::uint8_t> Get_UInt8Value(const vaf::String& key) noexcept override;
  ::vaf::Result<void> Set_UInt8Value(const vaf::String& key, const std::uint8_t& value) noexcept override;
  ::vaf::Result<std::int64_t> Get_Int64Value(const vaf::String& key) noexcept override;
  ::vaf::Result<void> Set_Int64Value(const vaf::String& key, const std::int64_t& value) noexcept override;
  ::vaf::Result<std::int32_t> Get_Int32Value(const vaf::String& key) noexcept override;
  ::vaf::Result<void> Set_Int32Value(const vaf::String& key, const std::int32_t& value) noexcept override;
  ::vaf::Result<std::int16_t> Get_Int16Value(const vaf::String& key) noexcept override;
  ::vaf::Result<void> Set_Int16Value(const vaf::String& key, const std::int16_t& value) noexcept override;
  ::vaf::Result<std::int8_t> Get_Int8Value(const vaf::String& key) noexcept override;
  ::vaf::Result<void> Set_Int8Value(const vaf::String& key, const std::int8_t& value) noexcept override;
  ::vaf::Result<bool> Get_BoolValue(const vaf::String& key) noexcept override;
  ::vaf::Result<void> Set_BoolValue(const vaf::String& key, const bool& value) noexcept override;
  ::vaf::Result<float> Get_FloatValue(const vaf::String& key) noexcept override;
  ::vaf::Result<void> Set_FloatValue(const vaf::String& key, const float& value) noexcept override;
  ::vaf::Result<double> Get_DoubleValue(const vaf::String& key) noexcept override;
  ::vaf::Result<void> Set_DoubleValue(const vaf::String& key, const double& value) noexcept override;
  ::vaf::Result<::vaf::String> Get_StringValue(const vaf::String& key) noexcept override;
  ::vaf::Result<void> Set_StringValue(const vaf::String& key, const ::vaf::String& value) noexcept override;
  ::vaf::Result<::test::MyArray> Get_MyArrayValue(const vaf::String& key) noexcept override;
  ::vaf::Result<void> Set_MyArrayValue(const vaf::String& key, const ::test::MyArray& value) noexcept override;
 private:
  leveldb::DB* db_{nullptr};
  bool opened_{false};
  bool sync_on_write_{false};
};

} // namespace persistency

#endif // PERSISTENCY_PERSISTENCY_H
