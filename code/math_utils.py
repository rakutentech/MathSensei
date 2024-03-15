from model import *
#from demos.testing_executor import *
#from math_features import *
#import inspect
#import sympy

from dotenv import load_dotenv
load_dotenv(".env")
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)


def add_missing_keys(dict1,dict2):
    for key in dict2:
        if key not in dict1:
            dict1[key]=0


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
    #logging.info(f"{string}")



    # remove inverse spaces
    string = string.replace("\\!", "")
    #logging.info(f"{string}")

    # replace \\ with \
    string = string.replace("\\\\", "\\")
    #logging.info(f"{string}")

    # replace tfrac and dfrac with frac
    string = string.replace("tfrac", "frac")
    string = string.replace("dfrac", "frac")
    #logging.info(f"{string}")

    # remove \left and \right
    string = string.replace("\\left", "")
    string = string.replace("\\right", "")
    #logging.info(f"{string}")
    
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
    #logging.info(f"Str1 {str1}")
    #logging.info(f"Str2 {str2}")

    if str1 is None and str2 is None:
        logging.info(f"WARNING: Both None")
        return True, str1, str2
    if str1 is None or str2 is None:
        return False,str1,str2
    else:
      try:
        ss1 = _strip_string(str1)
        ss2 = _strip_string(str2)
        #logging.info(f"SS1: {ss1}")
        #logging.info(f"SS2: {ss2}")

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



def read_jsonl_file(file_path):
    data = []
    count = 0
    with open(file_path, 'r') as file:
        for line in file:
            try:
                record = json.loads(line)
            except:
                record = {}  
                #logging.info(f"hjwhufhwufh")  
            data.append(record)
            count+=1

    return data



def save_python_errors(filepath):

    import pandas as pd 
    data = read_jsonl_file(filepath)
    
    all_math_data = read_jsonl_file(os.getenv("MATH_DATA_FILE_PATH"))
    logging.info(f"{len(data)}")
    #logging.info(f"{data[0]}")

    j={}

    for i in range(len(data)):

    
   
            program = data[i]["program_generator:output"]
            logging.info(f"Program:\n {program}")
            output, error_message = safe_execute_t(program)
            logging.info(f"Error message {error_message}")
            if error_message!=None:
                j[i] = [error_message]

    # Output dictionary to jsonl file
    with open("python_errors.json","w") as json_file:
        json.dump(j,json_file,indent=4)
    

def remove_whitespace_elements(input_list):
    return [item for item in input_list if item.strip()!=""]

def count_python_error_types(filepath):

     examples = json.load(open(filepath))
     category1 = "not defined"
     category2 = "no attribute"
     category3 = "out of range"
     category4 = "unsupported "
     
     count =0
     category1_count = 0
     category2_count = 0
     category3_count = 0
     category4_count = 0
     
     #logging.info(f"{examples}")

     for i in examples:
         count+=1
         if category1 in examples[i][0] :
             category1_count+=1

         if category2 in examples[i][0] :
             category2_count+=1

         if category3 in examples[i][0] :
             category3_count+=1

         if category4 in examples[i][0] :
             category4_count+=1            
    
     logging.info(f"{category1_count/count *100}")
     logging.info(f"{category2_count/count *100}")
     logging.info(f"{category3_count/count *100}")
     logging.info(f"{category4_count/count *100}")


import matplotlib.pyplot as plt

def plot_accuracy_by_cat(d,sx,sy,s):

    sorted_data = sorted(d.items())

    # Extract keys and values after sorting
    keys = [item[0] for item in sorted_data]
    values = [item[1] for item in sorted_data]

    # Create a bar plot
    plt.bar(keys, values)
    plt.xlabel(sx)
    plt.ylabel(sy)
    plt.title(s)
    plt.xticks(rotation=45)
    plt.xticks(keys)

    # Display the plot
    plt.show()

             

def accuracy_REACT(filepath):

    data = read_jsonl_file(filepath)
    examples= read_jsonl_file(os.getenv("SHUFFLED_MATH_DATA_FILE_PATH"))
    levels = [i['level'] for i in examples]

    unique_levels = list(set(levels))
    logging.info(f"Unique levels {unique_levels}")
    
    total_levels = [0]*len(unique_levels)
    correct_levels= [0]*len(unique_levels)
    
    types = [i['type'] for i in examples]

    unique_types = list(set(types))
    logging.info(f"Unique types {unique_types}")
    
    total_types = [0]*len(unique_types)
    correct_types = [0]*len(unique_types)
    logging.info(f"Total types {total_types}")
    
    count =0
    correct = 0
    
    false_indices_list = []
    correct_indices_list = []
    error_indices_list = []
    wrong_format = []
    obs = 0
    error_sg = 0

    for i in range(len(data)):

        if data[i] == {}:
            continue
        

        if "REACT_solution" in data[i]:  

            if data[i]["REACT_solution"]=="error" or data[i]["REACT_solution"]=='' or data[i]["REACT_solution"]==None:
                error_indices_list.append(i)
                continue
        else:
            error_indices_list.append(i)
            continue

       
        type_ = types[i]
        output = data[i]['REACT_solution']
        

       

        if "boxed" not in output:  # REACT did not converge for these examples ()
            #logging.info(output)
            error_sg+=1
            #count+=1
            wrong_format.append(i)
            continue
        
        gold_answer = remove_boxed(last_boxed_only_string(examples[i]["solution"])) 
        
        ind1 = unique_types.index(type_)
        total_types[ind1]+=1

        level_ = levels[i]
        ind = unique_levels.index(level_)
        total_levels[ind]+=1
        count+=1
        


        # Process the output to get final answer
        model_final_answer = remove_boxed(last_boxed_only_string(output)) 

       
        

        status,_,_  = is_equiv(model_final_answer,gold_answer) 

        if status==True:
            correct_levels[ind]+=1
            correct_types[ind1]+=1
            correct+=1
            correct_indices_list.append(i)
           
        else:
            false_indices_list.append(i)    
    
    logging.info(f"Total REACT correct {correct}")
    logging.info(f"Total No of examples: {len(data)}")
    logging.info(f"Accuracy REACT (on converged) : {((correct)/count)*100}")

   

    logging.info("*"*50)
    logging.info("Accuracy by level:::")

    for i in range(len(unique_levels)):

        logging.info("Accuracy " + unique_levels[i]+":")
        try: 
            logging.info(correct_levels[i]/total_levels[i]*100)
        except:
            pass   
    logging.info("*"*50)
    logging.info("Accuracy by type :::")

    for i in range(len(unique_types)):

        logging.info("Accuracy " + unique_types[i]+":")
        try: 
            logging.info(correct_types[i]/total_types[i]*100)
        except:
            pass         
    
    logging.info(f"No of non-converged examples (out of 3598): {len(wrong_format)}")

    return
        
