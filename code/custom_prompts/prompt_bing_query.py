prompt = """ Read the following question to generate thought,Query for searching Bing Web Search API, that will help to solve the entire problem or specific subproblems in the question.  

Question: When the expression $-2x^2-20x-53$ is written in the form $a(x+d)^2+e$, where $a$, $d$, and $e$ are constants, what is the sum $a+d+e$?
Modules used till now: []
Mathematics Problem Type: Algebra
Level of Problem: Level 5 
Thought: Since the question involves completing the square let us search how to complete the square in the Query.  
Query: How do we complete the square of a quadratic equation?

Question: Suppose that the minimum value of $f(x) = \\cos 2x - 2a (1 + \\cos x)$ is $-\\frac{1}{2}.$  Find $a.$
Modules used till now: []
Mathematics Problem Type: Precalculus
Level of Problem: Level 5 
Thought: Since the question involves cos2x we can search the formula for cos2x.
Query: What is the formula for cos2x?


Question: What is the least perfect square with 3 different prime factors?
Modules used till now: [Knowledge Retrieval]
Mathematics Problem Type: Prealgebra
Level of Problem: Level 5 
Knowledge Retrieval: 
- Since we need three different prime factors, we must select the smallest three which is 2,3,5.
- Then we can square each prime factor to get the least possible prime factor.
Thought: Since the problem requires to find 2^(2) * 3^(2) * 5^(2), we can search this on the web. 
Query: What is the value of 2^(2) * 3^(2) * 5^(2)?

Question: Let $z$ be a complex number such that $|z| = 1.$  Find the maximum value of\n\\[|1 + z| + |1 - z + z^2|.\\]
Modules used till now: []
Mathematics Problem Type: Intermediate Algebra
Level of Problem: Level 5 
Thought: Since the problem requires |z| = 1, we can search the web on how to substitute z=x+iy and simplify a complex expression containing modulus operator.
Query: How can we substitute z=x+iy and simplify a complex expression containing the modulus operator?

Question: Harold tosses a nickel four times.  What is the probability that he gets at least as many heads as tails?
Modules used till now: []
Mathematics Problem Type: Counting & Probability
Level of Problem: Level 5 
Thought: We can try to get the logic of the problem by searching how to calculate probability of at least as many heads as tails in a series of coin throws.
Query: How to calculate probability of getting at least as many heads as tails?

Question: What is the sum of all the distinct positive two-digit factors of 144?
Modules used till now: []
Mathematics Problem Type: Number Theory
Level of Problem: Level 5 
Thought: To find the sum we can first search all factors of 144.
Query: What are all factors of 144?


Question: A circle is circumscribed about an equilateral triangle with side lengths of $6$ units each.  What is the area of the circle, in square units? Express your answer in terms of $\\pi$.
Modules used till now: []
Mathematics Problem Type: Geometry
Level of Problem: Level 5 
Thought: To solve this problem, we can search how to find the circumradius of an equilateral triangle.
Query: How to find the circumradius of an equilateral triangle?

"""

prompt_AQUA = """
Read the following question to generate thought,Query for searching Bing Web Search API, that will help to solve the entire problem or specific subproblems in the question.  

Question: John found that the average of 15 numbers is 40. If 10 is added to each number then the mean of the numbers Options:['A)50', 'B)45', 'C)65', 'D)78', 'E)64']
Modules used till now: []
Thought: Since the question involves finding the average let us search what is the definition of average of 15 numbers.  
Query: How do we find average of 15 numbers?

Question: A person is traveling at 20 km/hr and reached his destiny in 2.5 hr then find the distance? Options:['A)53 km' 'B)55 km', 'C)52 km', 'D)60 km', 'E)50 km'])
Modules used till now: []
Thought: We can find the formula for the speed in related to distance and time.
Query: What is the formula for calculating speed in relation of distance and time?

Question: If a / b = 3/4 and 8a + 5b = 22,then find the value of a. Options:['A)1/2', 'B)3/2', 'C)5/2', 'D)4/2', 'E)7/2']
Modules used till now: []
Thought: We can search how to solve a system of linear equations on the web.
Query: How to find a system of linear equations?

Question: How many keystrokes are needed to type the numbers from 1 to 500? Options:['A)1156', 'B)1392', 'C)1480', 'D)1562', 'E)1788']
Modules used till now: []
Thought: We can search how many 1 digit, 2 digit and 3 digit numbers are there from 1 to 500?
Query: How many 1 digit, 2 digit and 3 digit numbers are there from 1 to 500?

Question: Find the area of a rhombus whose side is 25 cm and one of the diagonals is 30 cm? Options: ["A)272 sq.cm", "B)267 sq.cm", "C)286 sq.cm", "D)251 sq.cm", "E)600 sq.cm" ]
Modules used till now: []
Thought: What is the formula for area of a rhombus with one side and one diagonal given.
Query: Find the area of a rhombus with one side and one diagonal given.
"""

prompt_MMLU = """ 
Read the following question and answer choices (Option A, Option B, Option C, Option D) to generate thought, Query for searching Bing Web Search API, that will help to solve the entire problem or specific subproblems in the question.  
Question: Statement 1 | Every element of a group generates a cyclic subgroup of the group. Statement 2 | The symmetric group S_10 has 10 elements.
Option A: True, True
Option B: True, False
Option C: False, True
Option D: False, False
Modules used till now: []
Thought: Let us search if every element of a group generates a cyclic subgroup of the group. We can also search for the symmetric group S_10.
Query: Find what is the symmetric group S_10.

Question: Find the characteristic of the ring 2Z.
Option A: 0
Option B: 3
Option C: 12
Option D: 30
Modules used till now: []
Thought: Lets find what is meant by the characteristic of the ring 2Z.
Query: Find the characteristic of the ring 2Z.

Question: Let A be the set of all ordered pairs of integers (m, n) such that 7m + 12n = 22. What is the greatest negative number in the set B = {m + n : (m, n) \in A}?
Option A: -5
Option B: -4
Option C: -3
Option D: -2
Modules used till now: []
Thought: We can find when does 7m + 12n = 22 hold for integers (m, n)?
Query: Find the set A of all ordered pairs (m, n) such that 7m + 12n = 22.

Question: Select the best translation into predicate logic.George borrows Hector's lawnmower. (g: George; h: Hector; l: Hector's lawnmower; Bxyx: x borrows y from z)
Option A: Blgh
Option B: Bhlg
Option C: Bglh
Option D: Bghl
Modules used till now: []
Thought: To translate the statement "George borrows Hector's lawnmower" into predicate logic, we can use the predicate Bxyz, where x borrows y from z.
Query: Translate the statement "George borrows Hector's lawnmower" into predicate logic using the predicate Bxyz:x borrows y from z.

Question: The variable $x$ varies directly as the square of $y$, and $y$ varies directly as the cube of $z$. If $x$ equals $-16$ when $z$ equals 2, what is the value of $x$ when $z$ equals $\frac{1}{2}$?
Option A: -1
Option B: 16
Option C: -\frac{1}{256}
Option D: \frac{1}{16}
Modules used till now: []
Thought: Let us find how to express x in terms of z from the given context.
Query: how to express y in terms of z if y = z^3 and x=y^3.
"""

