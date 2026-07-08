_This project has been created as part of the 42 curriculum by dmota-ri._

# Description

CallMeMaybe is designed to teach students how to handle Small Large Language Models (LLMs) using Python.

The goal is to create an algorithm that uses the provided `Small_LLM_Model` class being a wrapper around the `Qwen/Qwen3-0.6B` Small LLM to generate a list of Function Calling Dictionaries from given Prompts.

The model takes in two files:

- `input` (default: data/input/function_calling_tests.json)
  - list of Prompt Dictionaries
  - Structure:
    ```
    [
      {
        "prompt": "prompt1"
      },
      {
        "prompt": "prompt2"
      },
      <...>
    ]
    ```

- `functions_definition` (default: data/input/functions_definition.json)
  - list of Functions Dictionaries
  - Defines the possible Functions the Model will try to draw from and their code properties
  - Structure:
    ```
    [
      {
          "name": "fn_name1",
          "description": "description_str",
          "parameters": {
            "param1": {
              "type": param1_type
            },
            "param2": {
              "type": param1_type
            },
            <...>
          },
          "returns": {
            "type": returns_type
          }
      },
      {
          "name": "fn_name2",
          "description": "description_str",
          "parameters": {
            "param1": {
              "type": param1_type
            },
            "param2": {
              "type": param1_type
            },
            <...>
          },
          "returns": {
            "type": returns_type
          }
      },
      <...>
    ]
    ```

These files are processed and Tokenized to be used by the LLM to generate a list of responses per prompt given. the result is an output file

- `output` (default: data/output/function_calls.json)
  - list of Function Calling Dictionaries
  - Includes the original Prompt, the function to call and the parameters extracted from the Prompt
  - Structure:
    ```
    [
      {
          "prompt": "given prompt1",
          "name": "fn_name1",
          "parameters": {
              "param1": param1_val,
              "param2": param2_val
              <...>
          }
      },
      {
          "prompt": "given prompt2",
          "name": "fn_name2",
          "parameters": {
              "param1": param1_val,
              "param2": param2_val
              <...>
          }
      },
      <...>
    ]
    ```




• Algorithm explanation: Describe your constrained decoding approach in detail
• Design decisions: Explain key choices in your implementation
• Performance analysis: Discuss accuracy, speed, and reliability of your solution
• Challenges faced: Document difficulties encountered and how you solved them
• Testing strategy: Describe how you validated your implementation



## Model Inner Workings

This Section will go into detail on the inner workings of my implementation of the model from inputs to pre processing, processing and output.

### Arguments and Input

First step is always to Parse the arguments given in the console, in this case the names of the files that will be read or written into. The code reads and checks if the files are all viable.
- for input files, it will check if they exist at all.
- for the output file, it will check of the path has '/' in it, dictating that it is inside a directory that may or may not exist, so it will always make sure that directory exists, and then try to create the output file. if it already exists, it will check with the user that it is ok for it to be overwritten.

With the information of the input files loaded, the Pre-processing starts. first we convert the JSON into a Python structure (`List of Dicts`). from there we extract the information into my own structures. Prompts are saved as a `list of str` while `Functions` are saved as `FunctDef` that behave similarly to a Dict.

if any of these steps are not successful, the program will end early and display an error message with basic information on what went wrong and at times instruction on how to fix it. Most importantly, it will save on the time that the LLM class needs to load every single time.

### Tokenization and Logits Processing

With the Inputs parsed and the LLM class loaded and helper objects are created (namely Vocabularies) we start the Tokenization Processing

First i construct an universal prompt beginner, since all calls of the LLM must know what the functions available are, i generate a string designed to be small tokenswise but still have all the information available similar to this:
```
JSON Function:
{"name":"fn_name1","description":"description_str","parameters":{"param1":{"type":param1_type},"param2":{"type":param2_type},<...>},"return":{"type":returns_type}}
JSON Function:
{"name":"fn_name1","description":"description_str","parameters":{"param1":{"type":param1_type},"param2":{"type":param2_type},<...>},"return":{"type":returns_type}}
JSON Function:
<...>
```
At the end of this structure i put in the desired output format:
```
JSON Format:
{
    "prompt": "given prompt",
    "name": "fn_name",
    "parameters": {
        "param1": param1_val,
        "param2": param2_val
        <...>
    }
}

```
i give this one with all the extra things so the formatting comes out as best as possible from the generation.

With all these predetermined prompt cores i join them together creating the final instructions. for each prompt, said prompt is added to the end of the instructions in the format:

```
{
    "prompt": "prompt1",
    "name": "
```

Ready for the Model to look at this and think it already generated the very start of the JSON formatted dictionary. with the Full prompt, Generation beginning with Logits Processing.

The Way Generation works with the model we were given is:

- Starting Prompt (str) is tokenized and then turned into Token IDs, turning into a List of Tokens IDs(Ints)
- this List of Tokens is fed to the function get_logits_from_input_ids() which will return a list of Logits(floats) one for each token in the dictionaries
- the logit with the highest value is the one that the model thinks is the most likely to come next based on the tokens it evaluated on this call, so we add the ID corresponding to that logit (logits.index(max(logits))) to the starting prompt.
- with this new prompt we then do the process all over again until we get to the end of the generation, aa parameter we need to set outside of the loop in question.

That is the basic loop of how we add to the prompt until we get the response we want.

in my case, i have some extra steps. first of all, ive noticed sometimes the model liked to put a few too many spaces in the formatting, among other "wrong token" situations. so after generation, i check the token, and if it is one of the situations ive observed, it gets amended by replacing the output as necessary.

The way i detect an End of Response is by detecting that all the Brackets in the response have been closed properly. we start with a '{' '"' and we add to it. when all the containers have been closed i detect an end of response. as a fail safe, if something goes wrong and we reach a length of 120 tokens, i forcibly start closing curly brackets until the generation finished

### Finalization and Outputs

after the LLM has run it's corse, all the responses are decoded back into strings and then joined into the final content of the output file.

with this content we must only open the file we created at the very beginning

# Instructions

For Execution, a Makefile is provided.

Upon getting the module, une must use `make install` to create the `.venv` folder and sync the contents with the requirements of the model. From there. running the command `make` or `make run` on a shell console will execute the program. If you use `make run_time`, at the end, it will display the time in seconds the program took to finish.

To change the default input and output files you may use the following format:
  ```
  make run [--functions_definition <function_definition_file>] [--input <input_file>] [--output <output_file>]
  ```

In the case that the Output file already exists, the following message will appear:
  ```
  File "<output_file>" already Exists, do you wish to replace it?
  Y for 'yes', any for 'no':
  ```
use 'y' to continue, or any other input to abort

# Resources

Most of the core concepts I learned from previous others projects and through pure experimentation with the tokens and vocabularies.

For further explanation of particular aspects of internal particular small inconsistencies or new errors i was not familiar with, I sometimes checked in with AI with mixed results. I also used it as a tool to sift through some particularly lengthy outputs to check for any inconsistencies i may have missed myself.

## Sources:
https://huggingface.co/
https://www.geeksforgeeks.org/python/tensors-in-pytorch/
