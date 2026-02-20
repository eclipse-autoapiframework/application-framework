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

#ifndef PROTOBUF_TEST2_PROTOBUF_TRANSFORMER_H
#define PROTOBUF_TEST2_PROTOBUF_TRANSFORMER_H

#include "protobuf_test2.pb.h"
#include "test2/impl_type_myarray.h"
#include "test2/impl_type_mystruct.h"
#include "test2/impl_type_myvector.h"
#include "vaf/output_sync_stream.h"
#include <cstdlib>

namespace protobuf {
namespace test2 {

void MyArrayVafToProto(const ::test2::MyArray &in, MyArray &out);
void MyArrayProtoToVaf(const MyArray &in, ::test2::MyArray &out);
void MyVectorVafToProto(const ::test2::MyVector &in, MyVector &out);
void MyVectorProtoToVaf(const MyVector &in, ::test2::MyVector &out);
void MyStructVafToProto(const ::test2::MyStruct &in, MyStruct &out);
void MyStructProtoToVaf(const MyStruct &in, ::test2::MyStruct &out);
inline void MyArrayVafToProto(const ::test2::MyArray &in, MyArray &out) {
  out.Clear();
  for (int i=0;i<in.size();i++) {
    out.mutable_vaf_value_internal()->Add(in[i]);
  }
}
inline void MyArrayProtoToVaf(const MyArray &in, ::test2::MyArray &out) {
  for (int i=0;i<out.size();i++) {
    out[i]=in.vaf_value_internal()[i];
  }
}
inline void MyVectorVafToProto(const ::test2::MyVector &in, MyVector &out) {
  out.Clear();
  for (auto element_in :in) {
      out.mutable_vaf_value_internal()->Add(element_in);
  }
}
inline void MyVectorProtoToVaf(const MyVector &in, ::test2::MyVector &out) {
  out.clear();
  for (auto element_in :in.vaf_value_internal()) {
    out.push_back(element_in);
  }
}
inline void MyStructVafToProto(const ::test2::MyStruct &in, MyStruct &out) {
  ::protobuf::test2::MyStructVafToProto(in.MySub1, *out.mutable_mysub1());
  ::protobuf::test2::MyVectorVafToProto(in.MySub2, *out.mutable_mysub2());
}
inline void MyStructProtoToVaf(const MyStruct &in, ::test2::MyStruct &out) {
  ::protobuf::test2::MyStructProtoToVaf(in.mysub1(), out.MySub1);
  ::protobuf::test2::MyVectorProtoToVaf(in.mysub2(), out.MySub2);
}

} // namespace test2
} // namespace protobuf

#endif // PROTOBUF_TEST2_PROTOBUF_TRANSFORMER_H