def accuracy_ENSEMBLE(filepath):

    data = read_jsonl_file(filepath)
    examples= read_jsonl_file(os.getenv("SHUFFLED_MATH_DATA_FILE_PATH"))
    levels = [i['level'] for i in examples]

    unique_levels = list(set(levels))
    #logging.info("Unique levels",unique_levels)
    
    total_levels = [0]*len(unique_levels)
    correct_levels= [0]*len(unique_levels)
    
    types = [i['type'] for i in examples]

    unique_types = list(set(types))
    #logging.info("Unique types",unique_types)
    
    total_types = [0]*len(unique_types)
    correct_types = [0]*len(unique_types)
    #logging.info("Total types",total_types)
    
    count =0
    correct = 0
    
    false_indices_list = []
    correct_indices_list = []
    error_indices_list = []

    obs = 0
    error_sg = 0
    indices_intalg =[]
    REACT_wrong_format = [6, 7, 11, 13, 26, 34, 36, 49, 59, 62, 66, 67, 72, 82, 92, 99, 101, 106, 110, 114, 122, 139, 152, 155, 181, 193, 196, 200, 206, 207, 211, 232, 234, 238, 239, 244, 246, 253, 254, 257, 267, 276, 279, 282, 289, 294, 297, 298, 299, 304, 308, 327, 329, 337, 344, 348, 352, 355, 366, 372, 391, 397, 401, 406, 407, 408, 416, 433, 444, 450, 455, 471, 472, 476, 485, 486, 491, 496, 514, 524, 525, 529, 537, 542, 555, 560, 573, 579, 612, 614, 623, 637, 639, 653, 694, 701, 702, 711, 721, 737, 741, 746, 753, 754, 766, 767, 769, 772, 779, 783, 795, 803, 814, 817, 823, 829, 831, 834, 856, 870, 873, 874, 875, 877, 880, 883, 885, 886, 889, 908, 912, 923, 924, 935, 937, 943, 952, 958, 961, 966, 970, 982, 996, 997, 1002, 1003, 1006, 1008, 1013, 1018, 1019, 1026, 1028, 1029, 1037, 1039, 1052, 1055, 1058, 1061, 1062, 1064, 1066, 1069, 1072, 1078, 1083, 1116, 1120, 1134, 1138, 1145, 1156, 1162, 1165, 1175, 1181, 1182, 1191, 1197, 1200, 1202, 1203, 1204, 1205, 1206, 1210, 1212, 1217, 1221, 1222, 1242, 1243, 1264, 1279, 1283, 1290, 1292, 1296, 1306, 1317, 1320, 1326, 1328, 1331, 1335, 1346, 1386, 1387, 1395, 1397, 1399, 1402, 1409, 1419, 1422, 1424, 1427, 1432, 1441, 1457, 1459, 1464, 1473, 1491, 1504, 1507, 1515, 1516, 1527, 1534, 1538, 1557, 1566, 1570, 1571, 1583, 1604, 1607, 1611, 1629, 1635, 1644, 1646, 1647, 1665, 1674, 1675, 1676, 1682, 1695, 1697, 1706, 1710, 1712, 1721, 1767, 1769, 1772, 1780, 1785, 1786, 1787, 1794, 1795, 1805, 1807, 1832, 1835, 1836, 1839, 1847, 1849, 1851, 1882, 1886, 1891, 1898, 1903, 1922, 1937, 1954, 1955, 1963, 1975, 1981, 1990, 1995, 2005, 2012, 2013, 2017, 2025, 2027, 2028, 2050, 2063, 2068, 2091, 2098, 2114, 2130, 2133, 2153, 2157, 2158, 2160, 2165, 2167, 2169, 2170, 2194, 2196, 2200, 2214, 2216, 2227, 2242, 2251, 2252, 2255, 2257, 2264, 2265, 2269, 2270, 2273, 2279, 2287, 2295, 2302, 2304, 2311, 2316, 2325, 2326, 2331, 2341, 2364, 2373, 2383, 2384, 2389, 2392, 2395, 2408, 2411, 2412, 2415, 2425, 2434, 2442, 2449, 2451, 2457, 2458, 2465, 2471, 2477, 2487, 2502, 2506, 2519, 2525, 2526, 2531, 2547, 2553, 2566, 2568, 2595, 2597, 2599, 2603, 2607, 2608, 2612, 2614, 2633, 2635, 2644, 2647, 2655, 2666, 2671, 2678, 2702, 2704, 2706, 2719, 2720, 2721, 2722, 2742, 2743, 2759, 2760, 2763, 2770, 2772, 2775, 2796, 2802, 2803, 2807, 2809, 2816, 2819, 2820, 2850, 2857, 2858, 2868, 2870, 2878, 2889, 2921, 2924, 2925, 2927, 2932, 2936, 2938, 2939, 2952, 2953, 2964, 2967, 2977, 2983, 2984, 2985, 2988, 2991, 2992, 3014, 3015, 3029, 3046, 3056, 3062, 3066, 3079, 3092, 3107, 3114, 3127, 3129, 3130, 3134, 3137, 3139, 3158, 3177, 3181, 3187, 3190, 3191, 3203, 3206, 3211, 3233, 3235, 3246, 3249, 3263, 3264, 3267, 3268, 3269, 3271, 3273, 3276, 3279, 3284, 3286, 3292, 3298, 3303, 3308, 3316, 3317, 3322, 3325, 3327, 3334, 3335, 3339, 3340, 3343, 3354, 3355, 3361, 3366, 3375, 3384, 3398, 3399, 3408, 3413, 3425, 3431, 3443, 3445, 3450, 3452, 3486, 3487, 3493, 3494, 3499, 3511, 3520, 3523, 3524, 3526, 3535, 3549, 3552, 3564, 3566, 3579, 3581, 3582, 3583, 3592, 3594, 3595]
    
    questions_ensemble_pt2 = [data[k]["example"]["problem"] for k in range(5000)]
    correct_accuracy_setting = [] 
    
    for i in REACT_wrong_format:
        
        
        question = examples[i]["problem"]
        i =  questions_ensemble_pt2.index(question)


        if data[i]['solution']=="error" or data[i]['solution']=='' or data[i]['solution']==None :
            continue
            
        type_ = data[i]["example"]['type']
        ind1 = unique_types.index(type_)
        total_types[ind1]+=1

        level_ = data[i]["example"]['level']
        ind = unique_levels.index(level_)
        total_levels[ind]+=1
        #logging.info(type_)
       

        output = data[i]['solution_generator:output']

        if "boxed" not in output:
            continue
        
        gold_answer = remove_boxed(last_boxed_only_string(data[i]['example']['solution'])) 
        count+=1
       
        # Process the output to get final answer
        model_final_answer = remove_boxed(last_boxed_only_string(output)) 
        status,_,_  = is_equiv(model_final_answer,gold_answer) 

        if status==True:
            correct_levels[ind]+=1
            correct_types[ind1]+=1
            #logging.info(model_final_answer,gold_answer)
            correct_accuracy_setting.append(i)
        else:
            false_indices_list.append(i)    
    
    return len(correct_accuracy_setting),len(REACT_wrong_format),correct_types,correct_levels,total_types,total_levels



