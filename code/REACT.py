import sys
import json
import requests

import os
import openai

from dotenv import load_dotenv
load_dotenv(".env")

import langchain 
import time
import random
import openai
import func_timeout
import requests
import numpy as np
import logging
from typing import Union, Any
from math import isclose
from tqdm import tqdm

# Import Langchain libraries
from langchain import LLMChain
from langchain.chat_models import AzureChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

openai.api_type =  "azure"
openai.api_base = os.environ['OPENAI_API_BASE']
openai.api_version = os.environ['OPENAI_API_VERSION']
openai.api_key = os.environ['OPENAI_API_KEY']
openai.deployment_name = os.environ["OPENAI_DEPLOYMENT_NAME"]
openai.model_name = os.environ['MODEL_NAME']


# Initiate a connection to the LLM from Azure OpenAI Service via LangChain.
llm = AzureChatOpenAI(
    openai_api_key=openai.api_key,
    deployment_name=openai.deployment_name ,
    openai_api_version = openai.api_version,
    openai_api_base = openai.api_base ,
    model_name = openai.model_name, 
    temperature=0.5
)

# Wolfram Alpha
import wolframalpha

# Import prompts
from REACT_prompts import prompts_MATH_react,prompt_walpha_context_withthought_REACT,prompt_bing_query_REACT,prompt_bing_answer_extractor
from demos import prompt_codefixer


def build_prompt_for_kr_walpha_sg(question,context):
        
        # build the prompt
        demo_prompt = prompt_walpha_kr_sg.strip() # WARNING: this is the prompt for kr_sg
        
        if context!= "":
            test_prompt = f"Question: {question}\n\n{context}\n\nSolution: "
        else:
            test_prompt = f"Question: {question}\n\nSolution: "
        
        full_prompt = demo_prompt + "\n\n" + test_prompt # full prompt
        
        return test_prompt, full_prompt

              


def call_bing_search(endpoint, bing_api_key, query, count):
    
    headers = {'Ocp-Apim-Subscription-Key': bing_api_key}
    params = {"q": query, "textDecorations": True,
      "textFormat": "HTML", "count": count}
    
    try:
        response = requests.get(endpoint, headers=headers, params=params)

        #response.raise_for_status()
        resp_status = response.status_code
        
        if resp_status == 200:
            result = response.json()
            return result 
    except:
        pass
        
    return None

def parse_bing_result(result):
    responses = []
    try:
        value = result["webPages"]["value"]
    except:
        return responses

    for i in range(len(value)):
        snippet = value[i]['snippet'] if 'snippet' in value[i] else ""
        snippet = snippet.replace("<b>", "").replace("</b>", "").strip()
        if snippet != "":
            responses.append(snippet)
        
    return responses

from REACT_prompts import prompts_KR_react,prompts_PG_REACT,prompts_TC_REACT


# Read the jsonl file 
def read_jsonl_file(file_path):
    data = []
    import json
    with open(file_path, 'r') as file:
        for line in file:
            try:
              record = json.loads(line)
            except:
              print(line)    
            data.append(record)

    return data

def remove_boxed(s):
    left = "\\boxed{"
    try:
        assert s[:len(left)] == left
        assert s[-1] == "}"
        return s[len(left):-1]
    except:
        return None

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

def safe_execute(code_string: str, keys=None):

    import sys
    from io import StringIO
    import signal
    import time
    import re
    import matplotlib
    matplotlib.use('Agg')
    #code_string = re.sub(r'[\x00-\x1f]', '', code_string)

    #print("Code string:", code_string)
    #print("Original length of code string", len(code_string))

    # Code string after strip
    import codecs
    new_code_string = codecs.decode(code_string, 'unicode_escape')
    #print("Length of code string after conversion:", len(new_code_string))

    output = None
    error_message = None

    def timeout_handler(num, stack):
       print("Received SIGALRM")
       raise Exception("TLE")

    # Executing the code and capturing the output
    old_stdout = sys.stdout

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(10)

    try:
        # Redirect stdout and stderr to capture the output and error message
        sys.stdout = StringIO()
        

        # Execute the code
        exec(new_code_string,globals())

        # Get the captured output
        output = sys.stdout.getvalue()

    except Exception as e:
        error_message = str(e)
    
    # Reset alarm
    signal.alarm(0)

    # Restore the original stdout and stderr
    sys.stdout = old_stdout
   

    return output, error_message   

