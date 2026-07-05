import sys
import os
from dotenv import load_dotenv
# import random
import httpcore
from typing import Any, cast
import json
# from json import JSONDecodeError
from torch import Tensor
from src import (val_args, ft_repr,
                 DefFunctException, FunctDef, Parameter
                 )
from llm_sdk import Small_LLM_Model

# import numpy as np
# from typing import Any


class FunctCallLLM():

    raw_prompts: list[str]
    funct_defs: list[FunctDef]
    output_path: str

    _llm: Small_LLM_Model | None
    llm_files: dict[str, str]

    vocab_text_int: dict[str, int]
    vocab_int_text: dict[int, str]

    # json_text_int: dict[str, int]
    # json_int_text: dict[int, str]

    tokenized_int_funct_list: list[list[int]]
    instructions: list[int]
    universal_start: list[int]
    universal_post_prompt: list[int]

    # to_export: (Any | str |
    #             list[str] |
    #             list[dict[str, str | dict[str, Any]]] |
    #             dict[str, str | dict[str, Any]])
    to_export: (str |
                dict[str, str | dict[str, Any]] |
                list[str | dict[str, str | dict[str, Any]]])

    def __init__(self, arg_inputs: dict[str, str] | None,
                 setting: bool = True) -> None:

        if arg_inputs:
            try:
                self._get_prompts(arg_inputs["input"])
            except FileNotFoundError:
                raise

            # print ()
            # print (self.raw_prompts)
            # print ()

            try:
                self._get_funct_defs(arg_inputs["functions_definition"])
            except FileNotFoundError:
                raise

            # print ()
            # print ("\n".join(map(str, funct_defs)))
            # print ()

            try:
                self._create_output_file(arg_inputs["output"], setting)
            except FileExistsError:
                raise

            print('\a', end="")
            print("setup complete")

        try:
            self._load_llm(setting)
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                f"Module Dependencies were not met:\n{e}")
        except httpcore.ConnectError as e:
            raise httpcore.ConnectError(
                "Small_LLM_Model was unable to Connect. "
                f"Check Connection and Try again another time\n{e}")

        except Exception as e:
            raise Exception("An unexpected error has occurred during "
                            f"LLM Class Creation:\n{e}")

        print()
        print('\a', end="")
        print("LLM Class generated")

        # tab_int: int = self._llm.encode("    ")[0].tolist()
        # print(tab_int)
        # tab_str = self.vocab_int_text[tab_int[0]]
        # print(f"tab_str='{tab_str}'")
        # tab_str = 'ĠĠĠĠ'

        # ttab_int: int = self._llm.encode("\t")[0].tolist()
        # print(ttab_int)
        # ttab_str = self.vocab_int_text[ttab_int[0]]
        # print(f"tab_str='{ttab_str}'")
        # ttab_str = 'ĉ'

        # enter_int: int = self._llm.encode("\n")[0].tolist()
        # print(enter_int)
        # enter_str = self.vocab_int_text[enter_int[0]]
        # print(f"enter_str='{enter_str}'")
        # enter_str = 'Ċ'

        # self.json_text_int = {}
        # self.json_int_text = {}

        # print("json chars")

        # for token in self.vocab_text_int.keys():
        #     if any(char in token for char in ["{", "}", "[", "]",
        #                                       "\"", 'ĠĠĠĠ', 'Ċ',
        #                                       ",", ":"]):
        #         print(token)

        # for json_char in ["{", "}", "}Ċ", "[", "]", "]Ċ",
        #                   "\"", "\"Ċ", 'ĠĠĠĠ', 'ĠĠĠĠĠĠĠĠ', 'Ċ', ",", ":"]:
        #     self.json_text_int[json_char] = self.vocab_text_int[json_char]
        #     self.json_int_text[self.vocab_text_int[json_char]] = json_char

        # print()
        # input()

        try:

            self._make_deffunct_ids()

        except DefFunctException as e:
            error_len = e.e_len
            del e.e_len
            raise Exception("An error has occurred in the Processing of "
                            f"Callable Function number {error_len}: "
                            f"{self.funct_defs[error_len]}:\n\n{e}")

    def redefine_inputs(self, arg_inputs: dict[str, str],
                        setting: bool = True) -> None:

        try:
            self._get_prompts(arg_inputs["input"])
        except FileNotFoundError:
            raise

        # print ()
        # print (self.raw_prompts)
        # print ()

        try:
            self._get_funct_defs(arg_inputs["functions_definition"])
        except FileNotFoundError:
            raise

        # print ()
        # print ("\n".join(map(str, funct_defs)))
        # print ()

        try:
            self._create_output_file(arg_inputs["output"], setting)
        except FileExistsError:
            raise

        print('\a', end="")
        print("setup complete")

        try:

            self._make_deffunct_ids()

        except DefFunctException as e:
            error_len = e.e_len
            del e.e_len
            raise Exception("An error has occurred in the Processing of "
                            f"Callable Function number {error_len}: "
                            f"{self.funct_defs[error_len]}:\n\n{e}")

    def _get_prompts(self, file_name: str) -> None:
        try:
            with open(file_name) as input_file:
                # inputs = input_file.read()
                parsed_inputs = json.load(input_file)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Input File \"{file_name}\""
                                    f" not found {e}")

        # print(parsed_inputs)

        self.raw_prompts = [ft_repr(obj["prompt"]) for obj in parsed_inputs]

        # print("inputs")
        # print(self.raw_prompts)

    def _get_funct_defs(self, file_name: str) -> None:
        try:
            with open(file_name) as funct_def_file:
                # funct_defs = funct_def_file.read()
                parsed_funct_defs: list[dict[str, Any]] = (
                    json.load(funct_def_file))
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Functions Definition File \"{file_name}\" not found {e}")

        # print(parsed_funct_defs)

        self.funct_defs = []

        for funct in parsed_funct_defs:
            # print()
            # print(funct)
            # print()
            # print(funct["parameters"])

            params: list[Parameter] = []
            if len(funct["parameters"]):
                for name, type_dict in funct["parameters"].items():
                    params.append(Parameter(p_name=name,
                                            p_type=type_dict["type"]))

            self.funct_defs.append(FunctDef(
                name=funct["name"],
                description=funct["description"],
                parameters=params,
                returns=funct["returns"]["type"]
            ))

    def _create_output_file(self, file_name: str, mode: bool = True) -> None:

        if not mode:
            file_name = file_name[:-5] + "TEST" + file_name[-5:]

        self.output_path = file_name

        if "/" in file_name:
            last_slash = 0
            i = 0
            for char in file_name:
                if char == "/":
                    last_slash = i
                i += 1

            path = file_name[:last_slash]

            try:
                os.makedirs(path)
            except FileExistsError:
                pass

        try:
            with open(file_name, "x") as output_file:
                pass
        except FileExistsError:
            print(f"File \"{file_name}\" "
                  "already Exists, do you wish to replace it?")
            # answer = input("Y for 'yes', any for 'no': ").lower()
            answer = "y"
            if answer == "y":
                with open(file_name, "w") as output_file:
                    output_file.write("")
                print("File Cleared, continuing...")
            else:
                print("Stopping Program")
                raise

    def _load_llm(self, init: bool = True) -> None:

        self.llm_files = {}

        if init:
            print()
            print()
            load_dotenv()
            # self._llm = Small_LLM_Model(device="cuda")
            self._llm = Small_LLM_Model(device="cpu")
            print("LLM created True")
            print()
            print()

            self.llm_files["vocab"] = self._llm.get_path_to_vocab_file()
            self.llm_files["merges"] = self._llm.get_path_to_merges_file()
            self.llm_files["tokenizer"] = (
                self._llm.get_path_to_tokenizer_file())

        else:

            self._llm = None
            print("LLM created False")

            self.llm_files["vocab"] = (
                "/home/tribeirinho/.cache/huggingface/hub/"
                "models--Qwen--Qwen3-0.6B/snapshots/"
                "c1899de289a04d12100db370d81485cdf75e47ca/vocab.json")
            self.llm_files["merges"] = (
                "/home/tribeirinho/.cache/huggingface/hub/"
                "models--Qwen--Qwen3-0.6B/snapshots/"
                "c1899de289a04d12100db370d81485cdf75e47ca/merges.txt")
            self.llm_files["tokenizer"] = (
                "/home/tribeirinho/.cache/huggingface/hub/"
                "models--Qwen--Qwen3-0.6B/snapshots/"
                "c1899de289a04d12100db370d81485cdf75e47ca/tokenizer.json")

        print(flush=True)
        print()
        print("\n".join([f"{k}: {v}" for k, v in self.llm_files.items()]))
        print()

        with open(self.llm_files["vocab"]) as vocab_file:
            self.vocab_text_int: dict[str, int] = json.load(vocab_file)

        self.vocab_int_text = {}

        for k, v in self.vocab_text_int.items():
            self.vocab_int_text[v] = k

        # i = 0
        # for k, v in vocab_text_int.items():
        #     print(k, v, end="  ")
        #     if i > 10:
        #         break
        #     i += 1

    def _make_deffunct_ids(self) -> None:

        self.tokenized_int_funct_list = []

        for funct in self.funct_defs:
            # print('\a', end="")
            # print(funct)
            # print()

            if self._llm:
                tokenized_tensor_funct = self._llm.encode(str(funct))
            else:
                tokenized_tensor_funct = Tensor(
                    [[675, 25, 5168, 2891, 32964, 198, 5009, 25, 2691, 1378,
                      5109, 3786, 323, 470, 862, 2629, 624, 4870, 25, 264, 259,
                      25, 1372, 198, 2233, 259, 25, 1372, 198, 5598, 25, 1372
                      ]], device="cpu")

            # print()
            # print("Prompt Tokenized int:")
            # print()
            # print(tokenized_tensor_funct[0])

            to_add: list[int] = (  # pyright: ignore
                tokenized_tensor_funct[0].tolist())  # pyright: ignore

            self.tokenized_int_funct_list.append(
                [self.vocab_text_int["ĠĠĠĠ"]
                 if x == self.vocab_text_int['ĉ']
                 else x for x in to_add]
            )

            # print()
            # print("Prompt Tokenized str:")
            # print(list(map(lambda x: self.vocab_int_text.get(x, ""),
            #                self.tokenized_int_funct_list[-1])))
            # print()
            # input()

            # str_back = self.id_decode(tokenized_funct)

            # print("Prompt re-coded:")
            # print(str_back)

            if not self._llm:
                break

        self.instructions = []

        if self._llm:
            json_prompt: list[int] = (  # pyright: ignore
                self._llm.encode(
                    "JSON Function:\n")[0].tolist())  # pyright: ignore
            format_request: list[int] = (  # pyright: ignore
                self._llm.encode(
                    "JSON Format:\n"
                    "{\n"
                    "    \"prompt\": \"given prompt\",\n"
                    "    \"name\": \"fn_name\",\n"
                    "    \"parameters\": {\n"
                    "        \"param1\": param1_val,\n"
                    "        \"param2\": param2_val\n"
                    "        <...>\n"
                    "    }\n"
                    "}\n\n"
                )[0].tolist())  # pyright: ignore

            self.universal_start = self._llm.encode(  # pyright: ignore
                "{\n"
                "    \"prompt\": \""
            )[0].tolist()  # pyright: ignore
            self.universal_post_prompt = self._llm.encode(  # pyright: ignore
                "\",\n"
                "    \"name\": \""
            )[0].tolist()  # pyright: ignore

            for t_funct in self.tokenized_int_funct_list:
                self.instructions += json_prompt + t_funct

            self.instructions += format_request
            # print("Instructions")
            # print(self.instructions)
            # print(len(self.instructions))

        else:
            self.instructions = []
            self.universal_start = [515, 262, 330, 40581, 788, 330]
            self.universal_post_prompt = [756, 262, 330, 606, 788, 330]
            # self.universal_post_prompt = [self.vocab_text_int["\",Ċ"],
            #                               self.vocab_text_int["ĠĠĠĠ"],
            #                               self.vocab_text_int["\""]]

        # print(self.universal_post_prompt)

    def run_model(self) -> None:

        self.to_export = []

        # try:

        for prompt in self.raw_prompts:
            print('\a', end="")
            print()
            print(prompt)
            print()

            prompt_id = self.prompt_to_id(prompt)

            starting = (self.universal_start + prompt_id
                        + self.universal_post_prompt)

            added_token = self.instructions + starting
            answer_len: int = len(starting)
            instruct_len: int = len(self.instructions)

            # print("universal_start", self.id_decode(self.universal_start))
            # print("prompt_id", self.id_decode(prompt_id))
            # print("universal_post_prompt", self.id_decode(
            #     self.universal_post_prompt))

            container_log: list[str] = ["{", "\""]
            logits_funct: list[float] = [1 for _ in range(151643)]

            pre_determined_str = """
name
":
Ġ"
fn
_add
_numbers
",Ċ
ĠĠĠĠ
Ġ"
parameters
":
Ġ{Ċ
ĠĠĠĠĠĠĠĠ
Ġ"
a
":
Ġ
2
,Ċ
ĠĠĠĠĠĠĠĠ
Ġ"
b
":
Ġ
3
Ċ
ĠĠĠĠ
Ġ}Ċ
}Ċ
"""

            pre_determined_list = [x for x in pre_determined_str.split("\n")
                                   if x]

            print()
            print("Starting Generation ", len(added_token),
                  "\n\n", self.id_decode(added_token), "\n\n",
                  container_log, sep="")
            print()
            print('\a', end="")
            # input()

            while True:

                print(flush=True)

                # logits_funct, gen = self._pre_gen_exceptions(
                #     logits_funct, answer_len, container_log)

                # gen = True

                # print(pre_determined_list, (len(pre_determined_list) - 1))
                # print(answer_len >= 70,
                #       (len(pre_determined_list)) == 0,
                #       (answer_len >= 70) or
                #       ((len(pre_determined_list)) == 0))

                if ((answer_len >= 120) or ((len(pre_determined_list)) == 0)):
                    print("Response too long, Cutting", container_log,
                          sep="\t")
                    logits_funct[self.vocab_text_int["}"]] = sys.maxsize

                    print("altered: ", end="")

                else:
                    print("generating: ", end="")
                    if self._llm:
                        logits_funct = (self._llm.get_logits_from_input_ids(
                            added_token))
                    else:
                        print(len(pre_determined_list), "til end")
                        logits_funct = [float(1) for _ in range(151643)]
                        logits_funct[self.vocab_text_int[
                            pre_determined_list.pop(0)]] = sys.maxsize

                # print("logits_funct len:", len(logits_funct))
                # print()
                # print()
                # print("vocab_int_text len:", len(self.vocab_int_text))
                # print("vocab_text_int len:", len(self.vocab_text_int))

                max_val = max(logits_funct)

                print(f"#{answer_len: 3} - max_val:",
                      ("inf" if max_val == sys.maxsize else round(max_val, 3)),
                      end="\t")
                max_val_ind = logits_funct.index(max_val)
                print(f"ID: {max_val_ind: 5}", end="\t")
                added_token_str = self.vocab_int_text[max_val_ind]
                print("added_token:", added_token_str, end="\t")

                max_val_ind = self._post_gen_exceptions(
                    max_val_ind, added_token[-1], logits_funct, answer_len)

                # added_token_int = vocab_text_int[added_token_str]
                # print("added_token_int", added_token_int)
                # print()

                added_token.append(max_val_ind)

                container_log = self._container_management(container_log,
                                                           added_token[-1])

                if not container_log:
                    break

                answer_len += 1

            print()
            print()
            print("Response Generated ", len(added_token),
                  "\n", self.id_decode(added_token), sep="")

            str_response = self.id_decode(added_token[instruct_len:])

            # str_response = ("{}"
            #                 if added_token[-1] in [
            #                     self.vocab_text_int["}"],
            #                     self.vocab_text_int["}Ċ"]]
            #                 else "Fail")

            # "".join([self.vocab_int_text[i]
            #                         for i in added_token]
            #                        ).replace("Ċ", "\n").replace("Ġ", " ")

            if not self._llm:
                self.to_export = str_response
                # print(self.to_export)
                break

            print()
            print()
            print("adding to list")

            self.to_export.append(str_response)

            print(self.to_export[-1])
            # break

        # except Exception as e:
        #     raise Exception("An error has occurred in the Processing"
        #                     f" of Prompts:\n\n{e}")

    def prompt_to_id(self, prompt: str) -> list[int]:

        if self._llm:
            # tokenized_prompt = self._llm.encode("\"prompt\": \""
            #                                     + prompt + "\"")
            tokenized_prompt = self._llm.encode(prompt)
        else:
            tokenized_prompt = Tensor(
                [[3838, 374, 279, 2629, 315, 220, 17, 323, 220, 18, 30]],
                device="cpu")

        print("Prompt Tokenized int:")
        print()
        print(tokenized_prompt[0])

        tokenized_int_prompt: list[int] = (  # pyright: ignore
            tokenized_prompt[0].tolist())  # pyright: ignore

        print()
        print("Prompt Tokenized str:")
        print(list(map(lambda x: self.vocab_int_text.get(x, ""),
                       tokenized_int_prompt)))

        # str_back = self.id_decode(tokenized)
        # print("Prompt re-coded:")
        # print(str_back)

        return (tokenized_int_prompt)

    def _pre_gen_exceptions(self, logits_funct: list[float],
                            ans_len: int,
                            container_log: list[str]
                            ) -> tuple[list[float], bool]:

        gen = True

        # logits_funct[self.vocab_text_int["{"]] = 1
        # logits_funct[self.vocab_text_int["Ċ"]] = 1
        # logits_funct[self.vocab_text_int["ĠĠĠĠ"]] = 1
        # logits_funct[self.vocab_text_int["}"]] = 1

        # if ans_len == 0:
        #     logits_funct[self.vocab_text_int["{"]] = sys.maxsize
        #     gen = False

        # elif ans_len == 1:
        #     logits_funct[self.vocab_text_int["Ċ"]] = sys.maxsize
        #     gen = False

        # elif ans_len == 2:
        #     logits_funct[self.vocab_text_int["ĠĠĠĠ"]] = sys.maxsize
        #     gen = False

        if (ans_len >= (70 if self._llm else 10)):
            print("Response too long, Cutting", container_log,
                  sep="\t")
            logits_funct[self.vocab_text_int["}"]] = sys.maxsize
            gen = False

        if not gen:
            print("altered: ", end="")

        return (logits_funct, gen)

    def _post_gen_exceptions(self, max_val_ind: int,
                             last_added_token: int,
                             logits_funct: list[float],
                             ans_len: int) -> int:

        return_val = max_val_ind

        if (max_val_ind in [self.vocab_text_int["}\""],
                            self.vocab_text_int["}\"Ċ"],
                            self.vocab_text_int["}\"ĊĊ"]]):
            return_val = self.vocab_text_int["}"]

        elif (max_val_ind in [self.vocab_text_int["]\""],
                              self.vocab_text_int["]\"Ċ"]]):
            return_val = self.vocab_text_int["]"]

        elif (max_val_ind in [self.vocab_text_int["}ĊĊ"]]):
            return_val = self.vocab_text_int["}Ċ"]

        elif (max_val_ind in [self.vocab_text_int[")\""],
                              self.vocab_text_int[")\"Ċ"]]):
            return_val = self.vocab_text_int[")"]

        elif (max_val_ind in [self.vocab_text_int["Ġ\""]] and
              last_added_token in [self.vocab_text_int["ĠĠĠĠ"],
                                   self.vocab_text_int["ĠĠĠĠĠĠĠĠ"]]):
            return_val = self.vocab_text_int["\""]

        elif max_val_ind == self.vocab_text_int["ĉ"]:
            return_val = self.vocab_text_int["ĠĠĠĠ"]

        if not return_val == max_val_ind:
            print(":\n: REPLACED:", end="")
            replace_logit = logits_funct[return_val]
            print(f"#{ans_len: 3} - max_val:",
                  ("inf" if replace_logit == sys.maxsize
                   else round(replace_logit, 3)),
                  end="\t")
            print(f"ID: {return_val: 5}", end="\t")
            added_token_str = self.vocab_int_text[return_val]
            print("added_token:", added_token_str, end="\t")

        return (return_val)

    def _container_management(self, container_log: list[str],
                              last_added_token: int) -> list[str]:

        to_print = True

        if (last_added_token in [self.vocab_text_int["{"],
                                 self.vocab_text_int["}"],
                                 self.vocab_text_int["}Ċ"],
                                 self.vocab_text_int["["],
                                 self.vocab_text_int["]"],
                                 self.vocab_text_int["]Ċ"],
                                 self.vocab_text_int["\""],
                                 self.vocab_text_int["\"Ċ"],
                                 self.vocab_text_int['ĠĠĠĠ'],
                                 self.vocab_text_int['ĠĠĠĠĠĠĠĠ'],
                                 self.vocab_text_int['Ċ'],
                                 self.vocab_text_int[","],
                                 self.vocab_text_int[":"],
                                 self.vocab_text_int["Ġ{Ċ"],
                                 self.vocab_text_int["Ġ}Ċ"],
                                 self.vocab_text_int["\",Ċ"],
                                 self.vocab_text_int["\","],
                                 self.vocab_text_int["Ġ\""],
                                 self.vocab_text_int["\":"]]):

            if last_added_token in [self.vocab_text_int["ĠĠĠĠĠĠĠĠ"],
                                    self.vocab_text_int["ĠĠĠĠ"],
                                    self.vocab_text_int["Ċ"],
                                    self.vocab_text_int[":"],
                                    self.vocab_text_int[","]]:
                to_print = False

            elif (last_added_token in [self.vocab_text_int["\""],
                                       self.vocab_text_int["\"Ċ"],
                                       self.vocab_text_int["\",Ċ"],
                                       self.vocab_text_int["\","],
                                       self.vocab_text_int["\":"]]
                    and container_log[-1] == "\""):
                container_log.pop()

            elif last_added_token in [self.vocab_text_int["Ġ{Ċ"],
                                      self.vocab_text_int["{"],
                                      self.vocab_text_int["["],
                                      self.vocab_text_int["\""],
                                      self.vocab_text_int["Ġ\""]]:
                to_add = last_added_token

                if to_add == self.vocab_text_int["Ġ{Ċ"]:
                    to_add = self.vocab_text_int["{"]
                if to_add == self.vocab_text_int["Ġ\""]:
                    to_add = self.vocab_text_int["\""]

                container_log.append(self.vocab_int_text[to_add])

            elif last_added_token in [self.vocab_text_int["}"],
                                      self.vocab_text_int["}Ċ"],
                                      self.vocab_text_int["Ġ}Ċ"],
                                      self.vocab_text_int["]"],
                                      self.vocab_text_int["]Ċ"]]:

                if ((last_added_token in [self.vocab_text_int["}"],
                                          self.vocab_text_int["}Ċ"],
                                          self.vocab_text_int["Ġ}Ċ"]]
                    and container_log[-1] == "{") or
                    (last_added_token in [self.vocab_text_int["]"],
                                          self.vocab_text_int["]Ċ"]]
                        and container_log[-1] == "[")):
                    print("Detected Bracket ending", end=" ")
                    container_log.pop()

                else:
                    print("ERROR", container_log[-1],
                          self.vocab_int_text[last_added_token])
                    if (last_added_token == self.vocab_text_int["}"]):
                        return []
            if to_print:
                print("log:", container_log, end="")

        return (container_log)

    def export_to_file(self, file_path: str | None = None) -> None:

        out_str: str

        if not file_path:
            file_path = self.output_path
        if not self._llm:
            file_path = file_path[:-5] + "TEST" + file_path[-5:]

        if isinstance(self.to_export, str):
            out_str = self.to_export
        elif isinstance(self.to_export, dict):
            out_str = json.dumps([self.to_export], indent=4)
        elif isinstance(self.to_export, list):  # pyright: ignore
            if isinstance(self.to_export[0], str):
                # to_export: str = cast(str, self.to_export)
                # converted: list[dict[str, Any]] = []
                # for out in to_export:
                #     try:
                #         converted.append(json.loads(out))
                #     except JSONDecodeError as e:
                #         print(e)
                # out_str = json.dumps(converted, indent=4)

                to_export: str = cast(str, self.to_export)


                out_list: list[str] = []

                for out in to_export:
                    # print()
                    # print()
                    # print(out)
                    in_list = [x for x in out.split("\n") if x]
                    out_list.append("\n    ".join(in_list))
                    # print()out_list
                    # print()
                    # print(out_list)
                out_str = "[\n    " + ",\n    ".join(out_list) + "\n]"

            elif isinstance(self.to_export[0], dict):  # pyright: ignore
                out_str = json.dumps(self.to_export, indent=4)

            else:
                raise TypeError(
                    "'self.to_export' is an unknown type:\n\n---\n\n"
                    f"{self.to_export}\n\n---\n\nType: {type(self.to_export)}")
        else:
            raise TypeError(
                "'self.to_export' is an unknown type:\n\n---\n\n"
                f"{self.to_export}\n\n---\n\nType: {type(self.to_export)}")

        print(out_str)

        try:
            with open(file_path, "w") as output_file:
                # inputs = input_file.read()
                output_file.write(out_str)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Output File \"{file_path}\" "
                                    f"not found {e}")

    def id_decode(self, ids: list[int]) -> str:

        if self._llm:
            return "".join(self._llm.decode(ids)
                           ).replace("Ċ", "\n").replace("Ġ", " ")
        else:
            return "".join([self.vocab_int_text[i] for i in ids]
                           ).replace("Ċ", "\n").replace("Ġ", " ")


def main(args: list[str]) -> None:

    # mode = False
    mode = True

    from time import localtime
    st = localtime()
    print(f"Start Time: {st.tm_hour}:{st.tm_min}")

    try:
        arg_inputs = val_args(args)
    except ValueError as e:
        print(f"Arguments passed incorrectly: {e}")
        return

    # print(arg_inputs)
    try:
        funct_caller = FunctCallLLM(arg_inputs, mode)
    except Exception as e:
        print("An error has occurred while building"
              f" 'FunctCallLLM':\n{e}")
        return
    # try:
    funct_caller.run_model()
    # except Exception as e:
    #     print(e)
    #     return
    print()
    print()
    print("success")
    print()
    print()

    try:
        funct_caller.export_to_file()
    except FileNotFoundError as e:
        print(e)
        return

    et = localtime()
    print(f"Start Time: {st.tm_hour}:{st.tm_min}")
    print(f"End Time: {et.tm_hour}:{et.tm_min}")
    rt = (et.tm_hour - st.tm_hour) * 60 + (et.tm_min - st.tm_min)
    print(f"Run Time: {rt} minutes")


if __name__ == "__main__":
    print("\033[2A", end="")
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print("\rThe program has been forcefully stopped")
