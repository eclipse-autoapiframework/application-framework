"""Module containing the VSS data types"""

from abc import ABC, abstractmethod
from types import NotImplementedType

from vaf import vafmodel

type_translation: dict[str, vafmodel.DataType] = {
    "int8": vafmodel.DataType(Name=vafmodel.BaseType.INT8_T, Namespace=""),
    "int16": vafmodel.DataType(Name=vafmodel.BaseType.INT16_T, Namespace=""),
    "int32": vafmodel.DataType(Name=vafmodel.BaseType.INT32_T, Namespace=""),
    "int64": vafmodel.DataType(Name=vafmodel.BaseType.INT64_T, Namespace=""),
    "uint8": vafmodel.DataType(Name=vafmodel.BaseType.UINT8_T, Namespace=""),
    "uint16": vafmodel.DataType(Name=vafmodel.BaseType.UINT16_T, Namespace=""),
    "uint32": vafmodel.DataType(Name=vafmodel.BaseType.UINT32_T, Namespace=""),
    "uint64": vafmodel.DataType(Name=vafmodel.BaseType.UINT64_T, Namespace=""),
    "boolean": vafmodel.DataType(Name=vafmodel.BaseType.BOOL, Namespace=""),
    "float": vafmodel.DataType(Name=vafmodel.BaseType.FLOAT, Namespace=""),
    "double": vafmodel.DataType(Name=vafmodel.BaseType.DOUBLE, Namespace=""),
    "string": vafmodel.DataType(Name="string", Namespace="vaf"),
}


def is_numeric(datatype: str) -> bool:
    """Checks wether a VSS datatype is numeric

    Args:
        datatype (str): The string representation of the datatype

    Returns:
        bool: True if the datatype is numeric, false otherwise
    """
    return datatype in [
        "int8",
        "int16",
        "int32",
        "int64",
        "uint8",
        "uint16",
        "uint32",
        "uint64",
        "float",
        "double",
    ]


# pylint: disable=too-few-public-methods
class BaseType(ABC):
    """Base class representing a VSS data type"""

    def __init__(self, name: str, namespace: str, type_name: str = "") -> None:
        self.name: str = name
        self.namespace: str = namespace.lower()
        self.type: str = type_name

    @abstractmethod
    def export(self) -> vafmodel.VafBaseModel:
        """Exports VSS type to VAF model type

        Raises:
            ValueError: Raised when a type cannot be exported

        Returns:
            vafmodel.VafBaseModel: Parent class for the VAF model types
        """


class PrimitiveType(BaseType):
    """Primitive types used in the VSS catalog"""

    def __init__(
        self, name: str, type_name: str, min_value: float | None = None, max_value: float | None = None
    ) -> None:
        super().__init__(name, "", type_name)
        self.min_value = min_value
        self.max_value = max_value

    def export(self) -> vafmodel.VafBaseModel:
        raise ValueError("PrimitiveType cannot be exported.")


class StructType(BaseType):
    """Struct type used in the VSS catalog"""

    def __init__(self, name: str, namespace: str) -> None:
        super().__init__(name, namespace)
        self.subelements: list[BaseType] = []

    def getTypeRefStr(self) -> str:
        """Returns the VAF TypeRef for this StructType"""
        return self.name

    def export(self) -> vafmodel.Struct:
        """Exports VSS struct to VAF model struct

        Raises:
            ValueError: Raised when a struct subelement is malformed in the VSS model

        Returns:
            vafmodel.Struct: struct containing the VSS data
        """
        subelements = []
        for subelement in self.subelements:
            if isinstance(subelement, (StructType, EnumType)):
                subelements.append(
                    vafmodel.SubElement(
                        Name=subelement.name,
                        TypeRef=vafmodel.DataType(Name=subelement.name, Namespace=subelement.namespace),
                    )
                )
            elif isinstance(subelement, (ArrayType, VectorType)):
                subelements.append(
                    vafmodel.SubElement(
                        Name=subelement.name,
                        TypeRef=vafmodel.DataType(Name=subelement.getTypeRefStr(), Namespace="vss"),
                    )
                )
            elif isinstance(subelement, PrimitiveType):
                type_ref = type_translation.get(subelement.type)
                if type_ref is None:
                    raise ValueError(f"Unsupported type '{subelement.type}' for subelement '{subelement.name}'")
                subelement_data = vafmodel.SubElement(
                    Name=subelement.name,
                    TypeRef=type_ref,
                )

                # Include min and max values if defined
                if subelement.min_value is not None:
                    subelement_data.Min = subelement.min_value
                if subelement.max_value is not None:
                    subelement_data.Max = subelement.max_value

                subelements.append(subelement_data)
            else:
                raise ValueError("Subelement has no valid Datatype set.")
        return vafmodel.Struct(Name=self.name, Namespace=self.namespace, SubElements=subelements)


