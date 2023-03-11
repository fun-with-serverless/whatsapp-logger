from enum import Enum
from typing import Type, TypeVar
from pynamodb.attributes import Attribute
from pynamodb.constants import STRING

T = TypeVar("T", bound=Enum)


def enum_from_str(my_enum_type: Type[T], value: str) -> T:
    """
    Convert a string to an enum value.

    Args:
        cls (Enum): The enum class.
        value (str): The string to convert to an enum value.

    Returns:
        Enum: The enum value corresponding to the input string.

    Raises:
        ValueError: If the input string is not a valid member of the enum class.
    """
    try:
        return my_enum_type[value.upper()]
    except KeyError:
        raise ValueError(f"{value} is not a valid member of {my_enum_type.__name__}")


class EnumAttribute(Attribute):
    """
    An attribute that represents an enum value.
    """

    attr_type = STRING

    def __init__(self, enum_cls, **kwargs):
        self.enum_cls = enum_cls
        super().__init__(**kwargs)

    def serialize(self, value):
        if not isinstance(value, Enum):
            raise TypeError(f"Expected an Enum value, but got {type(value)}")

        return value.name

    def deserialize(self, value):
        return self.enum_cls[value]
