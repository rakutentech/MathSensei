import os
import sys
import json
import openai
import re
from tqdm import tqdm 
import random
import csv 
import argparse
import pprint
import time
from huggingface_hub import login
from transformers import AutoTokenizer,AutoModelForCausalLM,BitsAndBytesConfig
import transformers
import torch
from huggingface_hub import snapshot_download

import logging
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

from dotenv import load_dotenv
load_dotenv(".env")

import langchain 
from langchain.utilities.wolfram_alpha import WolframAlphaAPIWrapper
from langchain.agents import initialize_agent
from langchain.llms import AzureOpenAI
from langchain.agents import load_tools, AgentType
from langchain.chat_models import AzureChatOpenAI
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory
#langchain.debug = True


import wolframalpha


# Set up huggingface token 
huggingface_token = os.environ['HUGGINGFACE_TOKEN']


# Helper functions 
def _fix_fracs(string):
    substrs = string.split("\\frac")
    new_str = substrs[0]
    if len(substrs) > 1:
        substrs = substrs[1:]
        for substr in substrs:
            new_str += "\\frac"
            if substr[0] == "{":
                new_str += substr
            else:
                try:
                    assert len(substr) >= 2
                except:
                    return string
                a = substr[0]
                b = substr[1]
                if b != "{":
                    if len(substr) > 2:
                        post_substr = substr[2:]
                        new_str += "{" + a + "}{" + b + "}" + post_substr
                    else:
                        new_str += "{" + a + "}{" + b + "}"
                else:
                    if len(substr) > 2:
                        post_substr = substr[2:]
                        new_str += "{" + a + "}" + b + post_substr
                    else:
                        new_str += "{" + a + "}" + b
    string = new_str
    return string


def _fix_a_slash_b(string):
    if len(string.split("/")) != 2:
        return string
    a = string.split("/")[0]
    b = string.split("/")[1]
    try:
        a = int(a)
        b = int(b)
        assert string == "{}/{}".format(a, b)
        new_string = "\\frac{" + str(a) + "}{" + str(b) + "}"
        return new_string
    except:
        return string

def _remove_right_units(string):
    # "\\text{ " only ever occurs (at least in the val set) when describing units
    if "\\text{ " in string:
        splits = string.split("\\text{ ")
        assert len(splits) == 2
        return splits[0]
    else:
        return string


def _fix_sqrt(string):
    if "\\sqrt" not in string:
        return string
    splits = string.split("\\sqrt")
    new_string = splits[0] 
    for split in splits[1:]:
        if split[0] != "{":
            a = split[0]
            new_substr = "\\sqrt{" + a + "}" + split[1:]
        else:
            new_substr = "\\sqrt" + split
        new_string += new_substr
    return new_string


def _strip_string(string):
    # linebreaks  
    string = string.replace("\n", "")
    
    # remove inverse spaces
    string = string.replace("\\!", "")
    

    # replace \\ with \
    string = string.replace("\\\\", "\\")
    

    # replace tfrac and dfrac with frac
    string = string.replace("tfrac", "frac")
    string = string.replace("dfrac", "frac")
    

    # remove \left and \right
    string = string.replace("\\left", "")
    string = string.replace("\\right", "")
    
    
    # Remove circ (degrees)
    string = string.replace("^{\\circ}", "")
    string = string.replace("^\\circ", "")

    # remove dollar signs
    string = string.replace("\\$", "")
    string = string.replace("$","")
    
    # remove " 
    string = string.replace('"',"")
    
    # Extract the numbers 

    # remove units (on the right)
    string = _remove_right_units(string)
    
    # remove percentage
    string = string.replace("\\%", "")
    string = string.replace("\%", "")

    # " 0." equivalent to " ." and "{0." equivalent to "{." Alternatively, add "0" if "." is the start of the string
    string = string.replace(" .", " 0.")
    string = string.replace("{.", "{0.")
    
    # if empty, return empty string
    if len(string) == 0:
        return string
    if string[0] == ".":
        string = "0" + string

    # to consider: get rid of e.g. "k = " or "q = " at beginning
    if len(string.split("=")) == 2:
        if len(string.split("=")[0]) <= 2:
            string = string.split("=")[1]

    # fix sqrt3 --> sqrt{3}
    string = _fix_sqrt(string)

    # remove spaces
    string = string.replace(" ", "")

    # \frac1b or \frac12 --> \frac{1}{b} and \frac{1}{2}, etc. Even works with \frac1{72} (but not \frac{72}1). Also does a/b --> \\frac{a}{b}
    string = _fix_fracs(string)

    # manually change 0.5 --> \frac{1}{2}
    if string == "0.5":
        string = "\\frac{1}{2}"

    # NOTE: X/Y changed to \frac{X}{Y} in dataset, but in simple cases fix in case the model output is X/Y
    string = _fix_a_slash_b(string)

    return string


def is_equiv(str1, str2, verbose=True):
    if str1 is None and str2 is None:
        logging.warning("Both None")
        return True, str1, str2
    if str1 is None or str2 is None:
        return False,str1,str2
    else:
      try:
        ss1 = _strip_string(str1)
        ss2 = _strip_string(str2)

        return ss1 == ss2,ss1,ss2
      except:
        return str1 == str2,str1,str2
      

def remove_boxed(s):
    left = "\\boxed{"
    try:
        assert s[:len(left)] == left
        assert s[-1] == "}"
        return s[len(left):-1]
    except:
        return None

def last_boxed_only(sample):
    """
    Given a (q,a) sample, filter the answers so that they only contain 
    the last \boxed{...} or \fbox{...} element
    """
    q, a = sample
    a = last_boxed_only_string(a)
    if a == None:
        return None
    return (q, a)

def last_boxed_only_string(string):
    idx = string.rfind("\\boxed")
    if idx < 0:
        idx = string.rfind("\\fbox")
        if idx < 0:
            return None

    i = idx
    right_brace_idx = None
    num_left_braces_open = 0
    while i < len(string):
        if string[i] == "{":
            num_left_braces_open += 1
        if string[i] == "}":
            num_left_braces_open -= 1
            if num_left_braces_open == 0:
                right_brace_idx = i
                break
        i += 1
    
    if right_brace_idx == None:
        retval = None
    else:
        retval = string[idx:right_brace_idx + 1]
    
    return retval

def only_until_first_boxed_from_tokens(string, tokens):
    idx = string.find("\\boxed")
    if idx < 0:
        idx = string.find("\\fbox")
        if idx < 0:
            return None
    
    cum_length = 0
    for i, t in enumerate(tokens):
        cum_length += len(t)
        if cum_length >= idx:
            break
    
    return tokens[:i]



def clean_numbers(sample):
    if not sample:
        return None
    new_sample = list()
    for s in sample:
        new_sample.append(_clean_numbers(s))

    return tuple(new_sample)

