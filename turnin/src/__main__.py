import sys
from src import val_args, FunctCallLLM

# import os
# from dotenv import load_dotenv
# import httpcore
# from typing import Any, cast
# import json
# from src import (val_args, ft_repr,
#                  DefFunctException, FunctDef, Parameter
#                  )
# from llm_sdk import Small_LLM_Model
# from torch import AcceleratorError


# class FunctCallLLM():
#     """
#     Class holding all the Methods to run the LLM for Function Calling
#     """

#     raw_prompts: list[str]
#     funct_defs: list[FunctDef]
#     output_path: str

#     _llm: Small_LLM_Model
#     llm_files: dict[str, str]

#     vocab_text_int: dict[str, int]
#     vocab_int_text: dict[int, str]

#     tokenized_int_funct_list: list[list[int]]
#     instructions: list[int]
#     universal_start: list[int]
#     universal_post_prompt: list[int]

#     to_export: (str |
#                 dict[str, str | dict[str, Any]] |
#                 list[str | dict[str, str | dict[str, Any]]])

#     def __init__(self, arg_inputs: dict[str, str]) -> None:

#         if arg_inputs:
#             try:
#                 self._get_prompts(arg_inputs["input"])
#             except FileNotFoundError:
#                 raise
#             except json.decoder.JSONDecodeError as e:
#                 raise ValueError(
#                     f"File {arg_inputs['input']} is not properly"
#                     f" formatted.\nError Message: {e}")

#             try:
#                 self._get_funct_defs(arg_inputs["functions_definition"])
#             except FileNotFoundError:
#                 raise
#             except json.decoder.JSONDecodeError as e:
#                 raise ValueError(
#                     f"File {arg_inputs['functions_definition']} is not "
#                     f"properly. formatted.\nError Message: {e}")

#             try:
#                 self._create_output_file(arg_inputs["output"])
#             except FileExistsError:
#                 raise
#             except json.decoder.JSONDecodeError as e:
#                 raise ValueError(
#                     f"File {arg_inputs['output']} is not properly."
#                     f" formatted.\nError Message: {e}")

#         else:
#             raise ValueError("No Arguments were passed to the Class")

#         try:
#             self._load_llm()
#         except ModuleNotFoundError as e:
#             raise ModuleNotFoundError(
#                 f"Module Dependencies were not met:\n{e}")
#         except httpcore.ConnectError as e:
#             raise httpcore.ConnectError(
#                 "Small_LLM_Model was unable to Connect. "
#                 f"Check Connection and Try again another time\n{e}")

#         except Exception as e:
#             raise Exception("An unexpected error has occurred during "
#                             f"LLM Class Creation:\n{e}")

#         try:

#             self._make_deffunct_ids()

#         except DefFunctException as e:
#             error_len = e.e_len
#             del e.e_len
#             raise ValueError("An error has occurred in the Processing of"
#                              f" Callable Function number {error_len}: "
#                              f"{self.funct_defs[error_len]}:\n\n{e}")

#     def redefine_inputs(self, arg_inputs: dict[str, str]) -> None:
#         """
#         Used to redefine the 3 input files to be able to run the function
#         calling on different files on a single initialization of the LLM.
#         UNUSED
#         """

#         try:
#             self._get_prompts(arg_inputs["input"])
#         except FileNotFoundError:
#             raise

#         try:
#             self._get_funct_defs(arg_inputs["functions_definition"])
#         except FileNotFoundError:
#             raise

#         try:
#             self._create_output_file(arg_inputs["output"])
#         except FileExistsError:
#             raise

#         try:

#             self._make_deffunct_ids()

#         except DefFunctException as e:
#             error_len = e.e_len
#             del e.e_len
#             raise ValueError("An error has occurred in the Processing of "
#                              f"Callable Function number {error_len}: "
#                              f"{self.funct_defs[error_len]}:\n\n{e}")

#     def _get_prompts(self, file_name: str) -> None:
#         """
#         Gets the Prompts out of the file and converts them into a
#         List of Strs inside the instanced object.
#         """

#         try:
#             with open(file_name) as input_file:
#                 parsed_inputs = json.load(input_file)
#         except FileNotFoundError as e:
#             raise FileNotFoundError(f"Input File \"{file_name}\""
#                                     f" not found {e}")

