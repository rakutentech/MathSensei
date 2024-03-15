# chameleon
prompt_pot = """ Given the question and all the context, generate the solution to the given mathematical problem. You should give concise solutions using the context. Finally, conclude the answer in the format of "the answer is [ANSWER]", where [ANSWER] is a short value. For example, "the answer is 67", "the answer is (2,3)", etc. Only use information from context. Do not output new information.

Question: An amusement park charges an entry fee of $\\$2.25$ plus $\\$1.50$ for each ride. If Simon spent a total of $\\$12.75$, how many rides did he pay for?

Python generator:
from sympy import *
# Define the variables
x = symbols('x')
# Equation for the problem
eq = Eq(2.25 + 1.5*x, 12.75)
print("Equation:",eq)
# Solve the equation
sol = solve(eq, x)
print("Solution x:",sol)
# The number of rides Simon paid for
rides = sol[0]
print("Number of rides:",rides)

Python output:
Equation: Eq(1.5*x + 2.25, 12.75)
Solution x: [7.00000000000000]
Number of rides: 7.00000000000000
Solution:
- $12.75 - $2.25 = $10.50$
- $10.50 ÷ $1.50 = 7$
- Therefore, the answer is $\\boxed{7}$.


Question: Walter, Agnes, and Holly are making beaded lizards. Walter has 476 green beads and 32 red beads. Agnes has 104 green beads and 16 red beads. Holly has 281 green beads and 80 red beads. They all share their beads so as to make the largest possible number of lizards.  If a beaded lizard requires 94 green beads and 16 red beads, what is the number of green beads left over?

Python generator:
from sympy import *
# Define the number of beads each person has
walter_green = 476
walter_red = 32
agnes_green = 104
agnes_red = 16
holly_green = 281
holly_red = 80
# Define the number of beads required for a lizard
lizard_green = 94
lizard_red = 16
# Calculate the total number of beads
total_green = walter_green + agnes_green + holly_green
total_red = walter_red + agnes_red + holly_red
print("Total green beads:", total_green)
print("Total red beads:", total_red)
# Calculate the number of lizards they can make
num_lizards = min(total_green // lizard_green, total_red // lizard_red)
print("Number of lizards:", num_lizards)
# Calculate the number of green beads left over
green_leftover = total_green - num_lizards * lizard_green
print("Green beads left over:", green_leftover)

Python output:
Total green beads: 861
Total red beads: 128
Number of lizards: 8
Green beads left over: 109

Solution:
- Total green beads: $476 + 104 + 281 = 861$
- Total red beads: $32 + 16 + 80 = 128$
- Number of lizards they can make: $min(861 ÷ 94, 128 ÷ 16) = 8$
- Green beads left over: $861 - 8 * 94 = 109$
- Therefore, the answer is $\\boxed{109}$.


Question: How many of the following numbers are factors of 34 or multiples of 7?\n\n1, 2, 3, 4, 8, 14, 17, 29, 56, 91

Python generator:
from sympy import *
# Define the list of numbers
numbers = [1, 2, 3, 4, 8, 14, 17, 29, 56, 91]
# Initialize the count of factors of 34 or multiples of 7
count = 0
# Iterate over the numbers
for num in numbers:
    # Check if the number is a factor of 34 or a multiple of 7
    if 34 % num == 0 or num % 7 == 0:
        # If so, increment the count
        count += 1
print("Count:",count)

Python output:
Count: 6

Solution:
- Factors of 34 in the list: 1, 2, 17
- Multiples of 7 in the list: 14, 56, 91
- Therefore, the answer is $\\boxed{7}$.

"""

