from pydantic import (BaseModel, Field, field_validator)
from enum import Enum
from typing import Any


class Parameter(BaseModel):
    name: str = Field(min_length=1)
    type: str = Field(min_length=1)

    def __str__(self):
        return (
            f"{self.name} t: {self.type}"
        )


# class Returns(BaseModel):
#     # pass
#     type: str = Field(min_length=1)


class FunctDef(BaseModel):
    name: str = Field(min_length=1)
    description: str = Field(default=None)
    parameters: list[Parameter] = Field()
    returns: str = Field(min_length=1)

    def __str__(self):
        return (
            f"Name: {self.name}\n"
            f"\t{self.description}\n"
            f"params: {"\n\t".join(map(str, self.parameters))}\n"
            f"return: {self.returns}"
        )