#         self.raw_prompts = [ft_repr(obj["prompt"]) for obj in parsed_inputs]

#     def _get_funct_defs(self, file_name: str) -> None:
#         """
#         Gets the Function Definitions out of the file and converts it into a
#         List of FunctDef inside the instanced object.
#         """
#         try:
#             with open(file_name) as funct_def_file:
#                 parsed_funct_defs: list[dict[str, Any]] = (
#                     json.load(funct_def_file))
#         except FileNotFoundError as e:
#             raise FileNotFoundError(
#                 f"Functions Definition File \"{file_name}\" not found {e}")

#         self.funct_defs = []

#         for funct in parsed_funct_defs:
#             params: list[Parameter] = []
#             if len(funct["parameters"]):
#                 for name, type_dict in funct["parameters"].items():
#                     params.append(Parameter(p_name=name,
#                                             p_type=type_dict["type"]))

#             self.funct_defs.append(FunctDef(
#                 name=funct["name"],
#                 description=funct["description"],
#                 parameters=params,
#                 returns=funct["returns"]["type"]
#             ))

#     def _create_output_file(self, file_name: str) -> None:
#         """
#         Creates the Output File. if the an object of the same name
#         already exists, it checks to see if the user wants to overwrite it.
#         """

#         self.output_path = file_name

#         if "/" in file_name:
#             last_slash = 0
#             i = 0
#             for char in file_name:
#                 if char == "/":
#                     last_slash = i
#                 i += 1

#             path = file_name[:last_slash]

#             try:
#                 os.makedirs(path)
#             except FileExistsError:
#                 pass

#         try:
#             with open(file_name, "x"):
#                 pass
#         except FileExistsError:
#             print(f"File \"{file_name}\" "
#                   "already exists, do you wish to replace it?")
#             answer = input("Y for 'yes', any for 'no': ").lower()
#             if not answer == "y":
#                 print("Stopping Program")
#                 raise
#             else:
#                 print("Continuing...")

#     def _load_llm(self) -> None:
#         """
#         Loads LLM from 'Small_LLM_Model', extracts the relevant
#         files and generates the vocabularies used later.
#         """

#         self.llm_files = {}
#         print()

#         load_dotenv()
#         self._llm = Small_LLM_Model()
#         try:
#             tokens = self.prompt_to_id("test")
#             self._llm.get_logits_from_input_ids(tokens)
#         except AcceleratorError:
#             print(f"\nDefault Loading ({self._llm._device}) has failed\n"
#                   "Reloading LLM using the device as 'cpu'\n")
#             self._llm = Small_LLM_Model(device="cpu")

#         self.llm_files["vocab"] = self._llm.get_path_to_vocab_file()
#         self.llm_files["merges"] = self._llm.get_path_to_merges_file()
#         self.llm_files["tokenizer"] = (
#             self._llm.get_path_to_tokenizer_file())

#         with open(self.llm_files["vocab"]) as vocab_file:
#             self.vocab_text_int: dict[str, int] = json.load(vocab_file)

#         self.vocab_int_text = {}

#         for k, v in self.vocab_text_int.items():
#             self.vocab_int_text[v] = k

#     def _make_deffunct_ids(self) -> None:
#         """
#         Turns the FunctDef into a standardized initial prompt
#         held in 'self.instructions'.
#         """

#         self.tokenized_int_funct_list = []

#         for funct in self.funct_defs:

#             tokenized_tensor_funct = self._llm.encode(str(funct))

#             to_add: list[int] = (  # pyright: ignore
#                 tokenized_tensor_funct[0].tolist())  # pyright: ignore

#             self.tokenized_int_funct_list.append(
#                 [self.vocab_text_int["ĠĠĠĠ"]
#                  if x == self.vocab_text_int['ĉ']
#                  else x for x in to_add]
#             )

#         self.instructions = []

