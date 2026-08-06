from pydantic import BaseModel, Field


class Parameter(BaseModel):
    """
    Class that holds the relevant information relating to a function parameter.
    Inherits from BaseModel for easy pydantic type checking
    """
    p_name: str = Field(min_length=1)
    p_type: str = Field(min_length=1)

    def __str__(self) -> str:
        """
        Converts the object into a string.
        Used to feed to the LLM
        """
        return (
            f"\"{self.p_name}\":" "{"
            f"\"type\":\"{self.p_type}\"" "}"
        )


class FunctDef(BaseModel):
    """
    Class that holds the relevant information relating to a single function.
    Inherits from BaseModel for easy pydantic type checking
    """
    name: str = Field(min_length=1)
    description: str = Field(default="")
    parameters: list[Parameter] = Field()
    returns: str = Field(min_length=1)

    def __str__(self) -> str:
        """
        Converts the object into a string.
        Used to feed to the LLM
        """
        return (
            f"\"name\":\"{self.name}\","
            f"\"description\":\"{self.description}\","
            "\"parameters\":"
            f"{','.join(map(str, self.parameters))}"
            f",\"return type\":\"{self.returns}\"\n"
        )


class DefFunctException(ValueError):
    """
    Custom Exception that holds the length of the error.
    Retry Specific to a few situations in the code.
    """

    e_len: int

    def __init__(self, e_len: int, *args: object) -> None:
        super().__init__(*args)
        self.e_len = e_len
