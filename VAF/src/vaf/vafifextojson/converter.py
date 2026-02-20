# Copyright (c) 2024-2026 by Vector Informatik GmbH. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""IFEX model to VAF model converter."""

# pylint: disable=too-many-lines
import re
from pathlib import Path
from typing import Any

from ifex.models.ifex.ifex_ast import Enumeration, Namespace, Struct, Typedef

from vaf import vafmodel

from .ifex_helper import load_ifex_file, load_ifex_with_includes

# Global registry to track which source files define each type FQN
# Maps FQN string to set of source file paths
_type_source_registry: dict[str, set[str]] = {}


def _split_type_name(type_ref: str) -> tuple[str, str]:
    """Split a fully qualified type name into namespace and name

    Args:
        type_ref: Fully qualified type name (e.g., "vaf::String", "MyNamespace::MyType", "int32_t")

    Returns:
        Tuple of (name, namespace) - namespace is empty string if no namespace
    """
    if "::" in type_ref:
        parts = type_ref.rsplit("::", 1)
        return (parts[1], parts[0])
    return (type_ref, "")


def _get_type_fqn(type_obj: Any) -> str:
    """Get fully qualified name for any vafmodel type object

    Args:
        type_obj: Any vafmodel type object with Name and Namespace attributes

    Returns:
        Fully qualified name in format "Namespace::Name" or just "Name" if no namespace
    """
    if hasattr(type_obj, "Namespace") and hasattr(type_obj, "Name"):
        return f"{type_obj.Namespace}::{type_obj.Name}" if type_obj.Namespace else type_obj.Name
    raise ValueError(f"Object {type_obj} does not have Name and Namespace attributes")


# Mapping of IFEX data types to VAF base types
IFEX_TO_VAF_TYPE_MAP = {
    # Integer types
    "int8": "int8_t",
    "int16": "int16_t",
    "int32": "int32_t",
    "int64": "int64_t",
    "uint8": "uint8_t",
    "uint16": "uint16_t",
    "uint32": "uint32_t",
    "uint64": "uint64_t",
    # Floating point types
    "float": "float",
    "double": "double",
    # Boolean type
    "boolean": "bool",
    "bool": "bool",
}


def _ensure_string_type() -> tuple[str, vafmodel.String]:
    """Create a String type

    Returns:
        Tuple of (type_reference, String object) - e.g., ("vaf::String", String(...))
    """
    string_type = vafmodel.String(Name="String", Namespace="vaf")
    print("Created String type: vaf::String")
    return ("vaf::String", string_type)


def _create_vector_type(base_type: str, vector_name: str, namespace: str) -> vafmodel.Vector:
    """Create a VAF Vector type for the given base type

    Args:
        base_type: The element type of the vector (e.g., "float", "vaf::String")
        vector_name: Name for the vector type (e.g., "FloatVector", "StringArray")
        namespace: Namespace for the vector type

    Returns:
        VAF Vector object
    """
    # Split base_type into name and namespace
    name, ns = _split_type_name(base_type)

    vector = vafmodel.Vector(
        Name=vector_name,
        Namespace=namespace,
        TypeRef=vafmodel.DataType(Name=name, Namespace=ns),
    )
    print(f"Created Vector type: {vector_name} with element type {base_type} in namespace '{namespace}'")
    return vector


def _create_map_type(key_type: str, value_type: str, map_name: str, namespace: str) -> vafmodel.Map:
    """Create a VAF Map type for the given key and value types

    Args:
        key_type: The key type of the map (e.g., "string", "int32_t", "vaf::String")
        value_type: The value type of the map (e.g., "float", "Coordinates")
        map_name: Name for the map type (e.g., "SensorDataMap")
        namespace: Namespace for the map type

    Returns:
        VAF Map object
    """
    # Split types into name and namespace
    key_name, key_ns = _split_type_name(key_type)
    value_name, value_ns = _split_type_name(value_type)

    map_obj = vafmodel.Map(
        Name=map_name,
        Namespace=namespace,
        MapKeyTypeRef=vafmodel.DataType(Name=key_name, Namespace=key_ns),
        MapValueTypeRef=vafmodel.DataType(Name=value_name, Namespace=value_ns),
    )
    print(
        f"Created Map type: {map_name} with key type {key_type} and value type {value_type} in namespace '{namespace}'"
    )
    return map_obj


def _create_variant_type(variant_types: list[str], variant_name: str, namespace: str) -> vafmodel.Variant:
    """Create a VAF Variant type for the given variant types

    Args:
        variant_types: List of types that can be held by the variant (e.g., ["int32_t", "float", "vaf::String"])
        variant_name: Name for the variant type (e.g., "DataVariant", "ValueUnion")
        namespace: Namespace for the variant type

    Returns:
        VAF Variant object
    """
    # Split each type into name and namespace
    variant_type_refs = []
    for vtype in variant_types:
        name, ns = _split_type_name(vtype)
        variant_type_refs.append(vafmodel.DataType(Name=name, Namespace=ns))

    variant_obj = vafmodel.Variant(
        Name=variant_name,
        Namespace=namespace,
        VariantTypeRefs=variant_type_refs,
    )
    types_str = ", ".join(variant_types)
    print(f"Created Variant type: {variant_name} with types [{types_str}] in namespace '{namespace}'")
    return variant_obj


def _parse_map_type(map_type_str: str) -> tuple[str, str] | None:
    """Parse a map type string like 'map<string, float>' into key and value types

    Args:
        map_type_str: Map type string in format "map<key_type, value_type>"

    Returns:
        Tuple of (key_type, value_type) or None if parsing fails
    """
    # Match map<...> or Map<...>
    match = re.match(r"[Mm]ap<\s*([^,]+)\s*,\s*([^>]+)\s*>", map_type_str)
    if match:
        key_type = match.group(1).strip()
        value_type = match.group(2).strip()
        return (key_type, value_type)
    return None


def _parse_variant_type(variant_type_str: str) -> list[str] | None:
    """Parse a variant/union type string like 'variant<int32, float, string>' into a list of types

    Args:
        variant_type_str: Variant type string in format "variant<type1, type2, ...>" or "union<type1, type2, ...>"

    Returns:
        List of types or None if parsing fails
    """
    # Match variant<...> or union<...> (case insensitive)
    match = re.match(r"(?:variant|union)<\s*([^>]+)\s*>", variant_type_str, re.IGNORECASE)
    if match:
        types_str = match.group(1)
        # Split by comma and strip whitespace from each type
        variant_types = [t.strip() for t in types_str.split(",")]
        return variant_types
    return None


# pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals,too-many-nested-blocks,too-many-statements
def _map_ifex_type_to_vaf(
    ifex_type: str,
    current_namespace: str,
    local_strings: dict[str, vafmodel.String],
    local_vectors: dict[str, vafmodel.Vector],
    local_maps: dict[str, vafmodel.Map],
    local_variants: dict[str, vafmodel.Variant],
) -> str:
    # pylint: disable=too-many-return-statements,too-many-branches
    """Map an IFEX data type to VAF data type

    Args:
        ifex_type: IFEX data type name
        current_namespace: Current namespace for resolving relative type references
        local_strings: Local dictionary to collect created String types
        local_vectors: Local dictionary to collect created Vector objects
        local_maps: Local dictionary to collect created Map objects
        local_variants: Local dictionary to collect created Variant objects

    Returns:
        VAF data type name
    """
    # Handle "string" type - need to create a String type in VAF
    if ifex_type == "string":
        type_ref, string_obj = _ensure_string_type()
        local_strings["string"] = string_obj
        return type_ref

    # Handle array types (e.g., "float[]", "string[]")
    if ifex_type.endswith("[]"):
        base_type = ifex_type[:-2]  # Remove the "[]" suffix

        # Handle string arrays specially
        if base_type == "string":
            type_ref, string_obj = _ensure_string_type()
            local_strings["string"] = string_obj
            base_type = type_ref
            vector_name = "StringArray"
        else:
            # Map the base type if it's a primitive
            base_type = IFEX_TO_VAF_TYPE_MAP.get(base_type, base_type)
            # Convert dots to :: for fully qualified type names
            if "." in base_type:
                base_type = base_type.replace(".", "::")
            # Create a name for the vector type
            vector_name = f"{base_type.replace('_t', '').replace('::', '').title()}Array"

        vector_tuple = _create_vector_type(base_type, vector_name, namespace="ifex_to_vaf")
        local_vectors[vector_name] = vector_tuple
        # Return fully qualified name
        return f"ifex_to_vaf::{vector_name}"

    # Handle map types (e.g., "map<string, float>")
    if ifex_type.startswith("map<") or ifex_type.startswith("Map<"):
        parsed = _parse_map_type(ifex_type)
        if parsed:
            key_type, value_type = parsed
            # Map the types
            if key_type == "string":
                type_ref, string_obj = _ensure_string_type()
                local_strings["string"] = string_obj
                key_type = type_ref
            else:
                key_type = IFEX_TO_VAF_TYPE_MAP.get(key_type, key_type)
                # Convert dots to :: for fully qualified type names
                if "." in key_type:
                    key_type = key_type.replace(".", "::")

            if value_type == "string":
                type_ref, string_obj = _ensure_string_type()
                local_strings["string"] = string_obj
                value_type = type_ref
            else:
                value_type = IFEX_TO_VAF_TYPE_MAP.get(value_type, value_type)
                # Convert dots to :: for fully qualified type names
                if "." in value_type:
                    value_type = value_type.replace(".", "::")

            # Generate a map name based on key and value types
            key_name = key_type.replace("_t", "").replace("::", "").title()
            value_name = value_type.replace("_t", "").replace("::", "").title()
            map_name = f"{key_name}{value_name}Map"

            map_tuple = _create_map_type(key_type, value_type, map_name, namespace="ifex_to_vaf")
            local_maps[map_name] = map_tuple
            # Return fully qualified name
            return f"ifex_to_vaf::{map_name}"

        print(f"Warning: Could not parse map type '{ifex_type}' - using as-is")
        return ifex_type

    # Handle variant/union types (e.g., "variant<int32, float, string>", "union<int32_t, string>")
    if ifex_type.lower().startswith("variant<") or ifex_type.lower().startswith("union<"):
        parsed_variant: list[str] | None = _parse_variant_type(ifex_type)
        if parsed_variant:
            variant_types = []
            for vtype in parsed_variant:
                # Map the type
                if vtype == "string":
                    type_ref, string_obj = _ensure_string_type()
                    local_strings["string"] = string_obj
                    variant_types.append(type_ref)
                else:
                    mapped_type = IFEX_TO_VAF_TYPE_MAP.get(vtype, vtype)
                    # Convert dots to :: for fully qualified type names
                    if "." in mapped_type:
                        mapped_type = mapped_type.replace(".", "::")
                    # If the type doesn't have a namespace and isn't a base type, add current namespace
                    if "::" not in mapped_type and mapped_type not in IFEX_TO_VAF_TYPE_MAP.values():
                        if current_namespace:
                            mapped_type = f"{current_namespace}::{mapped_type}"
                    variant_types.append(mapped_type)

            # Generate a variant name based on the types
            type_names = [t.replace("_t", "").replace("::", "").title() for t in variant_types]
            variant_name = "".join(type_names) + "Variant"

            variant_tuple = _create_variant_type(variant_types, variant_name, namespace="ifex_to_vaf")
            local_variants[variant_name] = variant_tuple
            # Return fully qualified name
            return f"ifex_to_vaf::{variant_name}"

        print(f"Warning: Could not parse variant type '{ifex_type}' - using as-is")
        return ifex_type

    # Check if it's a base type that needs mapping
    if ifex_type in IFEX_TO_VAF_TYPE_MAP:
        return IFEX_TO_VAF_TYPE_MAP[ifex_type]

    # Handle fully qualified names with dots (e.g., "Common.Types.Position" -> "Common::Types::Position")
    if "." in ifex_type:
        return ifex_type.replace(".", "::")

    # If type doesn't contain namespace separator and we have a current namespace,
    # it's a relative reference to a type in the same namespace
    if current_namespace and "::" not in ifex_type:
        return f"{current_namespace}::{ifex_type}"

    # Otherwise return as-is (custom types)
    return ifex_type


# pylint: disable=too-many-arguments,too-many-positional-arguments
def _convert_ifex_struct_to_vaf(
    ifex_struct: Struct,
    namespace: str,
    local_strings: dict[str, vafmodel.String],
    local_vectors: dict[str, vafmodel.Vector],
    local_maps: dict[str, vafmodel.Map],
    local_variants: dict[str, vafmodel.Variant],
) -> vafmodel.Struct:
    """Convert an IFEX struct to VAF Struct

    Args:
        ifex_struct: IFEX Struct object
        namespace: Namespace for the struct
        local_strings: Local dictionary to collect created String types
        local_vectors: Local dictionary to collect created Vector objects
        local_maps: Local dictionary to collect created Map objects
        local_variants: Local dictionary to collect created Variant objects

    Returns:
        VAF Struct
    """
    members = []
    if ifex_struct.members:
        for member in ifex_struct.members:
            # Map IFEX type to VAF type, passing namespace for relative type resolution
            vaf_type = _map_ifex_type_to_vaf(
                member.datatype, namespace, local_strings, local_vectors, local_maps, local_variants
            )
            name, ns = _split_type_name(vaf_type)
            type_ref = vafmodel.DataType(Name=name, Namespace=ns)
            members.append(
                vafmodel.SubElement(
                    Name=member.name,
                    TypeRef=type_ref,
                    IsOptional=False,
                )
            )

    return vafmodel.Struct(
        Name=ifex_struct.name,
        Namespace=namespace,
        SubElements=members,
    )


def _convert_ifex_enum_to_vaf(ifex_enum: Enumeration, namespace: str) -> vafmodel.VafEnum:
    """Convert an IFEX enumeration to VAF VafEnum

    Args:
        ifex_enum: IFEX Enumeration object
        namespace: Namespace for the enum

    Returns:
        VAF VafEnum
    """
    literals = []
    for option in ifex_enum.options:
        literals.append(
            vafmodel.EnumLiteral(
                Item=option.name,
                Value=int(option.value) if option.value is not None else 0,
            )
        )

    return vafmodel.VafEnum(
        Name=ifex_enum.name,
        Namespace=namespace,
        Literals=literals,
    )


# pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals,too-many-return-statements,too-many-branches,too-many-statements
def _convert_ifex_typedef_to_vaf(
    ifex_typedef: Typedef,
    namespace: str,
    local_strings: dict[str, vafmodel.String],
    local_vectors: dict[str, vafmodel.Vector],
    local_maps: dict[str, vafmodel.Map],
    local_typerefs: dict[str, vafmodel.TypeRef],
    local_variants: dict[str, vafmodel.Variant],
) -> str:
    """Convert an IFEX typedef to VAF TypeRef, Vector, Map, or Variant

    Args:
        ifex_typedef: IFEX Typedef object
        namespace: Namespace for the typedef
        local_strings: Local dictionary to collect created String types
        local_vectors: Local dictionary to collect created Vector objects
        local_maps: Local dictionary to collect created Map objects
        local_typerefs: Local dictionary to collect created TypeRef objects
        local_variants: Local dictionary to collect created Variant objects

    Returns:
        TypeRef, Vector, Map, or Variant name
    """
    # Map the target type
    if ifex_typedef.datatype is None:
        print(f"Warning: Typedef '{ifex_typedef.name}' has no datatype, skipping")
        return str(ifex_typedef.name)

    typedef_name: str = ifex_typedef.name

    # Special handling for array typedefs: create the Vector directly with the typedef name
    if ifex_typedef.datatype.endswith("[]"):
        base_type = ifex_typedef.datatype[:-2]  # Remove "[]"

        # Handle string arrays specially
        if base_type == "string":
            type_ref, string_obj = _ensure_string_type()
            local_strings["string"] = string_obj
            base_type = type_ref
        else:
            # Map the base type if it's a primitive
            mapped_type = IFEX_TO_VAF_TYPE_MAP.get(base_type, base_type)
            # If not a primitive (wasn't in the map) and doesn't have namespace, qualify with current namespace
            if base_type not in IFEX_TO_VAF_TYPE_MAP and "::" not in mapped_type and "." not in mapped_type:
                # Custom type in same namespace
                base_type = f"{namespace}::{mapped_type}"
            else:
                base_type = mapped_type

        # Create vector with typedef name directly and namespace
        vector_tuple = _create_vector_type(base_type, typedef_name, namespace)
        local_vectors[typedef_name] = vector_tuple
        print(f"Converted typedef (vector): {typedef_name} -> Vector of {base_type} in namespace '{namespace}'")
        return f"{namespace}::{typedef_name}"

    # Special handling for map typedefs: create the Map directly with the typedef name
    if ifex_typedef.datatype.startswith("map<") or ifex_typedef.datatype.startswith("Map<"):
        parsed = _parse_map_type(ifex_typedef.datatype)
        if parsed:
            key_type, value_type = parsed

            # Map the types
            if key_type == "string":
                type_ref, string_obj = _ensure_string_type()
                local_strings["string"] = string_obj
                key_type = type_ref
            else:
                mapped_key = IFEX_TO_VAF_TYPE_MAP.get(key_type, key_type)
                # If not a primitive (wasn't in the map) and doesn't have namespace, qualify with current namespace
                if key_type not in IFEX_TO_VAF_TYPE_MAP and "::" not in mapped_key and "." not in mapped_key:
                    key_type = f"{namespace}::{mapped_key}"
                else:
                    key_type = mapped_key

            if value_type == "string":
                type_ref, string_obj = _ensure_string_type()
                local_strings["string"] = string_obj
                value_type = type_ref
            else:
                mapped_value = IFEX_TO_VAF_TYPE_MAP.get(value_type, value_type)
                # If not a primitive (wasn't in the map) and doesn't have namespace, qualify with current namespace
                if value_type not in IFEX_TO_VAF_TYPE_MAP and "::" not in mapped_value and "." not in mapped_value:
                    value_type = f"{namespace}::{mapped_value}"
                else:
                    value_type = mapped_value

            # Create map with typedef name directly and namespace
            map_tuple = _create_map_type(key_type, value_type, typedef_name, namespace)
            local_maps[typedef_name] = map_tuple
            print(
                f"Converted typedef (map): {typedef_name} -> Map<{key_type}, {value_type}> in namespace '{namespace}'"
            )
            return f"{namespace}::{typedef_name}"

        print(f"Warning: Could not parse map type '{ifex_typedef.datatype}' in typedef '{typedef_name}'")
        return f"{namespace}::{typedef_name}"

    # Special handling for variant/union typedefs: create the Variant directly with the typedef name
    if ifex_typedef.datatype.lower().startswith("variant<") or ifex_typedef.datatype.lower().startswith("union<"):
        parsed_variant_typedef: list[str] | None = _parse_variant_type(ifex_typedef.datatype)
        if parsed_variant_typedef:
            variant_types = []
            for vtype in parsed_variant_typedef:
                # Map the type
                if vtype == "string":
                    type_ref, string_obj = _ensure_string_type()
                    local_strings["string"] = string_obj
                    variant_types.append(type_ref)
                else:
                    mapped_type = IFEX_TO_VAF_TYPE_MAP.get(vtype, vtype)
                    # If the type doesn't have a namespace and isn't a base type, add current namespace
                    if "::" not in mapped_type and mapped_type not in IFEX_TO_VAF_TYPE_MAP.values():
                        mapped_type = f"{namespace}::{mapped_type}"
                    variant_types.append(mapped_type)

            # Create variant with typedef name directly and namespace
            variant_tuple = _create_variant_type(variant_types, typedef_name, namespace)
            local_variants[typedef_name] = variant_tuple
            types_str = ", ".join(variant_types)
            print(f"Converted typedef (variant): {typedef_name} -> Variant<{types_str}> in namespace '{namespace}'")
            return f"{namespace}::{typedef_name}"

        print(f"Warning: Could not parse variant type '{ifex_typedef.datatype}' in typedef '{typedef_name}'")
        return f"{namespace}::{typedef_name}"

    # For non-array, non-map, non-variant typedefs, create a TypeRef
    target_type = _map_ifex_type_to_vaf(
        ifex_typedef.datatype, namespace, local_strings, local_vectors, local_maps, local_variants
    )
    name, ns = _split_type_name(target_type)
    typeref_obj = vafmodel.TypeRef(
        Name=typedef_name,
        Namespace=namespace,
        TypeRef=vafmodel.DataType(Name=name, Namespace=ns),
    )
    local_typerefs[typedef_name] = typeref_obj
    print(f"Converted typedef (typeref): {typedef_name} -> {target_type} in namespace '{namespace}'")
    return f"{namespace}::{typedef_name}"