prompt_pot_AQUA = """

Given the question with options and all the context, generate the solution to the given mathematical problem. If the final answer is not in the options reason using the options. You should give concise solutions using the context. Finally, conclude the answer in the format of "the answer is ". For example, "the answer is A", "the answer is D", etc. Use information from context. 

Question: A trader sold an article at a profit of 20% for Rs.360. What is the cost price of the article? Options:['A)270', 'B)300', 'C)280', 'D)320', 'E)315']

Python generator:
from sympy import *
# Define the variables
cp, profit_percent, selling_price = symbols('cp profit_percent selling_price')
# Define the equation for calculating selling price
eq = Eq(selling_price, cp + cp*profit_percent/100)
# Substitute the given values into the equation
eq_sub = eq.subs({selling_price: 360, profit_percent: 20})
# Solve the equation for the cost price
sol = solve(eq_sub, cp)
# Print the answer
print("Cost price:", sol[0]) # Option B, 300

Python output:
Cost price: 300

Solution: 
Let the cost price of the article be $x$.
Profit percent = 20%
Selling price = Cost price + Profit
360 = $x$ + 20% of $x$
360 = $x$ + $\frac{20}{100}$ $x$
360 = $\frac{120}{100}$ $x$
$x$ = $\frac{36000}{120}$ = 300
Therefore, the answer is B.


Question: An amusement park charges an entry fee of $\\$2.25$ plus $\\$1.50$ for each ride. If Simon spent a total of $\\$12.75$, how many rides did he pay for? Options:['A)2', 'B)30', 'C)7', 'D)3', 'E)31']

Python generator:
from sympy import *
# Define the variables
x = symbols('x')
# Equation for the problem
eq = Eq(2.25 + 1.5*x, 12.75)
print("Equation:",eq)
# Solve the equation
sol = solve(eq, x)
print("Solution x:",sol)
# The number of rides Simon paid for
rides = sol[0]
print("Number of rides:",rides)

Python output:
Equation: Eq(1.5*x + 2.25, 12.75)
Solution x: [7.00000000000000]
Number of rides: 7.00000000000000
Solution:
- $12.75 - $2.25 = $10.50$
- $10.50 ÷ $1.50 = 7$
- Therefore, the answer is C.


Question: Walter, Agnes, and Holly are making beaded lizards. Walter has 476 green beads and 32 red beads. Agnes has 104 green beads and 16 red beads. Holly has 281 green beads and 80 red beads. They all share their beads so as to make the largest possible number of lizards.  If a beaded lizard requires 94 green beads and 16 red beads, what is the number of green beads left over? Options:['A)20', 'B)300', 'C)250', 'D)120', 'E)109'

Python generator:
from sympy import *
# Define the number of beads each person has
walter_green = 476
walter_red = 32
agnes_green = 104
agnes_red = 16
holly_green = 281
holly_red = 80
# Define the number of beads required for a lizard
lizard_green = 94
lizard_red = 16
# Calculate the total number of beads
total_green = walter_green + agnes_green + holly_green
total_red = walter_red + agnes_red + holly_red
print("Total green beads:", total_green)
print("Total red beads:", total_red)
# Calculate the number of lizards they can make
num_lizards = min(total_green // lizard_green, total_red // lizard_red)
print("Number of lizards:", num_lizards)
# Calculate the number of green beads left over
green_leftover = total_green - num_lizards * lizard_green
print("Green beads left over:", green_leftover)

Python output:
Total green beads: 861
Total red beads: 128
Number of lizards: 8
Green beads left over: 109

Solution:
- Total green beads: $476 + 104 + 281 = 861$
- Total red beads: $32 + 16 + 80 = 128$
- Number of lizards they can make: $min(861 ÷ 94, 128 ÷ 16) = 8$
- Green beads left over: $861 - 8 * 94 = 109$
- Therefore, the answer is E.

Question: How many of the following numbers are factors of 34 or multiples of 7?\n\n1, 2, 3, 4, 8, 14, 17, 29, 56, 91 Options:['A)10', 'B)3', 'C)0', 'D)6', 'E)315'

Python generator:
from sympy import *
# Define the list of numbers
numbers = [1, 2, 3, 4, 8, 14, 17, 29, 56, 91]
# Initialize the count of factors of 34 or multiples of 7
count = 0
# Iterate over the numbers
for num in numbers:
    # Check if the number is a factor of 34 or a multiple of 7
    if 34 % num == 0 or num % 7 == 0:
        # If so, increment the count
        count += 1
print("Count:",count)

Python output:
Count: 6

Solution:
- Factors of 34 in the list: 1, 2, 17
- Multiples of 7 in the list: 14, 56, 91
- Hence there a 6 numbers.
- Therefore, the answer is D.







"""