def combine_ES(filepath,filepath2):
    data = read_jsonl_file(filepath)
    examples= read_jsonl_file(os.getenv("SHUFFLED_MATH_DATA_FILE_PATH"))
    levels = [i['level'] for i in examples]

    unique_levels = list(set(levels))
    logging.info(f"Unique levels {unique_levels}")
    
    total_levels = [0]*len(unique_levels)
    correct_levels= [0]*len(unique_levels)
    
    types = [i['type'] for i in examples]

    unique_types = list(set(types))
    logging.info(f"Unique types {unique_types}")
    
    total_types = [0]*len(unique_types)
    correct_types = [0]*len(unique_types)
    logging.info(f"Total types {total_types}")
    
    count =0
    correct = 0
    
    false_indices_list = []
    correct_indices_list = []
    error_indices_list = []
    wrong_format = []
    obs = 0
    error_sg = 0

    for i in range(len(data)):

        if data[i] == {}:
            continue
        
        if "REACT_solution" in data[i]:
            if data[i]["REACT_solution"]=="error" or data[i]["REACT_solution"]=='' or data[i]["REACT_solution"]==None :
                error_indices_list.append(i)
                continue
        else:
            error_indices_list.append(i)
            continue

       
        type_ = types[i]
        output = data[i]['REACT_solution']
        

        if "boxed" not in output:
            #logging.info(output)
            error_sg+=1
            wrong_format.append(i)
            continue
        
        gold_answer = remove_boxed(last_boxed_only_string(examples[i]["solution"])) 
        
        ind1 = unique_types.index(type_)
        total_types[ind1]+=1

        level_ = levels[i]
        ind = unique_levels.index(level_)
        total_levels[ind]+=1
        count+=1
        
        # Process the output to get final answer
        model_final_answer = remove_boxed(last_boxed_only_string(output)) 
        status,_,_  = is_equiv(model_final_answer,gold_answer) 

        if status==True:
            correct_levels[ind]+=1
            correct_types[ind1]+=1
            correct+=1
            correct_indices_list.append(i)

            '''
            if i<=100 and data[i]['program_executor:output']!=None:
                logging.info("-"*100)
                logging.info(data[i]['example']['problem'])
                logging.info(data[i]['example']['type'])
                logging.info(data[i]['example']['level'])
                logging.info("*"*20)
                logging.info("Ground truth sol:",data[i]['example']['solution'])
                logging.info("*"*20)
                logging.info(data[i]['solution_generator:input'])
                logging.info("*"*20)
                logging.info(data[i]['solution_generator:output'])
            '''    

            #logging.info("Correct"+str(i))
        else:
            '''
            if type_=="Intermediate Algebra" and data[i]['example']['level']=="Level 3" and obs<=20:
                logging.info("-"*100)
                logging.info(data[i]['example']['problem'])
                logging.info(data[i]['example']['type'])
                logging.info(data[i]['example']['level'])
                logging.info("*"*20)
                logging.info("Ground truth sol:",data[i]['example']['solution'])
                logging.info("*"*20)
                logging.info(data[i]['program_generator:output'])
                logging.info(data[i]['program_executor:output'])
                logging.info("*"*20)
                logging.info(data[i]['solution_generator:input'])
                logging.info("*"*20)
                logging.info(data[i]['solution_generator:output'])
                ch = input("Press a key")
                obs +=1
            '''    
                

            false_indices_list.append(i)    
    
    logging.info(f"Total REACT correct {correct}")
    logging.info(f"Total No of examples: {len(data)}")
    logging.info(f"Accuracy REACT (converged)): {((correct)/count)*100}")

    #logging.info("Correct indices:",correct_indices_list)
    #logging.info("Incorrect Indices",false_indices_list)
    #logging.info("Error indices",error_indices_list)
    
    correct_wr_no, total_wr_no,correct_type_wr,correct_lvl_wr,total_type_wr,total_level_wr = accuracy_ENSEMBLE(filepath2)
    logging.info(f"Total REACT Converged: {count}")
    logging.info(f"REACT Correct {correct}")
    logging.info(f"Accuracy REACT (for converged)): {(correct)/count*100}")
    logging.info(f"Not Converged {total_wr_no}")
    logging.info(f"Out of them Ensemble 2nd part got correct {correct_wr_no}")
    logging.info("Final accuracy of ensemble: {(correct_wr_no+correct)/len(data)}")

    for i in range(len(unique_levels)):

        logging.info("Accuracy " + unique_levels[i]+":")
        try: 
            logging.info((correct_levels[i]+correct_lvl_wr[i])*100/(total_levels[i]+total_level_wr[i]))
        except:
            pass
        
    logging.info("*"*50)
    logging.info("Accuracy by type :::")

    for i in range(len(unique_types)):

        logging.info("Accuracy " + unique_types[i]+":")
        try: 
            logging.info((correct_types[i]+correct_type_wr[i])*100/(total_types[i]+total_type_wr[i]))
        except:
            pass     