# pylint: disable=too-many-arguments,too-many-positional-arguments
def _convert_ifex_method_to_vaf_operation(
    ifex_method: Any,
    namespace: str,
    local_strings: dict[str, vafmodel.String],
    local_vectors: dict[str, vafmodel.Vector],
    local_maps: dict[str, vafmodel.Map],
    local_variants: dict[str, vafmodel.Variant],
) -> vafmodel.Operation:
    """Convert an IFEX method to VAF Operation

    Args:
        ifex_method: IFEX Method object
        namespace: Namespace for the operation (used for resolving type references)
        local_strings: Local dictionary to collect created String types
        local_vectors: Local dictionary to collect created Vector objects
        local_maps: Local dictionary to collect created Map objects
        local_variants: Local dictionary to collect created Variant objects

    Returns:
        VAF Operation
    """
    parameters = []

    # Convert input parameters
    if ifex_method.input:
        for param in ifex_method.input:
            vaf_type = _map_ifex_type_to_vaf(
                param.datatype, namespace, local_strings, local_vectors, local_maps, local_variants
            )
            name, ns = _split_type_name(vaf_type)
            type_ref = vafmodel.DataType(Name=name, Namespace=ns)
            parameters.append(
                vafmodel.Parameter(
                    Name=param.name,
                    TypeRef=type_ref,
                    Direction=vafmodel.ParameterDirection.IN,
                )
            )

    # Convert output parameters
    if ifex_method.output:
        for param in ifex_method.output:
            vaf_type = _map_ifex_type_to_vaf(
                param.datatype, namespace, local_strings, local_vectors, local_maps, local_variants
            )
            name, ns = _split_type_name(vaf_type)
            type_ref = vafmodel.DataType(Name=name, Namespace=ns)
            parameters.append(
                vafmodel.Parameter(
                    Name=param.name,
                    TypeRef=type_ref,
                    Direction=vafmodel.ParameterDirection.OUT,
                )
            )

    return vafmodel.Operation(
        Name=ifex_method.name,
        Parameters=parameters,
    )


# pylint: disable=too-many-arguments,too-many-positional-arguments
def _convert_ifex_event_to_vaf_data_element(
    ifex_event: Any,
    namespace: str,
    local_strings: dict[str, vafmodel.String],
    local_vectors: dict[str, vafmodel.Vector],
    local_maps: dict[str, vafmodel.Map],
    local_variants: dict[str, vafmodel.Variant],
) -> vafmodel.DataElement:
    """Convert an IFEX event to VAF DataElement

    Args:
        ifex_event: IFEX Event object
        namespace: Namespace for the data element (used for resolving type references)
        local_strings: Local dictionary to collect created String types
        local_vectors: Local dictionary to collect created Vector objects
        local_maps: Local dictionary to collect created Map objects
        local_variants: Local dictionary to collect created Variant objects

    Returns:
        VAF DataElement
    """
    # Events in IFEX typically map to DataElements in VAF
    # For events with a single parameter, use that parameter's type
    # For events with multiple parameters, we might need a struct (handled separately)

    if ifex_event.input and len(ifex_event.input) > 0:
        # Use the first parameter's type as the DataElement type
        # TODO: Handle multiple parameters by creating a struct  # pylint: disable=fixme
        first_param = ifex_event.input[0]
        vaf_type = _map_ifex_type_to_vaf(
            first_param.datatype, namespace, local_strings, local_vectors, local_maps, local_variants
        )
        name, ns = _split_type_name(vaf_type)
        type_ref = vafmodel.DataType(Name=name, Namespace=ns)
    else:
        # Event with no parameters - use bool as placeholder
        type_ref = vafmodel.DataType(Name="bool", Namespace="")

    return vafmodel.DataElement(
        Name=ifex_event.name,
        TypeRef=type_ref,
    )


# pylint: disable=too-many-arguments,too-many-positional-arguments
def _convert_ifex_property_to_vaf_data_element(
    ifex_property: Any,
    namespace: str,
    local_strings: dict[str, vafmodel.String],
    local_vectors: dict[str, vafmodel.Vector],
    local_maps: dict[str, vafmodel.Map],
    local_variants: dict[str, vafmodel.Variant],
) -> vafmodel.DataElement:
    """Convert an IFEX property to VAF DataElement

    Args:
        ifex_property: IFEX Property object
        namespace: Namespace for the data element (used for resolving type references)
        local_strings: Local dictionary to collect created String types
        local_vectors: Local dictionary to collect created Vector objects
        local_maps: Local dictionary to collect created Map objects
        local_variants: Local dictionary to collect created Variant objects

    Returns:
        VAF DataElement
    """
    vaf_type = _map_ifex_type_to_vaf(
        ifex_property.datatype, namespace, local_strings, local_vectors, local_maps, local_variants
    )
    name, ns = _split_type_name(vaf_type)
    type_ref = vafmodel.DataType(Name=name, Namespace=ns)

    return vafmodel.DataElement(
        Name=ifex_property.name,
        TypeRef=type_ref,
    )


# pylint: disable=too-many-arguments,too-many-positional-arguments
def _convert_ifex_property_to_vaf_operations(
    ifex_property: Any,
    namespace: str,
    local_strings: dict[str, vafmodel.String],
    local_vectors: dict[str, vafmodel.Vector],
    local_maps: dict[str, vafmodel.Map],
    local_variants: dict[str, vafmodel.Variant],
) -> tuple[vafmodel.Operation, vafmodel.Operation]:
    """Convert an IFEX property to VAF getter and setter Operations

    Args:
        ifex_property: IFEX Property object
        namespace: Namespace for the operations (used for resolving type references)
        local_strings: Local dictionary to collect created String types
        local_vectors: Local dictionary to collect created Vector objects
        local_maps: Local dictionary to collect created Map objects
        local_variants: Local dictionary to collect created Variant objects

    Returns:
        Tuple of (getter_operation, setter_operation)
    """
    vaf_type = _map_ifex_type_to_vaf(
        ifex_property.datatype, namespace, local_strings, local_vectors, local_maps, local_variants
    )
    name, ns = _split_type_name(vaf_type)
    type_ref = vafmodel.DataType(Name=name, Namespace=ns)

    # Create getter operation: Get<PropertyName>() -> value
    getter = vafmodel.Operation(
        Name=f"Get{ifex_property.name}",
        Parameters=[
            vafmodel.Parameter(
                Name="value",
                TypeRef=type_ref,
                Direction=vafmodel.ParameterDirection.OUT,
            )
        ],
    )

    # Create setter operation: Set<PropertyName>(value) -> void
    setter = vafmodel.Operation(
        Name=f"Set{ifex_property.name}",
        Parameters=[
            vafmodel.Parameter(
                Name="value",
                TypeRef=type_ref,
                Direction=vafmodel.ParameterDirection.IN,
            )
        ],
    )

    return (getter, setter)


