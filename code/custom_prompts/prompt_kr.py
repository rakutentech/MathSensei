# 
prompt = """
Read the following question, generate the background knowledge or relevant mathematical information as the context information that could be helpful for answering the question.

Question: What positive two-digit integer is exactly twice the sum of its digits?
Mathematics Problem Type: Number Theory
Level of Problem: Level 2
Knowledge Retrieval:
- The question involves understanding of number properties and basic arithmetic operations.
- A two-digit integer can be expressed as 10a + b, where a and b are its digits.
- The sum of the digits of a two-digit number is a + b.
- The condition given in the question, "twice the sum of its digits", can be expressed as 2(a + b).
- The problem is to find a two-digit number such that 10a + b = 2(a + b).

Question: In how many ways can a President, Vice-President, and Treasurer be chosen from a group of $4$ guys and $4$ girls and at least one girl and at least one guy holds at least one of those three positions? One person cannot serve in more than one position.
Mathematics Problem Type: Counting & Probability
Level of Problem: Level 4
Knowledge Retrieval:
- The question involves the concept of permutations in mathematics, specifically choosing 3 people from a group of 8 to fill 3 distinct positions.
- The order of selection matters in this case, as each position (President, Vice-President, and Treasurer) is unique.
- The formula for permutations is P(n, r) = n! / (n-r)!, where n is the total number of items, r is the number of items to choose, and "!" denotes factorial.
- In this case, n = 8 (the total number of people) and r = 3 (the number of positions to fill).
- The condition that at least one girl and at least one guy must hold at least one of the positions adds a layer of complexity to the problem. This means we must consider cases where there are 1 girl and 2 guys, 2 girls and 1 guy, and 3 girls or 3 guys.
- We need to calculate total ways of selecting without any restrictions.
- Then we can subtract the cases of all boys and all girls from above to get answer.


Question: A right circular cone is sliced into four pieces by planes parallel to its base, as shown in the figure. All of these pieces have the same height. What is the ratio of the volume of the second-largest piece to the volume of the largest piece? Express your answer as a common fraction.\n[asy]\nsize(150);\npair A, B, C, D, E, F, G, H, I, w, x, y, z;\nA=(0,0);\nB=(.25,.75);\nC=(.5,1.5);\nD=(.75,2.25);\nE=(1,3);\nF=(1.25,2.25);\nG=(1.5,1.5);\nH=(1.75,.75);\nI=(2,0);\nw=(A+I)/2;\nx=(B+H)/2;\ny=(C+G)/2;\nz=(D+F)/2;\ndraw(ellipse(w, 1, .25));\ndraw(ellipse(x, .75, .1875));\ndraw(ellipse(y, .5, .125));\ndraw(ellipse(z, .25, .0625));\ndraw(A--E--I);\n[/asy]
Mathematics Problem Type: Geometry
Level of Problem: Level 5
Knowledge Retrieval:
- Use the similarity of triangles to find the ratio of radius of the 4 pieces.
- All have same height, use volume of a cone formula to calculate volumes.


Question: Find the number of positive integers $n \\ge 3$ that have the following property: If $x_1,$ $x_2,$ $\\dots,$ $x_n$ are real numbers such that $x_1 + x_2 + \\dots + x_n = 0,$ then\n\\[x_1 x_2 + x_2 x_3 + \\dots + x_{n - 1} x_n + x_n x_1 \\le 0.\\]
Mathematics Problem Type: Intermediate Algebra
Level of Problem: Level 4
Knowledge:
- The question also involves understanding of mathematical sequences and series, specifically the concept of the sum of a series of numbers. 
- The condition given in the question, $x_1 + x_2 + \dots + x_n = 0,$ is a constraint that the sum of all the real numbers $x_1,$ $x_2,$ $\dots,$ $x_n$ is equal to zero.
- The inequality $x_1 x_2 + x_2 x_3 + \dots + x_{n - 1} x_n + x_n x_1 \le 0$ is another constraint that the sum of the product of consecutive numbers in the sequence, plus the product of the last and the first number, is less than or equal to zero.


Question: Given that\n\\begin{align*}\n\\cos x + \\cos y + \\cos z &= 0, \\\\\n\\sin x + \\sin y + \\sin z &= 0,\n\\end{align*}find\n\\begin{align*}\n&\\tan^2 x + \\tan^2 y + \\tan^2 z - (\\tan^2 x \\tan^2 y + \\tan^2 x \\tan^2 z + \\tan^2 y \\tan^2 z) \\\\\n&\\quad  - 3 \\tan^2 x \\tan^2 y \\tan^2 z.\n\\end{align*}
Mathematics Problem Type: PreCalculus
Level of Problem: Level 5
Knowledge Retrieval: 
- The question requires using the Euler representation formula a=e^(ix), b=e^(iy) , c = e^(iz).
- Find a+b+c and 1/a + 1/b + 1/c .
- Use the relations obtained to get to the desired equation using trigonometric identities.



Question: Let $S$ be the set of all real numbers $\\alpha$ such that the function \\[\\frac{x^2+5x+\\alpha}{x^2 + 7x - 44}\\]can be expressed as a quotient of two linear functions. What is the sum of the elements of $S$?
Mathematics Problem Type: Algebra
Level of Problem: Level 5
Knowledge Retrieval:
- The question requires using the factor and remainder theorem in Mathematics.
- First factorize the denominator of the expression.
- To be represented as division of linear factors, numerator should be multiple of either one of the linear factors of denominator.
- Use factor theorem to get alpha for both cases and sum them to get final answer. 


Question: Three students, with different names, line up single file. What is the probability that they are in alphabetical order from front-to-back?  Express your answer as a common fraction.
Mathematics Problem Type: PreAlgebra
Level of Problem: Level 4
Knowledge Retrieval: 
- Give names to the students A,B,C.
- Write down all possible ways to line up A,B,C. 
- Find the favourable outcome from all possible ways.
- Compute (no of favourable outcomes/total outcomes) to get probability. 


"""