#         json_prompt: list[int] = (  # pyright: ignore
#             self._llm.encode(
#                 "JSON Function:\n")[0].tolist())  # pyright: ignore
#         format_request: list[int] = (  # pyright: ignore
#             self._llm.encode(
#                 "JSON Format:\n"
#                 "{\n"
#                 "    \"prompt\": \"given prompt\",\n"
#                 "    \"name\": \"fn_name\",\n"
#                 "    \"parameters\": {\n"
#                 "        \"param1\": param1_val,\n"
#                 "        \"param2\": param2_val\n"
#                 "        <...>\n"
#                 "    }\n"
#                 "}\n\n"
#             )[0].tolist())  # pyright: ignore

#         self.universal_start = self._llm.encode(  # pyright: ignore
#             "{\n"
#             "    \"prompt\": \""
#         )[0].tolist()  # pyright: ignore
#         self.universal_post_prompt = self._llm.encode(  # pyright: ignore
#             "\",\n"
#             "    \"name\": \""
#         )[0].tolist()  # pyright: ignore

#         for t_funct in self.tokenized_int_funct_list:
#             self.instructions += json_prompt + t_funct

#         self.instructions += format_request

#     def run_model(self) -> None:
#         """
#         Runs the Full Model after the initialization.

#         Takes in the 'self.instructions' sections,
#         joins one of the tokenized Prompts at a time
#         and generates the answer.

#         Repeats for all Prompts and creates a list wit all
#         the the output function calling dictionaries ready
#         to be printed on a JSON File.
#         """

#         self.to_export = []

#         for prompt in self.raw_prompts:

#             prompt_id = self.prompt_to_id(prompt)

#             starting = (self.universal_start + prompt_id
#                         + self.universal_post_prompt)

#             added_token = self.instructions + starting
#             answer_len: int = len(starting)
#             instruct_len: int = len(self.instructions)

#             container_log: list[str] = ["{", "\""]

#             while True:

#                 if ((answer_len >= 120)):
#                     print("Response too long, Cutting", container_log,
#                           sep="\t")
#                     logits_funct = [float(1) for _ in range(151643)]
#                     if container_log[-1] == "{":
#                         logits_funct[self.vocab_text_int["}"]] = sys.maxsize
#                     if container_log[-1] == "[":
#                         logits_funct[self.vocab_text_int["]"]] = sys.maxsize
#                     if container_log[-1] == "\"":
#                         logits_funct[self.vocab_text_int["\""]] = sys.maxsize

#                 else:
#                     logits_funct = (self._llm.get_logits_from_input_ids(
#                         added_token))

#                 max_val = max(logits_funct)

#                 max_val_ind = logits_funct.index(max_val)

#                 max_val_ind = self._post_gen_exceptions(
#                     max_val_ind, added_token[-1])

#                 added_token.append(max_val_ind)

#                 container_log = self._container_management(container_log,
#                                                            added_token[-1])

#                 if not container_log:
#                     break

#                 answer_len += 1

#             str_response = self.id_decode(added_token[instruct_len:])

#             self.to_export.append(str_response)

#     def prompt_to_id(self, prompt: str) -> list[int]:
#         """
#         Standardized form of turning a string into a list of IDs
#         """

#         tokenized_prompt = self._llm.encode(prompt)

#         tokenized_int_prompt: list[int] = (  # pyright: ignore
#             tokenized_prompt[0].tolist())  # pyright: ignore

#         return (tokenized_int_prompt)

#     def _post_gen_exceptions(self, max_val_ind: int,
#                              last_added_token: int) -> int:
#         """
#         Catches unusual, unhelpful or harmful tokens and corrects
#         them to simplified and/or corrected tokens.
#         """

#         return_val = max_val_ind

#         if (max_val_ind in [self.vocab_text_int["}\""],
#                             self.vocab_text_int["}\"Ċ"],
#                             self.vocab_text_int["}\"ĊĊ"]]):
#             return_val = self.vocab_text_int["}"]

#         elif (max_val_ind in [self.vocab_text_int["\\"]]):
#             return_val = self.vocab_text_int["\\\\"]

#         elif (max_val_ind in [self.vocab_text_int["]\""],
#                               self.vocab_text_int["]\"Ċ"]]):
#             return_val = self.vocab_text_int["]"]

#         elif (max_val_ind in [self.vocab_text_int["}ĊĊ"]]):
#             return_val = self.vocab_text_int["}Ċ"]

