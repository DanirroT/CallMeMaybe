# import sys
from src import FunctDef, Parameter
# from src.data_classes import Coordinates, ZoneDataRaw, ConnData
# from src.map_classes import DroneMap
from typing import Any
import json
# import numpy as np
import pydantic
# import  Qwen/Qwen3-0.6B


def val_args(args: list[str]) -> dict[str, str]:

    argc = len(args)
    if argc > 6:
        raise ValueError("Too many Arguments! Try Again")
    if argc > 6:
        raise ValueError("Too many Arguments! Try Again")

    arg_inputs: dict[str, str] = {
        "functions_definition": "data/input/functions_definition.json",
        "input": "data/input/function_calling_tests.json",
        "output": "data/output/function_calls.json"
    }
    fail: bool = False
    next_ins: None | str = None

    for arg in args:

        if next_ins:
            arg_inputs[next_ins] = arg
            next_ins = None
            continue

        if arg == "--functions_definition":
            next_ins = "functions_definition"
        elif arg == "--input":
            next_ins = "input"
        elif arg == "--output":
            next_ins = "output"

        elif arg.startswith("--"):
            print(f"Error: Unknown Parameter: {arg}")
            fail = True
        else:
            print("Error: Unknown Argument")
            fail = True

    for arg, file in arg_inputs.items():
        if not file.endswith(".json"):
            print(f"{arg} must be a json file. {file}")
            fail = True

    if fail:
        raise ValueError("\nProgram Stopped")

    return arg_inputs


def get_prompts(file_name: str) -> list[str]:
    try:
        with open(file_name) as input_file:
            # inputs = input_file.read()
            parsed_inputs = json.load(input_file)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Input File \"{file_name}\" not found {e}")

    # print(parsed_inputs)

    return [obj["prompt"] for obj in parsed_inputs]


def get_funct_defs(file_name: str) -> list[FunctDef]:
    try:
        with open(file_name) as funct_def_file:
            # funct_defs = funct_def_file.read()
            parsed_funct_defs: list[dict[str, Any]] = json.load(funct_def_file)
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Functions Definition File \"{file_name}\" not found {e}")

    print(parsed_funct_defs)

    out_list: list[FunctDef] = []

    for funct in parsed_funct_defs:
        print()
        print(funct)
        print()
        print(funct["parameters"])

        params: list[Parameter] = []
        if len(funct["parameters"]):
            for name, type_dict in funct["parameters"].items():
                params.append(Parameter(name=name, type=type_dict["type"]))

        out_list.append(FunctDef(
            name=funct["name"],
            description=funct["description"],
            parameters=params,
            returns=funct["returns"]["type"]
        ))

    return out_list

# def str_to_dict_parse(in_str: str, entry_sep: str = ",", kv_sep: str = ":",
#                       expected_size: int | None = None) -> dict[str, str]:
#     out_dict: dict[str, str] = {}

#     in_list = in_str.split(entry_sep)

#     for entry in in_list:
#         entry_split = entry.split(kv_sep)
#         if len(entry_split) != 2:
#             raise ValueError(f"Error while Parsing a Str to Dict\n{entry}"
#                              f" does not have a format <key>{kv_sep}<value>")
#         k, v = entry_split

#         if out_dict.get(k):
#             raise ValueError("Error while Parsing a Str to Dict\nRepeated "
#                              f"Keys: {k} goth {out_dict.get(k)} and {v}")
#         out_dict[k] = v
#     if expected_size and expected_size != len(out_dict):
#         raise ValueError(f"Error: expected a size of {expected_size} "
#                          f"but got {len(out_dict)}\n{out_dict}")


#     return out_dict


# def read_map_file(file_name: str) -> DroneMap | Any:

#     with open(file_name) as file:
#         file_str = file.read()

#     file_lines = file_str.splitlines()

#     nb_drones: int = 0
#     zones: list[ZoneDataRaw] = []
#     connections: list[ConnData] = []

#     file_size: int = len(file_lines)

#     i: int = 0
#     while file_lines[i].startswith("#") or not file_lines[i].strip():
#         i += 1
#         if i >= file_size:
#             raise ValueError(
#                 "File is empty or only contains comments/empty lines")

#     if not file_lines[i].startswith("nb_drones:"):
#         raise ValueError("First line must define 'nb_drones'")

