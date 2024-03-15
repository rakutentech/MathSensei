prompt = """
Read the following question to generate queries seperated by commas for searching Wolfram Alpha API, that is being used to make specific calculations or solving specific problems. The queries should be mostly mathematical rather than natural language. 

Question: What positive two-digit integer is exactly twice the sum of its digits?
Knowledge:
- The question involves understanding of number properties and basic arithmetic operations.
- A two-digit integer can be expressed as 10a + b, where a and b are its digits.
- The sum of the digits of a two-digit number is a + b.
- The condition given in the question, "twice the sum of its digits", can be expressed as 2(a + b).
- The problem is to find a two-digit number such that 10a + b = 2(a + b).
Query: 
10a + b = 2(a + b)


Question: In how many ways can a President, Vice-President, and Treasurer be chosen from a group of $4$ guys and $4$ girls and at least one girl and at least one guy holds at least one of those three positions? One person cannot serve in more than one position.
Knowledge:
- The question involves the concept of permutations in mathematics, specifically choosing 3 people from a group of 8 to fill 3 distinct positions.
- The order of selection matters in this case, as each position (President, Vice-President, and Treasurer) is unique.
- The formula for permutations is P(n, r) = n! / (n-r)!, where n is the total number of items, r is the number of items to choose, and "!" denotes factorial.
- In this case, n = 8 (the total number of people) and r = 3 (the number of positions to fill).
- The condition that at least one girl and at least one guy must hold at least one of the positions adds a layer of complexity to the problem. This means we must consider cases where there are 1 girl and 2 guys, 2 girls and 1 guy, and 3 girls or 3 guys.
- We need to calculate total ways of selecting without any restrictions.
- Then we can subtract the cases of all boys and all girls from above to get answer.
Query: 
8p3,4p3


Question: A regular tetrahedron is a pyramid with four faces, each of which is an equilateral triangle.\n\nLet $V$ be the volume of a regular tetrahedron whose sides each have length $1$. What is the exact value of $V^2$ ?
Knowledge:
- A regular tetrahedron is a type of pyramid with four faces, each of which is an equilateral triangle. This means all sides and angles are equal.
- The formula for the volume of a regular tetrahedron with side length a is V = a³/ (6√2).
- In this case, the side length a is given as 1. 
- The question asks for the square of the volume, so we need to square the result of the volume calculation.
Query: 
1^3/(6*sqrt(2)),(1^3/(6*sqrt(2)))^2



Question: The smallest distance between the origin and a point on the graph of $y=\\frac{1}{2}x^2-9$ can be expressed as $a$.  Find $a^2$.
Knowledge:
- The question involves the concept of distance between two points in a coordinate system. 
- The distance between the origin and a point (x, y) on the graph is given by the formula √(x^2 + y^2). 
- Minimizing (x^2 + y^2) is same as minimizing √(x^2 + y^2).  
- Substitute y = 1/2x^2 - 9 into the equation to get x^2 + (1/2x^2 - 9)^2. 
- Take derivative of above equation and set it to 0.
Query: 
D[x^2 + (1/2x^2 - 9)^2], x^3 - 16 x == 0


Question: What, in degrees, is the measure of the largest angle in $\\triangle PQR?$\n\n[asy]\ndraw((0,0)--(-1.3,4)--(7,0)--cycle);\nlabel(\"$P$\",(-1.3,4),NW); label(\"$Q$\",(0,0),SW); label(\"$R$\",(7,0),SE);\n\nlabel(\"$6x^\\circ$\",(0,0),NE); label(\"$x^\\circ$\",(5,0),N); label(\"$3x^\\circ$\",(-.25,3));\n[/asy]
Knowledge:
- The question involves the concept of angles in a triangle.
- In a triangle, the sum of the angles is always 180 degrees.
- The angles in triangle PQR are given as 6x, x, and 3x degrees.
- The largest angle in a triangle is the one with the highest value when the values of x are substituted into the expressions for the angles.
Query: 
6 x + 3 x + x == 180

"""