prompt_GSM = """ 
Read the following question, generate the background knowledge as the context information that could be helpful for answering the question.

Question: What positive two-digit integer is exactly twice the sum of its digits?
Modules used till now:[]
Knowledge Retrieval:
- The question involves understanding of number properties and basic arithmetic operations.
- A two-digit integer can be expressed as 10a + b, where a and b are its digits.
- The sum of the digits of a two-digit number is a + b.
- The condition given in the question, "twice the sum of its digits", can be expressed as 2(a + b).
- The problem is to find a two-digit number such that 10a + b = 2(a + b).

Question: In how many ways can a President, Vice-President, and Treasurer be chosen from a group of $4$ guys and $4$ girls and at least one girl and at least one guy holds at least one of those three positions? One person cannot serve in more than one position.
Modules used till now:[]
Knowledge Retrieval:
- The question involves the concept of permutations in mathematics, specifically choosing 3 people from a group of 8 to fill 3 distinct positions.
- The order of selection matters in this case, as each position (President, Vice-President, and Treasurer) is unique.
- The formula for permutations is P(n, r) = n! / (n-r)!, where n is the total number of items, r is the number of items to choose, and "!" denotes factorial.
- In this case, n = 8 (the total number of people) and r = 3 (the number of positions to fill).
- The condition that at least one girl and at least one guy must hold at least one of the positions adds a layer of complexity to the problem. This means we must consider cases where there are 1 girl and 2 guys, 2 girls and 1 guy, and 3 girls or 3 guys.
- We need to calculate total ways of selecting without any restrictions.
- Then we can subtract the cases of all boys and all girls from above to get answer.


Question: A right circular cone is sliced into four pieces by planes parallel to its base, as shown in the figure. All of these pieces have the same height. What is the ratio of the volume of the second-largest piece to the volume of the largest piece? Express your answer as a common fraction.\n[asy]\nsize(150);\npair A, B, C, D, E, F, G, H, I, w, x, y, z;\nA=(0,0);\nB=(.25,.75);\nC=(.5,1.5);\nD=(.75,2.25);\nE=(1,3);\nF=(1.25,2.25);\nG=(1.5,1.5);\nH=(1.75,.75);\nI=(2,0);\nw=(A+I)/2;\nx=(B+H)/2;\ny=(C+G)/2;\nz=(D+F)/2;\ndraw(ellipse(w, 1, .25));\ndraw(ellipse(x, .75, .1875));\ndraw(ellipse(y, .5, .125));\ndraw(ellipse(z, .25, .0625));\ndraw(A--E--I);\n[/asy]
Modules used till now:[]
Knowledge Retrieval:
- Use the similarity of triangles to find the ratio of radius of the 4 pieces.
- All have same height, use volume of a cone formula to calculate volumes.


Question: Find the number of positive integers $n \\ge 3$ that have the following property: If $x_1,$ $x_2,$ $\\dots,$ $x_n$ are real numbers such that $x_1 + x_2 + \\dots + x_n = 0,$ then\n\\[x_1 x_2 + x_2 x_3 + \\dots + x_{n - 1} x_n + x_n x_1 \\le 0.\\]
Modules used till now:[]
Knowledge:
- The question also involves understanding of mathematical sequences and series, specifically the concept of the sum of a series of numbers. 
- The condition given in the question, $x_1 + x_2 + \dots + x_n = 0,$ is a constraint that the sum of all the real numbers $x_1,$ $x_2,$ $\dots,$ $x_n$ is equal to zero.
- The inequality $x_1 x_2 + x_2 x_3 + \dots + x_{n - 1} x_n + x_n x_1 \le 0$ is another constraint that the sum of the product of consecutive numbers in the sequence, plus the product of the last and the first number, is less than or equal to zero.


Question: Given that\n\\begin{align*}\n\\cos x + \\cos y + \\cos z &= 0, \\\\\n\\sin x + \\sin y + \\sin z &= 0,\n\\end{align*}find\n\\begin{align*}\n&\\tan^2 x + \\tan^2 y + \\tan^2 z - (\\tan^2 x \\tan^2 y + \\tan^2 x \\tan^2 z + \\tan^2 y \\tan^2 z) \\\\\n&\\quad  - 3 \\tan^2 x \\tan^2 y \\tan^2 z.\n\\end{align*}
Modules used till now:[]
Knowledge Retrieval: 
- The question requires using the Euler representation formula a=e^(ix), b=e^(iy) , c = e^(iz).
- Find a+b+c and 1/a + 1/b + 1/c .
- Use the relations obtained to get to the desired equation using trigonometric identities.



Question: Let $S$ be the set of all real numbers $\\alpha$ such that the function \\[\\frac{x^2+5x+\\alpha}{x^2 + 7x - 44}\\]can be expressed as a quotient of two linear functions. What is the sum of the elements of $S$?
Modules used till now:[]
Knowledge Retrieval:
- The question requires using the factor and remainder theorem in Mathematics.
- First factorize the denominator of the expression.
- To be represented as division of linear factors, numerator should be multiple of either one of the linear factors of denominator.
- Use factor theorem to get alpha for both cases and sum them to get final answer. 


Question: Three students, with different names, line up single file. What is the probability that they are in alphabetical order from front-to-back?  Express your answer as a common fraction.
Modules used till now:[]
Knowledge Retrieval: 
- Give names to the students A,B,C.
- Write down all possible ways to line up A,B,C. 
- Find the favourable outcome from all possible ways.
- Compute (no of favourable outcomes/total outcomes) to get probability. 

"""