def remove_boxed(s):
    left = "\\boxed{"
    try:
        assert s[:len(left)] == left
        assert s[-1] == "}"
        return s[len(left):-1]
    except:
        return None

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

def get_chat_response(context,stop=None,temperature=0.5, max_tokens=256, n=1, patience=10, sleep_time=5,system_mess=None):
    
    from langchain.schema.messages import HumanMessage, SystemMessage
    import time 
    
    print("----Response starts-----")
    
    if system_mess is not None:
        try:
            if stop!=None:
                response = llm([SystemMessage(content=system_mess),HumanMessage(content=context)],max_tokens=max_tokens,temperature=temperature,stop=stop)
            else:
                response = llm([SystemMessage(content=system_mess),HumanMessage(content=context)],max_tokens=max_tokens,temperature=temperature)


        except:
            response = ""
    
    else:
        
        try:
            if stop!=None:
                response = llm([HumanMessage(content=context)],max_tokens=max_tokens,temperature=temperature,stop=stop)
            else:
                response = llm([HumanMessage(content=context)],max_tokens=max_tokens,temperature=temperature)


        except:
            response = ""

     
    print("----Response ends-----")

    try:
      print("---------Sleep starts----------")
      time.sleep(sleep_time)
      print("---------Sleep ends----------")
      return response.content
    
    except:
      print("---------Sleep starts----------")
      time.sleep(sleep_time)
      print("---------Sleep ends----------")
      return ""     
    
def text_generator(question,context):
    print("Inside text Chatgpt")
    prompt_text = prompts_TC_REACT.prompt
    input = prompt_text + "\nContext:\n" + context+ f"Task:{question}" +"\nOutput:\n"
    #print(input)
    output = get_chat_response(input)
    #print("Text output", output)
    cache["text LLM input"] = question
    cache["text LLM output"] = output

    output = "text_generator output: "+output
   
    return output,False


############### Definition of the tools ##################################
def code_fixer(error_program,error_message):
        
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
        
    
       
        #print("Full prompt ",test_prompt)

        code_fixer_response = get_chat_response(full_prompt,temperature = 0.5, max_tokens=500,system_mess=system_message)
        
        print("Code-fixer response",code_fixer_response)
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
        
def program_generator(question,context):
    
    print("Inside program generator")
    
    len=0
    errors_fixed = None
    max_iterations=3   
   
    prompt_pg = prompts_PG_REACT.prompt

    code = None
    error = None
    output = None

    while(len<max_iterations): 
        
        len+=1
        
        if len>1: 

            code,errors_fixed = code_fixer(code,error)
            code = code.strip('"')
            output, error = safe_execute(code)
            
            print("code"+str(len),code)
            print("error"+str(len),error)
            print("errors fixed"+str(len),errors_fixed)
            
            cache["python_code"+"_round"+str(len)] = code
            cache["code_errors"+"_round"+str(len)] = error
            cache["errorsfixed"+"_round"+str(len)] = errors_fixed

            
            if error==None:
               break

        if len<=1:
            code = get_chat_response(prompt_pg + "\nContext:\n" + context+ f"Task:{question}" +"\nPython code:\n",stop=["Observation:"])
           
            print("code"+str(len),code)
            print("error"+str(len),error)
            
            code = code.strip('"')
            output, error = safe_execute(code)
            
            cache["python_code"+"_round"+str(len)] = code
            cache["code_errors"+"_round"+str(len)] = error
            
            if error==None:
               break
    
    
    if output is not None and error==None:
        text = f"Python code:'{code}',Code Output:'{output}'"
    else:
        text = "Python code: The program_generator action did not return relevant results."    
    
    
    cache["python code question"] = question
    cache["final_python_code"] = code
    cache["final_code_errors"] = error
    
    return text, False


            
def knowledge_retrieval(query,context):
   
    print("Inside  Knowledge_retrieval")
    prompt_kr = prompts_KR_react.prompt
    knowledge = get_chat_response(prompt_kr + "\nQuery:\n"+ query + "\nKnowledge:\n")
    cache["LLM knowledge query"] = query
    cache["LLM knowledge answer"] = knowledge
    return knowledge,False

