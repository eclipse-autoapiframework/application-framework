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

#ifndef PROTOBUF_INTERFACE_TEST_MYINTERFACE_PROTOBUF_TRANSFORMER_H
#define PROTOBUF_INTERFACE_TEST_MYINTERFACE_PROTOBUF_TRANSFORMER_H

#include "protobuf_interface_test_MyInterface.pb.h"
#include "test/my_operation.h"
#include "test/my_getter.h"

namespace protobuf {
namespace interface {
namespace test {
namespace MyInterface {

inline void my_data_element1VafToProto(const ::std::uint64_t &in, my_data_element1 &out) {
  out.set_vaf_value_internal(in);
}
inline void my_data_element1ProtoToVaf(const my_data_element1 &in, ::std::uint64_t &out) {
  out = in.vaf_value_internal();
}
inline void my_data_element2VafToProto(const ::std::uint64_t &in, my_data_element2 &out) {
  out.set_vaf_value_internal(in);
}
inline void my_data_element2ProtoToVaf(const my_data_element2 &in, ::std::uint64_t &out) {
  out = in.vaf_value_internal();
}
inline void MyVoidOperationInVafToProto(const ::std::uint64_t& in_in, MyVoidOperation_in &out){
  out.set_in(in_in);
}
inline void MyVoidOperationInProtoToVaf(const MyVoidOperation_in &in, ::std::uint64_t& out_in) {
  out_in = in.in();
}
inline void MyOperationOutVafToProto(const ::test::MyOperation::Output &in, MyOperation_out &out) {
  out.set_out(in.out);
  out.set_inout(in.inout);
}
inline void MyOperationOutProtoToVaf(const MyOperation_out &in, ::test::MyOperation::Output &out) {
  out.out = in.out();
  out.inout = in.inout();
}
inline void MyOperationInVafToProto(const ::std::uint64_t& in_in, const ::std::uint64_t& in_inout, MyOperation_in &out){
  out.set_in(in_in);
  out.set_inout(in_inout);
}
inline void MyOperationInProtoToVaf(const MyOperation_in &in, ::std::uint64_t& out_in, ::std::uint64_t& out_inout) {
  out_in = in.in();
  out_inout = in.inout();
}
inline void MyGetterOutVafToProto(const ::test::MyGetter::Output &in, MyGetter_out &out) {
  out.set_a(in.a);
}
inline void MyGetterOutProtoToVaf(const MyGetter_out &in, ::test::MyGetter::Output &out) {
  out.a = in.a();
}
inline void MySetterInVafToProto(const ::std::uint64_t& in_a, MySetter_in &out){
  out.set_a(in_a);
}
inline void MySetterInProtoToVaf(const MySetter_in &in, ::std::uint64_t& out_a) {
  out_a = in.a();
}

} // namespace MyInterface
} // namespace test
} // namespace interface
} // namespace protobuf

#endif // PROTOBUF_INTERFACE_TEST_MYINTERFACE_PROTOBUF_TRANSFORMER_H