def accuracy_by_level(filepath):

    data = read_jsonl_file(filepath)
    #q = [data[k]['example']["problem"] for k in range(len(data))]
    
    q = []
    
    for k in range(len(data)):
        try:
            q.append(data[k]['example']["problem"])
        except:
            logging.info("")    


    list_set = set(q)
    
    # convert the set to the list
    unique_list = (list(list_set))
    logging.info("No of Unique elements " + str(len(unique_list)))

    #examples= read_jsonl_file(os.getenv("SHUFFLED_MATH_DATA_FILE_PATH"))
    examples= read_jsonl_file(os.getenv("MATH_DATA_FILE_PATH"))

    
    levels = [i['level'] for i in examples]

    unique_levels = list(set(levels))
    logging.info("Unique levels" + str(unique_levels))
    
    total_levels = [0]*len(unique_levels)
    correct_levels= [0]*len(unique_levels)
    
    types = [i['type'] for i in examples]

    unique_types = list(set(types))
    logging.info("Unique types" + str(unique_types))
    
    total_types = [0]*len(unique_types)
    correct_types = [0]*len(unique_types)
    logging.info("Total types" + str(total_types))
    
    count =0
    correct = 0
    
    false_indices_list = []
    correct_indices_list = []
    error_indices_list = []

    obs = 0
    error_sg = 0
    indices_intalg =[]
    

    for i in range(len(data)):
        
        #logging.info(data[i]['example']['problem'])
        
        try:
            type_ = data[i]['example']['type']
            level_ = data[i]['example']['level']
        
        except:
            logging.info("")    
        
       
        if 'solution' not in data[i]:
            continue
        
        if data[i]['solution']=="error" or data[i]['solution']=='' or data[i]['solution']==None :
            error_indices_list.append(i)
            continue
        
        
        ind1 = unique_types.index(type_)
        total_types[ind1]+=1

        
        ind = unique_levels.index(level_)
        total_levels[ind]+=1
        output = data[i]['solution_generator:output']

        if "boxed" not in output:
            error_sg+=1
            count+=1
            #logging.info(f"{output}"")
            continue

        gold_answer = remove_boxed(last_boxed_only_string(data[i]['example']['solution'])) 
        count+=1
       

        # Process the output to get final answer
        model_final_answer = remove_boxed(last_boxed_only_string(output)) 
        status,_,_  = is_equiv(model_final_answer,gold_answer) 

        if status==True:
            correct_levels[ind]+=1
            correct_types[ind1]+=1
            correct+=1
            correct_indices_list.append(i)
            #logging.info(f"Correct {str(i)}")
        else:
            
            false_indices_list.append(i)    
    
    logging.info(f"Accuracy Math data: {((correct)/count)*100}")
    logging.info(f"Total No of examples: {count}")
   

    logging.info("*"*50)
    logging.info(f"Accuracy by level:::")

    for i in range(len(unique_levels)):

        logging.info(f"Accuracy  {unique_levels[i]} :")
        try: 
            logging.info(correct_levels[i]/total_levels[i]*100)
        except:
            pass   
    logging.info("*"*50)
    logging.info("Accuracy by type :::")

    for i in range(len(unique_types)):

        logging.info("Accuracy " + unique_types[i]+":")
        try: 
            logging.info(correct_types[i]/total_types[i]*100)
        except:
            pass         
    logging.info("No of errors in output format:" + str(error_sg))

    #logging.info(correct_indices_list)
    #logging.info("False indices list")
    #logging.info(false_indices_list)
    #logging.info(indices_intalg)
    return
        
    


def extract_answer(text):
    import re
    # Check if "the answer is" or "The answer is" is present in the string
    answer_match = re.search(r'(?:the answer is|The answer is)\s+([A-Z])', text)
    
    if answer_match:
        # Extract the next character after space if it is a capital letter
        return answer_match.group(1)

    # Check if "boxed" is present in the string
    boxed_match = re.search(r'\\boxed{\\textbf{[(](.)[)]}}', text)

    if boxed_match:
        # Extract the letter enclosed by textbf
        return boxed_match.group(1)

    # Return None if no match is found
    return None      
    

def extract_option_AQUA(input_string):
    # Define a regular expression pattern to find the option
    pattern = re.compile(r"[Tt]he answer is [A-Z]")

    # Search for the pattern in the input string
    match = re.search(pattern, input_string)

    # If a match is found, return the extracted option
    if match:
       s = match.group(0)
       s = s.strip()
       return s[-1]
    else:
        return None       # Return None if no match is found


def accuracy_AQUA(filepath):

    data = read_jsonl_file(filepath)
    q = []
    for k in range(len(data)):
        try:
            q.append(data[k]['example']["problem"])
        except:
            logging.info("")    

    list_set = set(q)
    
    # convert the set to the list
    unique_list = (list(list_set))
    logging.info(f"No of Unique elements {len(unique_list)}")

    examples= read_jsonl_file(os.getenv("TEST_AQUA_DATA_FILE_PATH"))
    #logging.info(examples[0])
    count =0
    correct = 0
    
    false_indices_list = []
    correct_indices_list = []
    error_indices_list = []

    obs = 0
    error_sg = 0
    

    for i in range(len(data)):
        
        #if  data[i]['solution']=="error" or data[i]['solution']=='' or data[i]['solution']==None:
        if 'solution' in data[i]:
            if data[i]['solution']=="error" or data[i]['solution']=='' or data[i]['solution']== None :
                error_indices_list.append(i)
                continue
        
        if 'solution_generator:output' not in data[i]:
            error_indices_list.append(i)
            continue

        output = data[i]['solution_generator:output']
      
       
        
        #logging.info("Format right")
        gold_answer = examples[i]["correct"]
       
       

        model_final_answer = extract_option_AQUA(output)
        if model_final_answer is None:
            error_sg+=1
            count+=1
            continue
        #logging.info(model_final_answer)
        
        count+=1
        status = False
        
        if model_final_answer is None:
            status = False
        
        if model_final_answer is not None:
            model_final_answer = model_final_answer.strip()
        
        gold_answer = gold_answer.strip()

        if model_final_answer == gold_answer or model_final_answer.upper() == gold_answer:
            status = True


            

        if status==True:
            correct+=1
            correct_indices_list.append(i)
            #logging.info("Correct"+str(i))
        else:
            #logging.info(model_final_answer,gold_answer)
            false_indices_list.append(i)    
    
    
    logging.info(f"Accuracy AQUA {(correct/count)*100}")
    logging.info(f"Total No of examples: {count}")
   
    return
        



def GSM_extract_answer(completion):
    ANS_RE = re.compile(r"#### (\-?[0-9\.\,]+)")
    INVALID_ANS = "[invalid]"
    match = ANS_RE.search(completion)
    if match:
        match_str = match.group(1).strip()
        match_str = match_str.replace(",", "")
        return match_str
    else:
        return INVALID_ANS 


def accuracy_GSM(filepath):
    
    data = read_jsonl_file(filepath)
    
    q = []
    for k in range(len(data)):
        try:
            q.append(data[k]['example']["problem"])
        except:
            logging.info("")    

    list_set = set(q)
    
    # convert the set to the list
    unique_list = (list(list_set))
    logging.info("No of Unique elements:" + str(len(unique_list)) )
    
    examples= read_jsonl_file(os.getenv("TEST_GSM8K_DATA_FILE_PATH"))
    #logging.info(examples[0])
    count =0
    correct = 0
    
    false_indices_list = []
    correct_indices_list = []
    error_indices_list = []

    obs = 0
    error_sg = 0
    

    for i in range(len(data)):
        
        #if  data[i]['solution']=="error" or data[i]['solution']=='' or data[i]['solution']==None:
        if data[i]['solution']=="error" or data[i]['solution']=='' or data[i]['solution']== None :
            error_indices_list.append(i)
            continue
        
       
        output = data[i]['solution_generator:output']
      
        #logging.info("Format right")
        gold_answer = examples[i]["answer"]
        
        # Extract the answer 
        gold_answer = GSM_extract_answer(gold_answer)
        model_final_answer = GSM_extract_answer(output)
        

        if model_final_answer == "[invalid]":
            #logging.info(output)
            error_sg+=1
            count+=1
            continue
        
       
        count+=1
        status = False
        #logging.info("Model answer:",model_final_answer)
        #logging.info("Gold answer:",gold_answer)
        if '.' in model_final_answer:
            idx = model_final_answer.find('.')
            model_final_answer = model_final_answer[:idx]
        
        if model_final_answer.strip() == gold_answer.strip():
            status = True

        if status==True:
            correct+=1
            correct_indices_list.append(i)
            
        else:
            #logging.info("Incorrect"+str(i),model_final_answer.strip(),gold_answer.strip())
            false_indices_list.append(i)    
    
  
    logging.info(f"Original Accuracy GSM {((correct)/count)*100}")
    logging.info(f"Total no of examples: {count}")

    
    #logging.info("Incorrect Indices",false_indices_list)
    #logging.info("Error indices",error_indices_list)
    #logging.info("No of incorrect format",error_sg)



