'''
from sympy import *
# Define the variables
a, b, c, d = symbols('a b c d')
# Define the matrices
matrix1 = Matrix([[a, b], [c, d]])
matrix2 = Matrix([[c, a], [d, b]])
# Define the equation
eq = Eq(matrix1**2, matrix2)
print("Equation:",eq)
# Solve the equation
sol = solve(eq, (a, b, c, d))
print("Solution:",sol)
# The number of ordered quadruples is the length of the solution
num_quadruples = len(sol)
print("Number of ordered quadruples:",num_quadruples)'''

def wolfram_alpha_search(question):
        
        import wolframalpha
  
        # Taking input from user
        
        # App id obtained by the above steps
        app_id = "YY7PGQ-XTHGP2R4HE"
        
        # Instance of wolf ram alpha 
        # client class
        client = wolframalpha.Client(app_id)
        
        # Stores the response from 
        # wolf ram alpha
        res = client.query(question)
        try: 
          assumption = next(res.pods).text
          answer = next(res.results).text

        except:
          return None       
        return f"Assumption: {assumption} \nAnswer: {answer}"

def get_wiki_summary(query):
        import wikipedia
        page = get_closest_wikipage(query)
        #print(page)
        summary = page.summary
        summary = summary.split(".")
        print(len(summary))
        print(summary[:6])
      
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
        


def get_content():
       
        from bs4 import BeautifulSoup
        import requests

        url = "https://en.wikipedia.org/wiki/Ryan_Gosling"  # replace with your URL
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Get all the text in the webpage
        text = soup.get_text()
        #print(text)
        # Split the text by line
        lines = text.splitlines()
        print(lines[1000:])

        # Get the first few lines
        #first_few_lines = lines[:20]  # replace 5 with the number of lines you want

        #print('\n'.join(first_few_lines))
    
        
        
    

#call_google("Ryan Gosling")
#get_content()
#get_wiki_summary("How to calculate decimal value of a 2 digit number using a formula?")

#print(wolfram_alpha_search("How to find the number of solutions to an equation"))
#print(get_wiki_summary("What is the symmetry in equations?"))

from sympy import *
# Define the variables
x, y = symbols("x y")
# Define the expressions
expr1 = x*y
expr2 = 1 - x - y + x*y
expr3 = x + y - 2*x*y
# Find the maximum of the three expressions
max_expr = Max(expr1, expr2, expr3)
print("Max expression:", max_expr)
