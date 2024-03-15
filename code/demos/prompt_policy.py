
prompt = """
You need to act as a policy model, that given a question, determines the sequence of modules that can be executed sequentially to solve the question. 

The modules are defined as follows:

- wolfram_alpha_search: This module calls the Wolfram_Alpha API module to solve the given question or intermediate steps in the question. The Wolfram Alpha API is most useful when there is a explicit mathematical object in the question, and requires some form of processing such as solving equations, calling functions, finding equations, etc. 

- bing_search: This module retrieves similar questions, background knowledge, useful information for the given question by using the Bing Web Search API. By default, bing_search is used once at the start of solving every question.

- python_generator_refine_executor: This module generates an executable python program that can solve the given question using the Sympy library and executes the code using a python interpreter. It takes in the question and possible context and produces an executable python program. In case of syntax errors, it also refines the code till it is free of errors. 

- solution_generator: This module generates a detailed solution to the question based on the already generated context. Normally, 'solution_generator' will incorporate the information from 'wolfram_alpha_search','bing_search','python_generator_refine_executor'. It is always the last module to be executed.


Below are some examples that map the problem to the modules.

Question: Find $q(x)$ if the graph of $\\frac{4x-x^3}{q(x)}$ has a hole at $x=-2$, a vertical asymptote at $x=1$, no horizontal asymptote, and $q(3) = -30$.
Mathematics Problem Type: Intermediate Algebra
Level of Problem: Level 4
Thought: Always use 'bing_search' as the first module. It contains math objects like functions, so we can use 'wolfram_alpha_search' to retrieve mathematical information. Then we can use 'python_generator_refine_executor' to perform complex computations. Finally, 'solution_generator' is always the last module.
Modules: ['bing_search','wolfram_alpha_search','python_generator_refine_executor, 'solution_generator']

Question: Find the vector $\\mathbf{v}$ such that\n\\[\\mathbf{i} \\times [(\\mathbf{v} - \\mathbf{j}) \\times \\mathbf{i}] + \\mathbf{j} \\times [(\\mathbf{v} - \\mathbf{k}) \\times \\mathbf{j}] + \\mathbf{k} \\times [(\\mathbf{v} - \\mathbf{i}) \\times \\mathbf{k}] = \\mathbf{0}.\\]
Mathematics Problem Type: Precalculus
Level of Problem: Level 4
Thought:  Always use 'bing_search' as the first module. We can simply use 'python_generator_refine_executor' to solve the vector equation. Then we can call 'wolfram_alpha_search' to continue computations got from 'python_generator_refine_executor'. Finally, 'solution_generator' is always the last module.
Modules: ['bing_search','python_generator_refine_executor','wolfram_alpha_search','solution_generator']

Question: Determine the number of ways to arrange the letters of the word ELEVEN.
Mathematics Problem Type: Counting & Probability
Level of Problem: Level 2
Thought: Always use 'bing_search' as the first module. This problem requires only 'solution_generator'.
Modules: ['bing_search','solution_generator']

Question: If the quadratic $x^2+6mx+m$ has exactly one real root, find the positive value of $m$.
Mathematics Problem Type: Algebra
Level of Problem: Level 5
Thought: Always use 'bing_search' as the first module. There is also an equation in the question which can be solved using 'wolfram_alpha_search'. Finally, 'solution_generator' is always the last module.   
Modules: ['bing_search','wolfram_alpha_search','solution_generator']

Question: How many different prime factors are in the prime factorization of $117\\cdot119$?
Mathematics Problem Type: Prealgebra
Level of Problem: Level 3
Thought: Always use 'bing_search' as the first module. We can directly use 'python_generator_refine_executor' to get the prime factorization of $117\\cdot119$. Finally, 'solution_generator' is always the last module.
Modules: ['bing_search', 'python_generator_refine_executor','solution_generator']

Question: Find the remainder when $91145 + 91146 + 91147 + 91148$ is divided by 4."
Mathematics Problem Type: Number Theory
Level of Problem: Level 1
Thought: Always use 'bing_search' as the first module. We can simply use 'wolfram_alpha_search' to find the remainder. Finally, 'solution_generator' is always the last module.
Modules: ['bing_search','wolfram_alpha_search','solution_generator']

"""


'''
Question: How many of the letters in MATHCOUNTS have a horizontal line of symmetry?
Mathematics Problem Type: Geometry
Level of Problem: Level 4
Thought: This problem requires understanding if each letter has a horizontal line of symmetry. This will be more suited for natural language solutions. 
Modules: ['knowledge_retrieval','solution_generator']
'''