prompt = """
Read the following question and provide the basic checks in form of predicates that need to be satisfied.

Question: What positive two-digit integer is exactly twice the sum of its digits?

Output type: integer

Basic checks: positive_integer(x), twodigit(x)



Question: In isosceles triangle $ABC$, angle $BAC$ and angle $BCA$ measure 35 degrees. What is the measure of angle $CDA$?

Output type: value_of_angle

Basic checks: isosceles(triangle ABC), BCA(35), BAC(35) 



Question: There are ten meerkats in a colony. Every night, two meerkats stand guard while the others sleep. During a certain period of nights, every meerkat stands guard with every other meerkat exactly once. During that period, how many nights of sleep does each meerkat get?

Output type: count

Basic checks: total_meerkats(10), num_guard_at_night(2)




Question: What is the smallest positive integer $n$ such that, out of the $n$ unit fractions $\\frac{1}{k}$ where $1 \\le k \\le n$, exactly half of the fractions give a terminating decimal?

Output type: integer

Basic checks: positive_integer(n)

Read the following question and generate the basic checks in the form of predicates that need to be satisfied.
"""