def MMLU_extract_answer(completion):
    ANS_RE = re.compile("#### (\-?[A-D])")
    INVALID_ANS = "[invalid]"
    match = ANS_RE.search(completion)
    if match:
        match_str = match.group(1).strip()
        match_str = match_str.replace(",", "")
        return match_str
    else:
        return INVALID_ANS 



def accuracy_MMLU(filepath):
    data = read_jsonl_file(filepath)
    
    q = []
    for k in range(len(data)):
        try:
            q.append(data[k]['example']["problem"])
        except:
            logging.info("")    

    list_set = set(q)
    
    # convert the set to the list
    unique_list = (list(list_set))
    logging.info(f"No of Unique elements {len(unique_list)}")
    examples= read_jsonl_file(os.getenv("TEST_MMLU_DATA_FILE_PATH"))
    #logging.info(examples[0])
    count =0
    correct = 0
    
    false_indices_list = []
    correct_indices_list = []
    error_indices_list = []

    obs = 0
    error_sg = 0
    
    types = [i["file_name"] for i in examples]
    unique_types = list(set(types))
    logging.info(f"Unique types {unique_types}")
    total_types = [0]*len(unique_types)
    correct_types = [0]*len(unique_types)
    logging.info(f"Total types {total_types}")

    for i in range(len(data)):
        
        #if  data[i]['solution']=="error" or data[i]['solution']=='' or data[i]['solution']==None:
        if data[i]['solution']=="error" or data[i]['solution']=='' or data[i]['solution']== None :
            error_indices_list.append(i)
            continue
        
       
        output = data[i]['solution_generator:output']
        
        type_ = data[i]["example"]["file_name"]
        ind1 = unique_types.index(type_)
        total_types[ind1]+=1

        #logging.info("Format right")
        gold_answer = examples[i]["Answer"]
        
    
        model_final_answer = MMLU_extract_answer(output)
        
        if model_final_answer == "[invalid]":
            error_sg+=1
            #logging.info(output)
            continue
        
        count+=1
        status = False
        #logging.info("Model answer:",model_final_answer)
        #logging.info("Gold answer:",gold_answer)
        if model_final_answer.strip() == gold_answer.strip():
            status = True

        if status==True:
            correct+=1
            correct_indices_list.append(i)
            correct_types[ind1]+=1
            #logging.info("Correct"+str(i))
        else:
            false_indices_list.append(i)    
    
    
    logging.info(f"Accuracy MMLU-MATH {(correct/count)*100}")
    logging.info(f"Total No of examples: {len(data)}")
    
    #logging.info("Incorrect Indices",false_indices_list)
    #logging.info("Error indices",error_indices_list)
    
    logging.info("Accuracy by type :::")

    for i in range(len(unique_types)):

        logging.info("Accuracy " + unique_types[i]+":")
        try: 
            logging.info(correct_types[i]/total_types[i]*100)
        except:
            pass        
    
    logging.info(f"No of examples with incorrect format {error_sg}")




