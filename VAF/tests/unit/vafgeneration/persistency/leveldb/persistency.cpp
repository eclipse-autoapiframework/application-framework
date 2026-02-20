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
/*!        \file  persistency.cpp
 *         \brief
 *
 *********************************************************************************************************************/

#include "persistency/persistency.h"

#include "vaf/error_domain.h"
#include "protobuf_basetypes.pb.h"

namespace persistency {

Persistency::Persistency() {
}

Persistency::~Persistency() {
  delete db_;
}

::vaf::Result<void> Persistency::Open(const vaf::String& filename, bool sync_on_write) noexcept {
  vaf::Result<void> ret_value {
    vaf::Result<void>::FromError(vaf::ErrorCode::kNotOk, "Error creating Instance Specifier for KVS")};

  leveldb::Options options;
  options.create_if_missing = true;

  sync_on_write_ = sync_on_write;

  leveldb::Status status = leveldb::DB::Open(options, filename.c_str(), &db_);
  if (true == status.ok()) {
    opened_ = true;
    ret_value = vaf::Result<void>::FromValue();
  } else {
    ret_value = vaf::Result<void>::FromError(vaf::Error(vaf::ErrorCode::kUnknown,"Error creating Instance Specifier for KVS."));
    logger_.LogWarn() <<  "Error creating Instance Specifier for KVS for Persistency.";
  }
  return ret_value;
};

::vaf::Result<void> Persistency::Set(const vaf::String& key, const vaf::String& value) noexcept{
  vaf::Result<void> ret_value{vaf::Result<void>::FromError(vaf::ErrorCode::kNotOk, "Kvs not opened.")};
  if (opened_) {
    leveldb::WriteOptions write_options;
    write_options.sync = sync_on_write_;
    leveldb::Status status = db_->Put(write_options, key.c_str(), value.c_str());
    if (true == status.ok()) {
      ret_value = vaf::Result<void>::FromValue();
    } else {
      ret_value = vaf::Result<void>::FromError(vaf::Error(vaf::ErrorCode::kUnknown,"Kvs set failed ."));
      logger_.LogWarn() <<  "Kvs set failed for Persistency.";
    }
  } else {
    ret_value = vaf::Result<void>::FromError(vaf::Error(vaf::ErrorCode::kUnknown,"Kvs not opened."));
    logger_.LogWarn() <<  "Kvs not opened for Persistency.";
  }
  return ret_value;
};

::vaf::Result<vaf::String> Persistency::Get(const vaf::String& key) noexcept{
  vaf::Result<vaf::String> ret_value{
    vaf::Result<vaf::String>::FromError(vaf::ErrorCode::kNotOk, "Kvs not opened.")};
  if (opened_) {
    leveldb::ReadOptions read_options;
    std::string temp;
    leveldb::Status status = db_->Get(read_options, key.c_str(), &temp);
    if (true == status.ok()) {
      vaf::String value(temp.c_str());
      ret_value = vaf::Result<vaf::String>::FromValue(value);
    } else {
      ret_value = vaf::Result<vaf::String>::FromError(vaf::Error(vaf::ErrorCode::kUnknown,"Kvs get failed."));
      logger_.LogWarn() <<  "Kvs get failed for Persistency.";
    }
  } else {
    ret_value = vaf::Result<vaf::String>::FromError(vaf::Error(vaf::ErrorCode::kUnknown,"Kvs not opened."));
    logger_.LogWarn() <<  "Kvs not opened for Persistency.";
  }
  return ret_value;
};

::vaf::Result<std::uint64_t> Persistency::Get_UInt64Value(const vaf::String& key) noexcept{
  vaf::Result<std::uint64_t> ret_value{vaf::Result<std::uint64_t>::FromError(vaf::ErrorCode::kNotOk, "Get failed.")};

  vaf::Result<vaf::String> result = Get(key);
  if (result.HasValue()) {
    protobuf::basetypes::UInt64 deserialized;
    if (!deserialized.ParseFromString(result.Value().c_str())) {
      vaf::OutputSyncStream{std::cerr} << "ERROR: Unable to deserialize!\n";
    }
    ret_value = vaf::Result<std::uint64_t>::FromValue(deserialized.vaf_value_internal());
  } else {
    ret_value = vaf::Result<std::uint64_t>::FromError(vaf::Error(vaf::ErrorCode::kUnknown,"Kvs get failed."));
    logger_.LogWarn() <<  "Get failed for Persistency.";
  }

  return ret_value;
}

::vaf::Result<void> Persistency::Set_UInt64Value(const vaf::String& key, const std::uint64_t& value) noexcept{
  protobuf::basetypes::UInt64 proto_message;
  proto_message.set_vaf_value_internal(value);
  size_t nbytes = proto_message.ByteSizeLong();
  std::string temp;
  if (nbytes) {
    proto_message.SerializeToString(&temp);
  }

  vaf::String serialized(temp.c_str());
  return Set(key, serialized);
}
::vaf::Result<std::uint32_t> Persistency::Get_UInt32Value(const vaf::String& key) noexcept{
  vaf::Result<std::uint32_t> ret_value{vaf::Result<std::uint32_t>::FromError(vaf::ErrorCode::kNotOk, "Get failed.")};

  vaf::Result<vaf::String> result = Get(key);
  if (result.HasValue()) {
    protobuf::basetypes::UInt32 deserialized;
    if (!deserialized.ParseFromString(result.Value().c_str())) {
      vaf::OutputSyncStream{std::cerr} << "ERROR: Unable to deserialize!\n";
    }
    ret_value = vaf::Result<std::uint32_t>::FromValue(deserialized.vaf_value_internal());
  } else {
    ret_value = vaf::Result<std::uint32_t>::FromError(vaf::Error(vaf::ErrorCode::kUnknown,"Kvs get failed."));
    logger_.LogWarn() <<  "Get failed for Persistency.";
  }

  return ret_value;
}

::vaf::Result<void> Persistency::Set_UInt32Value(const vaf::String& key, const std::uint32_t& value) noexcept{
  protobuf::basetypes::UInt32 proto_message;
  proto_message.set_vaf_value_internal(value);
  size_t nbytes = proto_message.ByteSizeLong();
  std::string temp;
  if (nbytes) {
    proto_message.SerializeToString(&temp);
  }

  vaf::String serialized(temp.c_str());
  return Set(key, serialized);
}
::vaf::Result<std::uint16_t> Persistency::Get_UInt16Value(const vaf::String& key) noexcept{
  vaf::Result<std::uint16_t> ret_value{vaf::Result<std::uint16_t>::FromError(vaf::ErrorCode::kNotOk, "Get failed.")};

  vaf::Result<vaf::String> result = Get(key);
  if (result.HasValue()) {
    protobuf::basetypes::UInt16 deserialized;
    if (!deserialized.ParseFromString(result.Value().c_str())) {
      vaf::OutputSyncStream{std::cerr} << "ERROR: Unable to deserialize!\n";
    }
    ret_value = vaf::Result<std::uint16_t>::FromValue(deserialized.vaf_value_internal());
  } else {
    ret_value = vaf::Result<std::uint16_t>::FromError(vaf::Error(vaf::ErrorCode::kUnknown,"Kvs get failed."));
    logger_.LogWarn() <<  "Get failed for Persistency.";
  }

  return ret_value;
}

::vaf::Result<void> Persistency::Set_UInt16Value(const vaf::String& key, const std::uint16_t& value) noexcept{
  protobuf::basetypes::UInt16 proto_message;
  proto_message.set_vaf_value_internal(value);
  size_t nbytes = proto_message.ByteSizeLong();
  std::string temp;
  if (nbytes) {
    proto_message.SerializeToString(&temp);
  }

  vaf::String serialized(temp.c_str());
  return Set(key, serialized);
}
::vaf::Result<std::uint8_t> Persistency::Get_UInt8Value(const vaf::String& key) noexcept{
  vaf::Result<std::uint8_t> ret_value{vaf::Result<std::uint8_t>::FromError(vaf::ErrorCode::kNotOk, "Get failed.")};

  vaf::Result<vaf::String> result = Get(key);
  if (result.HasValue()) {
    protobuf::basetypes::UInt8 deserialized;
    if (!deserialized.ParseFromString(result.Value().c_str())) {
      vaf::OutputSyncStream{std::cerr} << "ERROR: Unable to deserialize!\n";
    }
    ret_value = vaf::Result<std::uint8_t>::FromValue(deserialized.vaf_value_internal());
  } else {
    ret_value = vaf::Result<std::uint8_t>::FromError(vaf::Error(vaf::ErrorCode::kUnknown,"Kvs get failed."));
    logger_.LogWarn() <<  "Get failed for Persistency.";
  }

  return ret_value;
}

::vaf::Result<void> Persistency::Set_UInt8Value(const vaf::String& key, const std::uint8_t& value) noexcept{
  protobuf::basetypes::UInt8 proto_message;
  proto_message.set_vaf_value_internal(value);
  size_t nbytes = proto_message.ByteSizeLong();
  std::string temp;
  if (nbytes) {
    proto_message.SerializeToString(&temp);
  }

  vaf::String serialized(temp.c_str());
  return Set(key, serialized);
}
::vaf::Result<std::int64_t> Persistency::Get_Int64Value(const vaf::String& key) noexcept{
  vaf::Result<std::int64_t> ret_value{vaf::Result<std::int64_t>::FromError(vaf::ErrorCode::kNotOk, "Get failed.")};

  vaf::Result<vaf::String> result = Get(key);
  if (result.HasValue()) {
    protobuf::basetypes::Int64 deserialized;
    if (!deserialized.ParseFromString(result.Value().c_str())) {
      vaf::OutputSyncStream{std::cerr} << "ERROR: Unable to deserialize!\n";
    }
    ret_value = vaf::Result<std::int64_t>::FromValue(deserialized.vaf_value_internal());
  } else {
    ret_value = vaf::Result<std::int64_t>::FromError(vaf::Error(vaf::ErrorCode::kUnknown,"Kvs get failed."));
    logger_.LogWarn() <<  "Get failed for Persistency.";
  }

  return ret_value;
}

::vaf::Result<void> Persistency::Set_Int64Value(const vaf::String& key, const std::int64_t& value) noexcept{
  protobuf::basetypes::Int64 proto_message;
  proto_message.set_vaf_value_internal(value);
  size_t nbytes = proto_message.ByteSizeLong();
  std::string temp;
  if (nbytes) {
    proto_message.SerializeToString(&temp);
  }

  vaf::String serialized(temp.c_str());
  return Set(key, serialized);
}
::vaf::Result<std::int32_t> Persistency::Get_Int32Value(const vaf::String& key) noexcept{
  vaf::Result<std::int32_t> ret_value{vaf::Result<std::int32_t>::FromError(vaf::ErrorCode::kNotOk, "Get failed.")};

  vaf::Result<vaf::String> result = Get(key);
  if (result.HasValue()) {
    protobuf::basetypes::Int32 deserialized;
    if (!deserialized.ParseFromString(result.Value().c_str())) {
      vaf::OutputSyncStream{std::cerr} << "ERROR: Unable to deserialize!\n";
    }
    ret_value = vaf::Result<std::int32_t>::FromValue(deserialized.vaf_value_internal());
  } else {
    ret_value = vaf::Result<std::int32_t>::FromError(vaf::Error(vaf::ErrorCode::kUnknown,"Kvs get failed."));
    logger_.LogWarn() <<  "Get failed for Persistency.";
  }

  return ret_value;
}

::vaf::Result<void> Persistency::Set_Int32Value(const vaf::String& key, const std::int32_t& value) noexcept{
  protobuf::basetypes::Int32 proto_message;
  proto_message.set_vaf_value_internal(value);
  size_t nbytes = proto_message.ByteSizeLong();
  std::string temp;
  if (nbytes) {
    proto_message.SerializeToString(&temp);
  }

  vaf::String serialized(temp.c_str());
  return Set(key, serialized);
}
::vaf::Result<std::int16_t> Persistency::Get_Int16Value(const vaf::String& key) noexcept{
  vaf::Result<std::int16_t> ret_value{vaf::Result<std::int16_t>::FromError(vaf::ErrorCode::kNotOk, "Get failed.")};

  vaf::Result<vaf::String> result = Get(key);
  if (result.HasValue()) {
    protobuf::basetypes::Int16 deserialized;
    if (!deserialized.ParseFromString(result.Value().c_str())) {
      vaf::OutputSyncStream{std::cerr} << "ERROR: Unable to deserialize!\n";
    }
    ret_value = vaf::Result<std::int16_t>::FromValue(deserialized.vaf_value_internal());
  } else {
    ret_value = vaf::Result<std::int16_t>::FromError(vaf::Error(vaf::ErrorCode::kUnknown,"Kvs get failed."));
    logger_.LogWarn() <<  "Get failed for Persistency.";
  }

  return ret_value;
}

::vaf::Result<void> Persistency::Set_Int16Value(const vaf::String& key, const std::int16_t& value) noexcept{
  protobuf::basetypes::Int16 proto_message;
  proto_message.set_vaf_value_internal(value);
  size_t nbytes = proto_message.ByteSizeLong();
  std::string temp;
  if (nbytes) {
    proto_message.SerializeToString(&temp);
  }

  vaf::String serialized(temp.c_str());
  return Set(key, serialized);
}
::vaf::Result<std::int8_t> Persistency::Get_Int8Value(const vaf::String& key) noexcept{
  vaf::Result<std::int8_t> ret_value{vaf::Result<std::int8_t>::FromError(vaf::ErrorCode::kNotOk, "Get failed.")};

  vaf::Result<vaf::String> result = Get(key);
  if (result.HasValue()) {
    protobuf::basetypes::Int8 deserialized;
    if (!deserialized.ParseFromString(result.Value().c_str())) {
      vaf::OutputSyncStream{std::cerr} << "ERROR: Unable to deserialize!\n";
    }
    ret_value = vaf::Result<std::int8_t>::FromValue(deserialized.vaf_value_internal());
  } else {
    ret_value = vaf::Result<std::int8_t>::FromError(vaf::Error(vaf::ErrorCode::kUnknown,"Kvs get failed."));
    logger_.LogWarn() <<  "Get failed for Persistency.";
  }

  return ret_value;
}

::vaf::Result<void> Persistency::Set_Int8Value(const vaf::String& key, const std::int8_t& value) noexcept{
  protobuf::basetypes::Int8 proto_message;
  proto_message.set_vaf_value_internal(value);
  size_t nbytes = proto_message.ByteSizeLong();
  std::string temp;
  if (nbytes) {
    proto_message.SerializeToString(&temp);
  }

  vaf::String serialized(temp.c_str());
  return Set(key, serialized);
}
::vaf::Result<bool> Persistency::Get_BoolValue(const vaf::String& key) noexcept{
  vaf::Result<bool> ret_value{vaf::Result<bool>::FromError(vaf::ErrorCode::kNotOk, "Get failed.")};

  vaf::Result<vaf::String> result = Get(key);
  if (result.HasValue()) {
    protobuf::basetypes::Bool deserialized;
    if (!deserialized.ParseFromString(result.Value().c_str())) {
      vaf::OutputSyncStream{std::cerr} << "ERROR: Unable to deserialize!\n";
    }
    ret_value = vaf::Result<bool>::FromValue(deserialized.vaf_value_internal());
  } else {
    ret_value = vaf::Result<bool>::FromError(vaf::Error(vaf::ErrorCode::kUnknown,"Kvs get failed."));
    logger_.LogWarn() <<  "Get failed for Persistency.";
  }

  return ret_value;
}

::vaf::Result<void> Persistency::Set_BoolValue(const vaf::String& key, const bool& value) noexcept{
  protobuf::basetypes::Bool proto_message;
  proto_message.set_vaf_value_internal(value);
  size_t nbytes = proto_message.ByteSizeLong();
  std::string temp;
  if (nbytes) {
    proto_message.SerializeToString(&temp);
  }

  vaf::String serialized(temp.c_str());
  return Set(key, serialized);
}
::vaf::Result<float> Persistency::Get_FloatValue(const vaf::String& key) noexcept{
  vaf::Result<float> ret_value{vaf::Result<float>::FromError(vaf::ErrorCode::kNotOk, "Get failed.")};

  vaf::Result<vaf::String> result = Get(key);
  if (result.HasValue()) {
    protobuf::basetypes::Float deserialized;
    if (!deserialized.ParseFromString(result.Value().c_str())) {
      vaf::OutputSyncStream{std::cerr} << "ERROR: Unable to deserialize!\n";
    }
    ret_value = vaf::Result<float>::FromValue(deserialized.vaf_value_internal());
  } else {
    ret_value = vaf::Result<float>::FromError(vaf::Error(vaf::ErrorCode::kUnknown,"Kvs get failed."));
    logger_.LogWarn() <<  "Get failed for Persistency.";
  }

  return ret_value;
}

::vaf::Result<void> Persistency::Set_FloatValue(const vaf::String& key, const float& value) noexcept{
  protobuf::basetypes::Float proto_message;
  proto_message.set_vaf_value_internal(value);
  size_t nbytes = proto_message.ByteSizeLong();
  std::string temp;
  if (nbytes) {
    proto_message.SerializeToString(&temp);
  }

  vaf::String serialized(temp.c_str());
  return Set(key, serialized);
}
::vaf::Result<double> Persistency::Get_DoubleValue(const vaf::String& key) noexcept{
  vaf::Result<double> ret_value{vaf::Result<double>::FromError(vaf::ErrorCode::kNotOk, "Get failed.")};

  vaf::Result<vaf::String> result = Get(key);
  if (result.HasValue()) {
    protobuf::basetypes::Double deserialized;
    if (!deserialized.ParseFromString(result.Value().c_str())) {
      vaf::OutputSyncStream{std::cerr} << "ERROR: Unable to deserialize!\n";
    }
    ret_value = vaf::Result<double>::FromValue(deserialized.vaf_value_internal());
  } else {
    ret_value = vaf::Result<double>::FromError(vaf::Error(vaf::ErrorCode::kUnknown,"Kvs get failed."));
    logger_.LogWarn() <<  "Get failed for Persistency.";
  }

  return ret_value;
}

::vaf::Result<void> Persistency::Set_DoubleValue(const vaf::String& key, const double& value) noexcept{
  protobuf::basetypes::Double proto_message;
  proto_message.set_vaf_value_internal(value);
  size_t nbytes = proto_message.ByteSizeLong();
  std::string temp;
  if (nbytes) {
    proto_message.SerializeToString(&temp);
  }

  vaf::String serialized(temp.c_str());
  return Set(key, serialized);
}

::vaf::Result<::vaf::String> Persistency::Get_StringValue(const vaf::String& key) noexcept{
  vaf::Result<::vaf::String> ret_value{vaf::Result<::vaf::String>::FromError(vaf::ErrorCode::kNotOk, "Get failed.")};

  vaf::Result<vaf::String> result = Get(key);
  if (result.HasValue()) {
    protobuf::vaf::String deserialized;
    if (!deserialized.ParseFromString(result.Value().c_str())) {
      vaf::OutputSyncStream{std::cerr} << "ERROR: Unable to deserialize!\n";
    }
    ::vaf::String value;
    protobuf::vaf::StringProtoToVaf(deserialized, value);
    ret_value = vaf::Result<::vaf::String>::FromValue(value);
  } else {
    ret_value = vaf::Result<::vaf::String>::FromError(vaf::Error(vaf::ErrorCode::kUnknown,"Kvs get failed."));
    logger_.LogWarn() <<  "Get failed for Persistency.";
  }

  return ret_value;
}

::vaf::Result<void> Persistency::Set_StringValue(const vaf::String& key,
                                                            const ::vaf::String& value) noexcept{
  protobuf::vaf::String proto_message;
  protobuf::vaf::StringVafToProto(value, proto_message);
  size_t nbytes = proto_message.ByteSizeLong();
  std::string temp;
  if (nbytes) {
    proto_message.SerializeToString(&temp);
  }

  vaf::String serialized(temp.c_str());
  return Set(key, serialized);
}
::vaf::Result<::test::MyArray> Persistency::Get_MyArrayValue(const vaf::String& key) noexcept{
  vaf::Result<::test::MyArray> ret_value{vaf::Result<::test::MyArray>::FromError(vaf::ErrorCode::kNotOk, "Get failed.")};

  vaf::Result<vaf::String> result = Get(key);
  if (result.HasValue()) {
    protobuf::test::MyArray deserialized;
    if (!deserialized.ParseFromString(result.Value().c_str())) {
      vaf::OutputSyncStream{std::cerr} << "ERROR: Unable to deserialize!\n";
    }
    ::test::MyArray value;
    protobuf::test::MyArrayProtoToVaf(deserialized, value);
    ret_value = vaf::Result<::test::MyArray>::FromValue(value);
  } else {
    ret_value = vaf::Result<::test::MyArray>::FromError(vaf::Error(vaf::ErrorCode::kUnknown,"Kvs get failed."));
    logger_.LogWarn() <<  "Get failed for Persistency.";
  }

  return ret_value;
}

::vaf::Result<void> Persistency::Set_MyArrayValue(const vaf::String& key,
                                                            const ::test::MyArray& value) noexcept{
  protobuf::test::MyArray proto_message;
  protobuf::test::MyArrayVafToProto(value, proto_message);
  size_t nbytes = proto_message.ByteSizeLong();
  std::string temp;
  if (nbytes) {
    proto_message.SerializeToString(&temp);
  }

  vaf::String serialized(temp.c_str());
  return Set(key, serialized);
}


} // namespace persistency
