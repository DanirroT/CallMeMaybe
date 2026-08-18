import sys
import os
from dotenv import load_dotenv
import httpcore
from typing import Any, cast
import json
from src import ft_repr, DefFunctException, FunctDef, Parameter
from llm_sdk import Small_LLM_Model
from torch import AcceleratorError


class FunctCallLLM():
    """
    Class holding all the Methods to run the LLM for Function Calling
    """

    raw_prompts: list[str]
    funct_defs: list[FunctDef]
    output_path: str

    _llm: Small_LLM_Model | None
    llm_files: dict[str, str]

    vocab_text_int: dict[str, int]
    vocab_int_text: dict[int, str]

    tokenized_int_funct_list: list[list[int]]
    instructions: list[int]
    universal_start: list[int]
    universal_post_prompt: list[int]

    to_export: (str |
                dict[str, str | dict[str, Any]] |
                list[str | dict[str, str | dict[str, Any]]])

    def __init__(self, arg_inputs: dict[str, str], mode: bool = True) -> None:

        if arg_inputs:
            try:
                self._get_prompts(arg_inputs["input"])
            except FileNotFoundError:
                raise
            except json.decoder.JSONDecodeError as e:
                raise ValueError(
                    f"File {arg_inputs['input']} is not properly"
                    f" formatted.\nError Message: {e}")

            try:
                self._get_funct_defs(arg_inputs["functions_definition"])
            except FileNotFoundError:
                raise
            except json.decoder.JSONDecodeError as e:
                raise ValueError(
                    f"File {arg_inputs['functions_definition']} is not "
                    f"properly. formatted.\nError Message: {e}")

            try:
                self._create_output_file(arg_inputs["output"])
            except FileExistsError:
                raise
            except json.decoder.JSONDecodeError as e:
                raise ValueError(
                    f"File {arg_inputs['output']} is not properly."
                    f" formatted.\nError Message: {e}")

        else:
            raise ValueError("No Arguments were passed to the Class")

        try:
            self._load_llm(mode)
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

        try:

            self._make_deffunct_ids()

        except DefFunctException as e:
            error_len = e.e_len
            del e.e_len
            raise ValueError("An error has occurred in the Processing of"
                             f" Callable Function number {error_len}: "
                             f"{self.funct_defs[error_len]}:\n\n{e}")

    def redefine_inputs(self, arg_inputs: dict[str, str]) -> None:
        """
        Used to redefine the 3 input files to be able to run the function
        calling on different files on a single initialization of the LLM.
        UNUSED
        """

        try:
            self._get_prompts(arg_inputs["input"])
        except FileNotFoundError:
            raise
        except json.decoder.JSONDecodeError as e:
            raise ValueError(
                f"File {arg_inputs['input']} is not properly"
                f" formatted.\nError Message: {e}")

        try:
            self._get_funct_defs(arg_inputs["functions_definition"])
        except FileNotFoundError:
            raise
        except json.decoder.JSONDecodeError as e:
            raise ValueError(
                f"File {arg_inputs['functions_definition']} is not "
                f"properly. formatted.\nError Message: {e}")

        try:
            self._create_output_file(arg_inputs["output"])
        except FileExistsError:
            raise
        except json.decoder.JSONDecodeError as e:
            raise ValueError(
                f"File {arg_inputs['output']} is not properly."
                f" formatted.\nError Message: {e}")

        try:

            self._make_deffunct_ids()

        except DefFunctException as e:
            error_len = e.e_len
            del e.e_len
            raise ValueError("An error has occurred in the Processing of "
                             f"Callable Function number {error_len}: "
                             f"{self.funct_defs[error_len]}:\n\n{e}")

    def _get_prompts(self, file_name: str) -> None:
        """
        Gets the Prompts out of the file and converts them into a
        List of Strs inside the instanced object.
        """

        try:
            with open(file_name) as input_file:
                parsed_inputs = json.load(input_file)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Input File \"{file_name}\""
                                    f" not found {e}")

        self.raw_prompts = [ft_repr(obj["prompt"]) for obj in parsed_inputs]

    def _get_funct_defs(self, file_name: str) -> None:
        """
        Gets the Function Definitions out of the file and converts it into a
        List of FunctDef inside the instanced object.
        """

        try:
            with open(file_name) as funct_def_file:
                parsed_funct_defs: list[dict[str, Any]] = (
                    json.load(funct_def_file))
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Functions Definition File \"{file_name}\" not found {e}")

        self.funct_defs = []

        for funct in parsed_funct_defs:
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

    def _create_output_file(self, file_name: str) -> None:
        """
        Creates the Output File. if the an object of the same name
        already exists, it checks to see if the user wants to overwrite it.
        """

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
            with open(file_name, "x"):
                pass
        except FileExistsError:
            print(f"File \"{file_name}\" "
                  "already exists, do you wish to replace it?")
            # answer = input("Y for 'yes', any for 'no': ").lower()
            answer = "y"
            if not answer == "y":
                print("Stopping Program")
                raise
            else:
                print("Continuing...")

    def _load_llm(self, mode: bool = True) -> None:
        """
        Loads LLM from 'Small_LLM_Model', extracts the relevant
        files and generates the vocabularies used later.
        """

        self.llm_files = {}
        print()

        if mode:
            load_dotenv()
            self._llm = Small_LLM_Model(device="cpu")

            self.llm_files["vocab"] = self._llm.get_path_to_vocab_file()
            self.llm_files["merges"] = self._llm.get_path_to_merges_file()
            self.llm_files["tokenizer"] = (
                self._llm.get_path_to_tokenizer_file())

            # print(self.llm_files["vocab"])
        else:
            self._llm = None

            self.llm_files["vocab"] = (
                "/home/tribeirinho/.cache/huggingface/hub/"
                "models--Qwen--Qwen3-0.6B/snapshots/"
                "c1899de289a04d12100db370d81485cdf75e47ca/vocab.json"
            )

        with open(self.llm_files["vocab"]) as vocab_file:
            self.vocab_text_int: dict[str, int] = json.load(vocab_file)

        self.vocab_int_text = {}

        for k, v in self.vocab_text_int.items():
            self.vocab_int_text[v] = k

    def _make_deffunct_ids(self) -> None:
        """
        Turns the FunctDef into a standardized initial prompt
        held in 'self.instructions'.
        """

        self.tokenized_int_funct_list = []

        if self._llm:
            for funct in self.funct_defs:

                to_add: list[int] = self.prompt_to_id(str(funct))

                self.tokenized_int_funct_list.append(
                    [self.vocab_text_int["ĠĠĠĠ"]
                     if x == self.vocab_text_int['ĉ']
                     else x for x in to_add]
                )

            self.instructions = []

            json_prompt: list[int] = self.prompt_to_id("JSON Function:\n")
            format_request: list[int] = self.prompt_to_id(
                    "JSON Format:\n"
                    "{\n"
                    "    \"prompt\": \"given prompt\",\n"
                    "    \"name\": \"fn_name\",\n"
                    "    \"parameters\": {\n"
                    "        \"param1\": val1,\n"
                    "        \"param2\": val2\n"
                    "        <...>\n"
                    "    }\n"
                    "}\n\n"
                )

            self.universal_start = self.prompt_to_id(
                "{\n"
                "    \"prompt\": \""
            )
            self.universal_post_prompt = self.prompt_to_id(
                "\",\n"
                "    \"name\": \""
            )

            for t_funct in self.tokenized_int_funct_list:
                self.instructions += json_prompt + t_funct

            self.instructions += format_request

            # print()
            # print("self.universal_start")
            # print(self.universal_start)
            # print([515, 262, 330, 40581, 788, 330])
            # print()
            # print("self.universal_post_prompt")
            # print(self.universal_post_prompt)
            # print([756, 262, 330, 606, 788, 330])
            # print()
            # print("self.instructions")
            # print(self.instructions)
            # print(self.instructions ==
            #       [5370, 5712, 510, 31486, 3252, 8822, 93054, 32964, 2198,
            #        4684, 3252, 95155, 1378, 5109, 3786, 323, 470, 862, 1985,
            #        47891, 13786, 3252, 64, 22317, 1313, 3252, 4082, 58640, 65,
            #        22317, 1313, 3252, 4082, 58640, 689, 943, 3252, 4082, 698,
            #        5370, 5712, 510, 31486, 3252, 8822, 6892, 68347, 2198, 4684,
            #        3252, 3973, 421, 458, 7546, 374, 1496, 11, 4675, 3007, 421,
            #        1496, 11, 3557, 421, 10322, 47891, 13786, 3252, 77, 22317,
            #        1313, 3252, 11662, 58640, 689, 943, 3252, 6117, 698, 5370,
            #        5712, 510, 31486, 3252, 8822, 24005, 11207, 18177, 795,
            #        62527, 2198, 4684, 3252, 47866, 23628, 2734, 25, 12435,
            #        353, 320, 16, 488, 4379, 29776, 41720, 47891, 13786, 3252,
            #        66450, 22317, 1313, 3252, 4082, 58640, 7698, 22317, 1313,
            #        3252, 4082, 58640, 41720, 22317, 1313, 3252, 11662, 58640,
            #        689, 943, 3252, 4082, 698, 5370, 5712, 510, 31486, 3252,
            #        8822, 44329, 18063, 5738, 2198, 4684, 3252, 17174, 264,
            #        7870, 3239, 389, 264, 5189, 4625, 47891, 13786, 3252, 1631,
            #        22317, 1313, 3252, 917, 58640, 12216, 22317, 1313, 3252,
            #        917, 58640, 689, 943, 3252, 917, 698, 5370, 5712, 510,
            #        31486, 3252, 8822, 6443, 2458, 2198, 4684, 3252, 4418, 264,
            #        1034, 504, 279, 2661, 1815, 448, 5189, 11170, 47891, 13786,
            #        3252, 2343, 22317, 1313, 3252, 917, 58640, 17159, 22317,
            #        1313, 3252, 917, 58640, 689, 943, 3252, 917, 698, 5370,
            #        5712, 510, 31486, 3252, 8822, 8955, 8693, 2198, 4684, 3252,
            #        4061, 264, 3811, 914, 8482, 78428, 47891, 13786, 3252, 4214,
            #        22317, 1313, 3252, 917, 58640, 689, 943, 3252, 917, 698,
            #        5370, 15042, 510, 515, 262, 330, 40581, 788, 330, 41968,
            #        9934, 756, 262, 330, 606, 788, 330, 8822, 1269, 756, 262,
            #        330, 13786, 788, 341, 286, 330, 903, 16, 788, 1685, 16,
            #        6189, 345, 286, 330, 903, 17, 788, 1685, 17, 6189, 198,
            #        286, 366, 1112, 397, 262, 456, 630])
            # print()
            # print("self.tokenized_int_funct_list")
            # print(self.tokenized_int_funct_list)
            # print(self.tokenized_int_funct_list[0] ==
            #       [31486, 3252, 8822, 93054, 32964, 2198, 4684, 3252, 95155,
            #        1378, 5109, 3786, 323, 470, 862, 1985, 47891, 13786, 3252,
            #        64, 22317, 1313, 3252, 4082, 58640, 65, 22317, 1313, 3252,
            #        4082, 58640, 689, 943, 3252, 4082, 698])
            # print()

        else:

            self.universal_start = [515, 262, 330, 40581, 788, 330]

            self.universal_post_prompt = [756, 262, 330, 606, 788, 330]

            self.instructions = [
                5370, 5712, 510, 31486, 3252, 8822, 93054, 32964, 2198,
                4684, 3252, 95155, 1378, 5109, 3786, 323, 470, 862, 1985,
                47891, 13786, 3252, 64, 22317, 1313, 3252, 4082, 58640, 65,
                22317, 1313, 3252, 4082, 58640, 689, 943, 3252, 4082, 698,
                5370, 5712, 510, 31486, 3252, 8822, 6892, 68347, 2198, 4684,
                3252, 3973, 421, 458, 7546, 374, 1496, 11, 4675, 3007, 421,
                1496, 11, 3557, 421, 10322, 47891, 13786, 3252, 77, 22317,
                1313, 3252, 11662, 58640, 689, 943, 3252, 6117, 698, 5370,
                5712, 510, 31486, 3252, 8822, 24005, 11207, 18177, 795,
                62527, 2198, 4684, 3252, 47866, 23628, 2734, 25, 12435,
                353, 320, 16, 488, 4379, 29776, 41720, 47891, 13786, 3252,
                66450, 22317, 1313, 3252, 4082, 58640, 7698, 22317, 1313,
                3252, 4082, 58640, 41720, 22317, 1313, 3252, 11662, 58640,
                689, 943, 3252, 4082, 698, 5370, 5712, 510, 31486, 3252,
                8822, 44329, 18063, 5738, 2198, 4684, 3252, 17174, 264,
                7870, 3239, 389, 264, 5189, 4625, 47891, 13786, 3252, 1631,
                22317, 1313, 3252, 917, 58640, 12216, 22317, 1313, 3252,
                917, 58640, 689, 943, 3252, 917, 698, 5370, 5712, 510,
                31486, 3252, 8822, 6443, 2458, 2198, 4684, 3252, 4418, 264,
                1034, 504, 279, 2661, 1815, 448, 5189, 11170, 47891, 13786,
                3252, 2343, 22317, 1313, 3252, 917, 58640, 17159, 22317,
                1313, 3252, 917, 58640, 689, 943, 3252, 917, 698, 5370,
                5712, 510, 31486, 3252, 8822, 8955, 8693, 2198, 4684, 3252,
                4061, 264, 3811, 914, 8482, 78428, 47891, 13786, 3252, 4214,
                22317, 1313, 3252, 917, 58640, 689, 943, 3252, 917, 698,
                5370, 15042, 510, 515, 262, 330, 40581, 788, 330, 41968,
                9934, 756, 262, 330, 606, 788, 330, 8822, 1269, 756, 262,
                330, 13786, 788, 341, 286, 330, 903, 16, 788, 1685, 16,
                6189, 345, 286, 330, 903, 17, 788, 1685, 17, 6189, 198,
                286, 366, 1112, 397, 262, 456, 630]

            self.tokenized_int_funct_list = ([[
                31486, 3252, 8822, 93054, 32964, 2198, 4684, 3252, 95155,
                1378, 5109, 3786, 323, 470, 862, 1985, 47891, 13786, 3252,
                64, 22317, 1313, 3252, 4082, 58640, 65, 22317, 1313, 3252,
                4082, 58640, 689, 943, 3252, 4082, 698
            ]])

    def run_model(self) -> None:
        """
        Runs the Full Model after the initialization.

        Takes in the 'self.instructions' sections,
        joins one of the tokenized Prompts at a time
        and generates the answer.

        Repeats for all Prompts and creates a list wit all
        the the output function calling dictionaries ready
        to be printed on a JSON File.
        """

        self.to_export = []

        for prompt in self.raw_prompts:

            print()
            print(prompt)
            print()

            if self._llm:
                prompt_id = self.prompt_to_id(prompt)
            else:
                prompt_id = [
                    3838, 374, 279, 2629, 315, 220, 17, 323, 220, 18, 30]

            starting = (self.universal_start + prompt_id
                        + self.universal_post_prompt)

            added_token = self.instructions + starting
            answer_len: int = len(starting)
            instruct_len: int = len(self.instructions)

            container_log: list[str] = ["{"]

            pre_calc_out: list[int] = [
                8822, 10160, 756, 262, 330, 13786, 788, 341, 286, 330, 64,
                788, 220, 17, 345, 286, 330, 65, 788, 220, 18, 198, 262, 456,
                532
            ]

            while True:

                if ((answer_len >= 120) or not pre_calc_out):
                    print("Response too long, Cutting",
                          sep="\t")
                    logits_funct = [float(1) for _ in range(151643)]
                    if container_log[-1] == "{":
                        logits_funct[self.vocab_text_int["}"]] = sys.maxsize
                    if container_log[-1] == "[":
                        logits_funct[self.vocab_text_int["]"]] = sys.maxsize
                    if container_log[-1] == "\"":
                        logits_funct[self.vocab_text_int["\""]] = sys.maxsize

                else:
                    if self._llm:
                        logits_funct = (
                            self._llm.get_logits_from_input_ids(
                                added_token))
                    else:
                        logits_funct = [float(1) for _ in range(151643)]
                        logits_funct[pre_calc_out.pop(0)] = sys.maxsize

                max_val = max(logits_funct)

                max_val_ind = logits_funct.index(max_val)

                max_val_ind = self._post_gen_exceptions(
                    max_val_ind, added_token[-1])

                added_token.append(max_val_ind)

                print("added token:", self.vocab_int_text[added_token[-1]],
                      end="")

                container_log = self._container_check(container_log,
                                                      added_token[-1])

                if not container_log:
                    # print("out...")
                    break

                answer_len += 1

            # print()
            # print("Final int Output")
            # print(added_token[instruct_len:])
            # print()

            str_response = self.id_decode(added_token[instruct_len:])

            self.to_export.append(str_response)

    def prompt_to_id(self, prompt: str) -> list[int]:
        """
        Standardized form of turning a string into a list of IDs
        """

        if not self._llm:
            raise Exception("tried to encode on False Mode")

        tokenized_prompt = self._llm.encode(prompt)

        tokenized_int_prompt: list[int] = (  # pyright: ignore
            tokenized_prompt[0].tolist())  # pyright: ignore

        return (tokenized_int_prompt)

    def _post_gen_exceptions(self, max_val_ind: int,
                             last_added_token: int) -> int:
        """
        Catches unusual, unhelpful or harmful tokens and corrects
        them to simplified and/or corrected tokens.
        """

        return_val = max_val_ind

        if (max_val_ind in [self.vocab_text_int["}\""],
                            self.vocab_text_int["}\"Ċ"],
                            self.vocab_text_int["}\"ĊĊ"]]):
            return_val = self.vocab_text_int["}"]

        elif (max_val_ind in [self.vocab_text_int["\\"]]):
            return_val = self.vocab_text_int["\\\\"]

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

        return (return_val)

    def _container_check(self, container_log: list[str], next_id: int
                         ) -> list[str]:
        """
        Checks if all the containers (Brackets and Quotes)
        in the output are closed.
        """

        next_token = self.id_decode([next_id])

        # print("\tchecking:")

        for char in next_token:
            # print("\t", ft_repr(char), end="")

            if char in ["{", "["]:
                container_log.append(char)
                # print(container_log)
            elif char == "}" and container_log and container_log[-1] == "{":
                container_log.pop()
                # print(container_log)
            elif char == "]" and container_log and container_log[-1] == "[":
                container_log.pop()
                # print(container_log)
            elif char in ["}", "]"]:
                raise Exception("Unknown container syntax")

        # print("\nResult", container_log)

        return container_log

    # def _container_check(self, curr_tokens: list[int]) -> bool:
    #     """
    #     Checks if all the containers (Brackets and Quotes)
    #     in the output are closed.
    #     """

    #     curr_str = self.id_decode(curr_tokens)

    #     print("checking:", curr_str)

    #     container_log: list[str] = []

    #     for char in curr_str:
    #         print(ft_repr(char), end=" ")
    #         # if char == "\"":
    #         #     if not container_log:
    #         #         container_log.append(char)
    #         #     elif container_log[-1] == "\"":
    #         #         container_log.pop()
    #         #     else:
    #         #         container_log.append(char)
    #         #     print(container_log)

    #         if char in ["{", "["]:
    #             container_log.append(char)
    #             print(container_log)
    #         elif char == "}" and container_log[-1] == "{":
    #             container_log.pop()
    #             print(container_log)
    #         elif char == "]" and container_log[-1] == "[":
    #             container_log.pop()
    #             print(container_log)
    #         elif char in ["}", "]"]:
    #             raise Exception("Unknown container syntax")

    #     print("Result", container_log)

    #     return not bool(container_log)

    def _container_management(self, container_log: list[str],
                              last_added_token: int) -> list[str]:
        """
        Manages the container Tracker, checking that brackets are tracked from
        opening to closing, making sure the generation ends correctly
        """

        if (last_added_token in [self.vocab_text_int["{"],
                                 self.vocab_text_int["}"],
                                 self.vocab_text_int["}Ċ"],
                                 self.vocab_text_int["["],
                                 self.vocab_text_int["]"],
                                 self.vocab_text_int["]Ċ"],
                                 self.vocab_text_int["\""],
                                 self.vocab_text_int["\"Ċ"],
                                 self.vocab_text_int["Ġ{Ċ"],
                                 self.vocab_text_int[")\",Ċ"],
                                 self.vocab_text_int["}\",Ċ"],
                                 self.vocab_text_int["Ġ}Ċ"],
                                 self.vocab_text_int["\",Ċ"],
                                 self.vocab_text_int["\","],
                                 self.vocab_text_int["Ġ\""],
                                 self.vocab_text_int["\":"]]):

            if (last_added_token in [self.vocab_text_int["\""],
                                     self.vocab_text_int["\"Ċ"],
                                     self.vocab_text_int["\",Ċ"],
                                     self.vocab_text_int["\","],
                                     self.vocab_text_int[")\",Ċ"],
                                     self.vocab_text_int["}\",Ċ"],
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
                    container_log.pop()

                else:
                    print("ERROR in container generation", container_log[-1],
                          self.vocab_int_text[last_added_token])
                    if (last_added_token == self.vocab_text_int["}"]):
                        return []

        return (container_log)

    def export_to_file(self, file_path: str | None = None) -> None:
        """
        after generation, export_to_file takes the answer
        and prints into the output file
        """

        exp_str: str

        if not file_path:
            file_path = self.output_path

        if isinstance(self.to_export, str):
            exp_str = self.to_export
        elif isinstance(self.to_export, dict):
            exp_str = json.dumps([self.to_export], indent=4)
        elif isinstance(self.to_export, list):  # pyright: ignore
            if isinstance(self.to_export[0], str):

                to_export: str = cast(str, self.to_export)
                out_list: list[str] = []

                for out in to_export:
                    in_list = [x for x in out.split("\n") if x]
                    out_list.append("\n    ".join(in_list))
                exp_str = "[\n    " + ",\n    ".join(out_list) + "\n]"

            elif isinstance(self.to_export[0], dict):  # pyright: ignore
                exp_str = json.dumps(self.to_export, indent=4)

            else:
                raise TypeError(
                    "'self.to_export' is an unknown type:\n\n---\n\n"
                    f"{self.to_export}\n\n---\n\nType: {type(self.to_export)}")
        else:
            raise TypeError(
                "'self.to_export' is an unknown type:\n\n---\n\n"
                f"{self.to_export}\n\n---\n\nType: {type(self.to_export)}")

        out_str: str = ""

        for i, char in enumerate(exp_str):
            if char == "\\":
                if i == 0:
                    out_str += "\\\\"
                elif exp_str[i - 1] == "\\":
                    out_str += char
                elif i + 1 >= len(exp_str):
                    out_str += "\\\\"
                elif exp_str[i + 1] not in "\\\"":
                    out_str += "\\\\"
                else:
                    out_str += char
            else:
                out_str += char

        try:
            with open(file_path, "w") as output_file:
                output_file.write(out_str)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Output File \"{file_path}\" "
                                    f"not found {e}")

    def id_decode(self, ids: list[int]) -> str:
        """
        Standardized form of decoding IDs into a string.
        Also holds a backup decoder that is unused in the project.
        """

        if self._llm:
            return self._llm.decode(ids)
        else:
            return "".join([self.vocab_int_text[i] for i in ids]
                           ).replace("Ċ", "\n").replace("Ġ", " ")