def accuracy_REACT_converged_subset(filepath):

    data = read_jsonl_file(filepath)
    examples= read_jsonl_file(os.getenv("SHUFFLED_MATH_DATA_FILE_PATH"))
    data_REACT = read_jsonl_file(os.getenv("NEW_LATEST_REACT_DATA_FILE_PATH"))
    levels = [i['level'] for i in examples]

    unique_levels = list(set(levels))
    #logging.info("Unique levels",unique_levels)
    
    total_levels = [0]*len(unique_levels)
    correct_levels= [0]*len(unique_levels)
    
    types = [i['type'] for i in examples]

    unique_types = list(set(types))
    #logging.info("Unique types",unique_types)
    
    total_types = [0]*len(unique_types)
    correct_types = [0]*len(unique_types)
    #logging.info("Total types",total_types)
    


    count =0
    correct = 0
    
    false_indices_list = []
    correct_indices_list = []
    error_indices_list = []

    obs = 0
    error_sg = 0
    indices_intalg =[]
    REACT_wrong_format = [6, 7, 11, 13, 26, 34, 36, 49, 59, 62, 66, 67, 72, 82, 92, 99, 101, 106, 110, 114, 122, 139, 152, 155, 181, 193, 196, 200, 206, 207, 211, 232, 234, 238, 239, 244, 246, 253, 254, 257, 267, 276, 279, 282, 289, 294, 297, 298, 299, 304, 308, 327, 329, 337, 344, 348, 352, 355, 366, 372, 391, 397, 401, 406, 407, 408, 416, 433, 444, 450, 455, 471, 472, 476, 485, 486, 491, 496, 514, 524, 525, 529, 537, 542, 555, 560, 573, 579, 612, 614, 623, 637, 639, 653, 694, 701, 702, 711, 721, 737, 741, 746, 753, 754, 766, 767, 769, 772, 779, 783, 795, 803, 814, 817, 823, 829, 831, 834, 856, 870, 873, 874, 875, 877, 880, 883, 885, 886, 889, 908, 912, 923, 924, 935, 937, 943, 952, 958, 961, 966, 970, 982, 996, 997, 1002, 1003, 1006, 1008, 1013, 1018, 1019, 1026, 1028, 1029, 1037, 1039, 1052, 1055, 1058, 1061, 1062, 1064, 1066, 1069, 1072, 1078, 1083, 1116, 1120, 1134, 1138, 1145, 1156, 1162, 1165, 1175, 1181, 1182, 1191, 1197, 1200, 1202, 1203, 1204, 1205, 1206, 1210, 1212, 1217, 1221, 1222, 1242, 1243, 1264, 1279, 1283, 1290, 1292, 1296, 1306, 1317, 1320, 1326, 1328, 1331, 1335, 1346, 1386, 1387, 1395, 1397, 1399, 1402, 1409, 1419, 1422, 1424, 1427, 1432, 1441, 1457, 1459, 1464, 1473, 1491, 1504, 1507, 1515, 1516, 1527, 1534, 1538, 1557, 1566, 1570, 1571, 1583, 1604, 1607, 1611, 1629, 1635, 1644, 1646, 1647, 1665, 1674, 1675, 1676, 1682, 1695, 1697, 1706, 1710, 1712, 1721, 1767, 1769, 1772, 1780, 1785, 1786, 1787, 1794, 1795, 1805, 1807, 1832, 1835, 1836, 1839, 1847, 1849, 1851, 1882, 1886, 1891, 1898, 1903, 1922, 1937, 1954, 1955, 1963, 1975, 1981, 1990, 1995, 2005, 2012, 2013, 2017, 2025, 2027, 2028, 2050, 2063, 2068, 2091, 2098, 2114, 2130, 2133, 2153, 2157, 2158, 2160, 2165, 2167, 2169, 2170, 2194, 2196, 2200, 2214, 2216, 2227, 2242, 2251, 2252, 2255, 2257, 2264, 2265, 2269, 2270, 2273, 2279, 2287, 2295, 2302, 2304, 2311, 2316, 2325, 2326, 2331, 2341, 2364, 2373, 2383, 2384, 2389, 2392, 2395, 2408, 2411, 2412, 2415, 2425, 2434, 2442, 2449, 2451, 2457, 2458, 2465, 2471, 2477, 2487, 2502, 2506, 2519, 2525, 2526, 2531, 2547, 2553, 2566, 2568, 2595, 2597, 2599, 2603, 2607, 2608, 2612, 2614, 2633, 2635, 2644, 2647, 2655, 2666, 2671, 2678, 2702, 2704, 2706, 2719, 2720, 2721, 2722, 2742, 2743, 2759, 2760, 2763, 2770, 2772, 2775, 2796, 2802, 2803, 2807, 2809, 2816, 2819, 2820, 2850, 2857, 2858, 2868, 2870, 2878, 2889, 2921, 2924, 2925, 2927, 2932, 2936, 2938, 2939, 2952, 2953, 2964, 2967, 2977, 2983, 2984, 2985, 2988, 2991, 2992, 3014, 3015, 3029, 3046, 3056, 3062, 3066, 3079, 3092, 3107, 3114, 3127, 3129, 3130, 3134, 3137, 3139, 3158, 3177, 3181, 3187, 3190, 3191, 3203, 3206, 3211, 3233, 3235, 3246, 3249, 3263, 3264, 3267, 3268, 3269, 3271, 3273, 3276, 3279, 3284, 3286, 3292, 3298, 3303, 3308, 3316, 3317, 3322, 3325, 3327, 3334, 3335, 3339, 3340, 3343, 3354, 3355, 3361, 3366, 3375, 3384, 3398, 3399, 3408, 3413, 3425, 3431, 3443, 3445, 3450, 3452, 3486, 3487, 3493, 3494, 3499, 3511, 3520, 3523, 3524, 3526, 3535, 3549, 3552, 3564, 3566, 3579, 3581, 3582, 3583, 3592, 3594, 3595]
    
    questions_ensemble_pt2 = []
    
    for k in range(len(data)):
        try:
            questions_ensemble_pt2.append(data[k]['example']["problem"])
        except:
            logging.info("")  
    
    
    for i in range(len(data_REACT)):

        if i in REACT_wrong_format:
            continue    # Only accuracy for converged

        # Question of the REACT for converged
        question = data_REACT[i]["example"]["problem"]
        
        try: 
            j =  questions_ensemble_pt2.index(question)
        except:
            continue    
        
        
        if data[j]['solution']=="error" or data[j]['solution']=='' or data[j]['solution']==None :
            error_indices_list.append(j)
            continue
            
        type_ = data[j]["example"]['type']
        ind1 = unique_types.index(type_)
        total_types[ind1]+=1

        level_ = data[j]["example"]['level']
        ind = unique_levels.index(level_)
        total_levels[ind]+=1

        count+=1 # Increase count
        
        output = data[j]['solution_generator:output']

        if "boxed" not in output:
            error_sg+=1
            continue
        
        #count+=1 #Increase count
        gold_answer = remove_boxed(last_boxed_only_string(data[j]['example']['solution'])) 
        # Process the output to get final answer
        model_final_answer = remove_boxed(last_boxed_only_string(output)) 

        status,_,_  = is_equiv(model_final_answer,gold_answer) 

        if status==True:
            correct_levels[ind]+=1
            correct_types[ind1]+=1
            correct+=1
            #logging.info(model_final_answer,gold_answer)
            correct_indices_list.append(j)
        else:
            false_indices_list.append(j)    


    logging.info("Total examples: " + str(count))
    logging.info(f"Accuracy Math data on REACT converged SUBSET (3069 examples): {(correct/count)*100}")
    #logging.info("Correct indices:",correct_indices_list)
    #logging.info("length Incorrect Indices",len(false_indices_list))
    #logging.info("length Error indices",len(error_indices_list))

    logging.info("*"*50)
    logging.info("Accuracy by level:::")

    for i in range(len(unique_levels)):

        logging.info("Accuracy " + unique_levels[i]+":")
        try: 
            logging.info(correct_levels[i]/total_levels[i]*100)
        except:
            pass   
    logging.info("*"*50)
    logging.info("Accuracy by type :::")

    for i in range(len(unique_types)):

        logging.info("Accuracy " + unique_types[i]+":")
        try: 
            logging.info(correct_types[i]/total_types[i]*100)
        except:
            pass         
    
    logging.info(f"No of wrong format {error_sg}")   
    return 


