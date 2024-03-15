import os
import sys
import json
import argparse
import random
from tqdm import tqdm
import sys

# add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 



stry = """from sympy import *
# Define the number of beads each person has
walter_green = 476
walter_red = 32
agnes_green = 104
agnes_red = 16
holly_green = 281
print("Holly green:", holly_green)"""

str2 = "from sympy import *\n# Define the magnitudes of the vectors\nv_mag = 3\nw_mag = 4\n# The dot product of two vectors is equal to the product of their magnitudes and the cosine of the angle between them.\n# The minimum value of the dot product occurs when the angle between the vectors is 180 degrees (or pi radians), in which case the cosine of the angle is -1.\nmin_dot_product = v_mag * w_mag * cos(pi)\nprint(\"Minimum dot product:\", min_dot_product)"
#print(len(str2))

str3 = "from sympy import *\n# Define the magnitudes of the vectors\nv_mag = 3\nw_mag = 4\n# The dot product of two vectors is equal to the product of their magnitudes and the cosine of the angle between them.\n# The minimum value of the dot product occurs when the angle between the vectors is 180 degrees (or pi radians), in which case the cosine of the angle is -1.\nmin_dot_product = v_mag * w_mag * cos(pi)\nprint(\"Minimum dot product:\", min_dot_product)"
#print(len(str3))

str4 ="from sympy import *\n# Given values\nleg1 = 3\nleg2 = 4\n# The hypotenuse of the triangle is the side of the square\nhypotenuse = sqrt(leg1**2 + leg2**2)\nprint(\"Hypotenuse:\",hypotenuse)\n# The area of the square is the hypotenuse squared\narea_square = hypotenuse**2\nprint(\"Area of square:\",area_square)\n# The area of the triangle is 1/2 * base * height\narea_triangle = Rational(1, 2) * leg1 * leg2\nprint(\"Area of triangle:\",area_triangle)\n# The area of the pentagon is the area of the square minus the area of the triangle\narea_pentagon = area_square - area_triangle\nprint(\"Area of pentagon:\",area_pentagon)"
#print(len(str4))

str8 ='''from sympy import *
# Define the function
def f(x):
    if x >= 0:
        return -x**(Rational(1, 3))
    else:
        return x**2
# Calculate f(f(f(f(512))))
ans = f(f(f(f(512))))
print("Answer:",ans)
'''


str5 = '''
from sympy import *
# Define the fraction
frac = Rational(1, 1 + sqrt(2) - sqrt(3))
# Rationalize the denominator
denom = simplify((1 + sqrt(2) + sqrt(3)) * (1 + sqrt(2) - sqrt(3)))
num = frac * denom
# Simplify the numerator
simplified_num = simplify(num)
print("Simplified numerator:", simplified_num)
# Write the result in the desired form
a = simplified_num.coeff(sqrt(2))
b = simplified_num.coeff(sqrt(3))**2
c = simplified_num.coeff(1)
result = (sqrt(2) + a + sqrt(b))/c
print("Result:", result)
# Calculate a+b+c
sum_abc = a + b + c
print("a+b+c:", sum_abc)
'''

str6 = b'from sympy import *\n# Given values\nleg1 = 3\nleg2 = 4\n# The hypotenuse of the triangle is the side of the square\nhypotenuse = sqrt(leg1**2 + leg2**2)\n# The area of the square is the square of the hypotenuse\narea_square = hypotenuse**2\n# The area of the triangle is 1/2 * base * height\narea_triangle = Rational(1, 2) * leg1 * leg2\n# The area of the pentagon is the area of the square minus the area of the triangle\narea_pentagon = area_square - area_triangle\nprint(\"Area of Pentagon:\", area_pentagon)'

#unicode_string = str6.decode("utf-8")
#print(len(str6))


