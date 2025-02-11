# Copyright 2024 Superlinked, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

from dataclasses import dataclass

from beartype.typing import Any, Generic, Sequence, TypeVar, cast
from typing_extensions import override

from superlinked.framework.common.data_types import PythonTypes
from superlinked.framework.common.interface.comparison_operand import ComparisonOperand
from superlinked.framework.common.schema.blob_information import BlobInformation

# Exclude from documentation.
# A better approach would be to separate this file into atomic objects,
# which is blocked due to circular dependency issues.
__pdoc__ = {}
__pdoc__["SchemaFieldDescriptor"] = False


# SchemaFieldType
SFT = TypeVar("SFT", bound=PythonTypes)
SchemaObjectT = TypeVar("SchemaObjectT", bound="SchemaObject")


class SchemaObject:
    """
    `@schema` decorated class that has multiple `SchemaField`s.

    Use it to represent your structured data to reference during the vector embedding process.
    """

    def __init__(self, base_cls: type) -> None:
        self._base_cls = base_cls

    @property
    def _base_class_name(self) -> str:
        return self._base_cls.__name__

    @property
    def _schema_name(self) -> str:
        return self._base_class_name

    def __str__(self) -> str:
        schema_fields = ", ".join(
            [
                f"(name={field.name}, type={field.type_})"
                for field in self._get_schema_fields()
            ]
        )
        return f"{self.__class__.__name__}(schema_name={self._schema_name}, schema_fields=[{schema_fields}])"

    def _init_field(
        self: SchemaObjectT, field_descriptor: SchemaFieldDescriptor
    ) -> SchemaField:
        value = field_descriptor.type_(field_descriptor.name, self)
        setattr(self, field_descriptor.name, value)
        return value

    def _get_schema_fields(self) -> Sequence[SchemaField]:
        return []


class SchemaField(ComparisonOperand, Generic[SFT]):
    """
    A SchemaField is a generic field of your `@schema` decorated class.

    `SchemaField`s are the basic building block for inputs that will be referenced in an embedding space.
    Sub-types of a `SchemaField` are typed data representations that you can use to transform and load data
    to feed the vector embedding process.
    """

    def __init__(self, name: str, schema_obj: SchemaObjectT, type_: type[SFT]) -> None:
        super().__init__(SchemaField)
        self.name = name
        self.schema_obj = schema_obj
        self.type_ = type_

    def parse(self, value: SFT) -> SFT:
        return value

    def __hash__(self) -> int:
        return hash((self.name, self.schema_obj))

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(name={self.name}, type={self.type_}, schema_object_name={self.schema_obj._schema_name})"
        )

    @staticmethod
    def _built_in_equal(
        left_operand: ComparisonOperand[SchemaField], right_operand: object
    ) -> bool:
        if isinstance(left_operand, SchemaField) and isinstance(
            right_operand, SchemaField
        ):
            return (
                right_operand.name == left_operand.name
                and right_operand.schema_obj == left_operand.schema_obj
            )
        return False

    @staticmethod
    def _built_in_not_equal(
        left_operand: ComparisonOperand[SchemaField], right_operand: object
    ) -> bool:
        return not SchemaField._built_in_equal(left_operand, right_operand)


class String(SchemaField[str]):
    """
    Field of a schema that represents a string value.

    e.g.: `TextEmbeddingSpace` expects a String field as an input.
    """

    def __init__(self, name: str, schema_obj: SchemaObjectT) -> None:
        super().__init__(name, schema_obj, str)

    def __add__(self, other: Blob) -> DescribedBlob:
        if not isinstance(other, String):
            raise TypeError("Operand must be of type Blob")
        return DescribedBlob(blob=other, description=self)


class Timestamp(SchemaField[int]):
    """
    Field of a schema that represents a unix timestamp.

    e.g.: `RecencySpace` expects a Timestamp field as an input.
    """

    def __init__(self, name: str, schema_obj: SchemaObjectT) -> None:
        super().__init__(name, schema_obj, int)


class Blob(SchemaField[BlobInformation]):
    """
    Field of a schema that represents a local/remote file path or an utf-8 encoded bytes string.

    e.g.: `ImageSpace` expects a blob field as an input.
    """

    def __init__(self, name: str, schema_obj: SchemaObjectT) -> None:
        super().__init__(name, schema_obj, BlobInformation)

    def __add__(self, other: String) -> DescribedBlob:
        if not isinstance(other, String):
            raise TypeError("Operand must be of type String")
        return DescribedBlob(blob=self, description=other)


NSFT = TypeVar("NSFT", float, int)


class Number(Generic[NSFT], SchemaField[NSFT]):
    """
    Field of a schema that represents a union of Float and Integer.

    e.g.: `NumberSpace` expects a Number field as an input.
    """


class Float(Number[float]):
    """
    Field of a schema that represents a float.
    """

    def __init__(self, name: str, schema_obj: SchemaObjectT) -> None:
        super().__init__(name, schema_obj, float)


class Integer(Number[int]):
    """
    Field of a schema that represents an integer.
    """

    def __init__(self, name: str, schema_obj: SchemaObjectT) -> None:
        super().__init__(name, schema_obj, int)


class FloatList(SchemaField[list[float]]):
    """
    Field of a schema that represents a vector.
    """

    def __init__(self, name: str, schema_obj: SchemaObjectT) -> None:
        super().__init__(name, schema_obj, list[float])

    @override
    def parse(self, value: list[float]) -> list[float]:
        return value if isinstance(value, list) else [cast(float, value)]


class StringList(SchemaField[list[str]]):
    """
    Field of a schema that represents a list of strings.
    """

    def __init__(self, name: str, schema_obj: SchemaObjectT) -> None:
        super().__init__(name, schema_obj, list[str])

    @override
    def parse(self, value: list[str]) -> list[str]:
        return value if isinstance(value, list) else [cast(str, value)]


@dataclass(frozen=True)
class DescribedBlob:
    blob: Blob
    description: String


ConcreteSchemaField = (
    String | Timestamp | Float | Integer | FloatList | StringList | Blob
)
ConcreteSchemaFieldT = TypeVar("ConcreteSchemaFieldT", bound="ConcreteSchemaField")


@dataclass
class SchemaFieldDescriptor:
    name: str
    type_: type
    type_args: tuple[Any, ...]