def call_answer_cleaner(q, res):
        res = str(res)
        full_prompt = f"I called Wolfram alpha API using {q} and it gave me this answer as a dictionary object.\n {res}\n.Can you get the answer for me from this object?"
        answer = get_chat_response(full_prompt,max_tokens=400)
        return answer

def remove_backticks(input_str):
        if input_str.startswith("`") and input_str.endswith("`"):
            # String is enclosed with "`" characters
            return input_str[1:-1]  # Remove the first and last characters
        else:
            # String is not enclosed with "`" characters
            return input_str

def wolframalpha_generator(question,context):
        
    
        print("In wolfram alpha")
        demo_prompt = prompt_walpha_context_withthought_REACT.prompt.strip()

        tries = 0
        answer_walpha = None
        q = None

        while(tries<3):
            
            #print(f"Try {tries}")
            # Execute the module
            query = get_chat_response(demo_prompt + "\nContext:\n" + context+ f"Task:{question}" +"\nThought:",stop=["Context:"],max_tokens=600)
            #print(query)
            print(f"Query {str(tries)}:",query)
            tries+=1
            
            idx = query.find("Final Query:")
            print("IDX",idx)

            # Check if we get the right format 
            if idx== -1 or idx is None:
                continue
            
            else:
                
                print("In API Call")

                # Call the API
                app_id = os.environ['WOLFRAM_ALPHA_APPID']
                
                client = wolframalpha.Client(app_id)
                
                index = query.find("Final Query:") + len("Final Query:") 
                q = query[index:]
                q = remove_backticks(q)
                #print(f"Extracted query {str(tries)}:",q)
                
                try: 
                    print(q)
                    res = client.query(q)
                    print("WA: q =",q)
                    print("WA res=",res)
                except:
                    print("Error 403")
                    continue   
              
                
                # Got res
                if res['@success'] == True:
                    answer_walpha = call_answer_cleaner(q,res)
                    #print(answer_walpha)
                    break
                else:
                    print(f"\nSuccess is False {str(tries)}")
                    answer_walpha = None
                    continue
                   
                
        if  answer_walpha!= "" and answer_walpha is not None:
            
            output= "Wolfram Alpha Query:" + str(q) + "Wolfram_Alpha response::" +str(answer_walpha) 
            print("Done Wolfram Alpha!")
            print(output)
            output= output.strip()
            cache["Wolfram Alpha query"]= q
            cache["Wolfram Alpha Answer"] = answer_walpha
            cache["Wolfram Alpha output object"] = res
            
            return output,False
          
        else:
            output= "Wolfram Alpha Query:" + str(q) + "Wolfram_Alpha response::" + "Wolfram Alpha cannot handle query."
            output= output.strip()
            return output,False

       
       

    
    

def bing_search(question,context):
        
       
        print("In Bing !")
        # Bing credentials
        endpoint = os.environ['BING_API_ENDPOINT']
        count = os.environ['BING_API_COUNT']
        bing_api_key = os.environ['BING_API_KEY']
        
        math_question_start = context.find("Question:")
        math_question_end = context.find("Type:")

        question_text = context[math_question_start +len("Question:"):math_question_end]
        print("Bing question text:", question_text)

        # Use LLM to set up query based on question and context (response)
        demo_prompt = prompt_bing_query_REACT.prompt
       
        while(True): # Continue till we get query
            query_output = get_chat_response(demo_prompt + "\nContext:\n" + context+ f"Task:{question}" +"\nThought:",stop=["Context:"], temperature=0.5, max_tokens=500)
            #print(query_output)
            if query_output.find("Query:")!= -1:
                break
        
        
        # Extract the queries and call api 
        query1= question_text
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
        
        print("Bing response 1",responses1)
        print("Bing response 2",responses2)

        
        # Use LLM to extract useful information from responses
        demo_prompt_extract = prompt_bing_answer_extractor.prompt
        test_prompt_extract1 = f"Question:{question_text}\nBing Search API result:{responses1}\nUseful_information:\n"
        test_prompt_extract2= f"Question:{question_text}\nBing Search API result:{responses2}\nUseful_information:\n"

        full_prompt_extract1 = demo_prompt_extract + test_prompt_extract1
        full_prompt_extract2 = demo_prompt_extract + test_prompt_extract2
        
        
        info_bing1 = get_chat_response(full_prompt_extract1, temperature=0.5, max_tokens=500)
        info_bing2 = get_chat_response(full_prompt_extract2, temperature=0.5, max_tokens=500)
        
        print("Info Bing 1",info_bing1)
        print("Info Bing 2",info_bing2)
        
        # Concatenate bing responses from query 'question' and 'query2' using context
        info_bing = info_bing1 + "\n" + info_bing2
        
        if  info_bing!="" and info_bing is not None:
            response = f"Bing search response:{info_bing}"
            response = response.strip()
            cache["query2"] = query2
            cache["bing_response1"] = responses1 
            cache["bing_response2"]= responses2
            return response, False
        else:
            response = "Bing search response: Bing was not able to extract useful information"
            return response,False