def _clean_numbers(string):
    """
    Clean Numbers in the given string

    >>> _clean_numbers(None, "Hello 123")
    'Hello 123'
    >>> _clean_numbers(None, "Hello 1234")
    'Hello 1,234'
    >>> _clean_numbers(None, "Hello 1234324asdasd")
    'Hello 1,234,324asdasd'
    """
    num_prev_digits = 0
    new_string = ""
    for i, c in enumerate(string):
        # isdigit() doesnt work here because of weird unicode chars.
        if c in {'1', '2', '3', '4', '5', '6', '7', '8', '9', '0'}:
            num_prev_digits += 1
        else:
            if num_prev_digits > 3:
                # Some fixing
                string_number = new_string[-num_prev_digits:]
                new_string = new_string[:-num_prev_digits] + "{0:,}".format(int(string_number))
            num_prev_digits = 0
        new_string += c

    if num_prev_digits > 3:
        # Some fixing
        string_number = new_string[-num_prev_digits:]
        new_string = new_string[:-num_prev_digits] + "{0:,}".format(int(string_number))

    return new_string



def append_csv(save_file_path, data):
        
        # Check if the file exists
        file_exists = os.path.isfile(save_file_path)

        # Open the CSV file in append mode
        with open(save_file_path, 'a', newline='') as file:
            
            writer = csv.writer(file)

            # Write the header row if the file is newly created
            if not file_exists:
                writer.writerow(['Model_name','Temperature','Question','Gold_Solution','Gold_Answer','COT_Output','COT_final_answer'])  # Replace with your column names

            # Write the data to the CSV file
            writer.writerow(data)


def save_output(question, gold_answer,gold_final_answer, COT_output, COT_final_answer, method, args, save_file_dir="math_outputs_cot_variants"):
    file_name = "math_cot_" +"_"+ args.model_name +"_" +str(args.temperature) + method + ".csv" 
    save_file_path = os.path.join(save_file_dir,file_name)
   
    data_to_append = [args.model_name,args.temperature,question,gold_answer,gold_final_answer,COT_output,COT_final_answer]
    append_csv(save_file_path, data_to_append)


def extract_last_number(output):
    # Find all numbers in the text
    numbers = re.findall(r'\d+\.?\d*', output)
    
    # Return the last number
    return float(numbers[-1]) if numbers else None



def get_answer(output, string="The answer is "):

    
    match = re.search('The answer is (\w+)', output)
    if match:
        predicted_final_answer = (match.group(1))
    else:
        predicted_final_answer = None

    return predicted_final_answer 



def read_jsonl_file(file_path):
    data = []

    with open(file_path, 'r') as file:
        for line in file:
            record = json.loads(line)
            data.append(record)

    return data

def load_json_file(file_path):
    with open(file_path,"r") as file:
        data=json.load(file)

    return data    

def extract_boxed_value(text):
    boxed_value = re.search(r'\\boxed{(.*?)}', text)
    if boxed_value:
      return (boxed_value.group(1))

    else:
       return None 
    

def extract_model_answer(output):
    match = re.search(r'Answer:\s*(.*)', output)
    if match:
      answer = match.group(1)
    else:
      try:
          answer = extract_boxed_value(output)
      except:
          answer = None          

    return answer 

def extract_vals(string):
  match = re.search(r'####\s*(-?\d+)', string)
  if match:
    extracted_value = match.group(1)
    try: 
     extracted_value = float(extracted_value)  # Convert to an integer if needed
    except:
     extracted_value=extracted_value

  return extracted_value


# add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utilities import *
from demos import prompt_codefixer,prompt_bing_answer_extractor, prompt_bing_query,prompt_basc,prompt_kr, prompt_out_type,prompt_pg,prompt_policy,prompt_qg,prompt_pot,prompt_kr_sg,prompt_walpha_kr_sg,prompt_walpha_kr,prompt_kr_pg_sg,prompt_kr_pg,prompt_for_cot,prompt_walpha_context_withthought