'''
print("Raw str",str6)
print("Len raw", len(str6))
# Decode the byte string into a Unicode string
unicode_string = str6.encode("utf-8")

print("Unicode",unicode_string)
print("Len unicode",len(unicode_string))
'''
def safe_execute_t(code_string: str, keys=None):

    import sys
    from io import StringIO
    import re
    #code_string = re.sub(r'[\x00-\x1f]', '', code_string)

    #print("Code string:", code_string)
    #print("Original length of code string", len(code_string))

    # Code string after strip
    import codecs
    new_code_string = codecs.decode(code_string, 'unicode_escape')
    #print("Length of code string after conversion:", len(new_code_string))

    output = None
    error_message = None

    # Executing the code and capturing the output
    old_stdout = sys.stdout
    old_stderr = sys.stderr

    try:
        # Redirect stdout and stderr to capture the output and error message
        sys.stdout = StringIO()
        sys.stderr = StringIO()

        # Execute the code
        exec(new_code_string)

        # Get the captured output
        output = sys.stdout.getvalue()

    except Exception as e:
        error_message = str(e)

    # Restore the original stdout and stderr
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    return output, error_message



def call_executor(code_string):

    import sys
    from io import StringIO

    # Python code stored as a string
    '''
    code_string = """
    a = 5
    b = 10
    sum = a + b
    print(f"The sum of {a} and {b} is: {sum}")
    """
    '''

    print("Length:",len(code_string))

    # Executing the code and capturing the output
    output=None

        # Executing the code and capturing the output
    old_stdout = sys.stdout

    
    # Redirect stdout to capture the output
            
    sys.stdout = StringIO()

    # Execute the code
    exec(code_string)
        

    # Get the captured output
    output = sys.stdout.getvalue()

    #except:
     #       pass
        
        # Restore the original stdout
    sys.stdout = old_stdout
    print("Captured Output:")
    print(output)


def safe_execute(code_string: str, keys=None):

    import sys
    from io import StringIO
    import signal
    import time
    import re
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
        exec(new_code_string)

        # Get the captured output
        output = sys.stdout.getvalue()

    except Exception as e:
        error_message = str(e)
    
    # Reset alarm
    signal.alarm(0)

    # Restore the original stdout and stderr
    sys.stdout = old_stdout
   

    return output, error_message    

def wolfram_alpha_search(query):
        
        import wolframalpha
  
        # Taking input from user
        # Query

        
        queries = query.split(",")
        response=""

        # Wolfram App id obtained by the above steps
        app_id = "YY7PGQ-XTHGP2R4HE"
        
        # Instance of wolf ram alpha 
        # client class
        client = wolframalpha.Client(app_id)
        pf = "Wolfram_Alpha response:\n"
        final=""
       
        for q in queries:
            print(q)
            # Stores the response from 
            # wolf ram alpha
            try:
                res = client.query(q)
               
                solution =""
                for i in res.pods:
                     
                     if i['@title']=='Solution':
                          solution = (i['subpod']['img']['@title'])
                         
                          
                
                assumption = next(res.pods).text
                answer = next(res.results).text
                #solution = next(res.solutions).text
                #print("Solution:",solution)
                   
                final = final + f"\nAssumption: {assumption} \nAnswer: {answer}, {solution}"

            except:
                final=final+""
        
        
        if len(final) > 0 and final!= "" and final!=None:
            response += f"\n\n Wolfram_Alpha response:\: {final}"
            response = response.strip()


   

        return query,response

'''
query = "x^3 - 16 x = 0 "
_,response = (wolfram_alpha_search(query))
print("Response, Wolfram Alpha",response)
'''
code_string1 = '''from sympy import *
# Define the variables
a, b, c, d = symbols('a b c d')
# Define the function
F = a**b + c**d
# Substitute the given values into the function
F_sub = F.subs({a:4, c:2, d:3})
# Solve the equation F_sub = 12 for b
solution = solve(F_sub - 12, b)
print("Solution:",solution)
# Print the solution
print('b =', solution[0])'''