def analysis_walpha_sg(filepath):
    import pandas as pd
    import seaborn as sns
    import matplotlib.pyplot as plt

    data1 = read_jsonl_file(filepath)
    data_sg = read_jsonl_file(os.getenv("MATHSENSEI_CHATGPT_SG_MINITEST_CACHE_DATA_FILE_PATH"))
    
    examples= read_jsonl_file(os.getenv("SHUFFLED_MATH_DATA_FILE_PATH"))
    levels = [i['level'] for i in examples]

    unique_levels = list(set(levels))
    logging.info("Unique levels",unique_levels)
    
    total_levels = [0]*len(unique_levels)
    correct_levels= [0]*len(unique_levels)
    
    types = [i['type'] for i in examples]

    unique_types = list(set(types))
    logging.info("Unique types",unique_types)
    
    total_types = [0]*len(unique_types)
    correct_types = [0]*len(unique_types)
    logging.info("Total types",total_types)
    
    count =0
    correct = 0
    
    false_indices_list = []
    correct_indices_list = []
    error_indices_list = []

    obs = 0
    error_sg = 0
    indices_intalg =[]

    questions_module_settings = []
    
    for i in range(len(data1)):
        try:
           questions_module_settings.append(data1[i]["example"]["problem"])
        except:
           continue
    
   
    scatter_plot_dict = {}
    for t in unique_types :
        scatter_plot_dict[t] = [0,0,0,0,0]
    
    logging.info(scatter_plot_dict)
    found_q = 0 
    #REACT_wrong_format = [6, 7, 11, 13, 26, 34, 36, 49, 59, 62, 66, 67, 72, 82, 92, 99, 101, 106, 110, 114, 122, 139, 152, 155, 181, 193, 196, 200, 206, 207, 211, 232, 234, 238, 239, 244, 246, 253, 254, 257, 267, 276, 279, 282, 289, 294, 297, 298, 299, 304, 308, 327, 329, 337, 344, 348, 352, 355, 366, 372, 391, 397, 401, 406, 407, 408, 416, 433, 444, 450, 455, 471, 472, 476, 485, 486, 491, 496, 514, 524, 525, 529, 537, 542, 555, 560, 573, 579, 612, 614, 623, 637, 639, 653, 694, 701, 702, 711, 721, 737, 741, 746, 753, 754, 766, 767, 769, 772, 779, 783, 795, 803, 814, 817, 823, 829, 831, 834, 856, 870, 873, 874, 875, 877, 880, 883, 885, 886, 889, 908, 912, 923, 924, 935, 937, 943, 952, 958, 961, 966, 970, 982, 996, 997, 1002, 1003, 1006, 1008, 1013, 1018, 1019, 1026, 1028, 1029, 1037, 1039, 1052, 1055, 1058, 1061, 1062, 1064, 1066, 1069, 1072, 1078, 1083, 1116, 1120, 1134, 1138, 1145, 1156, 1162, 1165, 1175, 1181, 1182, 1191, 1197, 1200, 1202, 1203, 1204, 1205, 1206, 1210, 1212, 1217, 1221, 1222, 1242, 1243, 1264, 1279, 1283, 1290, 1292, 1296, 1306, 1317, 1320, 1326, 1328, 1331, 1335, 1346, 1386, 1387, 1395, 1397, 1399, 1402, 1409, 1419, 1422, 1424, 1427, 1432, 1441, 1457, 1459, 1464, 1473, 1491, 1504, 1507, 1515, 1516, 1527, 1534, 1538, 1557, 1566, 1570, 1571, 1583, 1604, 1607, 1611, 1629, 1635, 1644, 1646, 1647, 1665, 1674, 1675, 1676, 1682, 1695, 1697, 1706, 1710, 1712, 1721, 1767, 1769, 1772, 1780, 1785, 1786, 1787, 1794, 1795, 1805, 1807, 1832, 1835, 1836, 1839, 1847, 1849, 1851, 1882, 1886, 1891, 1898, 1903, 1922, 1937, 1954, 1955, 1963, 1975, 1981, 1990, 1995, 2005, 2012, 2013, 2017, 2025, 2027, 2028, 2050, 2063, 2068, 2091, 2098, 2114, 2130, 2133, 2153, 2157, 2158, 2160, 2165, 2167, 2169, 2170, 2194, 2196, 2200, 2214, 2216, 2227, 2242, 2251, 2252, 2255, 2257, 2264, 2265, 2269, 2270, 2273, 2279, 2287, 2295, 2302, 2304, 2311, 2316, 2325, 2326, 2331, 2341, 2364, 2373, 2383, 2384, 2389, 2392, 2395, 2408, 2411, 2412, 2415, 2425, 2434, 2442, 2449, 2451, 2457, 2458, 2465, 2471, 2477, 2487, 2502, 2506, 2519, 2525, 2526, 2531, 2547, 2553, 2566, 2568, 2595, 2597, 2599, 2603, 2607, 2608, 2612, 2614, 2633, 2635, 2644, 2647, 2655, 2666, 2671, 2678, 2702, 2704, 2706, 2719, 2720, 2721, 2722, 2742, 2743, 2759, 2760, 2763, 2770, 2772, 2775, 2796, 2802, 2803, 2807, 2809, 2816, 2819, 2820, 2850, 2857, 2858, 2868, 2870, 2878, 2889, 2921, 2924, 2925, 2927, 2932, 2936, 2938, 2939, 2952, 2953, 2964, 2967, 2977, 2983, 2984, 2985, 2988, 2991, 2992, 3014, 3015, 3029, 3046, 3056, 3062, 3066, 3079, 3092, 3107, 3114, 3127, 3129, 3130, 3134, 3137, 3139, 3158, 3177, 3181, 3187, 3190, 3191, 3203, 3206, 3211, 3233, 3235, 3246, 3249, 3263, 3264, 3267, 3268, 3269, 3271, 3273, 3276, 3279, 3284, 3286, 3292, 3298, 3303, 3308, 3316, 3317, 3322, 3325, 3327, 3334, 3335, 3339, 3340, 3343, 3354, 3355, 3361, 3366, 3375, 3384, 3398, 3399, 3408, 3413, 3425, 3431, 3443, 3445, 3450, 3452, 3486, 3487, 3493, 3494, 3499, 3511, 3520, 3523, 3524, 3526, 3535, 3549, 3552, 3564, 3566, 3579, 3581, 3582, 3583, 3592, 3594, 3595]

    for i in range(len(data_sg)):

        #if i not in REACT_wrong_format:
        #    continue
        
        #if  data[i]['solution']=="error" or data[i]['solution']=='' or data[i]['solution']==None:
        
        if 'solution' not in data_sg[i]:
            continue
        
        if data_sg[i]['solution']=="error" or data_sg[i]['solution']=='' or data_sg[i]['solution']==None :
            error_indices_list.append(i)
            continue
        
        #Increment type categories
        #type_ = data[i]["example"]['type']
        
        type_ = data_sg[i]["example"]['type']
        
        '''
        if type_!="Intermediate Algebra":
            continue
        '''
        
        ind1 = unique_types.index(type_)
        total_types[ind1]+=1

        level_ = data_sg[i]["example"]['level']
        ind = unique_levels.index(level_)
        total_levels[ind]+=1

        

        #output = data[i]['solution_generator:output']
        output = data_sg[i]['solution_generator:output']
        if "boxed" not in output:
            error_sg+=1
            count+=1
            logging.info(output)
            continue
        
        gold_answer = remove_boxed(last_boxed_only_string(data_sg[i]['example']['solution'])) 
        count+=1
       

        # Process the output to get final answer
        model_final_answer = remove_boxed(last_boxed_only_string(output)) 

        '''
        if i<=15:
            logging.info("Final answer "+str(i)+":",model_final_answer)
            logging.info("Gold answer "+str(i)+":",gold_answer)
        '''    

        

        status,_,_  = is_equiv(model_final_answer,gold_answer) 

        if status==True:
            correct_levels[ind]+=1
            correct_types[ind1]+=1
            correct+=1

            correct_indices_list.append(i)
            
            if type_=="Intermediate Algebra" and data_sg[i]['example']['level']=="Level 5":
                indices_intalg.append(i)

            # Find the example from data1 [The modular setting]. Check if it is correct
            try:
                indx = questions_module_settings.index(data_sg[i]["example"]["problem"])
            except:    
                logging.info("Not in PG+SG")
                continue


            #else:
                '''
                output_module_settings = data1[indx]['solution_generator:output']
                module_final_ans = remove_boxed(last_boxed_only_string(output_module_settings)) 
                status_module,_,_  = is_equiv(module_final_ans,gold_answer) 
                if status_module == False:   #Incorrect output 
                   # Module setting gets it right compared to SG setting
                   logging.info("The analysis of wrong answers!")
                   logging.info("Question")
                   logging.info(data_sg[i]["example"]["problem"])
                   logging.info("-"*30)
                   logging.info("Gold answer")
                   logging.info(data_sg[i]["example"]["solution"])
                   logging.info("-"*30)
                   logging.info("PG+SG Output")
                   logging.info(data_sg[i]["solution_generator:input"])
                   logging.info(data_sg[i]["solution_generator:output"])
                   logging.info("-"*30)
                   logging.info(data1[indx]["response"])
                   logging.info("-"*30)
                   cj = input("Enter a key to continue")
                '''   
    
            '''
            if i<=100 and data[i]['program_executor:output']!=None:
                logging.info("-"*100)
                logging.info(data[i]['example']['problem'])
                logging.info(data[i]['example']['type'])
                logging.info(data[i]['example']['level'])
                logging.info("*"*20)
                logging.info("Ground truth sol:",data[i]['example']['solution'])
                logging.info("*"*20)
                logging.info(data[i]['solution_generator:input'])
                logging.info("*"*20)
                logging.info(data[i]['solution_generator:output'])
            '''    

            #logging.info("Correct"+str(i))
        else:
            '''
            #if type_=="Intermediate Algebra" and data[i]['example']['level']=="Level 5" and obs<=20:
                logging.info("-"*100)
                logging.info(data[i]['example']['problem'])
                logging.info(data[i]['example']['type'])
                logging.info(data[i]['example']['level'])
                logging.info("*"*20)
                logging.info("Ground truth sol:",data[i]['example']['solution'])
                logging.info("*"*20)
                logging.info(data[i]['program_generator:output'])
                logging.info(data[i]['program_executor:output'])
                logging.info("*"*20)
                logging.info(data[i]['solution_generator:input'])
                logging.info("*"*20)
                logging.info(data[i]['solution_generator:output'])
                ch = input("Press a key")
                obs +=1
            ''' 
            
            '''  
            if level_=="Level 5":
                logging.info(i)
                logging.info(data[i]["example"]['problem'])
            '''    

            false_indices_list.append(i) 
            
            
            # Find the example from data1 [The modular setting]. Check if it is correct
            try:
                indx = questions_module_settings.index(data_sg[i]["example"]["problem"])
                
            except:
                logging.info("Not in PG+SG")
                continue    
            
            if indx == -1 or indx is None:
                continue
            else:
                
                
                output_module_settings = data1[indx]['solution_generator:output']
                module_final_ans = remove_boxed(last_boxed_only_string(output_module_settings)) 
                status_module,_,_  = is_equiv(module_final_ans,gold_answer) 
                
                if status_module ==True:
                   
                   found_q +=1
                    


                   # Put it visually on a scatter plot   
                   # Module setting gets it right compared to SG setting
                   
                   lvl_key = {"Level 1":0,"Level 2":1,"Level 3":2,"Level 4":3,"Level 5":4}
                   scatter_plot_dict[data_sg[i]["example"]['type']][lvl_key[data_sg[i]["example"]['level']]] += 1
                    

                   '''
                   logging.info("The analysis of correctness!")
                   logging.info("Question")
                   logging.info(data_sg[i]["example"]["problem"])
                   logging.info("-"*30)
                   logging.info("Gold answer")
                   
                   logging.info(data_sg[i]["example"]["solution"])
                   logging.info("-"*30)
                   logging.info("SG Output")
                   logging.info(data_sg[i]["response"])
                   logging.info("-"*30)
                   logging.info(data1[indx]["response"])
                   logging.info("-"*30)
                   ch = input("Enter a key to continue")
                   '''
    

    logging.info("No of questions found:",found_q)

    # Convert the dictionary to a DataFrame
    df = pd.DataFrame(scatter_plot_dict)
    
    # Transpose the DataFrame to have subject types as index and levels as columns
    df = df.transpose()
    df.columns = ['Level 1', 'Level 2', 'Level 3', 'Level 4', 'Level 5']
    logging.info(df)


    # Plot the heatmap
    plt.figure(figsize=(10, 6))
    sns.heatmap(df, annot=True, cmap='YlGnBu', fmt='g', cbar_kws={'label': 'Count'})
    #plt.title('Distribution by Subject Type and Level of Problem (1-5) [PG+SG correct & SG wrong]')
    plt.show()





    logging.info(count)
    logging.info("Accuracy Math data:",((correct)/count)*100)
    logging.info("Total No of examples:",count)
    #logging.info("Correct indices:",correct_indices_list)
    logging.info("Incorrect Indices",false_indices_list)
    logging.info("Error indices",error_indices_list)

    logging.info("*"*50)
    logging.info("Accuracy by level:::")

    for i in range(len(unique_levels)):

        logging.info("Accuracy " + unique_levels[i]+":")
        try: 
            logging.info(correct_levels[i]/total_levels[i]*100)
        except:
            pass   
    logging.info("*"*50)
    logging.info("Accuracy by type :::")

    for i in range(len(unique_types)):

        logging.info("Accuracy " + unique_types[i]+":")
        try: 
            logging.info(correct_types[i]/total_types[i]*100)
        except:
            pass         
    logging.info(error_sg)
    #logging.info(correct_indices_list)
    #logging.info("False indices list")
    #logging.info(false_indices_list)
    logging.info(indices_intalg)
    logging.info("No of examples found",found_q)
    return
        
    