# pylint: enable=too-few-public-methods
class ArrayType(BaseType):
    """Array type used in VSS catalog"""

    def __init__(self, name: str, type_name: str, array_size: int) -> None:
        super().__init__(name, "vss", type_name)
        self.array_size = array_size

    def __hash__(self) -> int:
        return hash((self.type, self.array_size))

    def __eq__(self, other: object) -> bool | NotImplementedType:
        if not isinstance(other, ArrayType):
            return NotImplemented
        return self.type == other.type and self.array_size == other.array_size

    def getTypeRefStr(self) -> str:
        """Returns the VAF TypeRef for this ArrayType"""
        return f"{self.type}ArraySize{self.array_size}"

    def export(self) -> vafmodel.Array:
        """Exports a fixed-size array to a VAF model array"""
        array = vafmodel.Array(
            Name=self.getTypeRefStr(),
            Namespace=self.namespace,
            TypeRef=type_translation[self.type],
            Size=self.array_size,
        )
        return array


class VectorType(BaseType):
    """Vector type used in VSS catalog"""

    def __init__(self, name: str, type_name: str) -> None:
        super().__init__(name, "vss", type_name)

    def __hash__(self) -> int:
        return hash(self.type)

    def __eq__(self, other: object) -> bool | NotImplementedType:
        if not isinstance(other, VectorType):
            return NotImplemented
        return self.type == other.type

    def getTypeRefStr(self) -> str:
        """Returns the VAF TypeRef for this VectorType"""
        return f"{self.type}Vector"

    def export(self) -> vafmodel.Vector:
        """Exports a dynamic vector to a VAF model vector"""
        vec = vafmodel.Vector(Name=self.getTypeRefStr(), Namespace=self.namespace, TypeRef=type_translation[self.type])
        return vec


class EnumType(BaseType):
    """Enum type used in VSS catalog"""

    def __init__(self, name: str, namespace: str) -> None:
        super().__init__(name, namespace)
        self.literals: list[dict[str, int]] = []

    def add_literal(self, label: str, value: int) -> None:
        """
        Adds a literal to the enum.

        Args:
            label (str): The label or name of the literal.
            value (int): The numeric value associated with the literal.
        """
        self.literals.append({"label": label, "value": value})  # type: ignore

    def export(self) -> vafmodel.VafEnum:
        """
        Exports the EnumType to a VAF model EnumType.

        Raises:
            ValueError: If the EnumType has no literals defined, a ValueError is raised.
        """

        if not self.literals:
            print(f"[ERROR] EnumType '{self.name}' has no literals defined.")
            raise ValueError(f"EnumType '{self.name}' cannot be exported without literals.")

        vaf_enum = vafmodel.VafEnum(
            Name=self.name,
            Namespace=self.namespace,
            BaseType=vafmodel.DataType(Name="uint8_t", Namespace=""),
            Literals=[
                vafmodel.EnumLiteral(Label=lit["label"], Value=lit["value"])  # type: ignore
                for lit in self.literals
            ],
        )

        return vaf_enum