prompt_MMLU = """
Read the following question, answer choices (Option A, Option B, Option C, Option D) and generate the background knowledge/useful information that could be helpful for answering the question.

Question: John found that the average of 15 numbers is 40. If 10 is added to each number then the mean of the numbers 
Option A: 50
Option B: 40 
Option C: 45
Option D: 43
Modules used till now:[]
Knowledge Retrieval: 
- The average of a set of numbers is the sum of the numbers divided by the total number of values in the set. 
- Mathematically, it is represented as: Average=Sum of numbers/Count of numbers
- We can compute how the average changes.

Question: A person is traveling at 20 km/hr and reached his destiny in 2.5 hr then find the distance? 
Option A: 16 
Option B: 50 
Option C: 20 
Option D: 40
Modules used till now:[]
Knowledge Retrieval:
- The distance traveled can be calculated using the formula: Distance=Speed*Time

Question: If a / b = 3/4 and 8a + 5b = 22,then find the value of a. 
Option A: 7/2
Option B: 3/2 
Option C: 5/2
Option D: 4/2
Modules used till now:[]
Knowledge Retrieval: 
- The question involves solving a system of equations involving both algebraic fractions and linear equations.
- Start by expressing the given ratio a/b as an equation: a/b = 3/4.
- Use this information to express one variable in terms of the other.
- Substitute this expression into the second equation, 8a + 5b = 22, and solve for the variable.
- The goal is to find the value of 'a' based on the given conditions.


Question: How many keystrokes are needed to type the numbers from 1 to 500? 
Option A: 2255
Option B: 1203 
Option C: 2344
Option D: 1109
Modules used till now:[]
Knowledge Retrieval: 
- To type the numbers from 1 to 500, consider the number of digits in each range (1-9, 10-99, 100-500).
- For the range 1-9, there are 9 single-digit numbers, requiring 9 keystrokes.
- For the range 10-99, there are 90 two-digit numbers. Each number requires 2 keystrokes, so this range requires 90 * 2 = 180 keystrokes.
- For the range 100-500, there are 401 three-digit numbers. Each number requires 3 keystrokes, so this range requires 401 * 3 = 1203 keystrokes.
- Sum up the keystrokes for each range to get the total number of keystrokes needed.

Question: Find the area of a rhombus whose side is 25 cm and one of the diagonals is 30 cm? 
Option A: 272  
Option B: 267 
Option C: 286 
Option D: 251 
Modules used till now:[]
Knowledge Retrieval:
- The area of a rhombus can be calculated using the formula: Area = (diagonal1 * diagonal2) / 2.
- For a rhombus, the diagonals bisect each other at right angles, forming four congruent right-angled triangles.
- The Pythagorean theorem can be applied to find the length of each half-diagonal using the side length and one diagonal length.
- Once the lengths of both diagonals are known, plug them into the area formula to find the area of the rhombus.
"""