'''
code_string2 = "from sympy import *\\nfrom sympy.abc import x, y\\n\\n# Define the three expressions\\nexpr1 = x*y\\nexpr2 = 1 - x - y + x*y\\nexpr3 = x + y - 2*x*y\\n\\n# Define the constraints\\nconstraints = [x >= 0, y >= x, y <= 1]\\n\\n# Find the minimum of each expression under the constraints\\nmin1 = minimize(expr1, constraints)\\nmin2 = minimize(expr2, constraints)\\nmin3 = minimize(expr3, constraints)\\n\\n# The minimum possible value of the largest of the three expressions is the maximum of the three minimum values\\nmin_possible_value = max(min1, min2, min3)\\n\\nprint(\\\"Minimum possible value:\\\", min_possible_value)"

code_string3 = "from sympy import *\n# Define the variables\nx, y = symbols('x y')\n# Define the expressions\nexpr1 = x*y\nexpr2 = 1 - x - y + x*y\nexpr3 = x + y - 2*x*y\n# Create a list of the expressions\nexpr_list = [expr1, expr2, expr3]\n# Use the minimize function from the scipy library to find the minimum possible value of the largest of the expressions\nmin_value = N(minimize(lambda x, y: max(expr1.subs({x:x, y:y}), expr2.subs({x:x, y:y}), expr3.subs({x:x, y:y})), [0, 0]))\nprint(\"Minimum possible value:\", min_value)"
code_string4 = "from sympy import *\n# Given values\nleg1 = 3\nleg2 = 4\n# The hypotenuse of the triangle is the side of the square\nhypotenuse = sqrt(leg1**2 + leg2**2)\nprint(\"Hypotenuse:\",hypotenuse)\n# The area of the square is the square of the hypotenuse\narea_square = hypotenuse**2\nprint(\"Area of square:\",area_square)\n# The area of the triangle is 1/2 * base * height\narea_triangle = Rational(1, 2) * leg1 * leg2\nprint(\"Area of triangle:\",area_triangle)\n# The area of the pentagon is the area of the square minus the area of the triangle\narea_pentagon = area_square - area_triangle\nprint(\"Area of pentagon:\",area_pentagon)"
code_string5 =r'from sympy import *\n# Given values\nleg1 = 3\nleg2 = 4\n# The hypotenuse of the triangle is the side of the square\nhypotenuse = sqrt(leg1**2 + leg2**2)\nprint(\"Hypotenuse:\",hypotenuse)\n# The area of the square is the square of the hypotenuse\narea_square = hypotenuse**2\nprint(\"Area of square:\",area_square)\n# The area of the triangle is 1/2 * base * height\narea_triangle = Rational(1, 2) * leg1 * leg2\nprint(\"Area of triangle:\",area_triangle)\n# The area of the pentagon is the area of the square minus the area of the triangle\narea_pentagon = area_square - area_triangle\nprint(\"Area of pentagon:\",area_pentagon)'
import codecs

#print(len(codecs.decode(code_string5, 'unicode_escape')))
#print(len(code_string4))

call_executor(codecs.decode(code_string2, 'unicode_escape'))

'''

# Example code str

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

data = read_jsonl_file("/Users/debrup/Desktop/math_experiment/math_results/math/eacl_pglibrary_sg_minitest_cache.jsonl")
#print(data[285]['program'])


import matplotlib
matplotlib.use('Agg')

'''
count = 0
indices = []
for i in range(0,285):

    num_refines = data[i]["num_refines"]
    example_code = data[i]["refine_round"+str(num_refines)]['code']
    try :
        j = data[i]["response"].index("Python output:")
    except:
        continue    
    
    out = data[i]["response"][j:]
    #print(example_code)

    output, error_message = safe_execute(example_code)
    if output == None:
        print(output)
    if output!=None:
      
       if  out!= output :
          print("W:",output)
          indices.append(i)

            
    count+=1


'''





example_code = '''
# Python Code
from sympy import symbols, Eq, solve

# Define variables
ten_place_digit, unit_place_digit = symbols('ten_place_digit unit_place_digit')

# Create equations based on the given conditions
equation1 = Eq(unit_place_digit, 4 * ten_place_digit)
equation2 = Eq(ten_place_digit + unit_place_digit, 10)

# Solve the system of equations
solution = solve((equation1, equation2), (ten_place_digit, unit_place_digit))

# Extract the values for ten's and unit's place digits
ten_place_value = solution[ten_place_digit]
unit_place_value = solution[unit_place_digit]

# Construct the two-digit number
two_digit_number = 10 * ten_place_value + unit_place_value

print(f"The two-digit number is {two_digit_number}")


'''



print(example_code)

# Call the safe_execute function

output, error_message = safe_execute(example_code)
print("Output:", output)
print("Error Message:", error_message)

#print("INDICES",indices)