#         elif (max_val_ind in [self.vocab_text_int[")\""],
#                               self.vocab_text_int[")\"Ċ"]]):
#             return_val = self.vocab_text_int[")"]

#         elif (max_val_ind in [self.vocab_text_int["Ġ\""]] and
#               last_added_token in [self.vocab_text_int["ĠĠĠĠ"],
#                                    self.vocab_text_int["ĠĠĠĠĠĠĠĠ"]]):
#             return_val = self.vocab_text_int["\""]

#         elif max_val_ind == self.vocab_text_int["ĉ"]:
#             return_val = self.vocab_text_int["ĠĠĠĠ"]

#         return (return_val)

#     def _container_check(self, curr_tokens: list[int]) -> bool:
#         """
#         Checks if all the containers (Brackets and Quotes) in the output are closed.
#         """

#         curr_str = self.id_decode(curr_tokens)

#         container_log = []

#         for char in curr_str:
#             if char == "\"":
#                 if not container_log:
#                     container_log.append(char)
#                 elif container_log[-1] == "\"":
#                     container_log.pop()
#                 else:
#                     container_log.append(char)

#             if char in ["{", "["]:
#                 container_log.append(char)
#             if char in ["}", "]"]:



#         container_log: list[str] = ["{", "\""]

#         for token in curr_tokens:
#             container_log = self._container_management(container_log, token)

#             if not container_log:
#                 return (False)

#         return (True)

#     def _container_management(self, container_log: list[str],
#                               last_added_token: int) -> list[str]:
#         """
#         Manages the container Tracker, checking that brackets are tracked from
#         opening to closing, making sure the generation ends correctly
#         """

#         if (last_added_token in [self.vocab_text_int["{"],
#                                  self.vocab_text_int["}"],
#                                  self.vocab_text_int["}Ċ"],
#                                  self.vocab_text_int["["],
#                                  self.vocab_text_int["]"],
#                                  self.vocab_text_int["]Ċ"],
#                                  self.vocab_text_int["\""],
#                                  self.vocab_text_int["\"Ċ"],
#                                  #  self.vocab_text_int['ĠĠĠĠ'],
#                                  #  self.vocab_text_int['ĠĠĠĠĠĠĠĠ'],
#                                  #  self.vocab_text_int['Ċ'],
#                                  #  self.vocab_text_int[","],
#                                  #  self.vocab_text_int[":"],
#                                  self.vocab_text_int["Ġ{Ċ"],
#                                  self.vocab_text_int[")\",Ċ"],
#                                  self.vocab_text_int["}\",Ċ"],
#                                  self.vocab_text_int["Ġ}Ċ"],
#                                  self.vocab_text_int["\",Ċ"],
#                                  self.vocab_text_int["\","],
#                                  self.vocab_text_int["Ġ\""],
#                                  self.vocab_text_int["\":"]]):

#             if (last_added_token in [self.vocab_text_int["\""],
#                                      self.vocab_text_int["\"Ċ"],
#                                      self.vocab_text_int["\",Ċ"],
#                                      self.vocab_text_int["\","],
#                                      self.vocab_text_int[")\",Ċ"],
#                                      self.vocab_text_int["}\",Ċ"],
#                                      self.vocab_text_int["\":"]]
#                     and container_log[-1] == "\""):
#                 container_log.pop()

#             elif last_added_token in [self.vocab_text_int["Ġ{Ċ"],
#                                       self.vocab_text_int["{"],
#                                       self.vocab_text_int["["],
#                                       self.vocab_text_int["\""],
#                                       self.vocab_text_int["Ġ\""]]:
#                 to_add = last_added_token

#                 if to_add == self.vocab_text_int["Ġ{Ċ"]:
#                     to_add = self.vocab_text_int["{"]
#                 if to_add == self.vocab_text_int["Ġ\""]:
#                     to_add = self.vocab_text_int["\""]

#                 container_log.append(self.vocab_int_text[to_add])

#             elif last_added_token in [self.vocab_text_int["}"],
#                                       self.vocab_text_int["}Ċ"],
#                                       self.vocab_text_int["Ġ}Ċ"],
#                                       self.vocab_text_int["]"],
#                                       self.vocab_text_int["]Ċ"]]:

#                 if ((last_added_token in [self.vocab_text_int["}"],
#                                           self.vocab_text_int["}Ċ"],
#                                           self.vocab_text_int["Ġ}Ċ"]]
#                     and container_log[-1] == "{") or
#                     (last_added_token in [self.vocab_text_int["]"],
#                                           self.vocab_text_int["]Ċ"]]
#                         and container_log[-1] == "[")):
#                     container_log.pop()

#                 else:
#                     print("ERROR in container generation", container_log[-1],
#                           self.vocab_int_text[last_added_token])
#                     if (last_added_token == self.vocab_text_int["}"]):
#                         return []

#         return (container_log)

#     def export_to_file(self, file_path: str | None = None) -> None:
#         """
#         after generation, export_to_file takes the answer
#         and prints into the output file
#         """

#         exp_str: str

#         if not file_path:
#             file_path = self.output_path

#         if isinstance(self.to_export, str):
#             exp_str = self.to_export
#         elif isinstance(self.to_export, dict):
#             exp_str = json.dumps([self.to_export], indent=4)
#         elif isinstance(self.to_export, list):  # pyright: ignore
#             if isinstance(self.to_export[0], str):

#                 to_export: str = cast(str, self.to_export)
#                 out_list: list[str] = []

#                 for out in to_export:
#                     in_list = [x for x in out.split("\n") if x]
#                     out_list.append("\n    ".join(in_list))
#                 exp_str = "[\n    " + ",\n    ".join(out_list) + "\n]"

#             elif isinstance(self.to_export[0], dict):  # pyright: ignore
#                 exp_str = json.dumps(self.to_export, indent=4)

#             else:
#                 raise TypeError(
#                     "'self.to_export' is an unknown type:\n\n---\n\n"
#                     f"{self.to_export}\n\n---\n\nType: {type(self.to_export)}")
#         else:
#             raise TypeError(
#                 "'self.to_export' is an unknown type:\n\n---\n\n"
#                 f"{self.to_export}\n\n---\n\nType: {type(self.to_export)}")

#         out_str: str = ""

#         for i, char in enumerate(exp_str):
#             if char == "\\":
#                 if i == 0:
#                     out_str += "\\\\"
#                 elif exp_str[i - 1] == "\\":
#                     out_str += char
#                 elif i + 1 >= len(exp_str):
#                     out_str += "\\\\"
#                 elif exp_str[i + 1] not in "\\\"":
#                     out_str += "\\\\"
#                 else:
#                     out_str += char
#             else:
#                 out_str += char

#         try:
#             with open(file_path, "w") as output_file:
#                 output_file.write(out_str)
#         except FileNotFoundError as e:
#             raise FileNotFoundError(f"Output File \"{file_path}\" "
#                                     f"not found {e}")

#     def id_decode(self, ids: list[int]) -> str:
#         """
#         Standardized form of decoding IDs into a string.
#         Also holds a backup decoder that is unused in the project.
#         """

#         if self._llm:
#             return self._llm.decode(ids)
#         else:
#             return "".join([self.vocab_int_text[i] for i in ids]
#                            ).replace("Ċ", "\n").replace("Ġ", " ")


def main(args: list[str]) -> None:
    """
    Main Function. Parses arguments, initialise LLM and runs it.
    """

    try:
        arg_inputs = val_args(args)
    except ValueError as e:
        print(f"Arguments passed incorrectly: {e}")
        return

    try:
        funct_caller = FunctCallLLM(arg_inputs)
    except FileExistsError:
        return
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return
    except ValueError as e:
        print(e)
        return
    except ModuleNotFoundError as e:
        print("Module Dependencies were not met:\n"
              f"{e}")
        return
    except TypeError as e:
        print("An error has occurred while building"
              f" 'FunctCallLLM':\n{e}")
        return
    # except Exception as e:
    #     print("An error has occurred while building"
    #           f" 'FunctCallLLM':\n{e}")
    #     return
    try:
        funct_caller.run_model()
    except Exception as e:
        print(f"Error while running model: {e}")
        return

    try:
        funct_caller.export_to_file()
    except FileNotFoundError as e:
        print(f"Error while exporting to file: {e}")
        return


if __name__ == "__main__":
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print("\rThe program has been forcefully stopped")
