from typing import Any, Dict, List, Optional
from CSP import Assignment, BinaryConstraint, Problem, UnaryConstraint
from helpers.utils import NotImplemented
import math
# This function should apply 1-Consistency to the problem.
# In other words, it should modify the domains to only include values that satisfy their variables' unary constraints.
# Then all unary constraints should be removed from the problem (they are no longer needed).
# The function should return False if any domain becomes empty. Otherwise, it should return True.
def one_consistency(problem: Problem) -> bool:

    # Loop over every variable in the problem, for each variable loop over its domain values, 
    # for each value if it violates the unary constraint it is involoved in, it wiil ve removed from the domain
    for var in problem.variables:
        for val in problem.domains[var].copy():
            for constraint in problem.constraints:
                # the constraint must be unary
                if not isinstance(constraint, UnaryConstraint): continue
                # the variable must be involved in the current constraint 
                if constraint.variable != var: continue
                if not constraint.is_satisfied({var: val}):
                    problem.domains[var].remove(val)
                    break

    # remove all of the unary constraints from the problemn constraints
    problem.constraints = [constraint for constraint in problem.constraints if not isinstance(constraint, UnaryConstraint)]

    # If any if the domain of any variable emptied, then there is no solution available, then return False
    for var in problem.variables:
        if not problem.domains[var]: return False # if the domain of var is empty
    return True

# This function should implement forward checking
# The function is given the problem, the variable that has been  and its  value and the domains of the un values
# The function should return False if it is impossible to solve the problem after the given assignment, and True otherwise.
# In general, the function should do the following:
#   - For each binary constraints that involve the  variable:
#       - Get the other involved variable.
#       - If the other variable has no domain (in other words, it is already ), skip this constraint.
#       - Update the other variable's domain to only include the values that satisfy the binary constraint with the  variable.
#   - If any variable's domain becomes empty, return False. Otherwise, return True.
# IMPORTANT: Don't use the domains inside the problem, use and modify the ones given by the "domains" argument 
#            since they contain the current domains of unassigned variables only.
def forward_checking(problem: Problem, assigned_variable: str, assigned_value: Any, domains: Dict[str, set]) -> bool:

    for constraint in problem.constraints:
        # the constraint must be binary
        if not isinstance(constraint, BinaryConstraint): continue
        # the variable must be involved in the current constraint 
        if assigned_variable not in constraint.variables: continue
        # get the other variable involved
        other_variable = constraint.get_other(assigned_variable)
        # if the other involved variable is already assigned, skip it
        if other_variable not in domains: continue 

        # remove any value from the other_variable's domain that doesn't satisfy the current constraint that 
        # this variable involved in 
        for val in domains[other_variable].copy():
            if not constraint.is_satisfied({ assigned_variable: assigned_value, other_variable: val }):
                domains[other_variable].remove(val)
        
        # If any if the domain of the other involved variable emptied, then there is no solution available, then return False
        if not domains[other_variable]: return False # if the domain of other_variable is empty
    return True

        
        

# This function should return the domain of the given variable order based on the "least restraining value" heuristic. !!!(descending)!!!
# IMPORTANT: This function should not modify any of the given arguments.
# Generally, this function is very similar to the forward checking function, but it differs as follows:
#   - You are not given a value for the given variable, since you should do the process for every value in the variable's
#     domain to see how much it will restrain the neigbors domain
#   - Here, you do not modify the given domains. But you can create and modify a copy.
# IMPORTANT: If multiple values have the same priority given the "least restraining value" heuristic, 
#            order them in ascending order (from the lowest to the highest value).
# IMPORTANT: Don't use the domains inside the problem, use and modify the ones given by the "domains" argument 
#            since they contain the current domains of un variables only.
def least_restraining_values(problem: Problem, variable_to_assign: str, domains: Dict[str, set]) -> List[Any]:
    # freq dictionary that describes each value with its count of satisfied constraints
    lrv_domain = {}
    # loop over every value in the domain of the passed variable, and for each value
    # count the number of satisfied constraints regarding all values in the other variable's domain
    # Then return a list of domain's values sorted descendigaly
    for var_to_assign_val in domains[variable_to_assign]:
        lrv_domain[var_to_assign_val] = 0
        for constraint in problem.constraints:
            # the constraint must be binary
            if not isinstance(constraint, BinaryConstraint): continue
            # the variable must be involved in the current constraint
            if variable_to_assign not in constraint.variables: continue
            # get the other variable involved
            other_variable = constraint.get_other(variable_to_assign)
            # if the other involved variable is already assigned, skip it
            if other_variable not in domains: continue 

            # count all values from the other_variable's domain that satisfies the current constraint that 
            # this variable involved in, and store them in the frequency dictionary
            for other_var_val in domains[other_variable].copy():
                if constraint.is_satisfied({ variable_to_assign: var_to_assign_val, other_variable: other_var_val }):
                    lrv_domain[var_to_assign_val] += 1

    # Sort the values ascendingaly to preserve the stability in case of equal count values
    lrv_domain = { val: lrv for val, lrv in sorted(lrv_domain.items(), key = lambda k: k[0]) } # to preserve the stability
    lrv_domain = [val for val, _ in sorted(lrv_domain.items(), key = lambda k: k[1], reverse = True)]
    return lrv_domain