prompt_AQUA = """
Read the following question and options, generate the background knowledge/useful information that could be helpful for answering the question.

Question: John found that the average of 15 numbers is 40. If 10 is added to each number then the mean of the numbers Options:['A)50', 'B)45', 'C)65', 'D)78', 'E)64']
Modules used till now:[]
Knowledge Retrieval: 
- The average of a set of numbers is the sum of the numbers divided by the total number of values in the set. 
- Mathematically, it is represented as: Average=Sum of numbers/Count of numbers
- We can compute how the average changes.

Question: A person is traveling at 20 km/hr and reached his destiny in 2.5 hr then find the distance? Options:['A)53 km' 'B)55 km', 'C)52 km', 'D)60 km', 'E)50 km'])
Modules used till now:[]
Knowledge Retrieval:
- The distance traveled can be calculated using the formula: Distance=Speed*Time

Question: If a / b = 3/4 and 8a + 5b = 22,then find the value of a. Options:['A)1/2', 'B)3/2', 'C)5/2', 'D)4/2', 'E)7/2']
Modules used till now:[]
Knowledge Retrieval: 
- The question involves solving a system of equations involving both algebraic fractions and linear equations.
- Start by expressing the given ratio a/b as an equation: a/b = 3/4.
- Use this information to express one variable in terms of the other.
- Substitute this expression into the second equation, 8a + 5b = 22, and solve for the variable.
- The goal is to find the value of 'a' based on the given conditions.


Question: How many keystrokes are needed to type the numbers from 1 to 500? Options:['A)1156', 'B)1392', 'C)1480', 'D)1562', 'E)1788']
Modules used till now:[]
Knowledge Retrieval: 
- To type the numbers from 1 to 500, consider the number of digits in each range (1-9, 10-99, 100-500).
- For the range 1-9, there are 9 single-digit numbers, requiring 9 keystrokes.
- For the range 10-99, there are 90 two-digit numbers. Each number requires 2 keystrokes, so this range requires 90 * 2 = 180 keystrokes.
- For the range 100-500, there are 401 three-digit numbers. Each number requires 3 keystrokes, so this range requires 401 * 3 = 1203 keystrokes.
- Sum up the keystrokes for each range to get the total number of keystrokes needed.

Question: Find the area of a rhombus whose side is 25 cm and one of the diagonals is 30 cm? Options: ["A)272 sq.cm", "B)267 sq.cm", "C)286 sq.cm", "D)251 sq.cm", "E)600 sq.cm" ]
Modules used till now:[]
Knowledge Retrieval:
- The area of a rhombus can be calculated using the formula: Area = (diagonal1 * diagonal2) / 2.
- For a rhombus, the diagonals bisect each other at right angles, forming four congruent right-angled triangles.
- The Pythagorean theorem can be applied to find the length of each half-diagonal using the side length and one diagonal length.
- Once the lengths of both diagonals are known, plug them into the area formula to find the area of the rhombus.
"""