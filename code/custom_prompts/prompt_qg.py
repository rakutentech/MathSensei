# 
prompt = """
Read the following question to generate single/multiple queries seperated by commas for searching Wolfram Alpha API/Wikipedia API that can be used to get important hints to solve the problem.

Question: What positive two-digit integer is exactly twice the sum of its digits?
Query: How to calculate decimal value of a 2 digit number using a formula?


Question: In how many ways can a President, Vice-President, and Treasurer be chosen from a group of $4$ guys and $4$ girls and at least one girl and at least one guy holds at least one of those three positions? One person cannot serve in more than one position.
Query: How to calculate number of combinations in mathematics?


Question: A regular tetrahedron is a pyramid with four faces, each of which is an equilateral triangle.\n\nLet $V$ be the volume of a regular tetrahedron whose sides each have length $1$. What is the exact value of $V^2$ ?
Query: What is the volume of a regular tetrahedron?


Question: The smallest distance between the origin and a point on the graph of $y=\\frac{1}{2}x^2-9$ can be expressed as $a$.  Find $a^2$.
Query: What is the formula for calculating the distance between two points?


Question: What, in degrees, is the measure of the largest angle in $\\triangle PQR?$\n\n[asy]\ndraw((0,0)--(-1.3,4)--(7,0)--cycle);\nlabel(\"$P$\",(-1.3,4),NW); label(\"$Q$\",(0,0),SW); label(\"$R$\",(7,0),SE);\n\nlabel(\"$6x^\\circ$\",(0,0),NE); label(\"$x^\\circ$\",(5,0),N); label(\"$3x^\\circ$\",(-.25,3));\n[/asy]
Query: What is the sum of angles in a triangle?, How to calculate the measure of lengths from coordinates of points?, How to calculate angles from the measure of sides?
"""