class solver:

    def __init__(self, args):
        # arguments
        
        # Set the attributes
        for key, value in vars(args).items():
            setattr(self, key, value)


        
        # external arguments
        #self.current_index = 0
        self.api_key = openai.api_key
        self.examples = self.load_data()
        self.modules = []

        if self.knowledge_model == 'llama2_13b':
            # Huggingface login
            login(token=huggingface_token,new_session=False)  

            repo = "meta-llama/Llama-2-13b-hf"

            # Set cache dir and local dir 
            cache_dir = os.environ['LLAMA2_13B_CACHE_DIR']
            local_dir = os.environ['LLAMA2_13B_LOCAL_DIR']

            snapshot_download(repo_id=repo,cache_dir=cache_dir,local_dir=local_dir,local_dir_use_symlinks=True)

            # path to model
            logging.info("=====Running Llama2-13B-hf========")

            # Check if CUDA (GPU) is available 
            if torch.cuda.is_available():
                    # Get the number of available GPUs
                    num_gpus = torch.cuda.device_count()
                    logging.info(f"Number of available GPUs: {num_gpus}")
                    # Iterate through available GPUs and print information about each
                    for i in range(num_gpus):
                        gpu = torch.cuda.get_device_name(i)
                        gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1e9  # in GB
                        logging.info(f"GPU,Total Memory: {gpu},{gpu_memory}")
            else:
                    logging.info("No GPU available. Using CPU.")

            
            # Define the tokenizer of python generator module
            self.knowledge_tokenizer = AutoTokenizer.from_pretrained(local_dir)

            
            # Define the model pipeline of the python generator module
            self.knowledge_pipeline = transformers.pipeline(
            "text-generation",
            model=local_dir,
            torch_dtype=torch.float32,
            device_map="auto",
        
            )
            
        if self.knowledge_model == 'llama2_7b':
            
            # Huggingface login
            login(token=huggingface_token,new_session=False)  

            repo = "meta-llama/Llama-2-7b-hf"

            cache_dir = os.environ['LLAMA2_7B_CACHE_DIR']
            local_dir = os.environ['LLAMA2_7B_LOCAL_DIR']

            snapshot_download(repo_id=repo,cache_dir=cache_dir,local_dir=local_dir,local_dir_use_symlinks=True)

            # Path to model
            logging.info("=====Running Llama2-7B-hf========")

            # Check if CUDA (GPU) is available 
            if torch.cuda.is_available():
                    # Get the number of available GPUs
                    num_gpus = torch.cuda.device_count()
                    logging.info(f"Number of available GPUs: {num_gpus}")
                    # Iterate through available GPUs and print information about each
                    for i in range(num_gpus):
                        gpu = torch.cuda.get_device_name(i)
                        gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1e9  # in GB
                        logging.info(f"GPU,Total Memory: {gpu},{gpu_memory}")
            else:
                    logging.info("No GPU available. Using CPU.")

            # Define the tokenizer of python generator module
            self.knowledge_tokenizer = AutoTokenizer.from_pretrained(local_dir)

            
            # Define the model pipeline of the python generator module
            self.knowledge_pipeline = transformers.pipeline(
            "text-generation",
            model=local_dir,
            torch_dtype=torch.float32,
            device_map="auto",
        
            )
            
            

        if self.python_model == 'code_llama7b_python':

            # Huggingface login
            login(token=huggingface_token,new_session=False)  

            repo = "codellama/CodeLlama-7b-Python-hf"
            cache_dir = os.environ['CODELLAMA_7B_PYTHON_CACHE_DIR']
            local_dir = os.environ['CODELLAMA_7B_PYTHON_LOCAL_DIR']
            snapshot_download(repo_id=repo,cache_dir=cache_dir,local_dir=local_dir,local_dir_use_symlinks=True)

            # Path to model
            logging.info("=====Running CodeLLama-7B-Python========")

            # Check if CUDA (GPU) is available 
            if torch.cuda.is_available():
                    # Get the number of available GPUs
                    num_gpus = torch.cuda.device_count()
                    logging.info(f"Number of available GPUs: {num_gpus}")
                    # Iterate through available GPUs and print information about each
                    for i in range(num_gpus):
                        gpu = torch.cuda.get_device_name(i)
                        gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1e9  # in GB
                        logging.info(f"GPU,Total Memory: {gpu},{gpu_memory}")
            else:
                    logging.info("No GPU available. Using CPU.")

           
            # Define the tokenizer of python generator module
            self.python_tokenizer = AutoTokenizer.from_pretrained(local_dir)

            
            # Define the model pipeline of the python generator module
            self.python_pipeline = transformers.pipeline(
            "text-generation",
            model=local_dir,
            torch_dtype=torch.float32,
            device_map="auto",
        
            )
            
        if self.python_model == 'code_llama13b_python':

            # Huggingface login
            login(token=huggingface_token,new_session=False)  
            repo = "codellama/CodeLlama-13b-Python-hf"

            cache_dir = os.environ['CODELLAMA_13B_PYTHON_CACHE_DIR']
            local_dir = os.environ['CODELLAMA_13B_PYTHON_LOCAL_DIR']
      

            snapshot_download(repo_id=repo,cache_dir=cache_dir,local_dir=local_dir,local_dir_use_symlinks=True)

            # Path to model
            logging.info("=====Running CodeLLama-13B-python========")

            # Check if CUDA (GPU) is available 
            if torch.cuda.is_available():
                    # Get the number of available GPUs
                    num_gpus = torch.cuda.device_count()
                    logging.info(f"Number of available GPUs: {num_gpus}")
                    # Iterate through available GPUs and print information about each
                    for i in range(num_gpus):
                        gpu = torch.cuda.get_device_name(i)
                        gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1e9  # in GB
                        logging.info(f"GPU,Total Memory: {gpu},{gpu_memory}")
            else:
                    logging.info("No GPU available. Using CPU.")

          
            # Define the tokenizer of python generator module
            self.python_tokenizer = AutoTokenizer.from_pretrained(local_dir)

            
            # Define the model pipeline of the python generator module
            self.python_pipeline = transformers.pipeline(
            "text-generation",
            model=local_dir,
            torch_dtype=torch.float32,
            device_map="auto",
        
            )
           

        if self.python_model == 'code_llama34b':

            # Huggingface login
            login(token=huggingface_token,new_session=False)  

            repo = "Phind/Phind-CodeLlama-34B-v2"
            cache_dir = os.environ['CODELLAMA_34B_CACHE_DIR']
            local_dir = os.environ['CODELLAMA_34B_LOCAL_DIR']
          
            snapshot_download(repo_id=repo,cache_dir=cache_dir,local_dir=local_dir,local_dir_use_symlinks=True)

            # Path to model
            logging.info("=====Running CodeLLama-34B-V2========")

            # Check if CUDA (GPU) is available 
            if torch.cuda.is_available():
                    # Get the number of available GPUs
                    num_gpus = torch.cuda.device_count()
                    logging.info(f"Number of available GPUs: {num_gpus}")
                    # Iterate through available GPUs and print information about each
                    for i in range(num_gpus):
                        gpu = torch.cuda.get_device_name(i)
                        gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1e9  # in GB
                        logging.info(f"GPU,Total Memory: {gpu},{gpu_memory}")
            else:
                    logging.info("No GPU available. Using CPU.")

            
            # Define the tokenizer of python generator module
            self.python_tokenizer = AutoTokenizer.from_pretrained(local_dir)

            
            # Define the model pipeline of the python generator module
            self.python_pipeline = transformers.pipeline(
            "text-generation",
            model=local_dir,
            torch_dtype=torch.float32,
            device_map="auto",
        
            )


        if self.python_model =='code_llama34b_pythonV1' :

            # Huggingface login
            login(token=huggingface_token,new_session=False)  

            repo = "Phind/Phind-CodeLlama-34B-Python-v1"

            cache_dir = os.environ['CODELLAMA_34B_PYTHONV1_CACHE_DIR']
            local_dir = os.environ['CODELLAMA_34B_PYTHONV1_LOCAL_DIR']
          

            snapshot_download(repo_id=repo,cache_dir=cache_dir,local_dir=local_dir,local_dir_use_symlinks=True)

            # Path to model
            logging.info("=====Running CodeLLama-34B-Python-V1========")

            # Check if CUDA (GPU) is available 
            if torch.cuda.is_available():
                    # Get the number of available GPUs
                    num_gpus = torch.cuda.device_count()
                    logging.info(f"Number of available GPUs: {num_gpus}")
                    # Iterate through available GPUs and print information about each
                    for i in range(num_gpus):
                        gpu = torch.cuda.get_device_name(i)
                        gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1e9  # in GB
                        logging.info(f"GPU,Total Memory: {gpu},{gpu_memory}")
            else:
                    logging.info("No GPU available. Using CPU.")

            # Define the tokenizer of python generator module
            self.python_tokenizer = AutoTokenizer.from_pretrained(local_dir)

            
            # Define the model pipeline of the python generator module
            self.python_pipeline = transformers.pipeline(
            "text-generation",
            model=local_dir,
            torch_dtype=torch.float32,
            device_map="auto",
        
            )

        
        if self.python_model == 'wizardcoder_34B':
            
            # Huggingface login
            login(token=huggingface_token,new_session=False)  
            repo = "WizardLM/WizardCoder-Python-34B-V1.0"

            
            cache_dir = os.environ['WIZARDCODER_34B_PYTHON_CACHE_DIR']
            local_dir = os.environ['WIZARDCODER_34B_PYTHON_LOCAL_DIR']
          
        

            snapshot_download(repo_id=repo,cache_dir=cache_dir,local_dir=local_dir,local_dir_use_symlinks=True)

            # Path to model
            logging.info("=====Running Wizard-Coder-34B========")

            # Check if CUDA (GPU) is available 
            if torch.cuda.is_available():
                    # Get the number of available GPUs
                    num_gpus = torch.cuda.device_count()
                    logging.info(f"Number of available GPUs: {num_gpus}")
                    # Iterate through available GPUs and print information about each
                    for i in range(num_gpus):
                        gpu = torch.cuda.get_device_name(i)
                        gpu_memory = torch.cuda.get_device_properties(i).total_memory / 1e9  # in GB
                        logging.info(f"GPU,Total Memory: {gpu},{gpu_memory}")
            else:
                    logging.info("No GPU available. Using CPU.")

            
            # Define the tokenizer of python generator module
            self.python_tokenizer = AutoTokenizer.from_pretrained(local_dir)

            # Define the model 
            self.model_code = AutoModelForCausalLM.from_pretrained(local_dir)
            

    def load_data(self):
        
      
        if self.dataset == "AQUA":
            
            # Load the JSON data into a list of dictionaries
            examples = read_jsonl_file(os.environ['TEST_AQUA_DATA_FILE_PATH'])
            logging.info(f"{examples[0]}")
            logging.info(f"{len(examples)}")
            logging.info(f"{type(examples)}")
        
        elif self.dataset == "MMLU":
            # Load the JSON data into a list of dictionaries
            examples = read_jsonl_file(os.environ['TEST_MMLU_DATA_FILE_PATH'])
            logging.info(f"{examples[0]}")
            logging.info(f"{len(examples)}")
            logging.info(f"{type(examples)}")

        elif self.dataset == "GSM":
            examples = read_jsonl_file(os.environ['TEST_GSM8K_DATA_FILE_PATH'])
            logging.info(f"{examples[0]}")
            logging.info(f"{len(examples)}")
            logging.info(f"{type(examples)}")
          

        else:    # MATH dataset 
            
            if self.data_file == 'yes':
                examples = read_jsonl_file(os.environ['MATH_DATA_FILE_PATH'])
            else:    
                examples = read_jsonl_file(os.environ['SHUFFLED_MATH_DATA_FILE_PATH'])


        self.len_examples = len(examples)
        # limit the number of test examples
        if self.test_number > 0:
            if self.test_number < self.len_examples:
                examples = examples[:self.test_number]
        
        return examples


    def get_question_text(self):
        
        if "question_text" in self.cache:
            return self.cache["question_text"] 
        
        # question text
        question = self.cache["example"]["problem"]
        question_text = f"{question}\n\n"
        self.cache["question_text"] = question_text
        return question_text

    def get_metadata(self):
        
        if "metadata" in self.cache:
            return self.cache["metadata"] 
        # extract metadata
        metadata = {}
        example = self.cache["example"]
        try:
            metadata["topic"] = example["type"]
        except:
            metadata["topic"] = example["subject"]

        metadata["level"] = example["level"]
        self.cache["metadata"] = metadata
        return metadata

    def build_prompt_for_policy(self):
        # get the example
        question_text = self.get_question_text()
        
        # build the prompt
        demo_prompt = prompt_policy.prompt.strip() # demo prompt
        
        #test_prompt = f"Question: {question_text}\n\nMetadata: {metadata}\n\nModules: " # test prompt
        
        try:
            typ = str(self.cache["example"]["type"])
        except:
            typ = str(self.cache["example"]["subject"])

        lvl = str(self.cache["example"]["level"])

        test_prompt = f"Question: {question_text}\n\nMathematics Problem Type:{typ}\nLevel of Problem:{lvl}\nThought:"
        full_prompt = demo_prompt + "\n\n" + test_prompt  # full prompt

        return test_prompt, full_prompt

    def predict_modules(self):
        # get the module input
        test_prompt, full_prompt = self.build_prompt_for_policy()
       
        messages=[
            {"role": "user", "content": full_prompt},
        ]
        
        # execute the module
     
        modules = get_chat_response(messages=messages, temperature = self.policy_temperature, max_tokens=self.policy_max_tokens)
        logging.info(f"Response by planner: {modules}")
            
        # Get part starting with '['
        try:
            index = modules.index('[')
            modules = modules[index:]

        except:
            modules = '''['solution_generator']'''

        modules = self.update_modules(modules)

        logging.info(f"Modules selected by planner: {modules}")

        # update the cache
        self.cache["modules:input"] = test_prompt
        self.cache["modules:output"] = modules
        

        return modules

    def update_modules(self, _modules):
        
        # default modules
        default_end_modules = ["solution_generator"]
       
        try:
            
            logging.info(f"Modules before eval {_modules}")
            modules = eval(_modules.lower().strip())
            logging.info(f"Modules after eval: {modules}")
            
            assert modules[-1:] == default_end_modules
               
        except:

            modules = default_end_modules

        return modules
    

    def call_answer_cleaner(self, q, res):
        res = str(res)
        full_prompt = f"I called Wolfram alpha API using {q} and it gave me this answer as a dictionary object.\n {res}\n.Can you get the answer for me from this object?"
        
        messages=[
            {"role": "user", "content": full_prompt},
        ]

        if self.wolfram_model == 'text_davinci_003':
            answer = get_textdavinci003_response(full_prompt,temperature=0.5, max_tokens=500)
            
        elif self.wolfram_model == 'gemini':
            answer = get_gemini_response(full_prompt)      
            
        else:
                answer = get_chat_response(messages = messages,temperature = 0.5, max_tokens=256)
                
        return answer
    
    
    def remove_backticks(self,input_str):
        if input_str.startswith("`") and input_str.endswith("`"):
            # String is enclosed with "`" characters
            return input_str[1:-1]  # Remove the first and last characters
        else:
            # String is not enclosed with "`" characters
            return input_str

    
    def wolfram_alpha_search(self):
        
        app_id = os.environ["WOLFRAM_ALPHA_APPID"] 

        # get the example
        question_text = self.get_question_text()
        response = self.cache["response"] if "response" in self.cache else ""
        
        if self.dataset == "AQUA":
            demo_prompt = prompt_walpha_context_withthought.prompt_AQUA.strip()
        elif self.dataset == "MMLU":
            demo_prompt = prompt_walpha_context_withthought.prompt_MMLU.strip() 
        elif self.dataset == "GSM":
            demo_prompt = prompt_walpha_context_withthought.prompt_GSM.strip() 
        else:
            demo_prompt = prompt_walpha_context_withthought.prompt.strip()
        
        try:
            ind = (self.modules).index('query_generator')
        except:  
            ind = None

        if ind!=None:
            mods = (self.modules)[:ind]
            mods = ' '.join(mods)
        else:
            mods = ""    
        
        if response != "" and mods!="":
            test_prompt = f"Question:{question_text}\nModules used till now:[{mods}]\n{response}\nThought:"
        else:
            test_prompt = f"Question: {question_text}\nThought:"


        # full prompt
        full_prompt = demo_prompt + "\n" + test_prompt
        
        messages=[
            {"role": "user", "content": full_prompt},
        ]
        
        tries = 0
        answer_walpha = None
        q=None
        
        while(tries<3):
            # execute the module
            
            if self.wolfram_model == 'text_davinci_003':
                query = get_textdavinci003_response(full_prompt,temperature=0.5, max_tokens=600)
                
            elif self.wolfram_model == 'gemini':
                query = get_gemini_response(full_prompt) 
            
            else:
                query = get_chat_response(messages = messages,temperature = 0.5, max_tokens=600)
                
           
            tries+=1
            
            # Check if we get the right format 
            if query.find("Final Query:") == -1 or query.find("Final Query:") is None:
                continue
            else:
                
                # Call the Wolfram Alpha API
                client = wolframalpha.Client(app_id)
                
                # Extract the thought 
                try:
                    i2 = query.find("Answer:")
                    thought = query[:i2]
                except:
                    thought = ""    
                
                index = query.find("Final Query:") + len("Final Query:") 
                q = query[index:]
                q = self.remove_backticks(q)
                
                
                try: 
                    res = client.query(q)
                except:
                    logging.error("Error 403")
                    continue   
                
                #logging.info(f"{res}")
                 # Got res
                
                if res['@success'] == True:
                    answer_walpha = self.call_answer_cleaner(q,res)
                    break
                else:
                    logging.info(f"\nSuccess is False {str(tries)}")
                    answer_walpha = None
                    continue
                   
                
        if  answer_walpha!= "" and answer_walpha is not None:
            response += f"\nWolfram Thought:{thought}\nQuery Generator: {q}\n Wolfram_Alpha response:: {answer_walpha}\n"
            response = response.strip()
       
        
        # update the cache
        self.cache["query"] = q
        self.cache["response"] = response
        self.cache["query_generator:input"] = test_prompt
        self.cache["query_generator:output"] = query
        self.cache["wolfram_alpha_search:input"]  = q
        self.cache["wolfram_alpha_search:output"] = answer_walpha
        return q, answer_walpha
    
   
        
    def get_wiki_summary_(self,query):
        import wikipedia
        page = self.get_closest_wikipage(query)
        
        if page == None:
            return ""
        
        summary = page.summary
        summary = summary.split(".")
        
        return summary[:6]
      
    def get_closest_wikipage(query):
        
        import wikipedia
        try: 
                wiki_page = wikipedia.page(query)
                return wiki_page
        except wikipedia.exceptions.DisambiguationError as e:
                wiki_page = wikipedia.page(e.options[0]) 
                return wiki_page
        except wikipedia.exceptions.PageError as e:
                return None  
    
    def wikipedia_search(self):
        
        question_text = self.get_question_text()
        
        # Wiki query
        wiki_query = self.cache["query"] if "query" in self.cache else None
        
        # Response of the pipeline till now 
        response = self.cache["response"] if "response" in self.cache else ""

        # execute the module (call the Bing Search API and get the responses)
        if wiki_query != None and wiki_query != "":
            result = self.get_wiki_summary_(wiki_query)
        else:
            result = None
        

        if len(result) > 0 and result != "" and result!=None:
            response += f"\n\n Wikipedia Search response: {result}"
            response = response.strip()

        # update the cache
        self.cache["response"] = response
        self.cache["wiki_search:input"] = wiki_query
        self.cache["wiki_search:output"] = result
        return wiki_query, result
    

    def knowledge_retrieval(self):
        # get the example
        question_text = self.get_question_text()
        
        # Get the response till now 
        response = self.cache["response"] if "response" in self.cache else ""

        # build the prompt
        if self.dataset == "AQUA":
           demo_prompt = prompt_kr.prompt_AQUA.strip() 
        elif self.dataset == "GSM":
           demo_prompt = prompt_kr.prompt_GSM.strip()  
        elif self.dataset == "MMLU":
           demo_prompt = prompt_kr.prompt_MMLU.strip()        
        else:
           demo_prompt = prompt_kr.prompt.strip()   # demo prompt

        if response != "":
            test_prompt = f"Question: {question_text}\n\n{response}\n\nKnowledge Retrieval:\n"
        else:
            test_prompt = f"Question: {question_text}\n\nKnowledge Retrieval:\n" # test prompt
        
        full_prompt = demo_prompt + "\n\n" + test_prompt # full prompt

        messages=[
            {"role": "user", "content": full_prompt},
        ]

        # execute the module
        if  self.knowledge_model=='no':
            
            knowledge = get_chat_response(messages = messages,temperature=self.kr_temperature, max_tokens=self.kr_max_tokens)
    
        elif self.knowledge_model=='text_davinci_002':
            knowledge = get_textdavinci002_response(prompt=full_prompt,temperature=self.kr_temperature)
        
        elif self.knowledge_model=='text_davinci_003':
            knowledge = get_textdavinci003_response(prompt=full_prompt,temperature=self.kr_temperature)
        
        elif self.knowledge_model == "llama2_13b":
            knowledge = get_llama_response(self.knowledge_tokenizer, self.knowledge_pipeline, prompt=full_prompt,temperature=self.kr_temperature)
        elif self.knowledge_model == "llama2_7b":
            knowledge = get_llama_13bresponse(self.knowledge_tokenizer, self.knowledge_pipeline, prompt=full_prompt,temperature=self.kr_temperature)

        # update the response cache
        if knowledge != "" and knowledge != None:
            response += f"\n\nKnowledge Retrieval:\n{knowledge}"
            response = response.strip()

        # update the cache
        self.cache["response"] = response
        self.cache["knowledge_retrieval:input"] = test_prompt
        self.cache["knowledge_retrieval:output"] = knowledge
        return test_prompt, knowledge
    
    
    def program_generator(self):
       
        test_prompt, full_prompt = self.build_prompt_for_pg()
        

        messages=[
            {"role": "user", "content": full_prompt},
        ]
        
        
        # Get the response till now 
        response = self.cache["response"] if "response" in self.cache else ""
        
        # execute the module
        if  self.python_model=='no':
            program = get_chat_response(messages = messages,temperature = self.pg_temperature, max_tokens=self.pg_max_tokens)

        elif self.python_model=='gemini':
            program = get_gemini_response(full_prompt)
        
        elif self.python_model=='code_davinci002':
            program = get_codex_response(prompt=full_prompt,temperature=self.pg_temperature)

        elif self.python_model=='code_llama7b_python':   
            program = get_codellama_response(self.python_tokenizer,self.python_pipeline,prompt=full_prompt,temperature=self.pg_temperature)

        elif self.python_model=='code_llama13b_python':   
            program = get_codellama_response(self.python_tokenizer,self.python_pipeline,prompt=full_prompt,temperature=self.pg_temperature)
        
        elif self.python_model=='code_llama34b':   
            program = get_codellama_response(self.python_tokenizer,self.python_pipeline,prompt=full_prompt,temperature=self.pg_temperature)
        
        elif self.python_model=='code_llama34b_pythonV1':   
            program = get_codellama_response(self.python_tokenizer,self.python_pipeline,prompt=full_prompt,temperature=self.pg_temperature)
        
        elif self.python_model=='wizardcoder_34B':
             program = get_wizard_coder_response(self.python_tokenizer,self.model_code,prompt=full_prompt,temperature=self.pg_temperature)
        
        
        program= program.strip('"')
        
        # update the response cache
        # update the cache
        self.cache["response"] = response
        self.cache["program"] = program

        self.cache["program_generator:input"] = test_prompt
        self.cache["program_generator:output"] = program
        
        return test_prompt, program
    

    def code_fixer(self,error_program,error_message):
        demo_prompt = prompt_codefixer.prompt
        test_prompt = f"\nIncorrect Python code:\n{error_program}\nError message:{error_message}\n"
        full_prompt = demo_prompt + test_prompt
        system_message = """
        You are an AI assistant skilled in Python programming and debugging. Help users identify errors in their Python code and output the new correct python code. Make sure to optimize the corrected code and follow best practices for writing clean, efficient, and maintainable Python code.
        Here are some common errors that the input python code may have:
        (1) Use of undefined functions or making up function names.
        (2) Forgetting to declare symbols or variables in the python code.
        (3) Use of classes or methods without properly importing required libraries like Sympy, math, etc.
        (4) Wrong way of handling mathematical objects specially in the Sympy library, use of invalid operators with class objects.
        (5) Code has an abrupt end, or code contains natural language sentences instead of python syntax.
        """
        
        code_fixer_response = get_chat_response_code(full_prompt,temperature = 0.7, max_tokens=500,system_mess=system_message)
        logging.info(f"Code-fixer response {code_fixer_response}")
        
        # Parse output to get new program
        try:
            idx1 = code_fixer_response.index("Corrected Python Code:")
        except:
            return error_program,None
        try:
            idx2 = code_fixer_response.index("Errors fixed:")
        except:
            return error_program,None
        
        new_program = code_fixer_response[idx1+len("Corrected Python Code:"):idx2]
        errors_fixed = code_fixer_response[idx2+len("Errors fixed:"):]
        return new_program,errors_fixed



    def python_generator_refine_executor(self):
        
        if self.model =='kr_pg_sg':
               test_prompt, full_prompt = self.build_prompt_for_kr_pg()
        else:
               test_prompt, full_prompt = self.build_prompt_for_pg()
        
        messages=[
               {"role": "user", "content": full_prompt},
            ]
        # Get the response till now
        response = self.cache["response"] if "response" in self.cache else ""
        max_iterations=3   # Maximum no of attempts to correct the code
        count=0
        errors_fixed = None
        
        while True and count<max_iterations:
            copy_messages = messages.copy()
            count=count+1
            if count>1:
                
                # Extract the program and error message of last round
                error_program = self.cache["refine_round"+str(count-1)]['code']
                error_message = self.cache["refine_round"+str(count-1)]['error']
                
                # Feed the error message and program to an independent code_fixer module
                # Make changes to the code using error message
                program,errors_fixed = self.code_fixer(error_program,error_message)
            
            if count<=1:
                # Generate code 1st time
                if  self.python_model == 'no':
                    program = get_chat_response(messages = copy_messages,temperature = self.pg_temperature, max_tokens=self.pg_max_tokens)
                
                elif self.python_model == 'code_llama34b':
                    program = get_codellama_response(self.python_tokenizer,self.python_pipeline,prompt=copy_messages[0]["content"],temperature=self.pg_temperature)
                
                elif self.python_model == 'code_llama34b_pythonV1':
                    program = get_codellama_response(self.python_tokenizer,self.python_pipeline,prompt=copy_messages[0]["content"],temperature=self.pg_temperature)
                
                elif self.python_model=='wizardcoder_34B':
                    program = get_wizard_coder_response(self.python_tokenizer,self.model_code,prompt=copy_messages[0]["content"],temperature=self.pg_temperature)
            
            # Check if the code is executable
            program = program.strip('"')
            output, error_message = safe_execute(program)
            
            if error_message == None and output!="" and output!=None:
               response += f"\nPython generator:\n{program}"
               response += f"\nPython output:\n{output}"
               response = response.strip()
               self.cache["refine_round"+str(count)] ={'code':program, 'error':error_message, 'output':output,'errors_fixed':errors_fixed}
               
               '''
               print("Code\n",self.cache["refine_round"+str(count)]['code'])
               print("Error\n",self.cache["refine_round"+str(count)]['error'])
               print("Output\n",self.cache["refine_round"+str(count)]['output'])
               print("Errors fixed\n",self.cache["refine_round"+str(count)]['errors_fixed'])
               '''
               break
            
            else:
               '''
               # Add the error message and the program to the messages context
                messages[0]["content"] += f"\n{program}"
                messages[0]["content"] += f"\nOutput:{output}"
                messages[0]["content"] += f"\nError message:\n{error_message}"
               '''
               # Store the code for this round
               self.cache["refine_round"+str(count)] ={'code':program, 'error':error_message, 'output':output,'errors_fixed':errors_fixed}
               
               '''
               print("Code\n",self.cache["refine_round"+str(count)]['code'])
               print("Error\n",self.cache["refine_round"+str(count)]['error'])
               print("Output\n",self.cache["refine_round"+str(count)]['output'])
               print("Errors fixed\n",self.cache["refine_round"+str(count)]['errors_fixed'])
               '''
        
        # update the cache
        self.cache["response"] = response
        self.cache["program"] = program
        # Store the messages of refine
        self.cache["messages_refine"] = messages
        # Store the no of steps of refinement
        self.cache["num_refines"] = count
        self.cache["program_generator:input"] = test_prompt
        self.cache["program_generator:output"] = program
        return test_prompt, program

        
   
    def program_executor(self):
        
        if "program" in self.cache:
            program = self.cache["program"]
        else:
            return None, False
        
        # Get the response till now 
        response = self.cache["response"] if "response" in self.cache else ""
        
        # execute the module
        ans, error_message = safe_execute(program)

        # update the response cache
        if ans != "" and ans!= None:
            response += f"\n\nPython generator:\n{program}"
            response += f"\n\nPython output:\n{ans}"
            response = response.strip()
        
        '''elif error_message!=None:

            if self.cache['refine']!='no':
               # Refine the code using error message 
               response += f"\n\nPython error message:\n{error_message}"
               response = response.strip()

               self.refine_python_code(program,error_message) 
        '''       

        # update the cache
        self.cache['response'] = response 
        self.cache["program_executor:output"] = ans

        return program, ans
    

    def solution_generator(self):
        # get the module input
        response = self.cache["response"] if "response" in self.cache else ""

        if self.model == "cot":
            test_prompt, full_prompt = self.build_prompt_for_sg_cot()

        elif self.model=='kr_walpha_sg' or  self.model=='sg' or self.model =="pg_sg" or self.model=='walpha_sg' or self.model=='walpha_pg_sg' or self.model == 'pg_walpha_sg' or self.model =='bing_walpha_sg' or self.model == 'walpha_bing_sg' or self.model =='bing_pg_walpha_sg' or self.model == 'kr_pg_sg' or self.model =='kr_sg' or self.model=='planner' or self.model == 'bing_sg' or self.model == 'bing_pg_sg' or self.model == 'pg_bing_sg':
            test_prompt, full_prompt = self.build_prompt_for_kr_walpha_sg()

        
        messages=[
            {"role": "user", "content": full_prompt},
        ]

        # excute the module
        success = False
        patience = self.sg_patience
        count = 0
        while count < patience and not success:
            if self.sg_temperature < 0.1 and count > 0:
                _temperature = min(self.sg_temperature + 0.1, 1.0)
            else:
                _temperature = self.sg_temperature
            
            
            if self.sg_model == 'text_davinci_003':  # Check text-davinci-003
                solution = get_textdavinci003_response(full_prompt,temperature=_temperature, max_tokens=self.sg_max_tokens)
            
            elif self.sg_model == 'gemini':
                solution = get_gemini_response(full_prompt)    
            
            else:
                solution = get_chat_response(messages=messages, temperature=_temperature, max_tokens=self.sg_max_tokens)

           
            #pattern = re.compile(r"[Tt]he answer is ([A-Z])")      # "The answer is XXXXX.",
            #res = pattern.findall(solution)
            
            if self.dataset == "AQUA":
                pattern = re.compile(r"[Tt]he answer is [A-Z]")      # "The answer is X.",
                res = pattern.findall(solution)
                if res:
                    success=True

            elif self.dataset == "GSM":
                pattern = re.compile(r"#### (\-?[0-9\.\,]+)")      # "The answer is ####.",
                res = pattern.findall(solution)
                if res:
                    success=True
            
            elif self.dataset == "MMLU":
                pattern = re.compile(r"#### (\-?[A-D])")      # "The answer is ####.",
                res = pattern.findall(solution)
                if res:
                    success=True        

            else:
                if "boxed" in solution: # For MATH format
                   success = True
            
            
            count += 1
        
        response = response + "\nSolution:\n" + solution
        # update the cache
        self.cache["response"] = response
        self.cache["solution"] = solution
        self.cache["solution_generator:input"] = test_prompt
        self.cache["solution_generator:output"] = solution
        return test_prompt, solution
    
    
    def bing_search(self):
        
        # Set up Bing credentials
        endpoint =  os.environ['BING_API_ENDPOINT']
        count = os.environ['BING_API_COUNT']
        bing_api_key = os.environ['BING_API_KEY']

        
        # Get the question and context
        question_text = self.get_question_text()
        response = self.cache["response"] if "response" in self.cache else ""
        

        try:
            ind = (self.modules).find('bing_search')
        except:  
            ind = None

        if ind!=None:
            mods = (self.modules)[:ind]
            mods = ' '.join(mods)
        else:
            mods = ""    


        # Use LLM to set up query based on question and context (response)
        if self.dataset == "AQUA":
           demo_prompt = prompt_bing_query.prompt_AQUA
        elif self.dataset == "MMLU":
           demo_prompt = prompt_bing_query.prompt_MMLU
        else:
           demo_prompt = prompt_bing_query.prompt
        
        if response != "" and mods!="":
            test_prompt = f"Question:{question_text}\nModules used till now:[{mods}]\n{response}\nThought:"
        else:
            test_prompt = f"Question: {question_text}\nThought:"
        
        full_prompt = demo_prompt + test_prompt
        
        messages=[
            {"role": "user", "content": full_prompt},
        ]

        # Query for Bing concept search using LLM-generated query
       
        num_tries = 3
        f = 0
        while(f<num_tries):
            f+=1
            if self.bing_model == 'text_davinci_003': # Check text-davinci-003
                query_output = get_textdavinci003_response(full_prompt,temperature=0.5, max_tokens=500)
            else:    
                query_output = get_chat_response(messages, temperature=0.5, max_tokens=500)
            
            if query_output.find("Query:")!= -1:
                break
       
        
        # Extract the queries and call api 
        query1= question_text  # Query for similar questions search is the input question
        ind = query_output.find("Query:")
        query2= query_output[ind+len("Query:"):]
        
        result1 = call_bing_search(endpoint, bing_api_key, query1, count)

        # execute the module (call the Bing Search API and get the responses for query2)
        if query2 != None and query2 != "":
            result2 = call_bing_search(endpoint, bing_api_key, query2, count)
        else:
            result2 = None
        
        
        # Get all the response snippets retrieved
        responses1 = parse_bing_result(result1)
        responses2 = parse_bing_result(result2)
        
        logging.info(f"Bing response 1 {responses1}")
        logging.info(f"Bing response 2 {responses2}")

        
        # Use LLM to extract useful information from responses
        if self.dataset == "AQUA":
            demo_prompt_extract = prompt_bing_answer_extractor.prompt_AQUA
        elif self.dataset == "MMLU":
            demo_prompt_extract = prompt_bing_answer_extractor.prompt_MMLU 
        else:   
            demo_prompt_extract = prompt_bing_answer_extractor.prompt

        test_prompt_extract1 = f"Question:{question_text}\nBing Search API result:{responses1}\nUseful_information:\n"
        test_prompt_extract2= f"Question:{question_text}\nBing Search API result:{responses2}\nUseful_information:\n"

        full_prompt_extract1 = demo_prompt_extract + test_prompt_extract1
        full_prompt_extract2 = demo_prompt_extract + test_prompt_extract2

        
        messages1=[
            {"role": "user", "content": full_prompt_extract1},
        ]

       
        if self.bing_model == 'text_davinci_003':  # Check text-davinci-003
            info_bing1 = get_textdavinci003_response(full_prompt_extract1,temperature=0.5, max_tokens=500)
        else:
            info_bing1 = get_chat_response(messages1, temperature=0.5, max_tokens=500)
       
            
        messages2=[
            {"role": "user", "content": full_prompt_extract2},
        ]

     
        if self.bing_model == 'text_davinci_003': # Check text-davinci-003
            info_bing2 = get_textdavinci003_response(full_prompt_extract2,temperature=0.5, max_tokens=500)
        else:
            info_bing2 = get_chat_response(messages2, temperature=0.5, max_tokens=500)
       
        
        # Concatenate bing responses from query 'question' and 'query2' using context
        
        info_bing = info_bing1 + "\n" + info_bing2
        
        if  info_bing!="" and info_bing is not None:
            response += f"\n\nBing search response:\n{info_bing}"
            response = response.strip()

        # update the cache
        self.cache["response"] = response
        self.cache["bing_query2"] = query2
        self.cache["bing_query2_output"] = responses2
        self.cache["bing_query1"] = query1
        self.cache["bing_query1_output"] = responses1
        self.cache["bing_search:input"] = query_output
        self.cache["bing_search:output"] = info_bing
        return query_output, info_bing

    
    def build_prompt_for_pot(self):
        
        question_text = self.get_question_text()
        
        #metadata = self.get_metadata()
        
        response = self.cache["response"] if "response" in self.cache else ""

        # build the prompt
        if self.dataset == "AQUA":
           demo_prompt = prompt_pot.prompt_pot_AQUA.strip() 
        else:   
           demo_prompt = prompt_pot.prompt_pot.strip() 
        
        if response != "":
            test_prompt = f"Question: {question_text}\n\n{response}\n\nSolution: "
        else:
            test_prompt = f"Question: {question_text}\n\nSolution: "
        
        full_prompt = demo_prompt + "\n\n" + test_prompt # full prompt
        return test_prompt, full_prompt
    
    
    def build_prompt_for_kr_walpha_sg(self):
        
        question_text = self.get_question_text()
        #metadata = self.get_metadata()
        response = self.cache["response"] if "response" in self.cache else ""
        
        #logging.info(f"Response context: {response}")
        flag = response.find("Solution:")
        if flag!=-1:
            response = response[:flag]
        #logging.info(f"After removing Solution - Response context: {response}")


        # build the prompt
        if self.dataset == "AQUA" and self.model=='sg':
            demo_prompt = prompt_walpha_kr_sg.prompt_AQUA_new_sg.strip()
        
        elif self.dataset == "AQUA":
            demo_prompt = prompt_walpha_kr_sg.prompt_AQUA_new_walpha.strip()
        
        elif self.dataset == "GSM" and (self.model == 'walpha_sg' or self.model == 'pg_walpha_sg' or self.model == 'walpha_pg_sg'):
            demo_prompt = prompt_walpha_kr_sg.prompt_GSM_new_walpha.strip()

        elif self.dataset == "GSM" and self.model == 'sg':
             demo_prompt = prompt_walpha_kr_sg.prompt_GSM_new_sg.strip()

        elif self.dataset == "GSM" and self.model == 'pg_sg':
            demo_prompt = prompt_walpha_kr_sg.prompt_GSM_new.strip()
        elif self.dataset == "MMLU" :
            demo_prompt = prompt_walpha_kr_sg.prompt_MMLU.strip()    
        else:
            demo_prompt = prompt_walpha_kr_sg.prompt.strip() 
        


        if response != "":
            test_prompt = f"Question: {question_text}\n\n{response}\n\nSolution: "
        else:
            test_prompt = f"Question: {question_text}\n\nSolution: "
        
        full_prompt = demo_prompt + "\n\n" + test_prompt # full prompt

        return test_prompt, full_prompt

    def build_prompt_for_kr_sg(self):
        
        question_text = self.get_question_text()
        
        #metadata = self.get_metadata()
        
        response = self.cache["response"] if "response" in self.cache else ""

        # build the prompt
        demo_prompt = prompt_kr_sg.prompt.strip() # WARNING: this is the prompt for kr_sg
        
        if response != "":
            test_prompt = f"Question: {question_text}\n\n{response}\n\nSolution: "
        else:
            test_prompt = f"Question: {question_text}\n\nSolution: "
        
        full_prompt = demo_prompt + "\n\n" + test_prompt # full prompt
        return test_prompt, full_prompt



     
    def build_prompt_for_pg(self):
        
        question = self.cache["example"]["problem"]
        response = self.cache["response"] if "response" in self.cache else ""
        try:
            ind = (self.modules).index('program_generator')
        except:  
            ind = (self.modules).index("python_generator_refine_executor")  

        mods = (self.modules)[:ind]
        mods = ' '.join(mods)
        if self.extra_python_libraries == 'no':
            if self.dataset == "AQUA":
              demo_prompt = prompt_pg.prompt_AQUA_new.strip()
            elif self.dataset == "MMLU":
              demo_prompt = prompt_pg.prompt_MMLU.strip()  
            elif  self.dataset == "GSM":
              demo_prompt = prompt_pg.prompt_GSM.strip() 
            else:
              demo_prompt = prompt_pg.prompt.strip()
        
        elif self.extra_python_libraries == 'yes':
            if self.dataset == "AQUA":
              demo_prompt = prompt_pg.prompt_AQUA.strip()
            else:
              demo_prompt = prompt_pg.prompt2.strip()

        if self.extra_python_libraries=='no' and self.dataset=="MATH":
            test_prompt = f"Question:{question}\nModules used till now:[{mods}]\n{response}\n\nPython generator:\n# Python Code, print answer. Also Output all the relevant objects in the intermediate steps of the python code. Make sure that the first line of the code is always 'from sympy import *'"
        
        elif self.extra_python_libraries=='no' and self.dataset=="GSM":
            test_prompt = f"Question:{question}\nModules used till now:[{mods}]\n{response}\n\nPython generator:\n# Python Code, print answer. Also Output all the relevant objects in the intermediate steps of the python code."

        else:
            test_prompt = f"Question:{question}\nModules used till now:[{mods}]\n{response}\nPython generator:\n# Python Code, print answer. Also Output all the relevant objects in the intermediate steps of the python code."

        full_prompt = demo_prompt + "\n\n" + test_prompt
        return test_prompt, full_prompt


    
    def build_prompt_for_kr_pg(self):
        
        question_text = self.get_question_text()
        
        #metadata = self.get_metadata()
        
        response = self.cache["response"] if "response" in self.cache else ""

        # build the prompt
        demo_prompt = prompt_kr_pg.prompt.strip()  # WARNING: this is the prompt for kr_pg_sg
        
        if response != "":
            test_prompt = f"Question: {question_text}\n\n{response}\n\nPython code:\n# Python Code, print answer. Also Output all the relevant objects in the intermediate steps of the python code.Make sure that the first line of the code is always 'from sympy import *' \n"
        else:
            test_prompt = f"Question: {question_text}\n\nPython code:\n# Python Code, print answer. Also Output all the relevant objects in the intermediate steps of the python code.Make sure that the first line of the code is always 'from sympy import *' \n "
        
        full_prompt = demo_prompt + "\n\n" + test_prompt # full prompt
        return test_prompt, full_prompt


    def build_prompt_for_kr_pg_sg (self):
        
        question_text = self.get_question_text()
        #metadata = self.get_metadata()
        response = self.cache["response"] if "response" in self.cache else ""

        # build the prompt
        if self.dataset == "AQUA":
           demo_prompt = prompt_kr_pg_sg.prompt_AQUA.strip()
        else:   
           demo_prompt = prompt_kr_pg_sg.prompt.strip() # WARNING: this is the prompt for kr_sg
        
        if response != "":
            test_prompt = f"Question: {question_text}\n\n{response}\n\nSolution: "
        else:
            test_prompt = f"Question: {question_text}\n\nSolution: "
        
        full_prompt = demo_prompt + "\n\n" + test_prompt # full prompt

        return test_prompt, full_prompt
    

    def build_prompt_for_sg_cot(self):

        question_text = self.get_question_text()
        #metadata = self.get_metadata()
        response = self.cache["response"] if "response" in self.cache else ""

        # build the prompt
        demo_prompt = prompt_for_cot.prompt.strip()        # WARNING: this is the prompt for cot
        
        if response != "":
            test_prompt = f"Question: {question_text}\n\n{response}\n\nSolution: "
        else:
            test_prompt = f"Question: {question_text}\n\nSolution: "
        
        full_prompt = demo_prompt + "\n\n" + test_prompt # full prompt

        return test_prompt, full_prompt