def finish(thought):
    model_final_answer = remove_boxed(last_boxed_only_string(thought))
    return model_final_answer,True


#################################################
# Define the System prompt 

# DEFINE THE <INSTRUCTION> part of the system prompt
instruction = """Solve a mathematical question with interleaving 'Thought', 'Action', 'Observation' steps. Your job is to generate only 'Thought'  and 'Action' in a step. 'Thought' reasons about the current context and information, already extracted from 'Observation' in all previous steps. 'Action' calls a particular action which can be of 5 types. The 'Action' is then executed externally outside your control to get the 'Observation' and the 'Observation' is returned to you. Continue and repeat this process for multiple steps, until the 'finish' action finds the answer. For the first step, as a planner always call the 'bing_search' action to search the web for similar questions or similar mathematical concepts.

'Action' types: 
(1) bing_search(query,context) which calls the Bing Web Search API to retrieve useful information, formulas or background information from the internet related to the query, using the context.
(2) wolframalpha_generator(query,context), calls a tool  with inputs (query and context) to solve the given query or intermediate steps in the query using the Wolfram Alpha API. The Wolfram Alpha API is most useful when there is a explicit mathematical object in the query, and requires some form of processing such as solving equations, calling functions, finding equations, etc. 
(3) text_generator(query,context), calls a tool to answer a query, using the given context by generating natural language text.
(4) program_generator(query,context), calls a tool with inputs (query and context) to generate an executable python program that can solve the given query  using the Sympy library and executing the code using a python interpreter. It takes in the query and possible context and produces an executable python program. In case of syntax errors, it also refines the code till it is free of errors. 
(5) finish(thought), which takes as input the final thought and returns the answer and finishes the task.

Information:
- The first action to be selected is always bing_search.
- Generate only 'Thought' and 'Action' in a step.
- Do not generate 'Observation' in any step. 
- Use can use a particular action in multiple steps.

Here are some examples:\n
"""



#DEFINE THE <FEW SHOT EXAMPLES> part of the system prompt
prompt_react = prompts_MATH_react.REACT_prompt
#prompt_react = prompts_MATH_Walpha_update.REACT_prompt

# System message <INSTRUCTION> + <FEW SHOT EXAMPLES> for the REACT planner
webthink_prompt = instruction + prompt_react
#webthink_prompt = instruction
length = len(webthink_prompt)

# Define context as a global variable 
context= ""

#################################################