def _extract_data_types_from_namespace(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    namespace: Namespace,
    namespace_path: str,
    local_strings: dict[str, vafmodel.String],
    local_vectors: dict[str, vafmodel.Vector],
    local_maps: dict[str, vafmodel.Map],
    local_typerefs: dict[str, vafmodel.TypeRef],
    local_variants: dict[str, vafmodel.Variant],
) -> tuple[list[vafmodel.Struct], list[vafmodel.VafEnum]]:
    # pylint: disable=too-many-locals,too-many-branches
    """Extract all data types from an IFEX namespace recursively

    Args:
        namespace: IFEX Namespace object
        namespace_path: Current namespace path
        local_strings: Local dictionary to collect created String types
        local_vectors: Local dictionary to collect created Vector objects
        local_maps: Local dictionary to collect created Map objects
        local_typerefs: Local dictionary to collect created TypeRef objects
        local_variants: Local dictionary to collect created Variant objects

    Returns:
        Tuple of (list of VAF Struct objects, list of VAF VafEnum objects)
    """
    structs: list[vafmodel.Struct] = []
    enums: list[vafmodel.VafEnum] = []

    # Convert dots in namespace names to double colons for VAF syntax
    namespace_name = namespace.name.replace(".", "::")
    current_namespace = f"{namespace_path}::{namespace_name}" if namespace_path else namespace_name

    # Convert structs
    if namespace.structs:
        for struct in namespace.structs:
            try:
                vaf_struct = _convert_ifex_struct_to_vaf(
                    struct, current_namespace, local_strings, local_vectors, local_maps, local_variants
                )
                structs.append(vaf_struct)
                print(f"Converted struct: {struct.name}")
            except Exception as e:  # pylint: disable=broad-exception-caught
                print(f"Warning: Could not convert struct '{struct.name}': {e}")

    # Convert enumerations
    if namespace.enumerations:
        for enum in namespace.enumerations:
            try:
                vaf_enum = _convert_ifex_enum_to_vaf(enum, current_namespace)
                enums.append(vaf_enum)
                print(f"Converted enum: {enum.name}")
            except Exception as e:  # pylint: disable=broad-exception-caught
                print(f"Warning: Could not convert enum '{enum.name}': {e}")

    # Convert typedefs (skipped for now)
    if namespace.typedefs:
        for typedef in namespace.typedefs:
            try:
                _convert_ifex_typedef_to_vaf(
                    typedef, current_namespace, local_strings, local_vectors, local_maps, local_typerefs, local_variants
                )
            except Exception as e:  # pylint: disable=broad-exception-caught
                print(f"Warning: Could not process typedef '{typedef.name}': {e}")

    # Warn about includes (not supported yet)
    if namespace.includes:
        for include in namespace.includes:
            include_name = include.file if hasattr(include, "file") else include
            print(f"Warning: IFEX include '{include_name}' is not yet supported - skipping")

    # Process nested namespaces recursively
    if namespace.namespaces:
        for nested_ns in namespace.namespaces:
            nested_structs, nested_enums = _extract_data_types_from_namespace(
                nested_ns, current_namespace, local_strings, local_vectors, local_maps, local_typerefs, local_variants
            )
            structs.extend(nested_structs)
            enums.extend(nested_enums)

    # Note: Interface data types (structs/enums) are extracted in _extract_module_interfaces_from_namespace()
    # to keep all interface-related processing together

    return structs, enums


