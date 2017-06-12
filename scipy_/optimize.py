
import numpy as np
from scipy import optimize


###############################################################################
#                              simplex method
#   The constraint of linear programming problem is a convex set. For any linear
# programming problem with n variables, each corner-point feasible solution(CPF)
# is the simultaneous solution of a system of n constraint boundary equations.
# CPF solutions have the following properties:
#     1) If there is exactly one optimal solution, then it must be a CPF
#        solution. If there are multiple optimal solutions, then at least two
#        must be adjacent CPF solutions.
#     2) There are only finite number of CPF solutions.
#     3) If a CPF solution has no adjacent CPF solution that are better, then
#        there are no better CPF solutions anywhere.
#
#   The assignment problem is a special case of the transportation problem,
# which is a special case of the minimum cost flow problem, which in turn is a
# special case of a linear program. While it is possible to solve any of these
# problems using the simplex algorithm, each specialization has more efficient
# algorithms designed to take advantage of its special structure.
###############################################################################
"""
**STANDARD FORM
minimize:    c^T x
subject to:  Ax = b
             x_i >= 0
             b_i >= 0

**EXAMPLE
minimize:    4x1 + 5x2
subject to:  3x1 +  x2  <= 27
             3x1 + 2x2  >= 30
              x1 +  x2  =  12
             x1 >= 0
             x2 >= 0

initialization of phase 1:
[[  1.   1.   0.   0.   1.   0.  12.]        ==, 1 artificial variable
 [  3.   1.   1.   0.   0.   0.  27.]        <=, 1 slack variable
 [  3.   2.  -0.  -1.  -0.   1.  30.]        >=, 1 slack and 1 artificial
 [  4.   5.   0.   0.   0.   0.   0.]        the real objective function
 [ -4.  -3.   0.   1.   0.   0. -42.]]       objective function for phase 1

"""

c = np.array([4, 5], dtype=np.float)
A_ub = np.array([3, 1, -3, -2], dtype=np.float).reshape((2, 2))
b_ub = np.array([27, -30], dtype=np.float)
A_eq = np.array([1, 1], dtype=np.float).reshape((1, 2))
b_eq = np.array([12], dtype=np.float)
bounds = np.array([0, None, 0, None], dtype=np.float).reshape((2, 2))

optimize.linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                 bounds=bounds, callback=optimize.linprog_verbose_callback)