#     for line in file_lines:
#         line = line.split("#")[0].strip()
#         metadata: list[str] = []
#         if not line:
#             continue
#         elif line.startswith("nb_drones:"):
#             if not nb_drones:
#                 nb_drones = int(line.split(":")[1].strip())
#             else:
#                 raise ValueError("Multiple definitions of 'nb_drones'")

#         elif line.startswith(("start_hub:", "hub:", "end_hub:")):
#             hub_type: str = ""
#             rest: str = ""
#             name: str = ""
#             x: str = ""
#             y: str = ""

#             try:
#                 hub_type, rest = line.split(":", 1)
#                 name, x, y, *metadata = rest.split()
#                 if metadata:
#                     if metadata[0][:1] != "[":
#                         raise ValueError(
#                             "Metadata must be in between Square Brackets\nor\n"
#                             f"Detected Junk Data at the end of line\n{line}")
#                     if metadata[-1][-1:] != "]":
#                         raise ValueError(
#                             "Metadata must be in between Square Brackets\nor\n"
#                             f"Detected Junk Data at the end of line\n{line}")
#                     # metadata[0] = metadata[0][:-1]
#                     # metadata[-1] = metadata[-1][1:]
#                     raw_meta = " ".join(metadata).strip("[]")
#                     meta_dict = str_to_dict_parse(raw_meta, " ", "=")
#                 else:
#                     meta_dict = {}
#                 zones.append(ZoneDataRaw(
#                     name=name,
#                     hub_type=hub_type,
#                     loc=Coordinates(int(x), int(y)),
#                     zone=meta_dict.get("zone", "normal"),
#                     color=meta_dict.get("color", "none"),
#                     max_drones=int(meta_dict.get("max_drones", 1))
#                 ))
#             except ValueError as e:
#                 raise ValueError(
#                     f"Line not according to Zone Format\n{line}\n"
#                     "Zone Formatting must be\n"
#                     f"<hub_type>: <name> <x> <y> [metadata]\n{e}")

#         elif line.startswith("connection:"):
#             a: str = ""
#             b: str = ""

#             try:
#                 _, conn = line.split(":")
#                 a, pre_b = conn.strip().split("-")
#                 b, *metadata = pre_b.split()
#                 if metadata:
#                     if metadata[0][:1] != "[":
#                         raise ValueError(
#                             "Metadata must be in between Square Brackets\nor\n"
#                             f"Detected Junk Data at the end of line\n{line}")
#                     if metadata[-1][-1:] != "]":
#                         raise ValueError(
#                             "Metadata must be in between Square Brackets\nor\n"
#                             f"Detected Junk Data at the end of line\n{line}")
#                     # metadata[0] = metadata[0][:-1]
#                     # metadata[-1] = metadata[-1][1:]
#                     raw_meta = " ".join(metadata).strip("[]")
#                     meta_dict = str_to_dict_parse(raw_meta, " ", "=")
#                 else:
#                     meta_dict = {}

#                 connections.append(ConnData(
#                     start=a, end=b,
#                     max_link_capacity=int(
#                         meta_dict.get("max_link_capacity", 1)
#                     )))
#             except ValueError as e:
#                 raise ValueError(
#                     f"Line not according to Connection Format\n{line}\n"
#                     "Connection Formatting must be\n"
#                     f"connection: <name1>-<name2> [metadata]\n{e}")

#         else:
#             raise ValueError(
#                 f"Line not according to Any Format\n{line}\n"
#             )
#     return DroneMap(nb_drones, zones, connections)
#     # return nb_drones, zones, connections


# if __name__ == "__main__":

#     args = sys.argv

#     # file_name = "maps/easy/01_linear_path.txt"
#     if len(args) == 1:
#         print("No Map Given. Try Again")
#         sys.exit()

#     if len(args) != 2:
#         print("Too many Arguments! Try Again")
#         sys.exit()
#     file_name = args[1]
#     drone_map = read_map_file(file_name)

#     print()
#     print("Drones", drone_map.nb_drones)
#     print("Zones", len(drone_map.zones))
#     print("Connections", len(drone_map.connections))

#     print()

#     # print(drone_map.get_summary())

#     print(drone_map.get_nice_summary())
