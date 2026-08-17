from argparse import ArgumentParser
from typing import cast


def val_args(args: list[str]) -> dict[str, str]:
    """
    Function to Parse all received arguments into
    a dictionary format. specific for the Project.
    """

    parser = ArgumentParser()

    parser.add_argument("--functions_definition",
                        default="data/input/functions_definition.json")
    parser.add_argument("--input",
                        default="data/input/function_calling_tests.json")
    parser.add_argument("--output",
                        default="data/output/function_calls.json")

    arg_inputs = cast(dict[str, str], parser.parse_args().__dict__)

    return arg_inputs


def ft_repr(s: str) -> str:
    """
    Function that converts any string into a representation
    of that string. Specific to turn strings JSON safe.
    """
    out: str = ""
    for char in s:
        if char in ["\"", "\\"]:
            out += "\\" + char
        elif char == "\n":
            out += "\\n"
        elif char == "\t":
            out += "\\t"
        elif char == "\0":
            out += "\\0"
        elif char == "\v":
            out += "\\v"
        else:
            out += char
    return out