# This function should return the variable that should be picked based on the MRV heuristic.
# IMPORTANT: This function should not modify any of the given arguments.
# IMPORTANT: Don't use the domains inside the problem, use and modify the ones given by the "domains" argument 
#            since they contain the current domains of un variables only.
# IMPORTANT: If multiple variables have the same priority given the MRV heuristic, 
#            order them in the same order in which they appear in "problem.variables".
def minimum_remaining_values(problem: Problem, domains: Dict[str, set]) -> str:
    mrv = None
    min_domain = math.inf
    # Loop over every variable that is unassigned, and minimize the length of their domains
    # also, store the variable that corresponds to this minimum domain length and return it eventually
    for var in problem.variables:
        if var not in domains: continue
        domain_len = len(domains[var])
        if domain_len < min_domain:
            min_domain = domain_len
            mrv = var
    return mrv
        


# This function should solve CSP problems using backtracking search with forward checking.
# The variable ordering should be decided by the MRV heuristic.
# The value ordering should be decided by the "least restraining value" heurisitc.
# Unary constraints should be handled using 1-Consistency before starting the backtracking search.
# This function should return the first solution it finds (a complete assignment that satisfies the problem constraints).
# If no solution was found, it should return None.
# IMPORTANT: To get the correct result for the explored nodes, you should check if the assignment is complete only once using "problem.is_complete"
#            for every assignment including the initial empty assignment, EXCEPT for the assignments pruned by the forward checking.
#            Also, if 1-Consistency deems the whole problem unsolvable, you shouldn't call "problem.is_complete" at all.


def solve_rec(problem: Problem, assignment: Assignment) -> Optional[Assignment]:
    # As a base case, return assignemnt if it is complete and consisitent with all constraints
    if problem.is_complete(assignment) and problem.satisfies_constraints(assignment): return assignment
    # Get all unassigned variables
    unassigned_variables_domains = { var: domain for var, domain in problem.domains.items() if var not in assignment }
    # Choose the variable to assign based on MRV heuristic
    variable = minimum_remaining_values(problem, unassigned_variables_domains)
    
    # Try all possible assignemnt values based on LRV heuristic 
    for value in least_restraining_values(problem, variable, unassigned_variables_domains):
        assignment[variable] = value
        # del unassigned_variables_domains[variable]
        
        # By applying forward checking on every possible value from lrv list, you will check
        # if this assignment will lead to no solution or not, if it will, then it continues checking for other values
        if forward_checking(problem, variable, value, unassigned_variables_domains.copy()):
            rec_assignment = solve_rec(problem, assignment)
            if rec_assignment is not None: return rec_assignment
        
        # unassigned_variables_domains[variable] = problem.domains[variable].copy()
        del assignment[variable]
    # if all values will lead to no solution, then return None
    return None

# This function used to apply one consistincy before recursivly backtracking the solution
# it also initializes the backtracking algorithm with empy assignment
def solve(problem: Problem) -> Optional[Assignment]:
    if not one_consistency(problem): return None
    return solve_rec(problem, {})
