

import sys
from typing import Any
import json
import os
# import numpy as np
from src import (val_args, get_prompts, get_funct_defs, create_output_file,
                 #  FunctDef
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

    print('\a')
    print("setup complete")

    from llm_sdk import Small_LLM_Model

    print('\a')
    print("Small_LLM_Model Class Loaded")
    print()
    print()

    try:
        llm_files: dict[str, str] = {}
        os.environ["HF_TOKEN"] = ""  # "hf_xxxxxxxxxxxxxxxxx"
        llm = Small_LLM_Model(device="cpu")

        llm_files["vocab"] = llm.get_path_to_vocab_file()
        llm_files["merges"] = llm.get_path_to_merges_file()
        llm_files["tokenizer"] = llm.get_path_to_tokenizer_file()

        # from torch import Tensor
        # llm_files["vocab"] = (
        #     "/home/tribeirinho/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/"
        #     "snapshots/c1899de289a04d12100db370d81485cdf75e47ca/vocab.json")
        # llm_files["merges"] = (
        #     "/home/tribeirinho/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/"
        #     "snapshots/c1899de289a04d12100db370d81485cdf75e47ca/merges.txt")
        # llm_files["tokenizer"] = (
        #     "/home/tribeirinho/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/"
        #     "snapshots/c1899de289a04d12100db370d81485cdf75e47ca/tokenizer.json")

        print()
        print("\n".join([f"{k}: {v}" for k, v in llm_files.items()]))

    except Exception as e:
        print("an unexpected error has occurred:\n", e)
        return

    with open(llm_files["vocab"]) as vocab_file:
        vocab_text_int: dict[str, int] = json.load(vocab_file)

    json_text_float: dict[str, int] = {}

    for json_char in ["{", "}", "    ", "\n", "[", "]", ",", ":"]:
        json_text_float[json_char] = vocab_text_int[json_char]

    # i = 0
    # for k, v in vocab_text_int.items():
    #     print(k, v, end="  ")
    #     if i > 10:
    #         break
    #     i += 1

    vocab_int_text: dict[int, str] = {}

    for k, v in vocab_text_int.items():
        vocab_int_text[v] = k

    print()
    print('\a')
    print("LLM Class generated")

    tokenized_int_funct_list: list[list[int]] = []

    try:

        for funct in funct_defs:
            print('\a')
            print(funct)
            input()
            print()

            tokenized_tensor_funct = llm.encode(str(funct))
            # tokenized_tensor_funct = Tensor(
            #     [[675, 25, 5168, 2891, 32964, 198, 5009, 25, 2691, 1378,
            #       5109, 3786, 323, 470, 862, 2629, 624, 4870, 25, 264, 259,
            #       25, 1372, 198, 2233, 259, 25, 1372, 198, 5598, 25, 1372]],
            #     device="cpu")

            print("Prompt Tokenized int:")
            print()
            print(tokenized_tensor_funct[0])

            tokenized_int_funct_list.append(tokenized_tensor_funct[0].tolist())

            print()
            print("Prompt Tokenized str:")
            print(list(map(lambda x: vocab_int_text.get(x, ""),
                           tokenized_int_funct_list[-1])))
            print()
            print()

            # str_back = llm.decode(tokenized_funct)

            # print("Prompt re-coded:")
            # print(str_back)

    except Exception as e:
        error_len = len(tokenized_int_funct_list)
        print("An error has occurred in the Processing of Callable Function"
              f" number {error_len}: {funct_defs[error_len]}:\n\n{e}")
        return

    out_list: list[dict[str, str | dict[str, Any]]] = []

    try:

        for prompt in inputs:
            print('\a')
            print(prompt)
            input()

            tokenized_prompt = llm.encode(prompt)
            # tokenized_prompt = Tensor(
            #     [[3838, 374, 279, 2629, 315, 220, 17, 323, 220, 18, 30]],
            #     device="cpu")

            print("Prompt Tokenized int:")
            print()
            print(tokenized_prompt[0])

            tokenized_int_prompt: list[int] = tokenized_prompt[0].tolist()

            print()
            print("Prompt Tokenized str:")
            print(list(map(lambda x: vocab_int_text.get(x, ""),
                           tokenized_int_prompt)))
            print()
            print()

            # str_back = llm.decode(tokenized)

            # print("Prompt re-coded:")
            # print(str_back)

            added_token = tokenized_int_prompt.copy()
            prompt_len = len(tokenized_int_prompt)

            while added_token[-1] is not vocab_text_int["\0"]:

                logits_funct = llm.get_logits_from_input_ids(added_token)

                added_token.append(
                    vocab_text_int[vocab_int_text[logits_funct.index(
                        max(logits_funct))]])

            funct_name = llm.decode(added_token[prompt_len:])

            funct_parameters: dict[str, Any] = {}

            out_list.append({
                "prompt": prompt,
                "name": funct_name,
                "parameters": funct_parameters
            })

            print(out_list[-1])

    except Exception as e:
        print(f"An error has occurred in the Processing of Prompts:\n\n{e}")

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