def _extract_module_interfaces_from_namespace(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    namespace: Namespace,
    namespace_path: str,
    service_name: str,
    local_strings: dict[str, vafmodel.String],
    local_vectors: dict[str, vafmodel.Vector],
    local_maps: dict[str, vafmodel.Map],
    local_variants: dict[str, vafmodel.Variant],
) -> list[vafmodel.ModuleInterface]:
    # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    """Extract module interfaces from an IFEX namespace recursively

    Args:
        namespace: IFEX Namespace object
        namespace_path: Current namespace path
        service_name: Service name from AST (used for top-level namespace module interface naming)
        local_strings: Local dictionary to collect created String types
        local_vectors: Local dictionary to collect created Vector objects
        local_maps: Local dictionary to collect created Map objects
        local_variants: Local dictionary to collect created Variant objects

    Returns:
        List of VAF ModuleInterface objects
    """
    module_interfaces: list[vafmodel.ModuleInterface] = []

    # Convert dots in namespace names to double colons for VAF syntax
    namespace_name = namespace.name.replace(".", "::")
    current_namespace = f"{namespace_path}::{namespace_name}" if namespace_path else namespace_name
    # Check if namespace has methods, events, or properties at top level
    has_methods = namespace.methods and len(namespace.methods) > 0
    has_events = namespace.events and len(namespace.events) > 0
    has_properties = namespace.properties and len(namespace.properties) > 0

    if has_methods or has_events or has_properties:
        operations = []
        data_elements = []

        # Convert methods to operations
        if namespace.methods:
            for method in namespace.methods:
                try:
                    operation = _convert_ifex_method_to_vaf_operation(
                        method, current_namespace, local_strings, local_vectors, local_maps, local_variants
                    )
                    operations.append(operation)
                    print(f"Converted method: {method.name}")
                except Exception as e:  # pylint: disable=broad-exception-caught
                    print(f"Warning: Could not convert method '{method.name}': {e}")

        # Convert events to data elements
        if namespace.events:
            for event in namespace.events:
                try:
                    data_element = _convert_ifex_event_to_vaf_data_element(
                        event, current_namespace, local_strings, local_vectors, local_maps, local_variants
                    )
                    data_elements.append(data_element)
                    print(f"Converted event: {event.name}")
                except Exception as e:  # pylint: disable=broad-exception-caught
                    print(f"Warning: Could not convert event '{event.name}': {e}")

        # Convert properties to data elements and getter/setter operations
        if namespace.properties:
            for prop in namespace.properties:
                try:
                    # Create data element for the property
                    data_element = _convert_ifex_property_to_vaf_data_element(
                        prop, current_namespace, local_strings, local_vectors, local_maps, local_variants
                    )
                    data_elements.append(data_element)

                    # Create getter and setter operations
                    getter, setter = _convert_ifex_property_to_vaf_operations(
                        prop, current_namespace, local_strings, local_vectors, local_maps, local_variants
                    )
                    operations.append(getter)
                    operations.append(setter)

                    print(f"Converted property: {prop.name} (with getter/setter)")
                except Exception as e:  # pylint: disable=broad-exception-caught
                    print(f"Warning: Could not convert property '{prop.name}': {e}")

        # Create ModuleInterface for this namespace
        # Use service_name for top-level namespace (when namespace_path is empty and service_name is provided)
        # Otherwise use the namespace_name
        interface_name = service_name if (service_name and not namespace_path) else namespace_name
        # For top-level namespace, set Namespace to namespace_name; for nested, use namespace_path
        interface_namespace = namespace_name if not namespace_path else namespace_path
        module_interface = vafmodel.ModuleInterface(
            Name=interface_name,
            Namespace=interface_namespace,
            Operations=operations,
            DataElements=data_elements,
        )
        module_interfaces.append(module_interface)

    # Process nested namespaces recursively
    if namespace.namespaces:
        for nested_ns in namespace.namespaces:
            # Nested namespaces don't get the service_name
            nested_interfaces = _extract_module_interfaces_from_namespace(
                nested_ns, current_namespace, "", local_strings, local_vectors, local_maps, local_variants
            )
            module_interfaces.extend(nested_interfaces)

    # Process interface if it exists
    if namespace.interface:
        interface = namespace.interface
        interface_namespace = current_namespace

        operations = []
        data_elements = []

        # Convert interface methods
        if interface.methods:
            for method in interface.methods:
                try:
                    operation = _convert_ifex_method_to_vaf_operation(
                        method, interface_namespace, local_strings, local_vectors, local_maps, local_variants
                    )
                    operations.append(operation)
                    print(f"Converted interface method: {method.name}")
                except Exception as e:  # pylint: disable=broad-exception-caught
                    print(f"Warning: Could not convert interface method '{method.name}': {e}")

        # Convert interface events
        if interface.events:
            for event in interface.events:
                try:
                    data_element = _convert_ifex_event_to_vaf_data_element(
                        event, interface_namespace, local_strings, local_vectors, local_maps, local_variants
                    )
                    data_elements.append(data_element)
                    print(f"Converted interface event: {event.name}")
                except Exception as e:  # pylint: disable=broad-exception-caught
                    print(f"Warning: Could not convert interface event '{event.name}': {e}")

        # Convert interface properties to data elements and getter/setter operations
        if interface.properties:
            for prop in interface.properties:
                try:
                    # Create data element for the property
                    data_element = _convert_ifex_property_to_vaf_data_element(
                        prop, interface_namespace, local_strings, local_vectors, local_maps, local_variants
                    )
                    data_elements.append(data_element)

                    # Create getter and setter operations
                    getter, setter = _convert_ifex_property_to_vaf_operations(
                        prop, interface_namespace, local_strings, local_vectors, local_maps, local_variants
                    )
                    operations.append(getter)
                    operations.append(setter)

                    print(f"Converted interface property: {prop.name} (with getter/setter)")
                except Exception as e:  # pylint: disable=broad-exception-caught
                    print(f"Warning: Could not convert interface property '{prop.name}': {e}")

        # Create ModuleInterface for the interface
        if operations or data_elements:
            module_interface = vafmodel.ModuleInterface(
                Name=interface.name,
                Namespace=current_namespace,
                Operations=operations,
                DataElements=data_elements,
            )
            module_interfaces.append(module_interface)

    return module_interfaces


def _deduplicate_types(
    items_dict: dict[str, list[Any]],
) -> list[Any]:
    """
    Deduplicate types by FQN - keep one instance per fully qualified name.

    Called after conflict validation, so all duplicates are guaranteed to be either:
    - Identical across files, or
    - Layered overrides within same file (where last wins)

    Simply keep the last occurrence of each FQN.

    Args:
        items_dict: Dictionary mapping FQN to list of type instances

    Returns:
        List of deduplicated type instances (one per unique FQN)
    """
    result = []
    for instances in items_dict.values():
        # Keep the last instance for each FQN (handles layering within files)
        result.append(instances[-1])

    return result


# pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals,too-many-branches,too-many-statements
def _check_type_conflicts(
    structs: dict[str, list[vafmodel.Struct]],
    enums: dict[str, list[vafmodel.VafEnum]],
    interfaces: dict[str, list[vafmodel.ModuleInterface]],
    vectors: dict[str, list[vafmodel.Vector]],
    maps: dict[str, list[vafmodel.Map]],
    typerefs: dict[str, list[vafmodel.TypeRef]],
    variants: dict[str, list[vafmodel.Variant]],
) -> None:
    """Check for type conflicts using HYBRID STRATEGY

    Hybrid Strategy Rules:
    1. Within same top-level file (including its includes): Override/layering allowed (last wins)
    2. Between different top-level files: Must be identical or conflict error
    3. Category conflicts: Always error (e.g., Struct vs Enum with same name)

    Args:
        structs: Dict mapping FQN to list of Struct objects
        enums: Dict mapping FQN to list of VafEnum objects
        interfaces: Dict mapping FQN to list of ModuleInterface objects
        vectors: Dict mapping FQN to list of Vector objects
        maps: Dict mapping FQN to list of Map objects
        typerefs: Dict mapping FQN to list of TypeRef objects
        variants: Dict mapping FQN to list of Variant objects

    Raises:
        ValueError: If type conflicts are detected
    """
    errors = []

    # Collect all FQNs that appear in multiple categories
    all_fqns: set[str] = set()
    all_fqns.update(structs.keys())
    all_fqns.update(enums.keys())
    all_fqns.update(interfaces.keys())
    all_fqns.update(vectors.keys())
    all_fqns.update(maps.keys())
    all_fqns.update(typerefs.keys())
    all_fqns.update(variants.keys())

    # Check for category conflicts (same FQN in multiple type dictionaries)
    category_conflicts = []
    for fqn in all_fqns:
        categories = []
        if fqn in structs:
            categories.append("Struct")
        if fqn in enums:
            categories.append("Enum")
        if fqn in interfaces:
            categories.append("ModuleInterface")
        if fqn in vectors:
            categories.append("Vector")
        if fqn in maps:
            categories.append("Map")
        if fqn in typerefs:
            categories.append("TypeRef")
        if fqn in variants:
            categories.append("Variant")

        if len(categories) > 1:
            category_conflicts.append(f"  - '{fqn}' defined as: {', '.join(categories)}")

    if category_conflicts:
        errors.append(
            "❌ Type name conflicts detected (same name used for different type categories):\n"
            + "\n".join(category_conflicts)
            + "\n\nEach type name must belong to only one category "
            + "(Struct, Enum, Vector, Map, TypeRef, Variant, or Interface)."
        )

    # Check for definition conflicts across files for each category
    def check_definition_conflicts(type_dict: dict[str, list[Any]], type_name: str) -> list[str]:
        """Check if types with same FQN from different files have identical definitions

        Args:
            type_dict: Dictionary mapping FQN to list of type instances
            type_name: Name of the type category (e.g., "Struct", "Enum")

        Returns:
            List of conflict error messages
        """
        conflicts = []

        for fqn, instances in type_dict.items():
            if len(instances) <= 1:
                continue

            # Check if this FQN comes from multiple top-level files
            source_files = _type_source_registry[fqn]

            if len(source_files) <= 1:
                continue  # All from same top-level file (including its includes)

            # Multiple top-level files - check if all definitions are identical
            first_dump = instances[0].model_dump()
            for instance in instances[1:]:
                if instance.model_dump() != first_dump:
                    # Found a conflict
                    source_names = ", ".join(Path(f).name for f in source_files)
                    conflicts.append(f"  - {type_name} '{fqn}' defined differently in batch files: {source_names}")
                    break

        return conflicts

    # Check each type category
    struct_conflicts = check_definition_conflicts(structs, "Struct")
    enum_conflicts = check_definition_conflicts(enums, "Enum")
    interface_conflicts = check_definition_conflicts(interfaces, "ModuleInterface")
    vector_conflicts = check_definition_conflicts(vectors, "Vector")
    map_conflicts = check_definition_conflicts(maps, "Map")
    typeref_conflicts = check_definition_conflicts(typerefs, "TypeRef")
    variant_conflicts = check_definition_conflicts(variants, "Variant")

    # Collect all conflict messages with context
    if struct_conflicts:
        errors.append(
            "❌ Conflicting Struct definitions detected across different batch files:\n"
            + "\n".join(struct_conflicts)
            + "\n\nStructs from different top-level batch files must have identical definitions. "
            "Within a single file's include hierarchy, layering/override is supported. "
            "To share a struct across batch files, ensure the definitions are identical."
        )

    if enum_conflicts:
        errors.append(
            "❌ Conflicting Enum definitions detected across different batch files:\n"
            + "\n".join(enum_conflicts)
            + "\n\nEnums from different top-level batch files must have identical definitions. "
            "Within a single file's include hierarchy, layering/override is supported. "
            "To share an enum across batch files, ensure the definitions are identical."
        )

    if interface_conflicts:
        errors.append(
            "❌ Conflicting ModuleInterface definitions detected across different batch files:\n"
            + "\n".join(interface_conflicts)
            + "\n\nModuleInterfaces from different top-level batch files must have identical definitions. "
            "Within a single file's include hierarchy, layering/override is supported. "
            "To share an interface across batch files, ensure the definitions are identical."
        )

    if vector_conflicts:
        errors.append(
            "❌ Conflicting Vector definitions detected across different batch files:\n"
            + "\n".join(vector_conflicts)
            + "\n\nVectors from different top-level batch files must have identical definitions. "
            "Within a single file's include hierarchy, layering/override is supported. "
            "To share a vector across batch files, ensure the definitions are identical."
        )

    if map_conflicts:
        errors.append(
            "❌ Conflicting Map definitions detected across different batch files:\n"
            + "\n".join(map_conflicts)
            + "\n\nMaps from different top-level batch files must have identical definitions. "
            "Within a single file's include hierarchy, layering/override is supported. "
            "To share a map across batch files, ensure the definitions are identical."
        )

    if typeref_conflicts:
        errors.append(
            "❌ Conflicting TypeRef definitions detected across different batch files:\n"
            + "\n".join(typeref_conflicts)
            + "\n\nTypeRefs from different top-level batch files must have identical definitions. "
            "Within a single file's include hierarchy, layering/override is supported. "
            "To share a typedef across batch files, ensure the definitions are identical."
        )

    if variant_conflicts:
        errors.append(
            "❌ Conflicting Variant definitions detected across different batch files:\n"
            + "\n".join(variant_conflicts)
            + "\n\nVariants from different top-level batch files must have identical definitions. "
            "Within a single file's include hierarchy, layering/override is supported. "
            "To share a variant across batch files, ensure the definitions are identical."
        )

    if errors:
        raise ValueError("\n\n".join(errors))


# pylint: disable=too-many-locals
def _process_single_file(
    ifex_file: Path, enable_layering: bool
) -> tuple[
    dict[str, list[vafmodel.Struct]],
    dict[str, list[vafmodel.VafEnum]],
    dict[str, list[vafmodel.ModuleInterface]],
    dict[str, list[vafmodel.Vector]],
    dict[str, list[vafmodel.Map]],
    dict[str, list[vafmodel.TypeRef]],
    dict[str, list[vafmodel.Variant]],
    list[vafmodel.String],
]:
    """Process a single IFEX file and return all its types grouped by FQN

    This function processes each file in isolation, ensuring clean per-file type creation.
    Local dictionaries collect typedef info during processing.
    Types are registered in the global _type_source_registry for tracking.

    Args:
        ifex_file: Path to the IFEX file
        enable_layering: If True, recursively load included IFEX files

    Returns:
        Tuple of (structs_dict, enums_dict, interfaces_dict, vectors_dict,
        maps_dict, typerefs_dict, variants_dict, strings_list)
        where each dict maps FQN to list of instances
    """
    print(f"\nProcessing IFEX file: {ifex_file}")

    # Create local collections for this file's type processing
    local_strings: dict[str, vafmodel.String] = {}
    local_vectors: dict[str, vafmodel.Vector] = {}
    local_maps: dict[str, vafmodel.Map] = {}
    local_typerefs: dict[str, vafmodel.TypeRef] = {}
    local_variants: dict[str, vafmodel.Variant] = {}

    # Load IFEX file to AST (with or without layering)
    if enable_layering:
        ast = load_ifex_with_includes(ifex_file)
    else:
        ast = load_ifex_file(ifex_file)

    # Process all namespaces in this file - collect in dicts grouped by FQN
    file_structs: dict[str, list[vafmodel.Struct]] = {}
    file_enums: dict[str, list[vafmodel.VafEnum]] = {}
    file_interfaces: dict[str, list[vafmodel.ModuleInterface]] = {}

    if ast.namespaces:
        ast_name = ast.name if ast.name else ""
        for namespace in ast.namespaces:
            # Extract data types
            structs, enums = _extract_data_types_from_namespace(
                namespace, "", local_strings, local_vectors, local_maps, local_typerefs, local_variants
            )
            # Register structs and enums with source file and group by FQN
            for struct in structs:
                fqn = _get_type_fqn(struct)
                if fqn not in file_structs:
                    file_structs[fqn] = []
                file_structs[fqn].append(struct)
                if fqn not in _type_source_registry:
                    _type_source_registry[fqn] = set()
                _type_source_registry[fqn].add(str(ifex_file))
            for enum in enums:
                fqn = _get_type_fqn(enum)
                if fqn not in file_enums:
                    file_enums[fqn] = []
                file_enums[fqn].append(enum)
                if fqn not in _type_source_registry:
                    _type_source_registry[fqn] = set()
                _type_source_registry[fqn].add(str(ifex_file))

            # Extract interfaces
            interfaces = _extract_module_interfaces_from_namespace(
                namespace, "", ast_name, local_strings, local_vectors, local_maps, local_variants
            )
            # Register interfaces with source file and group by FQN
            for iface in interfaces:
                fqn = _get_type_fqn(iface)
                if fqn not in file_interfaces:
                    file_interfaces[fqn] = []
                file_interfaces[fqn].append(iface)
                if fqn not in _type_source_registry:
                    _type_source_registry[fqn] = set()
                _type_source_registry[fqn].add(str(ifex_file))

        print(
            f"  Extracted {sum(len(v) for v in file_structs.values())} structs, "
            f"{sum(len(v) for v in file_enums.values())} enums, "
            f"{sum(len(v) for v in file_interfaces.values())} interfaces"
        )

    # Collect all typedefs created during this file's processing from local dicts
    file_vectors: dict[str, list[vafmodel.Vector]] = {}
    for vector_obj in local_vectors.values():
        fqn = _get_type_fqn(vector_obj)
        if fqn not in file_vectors:
            file_vectors[fqn] = []
        file_vectors[fqn].append(vector_obj)
        if fqn not in _type_source_registry:
            _type_source_registry[fqn] = set()
        _type_source_registry[fqn].add(str(ifex_file))

    file_maps: dict[str, list[vafmodel.Map]] = {}
    for map_obj in local_maps.values():
        fqn = _get_type_fqn(map_obj)
        if fqn not in file_maps:
            file_maps[fqn] = []
        file_maps[fqn].append(map_obj)
        if fqn not in _type_source_registry:
            _type_source_registry[fqn] = set()
        _type_source_registry[fqn].add(str(ifex_file))

    file_typerefs: dict[str, list[vafmodel.TypeRef]] = {}
    for typeref_obj in local_typerefs.values():
        fqn = _get_type_fqn(typeref_obj)
        if fqn not in file_typerefs:
            file_typerefs[fqn] = []
        file_typerefs[fqn].append(typeref_obj)
        if fqn not in _type_source_registry:
            _type_source_registry[fqn] = set()
        _type_source_registry[fqn].add(str(ifex_file))

    file_variants: dict[str, list[vafmodel.Variant]] = {}
    for variant_obj in local_variants.values():
        fqn = _get_type_fqn(variant_obj)
        if fqn not in file_variants:
            file_variants[fqn] = []
        file_variants[fqn].append(variant_obj)
        if fqn not in _type_source_registry:
            _type_source_registry[fqn] = set()
        _type_source_registry[fqn].add(str(ifex_file))

    # Collect strings created (not grouped by FQN - just a list)
    file_strings: list[vafmodel.String] = []
    for string_obj in local_strings.values():
        file_strings.append(string_obj)
        fqn = _get_type_fqn(string_obj)
        if fqn not in _type_source_registry:
            _type_source_registry[fqn] = set()
        _type_source_registry[fqn].add(str(ifex_file))

    print(
        f"  Created {sum(len(v) for v in file_vectors.values())} vectors, "
        f"{sum(len(v) for v in file_maps.values())} maps, "
        f"{sum(len(v) for v in file_typerefs.values())} typerefs, "
        f"{sum(len(v) for v in file_variants.values())} variants, "
        f"{len(file_strings)} strings"
    )

    return (
        file_structs,
        file_enums,
        file_interfaces,
        file_vectors,
        file_maps,
        file_typerefs,
        file_variants,
        file_strings,
    )


def ifex_batch_to_json(  # pylint: disable= too-many-branches
    ifex_files: list[Path],
    output_file: Path,
    enable_layering: bool = True,
) -> None:
    # pylint: disable=too-many-locals,too-many-statements
    """Convert multiple IFEX files to a single merged VAF JSON model

    Args:
        ifex_files: List of paths to IFEX input files
        output_file: Path to the output JSON file
        enable_layering: If True, recursively load and merge included IFEX files (default: True)
    """
    # Clear the global type source registry before processing
    global _type_source_registry  # pylint: disable=global-statement
    _type_source_registry = {}

    # Process each file independently and collect all types grouped by FQN
    all_structs: dict[str, list[vafmodel.Struct]] = {}
    all_enums: dict[str, list[vafmodel.VafEnum]] = {}
    all_module_interfaces: dict[str, list[vafmodel.ModuleInterface]] = {}
    all_vectors: dict[str, list[vafmodel.Vector]] = {}
    all_maps: dict[str, list[vafmodel.Map]] = {}
    all_typerefs: dict[str, list[vafmodel.TypeRef]] = {}
    all_variants: dict[str, list[vafmodel.Variant]] = {}
    all_strings: list[vafmodel.String] = []

    # Helper function to merge dict[str, list] - extends lists for matching keys
    def merge_dict(target: dict[str, list[Any]], source: dict[str, list[Any]]) -> None:
        for key, value_list in source.items():
            target.setdefault(key, []).extend(value_list)

    # Load and process each IFEX file independently
    for ifex_file in ifex_files:
        (
            file_structs,
            file_enums,
            file_interfaces,
            file_vectors,
            file_maps,
            file_typerefs,
            file_variants,
            file_strings,
        ) = _process_single_file(ifex_file, enable_layering)
        # Merge dictionaries from this file into global dictionaries
        merge_dict(all_structs, file_structs)
        merge_dict(all_enums, file_enums)
        merge_dict(all_module_interfaces, file_interfaces)
        merge_dict(all_vectors, file_vectors)
        merge_dict(all_maps, file_maps)
        merge_dict(all_typerefs, file_typerefs)
        merge_dict(all_variants, file_variants)
        all_strings.extend(file_strings)

    print(
        f"\nTotal extracted: {sum(len(v) for v in all_structs.values())} structs, "
        f"{sum(len(v) for v in all_enums.values())} enums, "
        f"{sum(len(v) for v in all_module_interfaces.values())} interfaces"
    )
    print(
        f"Total created: {sum(len(v) for v in all_vectors.values())} vectors, "
        f"{sum(len(v) for v in all_maps.values())} maps, "
        f"{sum(len(v) for v in all_typerefs.values())} typerefs, "
        f"{sum(len(v) for v in all_variants.values())} variants, "
        f"{len(all_strings)} strings"
    )

    # Check for type name conflicts BEFORE deduplication
    # This catches true conflicts (same name but different definitions)
    _check_type_conflicts(
        all_structs, all_enums, all_module_interfaces, all_vectors, all_maps, all_typerefs, all_variants
    )

    # Deduplicate types - keep last instance per FQN
    # (handles both layering within files and identical definitions across files)
    all_structs_clean = _deduplicate_types(all_structs)
    all_enums_clean = _deduplicate_types(all_enums)
    all_module_interfaces_clean = _deduplicate_types(all_module_interfaces)
    all_vectors_clean = _deduplicate_types(all_vectors)
    all_maps_clean = _deduplicate_types(all_maps)
    all_typerefs_clean = _deduplicate_types(all_typerefs)
    all_variants_clean = _deduplicate_types(all_variants)

    # Deduplicate strings (there's only ever one: vaf::String)
    strings = [all_strings[0]] if all_strings else []

    print(
        f"After deduplication: {len(all_structs_clean)} unique structs, {len(all_enums_clean)} unique enums, "
        f"{len(all_module_interfaces_clean)} unique interfaces, {len(all_vectors_clean)} unique vectors, "
        f"{len(all_maps_clean)} unique maps, {len(all_typerefs_clean)} unique typerefs, "
        f"{len(all_variants_clean)} unique variants"
    )

    # Vectors, Maps, TypeRefs, and Variants are already vafmodel objects from the type creation functions
    # No need to create them again - just use them directly

    # Create final VAF model instance with all data type definitions
    data_type_definitions = vafmodel.DataTypeDefinition(
        Structs=all_structs_clean,
        Enums=all_enums_clean,
        Strings=strings,
        Vectors=all_vectors_clean,
        Maps=all_maps_clean,
        TypeRefs=all_typerefs_clean,
        Variants=all_variants_clean,
    )

    # Create MainModel with the data type definitions and module interfaces
    main_model = vafmodel.MainModel(
        DataTypeDefinitions=data_type_definitions,
        ModuleInterfaces=all_module_interfaces_clean,
    )

    # Write VAF model to JSON file
    print(f"\nWriting merged VAF model to {output_file}")

    # Create parent directories if they don't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Serialize the model to JSON
    json_content = main_model.model_dump_json(indent=2, exclude_none=True, exclude_defaults=True)

    # Write to file
    with output_file.open("w") as f:
        f.write(json_content)

    print(f"Successfully written merged VAF model from {len(ifex_files)} file(s) to {output_file}")
