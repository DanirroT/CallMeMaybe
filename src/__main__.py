

import sys

# from ..llm_sdk.llm_sdk import Small_LLM_Model

from llm_sdk.llm_sdk import Small_LLM_Model

from src import (val_args, get_prompts, get_funct_defs,
                 FunctDef
                 )
# from llm_sdk.llm_sdk import Small_LLM_Model
# from pydantic import ValidationError
# from src.input import read_map_file
# from src.drone_class import DroneManager
# from src.visualizer import WindowedVisualizer
# # from visualizer import terminal_clear
# from src.validation_error_handling import error_processing
# from typing import Any


def main(args: list[str]) -> None:

    try:
        arg_inputs = val_args(args)
    except ValueError as e:
        print(f"Arguments passed incorrectly: {e}")
        return

    print(arg_inputs)

    try:
        inputs = get_prompts(arg_inputs["input"])
    except FileNotFoundError as e:
        print(e)
        return

    print ()
    print (inputs)
    print ()

    try:
        funct_defs = get_funct_defs(arg_inputs["functions_definition"])
    except FileNotFoundError as e:
        print(e)
        return

    print ()
    print ("\n".join(map(str, funct_defs)))
    print ()

    llm = Small_LLM_Model()

    for prompt in inputs:
        print()
        print(prompt)
        print()

        tokenized = llm.encode(prompt)

        print(tokenized)

        print(llm.decode(tokenized))


    # file_name = args[1]
    # try:
    #     drone_map = read_map_file(file_name)
    # except FileNotFoundError as e:
    #     print(e)
    #     return
    # except ValidationError as e:
    #     error_processing(e.errors())
    #     return
    # except ValueError as e:
    #     print(f"Error reading map file: {e}")
    #     return
    # except Exception as e:
    #     print(f"Unexpected error occurred: {e}")
    #     return

    # print()
    # print("Drones", drone_map.nb_drones)
    # print("Zones", len(drone_map.zones))
    # print("Connections", len(drone_map.connections))

    # print()

    # print(drone_map.get_nice_summary())

    # print()

    # print("Name:", file_name, end="\t")

    # drone_map.print_map()

    # manager = DroneManager(drone_map, WindowedVisualizer)

    # try:
    #     manager.run_program()
    # except ValueError as e:
    #     print(f"Error: {e}")
    # print("END SIM")


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print("\rThe program has been forcefully stopped")
