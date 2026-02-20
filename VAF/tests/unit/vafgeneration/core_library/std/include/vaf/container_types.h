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
/*!        \file  container_types.h
 *         \brief
 *
 *********************************************************************************************************************/

#ifndef VAF_H_
#define VAF_H_

#include <cstdint>
#include <map>
#include <string>
#include <vector>

namespace vaf {

template <typename CharT, typename Traits = std::char_traits<CharT>, typename Allocator = std::allocator<CharT>>
using basic_string = std::basic_string<CharT, Traits, Allocator>;
using String = basic_string<char>;

template <typename T, typename Allocator = std::allocator<T>>
using Vector = std::vector<T, Allocator>;

template <typename K, typename V, typename C = std::less<K>, typename Allocator = std::allocator<std::pair<K const, V>>>
using Map = std::map<K, V, C, Allocator>;

template <typename T>
using hash = std::hash<T>;

}  // namespace vaf

#endif  // VAF_H_