# Main function
def webthink(idx=None, prompt=webthink_prompt, to_print=True):
    
    global context

    examples= read_jsonl_file(os.environ['SHUFFLED_MATH_DATA_FILE_PATH'])
    data = examples[idx]
    question = data['problem']
    problem_type = data['type']
    level = data['level']
    
    # Starting context (the question) (without Thought, Action, Obs)
    context += f"\nQuestion:{question}\n"

    # Starting REACT context (containing Thought, Action, Obs)
    React_context = "Please answer the following question.\n"+f"\nQuestion:{question}\n"


    # Print the starting context
    print("Initial REACT context:",React_context)
    
    n_calls, n_badcalls = 0, 0
    max_steps = 6
    i = None
    
    
    for i in range(1, max_steps):
        print("-" *90)
        #print("System instr:",prompt)
        
        
        n_calls += 1  

        # Add the next step Thought prompt to context
        thought_action = get_chat_response(context=React_context + f"\nThought {i}:",stop=["Thought","Observation"],system_mess=prompt)
        print("1st:",thought_action)
        print("-" *90)
        
        if "Observation" in thought_action:    # If still 'Observation' is generated 
            ind = thought_action.find("Observation")
            thought_action = thought_action[:ind]  # Extract only till 'Observation'

        try:
            thought, action = thought_action.strip().split(f"\nAction {i}: ")  # Split the thought and action
        except:
            #print('ohh...', thought_action)
            n_badcalls += 1
            thought = thought_action.strip().split('\n')[0]

            # Generate action seperately 
            action = get_chat_response(context=React_context+f"Thought {i}: {thought}\nAction {i}:", stop=["Thought","Action","Observation"],system_mess=prompt)
            print("2nd:",action)
            print("-" *90)

            if "Observation" in action:         # If still 'Observation' is generated 
              ind = action.find("Observation")
              action = action[:ind]             

       
        print(f"Thought {i}:",thought)
        print("-" *90)
        print(f"Action {i}:",action)
        print("-" *90)
        

        
     
 
        print("------Calling action tool------")
    
        # Initialize the observation tool 
        observation = "DIDNT CALL ACTION TOOL"
        done = False
        
        # Call the action tool 
        
        print("Action executed!:")
        try:
            observation, done = eval(action)
        
        except:
            print("Can't call!")

        # Display the observation
        print(f"Observation {i}:",observation)
        print("-" *90)
        print(f"Done {i}", done)
        print("-" *90)



        if done==False:
            
            if observation is not None:
                context+="\n" + thought + "\n" + action +"\n" + observation
                React_context += f"\nThought {i}: {thought}\nAction {i}: {action}\nObservation {i}: {observation}"  
            else:
                context+="\n" + thought + "\n" + action +"\n" + "No observation"
                React_context += f"\nThought {i}: {thought}\nAction {i}: {action}\nObservation {i}: No observation"

        elif done==True:
            
            if observation!=None:
                context+="\n" + thought + "\n" + action +"\n" + observation
                React_context += f"\nThought {i}: {thought}\nAction {i}: {action}\nObservation {i}: {observation}"  
            
            break

    
    if done==False:  # Still the done bool variable is False
        
        # Process the output to get final answer
        model_final_answer = remove_boxed(last_boxed_only_string(thought))  # Extract the answer from final thought
        
        if model_final_answer !=None:
            return model_final_answer, React_context 
        else:
            # No answer in final thought 
            # Call solution generator (from other pipeline)

            cache["context"] = context
            cache["REACT_solution"] = React_context
            return None, React_context

    
    cache["context"] = context
    cache["REACT_solution"] = React_context

    return observation, React_context
    
           

# Run the setup using WebThink function
import random
import time
idxs = list(range(7405))
cache_jsonl = "testing_REACT_MATHSENSEI.jsonl"
j = None

print("System prompt",webthink_prompt)

with open("planning/"+cache_jsonl,'a') as outfile:

    examples= read_jsonl_file(os.environ['SHUFFLED_MATH_DATA_FILE_PATH'])
    
    for j in tqdm(range(0,5000)):
        print(j)
        cache = {}
        
        data = examples[j]
        cache.update({"pid":j,"example":data})

        answer,prompt = webthink(j, to_print=False)
        
        
        
        if answer is not None:
            cache.update({"answer":answer})
        else:
            cache.update({"answer":"Not found"})

        
        json.dump(cache, outfile)
        outfile.write('\n') 
        print("Answer "+str(j),answer)
        print("-"*100)
        context = ""


                


'''
def solution_generator():
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
            
            
            solution = get_chat_response(messages=messages, temperature=_temperature, max_tokens=self.sg_max_tokens)
            # print(f"Solution: {solution}"
            
            pattern = re.compile(r"[Tt]he answer is ([A-Z])")      # "The answer is XXXXX.",
            res = pattern.findall(solution)
            if len(res) > 0:
                success = True
            count += 1

        # update the cache
        self.cache["response"] =  self.cache["response"] + "\n Solution:\n" + solution
        self.cache["solution"] = solution
        self.cache["solution_generator:input"] = test_prompt
        self.cache["solution_generator:output"] = solution
        return test_prompt, solution
    
'''