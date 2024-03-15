prompt = """ Read the following question to generate thought, Query for searching Bing Web Search API, that will help to solve the entire problem or specific subproblems in the question.  

Context: 
Question: When the expression $-2x^2-20x-53$ is written in the form $a(x+d)^2+e$, where $a$, $d$, and $e$ are constants, what is the sum $a+d+e$?
Type: Algebra
Level: Level 5 
Task: Search the Web to find how to complete the square using Bing Search API.
Reasoning: Since the question involves completing the square let us search how to complete the square in the Query.  
Query: How do we complete the square of a quadratic equation?


Context: 
Question: Suppose that the minimum value of $f(x) = \\cos 2x - 2a (1 + \\cos x)$ is $-\\frac{1}{2}.$  Find $a.$
Type: Precalculus
Level : Level 5 
Task: Search the web to learn how to find derivative of $f(x) = \\cos 2x - 2a (1 + \\cos x)$ .
Reasoning: Let us find the derivative by calculating f'(x).
Query: Find derivative of $f(x) = \\cos 2x - 2a (1 + \\cos x)$ wrt x.


Context: 
Question: What is the least perfect square with 3 different prime factors?
Type: Prealgebra
Level: Level 5 
We can find the smallest three prime factors possible.
Knowledge_retrieval('Retrieve knowledge/background information on which are the smallest three prime numbers')
Since we need three different prime factors, we must select the smallest three which is 2,3,5.
Then we can square each prime factor to get the least possible prime factor.
Task: Find the square of 2*3*5 using Bing Search API.
Reasoning: Since the problem requires to find 2^(2) * 3^(2) * 5^(2), we can search this on the web using Bing Search API. 
Query: What is the value of 2^(2) * 3^(2) * 5^(2)?


Context: 
Question: Let $z$ be a complex number such that $|z| = 1.$  Find the maximum value of\n\\[|1 + z| + |1 - z + z^2|.\\]
Type: Intermediate Algebra
Level: Level 5 
Task: Find the method of simplifiying complex expressions, extract similar questions using Bing Web Search API.
Reasoning: Since the problem requires |z| = 1, we can search the web on how to substitute z=x+iy and simplify a complex expression containing modulus operator.
Query: How can we substitute z=x+iy and simplify a complex expression containing the modulus operator?


Context: 
Question: Harold tosses a nickel four times.  What is the probability that he gets at least as many heads as tails?
Type: Counting & Probability
Level: Level 5 
Task: Search the web using the Bing Search API to find how to calculate probabilities of as many heads as tails in 4 coim throws.
Reasoning: We can try to get the logic of the problem by searching how to calculate probability of at least as many heads as tails in a series of coin throws.
Query: How to calculate probability of getting at least as many heads as tails?


Context: 
Question: What is the sum of all the distinct positive two-digit factors of 144?
Type: Number Theory
Level: Level 5 
Task: Find the distinct factors of 144 using the Bing Web Search API.
Reasoning : To find the sum we can first search all factors of 144.
Query: What are all factors of 144?

Context: 
Question: A circle is circumscribed about an equilateral triangle with side lengths of $6$ units each.  What is the area of the circle, in square units? Express your answer in terms of $\\pi$.
Type: Geometry
Level: Level 5 
Task: Using the Bing API to find the circumradius of an equilateral triangle with length 6.
Reasoning: To solve this problem, we can search the Bing Search API on how to find the circumradius of an equilateral triangle.
Query: How to find the circumradius of an equilateral triangle with length 6?

"""