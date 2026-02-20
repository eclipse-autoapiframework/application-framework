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
/*!        \file  protobuf_transformer.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef PROTOBUF_TEST_PROTOBUF_TRANSFORMER_H
#define PROTOBUF_TEST_PROTOBUF_TRANSFORMER_H

#include "protobuf/test2/protobuf_transformer.h"
#include "protobuf_test.pb.h"
#include "protobuf_test2.pb.h"
#include "test/impl_type_myarray.h"
#include "test/impl_type_mymap.h"
#include "test/impl_type_mystring.h"
#include "test/impl_type_mystruct.h"
#include "test/impl_type_mytyperef.h"
#include "test/impl_type_myvector.h"
#include "test2/impl_type_mystruct.h"
#include <cstdlib>
#include "vaf/output_sync_stream.h"

namespace protobuf {
namespace test {

void MyArrayVafToProto(const ::test::MyArray &in, MyArray &out);
void MyArrayProtoToVaf(const MyArray &in, ::test::MyArray &out);
void MyVectorVafToProto(const ::test::MyVector &in, MyVector &out);
void MyVectorProtoToVaf(const MyVector &in, ::test::MyVector &out);
void MyMapVafToProto(const ::test::MyMap &in, MyMap &out);
void MyMapProtoToVaf(const MyMap &in, ::test::MyMap &out);
void MyStringVafToProto(const ::test::MyString &in, MyString &out);
void MyStringProtoToVaf(const MyString &in, ::test::MyString &out);
void MyEnumVafToProto(const ::test::MyEnum &in, MyEnum &out);
void MyEnumProtoToVaf(const MyEnum &in, ::test::MyEnum &out);
void MyStructVafToProto(const ::test::MyStruct &in, MyStruct &out);
void MyStructProtoToVaf(const MyStruct &in, ::test::MyStruct &out);
void MyTypeRefVafToProto(const ::test::MyTypeRef &in, MyTypeRef &out);
void MyTypeRefProtoToVaf(const MyTypeRef &in, ::test::MyTypeRef &out);
inline void MyArrayVafToProto(const ::test::MyArray &in, MyArray &out) {
  out.Clear();
  for (int i=0;i<in.size();i++) {
    out.mutable_vaf_value_internal()->Add(in[i]);
  }
}
inline void MyArrayProtoToVaf(const MyArray &in, ::test::MyArray &out) {
  for (int i=0;i<out.size();i++) {
    out[i]=in.vaf_value_internal()[i];
  }
}
inline void MyVectorVafToProto(const ::test::MyVector &in, MyVector &out) {
  out.Clear();
  for (auto element_in :in) {
      out.mutable_vaf_value_internal()->Add(element_in);
  }
}
inline void MyVectorProtoToVaf(const MyVector &in, ::test::MyVector &out) {
  out.clear();
  for (auto element_in :in.vaf_value_internal()) {
    out.push_back(element_in);
  }
}
inline void MyMapEntryVafToProto(const ::std::uint64_t &in_key, ::test::MyString &in_value,  MyMapEntry &out) {
  out.set_vaf_key_internal(in_key);
  ::protobuf::test::MyStringVafToProto(in_value, *out.mutable_vaf_value_internal());
}
inline void MyMapEntryProtoToVaf(const MyMapEntry &in, ::std::uint64_t &out_key, ::test::MyString &out_value) {
  out_key = in.vaf_key_internal();
  ::protobuf::test::MyStringProtoToVaf(in.vaf_value_internal(), out_value);
}
inline void MyMapVafToProto(const ::test::MyMap &in, MyMap &out) {
  out.Clear();
  for (auto in_entry: in) {
    MyMapEntry out_entry{};
    MyMapEntryVafToProto(in_entry.first, in_entry.second, out_entry);
    out.mutable_vaf_entry_internal()->Add(std::move(out_entry));
  }
}
inline void MyMapProtoToVaf(const MyMap &in, ::test::MyMap &out) {
  out.clear();
  for (auto in_entry: in.vaf_entry_internal()) {
    std::pair<::std::uint64_t, ::test::MyString> out_entry{};
    MyMapEntryProtoToVaf(in_entry, out_entry.first, out_entry.second);
    out.insert(std::move(out_entry));
  }
}
inline void MyStringVafToProto(const ::test::MyString &in, MyString &out) {
    (*out.mutable_vaf_value_internal()) = in.c_str();
}
inline void MyStringProtoToVaf(const MyString &in, ::test::MyString &out) {
    out = in.vaf_value_internal();
}
inline void MyEnumVafToProto(const ::test::MyEnum &in, MyEnum &out) {
    out.set_vaf_value_internal(static_cast<typename std::underlying_type<::test::MyEnum>::type>(in));
}
inline void MyEnumProtoToVaf(const MyEnum &in, ::test::MyEnum &out) {
  out = static_cast<::test::MyEnum>(in.vaf_value_internal());
}
inline void MyStructVafToProto(const ::test::MyStruct &in, MyStruct &out) {
  ::protobuf::test2::MyStructVafToProto(in.MySub1, *out.mutable_mysub1());
  ::protobuf::test::MyVectorVafToProto(in.MySub2, *out.mutable_mysub2());
}
inline void MyStructProtoToVaf(const MyStruct &in, ::test::MyStruct &out) {
  ::protobuf::test2::MyStructProtoToVaf(in.mysub1(), out.MySub1);
  ::protobuf::test::MyVectorProtoToVaf(in.mysub2(), out.MySub2);
}
inline void MyTypeRefVafToProto(const ::test::MyTypeRef &in, MyTypeRef &out) {
  out.set_vaf_value_internal(in);
}
inline void MyTypeRefProtoToVaf(const MyTypeRef &in, ::test::MyTypeRef &out) {
  out = in.vaf_value_internal();
}

} // namespace test
} // namespace protobuf

#endif // PROTOBUF_TEST_PROTOBUF_TRANSFORMER_H
