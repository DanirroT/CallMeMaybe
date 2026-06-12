

import sys
from typing import Any
import json

# import numpy as np

from src import (val_args, get_prompts, get_funct_defs, create_output_file,
                 FunctDef
                 )

# from pydantic import ValidationError
# from typing import Any


def main(args: list[str]) -> None:

    try:
        arg_inputs = val_args(args)
    except ValueError as e:
        print(f"Arguments passed incorrectly: {e}")
        return

    # print(arg_inputs)

    try:
        inputs = get_prompts(arg_inputs["input"])
    except FileNotFoundError as e:
        print(e)
        return

    # print ()
    # print (inputs)
    # print ()

    try:
        funct_defs = get_funct_defs(arg_inputs["functions_definition"])
    except FileNotFoundError as e:
        print(e)
        return

    # print ()
    # print ("\n".join(map(str, funct_defs)))
    # print ()

    try:
        create_output_file(arg_inputs["output"])
    except FileExistsError:
        return

    out_list: list[dict[str, str | dict[str, Any]]] = []

    input("setup complete")

    # from llm_sdk import Small_LLM_Model

    input("Small_LLM_Model Class Loaded")
    print()
    print()

    # try:
    #     os.environ["HF_TOKEN"] = ""  # "hf_xxxxxxxxxxxxxxxxx"
    #     llm = Small_LLM_Model()
    # except Exception as e:
    #     print("an unexpected error has occurred:\n", e)
    #     return

    print()
    print()
    input("LLM Class generated")

    for prompt in inputs:
        print()
        input(prompt)

        # tokenized = llm.encode(prompt)

        # print("Prompt Tokenized:")
        # print(tokenized)

        # rever = llm.decode(tokenized)

        # print("Prompt re-coded:")
        # print(rever)

        name = prompt[:5]

        parameters = {prompt[6]: 1, prompt[7]: 2}

        out_list.append({
            "prompt": prompt,
            "name": name,
            "parameters": parameters
        })

        print(out_list[-1])

    out_str = json.dumps(out_list, indent=4)

    try:
        with open(arg_inputs["output"], "w") as output_file:
            # inputs = input_file.read()
            output_file.write(out_str)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Output File \"{arg_inputs['output']}\" "
                                f"not found {e}")


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print("\rThe program has been forcefully stopped")