if __name__ == "__main__":

    # Call accuracy_by_level for MATH dataset accuracy
    accuracy_by_level("outputs/MATH_outputs/arxiv_pg_sg_minitest_cache.jsonl")
    
    # Accuracy for REACT 
    #accuracy_REACT("planning/REACT_output.jsonl")
    
    # Accuracy of other settings on examples for which REACT converges
    #accuracy_REACT_converged_subset("outputs/MATH_outputs/arxiv_pg_walpha_sg_minitest_cache.jsonl")
    
    # Accuracy of REACT (on converged) + PG+WA+SG on non-converged
    #combine_ES("planning/REACT_output.jsonl","outputs/MATH_outputs/arxiv_pg_walpha_sg_minitest_cache.jsonl")

    # Call accuracy_GSM() for GSM accuracy 
    #accuracy_GSM("outputs/GSM_outputs/oldprompt_results/pg_sg_oldprompt_minitest_cache.jsonl")

    # Call accuracy_MMLU for MMLU accuracy
    #accuracy_MMLU("outputs/MMLU_outputs/MMLU_pg_bing_sg_minitest_cache.jsonl")

    # Call accuracy_AQUA for AQUA accuracy
    #accuracy_AQUA("outputs/AQUA_outputs/pg_sg_minitest_cache.jsonl")


    