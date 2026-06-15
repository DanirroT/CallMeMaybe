from pydantic import BaseModel, Field  # , field_validator
# from enum import Enum
# from typing import Any


class Parameter(BaseModel):
    p_name: str = Field(min_length=1)
    p_type: str = Field(min_length=1)

    def __str__(self):
        return (
            f"{self.p_name} t: {self.p_type}"
        )


# class Returns(BaseModel):
#     # pass
#     p_type: str = Field(min_length=1)


class FunctDef(BaseModel):
    name: str = Field(min_length=1)
    description: str = Field(default="")
    parameters: list[Parameter] = Field()
    returns: str = Field(min_length=1)

    def __str__(self):
        return (
            f"Name: {self.name}\n"
            f"Description: {self.description}\n"
            f"Params: {"\n\t".join(map(str, self.parameters))}\n"
            f"Return: {self.returns}"
        )
